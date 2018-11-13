import re

# variable types
INPUT_VARIABLE_TYPES = [
    'staticBinding',                # Use constant inputs
    'userInputBinding',             # Prompt inputs
    'resultBinding',                # Use Previous result inputs
    'identityBinding',              # System Account Inputs
    'loggedUserIdentityBinding',    # Logged-in user credantial input
]

# Violation Matrix
VIOLATION_MATRIX = {
    "001": "Input variable name and Assign from values are not identical",
    "002": "Hard-coded values present in use constant field",
    "003": "Input variable is using Prompt User",
    "004": "Input variable name contains sensitive keywords, but not OBFUSCATED",
    "005": "Sensitive input is assigned from USERNAME field from System Account",
    "006": "Scriptlet used in variable filter",
    "007": "try catch not implemented in Scriptlet",
    "008": "Flow Output variable created in flow steps",
    "009": "Varible is defined but not assigned",
    "010": "Description is not provided for System Property",
    "011": "Description is not provided for System Account",
    "012": "System Property is not used anywhere in this project",
}

SENSITIVE_VARIBLE_IDENTIFIERS = [
    'password',
]


def get_request_data(request):
    """
    Get the data from the request post
    """
    jar_file = request.files['project_file']    
    steps_to_ignore = request.form.get('steps_to_ignore')
    vars_to_ignore = request.form.get('vars_to_ignore')

    if steps_to_ignore:
        steps_to_ignore = steps_to_ignore.replace('\r', '').strip().split('\n')
    else:
        steps_to_ignore = []

    if vars_to_ignore:
        vars_to_ignore = vars_to_ignore.replace('\r', '').strip().split('\n')
    else:
        vars_to_ignore = []

    return {
        'jar_file': jar_file,
        'steps_to_ignore': steps_to_ignore,
        'only_errors': request.form.get("only_errors"),
        'ignore_scriptlets_in_filters': request.form.get('ignore_scriptlets_in_filters'),
        'ignore_flow_output_vars_in_steps': request.form.get("ignore_flow_output_vars_in_steps"),
        'vars_to_ignore' : vars_to_ignore,
    }


def get_input_var_elements(input_element, var_type, form, opr_ref_id=None):
    """
    Extract input elements from given input_element
    """
    variables = []
    sys_props = []    

    for input_var_element in input_element:
        violation = []

        variable = {
            "id": input_var_element.get('id'),
            "name": input_var_element.find('inputSymbol').text,
            "data_type": input_var_element.find('inputType').text,
            "type": var_type
        }

        assign_frm_cntxt = input_var_element.find('assignFromContext').text
        frm_cntxt_key = input_var_element.find('fromContextKey')

        if frm_cntxt_key != None and frm_cntxt_key.text != None and \
           frm_cntxt_key.text != variable['name']:
            variable['assign_from'] = frm_cntxt_key.text
            # Check if variable is assigned from system property
            if not re.match(r'.*/.+', frm_cntxt_key.text):
                violation.append("001")
            else:
                sys_props.append(frm_cntxt_key.text)

        elif assign_frm_cntxt == 'true':
            variable['assign_from'] = variable['name']

        else:
            variable['assign_from'] = "<not assigned>"
            if variable['type'] == "identityBinding":
                violation.append("001")
            else:                    
                violation.append("009")

        # get variable default value
        value = input_var_element.find('value')
        if variable['data_type'] == "ENCRYPTED":
            variable['default_value'] = ""
        elif value is not None and value.text is not None:
            variable['default_value'] = value.text
            violation.append("002")
        else:
            variable['default_value'] = ""

        for sensitive_var_identifier in SENSITIVE_VARIBLE_IDENTIFIERS:
            if sensitive_var_identifier in variable['name'].lower() \
               and variable['data_type'] != "ENCRYPTED":
                violation.append("004")
                break

        # if variable is using system account
        if var_type == 'identityBinding':
            variable['sys_acct_uuid'] = input_var_element.\
                                        find('link/refId').text
            variable['sys_acct_ref_name'] = input_var_element.\
                                            find('link/refName').text
            variable['sys_acct_ref_attr'] = input_var_element.\
                                            find('identityAttribute').text
            variable['default_value'] = "{} : {}".format(
                                                variable['sys_acct_ref_name'],
                                                variable['sys_acct_ref_attr'])

            # Remove not assigned violation
            if "009" in violation : violation.remove("009")

            for sensitive_var_identifier in SENSITIVE_VARIBLE_IDENTIFIERS:
                if sensitive_var_identifier.lower() in \
                   variable['name'].lower() and \
                   variable['sys_acct_ref_name'] == 'USERNAME':
                    violation.append("005")

        elif var_type == "userInputBinding":
            violation.append("003")

        if opr_ref_id and opr_ref_id in form['steps_to_ignore']:
            variable['violations'] = []
        elif variable['name'] in form['vars_to_ignore']:
            variable['violations'] = []
        else:
            variable['violations'] = violation

        if form['only_errors']:
            if len(variable['violations']) > 0 :
                variables.append(variable)
            else:
                continue
        else:
            variables.append(variable)

    return {
        'variables': variables,
        'sys_props': sys_props
    }


def get_stats(json_data):
    variables = []
    steps_count = 0
    error_count = 0
    overall_variable_count = 0
    for flow in json_data:
        steps_count += flow['steps_count']
        overall_variable_count += flow['var_count']

        for inpt_var in flow['inputs']:
            variables.append(inpt_var['name'])
            if len(inpt_var['violations']):
                error_count += 1

        for outpt_var in flow['outputs']:
            variables.append(outpt_var['name'])

        for step in flow['steps']:
            overall_variable_count += step['var_count']
            for inpt_var in step['inputs']:
                variables.append(inpt_var['name'])
                if len(inpt_var['violations']):
                    error_count += 1
            for outpt_var in step['outputs']:
                variables.append(outpt_var['name'])
                if len(outpt_var['violations']):
                    error_count += 1

    return {
        'steps_count': steps_count,
        'overall_variable_count': overall_variable_count,
        'error_count': error_count,
        'variables': variables
    }


def check_try_catch_in_js(js_script):
    """
    Validates try catch implemented in JS script
    Returns : True or False
    """
    if 'try' not in js_script or 'catch' not in js_script:
        return False
    else:
        return True


def get_default_steps_to_ignore_data():
    """
    Returns default steps ignore data
    """
    with open('./data/defaults_steps_to_ignote.txt', 'r') as file_desc:
        return file_desc.read()

import jsbeautifier

from custom_lib import (
        INPUT_VARIABLE_TYPES,
        get_input_var_elements,
        check_try_catch_in_js
    )


class StepParser(object):
    """ Flow Step class"""    

    def __init__(self, element, form):
        self.var_count = 0
        self.form = form
        self.violations = []
        self.sys_props = []
        self.has_violations = False
        self.element = element
        self.uuid = element.get('id')
        self.name = element.find('name').text.strip()
        self.step_type = self.get_step_type()
        self.oprtr_ref_id = self.get_step_ref_id(element)
        self.inputs = self.get_step_inputs()
        self.outputs = self.get_step_outputs()        
        self.get_step_scriptlet()
        self.find_violations()


    def __str__(self):
        return self.name

    def __repr__(self):
        return "<StepParser : {}>".format(self.name)

    def get_step_ref_id(self, element):
        """
        Returns step refernce ID
        """
        if self.step_type == 'operator-step':
            return element.find('opRef').find('refId').text
        return self.step_type

    def find_violations(self):
        """
        set violation flag for setp
        """
        for inpt in self.inputs:
            if len(inpt['violations']) > 0:
                self.has_violations = True
                break
        else:
            for output in self.outputs:
                if len(output['violations']) > 0:
                    self.has_violations = True
                    break

    def get_step_type(self):
        """
        Identify and returns the step type
        """
        return 'return-step' if self.element.find('returnStepType') != None else 'operator-step'

    def get_step_inputs(self):
        """
        Find and returns step input vars
        """
        variables = []
        for var_type in INPUT_VARIABLE_TYPES:
            var_tags = self.element.findall('bindings/' + var_type)            
            # variables = variables + get_input_var_elements(
            #                             var_tags,
            #                             var_type,
            #                             self.form,
            #                             self.oprtr_ref_id
            #                         )
            return_data = get_input_var_elements(
                            var_tags,
                            var_type,
                            self.form,
                            self.oprtr_ref_id
                        )
            variables += return_data['variables']
            self.sys_props += return_data['sys_props']

            self.var_count += len(var_tags)
        return variables

    def get_step_outputs(self):
        """
        Find and Returns Step outputs variables
        """
        variables = []
        flw_var_assignments = self.element.findall('assignments/flowVariableAssignment')
        self.var_count += len(flw_var_assignments)

        for flw_var_assignment in flw_var_assignments:            
            variable = {}
            violation = []
            expression = flw_var_assignment.find('expression')
            variable['id'] = expression.get('id')
            variable['name'] = flw_var_assignment.find('contextKey').text
            variable['assign_from'] = expression.find('name').text
            variable['variable_type'] = flw_var_assignment.find('assignmentTargetType').text

            # Check if its configured to ignore
            if not self.form['ignore_flow_output_vars_in_steps'] and \
               variable['variable_type'] == "FLOW_OUTPUT_FIELD" and \
               self.step_type == 'operator-step':
                violation.append("008")

            variable['violations'] = violation

            # Check if only-error parameter is set
            if self.form['only_errors']:
                if violation:
                    variables.append(variable)
                else:
                    continue
            else:
                variables.append(variable)
        return variables

    def get_step_scriptlet(self):
        """
        Find and set the step scriptlet
        and find violation in scriptlet
        """
        scriptlet = self.element.find('scriptlet')
        if scriptlet is not None :
            if scriptlet.find('script').text is not None:
                self.scriptlet = jsbeautifier.beautify(scriptlet.find('script').text.strip())
                # Check script has try catch implemented
                if not check_try_catch_in_js(self.scriptlet):
                    self.violations.append('007')
            else:
                self.scriptlet = None
        else:
            self.scriptlet = None

    def json(self):
        return {
            'name': self.name,
            'uuid': self.uuid,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'scriptlet': self.scriptlet,
            'var_count': self.var_count,
            'actual_var_count': len(self.inputs) + len(self.outputs),
            'violations': self.violations,
            'sys_props': list(set(self.sys_props)),
        }

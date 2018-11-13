import os
from xml.etree import ElementTree

from custom_lib import (
        INPUT_VARIABLE_TYPES,
        get_input_var_elements
    )
from step_parser import StepParser

class FlowParser():
    """FlowParser is parsing induvidual flows"""
    def __init__(self, zf_ref, file_ref, form):
        self.var_count = 0
        self.has_violations = False
        self.scriptlet = False
        self.zf_ref = zf_ref
        self.file_ref = file_ref
        self.form = form
        self.sys_props = []
        self.filename = self.get_file_name()
        self.root = self.get_et_root()
        self.uuid = self.root.get('id')
        self.name = self.root.find('name').text
        self.path = self.file_ref.filename.replace('.xml','')
        self.inputs = self.get_flow_inputs()
        self.outputs = self.get_flow_outputs()
        self.steps = self.process_steps()        

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<FlowParser : {}>'.format(self.name)

    def get_file_name(self):
        """
        Return filename from file ref
        """
        return os.path.basename(self.file_ref.filename)

    def get_et_root(self):
        """
        Returns XML ElementTree object for given flow
        """
        #return zf_ref.open(file).read().decode("utf-8")
        return ElementTree.parse(self.zf_ref.open(self.file_ref)).getroot()

    def get_flow_inputs(self):
        """
        Returns Flow Input variables
        """
        variables = []
        for var_type in INPUT_VARIABLE_TYPES:
            var_tags = self.root.findall('inputs/' + var_type)
            # variables = variables + get_input_var_elements(var_tags, var_type,
            #                                                self.form)
            return_data = get_input_var_elements(var_tags, var_type, self.form)
            variables += return_data['variables']
            self.sys_props += return_data['sys_props']

            self.var_count += len(var_tags)
        return variables

    def get_flow_outputs(self):
        """
        Returns Flow Output variables
        """
        variables = []
        expressions = self.root.findall(r'availableResultExpressions/expression')
        self.var_count += len(expressions)
        if not self.form['only_errors']:
            for expression in expressions:
                variables.append({
                        'id': expression.get('id'),
                        'name': expression.find('name').text,
                        'assign_from': expression.find('fieldName').text
                    })
        return variables

    def process_steps(self):
        steps = []
        # Find both steps and return steps in the flow
        flow_steps = self.root.findall('steps/step') + self.root.findall('steps/returnStep')
        for step in flow_steps:
            step_obj = StepParser(step, self.form)
            self.sys_props += step_obj.sys_props
            if not self.has_violations and step_obj.has_violations:
                self.has_violations = True
            if step_obj.scriptlet:
                self.scriptlet = True
            
            steps.append(step_obj.json())

        if not self.has_violations:
            for inpt in self.inputs:
                if len(inpt['violations']):
                    self.has_violations = True
                    break

        return steps

    def json(self):
        return {
            'name': self.name,
            'uuid': self.uuid,
            'path': self.path,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'steps': self.steps,
            'var_count': self.var_count,
            'steps_count': len(self.steps),
            'actual_var_count': len(self.inputs) + len(self.outputs),
            'has_violations': self.has_violations,
            'scriptlet': self.scriptlet,
            'sys_props': list(set(self.sys_props)),
        }

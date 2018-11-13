from xml.etree import ElementTree


class SysProps():
    """docstring for SysProps"""
    sys_props_usage_list = []
    form = None
    zf_ref = None

    def __init__(self, file_ref):        
        self.file_ref = file_ref        
        self.violations = []
        self.path = self.get_path()
        self.root = self.get_et_root()
        self.uuid = self.root.get('id')
        self.name = self.root.find('name').text
        self.desc = self.get_desc()        
        self.find_usage()

        
    def get_et_root(self):
        """
        Returns XML ElementTree object for given flow
        """        
        return ElementTree.parse(SysProps.zf_ref.open(self.file_ref)).getroot()

    def get_desc(self):
        """
        Returns the description of the configuration item
        """

        desc = self.root.find('descriptionCdata')
        # print(desc_txt)
        if desc:
            if '=' in desc.text:
                # print(desc_txt.text)
                return desc.text.split('=')[1]
            else:            
                self.violations.append['010']
                return ''
        else:
            return ''       

    def get_path(self):
        """
        Returns Path of System Property
        """
        return self.file_ref.filename.split('System Properties/')[1].replace('.xml', '')


    def find_usage(self):
        self.usage = []
        for sys_prop_info in SysProps.sys_props_usage_list:
            if self.path in sys_prop_info['sys_props']:
                self.usage.append(sys_prop_info['flow_name'])

        # Add condition check for form parameters 
        if not self.usage:            
            self.violations.append('012')

    def json(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'path': self.path,
            'violations': self.violations,
            'path': self.path,
            'usage': self.usage,
            'desc': self.desc,
        }

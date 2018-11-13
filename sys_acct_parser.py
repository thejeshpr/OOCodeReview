from xml.etree import ElementTree


class SysAcct():
    """docstring for SysAcct"""    
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
        # self.find_usage()

        
    def get_et_root(self):
        """
        Returns XML ElementTree object for given flow
        """        
        return ElementTree.parse(SysAcct.zf_ref.open(self.file_ref)).getroot()

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
        Returns Path of System Account
        """
        return self.file_ref.filename.split('System Accounts/')[1].replace('.xml', '')
    

    def json(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'path': self.path,
            'violations': self.violations,            
            'desc': self.desc,
        }

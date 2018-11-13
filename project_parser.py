import os
from xml.etree import ElementTree
from multiprocessing.dummy import Pool as ThreadPool
import zipfile
from pprint import pprint
from functools import partial

from flow_parser import(
    FlowParser
)

from sys_props_parser import SysProps
from sys_acct_parser import SysAcct


class ProjectParser():
    """
    OO Project Parser
    """
    def __init__(self, form):
        self.zf_ref = zipfile.ZipFile(form['jar_file'])
        self.form = form
        self.sys_props_usage_list = []        
        self.project_name = form['jar_file'].filename.split('-')[0]
        self.set_flws_and_cfgs()

    def set_flws_and_cfgs(self):
        """
        Find flows and config items
        """
        self.flows = []
        self.sys_props = []
        self.sys_accts = []
        for file_ref in self.zf_ref.infolist():
            if file_ref.filename.endswith('.xml'):
                if file_ref.filename.startswith('Content/Library/'):
                    self.flows.append(file_ref)
                elif file_ref.filename.startswith('Content/Configuration/'):
                    if 'System Properties' in file_ref.filename:
                        self.sys_props.append(file_ref)
                    elif 'System Accounts' in file_ref.filename:
                        self.sys_accts.append(file_ref)

    def parse_flows(self, flow_ref):
        """
        Create FlowParser object and return FlowParser.json
        Returns: dict FlowParser.json
        """     
        flow_parser = FlowParser(self.zf_ref, flow_ref, self.form)

        sys_props_info = {
            "flow_name" : flow_parser.name,
            "sys_props" : flow_parser.sys_props
        }

        self.sys_props_usage_list.append(sys_props_info)
        
        return flow_parser.json()         
        
    def process_project(self):
        """
        Create Threads to Parse the flows and merge the results
        Returns: list of FlowParser.json
        """
        pool = ThreadPool(5)
        results = pool.map(self.parse_flows, self.flows)
        pool.close()
        pool.join()
        self.parse_config_items()
        return results    

    def parse_config_items(self):
        """
        Parse and process Configuration Items
        """
        self.sys_props_list = []
        self.sys_accts_list = []

        SysProps.sys_props_usage_list = self.sys_props_usage_list
        SysProps.form = self.form
        SysProps.zf_ref = self.zf_ref

        for sys_prop in self.sys_props:            
            sys_props_obj = SysProps(sys_prop)
            self.sys_props_list.append(sys_props_obj.json())


        SysAcct.form = self.form
        SysAcct.zf_ref = self.zf_ref

        for sys_acct in self.sys_accts:
            sys_acct_obj = SysAcct(sys_acct)
            self.sys_accts_list.append(sys_acct_obj.json())

        #pprint(self.sys_accts_list)
        
            


import zipfile
from pprint import pprint

from flask import Flask, render_template, jsonify, request

from project_parser import ProjectParser
from custom_lib import (
    get_request_data,
    get_stats,
    VIOLATION_MATRIX,
    get_default_steps_to_ignore_data
)

APP = Flask(__name__)


@APP.route("/")
def index():
    """
    Index of the website
    Return : renders index.html
    """
    context = {}
    context['default_steps_to_ignore'] = get_default_steps_to_ignore_data()
    return render_template('index.html', context=context)


@APP.route("/parse", methods = ['POST'])
def parse():
    """
    Parse the given OO Project
    """
    form = get_request_data(request)
    proj_parser = ProjectParser(form)
    json_result = proj_parser.process_project()    

    context = {}
    context['violations'] = VIOLATION_MATRIX
    context['title'] = proj_parser.project_name
    context['flows_count'] = len(json_result)
    context['flows'] = json_result
    context['sys_props'] = proj_parser.sys_props_list
    context['sys_accts'] = proj_parser.sys_accts_list

    stats = get_stats(json_result)
    context['variables_count'] = len(stats['variables'])
    context['unique_variables_count'] = len(set(stats['variables']))
    context['steps_count'] = stats['steps_count']
    context['error_count'] = stats['error_count']
    context['overall_variable_count'] = stats['overall_variable_count']

    return render_template('report.html', context=context) 


@APP.route("/config")
def config():
    """
    Index of the website
    Return : renders index.html
    """
    context = {}
    context['default_steps_to_ignore'] = ""
    return render_template('update_config.html', context=context)


if __name__ == "__main__":
    # APP.run(debug=True)
    # APP.run(host='0.0.0.0', port=8080)
    APP.run(host='0.0.0.0', port=80)

#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from typing import Any, Dict, List

import yaml


def load_yaml_files(file_names: List[str]) -> Dict[str, Any]:
    '''Create a dictionary using definitions from a set of yaml files.
    
    This function requires a list of file names in input, each in the YAML format.
    It produces one Python dictionary containing the set of keys and values from all the input files.
    If a key is found more than once, only the last definition will be used in the result. 
    Therefore, the order in specifying the input file names is significant.'''

    parameters = dict()

    for cur_name in file_names:
        with open(cur_name, 'rt') as f:
            cur_parameters = yaml.load(f)
        for key, value in cur_parameters.items():
            parameters[key] = value

    return parameters     

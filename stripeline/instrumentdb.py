#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'Utilities to access the instrument database.'

import os.path


def instrument_db_path():
    '''Return the path to the instrument database.

    Return a string containing the path to the YAML files defining the
    instrument database.'''

    return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', 'instrument'))

def focal_plane_db_file_name():
    'Return the name of the file containing the definition of the focal plane.'

    return os.path.join(instrument_db_path(), 'strip_focal_plane.yaml')

def detector_db_file_name():
    'Return the name of the file containing the definition of the detectors.'

    return os.path.join(instrument_db_path(), 'strip_detectors.yaml')

def scanning_strategy_db_file_name():
    'Return the name of the file containing the definition of the scanning strategy.'

    return os.path.join(instrument_db_path(), 'scanning_strategy.yaml')

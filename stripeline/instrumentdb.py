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

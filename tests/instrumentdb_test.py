#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'Test the functions in the instrumentdb module.'

import os.path
import unittest as ut

import stripeline.instrumentdb as idb

class TestInstrumentDb(ut.TestCase):
    def test_paths(self):
        self.assertTrue(os.path.exists(idb.instrument_db_path()),
                        'Path "{0}" not found'.format(idb.instrument_db_path()))

        for file_name in (idb.focal_plane_db_file_name(),
                          idb.detector_db_file_name(),
                          idb.scanning_strategy_db_file_name()):
            self.assertTrue(os.path.exists(file_name),
                            'File "{0}" not found'.format(file_name))

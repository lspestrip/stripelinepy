#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'Test the functions in the instrumentdb module.'

import os.path
import unittest as ut

import stripeline.instrumentdb as idb

class TestInstrumentDb(ut.TestCase):
    def test_paths(self):
        self.assertTrue(os.path.exists(idb.instrument_db_path()))

        self.assertTrue(os.path.exists(idb.focal_plane_db_file_name()))
        self.assertTrue(os.path.exists(idb.detector_db_file_name()))
        self.assertTrue(os.path.exists(idb.scanning_strategy_db_file_name()))

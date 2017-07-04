#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import unittest as ut
import stripeline.paramfile as pf


class Test_paramfile(ut.TestCase):
    def test_overwrite(self):
        parameters = pf.load_yaml_files(['tests/test1.yaml', 'tests/test2.yaml'])

        self.assertEqual(len(parameters.keys()), 3)
        self.assertEqual(parameters['alpha'], 2)
        self.assertEqual(parameters['wn'], 3)
        self.assertEqual(parameters['beta'], 2)
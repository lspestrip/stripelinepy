#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import unittest as ut

import stripeline.timetools as tt
import numpy as np


class TestTimeTools(ut.TestCase):

    def testSplitTimeRangeSimple(self):
        '''Test split_time_range against a very simple input'''
        result = tt.split_time_range(
            time_length=2.0, num_of_chunks=2, sampfreq=2.0, time0=0.5)

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0], tt.TimeChunk(
            start_time=0.5, num_of_samples=2))
        self.assertEqual(result[1], tt.TimeChunk(
            start_time=1.5, num_of_samples=2))

    def testSplitTimeRangeComplex(self):
        '''Test split_time_range against a tricky input'''
        result = tt.split_time_range(
            time_length=10.0, num_of_chunks=4, sampfreq=1.0, time0=2.0)

        self.assertEqual(len(result), 4)

        self.assertEqual(result[0], tt.TimeChunk(
            start_time=2.0, num_of_samples=2))
        self.assertEqual(result[1], tt.TimeChunk(
            start_time=5.0, num_of_samples=2))
        self.assertEqual(result[2], tt.TimeChunk(
            start_time=7.0, num_of_samples=2))
        self.assertEqual(result[3], tt.TimeChunk(
            start_time=10.0, num_of_samples=2))

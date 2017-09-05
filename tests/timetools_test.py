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


class TestToiProviders(ut.TestCase):
    def test_split(self):
        'Verify that "split_into_n" returns the expected results.'
        self.assertEqual(tuple(tt.split_into_n(10, 4)), (2, 3, 2, 3))
        self.assertEqual(tuple(tt.split_into_n(201, 2)), (100, 101))

    def test_toi_splitting(self):
        'Verify that "assign_toi_files_to_processes" returns the expected results.'
        samples_per_processes = [50, 50, 50, 50]
        fits_files = [tt.ToiFile(file_name='A.fits', num_of_samples=40),
                      tt.ToiFile(file_name='B.fits', num_of_samples=60),
                      tt.ToiFile(file_name='C.fits', num_of_samples=30),
                      tt.ToiFile(file_name='D.fits', num_of_samples=70)]

        result = tt.assign_toi_files_to_processes(
            samples_per_processes, fits_files)

        self.assertEqual(len(result), 4)
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(len(result[1]), 1)
        self.assertEqual(len(result[2]), 2)
        self.assertEqual(len(result[3]), 1)

        segment0, segment1, segment2, segment3 = tuple(result)
        self.assertEqual(segment0[0],
                         tt.ToiFileSegment(file_name='A.fits',
                                           first_element=0,
                                           num_of_elements=40))
        self.assertEqual(segment0[1],
                         tt.ToiFileSegment(file_name='B.fits',
                                           first_element=0,
                                           num_of_elements=10))

        self.assertEqual(segment1[0],
                         tt.ToiFileSegment(file_name='B.fits',
                                           first_element=10,
                                           num_of_elements=50))

        self.assertEqual(segment2[0],
                         tt.ToiFileSegment(file_name='C.fits',
                                           first_element=0,
                                           num_of_elements=30))
        self.assertEqual(segment2[1],
                         tt.ToiFileSegment(file_name='D.fits',
                                           first_element=0,
                                           num_of_elements=20))

        self.assertEqual(segment3[0],
                         tt.ToiFileSegment(file_name='D.fits',
                                           first_element=20,
                                           num_of_elements=50))

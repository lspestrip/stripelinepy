#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import unittest as ut

import stripeline.maptools as mt
import numpy as np


class TestMaptools(ut.TestCase):

    def test_condmatr(self):
        cond = mt.ConditionMatrix(numpix=2)
        cond.update(pixidx=np.array([0, 0, 0], dtype='int32'),
                    angle=np.array([0.0, 1. / 8., 1. / 4.]) * np.pi)
        cond.update(pixidx=np.array([1, 1, 1], dtype='int32'),
                    angle=np.array([0.0, 1. / 12., 1. / 8.]) * np.pi)

        expected = np.array([
            [3., 1.7071067811865475, 1.7071067811865475,
             1.7071067811865475, 1.5, 0.5,
             1.7071067811865475, 0.5, 1.5],
            [3., 2.5731321849709863, 1.2071067811865475,
             2.5731321849709863, 2.25, 0.9330127018922193,
             1.2071067811865475, 0.9330127018922193, 0.75]
        ])

        self.assertTrue(np.allclose(expected, cond.matr))


class TestToiProviders(ut.TestCase):
    def test_split(self):
        'Verify that "split_into_n" returns the expected results.'
        self.assertEqual(tuple(mt.split_into_n(10, 4)), (2, 3, 2, 3))
        self.assertEqual(tuple(mt.split_into_n(201, 2)), (100, 101))


    def test_toi_splitting(self):
        'Verify that "assign_toi_files_to_processes" returns the expected results.'
        samples_per_processes = [50, 50, 50, 50]
        fits_files = [mt.FitsToiFile(file_name='A.fits', num_of_samples=40),
                      mt.FitsToiFile(file_name='B.fits', num_of_samples=60),
                      mt.FitsToiFile(file_name='C.fits', num_of_samples=30),
                      mt.FitsToiFile(file_name='D.fits', num_of_samples=70)]

        result = mt.assign_toi_files_to_processes(samples_per_processes, fits_files)

        self.assertEqual(len(result), 4)
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(len(result[1]), 1)
        self.assertEqual(len(result[2]), 2)
        self.assertEqual(len(result[3]), 1)

        segment0, segment1, segment2, segment3 = tuple(result)
        self.assertEqual(segment0[0],
                         mt.FitsToiSegment(file_name='A.fits',
                                           first_element=0,
                                           num_of_elements=40))
        self.assertEqual(segment0[1],
                         mt.FitsToiSegment(file_name='B.fits',
                                           first_element=0,
                                           num_of_elements=10))

        self.assertEqual(segment1[0],
                         mt.FitsToiSegment(file_name='B.fits',
                                           first_element=10,
                                           num_of_elements=50))

        self.assertEqual(segment2[0],
                         mt.FitsToiSegment(file_name='C.fits',
                                           first_element=0,
                                           num_of_elements=30))
        self.assertEqual(segment2[1],
                         mt.FitsToiSegment(file_name='D.fits',
                                           first_element=0,
                                           num_of_elements=20))

        self.assertEqual(segment3[0],
                         mt.FitsToiSegment(file_name='D.fits',
                                           first_element=20,
                                           num_of_elements=50))


class TestMapMakers(ut.TestCase):

    def testNonoiseMap(self):
        reference_map = np.array([7.0, 9.0, 5.0, 2.0, 4.0, 12.0])
        pixidx = np.array([1, 1, 2, 5, 4, 4, 5, 0, 3, 2, 0, 4], dtype='int')
        signal = reference_map[pixidx]

        result = mt.nonoise_map(signal, pixidx, 6)
        self.assertTrue(np.allclose(reference_map, result),
                         "reference = {0}, result = {1}".format(reference_map, result))

    def testBinnedMap(self):
        # Pixel at pos. 1 is never observed (see pixidx)
        reference_map = np.array([5.0, 0.0, 2.0, -1.0])
        pixidx = np.array([0, 2, 2, 3, 0, 2], dtype='int')
        signal = np.array([4.0, 1.0, 2.0, -1.0, 6.0, 3.0])

        pixels, hits = mt.binned_map(signal, pixidx, 4)
        self.assertTrue(np.allclose(reference_map, pixels),
                        "reference = {0}, result = {1}".format(reference_map, pixels))
        self.assertTrue(np.array_equal(np.array([2, 0, 3, 1]), hits))
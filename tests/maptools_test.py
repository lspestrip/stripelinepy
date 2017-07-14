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
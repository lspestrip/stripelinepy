#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import unittest as ut

import stripeline.maptools as mt
import numpy as np


class TestMaptools(ut.TestCase):

    def test_condmatr(self):
        matr = np.zeros((2, 9), dtype='float64', order='F')
        mt.update_condmatr(numpix=2,
                           pixidx=[0, 0, 0],
                           angle=np.array([0.0, 1. / 8., 1. / 4.]) * np.pi,
                           m=matr)
        mt.update_condmatr(numpix=2,
                           pixidx=[1, 1, 1],
                           angle=np.array([0.0, 1. / 12., 1. / 8.]) * np.pi,
                           m=matr)

        expected = np.array([
            [3., 1.7071067811865475, 1.7071067811865475,
             1.7071067811865475, 1.5, 0.5,
             1.7071067811865475, 0.5, 1.5],
            [3., 2.5731321849709863, 1.2071067811865475,
             2.5731321849709863, 2.25, 0.9330127018922193,
             1.2071067811865475, 0.9330127018922193, 0.75]
        ])

        self.assertTrue(np.allclose(expected, matr))

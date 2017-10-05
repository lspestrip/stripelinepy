#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import unittest as ut

import stripeline.maptools as mt
import numpy as np
from mpi4py import MPI


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


# This class is used to provide some mock data for the MPI-based tests
class MockToiProvider:
    def __init__(self, rank):
        self.rank = rank
        self.num_of_processes = 2

        self.map_q = np.zeros(12)
        self.map_q[0] = 1.0
        self.map_q[2] = 4.0
        self.map_q[3] = 7.0
        self.map_q[4] = -2.0

        self.map_u = np.zeros(12)
        self.map_u[0] = 5.0
        self.map_u[2] = 9.0
        self.map_u[3] = -3.0
        self.map_u[4] = 10.0

        self.time = [np.arange(start=0, stop=5),
                     np.arange(start=5, stop=11)]
        self.pixidx = [np.array([0, 2, 2, 3, 0]),
                       np.array([2, 4, 3, 2, 0, 2])]
        # The second MPI process will see everything rotated by pi/4
        self.psi = [np.zeros(5),
                    np.ones(6) * np.pi * 0.25]

        # Build Q and U timelines. Add/subtract the same constant to the first
        # and second diode, so that their average matches the pixel in the map.
        # Also remember that the second chunk has a polarization angle equal to
        # 45°, so Q → U and U → −Q.
        self.signal_q1 = [
            0.2500 * self.map_q[self.pixidx[0]] + 0.5,
            0.2500 * self.map_u[self.pixidx[1]] + 0.25
        ]
        self.signal_q2 = [
            0.2500 * self.map_q[self.pixidx[0]] - 0.5,
            0.2500 * self.map_u[self.pixidx[1]] - 0.25
        ]
        self.signal_u1 = [
            0.2500 * self.map_u[self.pixidx[0]] + 0.3,
            -0.2500 * self.map_q[self.pixidx[1]] + 0.6
        ]
        self.signal_u2 = [
            0.2500 * self.map_u[self.pixidx[0]] - 0.3,
            -0.2500 * self.map_q[self.pixidx[1]] - 0.6
        ]

    def get_signal(self, det_idx):
        if det_idx in (0, 'Q1'):
            return self.signal_q1[self.rank]
        elif det_idx in (1, 'Q2'):
            return self.signal_q2[self.rank]
        elif det_idx in (2, 'U1'):
            return self.signal_u1[self.rank]
        elif det_idx in (3, 'U2'):
            return self.signal_u2[self.rank]
        else:
            raise AssertionError('Unknown detector {0}'.format(det_idx))

    def get_pixel_index(self, *args, **kwargs):
        # Unused parameter
        del args
        del kwargs
        return self.pixidx[self.rank]

    def get_polarization_angle(self):
        return self.psi[self.rank]


class TestMapMakersMPI(ut.TestCase):
    def testBinnedMapMPI(self):
        comm = MPI.COMM_WORLD
        provider = MockToiProvider(comm.rank)

        if comm.size == 1:
            # We just use the first chunk of data
            expected_map_q = np.array([
                1.0, 0.0, 4.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ])
            expected_map_u = np.array([
                5.0, 0.0, 9.0, -3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ])
            expected_hits = np.array([
                2, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0
            ], dtype='int')
        elif comm.size == 2:
            # In this case, we expect to obtain the same maps as the one used to
            # create the mock TOIs
            expected_map_q = provider.map_q
            expected_map_u = provider.map_u
            expected_hits = np.array([
                3, 0, 5, 2, 1, 0, 0, 0, 0, 0, 0, 0
            ], dtype='int')

        map_i, map_q, map_u, hits = mt.binned_map_strip(1, provider, comm=comm)

        self.assertTrue(np.allclose(map_q, expected_map_q))
        self.assertTrue(np.allclose(map_u, expected_map_u))
        self.assertTrue(np.alltrue(hits == expected_hits))

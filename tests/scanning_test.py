#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import unittest as ut

import stripeline.scanning as sc
import numpy as np


class PointingStorage:
    def __init__(self):
        self.time = None
        self.theta = None
        self.phi = None
        self.psi = None

    def __call__(self, pointings, scanning: sc.ScanningStrategy, dir_vec, index: int):
        self.time = pointings[:, 0]
        self.theta = pointings[:, 1]
        self.phi = pointings[:, 2]
        self.psi = pointings[:, 3]


class TestScanning(ut.TestCase):
    def test_polarization_angle(self):
        storage = PointingStorage()
        scanning = sc.ScanningStrategy(wheel1_rpm=0.0,
                                       wheel3_rpm=60.0,
                                       wheel1_angle0_deg=0.0,
                                       wheel2_angle0_deg=0.0,
                                       wheel3_angle0_deg=0.0,
                                       latitude_deg=0.0,  # Equator
                                       overall_time_s=1.0,
                                       sampling_frequency_hz=4.0)

        sc.generate_pointings(scanning=scanning, dir_vec=[0, 0, 1],
                              num_of_chunks=1, tod_callback=storage)

        self.assertTrue(np.allclose(storage.time, np.array([
            0.00, 0.25, 0.50, 0.75
        ])))

        self.assertTrue(np.allclose(storage.psi, np.deg2rad([
            -90.0, 0.0, 90.0, 180.0
        ])))


    def test_dir_vec(self):
        # Checks that bug #11 does not appear again
        storage = PointingStorage()
        scanning = sc.ScanningStrategy(wheel1_rpm=0.0,
                                       wheel3_rpm=60.0,
                                       wheel1_angle0_deg=0.0,
                                       wheel2_angle0_deg=0.0,
                                       wheel3_angle0_deg=0.0,
                                       latitude_deg=0.0,  # Equator
                                       overall_time_s=1.0,
                                       sampling_frequency_hz=4.0)

        sc.generate_pointings(scanning=scanning, dir_vec=[1, 0, 0],
                              num_of_chunks=1, tod_callback=storage)

        self.assertTrue(np.allclose(storage.theta, np.deg2rad([
            90.0, 0.0, 90.0, 180.0
        ])), "theta is {0}".format(storage.theta))

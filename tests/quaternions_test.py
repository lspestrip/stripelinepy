#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import unittest as ut

import stripeline.quaternions as q
import numpy as np

class TestOperations(ut.TestCase):
    def test_addition(self):
        'Check that the quaternion addition is implemented correctly'

        q1 = np.array([[1.0,  2.0,  3.0,  4.0],
                       [5.0,  6.0,  7.0,  8.0],
                       [9.0, 10.0, 11.0, 12.0]])
        q2 = np.array([[4.0,  3.0,  6.0,  1.0],
                       [9.0,  5.0, 11.0,  8.0],
                       [8.0,  0.0,  4.0,  1.0]])
        expected = np.array([[ 5.0,  5.0,  9.0,  5.0],
                             [14.0, 11.0, 18.0, 16.0],
                             [17.0, 10.0, 15.0, 13.0]])
        self.assertTrue(np.allclose(q.qadd(q1, q2), expected))

    def test_dot(self):
        'Check that the dot product of two quaternions return correct values'

        q1 = np.array([[3.0, 2.0, 4.0, 1.0],
                       [1.0, 1.0, 6.0, 4.0]])
        q2 = np.array([[1.0, 2.0, 1.0, 6.0],
                       [3.0, 8.0, 1.0, 2.0]])
        expected = np.array([17.0, 25.0])
        self.assertTrue(np.allclose(q.qdot(q1, q2), expected))

    def test_norm(self):
        'Check that quaternions are normalized correctly'

        quat = np.array([[1.0, 2.0, 3.0, 4.0],
                         [3.0, 3.0, 3.0, 2.0],
                         [0.0, 0.0, 0.0, 0.0]])
        expected = np.array([[ 0.18257419, 0.36514837, 0.54772256, 0.73029674],
                             [ 0.53881591, 0.53881591, 0.53881591, 0.3592106 ],
                             [ 0.0       , 0.0       , 0.0       , 0.0]])
        print(q.qnorm(quat))
        self.assertTrue(np.allclose(q.qnorm(quat), expected))

    def test_product(self):
        'Check that the quaternion product is implemented correctly'

        q1 = np.array([[1.0,  2.0,  3.0,  4.0],
                       [5.0,  6.0,  7.0,  8.0],
                       [9.0, 10.0, 11.0, 12.0]])
        q2 = np.array([[4.0,  3.0,  6.0,  1.0],
                       [9.0,  5.0, 11.0,  8.0],
                       [8.0,  0.0,  4.0,  1.0]])
        expected = np.array([[  20., 20.,  22.,  -24.],
                             [ 143., 96., 115.,  -88.],
                             [ 145., 62., -21., -104.]])
        self.assertTrue(np.allclose(q.qmul(q1, q2), expected))

    def test_from_axisangle(self):
        'Check that quaternions are built from axis and angles correctly'

        axes = np.array([[1.0, 2.0, 3.0],
                         [4.0, 5.0, 6.0]])
        angles = np.array([0.1, -0.2])
        expected = np.array([[ 0.01335749,  0.02671499,  0.04007248, 0.99875026039496628],
                             [-0.04550829, -0.05688537, -0.06826244, 0.99500416527802582]])
        self.assertTrue(np.allclose(q.qfromaxisangle(axes, angles),
                                    expected))

    def test_to_axisangle(self):
        'Check that rotations are retrieved correctly from quaternions'

        quat = np.array([[1.0, 2.0, 3.0, 0.1],
                         [5.0, 6.0, 7.0, 0.2]])
        axes, angles = q.qtoaxisangle(quat)
        expected_axes = np.array([[1.00503782, 2.01007563, 3.01511345],
                                  [5.10310363, 6.12372436, 7.14434508]])
        expected_angles = np.array([2.9412578112666736,
                                    2.7388768120091318])
        self.assertTrue(np.allclose(axes, expected_axes))
        self.assertTrue(np.allclose(angles, expected_angles))

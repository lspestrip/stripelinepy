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
        expected = np.array([[5.0,  5.0,  9.0,  5.0],
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
        expected = np.array([[0.18257419, 0.36514837, 0.54772256, 0.73029674],
                             [0.53881591, 0.53881591, 0.53881591, 0.3592106],
                             [0.0, 0.0, 0.0, 0.0]])
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
        expected = np.array([[20., 20.,  22.,  -24.],
                             [143., 96., 115.,  -88.],
                             [145., 62., -21., -104.]])
        self.assertTrue(np.allclose(q.qmul(q1, q2), expected))

    def test_from_axisangle(self):
        'Check that quaternions are built from axis and angles correctly'

        axes = np.array([[0.07142857, 0.14285714, 0.21428571],
                         [0.05194805, 0.06493506, 0.07792208]])
        angles = np.array([0.1, -0.2])
        expected = np.array([[0.00356994,  0.00713988,  0.01070982, 0.99875026, ],
                             [-0.00518615, -0.00648269, -0.00777923, 0.99500417]])
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

    def test_inverse(self):
        '''Check that the inversion of rot. quaternion is correct'''

        quat = np.array([[0.00356994,  0.00713988,  0.01070982, 0.99875026, ],
                         [-0.00518615, -0.00648269, -0.00777923, 0.99500417]])
        expected = np.array([[-0.00356994, -0.00713988, -0.01070982, 0.99875026, ],
                             [0.00518615,  0.00648269,  0.00777923, 0.99500417]])
        self.assertTrue(np.allclose(q.qinvrot(quat), expected))

    def test_rotations(self):
        '''Check that the rotation of 3D vectors work as expected'''

        vec = np.array([[1, 0, 0],
                        [0, 1, 0],
                        [0, 0, 1],
                        [0.45584211, 0.56980286, 0.68376361]])
        axes = np.array([[0, 1, 0],
                         [1, 0, 0],
                         [0, 1, 0],
                         [0.71701072,  0.21244762, -0.66389881]])
        angles = np.array([0.5, 0.5, 0.5, 0.3]) * np.pi
        quat = q.qfromaxisangle(axes, angles)

        expected = np.array([[0, 0, -1],
                             [0, 0,  1],
                             [1, 0,  0],
                             [6.89713469e-01, -3.07077022e-01, 6.55743116e-01]])
        print(q.qrotate(vec, quat))
        self.assertTrue(np.allclose(q.qrotate(vec, quat), expected))

    def test_rotation_composition(self):
        '''Check that the composition of rotations through quaternion works'''

        q1 = q.qfromaxisangle([[1, 0, 0]], [np.pi * 0.5])
        q2 = q.qfromaxisangle([[0, 1, 0]], [np.pi * 0.5])
        print('q1 =', q1)
        print('q2 =', q2)
        qprod = q.qmul(q2, q1)
        print('q2*q1 =', qprod)
        vec = np.array([[0, 0, 1]])
        comp_dir = q.qrotate(q.qrotate(vec, q1), q2)
        prod_dir = q.qrotate(vec, qprod)
        print('comp_dir =', comp_dir)
        print('prod_dir =', prod_dir)
        self.assertTrue(np.allclose(comp_dir, prod_dir))

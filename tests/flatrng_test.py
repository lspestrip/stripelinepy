#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import stripeline.noisegen as ng
import unittest as ut

class TestFlatRNG(ut.TestCase):
    def test_identity(self):
        '''Check that the first numbers returned by the generator match the
        ones produced by the C++ version'''

        rng = ng.FlatRNG()
        for idx, reference in enumerate([0.9854981268, 0.2536861135,
                                         0.8791850018, 0.8541532028,
                                         0.4161281283, 0.6491611481,
                                         0.8336713058, 0.2541507778,
                                         0.0673349826, 0.7994472017,
                                         0.2600378725, 0.5134736516,
                                         0.4544143085, 0.9879117254,
                                         0.1875971474, 0.1698732623,
                                         0.9844831470, 0.2436698098,
                                         0.2365035815, 0.9442295933]):
            self.assertAlmostEqual(rng.rand_uniform(), reference,
                                   msg='Reference #{0} does not match'.format(idx))


class TestGaussRNG(ut.TestCase):
    def test_gaussW(self):
        '''Check that the first numbers returned by the Gaussian generator
        match the ones produced by the C++ version'''

        rng = ng.FlatRNG()
        for idx, reference in enumerate([2.2203453391, -1.2484787209,
                                         -0.6320746584, 0.8578639165,
                                         0.1180357999, -2.1021859931,
                                         0.3474941116, -0.0324664453,
                                         -0.5518493521, -0.5222215958,
                                         -2.0377934674, -1.4954636239,
                                         0.3974094356, -1.3198209914,
                                         -0.7904688505, 1.2892796355,
                                         -0.0648447824, -0.2484938345,
                                         0.6008647892, 0.2596945612]):
            self.assertAlmostEqual(rng.rand_normal(), reference,
                                   msg='Reference #{0} does not match'.format(idx))


if __name__ == '__main__':
    ut.main()

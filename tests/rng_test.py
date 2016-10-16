#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import stripeline.noisegen as ng
import unittest as ut

class TestFlatRNG(ut.TestCase):
    def test_identity(self):
        'Check that the generator\'s result match the C++ implementation'

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
            self.assertAlmostEqual(rng.next(), reference,
                                   msg='Reference #{0} does not match'.format(idx))


class TestNormalRNG(ut.TestCase):
    def test_gaussW(self):
        'Check that the generator\'s result match the C++ implementation'

        rng = ng.NormalRNG()
        for idx, reference in enumerate([1.8051588123, -1.0150233503,
                                         -0.5138818361, 0.6974503387,
                                         0.0959640650, -1.7090943033,
                                         0.2825155379, -0.0263954840,
                                         -0.4486580098, -0.4245704031,
                                         -1.6567426564, -1.2158240845,
                                         0.3230971021, -1.0730251963,
                                         -0.6426576020, 1.0481948256,
                                         -0.0527193353, -0.2020275077,
                                         0.4885079587, 0.2111337896]):
            self.assertAlmostEqual(rng.next(), reference,
                                   msg='Reference #{0} does not match'.format(idx))


class TestOof2RNG(ut.TestCase):
    def test_identity(self):
        'Check that the generator\'s result match the C++ implementation'

        rng = ng.Oof2RNG(fmin=1.15e-5, fknee=0.05, fsample=1.0)
        for idx, reference in enumerate([2.0886370365, -0.6074844495,
                                         -0.3464683356, 0.8936789422,
                                         0.4167745672, -1.6416294545,
                                         0.1259486772, -0.1427304943,
                                         -0.6395859847, -0.7526144784,
                                         -2.3116079175, -2.3217436788,
                                         -0.9229344940, -2.4367338428,
                                         -2.2756948201, -0.5210397131,
                                         -1.4655131788, -1.6547241628,
                                         -0.9190954646, -1.0864977062]):
            self.assertAlmostEqual(rng.next(), reference,
                                   msg='Reference #{0} does not match'.format(idx))

if __name__ == '__main__':
    ut.main()

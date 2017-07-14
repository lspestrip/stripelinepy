#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import numpy as np
import stripeline.rng as rng


class FlatRNG:
    'Random number generator with uniform distribution in the range [0, 1['

    def __init__(self, x_init=0, y_init=0, z_init=0, w_init=0):
        '''Initialize the random number generator.

        The four parameters ``x_init``, ``y_init``, ``z_init``, and
        ``w_init`` are the four 32-bit seeds used by the generator.
        '''

        self.state = rng.init_rng(x_init, y_init, z_init, w_init)

    def next(self):
        'Return a new pseudorandom number'
        return rng.rand_uniform(self.state)

    def fill_vector(self, array):
        'Fill the ``array`` vector with a sequence of pseudorandom numbers'
        rng.fill_vector_uniform(self.state, array)


class NormalRNG:
    '''Random number generator with Gaussian distribution

    The Gaussian distribution has mean=0 and sigma=1. It is easy to
    scale the result to an arbitrary mean and sigma:

        rng = NormalRNG()
        mean = 10.0
        sigma = 1.36
        num = mean + rng.next() * sigma

    '''

    def __init__(self, x_init=0, y_init=0, z_init=0, w_init=0):
        self.state = rng.init_rng(x_init, y_init, z_init, w_init)
        self.empty = np.ones(1, dtype='int8')
        self.gset = np.zeros(1, dtype='float64')

    def next(self):
        'Return a new pseudorandom number'
        return rng.rand_normal(self.state, self.empty, self.gset)

    def fill_vector(self, array):
        'Fill the ``array`` vector with a sequence of pseudorandom numbers'
        rng.fill_vector_normal(self.state, self.empty, self.gset, array)


class Oof2RNG:
    '''Random number generator with spectral power 1/f^2

    The random numbers have zero mean.
    '''

    def __init__(self, fmin, fknee, fsample,
                 x_init=0, y_init=0, z_init=0, w_init=0):
        self.flat_state = rng.init_rng(x_init, y_init, z_init, w_init)
        self.empty = np.ones(1, dtype='int8')
        self.gset = np.zeros(1, dtype='float64')
        self.oof2_state = rng.init_oof2(fmin, fknee, fsample)

    def next(self):
        'Return a new pseudorandom number'
        return rng.rand_oof2(self.flat_state, self.empty,
                             self.gset, self.oof2_state)

    def fill_vector(self, array):
        'Fill the ``array`` vector with a sequence of pseudorandom numbers'
        rng.fill_vector_oof2(self.state, self.empty, self.gset,
                             self.oof2_state, array)


class OofRNG:
    '''Random number generator with spectral power 1/f^a

    The random numbers have zero mean. The value of a must be in the range [-2, 0).'''

    def __init__(self, alpha, fmin, fknee, fsample,
                 x_init=0, y_init=0, z_init=0, w_init=0):
        self.flat_state = rng.init_rng(x_init, y_init, z_init, w_init)
        self.empty = np.ones(1, dtype='int8')
        self.gset = np.zeros(1, dtype='float64')
        self.oof_state = np.empty(rng.oof_state_size(fmin, fknee, fsample),
                                  dtype='float64')
        self.num_of_states = rng.init_oof(alpha, fmin, fknee, fsample,
                                          self.oof_state)

    def next(self):
        'Return a new pseudorandom number'
        return rng.rand_oof(self.flat_state, self.empty,
                            self.gset, self.oof_state, self.num_of_states)

    def fill_vector(self, array):
        'Fill the ``array`` vector with a sequence of pseudorandom numbers'
        rng.fill_vector_oof(self.state, self.empty, self.gset,
                            self.oof_state, self.num_of_states, array)

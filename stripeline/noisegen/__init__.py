#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

'''Set of classes for random number generation.

The "stripeline.noisegen" module provides a number of classes to
generate pseudo-random numbers. It has been modeled after S.
Plaszczynski's "absrand" package version 1.1, and it returns the same
results when the same seeds are digested.

Here is a list of the classes implemented by this module:

- FlatRNG: uniform distribution in the range [0, 1[

- NormalRNG: Gaussian distribution with mean=0, sigma=1

- Oof2RNG: 1/f^2 distribution with custom knee frequency, sampling
  frequency and minimum frequency.

All the classes implement a `next` method and a `fill_vector` method
(the latter is missing from the Oof2RNG class). The `fill_vector`
methods have been optimized for handling large datasets.

Example
-------

Create an array of 100 random number in the range [0, 1[ with an
uniform distribution:

   rng = FlatRNG()
   vec = numpy.empty(100)
   rng.fill_vector(vec)

'''

import numpy as np
import rng

class FlatRNG:
    'Random number generator with uniform distribution in the range [0, 1['

    def __init__(self, x_init=0, y_init=0, z_init=0, w_init=0):
        self.state = rng.init_rng(x_init, y_init, z_init, w_init)

    def next(self):
        return rng.rand_uniform(self.state)

    def fill_vector(self, array):
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
        return rng.rand_normal(self.state, self.empty, self.gset)

    def fill_vector(self, array):
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
        return rng.rand_oof2(self.flat_state, self.empty,
                             self.gset, self.oof2_state)

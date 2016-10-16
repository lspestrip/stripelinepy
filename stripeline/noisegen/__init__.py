#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import numpy as np
import rng

class FlatRNG:
    def __init__(self, x_init=0, y_init=0, z_init=0, w_init=0):
        self.state = rng.init_rng(x_init, y_init, z_init, w_init)

    def next(self):
        return rng.rand_uniform(self.state)

    def fill_vector(self, array):
        rng.fill_vector_uniform(self.state, array)


class NormalRNG:
    def __init__(self, x_init=0, y_init=0, z_init=0, w_init=0):
        self.state = rng.init_rng(x_init, y_init, z_init, w_init)
        self.empty = np.ones(1, dtype='int8')
        self.gset = np.zeros(1, dtype='float64')

    def next(self):
        return rng.rand_normal(self.state, self.empty, self.gset)

    def fill_vector(self, array):
        rng.fill_vector_normal(self.state, self.empty, self.gset, array)

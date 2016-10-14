# -*- encoding: utf-8 -*-

from libc.stdint cimport uint32_t, int64_t
from libc.math cimport sqrt, log


cdef twiddle(uint32_t * v):
    for i in range(9):
        v[0] ^= v[0] << 13
        v[0] ^= v[0] >> 17
        v[0] ^= v[0] << 5


cdef struct FlatRNGState:
    uint32_t x
    uint32_t y
    uint32_t z
    uint32_t w


cdef int_rand_uni(FlatRNGState * state):
    cdef uint32_t tmp = state[0].x ^ (state[0].x << 11)
    state[0].x = state[0].y
    state[0].y = state[0].z
    state[0].z = state[0].w
    state[0].w = (state[0].w ^ (state[0].w >> 19)) ^ (tmp ^ (tmp >> 8))

    return state[0].w


cdef init_rng(uint32_t x_start, uint32_t y_start, uint32_t z_start, uint32_t w_start,
              FlatRNGState * state):

    if x_start != 0:
        state[0].x = x_start
    else:
        state[0].x = 123456789

    if y_start != 0:
        state[0].y = y_start
    else:
        state[0].y = 362436069

    if z_start != 0:
        state[0].z = z_start
    else:
        state[0].z = 521288629

    if w_start != 0:
        state[0].w = w_start
    else:
        state[0].w = 88675123

    twiddle(&state[0].x)
    twiddle(&state[0].y)
    twiddle(&state[0].z)
    twiddle(&state[0].w)

    for i in range(16):
        int_rand_uni(state)


cdef class FlatRNG:
    cdef FlatRNGState state
    cdef double scale_factor
    cdef double gset
    cdef int empty

    def __init__(self, x_start=0, y_start=0, z_start=0, w_start=0):
        self.scale_factor = 1.0 / (1.0 + 0xFFFFFFFF)
        self.seed(x_start, y_start, z_start, w_start)

    def seed(self, x_start, y_start, z_start, w_start):
        self.state.x = x_start
        self.state.y = y_start
        self.state.z = z_start
        self.state.w = w_start

        self.empty = 1
        init_rng(x_start, y_start, z_start, w_start, &self.state)

    def int_rand_uniform(self):
        return int_rand_uni(&self.state)

    def rand_uniform(self):
        return self.scale_factor * self.int_rand_uniform()

    def rand_normal(self):
        cdef double v1, v2, rsq
        cdef double fac

        if self.empty != 0:
            while True:
                v1 = 2 * self.rand_uniform()
                v2 = 2 * self.rand_uniform()
                rsq = v1 * v1 + v2 * v2
                if (rsq > 0) and (rsq < 1):
                    break

            fac = sqrt(-2 * log(rsq) / rsq)
            self.gset = v1 * fac
            self.empty = 0
            return v2 * fac
        else:
            self.empty = 1
            return self.gset

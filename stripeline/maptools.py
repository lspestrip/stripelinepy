#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

'''Map-related facilities
'''

from typing import Any

import stripeline._maptools as _m
import numpy as np


class ConditionMatrix:
    '''Compute the inverse condition number for pixels in a map

    This class computes the inverse condition number of the pixels in a map,
    given one or more streams of samples taken from TODs. Condition numbers
    are useful to quantify how well map-makers are able to derive the I/Q/U
    components of the sky signal. This class computes the *inverse* condition
    numbers, which is the most widely used approach: condition numbers range
    from 1 (best case, perfect I/Q/U reconstruction) to infinity (worst case),
    while inverse condition numbers range from 0 (no possibility to disentangle
    I/Q/U) to 1 (best case).

    A typical usage of this class is to create an object and repeatedly call
    the :func:`ConditionMatrix.update` method with part of all the samples
    in the TOD. When all the TODs have been processed, the function
    :func:`ConditionMatrix.to_map` can be used to trigger the computation
    of the condition numbers and produce a map.
    '''

    def __init__(self, numpix: int):
        '''Create a ConditionMatrix object

        The `numpix` parameter specifies how many pixels the map should contain.
        In the case of Healpix maps, this should be the result of a call
        to healpy.nside2npix.
        '''
        self.numpix = numpix
        self.matr = np.zeros((numpix, 9), dtype='float64', order='F')

    def update(self, pixidx: Any, angle: Any):
        '''Update the condition matrix with new samples from a TOD.

        The arrays `pixidx` and `angle` must have the same number of elements.
        The first array associates each item in `angle` with a pixel in the sky.
        '''
        print('pixidx.shape =', pixidx.shape)
        print('matr.shape =', self.matr.shape)
        _m.update_condmatr(numpix=self.numpix, pixidx=pixidx,
                           angle=angle, m=self.matr)

    def to_map(self):
        '''Compute the inverse condition numbers and return them as a map.

        A pixel in the map is set to zero either if it has not been seen
        (hit count is zero), or if the components I/Q/U cannot be determined
        at all.
        '''
        seen_mask = self.matr[:, 0] > 0
        cond_map = np.zeros(self.numpix)

        # Ordered list of all the pixels which have an hit count larger than 0
        pixels = np.arange(self.matr.shape[0])[seen_mask]

        for cur_pixel in pixels:
            cond_map[cur_pixel] = 1.0 / \
                np.linalg.cond(np.reshape(self.matr[cur_pixel], (3, 3)))

        return cond_map

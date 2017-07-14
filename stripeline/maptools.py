#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

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

def nonoise_map(signal, pixidx, num_of_pixels):
    '''Convert a timeline into a map assuming no noise.

    This function estimates the map produced from ``signal`` (a vector
    containing the timeline of measurements), assuming that each sample
    in ``signal`` was looking at the sky along the direction specified
    by each element in ``pixidx`` (a vector containing the index of
    the pixels). The value of ``num_of_pixels`` is the length of the
    vector containing the map that is returned by this function.

    This function assumes that there is *no noise at all* in ``signal``.
    '''

    assert len(signal) == len(pixidx)
    assert isinstance(num_of_pixels, int)
    assert num_of_pixels > 0

    mappixels = np.zeros(num_of_pixels)
    observed = np.zeros(num_of_pixels, dtype='bool')

    for i in range(len(signal)):
        cur_pixel_pos = pixidx[i]
        if not observed[cur_pixel_pos]:
            mappixels[cur_pixel_pos] = signal[i]
            observed[cur_pixel_pos] = True

    return mappixels

def binned_map(signal, pixidx, num_of_pixels):
    '''Convert a timeline into a map assuming white noise with zero mean.

    This function estimates the map produced from ``signal`` (a vector
    containing the timeline of measurements), assuming that each sample
    in ``signal`` was looking at the sky along the direction specified
    by each element in ``pixidx`` (a vector containing the index of
    the pixels). The value of ``num_of_pixels`` is the length of the
    vector containing the map that is returned by this function.

    This function assumes that the only kind of noise in ``signal`` is
    uncorrelated noise with zero mean and symmetric probability function.

    This function returns a tuple containing the binned map and the hit map.

    The following example loads the pointing information and the signal TOD
    from a FITS file, creates a map and saves it to disk::

        from stripeline import maptools as mt
        import healpy
        from astropy.io import fits

        # Read pointings and signal from a FITS file
        with fits.open('toi.fits') as f:
            theta, phi, signal = [f[1].data.field(x)
                                  for x in ('THETA', 'PHI', 'SIGNAL')]

        NSIDE = 256
        pixidx = healpy.ang2pix(NSIDE, theta, phi)
        m, hits = mt.binned_map(signal, pixidx, healpy.nside2npix(pixidx))

        # Save both the sky map and the hit map
        healpy.write_map('map.fits', (m, hits))
    '''

    assert len(signal) == len(pixidx)
    assert isinstance(num_of_pixels, int)
    assert num_of_pixels > 0

    mappixels = np.zeros(num_of_pixels)
    hits = np.zeros(num_of_pixels, dtype='int')

    _m.binned_map(signal, pixidx, mappixels, hits)

    return mappixels, hits

#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

'''Map-related facilities
'''

from typing import Any, List

from collections import namedtuple

import stripeline._maptools as _m
import numpy as np
from mpi4py import MPI
from astropy.io import fits


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


class ToiProvider:
    '''Load a TOI and split it evenly among MPI processes.

    This is an abstract base class, and it should not be instantiated. Consider
    using any of its derived classes, like FitsToiProvider.'''

    def __init__(self, rank: int, num_of_processes: int):
        '''Create a new ToiProvider object.

        Parameters:
        * "rank" is the rank of the running MPI process
        * "num_of_processes" is the number of MPI processes
        '''
        self.rank = rank
        self.num_of_processes = num_of_processes
        self.total_num_of_samples = 0

    def get_signal(self):
        '''Return a vector containing the signal from the TOI.

        Only the part of the TOI that belongs to the rank of this process is returned.
        See the definition of ToiProvider.__init__'''
        return None

    def get_pixel_index(self):
        'Return a vector containing the pixel index for each sample in the TOI.'
        return None


FitsToiFile = namedtuple('FitsToiFile', ['file_name', 'num_of_samples'])


def read_fits_file_information(file_name: str, hdu=1) -> FitsToiFile:
    'Read the number of rows in the first tabular HDU of a FITS file'
    with fits.open(file_name) as fin:
        num_of_samples = fin[hdu].header['NAXIS2']

    return FitsToiFile(file_name=file_name, num_of_samples=num_of_samples)


def split_into_n(length: int, num_of_segments: int) -> List[int]:
    '''Split a set of "length" elements into "num_of_segments" subsets.

    Example:
    >>> split_into_n(10, 4)
    [2 3 2 3]
    >>> split_into_n(201, 2)
    [100 101]
    '''
    assert num_of_segments > 0
    assert length > num_of_segments

    start_points = np.array([int(i * length / num_of_segments)
                             for i in range(num_of_segments + 1)])
    return start_points[1:] - start_points[:-1]


FitsToiSegment = namedtuple('FitsToiSegment', ['file_name', 'first_element', 'num_of_elements'])

def assign_toi_files_to_processes(samples_per_processes: List[int], fits_files: List[FitsToiFile]):
    '''Given a list of samples to be processed by each MPI process, decide which files and samples
    must be loaded by each process.'''

    assert sum(samples_per_processes) == sum([x.num_of_samples for x in fits_files])

    result = []  # Type: List[List[FitsToiFile]]

    file_idx = 0
    element_idx = 0
    # Iterate over the MPI processes
    for samples_in_this_proc in samples_per_processes:
        # This is the list of FITS segments that the current MPI process is going to load
        segments = []  # Type: List[FitsToiSegment]
        elements_in_this_segment = 0
        # Iterate over the files to be read by the current MPI process
        while elements_in_this_segment < samples_in_this_proc:
            if fits_files[file_idx].num_of_samples - element_idx <= samples_in_this_proc:
                # The whole FITS file is going to be read by the current MPI process
                num = fits_files[file_idx].num_of_samples - element_idx
                segments.append(FitsToiSegment(file_name=fits_files[file_idx].file_name,
                                               first_element=element_idx,
                                               num_of_elements=num))
                elements_in_this_segment += num
                file_idx += 1
                element_idx = 0
            else:
                # This is the size of the segment we're going to append to "segments"
                num = samples_in_this_proc - elements_in_this_segment
                # Only a subset of this FITS file will be read by the current MPI process
                segments.append(FitsToiSegment(file_name=fits_files[file_idx].file_name,
                                               first_element=element_idx,
                                               num_of_elements=num))
                elements_in_this_segment += num
                element_idx += num

        result.append(segments)

    return result


class FitsToiProvider(ToiProvider):
    '''Distribute a TOI saved in FITS files among MPI processes.

    This class specializes ToiProvider in order to load the TOI from a set of FITS files.'''

    def __init__(self, rank: int, num_of_processes: int, file_names: List[str], comm=None):
        ToiProvider.__init__(self, rank, num_of_processes)

        self.fits_files = []  # Type: List[FitsToiFile]
        if rank == 0 or comm is None:
            for cur_file in file_names:
                self.fits_files.append(read_fits_file_information(cur_file))

        if comm:
            self.fits_files = comm.bcast(self.fits_files, root=0)

        self.total_num_of_samples = sum([x.num_of_samples for x in self.fits_files])
        self.samples_per_process = split_into_n(self.total_num_of_samples,
                                                num_of_processes)

        self.segments_per_process = assign_toi_files_to_processes(self.samples_per_process, 
                                                                  self.fits_files)

    def get_signal(self):
        # TODO: implement me!
        return None


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

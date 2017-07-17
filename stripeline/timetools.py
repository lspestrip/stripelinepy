#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from collections import namedtuple
from typing import List
import numpy as np
from astropy.io import fits


TimeChunk = namedtuple('TimeChunk', 'start_time num_of_samples')


def split_time_range(time_length: float,
                     num_of_chunks: int,
                     sampfreq: float,
                     time0=0.0) -> List[TimeChunk]:
    '''Split a time interval in a number of chunks.

    Return a list of objects of kind :class:`stripeline.timetools.TimeChunk`.
    '''

    delta_time = time_length / num_of_chunks

    result = []
    for chunk_idx in range(num_of_chunks):
        # Determine the time of each sample in this chunk
        cur_time = chunk_idx * delta_time
        chunk_time0 = np.ceil(cur_time * sampfreq) / sampfreq - cur_time
        start_time = time0 + cur_time + chunk_time0
        num_of_samples = int(delta_time * sampfreq)
        result.append(TimeChunk(start_time=start_time,
                                num_of_samples=num_of_samples))

    return result


class ToiProvider:
    '''Load a TOI and split it evenly among MPI processes.

    .. note:: This is an abstract base class, and it should not be instantiated.
              Consider using any of its derived classes, like
              :class:`stripeline.timetools.FitsToiProvider`.

    In the case of a run split among many MPI processes, this class balances the
    load of a long TOI. If every MPI process creates a
    :class:`stripeline.timetools.ToiProvider` object, every object will take
    responsibility of reading one section of the TOI. The methods
    :func:`stripeline.timetools.ToiProvider.get_signal`,
    :func:`stripeline.timetools.ToiProvider.get_pointings`, and
    :func:`stripeline.timetools.ToiProvider.get_pixel_index` can be used by
    processes to read the chunk of data which belongs to each.
    '''

    def __init__(self, rank: int, num_of_processes: int):
        '''Create a new object.

        Parameters:
        * "rank" is the rank of the running MPI process
        * "num_of_processes" is the number of MPI processes
        '''
        self.rank = rank
        self.num_of_processes = num_of_processes
        self.total_num_of_samples = 0

    def get_signal(self):
        '''Return a vector containing the signal from the TOI.

        Only the part of the TOI that belongs to the rank of this process is
        returned.'''
        return None

    def get_pixel_index(self):
        '''Return a vector containing the pixel index for each sample in the
        TOI.

        Only the part of the TOI that belongs to the rank of this process is
        returned.'''
        return None

    def get_pointings(self):
        '''Return two vectors containing the colatitude and longitude for each
        sample in the TOI.

        Only the part of the TOI that belongs to the rank of this process is
        returned.'''
        return None, None


ToiFile = namedtuple('ToiFile', ['file_name', 'num_of_samples'])


def read_fits_file_information(file_name: str, hdu=1) -> ToiFile:
    '''Read the number of rows in the first tabular HDU of a FITS file

    Return a :class:`stripeline.timetools.ToiFile` object.
    '''
    with fits.open(file_name) as fin:
        num_of_samples = fin[hdu].header['NAXIS2']

    return ToiFile(file_name=file_name, num_of_samples=num_of_samples)


def split_into_n(length: int, num_of_segments: int) -> List[int]:
    '''Split a set of `length` elements into `num_of_segments` subsets.

    Example::

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


def assign_toi_files_to_processes(samples_per_processes: List[int],
                                  fits_files: List[ToiFile]):
    '''Determine how to balance the load of TOI files among processes.

    Given a list of samples to be processed by each MPI process, decide which
    files and samples must be loaded by each process, using the principle that
    all the processes should read the same number of files, when possible.

    Return a list of :class:`stripeline.timetools.ToiFile` objects.
    '''

    assert (sum(samples_per_processes) ==
            sum([x.num_of_samples for x in fits_files]))

    result = []  # Type: List[List[ToiFile]]

    file_idx = 0
    element_idx = 0
    # Iterate over the MPI processes
    for samples_in_this_proc in samples_per_processes:
        # This is the list of FITS segments that the current MPI process is
        # going to load
        segments = []  # Type: List[ToiFileSegment]
        elements_in_this_segment = 0
        # Iterate over the files to be read by the current MPI process
        while elements_in_this_segment < samples_in_this_proc:
            if fits_files[file_idx].num_of_samples - element_idx <= samples_in_this_proc:
                # The whole FITS file is going to be read by the current MPI
                # process
                num = fits_files[file_idx].num_of_samples - element_idx
                segments.append(ToiFileSegment(file_name=fits_files[file_idx].file_name,
                                               first_element=element_idx,
                                               num_of_elements=num))
                elements_in_this_segment += num
                file_idx += 1
                element_idx = 0
            else:
                # This is the size of the segment we're going to append to "segments"
                num = samples_in_this_proc - elements_in_this_segment
                # Only a subset of this FITS file will be read by the current MPI process
                segments.append(ToiFileSegment(file_name=fits_files[file_idx].file_name,
                                               first_element=element_idx,
                                               num_of_elements=num))
                elements_in_this_segment += num
                element_idx += num

        result.append(segments)

    return result


ToiFileSegment = namedtuple(
    'ToiFileSegment', ['file_name', 'first_element', 'num_of_elements'])


class FitsToiProvider(ToiProvider):
    '''Distribute a TOI saved in FITS files among MPI processes.

    This class specializes :class:`stripeline.timetools.ToiProvider` in order to
    load the TOI from a set of FITS files.'''

    def __init__(self,
                 rank: int,
                 num_of_processes: int,
                 file_names: List[str],
                 comm=None):
        ToiProvider.__init__(self, rank, num_of_processes)

        self.fits_files = []  # Type: List[ToiFile]
        if rank == 0 or comm is None:
            for cur_file in file_names:
                self.fits_files.append(read_fits_file_information(cur_file))

        if comm:
            self.fits_files = comm.bcast(self.fits_files, root=0)

        self.total_num_of_samples = sum(
            [x.num_of_samples for x in self.fits_files])
        self.samples_per_process = split_into_n(self.total_num_of_samples,
                                                num_of_processes)

        self.segments_per_process = \
            assign_toi_files_to_processes(self.samples_per_process,
                                          self.fits_files)

    def get_signal(self):
        # TODO: implement me!
        return None

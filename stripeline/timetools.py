#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from collections import namedtuple
from typing import List
import numpy as np


TimeChunk = namedtuple('TimeChunk', 'start_time num_of_samples')


def split_time_range(time_length: float,
                     num_of_chunks: int,
                     sampfreq: float,
                     time0=0.0) -> List[TimeChunk]:
    '''Split a time interval in a number of chunks.

    Return a list of 2-tuples of the form (START_TIME, NUM_OF_SAMPLES).
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

Handling timelines
==================

The ``stripeline.timeline`` submodule provides a number of facilities to
process timelines in parallel. These facilities can be divided into two
broad categories:

- Tools which find the optimal split of a number of samples amount a set of
  processes (:func:`stripeline.timetools.split_into_n`);
- Classes which ease the reading/writing of TOIs to disk
  (:class:`stripeline.timetools.ToiProvider`,
  :class:`stripeline.timetools.FitsToiProvider`).

All the functions and classes implemented in this submodule have been designed
for the purpose of providing the best read/write balance in MPI programs which
analyze timelines.

The following example shows a typical usage of some of the classes provided by
this module::

    from mpi4py import MPI
    import numpy as np
    from stripeline import timetools as tt 

    comm = MPI.COMM_WORLD
    
    # We assume that the data we want to load is in two TOI files named
    # A.fits and B.fits
    tois = tt.FitsToiProvider(rank=comm.Get_rank(), 
                              num_of_processes=comm.Get_size,
                              file_names=['A.fits', 'B.fits'])

    # Each MPI process gets a different array for "signal"…
    signal = tois.get_signal()

    # …and thus what we're computing here is a «local» mean
    local_mean = np.mean(signal)
    print('Process {rank} has loaded {n} samples with average {avg}'
          .format(rank=comm.Get_rank(), avg=local_mean, n=len(signal)))


Documentation
-------------

.. automodule:: stripeline.timetools
                :members:

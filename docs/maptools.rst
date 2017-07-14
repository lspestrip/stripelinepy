Map-related tools
=================

The functions and classes provided in this submodule allow to compute
maximum-likelihood maps and perform analysis on condition numbers.

Here is an overview of the tools provided by this submodule:

- :class:`ConditionMatrix` allows to compute the inverse condition numbers from
  a timeline. It is mildly useful in the context of STRIP data analysis, because

- :func:`binned_map` bins a map, assuming only uncorrelated noise.

The functions implemented in this code are still not able to take advantage of
MPI.

Documentation
-------------

.. automodule:: stripeline.maptools
                :members:

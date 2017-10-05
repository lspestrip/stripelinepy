Map-related tools
=================

The functions and classes provided in this submodule allow to compute
maximum-likelihood maps and perform analysis on condition numbers.

Here is an overview of the tools provided by this submodule:

- :class:`ConditionMatrix` allows to compute the inverse condition numbers from
  a timeline. It is mildly useful in the context of STRIP data analysis, because

- :func:`binned_map` bins a map, assuming only uncorrelated noise.

- :func:`binned_map_strip` bins a map from TOI acquired using STRIP-like
  polarimeters (i.e., able to measure I, Q, and U at the same time). It uses MPI
  to distribute the computation among a set of computation nodes.


Documentation
-------------

.. automodule:: stripeline.maptools
                :members:

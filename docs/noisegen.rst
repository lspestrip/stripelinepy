Random number generation
========================

Set of classes for random number generation.

The "stripeline.noisegen" module provides a number of classes to
generate pseudo-random numbers. It has been modeled after S.
Plaszczynski's "absrand" package version 1.1, and it returns the same
results when the same seeds are digested.

Here is a list of the classes implemented by this module:

- :class:`FlatRNG`: uniform distribution in the range :math:`[0, 1[`.

- :class:`NormalRNG`: Gaussian distribution with mean :math:`\mu=0`
  and standard deviation :math:`\sigma=1`.

- :class:`Oof2RNG`: :math:`1/f^2` distribution with custom knee
  frequency, sampling frequency and minimum frequency.

All the classes implement a ``next`` method and a ``fill_vector``
method (the latter is missing from the :class:`Oof2RNG` class). The
``fill_vector`` methods have been optimized for handling large
datasets.

Example
-------

Create an array of 100 random number in the range [0, 1[ with an
uniform distribution::

   rng = FlatRNG()
   vec = numpy.empty(100)
   rng.fill_vector(vec)


Documentation
-------------

.. automodule:: stripeline.noisegen
                :members:

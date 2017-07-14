.. _parameter-files:

Parameter files
===============

This module implements the function
:func:`stripeline.paramfile.load_yaml_files`, which loads a
sequence of YAML files and returns one dictionary. It is used by a number of
tools in the STRIP pipeline in order to load a set of parameters to be used in
simulations.

We explain here the philosophy behind this approach. Simulating an instrument
requires an *instrument database*, i.e., a database containing the parameters
that characterize the real instrument.  We call this set of parameters and
values the *nominal case*. Examples of parameters are: the noise
characteristics of the detectors, the geometrical configuration of the antennas
on the focal plane, and so on. One of the uses of a simulation pipeline is to
make forecasts of the impact of non-idealities in the instrument, i.e., what
happens when one of the parameters changes, but everything else stays the same
as in the nominal case.

In the case described above, the best solution is to keep a large database
containing the nominal value for each parameter, and to pair it with small
databases containing only the values that need to be customized for a specific
simulation. This is the reason why the tools provided in Stripeline accept an
arbitrary number of YAML files to specify the configuration to use. The YAML
files are read sequentially, and every time a parameter is found in the next
file, the new value overwrites the old one.

The PyYAML library offers an API to load one YAML file and return a dictionary.
This module provides the :func:`stripeline.paramfile.load_yaml_files` function
which wraps PyYAML and implements the mechanism described above.

As an example, suppose you have the following YAML file, named ``scan.yaml``,
which describes an hypothetical scanning strategy:

.. code-block:: yaml

    ---
    wheel1_rpm: 0.0
    wheel3_rpm: 1.0

    wheel1_angle0_deg: 0.0
    wheel2_angle0_deg: 25.0
    wheel3_angle0_deg: 0.0

    latitude_deg: 28.2916  # Tenerife
    overall_time_s: 31536000.0  # One year of observations
    sampling_frequency_hz: 50.0
    ...

If you want to test the case when the angle for wheel 2 is 30° instead of 25°,
you can create a new YAML file, which we name ``custom.yaml``, and only specify
the value of the new parameter:

.. code-block:: yaml

    ---
    wheel2_angle0_deg: 30.0
    ...

Now call :func:`stripeline.paramfile.load_yaml_files`::

    from stripeline.paramfile import load_yaml_files

    params = load_yaml_files(['scan.yaml', 'custom.yaml'])

The variable ``params`` will be a dictionary whose key ``wheel2_angle0_deg`` is
equal to 30.0, but all the other keys will be associated with the nominal values
specified in the file ``scan.yaml``.

Consider now the case where you invert the order of the two files::

    params = load_yaml_files(['custom.yaml', 'scan.yaml'])

In this case, ``custom.yaml`` is loaded first, then its only definition
(``wheel2_angle0_deg``) is overwritten by the same entry in ``scan.yaml``. In
this specific case, the call is perfectly equivalent to::

    params = load_yaml_files(['scan.yaml'])


Documentation
-------------

.. automodule:: stripeline.paramfile
                :members:

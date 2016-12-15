Instrument configuration
========================

The Stripeline code often needs to use numerical parameters that
characterize the instrument. These numbers are usually retrieved by means
of simulations or actual measurements, and they are kept in 
the Stripeline repository as `YAML <https://en.wikipedia.org/wiki/YAML>`_
files. Since YAML files are text files, they can be read and
modified with any text editor. In this section we describe the format of the
files used by Stripeline, as well as a few examples of their usage. To load
YAML files in Python, you can use the `PyYAML <http://pyyaml.org/wiki/PyYAML>`_
library.

All the files described in this section are available in the directory
`instrument`.

Focal plane
-----------
The file `strip_focal_plane.yaml` contains the geometry of the focal plane,
i.e., the orientation of the 49 horns. Each orientation is a 3D vector of
length one which points toward the point on the sky sphere where the centre
of the main beam is located. The boresight direction coincides with horn I0,
and it is conventionally set to be `(0, 0, 1)` (the z axis).

Here are a reduced version of the file, containing only two horns:

.. code-block:: yaml

    ---
    I0:
        id: 0              
        color: indigo        
        module_id: 0
        orientation:
        - 4.720000e-06
        - -0.000000e+00                                                                                                                               
        - 1.000000e+00                                                                                                                               
                                                                                                                                                
    I1:
        id: 1              
        color: indigo        
        module_id: 1
        orientation:
        - -1.077670e-02
        - -1.876756e-02                                                                                                                               
        - 9.997658e-01                                                                                                                               
    ...

Each entry contains the following items:

=============== ======= ==============================================
Name            Type    Meaning
=============== ======= ==============================================
``id``          int     Unique index of the horn (0-48)
``color``       str     Color of the module to whom the horn belongs
``module_id``   int     Index of the horn within the module (0-6)
``orientation`` tuple   3D vector of length one
=============== ======= ==============================================


The PyYAML module loads YAML files into dictionaries. So, in order to access the
``color`` field of the horn ``I0``, you can write::

    with open('instrument/strip_focal_plane.yaml', 'rt') as f:
        d = yaml.load(f)
        print(d['I0']['color'])  # prints "indigo"


The following plot shows the orientation in the UV plane of the 49 horns, where
U and V are the X and Y components of the orientations:

.. image:: strip_focal_plane_plot.svg

The plot has been created using the following script:

.. literalinclude:: strip_focal_plane_plot.py

Scanning strategy
-----------------

.. automodule:: stripeline.scanning
                :members:


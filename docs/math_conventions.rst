Mathematical conventions used in the code
=========================================

This section of the Stripeline documentation covers the conventions
used in the mathematical formulae implemented by the code. It is
important to have this reference in hand when studying the
implementation of Stripeline.


Vectors
-------

Stripeline uses a right-handed coordinate system. The following cross
products uniquely define the coordinate system:

.. math::

   \hat e_x \times \hat e_y &= \hat e_z,

   \hat e_y \times \hat e_z &= \hat e_x,

   \hat e_z \times \hat e_x &= \hat e_y


.. image:: right-handed-system.svg


Convention for measuring polarization
-------------------------------------

Polarization angles
+++++++++++++++++++


Polarization measurements in the CMB world are usually done using the I, Q, U,
and V `Stokes parameters <https://en.wikipedia.org/wiki/Stokes_parameters>`_,
which require to fix a reference frame. There are two reference frames used in
Stripeline:

1. The reference frame of the focal plane is assumed in TOI files. In this case,
   the polarization angle is zero when it is pointing along the direction from
   detector ``I3`` to detector ``I6`` (see image below). It increases
   counterclockwise, and it is always measured in radians.

.. image:: strip_focal_plane_plot.svg

2. The celestial reference frame assumes that a polarization angle is zero when
   it is aligned along the direction from the South Celestial Pole to the North
   Celestial Pole.

   In this case too, the angle is measured counterclockwise (thus following
   the order North-NW-West-SW-South-SE-East-NE), and it is measured in radians.


Polarization in the celestial reference frame
+++++++++++++++++++++++++++++++++++++++++++++

Traditionally, the CMB community has always used the COSMO convention
for defining polarization angles and Stokes vector. This conflicted
with the convention used by the International Astronomical Union
(IAU), and the result was a sign reversal of the U Stokes component.

Stripeline follows the `recommendation
<https://aas.org/files/resources/iau_polarization_angle.pdf>`_ issued
on December 8th 2015 by the IAU, and it therefore does *not* use the
same convention used by other CMB datasets like `Lambda
<https://lambda.gsfc.nasa.gov/product/about/pol_convention.cfm>`_ and
`Planck
<https://wiki.cosmos.esa.int/planckpla2015/index.php/Sky_temperature_maps#Polarization_convention_used_in_the_Planck_project>`_.
See also the `Healpix documentation
<http://healpix.jpl.nasa.gov/html/intronode12.htm>`_; note that tools
like `anafast` do not like the IAU convention, and they will crash
when dealing with this kind of files. Stripeline is immune to such
deficiency.


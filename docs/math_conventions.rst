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

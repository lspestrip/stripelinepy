#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'Calculations with polarization angles.'

import numpy as np


def rotate_qu(q_from, u_from, psi, inverse=False):
    '''Apply a rotation to a set of Q/U Stokes parameters

    The parameters ``q_from``, ``u_from`` and ``psi`` are arrays of $N$
    elements. The arrays ``q_from`` and ``u_from`` are measured in some
    reference frame, and ``psi`` contains the angles (in radians) of the
    rotation to be performed.

    Setting "inverse" to True will invert the transformation, i.e., it will
    rotate by an angle equal to ``-psi``.

    Return a pair containing the two arrays ``q_from`` and ``u_from`` in the new
    reference frame.'''

    assert len(q_from) == len(u_from)
    assert len(q_from) == len(psi)

    if inverse:
        cos2psi = np.cos(-2.0 * psi)
        sin2psi = np.sin(-2.0 * psi)
    else:
        cos2psi = np.cos(2.0 * psi)
        sin2psi = np.sin(2.0 * psi)

    q_to = cos2psi * q_from + sin2psi * u_from
    u_to = -sin2psi * q_from + cos2psi * u_from

    return q_to, u_to

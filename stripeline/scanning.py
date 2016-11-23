#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Scanning strategy simulation
'''

import logging as log
import os.path
from collections import namedtuple
from typing import Any, List
import click
import healpy
import numpy as np
from astropy.io import fits

import stripeline.quaternions as q
import stripeline.timetools as timetools


def time_to_rot_angle(time_vec: Any, rpm: float) -> Any:
    '''Return a set of angles given a set of times and the RPMs.abs

    RPM is Rotation Per Minute, of course!'''

    assert rpm >= 0.0

    if rpm == 0.0:
        return np.zeros_like(time_vec)
    else:
        return 2 * np.pi * time_vec * (rpm / 60.0)


def save_tod(time, theta, phi, psi, file_name: str):
    ''' Save a TOD into a FITS file'''
    cols = [
        fits.Column(name=name, format=fmt, unit=unit, array=arr)
        for name, fmt, unit, arr in (('TIME', 'D', 's', time),
                                     ('THETA', 'D', 'rad', theta),
                                     ('PHI', 'D', 'rad', phi),
                                     ('PSI', 'D', 'rad', psi))
    ]
    hdu = fits.BinTableHDU.from_columns(cols)
    hdu.writeto(file_name, clobber=True)
    log.info('file "%s" written successfully', file_name)


@click.command()
@click.argument('output_path')
@click.option('--wheel1-rpm',
              'wheel1_rpm',
              type=float,
              default=0.0,
              help='Rotations per minute of the first (focal plane) wheel')
@click.option('--wheel3-rpm',
              'wheel3_rpm',
              type=float,
              default=1.0,
              help='Rotations per minute of the third (ground) wheel')
@click.option('--wheel1-angle0',
              'wheel1_angle0',
              type=float,
              default=0.0,
              help='Initial angle of the first (focal plane) wheel [deg]')
@click.option('--wheel2-angle0',
              'wheel2_angle0',
              type=float,
              default=10.0,
              help='Initial angle of the second (elevation) wheel [deg]')
@click.option('--wheel3-angle0',
              'wheel3_angle0',
              type=float,
              default=0.0,
              help='Initial angle of the third (ground) wheel [deg]')
@click.option('--latitude',
              'latitude',
              type=float,
              default=28.2916,
              help='Latitude of the observing site (North is positive) [deg]')
@click.option('--time',
              'time_length',
              type=float,
              default=3600.0,
              help='Amount of observation time [s]')
@click.option('--samp',
              'sampfreq',
              type=float,
              default=50.0,
              help='Sampling frequency [Hz]')
@click.option('--num-of-chunks',
              '-n',
              type=int,
              default=1,
              help='Number of chunks for splitting the computation')
def main(output_path, wheel1_rpm, wheel3_rpm, wheel1_angle0, wheel2_angle0,
         wheel3_angle0, latitude, time_length, sampfreq, num_of_chunks):
    '''This function is called when the script is ran from the command line.'''

    log.basicConfig(
        level=log.INFO, format='%(asctime)s %(levelname)s] %(message)s')

    num_of_samples = int(time_length * sampfreq)
    log.info('%d samples will be processed in %d steps', num_of_samples,
             num_of_chunks)

    x_vec = np.array([1, 0, 0])
    z_vec = np.array([0, 0, 1])

    chunks = timetools.split_time_range(time_length=time_length,
                                        num_of_chunks=num_of_chunks,
                                        sampfreq=sampfreq,
                                        time0=0.0)
    for chunk_idx, cur_chunk in enumerate(chunks):
        start_time, samples_per_chunk = cur_chunk

        time_vec = start_time + np.arange(samples_per_chunk) / sampfreq

        # Determine the angle of each wheel (the second wheel is the simplest)
        wheel1_angle = np.deg2rad(wheel1_angle0) + time_to_rot_angle(
            time_vec, wheel1_rpm)
        wheel3_angle = np.deg2rad(wheel3_angle0) + time_to_rot_angle(
            time_vec, wheel3_rpm)

        tile_x = np.reshape(np.tile(x_vec, time_vec.size), (-1, 3))
        tile_z = np.reshape(np.tile(z_vec, time_vec.size), (-1, 3))
        # Build the wheel quaternions
        qwheel1 = q.qfromaxisangle(tile_z, wheel1_angle)
        qwheel2 = np.reshape(
            np.tile(
                q.qfromaxisangle([x_vec], [np.deg2rad(wheel2_angle0)]),
                time_vec.size), (-1, 4))
        qwheel3 = q.qfromaxisangle(tile_z, wheel3_angle)

        # This is in the ground's reference frame
        ground_quat = q.qmul(qwheel3, q.qmul(qwheel2, qwheel1))
        ground_dirs = q.qrotate(tile_z, ground_quat)

        # Now we convert from the ground reference frame to the Earth's centre
        location_quat = np.reshape(
            np.tile(
                q.qfromaxisangle([x_vec], [-np.deg2rad(90.0 - latitude)]),
                time_vec.size), (-1, 4))
        earth_rot_quat = q.qfromaxisangle(tile_z,
                                          2 * np.pi * time_vec / 86400.0)
        quat = q.qmul(earth_rot_quat, q.qmul(location_quat, ground_quat))
        dirs = q.qrotate(tile_z, quat)
        poldirs = q.qrotate(tile_x, quat)
        theta, phi = healpy.vec2ang(dirs)
        psi = np.arccos(poldirs[:, 2])

        output_file_name = os.path.join(
            output_path, 'pointings_{0:04d}.fits'.format(chunk_idx))
        save_tod(time=time_vec,
                 theta=theta,
                 phi=phi,
                 psi=psi,
                 file_name=output_file_name)


if __name__ == '__main__':
    main()

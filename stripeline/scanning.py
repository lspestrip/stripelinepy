#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

'''Functions to quickly simulate the observation of the sky through the year.

We call *scanning strategy* the way the instrument changes its orientation
towards the sky with the passing of time. It is encoded as a set of times and
sky coordinates, and it depends on the way the Earth rotates and the instrument
wheels are operated.

Stripeline offers a set of utilities to generate a scanning strategy, given a
set of instrumental parameters. These are used to determine which configuration
has the most desirable properties in terms of the scientific outcome (sky
coverage, integration time per pixel, etc.).

The function which creates pointing information from a description of the
scanning strategy is :meth:`~stripeline.scanning.generate_pointings`, which
depends on the class :class:`~stripeline.scanning.ScanningStrategy`. This
function is `quick`, in the sense that it does not take into account many
time-dependent effects (like the nutation of the Earth's axis), it just models
the Earth as a sphere rotating around a fixed axis with constant angular
velocity. To make a more realistic simulation, see Sect.
:ref:`accurate-generation-of-pointing-timelines`.

Here is a short example which shows how to use these facilities::

    import stripeline.scanning as sc

    def save_tod(pointings,
                 scanning: sc.ScanningStrategy,
                 dir_vec,
                 index: int):
        # Here you can save/use "pointings", which is a 4xn matrix
        pass

    scanning = sc.ScanningStrategy(wheel3_rpm=1.0,
                                   wheel2_angle0_deg=45.0,
                                   latitude_deg=28.3,
                                   overall_time_s=3600.0,
                                   sampling_frequency_hz=50.0)
    sc.generate_pointings(scanning=scanning,
                          dir_vec=[0., 0., 1.],
                          num_of_chunks=1,
                          tod_callback=save_tod)

This module provides the class :class:`~stripeline.scanning.TodWriter`, which
saves pointing information in FITS files.
'''

import logging as log
import io
import os.path
import sys
from typing import Any
import click
import healpy
import numpy as np
from astropy.io import fits
import yaml

import stripeline.quaternions as q
import stripeline.timetools as timetools


class ScanningStrategy:
    '''Parameters of a sky scanning strategy.

    This class holds together a number of information needed to define a
    strategy to scan the sky. It works like a named tuple, but it allows
    members to be changed after the object has been created.

    The following parameters are accepted:

    - `wheel1_rpm`: rotations per minute of the first wheel
        (focal plane wheel);
    - `wheel3_rpm`: rotations per minute of the third wheel
        (ground wheel, also called «azimuth wheel»);
    - `wheel1_angle0_deg`: angle of the first wheel when the simulation
        starts (degrees);
    - `wheel2_angle0_deg`: angle of the second wheel (elevation wheel)
        when the simulation starts (degrees);
    - `wheel3_angle0_deg`: angle of the third wheel when the simulation
        starts (degrees);
    - `latitude_deg`: latitude (in degrees) of the observing site;
    - `overall_time_s`: overall duration of the observation (in seconds);
    - `sampling_frequency_hz`: sampling frequency of the detector (in Hz).

     The class implements YAML serialization through the methods
     :meth:`~stripeline.scanning.ScanningStrategy.load` and
     :meth:`~stripeline.scanning.ScanningStrategy.save`.'''

    def __init__(self,
                 wheel1_rpm=0.0,
                 wheel3_rpm=0.0,
                 wheel1_angle0_deg=0.0,
                 wheel2_angle0_deg=0.0,
                 wheel3_angle0_deg=0.0,
                 latitude_deg=0.0,
                 overall_time_s=0.0,
                 sampling_frequency_hz=0.0):
        self.wheel1_rpm = wheel1_rpm
        self.wheel3_rpm = wheel3_rpm
        self.wheel1_angle0_deg = wheel1_angle0_deg
        self.wheel2_angle0_deg = wheel2_angle0_deg
        self.wheel3_angle0_deg = wheel3_angle0_deg
        self.latitude_deg = latitude_deg
        self.overall_time_s = overall_time_s
        self.sampling_frequency_hz = sampling_frequency_hz

    def validate(self):
        '''Raise a ValueError if the scanning strategy is invalid.'''

        if not isinstance(self.wheel1_rpm, float) or self.wheel1_rpm < 0.0:
            raise ValueError('invalid value for wheel1_rpm ({0})'
                             .format(self.wheel1_rpm))

        if not isinstance(self.wheel3_rpm, float) or self.wheel3_rpm < 0.0:
            raise ValueError('invalid value for wheel3_rpm ({0})'
                             .format(self.wheel3_rpm))

        if not isinstance(self.wheel1_angle0_deg, float):
            raise ValueError('invalid value for wheel1_angle0_deg ({0})'
                             .format(self.wheel1_angle0_deg))

        if not isinstance(self.wheel2_angle0_deg, float):
            raise ValueError('invalid value for wheel2_angle0_deg ({0})'
                             .format(self.wheel2_angle0_deg))

        if not isinstance(self.wheel3_angle0_deg, float):
            raise ValueError('invalid value for wheel3_angle0_deg ({0})'
                             .format(self.wheel3_angle0_deg))

        if not isinstance(self.latitude_deg, float) or \
                self.latitude_deg < 0.0 or self.latitude_deg > 90.0:
            raise ValueError('invalid value for latitude_deg ({0})'
                             .format(self.latitude_deg))

        if not isinstance(self.sampling_frequency_hz, float) or \
                self.sampling_frequency_hz <= 0.0:
            raise ValueError('invalid value for sampling_frequency_hz ({0})'
                             .format(self.sampling_frequency_hz))

    def save(self, stream):
        '''Write a YAML representation of `self` into the stream.'''

        yaml.dump({'wheel1_rpm': self.wheel1_rpm,
                   'wheel3_rpm': self.wheel3_rpm,
                   'wheel1_angle0_deg': self.wheel1_angle0_deg,
                   'wheel2_angle0_deg': self.wheel2_angle0_deg,
                   'wheel3_angle0_deg': self.wheel3_angle0_deg,
                   'latitude_deg': self.latitude_deg,
                   'overall_time_s': self.overall_time_s,
                   'sampling_frequency_hz': self.sampling_frequency_hz},
                  stream=stream,
                  explicit_start=True,
                  explicit_end=True)

    def load(self, input):
        '''Build a :class:`ScanningStrategy` object from its YAML representation.

        The parameter "input" can either be a file object, a dictionary or a string.'''
        if isinstance(input, dict):
            d = input
        else:
            d = yaml.load(input)

        self.wheel1_rpm = d['wheel1_rpm']
        self.wheel3_rpm = d['wheel3_rpm']
        self.wheel1_angle0_deg = d['wheel1_angle0_deg']
        self.wheel2_angle0_deg = d['wheel2_angle0_deg']
        self.wheel3_angle0_deg = d['wheel3_angle0_deg']
        self.latitude_deg = d['latitude_deg']
        self.overall_time_s = d['overall_time_s']
        self.sampling_frequency_hz = d['sampling_frequency_hz']


def time_to_rot_angle(time_vec: Any, rpm: float) -> Any:
    '''Return a set of angles given a set of times and the RPMs.

    RPM is Rotation Per Minute, of course!'''

    assert rpm >= 0.0

    if rpm == 0.0:
        return np.zeros_like(time_vec)
    else:
        return 2 * np.pi * time_vec * (rpm / 60.0)


def generate_pointings(scanning: ScanningStrategy,
                       dir_vec=[0, 0, 1],
                       num_of_chunks=1,
                       tod_callback=None):
    '''Generate a set of pointing directions.

    Simulate the scanning of the sky with the parameters provided in
    `scanning`, `dir_vec`. The `tod_callback` parameter is a function
    which is called whenever a new chunk of samples has been calculated.
    (It is fine if it is set to ``None``: in this case, pointings will
    be silently thrown away once they have been computed.)

    The callback must accept the following parameters:

    - `pointings`: 4xn matrix containing the time (in seconds),
      colatitude (in radians), longitude (ditto), and polarization angle
      (ditto), each in its own column;
    - `scanning`: copy of the parameter passed to this function;
    - `dir_vec`: copy of the parameter passed to this function;
    - `index`: counter which keeps track of how many times the
      callback has been called, starting from 0.
    '''
    x_vec = np.array([1, 0, 0])
    z_vec = np.array([0, 0, 1])

    chunks = timetools.split_time_range(time_length=scanning.overall_time_s,
                                        num_of_chunks=num_of_chunks,
                                        sampfreq=scanning.sampling_frequency_hz,
                                        time0=0.0)
    for chunk_idx, cur_chunk in enumerate(chunks):
        start_time, samples_per_chunk = cur_chunk

        time_vec = start_time + \
            np.arange(samples_per_chunk) / scanning.sampling_frequency_hz

        # Determine the angle of each wheel (the second wheel is the simplest)
        wheel1_angle = np.deg2rad(scanning.wheel1_angle0_deg) + time_to_rot_angle(
            time_vec, scanning.wheel1_rpm)
        wheel3_angle = np.deg2rad(scanning.wheel3_angle0_deg) + time_to_rot_angle(
            time_vec, scanning.wheel3_rpm)

        tile_dir = np.reshape(np.tile(dir_vec, time_vec.size), (-1, 3))
        tile_x = np.reshape(np.tile(x_vec, time_vec.size), (-1, 3))
        tile_z = np.reshape(np.tile(z_vec, time_vec.size), (-1, 3))
        # Build the wheel quaternions
        qwheel1 = q.qfromaxisangle(tile_dir, wheel1_angle)
        qwheel2 = np.reshape(
            np.tile(
                q.qfromaxisangle(
                    [x_vec], [np.deg2rad(scanning.wheel2_angle0_deg)]),
                time_vec.size), (-1, 4))
        qwheel3 = q.qfromaxisangle(tile_z, wheel3_angle)

        # This is in the ground's reference frame
        ground_quat = q.qmul(qwheel3, q.qmul(qwheel2, qwheel1))

        # Now we convert from the ground reference frame to the Earth's centre
        location_quat = np.reshape(
            np.tile(
                q.qfromaxisangle(
                    [x_vec], [np.deg2rad(90.0 - scanning.latitude_deg)]),
                time_vec.size), (-1, 4))
        earth_rot_quat = q.qfromaxisangle(tile_z,
                                          2 * np.pi * time_vec / 86400.0)
        quat = q.qmul(earth_rot_quat, q.qmul(location_quat, ground_quat))
        dirs = q.qrotate(tile_z, quat)
        poldirs = q.qrotate(tile_x, quat)
        theta, phi = healpy.vec2ang(dirs)

        # The north direction for a vector v is just -dv/dtheta, as
        # theta is the colatitude and moves along the meridian
        thetapol, phipol = healpy.vec2ang(dirs)
        northdir = np.column_stack((-np.cos(thetapol) * np.cos(phipol),
                                    -np.cos(thetapol) * np.sin(phipol),
                                    np.sin(thetapol)))

        # The counterclockwise/clockwise measurement of the polarization angle
        # is determined by the ordering of the terms in the call to "np.cross"
        cos_psi = np.clip(np.sum(northdir * poldirs, axis=1), -1.0, 1.0)
        cross = np.cross(northdir, poldirs)
        sin_psi = np.clip(np.sum(cross * cross, axis=1), -1.0, 1.0)
        psi = np.arctan2(sin_psi, cos_psi)
        psi *= np.sign(np.sum(cross * dirs, axis=1))

        if tod_callback is not None:
            tod_callback(pointings=np.column_stack((time_vec, theta, phi, psi)),
                         scanning=scanning,
                         dir_vec=dir_vec,
                         index=chunk_idx)


class TodWriter:
    '''Write a TOD.

    This class has been designed to be used together with
    :meth:`~stripeline.scanning.generate_pointings`.

    You create an instance of the object and then pass it to
    :meth:`~stripeline.scanning.generate_pointings`, like in the following way::

        writer = TodWriter(outdir='/storage',
                           file_name_mask='mytod_{index:04d}.fits.gz')
        generate_pointings(..., tod_callback=writer)

    As you can see, you can use the `index` key in the `file_name_mask`
    parameter to separate the files in chunks. The number of times `writer` is
    called depends on the parameter `num_of_chunks` passed to
    :meth:`~stripeline.scanning.generate_pointings`.
    '''

    def __init__(self,
                 outdir='.',
                 file_name_mask='pointings_{index:04d}.fits'):
        self.outdir = outdir
        self.file_name_mask = file_name_mask

    def __call__(self,
                 pointings,
                 scanning: ScanningStrategy,
                 dir_vec,
                 index: int):
        ''' Save a TOD into a FITS file'''

        file_name = os.path.join(self.outdir,
                                 self.file_name_mask.format(index=index))
        cols = [
            fits.Column(name=name, format=fmt, unit=unit, array=arr)
            for name, fmt, unit, arr in (('TIME', 'D', 's', pointings[:, 0]),
                                         ('THETA', 'D', 'rad',
                                          pointings[:, 1]),
                                         ('PHI', 'D', 'rad', pointings[:, 2]),
                                         ('PSI', 'D', 'rad', pointings[:, 3]))
        ]
        hdu = fits.BinTableHDU.from_columns(cols, name='TOD')
        hdu.header['FSTTIME'] = (
            pointings[0, 0], 'Time of the first sample in the file [s]')
        hdu.header['LSTTIME'] = (
            pointings[-1, 0], 'Time of the last sample in the file [s]')
        hdu.header['DIRX'] = (dir_vec[0], 'X component of the beam axis')
        hdu.header['DIRY'] = (dir_vec[1], 'Y component of the beam axis')
        hdu.header['DIRZ'] = (dir_vec[2], 'Z component of the beam axis')
        hdu.header['SAMPFREQ'] = (scanning.sampling_frequency_hz,
                                  'Sampling frequency [Hz]')
        hdu.header['SITELAT'] = (
            scanning.latitude_deg, 'Latitude of the site [deg]')
        hdu.header['W1RPM'] = (scanning.wheel1_rpm,
                               'Angular speed of wheel 1 [rpm]')
        hdu.header['W3RPM'] = (scanning.wheel3_rpm,
                               'Angular speed of wheel 3 [rpm]')
        hdu.header['W1ANG0'] = (
            scanning.wheel1_angle0_deg, 'Start angle for wheel 1 [deg]')
        hdu.header['W2ANG0'] = (
            scanning.wheel2_angle0_deg, 'Start angle for wheel 2 [deg]')
        hdu.header['W3ANG0'] = (
            scanning.wheel3_angle0_deg, 'Start angle for wheel 3 [deg]')
        hdu.header['TIMELEN'] = (
            scanning.overall_time_s, 'Time span of the *whole* sim [s]')
        hdu.header['TODIDX'] = (index, '0-based index of this file')

        with io.StringIO() as primary_data:
            scanning.save(stream=primary_data)
            raw_bytes = np.array(list(primary_data.getvalue().encode('utf-8')))
            primhdu = fits.PrimaryHDU(data=raw_bytes)

        hdulist = fits.HDUList([primhdu, hdu])
        hdulist.writeto(file_name, clobber=True)
        log.info('file "%s" written successfully', file_name)


@click.command()
@click.argument('output_path')
@click.option('--input-file',
              type=str,
              default=None,
              help='Path to a YAML file containing the parameters of the '
              'scanning strategy')
@click.option('--wheel1-rpm',
              'wheel1_rpm',
              type=float,
              default=None,
              help='Rotations per minute of the first (focal plane) wheel')
@click.option('--wheel3-rpm',
              'wheel3_rpm',
              type=float,
              default=None,
              help='Rotations per minute of the third (ground) wheel')
@click.option('--wheel1-angle0',
              'wheel1_angle0',
              type=float,
              default=None,
              help='Initial angle of the first (focal plane) wheel [deg]')
@click.option('--wheel2-angle0',
              'wheel2_angle0',
              type=float,
              default=None,
              help='Initial angle of the second (elevation) wheel [deg]')
@click.option('--wheel3-angle0',
              'wheel3_angle0',
              type=float,
              default=None,
              help='Initial angle of the third (ground) wheel [deg]')
@click.option('--latitude',
              'latitude',
              type=float,
              default=None,
              help='Latitude of the observing site (North is positive) [deg]')
@click.option('--time',
              'time_length',
              type=float,
              default=None,
              help='Amount of observation time [s]')
@click.option('--samp',
              'sampfreq',
              type=float,
              default=None,
              help='Sampling frequency [Hz]')
@click.option('--num-of-chunks',
              '-n',
              type=int,
              default=1,
              help='Number of chunks for splitting the computation')
@click.option('--direction',
              type=str,
              default='0,0,1',
              help='Pointing direction of the main beam with respect to '
              'the focal plane (3D vector, written as a comma-separated list '
              'of 3 numbers)')
def main(output_path, input_file, wheel1_rpm, wheel3_rpm, wheel1_angle0, wheel2_angle0,
         wheel3_angle0, latitude, time_length, sampfreq, num_of_chunks,
         direction):
    '''This function is called when the script is ran from the command line.'''

    log.basicConfig(
        level=log.INFO, format='%(asctime)s %(levelname)s] %(message)s')

    num_of_samples = int(time_length * sampfreq)
    log.info('%d samples will be processed in %d steps', num_of_samples,
             num_of_chunks)

    try:
        direction = np.array([float(x) for x in direction.split(',')])
        if len(direction) != 3:
            raise ValueError()
    except ValueError:
        log.error('pointing direction must be a comma-separated list of '
                  'three floating-point numbers (es., "0,0,1")')
        sys.exit(1)

    scanning = ScanningStrategy()
    if input_file is not None:
        with open(input_file, 'rt') as f:
            scanning.load(f)

    if wheel1_rpm is not None:
        scanning.wheel1_rpm = wheel1_rpm
    if wheel3_rpm is not None:
        scanning.wheel3_rpm = wheel3_rpm
    if wheel1_angle0 is not None:
        scanning.wheel1_angle0_deg = wheel1_angle0
    if wheel2_angle0 is not None:
        scanning.wheel2_angle0_deg = wheel2_angle0
    if wheel3_angle0 is not None:
        scanning.wheel3_angle0_deg = wheel3_angle0
    if latitude is not None:
        scanning.latitude_deg = latitude
    if time_length is not None:
        scanning.overall_time_s = time_length
    if sampfreq is not None:
        scanning.sampling_frequency_hz = sampfreq

    scanning.validate()

    writer = TodWriter(output_path)
    generate_pointings(scanning=scanning,
                       dir_vec=direction,
                       num_of_chunks=num_of_chunks,
                       tod_callback=writer)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Scanning strategy simulation
'''

import logging as log
import io
import os.path
import sys
from collections import namedtuple
from typing import Any
import click
import healpy
import numpy as np
from astropy.io import fits
import yaml

import stripeline.quaternions as q
import stripeline.timetools as timetools


ScanningStrategy = namedtuple('ScanningStrategy',
                              ['wheel1_rpm',
                               'wheel3_rpm',
                               'wheel1_angle0_deg',
                               'wheel2_angle0_deg',
                               'wheel3_angle0_deg',
                               'latitude_deg',
                               'overall_time_s',
                               'sampling_frequency_hz'])


def save_scanning_strategy(strategy: ScanningStrategy, stream):
    '''Write a YAML representation of `strategy` into the stream.'''

    yaml.dump(strategy._asdict(),
              stream=stream,
              explicit_start=True,
              explicit_end=True)


def load_scanning_strategy(stream) -> ScanningStrategy:
    '''Build a ScanningStrategy object from its YAML representation.'''
    return ScanningStrategy(**yaml.load(stream))


def time_to_rot_angle(time_vec: Any, rpm: float) -> Any:
    '''Return a set of angles given a set of times and the RPMs.

    RPM is Rotation Per Minute, of course!'''

    assert rpm >= 0.0

    if rpm == 0.0:
        return np.zeros_like(time_vec)
    else:
        return 2 * np.pi * time_vec * (rpm / 60.0)


def generate_pointings(scanning: ScanningStrategy,
                       dir_vec,
                       num_of_chunks: int,
                       tod_callback):
    '''Generate a set of pointing directions.

    Simulate the scanning of the sky with the parameters provided in
    `scanning`, `dir_vec`. The `tod_callback` parameter is a function
    which is called whenever a new chunk of samples has been calculated.
    (It is fine if it is set to ``None``: in this case, pointings will
    be silently thrown away once they have been computed.)

    The callback must accept the following parameters:
    - pointings: this is a 4xn matrix containing the time (in seconds),
      colatitude (in radians), longitude (ditto), and polarization angle
      (ditto), each in its own column;
    - scanning: this is a copy of the parameter passed to this function
    - dir_vec: this is a copy of the parameter passed to this function
    - index: this is a counter which keeps track of how many times the
      callback has been called, starting from 0
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
                    [x_vec], [-np.deg2rad(90.0 - scanning.latitude_deg)]),
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
        psi = np.arccos(np.sum(northdir * poldirs, axis=1))

        if tod_callback is not None:
            tod_callback(pointings=np.column_stack((time_vec, theta, phi, psi)),
                         scanning=scanning,
                         dir_vec=dir_vec,
                         index=chunk_idx)


class TodWriter:

    def __init__(self, outdir: str):
        self.outdir = outdir

    def __call__(self,
                 pointings,
                 scanning: ScanningStrategy,
                 dir_vec,
                 index: int):
        ''' Save a TOD into a FITS file'''

        file_name = os.path.join(self.outdir,
                                 'pointings_{0:04d}.fits'.format(index))
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
            save_scanning_strategy(strategy=scanning, stream=primary_data)
            raw_bytes = np.array(list(primary_data.getvalue().encode('utf-8')))
            primhdu = fits.PrimaryHDU(data=raw_bytes)

        hdulist = fits.HDUList([primhdu, hdu])
        hdulist.writeto(file_name, clobber=True)
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
@click.option('--direction',
              type=str,
              default=[0., 0., 1.],
              help='Pointing direction of the main beam with respect to '
              'the focal plane (3D vector, written as a comma-separated list '
              'of 3 numbers)')
def main(output_path, wheel1_rpm, wheel3_rpm, wheel1_angle0, wheel2_angle0,
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

    scanning = ScanningStrategy(wheel1_rpm=wheel1_rpm,
                                wheel3_rpm=wheel3_rpm,
                                wheel1_angle0_deg=wheel1_angle0,
                                wheel2_angle0_deg=wheel2_angle0,
                                wheel3_angle0_deg=wheel3_angle0,
                                latitude_deg=latitude,
                                overall_time_s=time_length,
                                sampling_frequency_hz=sampfreq)

    writer = TodWriter(output_path)
    generate_pointings(scanning=scanning,
                       dir_vec=direction,
                       num_of_chunks=num_of_chunks,
                       tod_callback=writer)

if __name__ == '__main__':
    main()

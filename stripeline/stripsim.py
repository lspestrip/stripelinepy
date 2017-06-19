#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import numpy as np
import click
import healpy
import os
import io
import logging as log
from astropy.io import fits
import scanning



class TodWriter:
    def __init__(self,
                 sky_map_I,
                 sky_map_Q,
                 sky_map_U,
                 outdir='.',
                 file_name_mask='TOI_{index:04d}.fits'):
        self.sky_map_I = sky_map_I
        self.sky_map_Q = sky_map_Q
        self.sky_map_U = sky_map_U
        self.outdir = outdir
        self.file_name_mask = file_name_mask

    def __call__(self,
                 pointings,
                 scanning: scanning.ScanningStrategy,
                 dir_vec,
                 index: int):

        ''' Save a TOD into a FITS file'''

        file_name = os.path.join(self.outdir,
                                 self.file_name_mask.format(index=index))
        pixidx = healpy.ang2pix(healpy.get_nside(self.sky_map_Q), pointings[:, 1], pointings[:, 2])

        TOI_I_sky = self.sky_map_I[pixidx]
        TOI_Q_sky = self.sky_map_Q[pixidx]
        TOI_U_sky = self.sky_map_U[pixidx]

        TwoPsi = pointings[:, 3] * 2
        TOI_I_beam = TOI_I_sky
        TOI_Q_beam = TOI_Q_sky*np.cos(TwoPsi) - TOI_U_sky*np.sin(TwoPsi)
        TOI_U_beam = TOI_Q_sky*np.sin(TwoPsi) + TOI_U_sky*np.cos(TwoPsi)

        det_output_1 = 1/4 * (TOI_I_beam + TOI_Q_beam)
        det_output_2 = 1/4 * (TOI_I_beam - TOI_Q_beam)
        det_output_3 = 1/4 * (TOI_I_beam + TOI_U_beam)
        det_output_4 = 1/4 * (TOI_I_beam - TOI_U_beam)

        cols = [
            fits.Column(name=name, format=fmt, unit=unit, array=arr)
            for name, fmt, unit, arr in (('TIME', 'D', 's', pointings[:, 0]),
                                         ('THETA', 'D', 'rad',
                                          pointings[:, 1]),
                                         ('PHI', 'D', 'rad', pointings[:, 2]),
                                         ('PSI', 'D', 'rad', pointings[:, 3]),
                                         ('DET1', 'D', 'K', det_output_1),
                                         ('DET2', 'D', 'K', det_output_2),
                                         ('DET3', 'D', 'K', det_output_3),
                                         ('DET4', 'D', 'K', det_output_4))
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
@click.argument('parameter_file')
@click.argument('sky_map_filename')
@click.argument('output_path')
def main(parameter_file, sky_map_filename, output_path):
    strategy = scanning.ScanningStrategy()
    with open(parameter_file, 'rt') as f:
        strategy.load(f)    
    sky_map = healpy.read_map(sky_map_filename, field=(0, 1, 2)) #0 = Temperature, 1 = Stokes Parameter Q, 2=Stokes Parameter U

    writer = TodWriter(sky_map[0], sky_map[1], sky_map[2], output_path)
 
    scanning.generate_pointings(strategy, [0, 0, 1], 1, writer)

if __name__ == '__main__':
    main()

from stripeline.maptools import binned_map
from astropy.io import fits
import healpy
import click
import numpy as np


@click.command()
@click.argument('tod_filename')
@click.argument('nside', type=int)
@click.argument('map_filename')
def main(tod_filename, nside, map_filename):
    f = fits.open(tod_filename)
    theta, phi, detQ1, detQ2, detU1, detU2 = [f[1].data.field(
        x) for x in ('THETA', 'PHI', 'DETQ1', 'DETQ2', 'DETU1', 'DETU2')]
    pixidx = healpy.ang2pix(nside, theta, phi)
    num_of_pixels = healpy.nside2npix(nside)
    Imap = binned_map(detQ1 + detQ2 + detU1 + detU2, pixidx, num_of_pixels)
    Qmap = binned_map(2 * (detQ1 - detQ2), pixidx, num_of_pixels)
    Umap = binned_map(2 * (detU1 - detU2), pixidx, num_of_pixels)

    healpy.write_map(map_filename, Imap)


if __name__ == '__main__':
    main()


f = fits.open('')

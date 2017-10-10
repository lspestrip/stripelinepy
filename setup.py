#!/usr/bin/env python

import os

NAME = 'stripeline'
VERSION = '0.1'
DESCRIPTION = 'A simulation pipeline for the LSPE/Strip instrument'
AUTHOR = 'Maurizio Tomasi'
AUTHOR_EMAIL = 'maurizio.tomasi@unimi.it'
LICENSE = 'MIT'
URL = 'https://github.com/ziotom78/stripeline'
FORTRAN2003_FLAG = '-std=f2003'


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# This branch is ran whenever there is some user that actually
# wants to install and use Stripeline, so we need to configure
# everything properly: NumPy, the Fortran and C modules, etc.
# We do not use setuptools but numpy.distutils, so that it is
# easier to tell how to compile Fortran and C files using f2py.

from numpy.distutils.core import setup, Extension
from numpy.distutils.misc_util import Configuration
def configuration(parent_package='', top_path=None):
    extensions = [Extension('fortran_routines',
                            sources=['stripeline/fortran_routines.f90'],
                            extra_f90_compile_args=[FORTRAN2003_FLAG]),
                    Extension('stripeline.quaternions',
                            sources=['stripeline/_quaternions.f90'],
                            extra_f90_compile_args=[FORTRAN2003_FLAG]),
                    Extension('stripeline._maptools',
                            sources=['stripeline/_maptools.f90'],
                            extra_f90_compile_args=[FORTRAN2003_FLAG]),
                    Extension('stripeline.rng',
                            sources=['stripeline/rng.pyf',
                                        'stripeline/rng.c'])]

    config = Configuration(NAME, parent_package, top_path,
                            version=VERSION,
                            description=DESCRIPTION,
                            author=AUTHOR,
                            author_email=AUTHOR_EMAIL,
                            license=LICENSE,
                            url=URL,
                            long_description=read('README.md'),
                            py_modules=['stripeline/stripsim'],
                            requires=['numpy', 'pyyaml', 'healpy'],
                            data_files=[('instrument', [
                                'instrument/scanning_strategy.yaml',
                                'instrument/strip_detectors.yaml',
                                'instrument/strip_focal_plane.yaml',
                            ])],
                            ext_modules=extensions)
    return config.todict()


if __name__ == '__main__':
    setup(**configuration(top_path=''))

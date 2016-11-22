#!/usr/bin/env python

from numpy.distutils.core import setup, Extension
from numpy.distutils.misc_util import Configuration

NAME = 'stripeline'
VERSION = '0.1'
DESCRIPTION = 'A simulation pipeline for the LSPE/Strip instrument'
FORTRAN2003_FLAG = '-std=f2003'


# Utility function to read the README file.
def read(fname):
    import os
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def configuration(parent_package='', top_path=None):
    extensions = [Extension('fortran_routines',
                            sources=['stripeline/fortran_routines.f90'],
                            extra_f90_compile_args=[FORTRAN2003_FLAG]),
                  Extension('stripeline.quaternions',
                            sources=['stripeline/_quaternions.f90'],
                            extra_f90_compile_args=[FORTRAN2003_FLAG]),
                  Extension('stripeline.rng',
                            sources=['stripeline/rng.pyf',
                                     'stripeline/rng.c'])]

    config = Configuration(NAME, parent_package, top_path,
                           version=VERSION,
                           description=DESCRIPTION,
                           author='Maurizio Tomasi',
                           author_email='maurizio.tomasi@unimi.it',
                           license='MIT',
                           url='https://github.com/ziotom78/stripeline',
                           long_description=read('README.md'),
                           py_modules=['stripeline/stripsim'],
                           requires=['numpy', 'pyyaml', 'healpy'],
                           ext_modules=extensions)
    return config


if __name__ == '__main__':
    setup(**configuration(top_path='').todict())

#!/usr/bin/env python

import os
from numpy.distutils.core import setup, Extension

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
     
wrapper = Extension('fortran_routines',
                    sources=['src/fortran_routines.f90'],
                    extra_f90_compile_args=["-std=f2003"])
setup(name='stripsim',
      version='0.1',
      description='A simulation pipeline for the LSPE/Strip instrument',
      author='Maurizio Tomasi',
      author_email='maurizio.tomasi@unimi.it',
      license='MIT',
      url='https://github.com/ziotom78/stripsim',
      long_description=read('README.md'),
      py_modules=['src/stripsim'],
      install_requires=['healpy', 'pyyaml'],
      ext_modules=[wrapper]
)

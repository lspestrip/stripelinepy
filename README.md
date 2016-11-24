# STRIPeline

A simulation pipeline for the STRIP instrument.

[![Build Status](https://travis-ci.org/ziotom78/stripeline.svg?branch=master)](https://travis-ci.org/ziotom78/stripeline)

[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


# Requirements

You'll need Python 3.x, a Fortran 2003 compiler, and the following Python
libraries:
- Numpy (http://www.numpy.org)
- Astropy (http://www.astropy.org)
- Healpy (https://github.com/healpy/healpy)
- PyYAML (http://pyyaml.org)
- Click (http://click.pocoo.org)


# Install

After having downloaded/cloned this repository, enter the folder and
run the following command:

    python setup.py install

This will install the script `stripsim`, which can be run from the
command line. (If it does not start, check your `PATH` settings.)

If you're a developer, you can build and run the code within the
repository folder and install it using the following command:

    pip install -e .

You can now run each of the tests under the directory `tests`, like
this:

    python tests/rng_test.py
    
You can use [pytest](http://docs.pytest.org/en/latest/) to discover
and run all the tests automatically:

    pytest

(If you are a Nose user, you can use `nosetests` as well.)


# Documentation

The documentation is hosted on [ReadTheDocs](http://stripeline.readthedocs.io).


# License

The code is released under a [MIT
license](https://github.com/ziotom78/stripeline/blob/master/LICENSE).

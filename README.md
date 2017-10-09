# STRIPeline

A simulation pipeline for the STRIP instrument.

[![Build Status](https://travis-ci.org/lspestrip/stripeline.svg?branch=master)](https://travis-ci.org/lspestrip/stripeline)

[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


# Requirements

You'll need Python 3.x, a Fortran 2003 compiler, and the Python libraries listed
in the file
[requirements.txt](https://github.com/lspestrip/stripeline/blob/master/requirements.txt)

The code has been tested under Linux. It won't run under Windows, at least not
until [Healpy will support it](https://github.com/healpy/healpy/issues/25).

# Install

If you're a developer, download/clone this repository, enter the folder
and run the following command:

    pip install -e .

This will create soft links to the source files in the folders used by your
Python distribution. In this way, every time you modify a source file, the
change will be immediately visible to the system without the need to re-install
Stripeline.

If you're just a casual user, after having downloaded/cloned this repository,
enter the folder and run the following command:

    python setup.py install

This will install the script `stripsim`, which can be run from the
command line. (If it does not start, check your `PATH` settings.)

You can now run each of the tests under the directory `tests`, like
this:

    python tests/rng_test.py
    
You can use [pytest](http://docs.pytest.org/en/latest/) to discover
and run all the tests automatically:

    pytest

(If you are a Nose user, you can use `nosetests` as well.)


# Documentation

You need [Sphinx](https://pypi.python.org/pypi/Sphinx) to build the documentation.

Once you have Sphinx, you can build a copy of the documentation locally using the
following commands:

    cd docs
    make html

The index of the generated documentation will be available in
`docs/_build/html/index.html`.


# License

The code is released under a [MIT
license](https://github.com/ziotom78/stripeline/blob/master/LICENSE).

# STRIPeline
A simulation pipeline for the STRIP instrument.

# Requirements

You'll need Python 3.x, a Fortran 2003 compiler, and the following Python
libraries:
- Healpy
- PyYAML

# Install

After having downloaded/cloned this repository, enter the folder and
run the following command:

    python setup.py install

This will install the script `stripsim`, which can be run from the
command line. (If it does not start, check your `PATH` settings.)

If you're a developer, you can build and run the code within the
repository folder using the following commands:

    pip install -e .

# License
The code is released under a MIT license.

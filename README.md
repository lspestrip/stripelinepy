# stripsim
A simulation pipeline for the Strip instrument.

# Requirements

You'll need Python3, a Fortran 2003 compiler, and the following Python
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

    python setup.py build_ext --inplace
    python src/stripsim.py

# License
The code is released under a MIT license.

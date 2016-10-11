#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import numpy as np
from fortran_routines import test

def main():
    print(test(np.array([1.0, 2.0, 3.0])))

if __name__ == '__main__':
    main()

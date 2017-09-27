#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import unittest as ut
import os.path

import stripeline.timetools as tt
import numpy as np


class TestTimeTools(ut.TestCase):

    def testSplitTimeRangeSimple(self):
        '''Test split_time_range against a very simple input'''
        result = tt.split_time_range(
            time_length=2.0, num_of_chunks=2, sampfreq=2.0, time0=0.5)

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0], tt.TimeChunk(
            start_time=0.5, num_of_samples=2))
        self.assertEqual(result[1], tt.TimeChunk(
            start_time=1.5, num_of_samples=2))

    def testSplitTimeRangeComplex(self):
        '''Test split_time_range against a tricky input'''
        result = tt.split_time_range(
            time_length=10.0, num_of_chunks=4, sampfreq=1.0, time0=2.0)

        self.assertEqual(len(result), 4)

        self.assertEqual(result[0], tt.TimeChunk(
            start_time=2.0, num_of_samples=2))
        self.assertEqual(result[1], tt.TimeChunk(
            start_time=5.0, num_of_samples=2))
        self.assertEqual(result[2], tt.TimeChunk(
            start_time=7.0, num_of_samples=2))
        self.assertEqual(result[3], tt.TimeChunk(
            start_time=10.0, num_of_samples=2))


class TestToiProviders(ut.TestCase):
    'Test classes like ToiProvider and FitsToiProvider'

    def test_split(self):
        'Verify that "split_into_n" returns the expected results.'
        self.assertEqual(tuple(tt.split_into_n(10, 4)), (2, 3, 2, 3))
        self.assertEqual(tuple(tt.split_into_n(201, 2)), (100, 101))

    def test_toi_splitting(self):
        'Verify that "assign_toi_files_to_processes" returns the expected results.'
        samples_per_processes = [110, 90]
        fits_files = [tt.ToiFile(file_name='A.fits', num_of_samples=40),
                      tt.ToiFile(file_name='B.fits', num_of_samples=60),
                      tt.ToiFile(file_name='C.fits', num_of_samples=30),
                      tt.ToiFile(file_name='D.fits', num_of_samples=70)]

        result = tt.assign_toi_files_to_processes(
            samples_per_processes, fits_files)

        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 3)
        self.assertEqual(len(result[1]), 2)

        segment0, segment1 = tuple(result)
        self.assertEqual(segment0[0],
                         tt.ToiFileSegment(file_name='A.fits',
                                           first_element=0,
                                           num_of_elements=40))
        self.assertEqual(segment0[1],
                         tt.ToiFileSegment(file_name='B.fits',
                                           first_element=0,
                                           num_of_elements=60))
        self.assertEqual(segment0[2],
                         tt.ToiFileSegment(file_name='C.fits',
                                           first_element=0,
                                           num_of_elements=10))

        self.assertEqual(segment1[0],
                         tt.ToiFileSegment(file_name='C.fits',
                                           first_element=10,
                                           num_of_elements=20))

        self.assertEqual(segment1[1],
                         tt.ToiFileSegment(file_name='D.fits',
                                           first_element=0,
                                           num_of_elements=70))

    def test_fits_tois(self):
        'Verify that FitsToiProvider is able to load some real data from FITS files'

        test_file_path = os.path.dirname(__file__)
        file_names = [os.path.join(test_file_path, x) for x in ['toi_test_A.fits',
                                                                'toi_test_B.fits',
                                                                'toi_test_C.fits']]
        file_layout = \
            tt.FitsTableLayout(time_col=tt.FitsColumn(hdu=1, column='TIME'),
                               theta_col=tt.FitsColumn(hdu=2, column=0),
                               phi_col=tt.FitsColumn(hdu=2, column=1),
                               psi_col=tt.FitsColumn(hdu=2, column=2),
                               signal_cols=[
                                   tt.FitsColumn(hdu=3, column='DET_Q1'),
                                   tt.FitsColumn(hdu=3, column='DET_Q2'),
                                   tt.FitsColumn(hdu=3, column='DET_U1'),
                                   tt.FitsColumn(hdu=3, column='DET_U2')
            ])

        # Create a set of FitsToiProviders, one for each MPI rank. Note that we do
        # *not* really use MPI here (comm is None): we just want to check that
        # the segment is loaded correctly for each rank
        num_of_processes = 2
        providers = [tt.FitsToiProvider(rank=i,
                                        num_of_processes=num_of_processes,
                                        file_names=file_names,
                                        file_layout=file_layout,
                                        comm=None)
                     for i in range(num_of_processes)]

        # Check that get_time works
        self.assertTrue(np.allclose(
            providers[0].get_time(), np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])))
        self.assertTrue(np.allclose(
            providers[1].get_time(), np.array([8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0])))

        # Check that get_pointings work
        theta0, phi0 = providers[0].get_pointings()
        theta1, phi1 = providers[1].get_pointings()

        self.assertTrue(np.allclose(
            theta0, np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])))
        self.assertTrue(np.allclose(
            theta1, np.array([0.5, 0.4, 0.3, 0.0, 0.1, 0.2, 0.3, 0.4])))
        self.assertTrue(np.allclose(
            phi0, np.array([0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.0])))
        self.assertTrue(np.allclose(
            phi1, np.array([0.2, 0.4, 0.6, 0.0, 0.01, 0.02, 0.03, 0.04])))

        # Check that get_signal works, both when passing an integer and a string
        sig_from_idx = providers[0].get_signal(0)
        sig_from_name = providers[0].get_signal('Q1')
        self.assertTrue(np.allclose(sig_from_idx, sig_from_name))
        self.assertTrue(np.allclose(
            sig_from_idx, np.array([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])))

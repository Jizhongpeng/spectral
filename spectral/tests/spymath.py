#########################################################################
#
#   spymath.py - This file is part of the Spectral Python (SPy) package.
#
#   Copyright (C) 2013 Thomas Boggs
#
#   Spectral Python is free software; you can redistribute it and/
#   or modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   Spectral Python is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this software; if not, write to
#
#               Free Software Foundation, Inc.
#               59 Temple Place, Suite 330
#               Boston, MA 02111-1307
#               USA
#
#########################################################################
#
# Send comments to:
# Thomas Boggs, tboggs@users.sourceforge.net
#
'''Runs unit tests for various SPy math functions.

To run the unit tests, type the following from the system command line:

    # python -m spectral.tests.spymath
'''

import numpy as np
from numpy.testing import assert_allclose
from spytest import SpyTest


class SpyMathTest(SpyTest):
    '''Tests various math functions.'''

    def setup(self):
        import spectral as spy
        self.data = spy.open_image('92AV3C.lan').open_memmap()
        self.C = spy.calc_stats(self.data).cov
        self.X = np.random.rand(100, 100)

    def test_matrix_sqrt(self):
        from spectral.algorithms.spymath import matrix_sqrt
        S = matrix_sqrt(self.X)
        assert_allclose(S.dot(S), self.X)

    def test_matrix_sqrt_inv(self):
        from spectral.algorithms.spymath import matrix_sqrt
        S = matrix_sqrt(self.X, inverse=True)
        assert_allclose(S.dot(S), np.linalg.inv(self.X))

    def test_matrix_sqrt_sym(self):
        from spectral.algorithms.spymath import matrix_sqrt
        S = matrix_sqrt(self.C, symmetric=True)
        assert_allclose(S.dot(S), self.C, atol=1e-8)

    def test_matrix_sqrt_sym_inv(self):
        from spectral.algorithms.spymath import matrix_sqrt
        S = matrix_sqrt(self.C, symmetric=True, inverse=True)
        assert_allclose(S.dot(S), np.linalg.inv(self.C), atol=1e-8)

    def test_matrix_sqrt_eigs(self):
        import spectral as spy
        from spectral.algorithms.spymath import matrix_sqrt
        stats = spy.calc_stats(self.data)
        (evals, evecs) = np.linalg.eig(stats.cov)
        S = matrix_sqrt(eigs=(evals, evecs))
        assert_allclose(S.dot(S), self.C, atol=1e-8)

    def test_stats_property_sqrt_cov(self):
        import spectral as spy
        from spectral.algorithms.spymath import matrix_sqrt
        stats = spy.calc_stats(self.data)
        s = stats.sqrt_cov.dot(stats.sqrt_cov)
        assert_allclose(s, stats.cov, atol=1e-8)

    def test_stats_property_sqrt_inv_cov(self):
        import spectral as spy
        from spectral.algorithms.spymath import matrix_sqrt
        stats = spy.calc_stats(self.data)
        s = stats.sqrt_inv_cov.dot(stats.sqrt_inv_cov)
        assert_allclose(s, stats.inv_cov, atol=1e-8)

    def test_whiten_data(self):
        '''Test that whitening transform produce unit diagonal covariance.'''
        import spectral as spy
        stats = spy.calc_stats(self.data)
        wdata = stats.get_whitening_transform()(self.data)
        wstats = spy.calc_stats(wdata)
        assert_allclose(wstats.cov, np.eye(wstats.cov.shape[0]), atol=1e-8)


class PCATest(SpyTest):
    '''Tests Principal Components transformation.'''

    def setup(self):
        import spectral as spy
        self.data = spy.open_image('92AV3C.lan').open_memmap()
        self.pc = spy.principal_components(self.data)

    def test_evals_sorted(self):
        '''Eigenvalues should be sorted in descending order.'''
        assert(np.alltrue(np.diff(self.pc.eigenvalues) <= 0))

    def test_evecs_orthonormal(self):
        '''Eigenvectors should be orthonormal.'''
        evecs = self.pc.eigenvectors
        assert(np.allclose(evecs.T.dot(evecs), np.eye(evecs.shape[0])))


class LDATest(SpyTest):
    '''Tests various math functions.'''

    def setup(self):
        import spectral as spy
        self.data = spy.open_image('92AV3C.lan').open_memmap()
        self.classes = spy.open_image('92AV3GT.GIS').read_band(0)

    def test_lda_covw_whitened(self):
        '''cov_w should be whitened in the transformed space.'''
        import spectral as spy
        classes = spy.create_training_classes(self.data, self.classes)
        fld = spy.linear_discriminant(classes)
        xdata = fld.transform(self.data)
        classes.transform(fld.transform)
        fld2 = spy.linear_discriminant(classes)
        assert_allclose(np.eye(fld2.cov_w.shape[0]), fld2.cov_w, atol=1e-8)


def run():
    print '\n' + '-' * 72
    print 'Running math tests.'
    print '-' * 72
    for T in [SpyMathTest, PCATest, LDATest]:
        T().run()

if __name__ == '__main__':
    from spectral.tests.run import parse_args, reset_stats, print_summary
    parse_args()
    reset_stats()
    run()
    print_summary()

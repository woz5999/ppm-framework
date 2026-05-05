"""
PPM Framework — Golden Ratio Module Tests
===========================================

Tests for ppm.golden_ratio: square-pyramidal numbers, the central pyramidal
identity P₃²·ln(φ) ≈ P₄·π, A₅ ≅ PSL(2,5) decomposition of sl(4,R), Dirichlet
L-function L(1, (·/5)) = 2ln(φ)/√5.

Run with:
    pytest tests/test_golden_ratio.py -v
"""

import unittest
import math
from ppm import golden_ratio as GR
from ppm import constants as C


class TestPyramidalNumber(unittest.TestCase):

    def test_first_few(self):
        """P_n = n(n+1)(2n+1)/6: P₁=1, P₂=5, P₃=14, P₄=30, P₅=55."""
        expected = {1: 1, 2: 5, 3: 14, 4: 30, 5: 55}
        for n, val in expected.items():
            self.assertEqual(GR.pyramidal_number(n), val)


class TestPyramidalIdentity(unittest.TestCase):
    """P₃²·ln(φ) ≈ P₄·π — central numerical near-identity."""

    def test_required_keys(self):
        result = GR.pyramidal_identity()
        for key in ('P3', 'P4', 'P3_squared', 'lhs', 'rhs', 'ratio',
                    'mismatch_pct', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_P3_value(self):
        self.assertEqual(GR.pyramidal_identity()['P3'], 14)

    def test_P4_value(self):
        self.assertEqual(GR.pyramidal_identity()['P4'], 30)

    def test_P3_squared_196(self):
        self.assertEqual(GR.pyramidal_identity()['P3_squared'], 196)

    def test_lhs_consistency(self):
        result = GR.pyramidal_identity()
        self.assertAlmostEqual(result['lhs'], 196.0 * math.log(C.PHI),
                               places=10)

    def test_rhs_consistency(self):
        result = GR.pyramidal_identity()
        self.assertAlmostEqual(result['rhs'], 30.0 * math.pi, places=10)

    def test_mismatch_under_0_1pct(self):
        """Documented 0.074% mismatch."""
        result = GR.pyramidal_identity()
        self.assertLess(result['mismatch_pct'], 0.1)

    def test_status_verified(self):
        self.assertEqual(GR.pyramidal_identity()['status'], 'VERIFIED')


class TestCpnSelectivity(unittest.TestCase):

    def test_default_range(self):
        result = GR.cpn_selectivity()
        for n in range(1, 8):
            self.assertIn(n, result)

    def test_each_entry_keys(self):
        result = GR.cpn_selectivity()
        for n, entry in result.items():
            for key in ('d1', 'dim_pgl', 'lhs', 'rhs', 'ratio'):
                self.assertIn(key, entry, f"n={n}: missing {key}")

    def test_dim_pgl_consistency(self):
        """dim_R PGL(n+1,C) = 2((n+1)²-1)."""
        result = GR.cpn_selectivity()
        for n, entry in result.items():
            expected_dim = 2 * ((n + 1)**2 - 1)
            self.assertEqual(entry['dim_pgl'], expected_dim)


class TestA5Decomposition(unittest.TestCase):
    """sl(4,R) under A₅ ≅ PSL(2,5)."""

    def test_required_keys(self):
        result = GR.a5_decomposition()
        for key in ('decomposition', 'dim_sl4R', 'components',
                    'component_dims', 'total_dim', 'character_field',
                    'fundamental_unit', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_total_dim_15(self):
        result = GR.a5_decomposition()
        self.assertEqual(result['total_dim'], 15)
        self.assertEqual(result['dim_sl4R'], 15)

    def test_components(self):
        result = GR.a5_decomposition()
        self.assertEqual(result['components'], {'chi_1': 1, 'chi_3': 3, 'chi_5': 1})

    def test_dim_consistency(self):
        """Σ_rep mult × dim = 15."""
        result = GR.a5_decomposition()
        total = sum(result['components'][r] * result['component_dims'][r]
                    for r in result['components'])
        self.assertEqual(total, 15)

    def test_character_field(self):
        """Character field of A₅ is Q(√5)."""
        result = GR.a5_decomposition()
        self.assertEqual(result['character_field'], 'Q(√5)')

    def test_fundamental_unit_is_phi(self):
        result = GR.a5_decomposition()
        self.assertAlmostEqual(result['fundamental_unit'], C.PHI, places=12)


class TestDirichletLFunction(unittest.TestCase):
    """L(1, (·/5)) = 2ln(φ)/√5."""

    def test_required_keys(self):
        result = GR.dirichlet_l_function()
        for key in ('L_1_chi5', 'formula', 'numerical', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_value_2lnphi_over_sqrt5(self):
        result = GR.dirichlet_l_function()
        expected = 2.0 * math.log(C.PHI) / math.sqrt(5.0)
        self.assertAlmostEqual(result['L_1_chi5'], expected, places=12)

    def test_numerical_around_0_43(self):
        """L(1, (·/5)) ≈ 0.4304."""
        result = GR.dirichlet_l_function()
        self.assertAlmostEqual(result['numerical'], 0.4304, places=3)


if __name__ == '__main__':
    unittest.main()

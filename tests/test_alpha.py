"""
PPM Framework — Alpha Module Tests
====================================

Tests for ppm.alpha: three derivation routes for the fine-structure constant.

These complement (do not duplicate) ppm.verify checks. The verify suite covers
absolute numerical agreement with 1/α = 137.036; these tests pin signature
contracts, return-dict shapes, t* values, and route-comparison structure.

Run with:
    pytest tests/test_alpha.py -v
"""

import unittest
import math
from ppm import alpha as A
from ppm import constants as C


class TestTStar(unittest.TestCase):
    """Half-variance condition t* = 1/(2(n+1)²)."""

    def test_n3_value(self):
        """For CP³ (n=3): t* = 1/32 = 0.03125."""
        self.assertEqual(A.t_star(n=3), 1.0/32.0)

    def test_n1_value(self):
        """For CP¹: t* = 1/8 = 0.125."""
        self.assertEqual(A.t_star(n=1), 0.125)

    def test_default_n3(self):
        """Default argument is n=3."""
        self.assertEqual(A.t_star(), A.t_star(n=3))

    def test_decreases_with_n(self):
        """t* decreases with n (higher CP^n has smaller half-variance time)."""
        self.assertGreater(A.t_star(1), A.t_star(2))
        self.assertGreater(A.t_star(2), A.t_star(3))
        self.assertGreater(A.t_star(3), A.t_star(5))


class TestAlphaFromSpectralGeometry(unittest.TestCase):
    """Route I: α from twisted heat traces at t*=1/32."""

    def test_returns_dict(self):
        result = A.alpha_from_spectral_geometry()
        self.assertIsInstance(result, dict)

    def test_required_keys(self):
        result = A.alpha_from_spectral_geometry()
        for key in ('alpha', 'alpha_inv', 't_star', 'error_pct', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_t_star_field_is_one_over_32(self):
        result = A.alpha_from_spectral_geometry()
        self.assertEqual(result['t_star'], 1.0/32.0)

    def test_alpha_inv_close_to_137(self):
        """1/α ≈ 137.26 (within 0.5% of observed 137.036)."""
        result = A.alpha_from_spectral_geometry()
        self.assertAlmostEqual(result['alpha_inv'], C.ALPHA_EM_INV,
                               delta=C.ALPHA_EM_INV * 0.005)

    def test_alpha_inverse_of_alpha_inv(self):
        result = A.alpha_from_spectral_geometry()
        self.assertAlmostEqual(result['alpha'] * result['alpha_inv'], 1.0,
                               places=12)

    def test_error_pct_under_one_percent(self):
        result = A.alpha_from_spectral_geometry()
        self.assertLess(abs(result['error_pct']), 1.0)

    def test_status_canonical(self):
        result = A.alpha_from_spectral_geometry()
        self.assertIn(result['status'],
                      {'VERIFIED', 'FLAGGED', 'CONCEPTUAL', 'FORMULA',
                       'OPEN', 'INTERNAL', 'AWAITING DATA', 'COMPLETE'})

    def test_convergence_at_nmax_50(self):
        """Result at nmax=50 matches default (nmax=200) to <1e-12."""
        r_low = A.alpha_from_spectral_geometry(nmax=50)
        r_def = A.alpha_from_spectral_geometry()
        self.assertAlmostEqual(r_low['alpha'], r_def['alpha'], places=12)

    def test_alpha_observed_constant(self):
        """ALPHA_OBSERVED at module level matches 1/137.036."""
        self.assertAlmostEqual(A.ALPHA_OBSERVED, 1.0/C.ALPHA_EM_INV, places=12)


class TestAlphaFromCogitoLoop(unittest.TestCase):
    """Route II: α from cogito loop (uses G_obs, Λ_obs)."""

    def test_required_keys(self):
        result = A.alpha_from_cogito_loop()
        for key in ('alpha', 'alpha_inv', 'N', 'sqrt_N', 'phi_196',
                    'sqrt_N_over_phi196', 'error_pct', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_N_near_phi392(self):
        """Recovered N within 5% of φ^392."""
        result = A.alpha_from_cogito_loop()
        self.assertAlmostEqual(result['N'], C.N_ASYMPTOTIC,
                               delta=C.N_ASYMPTOTIC * 0.05)

    def test_sqrt_N_squared_equals_N(self):
        result = A.alpha_from_cogito_loop()
        self.assertAlmostEqual(result['sqrt_N']**2, result['N'],
                               delta=result['N']*1e-12)

    def test_alpha_inv_close_to_137(self):
        """1/α ≈ 137.6 — within ~1% of observed."""
        result = A.alpha_from_cogito_loop()
        self.assertAlmostEqual(result['alpha_inv'], C.ALPHA_EM_INV,
                               delta=C.ALPHA_EM_INV * 0.01)

    def test_phi_196_field(self):
        """phi_196 = φ^196 within 1e-30 (large-magnitude relative)."""
        result = A.alpha_from_cogito_loop()
        expected = C.PHI**196
        self.assertAlmostEqual(result['phi_196']/expected, 1.0, places=10)

    def test_status_marks_partial(self):
        """Route II is marked as partial/anchored to observed inputs."""
        result = A.alpha_from_cogito_loop()
        self.assertIn('PARTIAL', result['status'])


class TestAlphaFromInstanton(unittest.TestCase):
    """Route III: bare instanton suppression (prefactor open)."""

    def test_required_keys(self):
        result = A.alpha_from_instanton()
        for key in ('R_tau_bare', 'alpha_observed', 'prefactor_gap',
                    'log10_prefactor_gap', 'S_inst', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_S_inst_is_30pi(self):
        result = A.alpha_from_instanton()
        self.assertAlmostEqual(result['S_inst'], 30.0 * math.pi, places=10)

    def test_R_tau_bare_is_half_exp_minus_S(self):
        result = A.alpha_from_instanton()
        expected = 0.5 * math.exp(-30.0 * math.pi)
        self.assertAlmostEqual(result['R_tau_bare'], expected, places=50)

    def test_log10_prefactor_around_39(self):
        """Documented log10 prefactor gap ~39."""
        result = A.alpha_from_instanton()
        self.assertGreater(result['log10_prefactor_gap'], 38.0)
        self.assertLess(result['log10_prefactor_gap'], 40.0)

    def test_status_parked(self):
        result = A.alpha_from_instanton()
        self.assertIn('PARKED', result['status'])


class TestAlphaCpnFamily(unittest.TestCase):
    """CP^n family scan: only n=3 is in the physical band."""

    def test_default_range_keys(self):
        result = A.alpha_cpn_family()
        for n in range(1, 8):
            self.assertIn(n, result, f"missing n={n}")

    def test_n3_alpha_inv_in_137_band(self):
        """CP³ gives 1/α ~ 137 (the only physical case)."""
        result = A.alpha_cpn_family()
        self.assertAlmostEqual(result[3]['alpha_inv'], 137.26, delta=0.5)

    def test_other_n_far_from_137(self):
        """n != 3 gives 1/α far from 137 (factor ≥ 7 away)."""
        result = A.alpha_cpn_family()
        for n in (1, 2, 4, 5):
            ratio = result[n]['alpha_inv'] / 137.0
            self.assertTrue(ratio < 0.15 or ratio > 7.0,
                            f"n={n}: 1/α = {result[n]['alpha_inv']} too close to 137")

    def test_each_entry_has_t_star(self):
        result = A.alpha_cpn_family()
        for n, entry in result.items():
            self.assertIn('t_star', entry)
            self.assertAlmostEqual(entry['t_star'], 1.0/(2.0*(n+1)**2), places=12)


class TestAlphaComparison(unittest.TestCase):
    """Aggregator: all three routes plus observed."""

    def test_keys(self):
        result = A.alpha_comparison()
        for key in ('route_I', 'route_II', 'route_III',
                    'alpha_observed', 'alpha_inv_observed'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_alpha_inv_observed_137_036(self):
        result = A.alpha_comparison()
        self.assertAlmostEqual(result['alpha_inv_observed'], 137.036, places=3)

    def test_routes_are_dicts(self):
        result = A.alpha_comparison()
        for k in ('route_I', 'route_II', 'route_III'):
            self.assertIsInstance(result[k], dict)


class TestAlphaObserved(unittest.TestCase):

    def test_value(self):
        self.assertAlmostEqual(A.alpha_observed(), 1.0/137.036, places=8)

    def test_returns_float(self):
        self.assertIsInstance(A.alpha_observed(), float)


if __name__ == '__main__':
    unittest.main()

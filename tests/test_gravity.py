"""
PPM Framework — Gravity Module Tests
======================================

Tests for ppm.gravity: Newton constant, two-couplings ratio, Hubble re-export,
dark-energy w_eff sampler.

These complement (do not duplicate) ppm.verify checks. The verify suite covers
absolute numerical agreement against the registry; these tests pin signature
contracts, return-dict shapes, and per-key sanity ranges.

Run with:
    pytest tests/test_gravity.py -v
"""

import unittest
import math
from ppm import gravity as GRAV
from ppm import constants as C


class TestNewtonConstant(unittest.TestCase):
    """G_N from PPM formula: G = 16π⁴ ℏc α / (m_π² √N_∞)."""

    def test_returns_dict(self):
        result = GRAV.newton_constant()
        self.assertIsInstance(result, dict)

    def test_required_keys(self):
        """All documented keys are present."""
        result = GRAV.newton_constant()
        for key in ('G_ppm_si', 'G_obs_si', 'error_pct', 'formula',
                    'm_pi_used_MeV', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_G_within_2pct(self):
        """PPM G matches observed within 2% (currently +1.66%)."""
        result = GRAV.newton_constant()
        self.assertAlmostEqual(result['G_ppm_si'], C.G_NEWTON_SI,
                               delta=C.G_NEWTON_SI * 0.02)

    def test_G_obs_matches_constants(self):
        """The 'G_obs_si' field reflects constants.G_NEWTON_SI."""
        result = GRAV.newton_constant()
        self.assertEqual(result['G_obs_si'], C.G_NEWTON_SI)

    def test_neutral_pion_anchor(self):
        """The function uses the neutral pion mass 134.977 MeV (per fix-001)."""
        result = GRAV.newton_constant()
        self.assertAlmostEqual(result['m_pi_used_MeV'], 134.977, places=3)

    def test_error_pct_consistent(self):
        """error_pct equals (G_ppm/G_obs - 1)*100 to 1e-9."""
        result = GRAV.newton_constant()
        recomputed = (result['G_ppm_si'] / result['G_obs_si'] - 1) * 100
        self.assertAlmostEqual(result['error_pct'], recomputed, places=9)

    def test_status_canonical(self):
        """Status uses canonical taxonomy."""
        result = GRAV.newton_constant()
        self.assertIn(result['status'],
                      {'VERIFIED', 'FLAGGED', 'CONCEPTUAL', 'FORMULA',
                       'OPEN', 'INTERNAL', 'AWAITING DATA', 'DERIVED'})

    def test_G_positive(self):
        result = GRAV.newton_constant()
        self.assertGreater(result['G_ppm_si'], 0)


class TestTwoCouplings(unittest.TestCase):
    """G·Λ/c⁴ ratio fixed by N_∞ geometry."""

    def test_required_keys(self):
        result = GRAV.two_couplings()
        for key in ('G_si', 'Lambda_m2', 'G_Lambda_over_c4', 'N_inf', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_N_inf_is_phi392(self):
        """N_inf field equals constants.N_ASYMPTOTIC = φ^392."""
        result = GRAV.two_couplings()
        self.assertEqual(result['N_inf'], C.N_ASYMPTOTIC)

    def test_ratio_consistency(self):
        """G_Lambda_over_c4 = G·Λ/c⁴."""
        result = GRAV.two_couplings()
        recomputed = result['G_si'] * result['Lambda_m2'] / C.C_LIGHT_SI**4
        self.assertAlmostEqual(result['G_Lambda_over_c4'], recomputed, places=20)

    def test_lambda_within_2pct(self):
        """Λ within 2% of observed (uses N_∞)."""
        result = GRAV.two_couplings()
        self.assertAlmostEqual(result['Lambda_m2'], C.LAMBDA_CC,
                               delta=C.LAMBDA_CC * 0.02)

    def test_status_verified(self):
        result = GRAV.two_couplings()
        self.assertEqual(result['status'], 'VERIFIED')


class TestHubble(unittest.TestCase):
    """Hubble re-exported from cosmology.hubble_from_age()."""

    def test_required_keys(self):
        result = GRAV.hubble()
        for key in ('H0_km_s_Mpc', 'H0_per_s', 'T_universe_s',
                    'T_universe_Gyr', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_H0_in_band(self):
        """H₀ in 65–75 km/s/Mpc (TRGB/Cepheid range)."""
        result = GRAV.hubble()
        self.assertGreater(result['H0_km_s_Mpc'], 65.0)
        self.assertLess(result['H0_km_s_Mpc'], 75.0)

    def test_age_default(self):
        """Default age is 13.797 Gyr."""
        result = GRAV.hubble()
        self.assertAlmostEqual(result['T_universe_Gyr'], 13.797, places=3)

    def test_H0_inverse_of_age(self):
        """H₀ × T_universe ≈ 1 by construction."""
        result = GRAV.hubble()
        self.assertAlmostEqual(result['H0_per_s'] * result['T_universe_s'],
                               1.0, places=10)


class TestDarkEnergy(unittest.TestCase):
    """Dark-energy w_eff at low and high backreaction ratios."""

    def test_required_keys(self):
        result = GRAV.dark_energy()
        for key in ('w_eff_low', 'w_eff_high'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_w_eff_low_close_to_minus_one(self):
        """w_eff at Ω_δ/Ω_DE = 0.01 is ≈ -0.993."""
        result = GRAV.dark_energy()
        self.assertAlmostEqual(result['w_eff_low'], -1.0 + 2.0/300.0, places=8)

    def test_w_eff_high_more_negative_band(self):
        """w_eff at higher ratio is more positive (less negative)."""
        result = GRAV.dark_energy()
        self.assertGreater(result['w_eff_high'], result['w_eff_low'])

    def test_both_above_minus_one(self):
        """Backreaction shifts w upward from -1; both above -1."""
        result = GRAV.dark_energy()
        self.assertGreater(result['w_eff_low'], -1.0)
        self.assertGreater(result['w_eff_high'], -1.0)


class TestReExports(unittest.TestCase):
    """gravity re-exports cosmology functions; spot-check they resolve."""

    def test_cosmological_constant_callable(self):
        result = GRAV.cosmological_constant()
        self.assertIn('Lambda_m2', result)

    def test_g_eff_callable(self):
        self.assertEqual(GRAV.g_eff(0), 1.0)

    def test_w_eff_callable(self):
        """w_eff(0) = -1 (no backreaction → pure Λ)."""
        self.assertAlmostEqual(GRAV.w_eff(0.0), -1.0)

    def test_gw_dispersion_callable(self):
        result = GRAV.gw_dispersion(100.0)
        self.assertIn('delta_v_over_c', result)


if __name__ == '__main__':
    unittest.main()

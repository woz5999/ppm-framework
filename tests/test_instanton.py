"""
PPM Framework — Instanton Module Tests
========================================

Tests for ppm.instanton: degree-3 CP³ instanton action S = 30π, zero-mode
count = 30, e^{-30π} ≈ φ^{-196} match, T² zeta-regulated partition function,
prefactor budget.

Run with:
    pytest tests/test_instanton.py -v
"""

import unittest
import math
from ppm import instanton as I
from ppm import constants as C


class TestInstantonAction(unittest.TestCase):

    def test_value_is_30pi(self):
        self.assertAlmostEqual(I.instanton_action(), 30.0 * math.pi, places=10)

    def test_matches_constant(self):
        self.assertAlmostEqual(I.instanton_action(), C.INSTANTON_ACTION,
                               places=12)


class TestInstantonSuppression(unittest.TestCase):

    def test_value(self):
        self.assertAlmostEqual(I.instanton_suppression(),
                               math.exp(-30.0 * math.pi), places=50)

    def test_around_1e_minus_41(self):
        """e^{-30π} ≈ 1.17×10⁻⁴¹."""
        self.assertGreater(I.instanton_suppression(), 1e-42)
        self.assertLess(I.instanton_suppression(), 1e-40)


class TestPhi196Check(unittest.TestCase):

    def test_required_keys(self):
        result = I.phi_196_check()
        for key in ('S_30pi', 'exponent_phi196', 'mismatch_pct',
                    'exp_neg_S', 'phi_neg_196', 'ratio', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_S_30pi_value(self):
        result = I.phi_196_check()
        self.assertAlmostEqual(result['S_30pi'], 30.0 * math.pi, places=10)

    def test_mismatch_under_0_1pct(self):
        """Documented 0.073% mismatch in exponent."""
        result = I.phi_196_check()
        self.assertLess(result['mismatch_pct'], 0.1)

    def test_phi_neg_196_value(self):
        result = I.phi_196_check()
        self.assertAlmostEqual(result['phi_neg_196'], C.PHI**(-196.0), places=50)


class TestZeroModeCount(unittest.TestCase):

    def test_required_keys(self):
        result = I.zero_mode_count()
        for key in ('n_complex', 'n_real', 'dim_R_PGL4C',
                    'formula', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_n_real_30(self):
        self.assertEqual(I.zero_mode_count()['n_real'], 30)

    def test_n_complex_15(self):
        self.assertEqual(I.zero_mode_count()['n_complex'], 15)

    def test_dim_PGL_consistency(self):
        result = I.zero_mode_count()
        self.assertEqual(result['n_real'], result['dim_R_PGL4C'])


class TestZeroModeVolume(unittest.TestCase):

    def test_default_F_zero_1e15(self):
        """V_⊥^15 = 10^15 with V_⊥ = 10."""
        result = I.zero_mode_volume()
        self.assertAlmostEqual(result['F_zero'], 1e15, places=0)

    def test_log_F_zero(self):
        result = I.zero_mode_volume()
        self.assertAlmostEqual(result['log_F_zero'], 15.0 * math.log(10.0),
                               places=10)

    def test_argument(self):
        """Custom V_⊥ value gets used."""
        result = I.zero_mode_volume(V_perp=2.0)
        self.assertEqual(result['V_perp'], 2.0)
        self.assertAlmostEqual(result['F_zero'], 2.0**15)


class TestT2ModularParameter(unittest.TestCase):

    def test_required_keys(self):
        result = I.t2_modular_parameter()
        for key in ('beta', 'piR', 'tau_imag', 'q'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_tau_imag_around_one(self):
        """τ_im = 10/π² ≈ 1.013."""
        result = I.t2_modular_parameter()
        self.assertAlmostEqual(result['tau_imag'], 10.0/math.pi**2, places=10)

    def test_q_consistency(self):
        result = I.t2_modular_parameter()
        self.assertAlmostEqual(result['q'],
                               math.exp(-2.0 * math.pi * result['tau_imag']),
                               places=12)


class TestZt2PerScalar(unittest.TestCase):

    def test_required_keys(self):
        result = I.zt2_per_scalar()
        for key in ('log_ZT2', 'ZT2', 'tau_imag', 'q', 'eta_abs', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_log_ZT2_value(self):
        """log Z_T² ≈ 0.5274."""
        result = I.zt2_per_scalar()
        self.assertAlmostEqual(result['log_ZT2'], 0.5274, places=3)

    def test_ZT2_consistency(self):
        result = I.zt2_per_scalar()
        self.assertAlmostEqual(result['ZT2'], math.exp(result['log_ZT2']),
                               places=10)


class TestZt2Total(unittest.TestCase):

    def test_required_keys(self):
        result = I.zt2_total()
        for key in ('n_dof', 'log_ZT2_total', 'ZT2_total',
                    'log_ZT2_per_scalar'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_default_n_dof_6(self):
        self.assertEqual(I.zt2_total()['n_dof'], 6)

    def test_log_total_six_times_per_scalar(self):
        """Total log scales linearly with n_dof."""
        per = I.zt2_per_scalar()['log_ZT2']
        result = I.zt2_total(n_dof=6)
        self.assertAlmostEqual(result['log_ZT2_total'], 6.0 * per, places=10)


class TestPrefactorSubtotal(unittest.TestCase):

    def test_required_keys(self):
        result = I.prefactor_subtotal()
        for key in ('log_F_zero', 'log_F_trans', 'log_ZT2_total',
                    'subtotal', 'target_log_J', 'log_Z_worldsheet_needed',
                    'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_subtotal_consistency(self):
        result = I.prefactor_subtotal()
        expected = (result['log_F_zero'] + result['log_F_trans']
                    + result['log_ZT2_total'])
        self.assertAlmostEqual(result['subtotal'], expected, places=10)

    def test_status_keys(self):
        result = I.prefactor_subtotal()
        for key in ('F_zero', 'F_trans', 'ZT2', 'Z_worldsheet'):
            self.assertIn(key, result['status'])


class TestDedekindEta(unittest.TestCase):

    def test_value_at_tau_imag_1(self):
        """|η(i)| ≈ 0.768."""
        result = I.dedekind_eta(1.0)
        self.assertAlmostEqual(result, 0.768, delta=0.01)

    def test_decreases_at_high_tau(self):
        """|η| decreases as τ_im increases (q-product → 0)."""
        e_low = I.dedekind_eta(0.5)
        e_hi = I.dedekind_eta(2.0)
        self.assertGreater(e_low, e_hi)


if __name__ == '__main__':
    unittest.main()

"""
PPM Framework — Cosmology Module Tests
========================================

Tests for ppm.cosmology: Λ from N_∞, Hubble from age and Sidharth, G_eff(z)
nonlinear scaling, dark-energy w_eff with backreaction, Friedmann age,
actualization record M(t), GW dispersion, consciousness numerics.

Run with:
    pytest tests/test_cosmology.py -v
"""

import unittest
import math
from ppm import cosmology as CO
from ppm import constants as C


class TestCosmologicalConstant(unittest.TestCase):

    def test_required_keys(self):
        result = CO.cosmological_constant()
        for key in ('Lambda_m2', 'Lambda_obs', 'error_pct', 'N', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_N_is_phi392(self):
        """Λ formula uses N = φ^392 (static topological invariant)."""
        result = CO.cosmological_constant()
        self.assertEqual(result['N'], C.N_ASYMPTOTIC)
        # Within float precision
        self.assertAlmostEqual(result['N'] / (C.PHI**392), 1.0, places=12)

    def test_lambda_within_2pct(self):
        result = CO.cosmological_constant()
        self.assertLess(abs(result['error_pct']), 2.0)

    def test_status_verified(self):
        self.assertEqual(CO.cosmological_constant()['status'], 'VERIFIED')


class TestHubbleFromAge(unittest.TestCase):

    def test_default_age(self):
        result = CO.hubble_from_age()
        self.assertAlmostEqual(result['T_universe_Gyr'], 13.797, places=3)

    def test_required_keys(self):
        result = CO.hubble_from_age()
        for key in ('H0_km_s_Mpc', 'H0_per_s', 'T_universe_s',
                    'T_universe_Gyr', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_H0_around_70(self):
        result = CO.hubble_from_age()
        self.assertAlmostEqual(result['H0_km_s_Mpc'], 70.87, delta=0.1)

    def test_H0_inverse_of_age(self):
        result = CO.hubble_from_age()
        self.assertAlmostEqual(result['H0_per_s'] * result['T_universe_s'],
                               1.0, places=10)

    def test_argument_passed(self):
        """Different T gives different H₀."""
        result = CO.hubble_from_age(T_Gyr=14.0)
        self.assertAlmostEqual(result['T_universe_Gyr'], 14.0, places=8)


class TestHubbleFromSidharth(unittest.TestCase):

    def test_required_keys(self):
        result = CO.hubble_from_sidharth()
        for key in ('R_universe_m', 'T_universe_s', 'T_universe_Gyr',
                    'H0_km_s_Mpc', 'sqrt_N', 'lambda_C_m', 'tau_C_s', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_sqrt_N_is_phi196(self):
        """√N = φ^196."""
        result = CO.hubble_from_sidharth()
        self.assertEqual(result['sqrt_N'], C.N_ASYMPTOTIC_SQRT)

    def test_age_close_to_14_Gyr(self):
        result = CO.hubble_from_sidharth()
        self.assertAlmostEqual(result['T_universe_Gyr'], 14.14, delta=0.5)


class TestGEff(unittest.TestCase):
    """G_eff(z) = (1+z)^{3/2} for nonlinear regime."""

    def test_z_zero(self):
        self.assertEqual(CO.g_eff(0), 1.0)

    def test_z_12(self):
        """At z=12: G_eff ≈ 47G₀."""
        self.assertAlmostEqual(CO.g_eff(12), 13.0**1.5, places=8)
        self.assertAlmostEqual(CO.g_eff(12), 46.87, delta=0.05)

    def test_monotonic_in_z(self):
        for z1, z2 in [(0, 1), (1, 5), (5, 10)]:
            self.assertLess(CO.g_eff(z1), CO.g_eff(z2))


class TestDeltaCPpm(unittest.TestCase):
    """Modified collapse threshold."""

    def test_z_zero_above_standard(self):
        """At z=0: δ_c^PPM ≈ 1.75 (slightly above standard 1.686)."""
        self.assertAlmostEqual(CO.delta_c_ppm(0), 1.75, delta=0.02)

    def test_decreases_with_z(self):
        """δ_c^PPM decreases at higher z."""
        self.assertGreater(CO.delta_c_ppm(0), CO.delta_c_ppm(10))


class TestGwDispersion(unittest.TestCase):

    def test_required_keys(self):
        result = CO.gw_dispersion(100.0)
        for key in ('alpha_GW', 'delta_v_over_c', 'l_P_k', 'f_hz', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_alpha_GW_near_1(self):
        """α_GW ≈ 0.995 from heat-kernel calculation."""
        self.assertAlmostEqual(CO.ALPHA_GW, 0.995, delta=0.01)

    def test_delta_v_planck_suppressed(self):
        """At LIGO 100 Hz, Δv/c ≪ 10⁻⁸⁰."""
        result = CO.gw_dispersion(100.0)
        self.assertLess(result['delta_v_over_c'], 1e-80)

    def test_dispersion_grows_quadratically_with_f(self):
        """Δv/c ∝ f² (since k ∝ f and dispersion ∝ k²)."""
        d1 = CO.gw_dispersion(100.0)['delta_v_over_c']
        d2 = CO.gw_dispersion(200.0)['delta_v_over_c']
        self.assertAlmostEqual(d2/d1, 4.0, delta=0.01)


class TestGwPhaseShift(unittest.TestCase):

    def test_returns_float(self):
        result = CO.gw_phase_shift(100.0, 100.0)
        self.assertIsInstance(result, float)

    def test_zero_distance(self):
        self.assertEqual(CO.gw_phase_shift(100.0, 0.0), 0.0)


class TestWEff(unittest.TestCase):
    """Deprecated w_eff (linear-Ω form)."""

    def test_zero_ratio_gives_minus_one(self):
        self.assertAlmostEqual(CO.w_eff(0.0), -1.0)

    def test_positive_ratio_above_minus_one(self):
        self.assertGreater(CO.w_eff(0.1), -1.0)


class TestWEffBackreaction(unittest.TestCase):

    def test_required_keys(self):
        result = CO.w_eff_backreaction()
        for key in ('w0', 'wa', 'beta', 'Omega_m', 'Omega_L', 'eps', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_default_beta(self):
        result = CO.w_eff_backreaction()
        self.assertAlmostEqual(result['beta'], 0.05)

    def test_w0_above_minus_one(self):
        """Backreaction lifts w above -1 (not below)."""
        result = CO.w_eff_backreaction()
        self.assertGreater(result['w0'], -1.0)

    def test_wa_positive(self):
        """w_a is positive (w → -1 over time)."""
        result = CO.w_eff_backreaction()
        self.assertGreater(result['wa'], 0)

    def test_beta_zero_gives_pure_lambda(self):
        result = CO.w_eff_backreaction(beta=0.0)
        self.assertAlmostEqual(result['w0'], -1.0)
        self.assertAlmostEqual(result['wa'], 0.0)


class TestFriedmannAge(unittest.TestCase):

    def test_required_keys(self):
        result = CO.friedmann_age()
        for key in ('f_coefficient', 'T_pred_Gyr', 'T_pred_s', 'T_obs_Gyr',
                    'error_pct', 'sqrt_N', 'tau_C_s', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_T_pred_close_to_obs(self):
        """T_pred within 5% of 13.797 Gyr."""
        result = CO.friedmann_age()
        self.assertLess(abs(result['error_pct']), 5.0)

    def test_f_coefficient_around_0_95(self):
        """f ≈ 0.951 from Friedmann integral."""
        result = CO.friedmann_age()
        self.assertAlmostEqual(result['f_coefficient'], 0.951, delta=0.01)


class TestActualizationRecord(unittest.TestCase):

    def test_required_keys(self):
        result = CO.actualization_record()
        for key in ('M_total', 'S_record_kB', 'S_BH_kB', 'S_ratio',
                    'tau_C_s', 'N_particles',
                    're_actualizations_per_position', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_M_around_1e121(self):
        """M(t₀) ≈ 1.8×10¹²¹ τ-events."""
        result = CO.actualization_record()
        self.assertGreater(result['M_total'], 1e121)
        self.assertLess(result['M_total'], 1e122)

    def test_S_ratio_order_unity(self):
        """S_record / S_BH ≈ 1.5 (order-unity match)."""
        result = CO.actualization_record()
        self.assertAlmostEqual(result['S_ratio'], 1.5, delta=0.2)

    def test_re_actualizations_around_1e39(self):
        """Each boundary position re-actualized ~10³⁹ times."""
        result = CO.actualization_record()
        self.assertGreater(result['re_actualizations_per_position'], 1e38)
        self.assertLess(result['re_actualizations_per_position'], 1e41)


class TestKConscious(unittest.TestCase):

    def test_310k_around_75(self):
        self.assertAlmostEqual(CO.k_conscious(310.0), 75.35, delta=0.1)

    def test_higher_T_lower_k(self):
        self.assertGreater(CO.k_conscious(200.0), CO.k_conscious(400.0))


class TestIntegrationTime(unittest.TestCase):

    def test_required_keys(self):
        result = CO.integration_time()
        for key in ('tau_sys_eff_s', 'tau_bath_thermal_s', 't_integrate_s',
                    't_integrate_ms', 'N_sites', 'tau_bath_confinement_s',
                    'N_eff_sub', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_t_integrate_around_60_ms(self):
        """Default (T=310K, N=10¹⁴): t_integrate ≈ 60 ms."""
        result = CO.integration_time()
        self.assertAlmostEqual(result['t_integrate_ms'], 60.7, delta=2.0)


class TestNReliable(unittest.TestCase):

    def test_required_keys(self):
        result = CO.n_reliable()
        for key in ('N_reliable', 'Gamma_PD', 't_integrate_s',
                    'M_windows', 'Delta_m_kg', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_N_around_5e5(self):
        """N_reliable ≈ 5×10⁵ matching corticospinal-tract anatomy."""
        result = CO.n_reliable()
        self.assertGreater(result['N_reliable'], 1e5)
        self.assertLess(result['N_reliable'], 1e7)


class TestBrainPower(unittest.TestCase):

    def test_required_keys(self):
        result = CO.brain_power()
        for key in ('P_watts', 'P_uW', 'E_per_cycle_J',
                    'fraction_of_brain', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_default_around_3uW(self):
        """Default (N=10¹⁴, f=10 Hz): P ≈ 3 μW."""
        result = CO.brain_power()
        self.assertAlmostEqual(result['P_uW'], 3.0, delta=0.5)

    def test_fraction_of_brain_tiny(self):
        """Conservative case is negligible fraction of 20W brain baseline."""
        result = CO.brain_power()
        self.assertLess(result['fraction_of_brain'], 1e-5)


if __name__ == '__main__':
    unittest.main()

"""
PPM Framework — Test Suite
============================

Tests for all framework modules. Run with:
    pytest tests/test_all.py -v
or:
    python -m unittest tests.test_all -v
"""

import unittest
import math
from ppm.hierarchy import (
    energy_mev, energy_gev, k_from_energy_mev, k_from_energy_gev,
    planck_anchor, consciousness_level, g_from_topology, k_level_table,
)
from ppm import constants as C


class TestHierarchy(unittest.TestCase):
    def test_planck_scale_order_of_magnitude(self):
        """E(1) should be within an order of magnitude of Planck energy."""
        E_gev = energy_gev(1.0)
        ratio = E_gev / C.E_PLANCK_GEV
        self.assertGreater(ratio, 0.1)
        self.assertLess(ratio, 10.0)

    def test_confinement_reference(self):
        """E(51) is the reference energy = 140 MeV exactly."""
        E = energy_mev(51)
        self.assertAlmostEqual(E, 140.0, places=8)

    def test_consciousness_thermal_match(self):
        """E(k_conscious) ~ k_BT at T_bio = 310 K."""
        k_c = consciousness_level(310.0)
        E_MeV = energy_mev(k_c)
        kB_eV = 8.617333e-5
        kBT_MeV = kB_eV * 310.0 * 1e-6
        self.assertAlmostEqual(E_MeV, kBT_MeV, delta=kBT_MeV * 1e-6)

    def test_hierarchy_monotonically_decreasing(self):
        """Energy decreases with increasing k."""
        k_vals = [1, 10, 20, 30, 40, 51, 57, 61, 70, 75]
        energies = [energy_mev(k) for k in k_vals]
        for i in range(len(energies) - 1):
            self.assertGreater(energies[i], energies[i + 1])

    def test_inverse_consistency(self):
        """k_from_energy_mev(energy_mev(k)) == k for all k."""
        for k in [1, 13, 44.5, 51, 57, 61, 70, 75]:
            E = energy_mev(k)
            k_recovered = k_from_energy_mev(E)
            self.assertAlmostEqual(k, k_recovered, places=6)

    def test_gev_mev_consistency(self):
        """energy_gev(k) = energy_mev(k) / 1000."""
        for k in [10, 30, 51]:
            self.assertAlmostEqual(energy_gev(k), energy_mev(k) * 1e-3, places=10)

    def test_electron_k_level(self):
        k_e = k_from_energy_mev(0.511)
        self.assertAlmostEqual(k_e, 57.0, delta=0.5)

    def test_muon_k_level(self):
        k_mu = k_from_energy_mev(105.7)
        self.assertAlmostEqual(k_mu, 51.5, delta=0.5)

    def test_top_k_level(self):
        k_top = k_from_energy_gev(172.7)
        self.assertAlmostEqual(k_top, 44.5, delta=1.5)

    def test_scaling_factor(self):
        """E(k)/E(k+2) = 2π for all k."""
        for k in [10, 30, 51]:
            ratio = energy_mev(k) / energy_mev(k + 2)
            self.assertAlmostEqual(ratio, C.TAU, places=8)

    def test_planck_anchor_dict(self):
        pa = planck_anchor()
        self.assertIn('E_predicted_GeV', pa)
        self.assertIn('error_pct', pa)
        self.assertLess(abs(pa['error_pct']), 10.0)

    def test_g_from_topology(self):
        """g = 2π from both topological and Maslov derivations."""
        result = g_from_topology()
        self.assertAlmostEqual(result['g'], 2 * math.pi, places=10)
        self.assertAlmostEqual(result['g_topo'], result['g_maslov'], places=10)

    def test_k_conscious_range(self):
        """k_conscious should be 70 < k < 80 at T = 310 K."""
        k_c = consciousness_level(310.0)
        self.assertGreater(k_c, 70)
        self.assertLess(k_c, 80)

    def test_k_level_table(self):
        """Particle table should have entries and finite predictions."""
        rows = k_level_table()
        self.assertGreater(len(rows), 10)
        for row in rows:
            self.assertTrue(math.isfinite(row['E_predicted_GeV']))


class TestConstants(unittest.TestCase):
    def test_lambda_ppm(self):
        """λ_PPM = 1/(4√π) ≈ 0.14105."""
        self.assertAlmostEqual(C.LAMBDA_PPM, 1.0 / (4 * math.sqrt(math.pi)), places=10)

    def test_tau(self):
        self.assertAlmostEqual(C.TAU, 2 * math.pi, places=10)

    def test_r_squared(self):
        """r² = 2(N+1) = 10."""
        self.assertEqual(C.R_SQUARED, 10.0)

    def test_instanton_action(self):
        """S = 30π."""
        self.assertAlmostEqual(C.INSTANTON_ACTION, 30 * math.pi, places=8)

    def test_alpha_gut(self):
        self.assertAlmostEqual(C.ALPHA_GUT, 0.1, places=10)

    def test_sin2_theta_w(self):
        self.assertAlmostEqual(C.SIN2_THETA_W_PPM, 0.375, places=10)

    def test_phi_196_match(self):
        """φ^{-196} ≈ e^{-30π} to < 0.1%."""
        self.assertLess(C.PHI_196_EXPONENT_MATCH_PERCENT, 0.1)

    def test_y_top_ppm(self):
        """y_t^PPM ≈ 0.992."""
        self.assertAlmostEqual(C.Y_TOP_PPM, 0.992, delta=0.001)


class TestGauge(unittest.TestCase):
    def test_alpha_gut(self):
        """alpha_gut() returns bare float = 0.1."""
        from ppm.gauge import alpha_gut
        self.assertAlmostEqual(alpha_gut(), 0.1, places=10)

    def test_sin2_theta_W_pati_salam(self):
        """sin2_theta_W_pati_salam() returns bare float = 0.375."""
        from ppm.gauge import sin2_theta_W_pati_salam
        self.assertAlmostEqual(sin2_theta_W_pati_salam(), 0.375, places=10)

    def test_sin2_theta_W_sm_running(self):
        """SM running of sin²θ_W to E_break should be close to 3/8."""
        from ppm.gauge import sin2_theta_W_sm_running
        result = sin2_theta_W_sm_running()
        self.assertAlmostEqual(result['sin2_tW_sm'], 0.375, delta=0.005)

    def test_three_generations(self):
        from ppm.gauge import generation_count
        result = generation_count()
        self.assertEqual(result['N_generations'], 3)

    def test_couplings_at_ebreak(self):
        from ppm.gauge import couplings_at_ebreak
        result = couplings_at_ebreak()
        for key in ['alpha1_sm', 'alpha2_sm', 'alpha3_sm']:
            self.assertGreater(result[key], 0)


class TestHiggs(unittest.TestCase):
    def test_lambda_ppm(self):
        """lambda_ppm() returns bare float."""
        from ppm.higgs import lambda_ppm
        self.assertAlmostEqual(lambda_ppm(), C.LAMBDA_PPM, places=10)

    def test_top_yukawa(self):
        """top_yukawa_ppm() returns bare float ≈ 0.992."""
        from ppm.higgs import top_yukawa_ppm
        self.assertAlmostEqual(top_yukawa_ppm(), 0.992, delta=0.001)

    def test_higgs_quartic_comparison(self):
        from ppm.higgs import higgs_quartic_comparison
        result = higgs_quartic_comparison()
        self.assertLess(abs(result['error_pct']), 15.0)


class TestInstanton(unittest.TestCase):
    def test_action(self):
        """instanton_action() returns bare float = 30π."""
        from ppm.instanton import instanton_action
        self.assertAlmostEqual(instanton_action(), 30 * math.pi, places=6)

    def test_phi_196(self):
        from ppm.instanton import phi_196_check
        result = phi_196_check()
        self.assertLess(result['mismatch_pct'], 0.1)

    def test_zero_modes(self):
        from ppm.instanton import zero_mode_count
        result = zero_mode_count()
        self.assertEqual(result['n_complex'], 15)
        self.assertEqual(result['n_real'], 30)


class TestSpectral(unittest.TestCase):
    def test_heat_kernel(self):
        from ppm.spectral import heat_kernel_coefficients
        result = heat_kernel_coefficients()
        # Has a0, a2, a4, a6 keys
        for key in ['a0', 'a2', 'a4', 'a6']:
            self.assertIn(key, result)

    def test_zeta_delta_0(self):
        """zeta_delta_0() returns bare float = -733/945."""
        from ppm.spectral import zeta_delta_0
        self.assertAlmostEqual(zeta_delta_0(), -733.0 / 945.0, places=6)


class TestBerryPhase(unittest.TestCase):
    def test_delta_cp(self):
        from ppm.berry_phase import delta_cp
        result = delta_cp()
        self.assertIn('delta_cp_rad', result)
        self.assertTrue(math.isfinite(result['delta_cp_rad']))

    def test_ckm_angles(self):
        from ppm.berry_phase import ckm_angles
        result = ckm_angles()
        self.assertIn('theta_cabibbo_deg', result)
        self.assertGreater(result['theta_cabibbo_deg'], 10)
        self.assertLess(result['theta_cabibbo_deg'], 15)

    def test_jarlskog(self):
        from ppm.berry_phase import jarlskog_invariant
        result = jarlskog_invariant()
        self.assertGreater(result['J'], 0)


class TestCosmology(unittest.TestCase):
    def test_cosmological_constant(self):
        from ppm.cosmology import cosmological_constant
        result = cosmological_constant()
        self.assertGreater(result['Lambda_m2'], 1e-53)
        self.assertLess(result['Lambda_m2'], 1e-51)

    def test_hubble(self):
        from ppm.cosmology import hubble_from_age
        result = hubble_from_age()
        self.assertGreater(result['H0_km_s_Mpc'], 60)
        self.assertLess(result['H0_km_s_Mpc'], 80)


class TestNeutrino(unittest.TestCase):
    def test_theta_strong(self):
        """Strong CP: θ = 0 from RP³ non-orientability."""
        from ppm.neutrino import theta_strong
        result = theta_strong()
        self.assertEqual(result['theta'], 0.0)

    def test_pmns(self):
        from ppm.neutrino import pmns_tribimaximal
        result = pmns_tribimaximal()
        self.assertAlmostEqual(result['sin2_theta12_ppm'], 1.0 / 3.0, places=10)
        self.assertAlmostEqual(result['sin2_theta23_ppm'], 0.5, places=10)


class TestGoldenRatio(unittest.TestCase):
    def test_pyramidal_identity(self):
        from ppm.golden_ratio import pyramidal_identity
        result = pyramidal_identity()
        self.assertLess(result['mismatch_pct'], 1.0)


if __name__ == '__main__':
    unittest.main()

"""
PPM Framework — Stability Module Tests
========================================

Tests for ppm.stability: cascade irreversibility, EWSB bifurcation,
two-loop confinement, information theory, consciousness attractor.

Run with:
    pytest tests/test_stability.py -v
"""

import unittest
import math
from ppm import stability
from ppm import constants as C


class TestBetaCoefficients(unittest.TestCase):
    def test_b0_nf6(self):
        """b0(n_f=6) = 11 - 4 = 7."""
        b0, _ = stability.beta_coefficients_su3(6)
        self.assertAlmostEqual(b0, 7.0)

    def test_b0_nf5(self):
        """b0(n_f=5) = 11 - 10/3 ≈ 7.667."""
        b0, _ = stability.beta_coefficients_su3(5)
        self.assertAlmostEqual(b0, 23.0 / 3.0)

    def test_b0_nf3(self):
        """b0(n_f=3) = 11 - 2 = 9."""
        b0, _ = stability.beta_coefficients_su3(3)
        self.assertAlmostEqual(b0, 9.0)

    def test_b1_nf5(self):
        """b1(n_f=5) = 102 - 190/3."""
        _, b1 = stability.beta_coefficients_su3(5)
        self.assertAlmostEqual(b1, 102.0 - 190.0 / 3.0)

    def test_asymptotic_freedom(self):
        """b0 > 0 for n_f ≤ 16 (asymptotic freedom)."""
        for nf in range(0, 17):
            b0, _ = stability.beta_coefficients_su3(nf)
            self.assertGreater(b0, 0, f"n_f={nf}")


class TestTwoLoopRG(unittest.TestCase):
    def test_coupling_decreases_running_up(self):
        """α_s decreases running from M_Z up to 1 TeV (asymptotic freedom)."""
        mus, alphas = stability.run_alpha_s_twoloop(91.2, 1000.0, 0.1179, 5,
                                                     n_steps=10000)
        self.assertLess(alphas[-1], alphas[0])

    def test_coupling_increases_running_down(self):
        """α_s increases running from M_Z down to 10 GeV."""
        mus, alphas = stability.run_alpha_s_twoloop(91.2, 10.0, 0.1179, 5,
                                                     n_steps=10000)
        self.assertGreater(alphas[-1], alphas[0])

    def test_alpha_at_10gev(self):
        """α_s(10 GeV) ≈ 0.18 from M_Z (rough check)."""
        _, alphas = stability.run_alpha_s_twoloop(91.2, 10.0, 0.1179, 5,
                                                   n_steps=50000)
        self.assertAlmostEqual(alphas[-1], 0.18, delta=0.02)

    def test_output_lengths_match(self):
        mus, alphas = stability.run_alpha_s_twoloop(91.2, 50.0, 0.1179, 5,
                                                     n_steps=1000)
        self.assertEqual(len(mus), len(alphas))


class TestConfinementScale(unittest.TestCase):
    def test_confinement_reached(self):
        """Two-loop running must reach α_s = 1 (confinement)."""
        result = stability.confinement_scale()
        self.assertIsNotNone(result['mu_conf_GeV'])
        self.assertIsNotNone(result['k_conf'])

    def test_confinement_k_near_51(self):
        """Confinement k-level within Δk < 3 of k = 51."""
        result = stability.confinement_scale()
        self.assertLess(result['delta_k'], 3.0)

    def test_confinement_energy_order(self):
        """μ_conf should be between 100 MeV and 2 GeV."""
        result = stability.confinement_scale()
        self.assertGreater(result['mu_conf_MeV'], 100.0)
        self.assertLess(result['mu_conf_MeV'], 2000.0)

    def test_alpha_at_mb(self):
        """α_s(m_b) ≈ 0.22 (standard result)."""
        result = stability.confinement_scale()
        self.assertAlmostEqual(result['alpha_at_mb'], 0.22, delta=0.02)

    def test_alpha_at_mc(self):
        """α_s(m_c) in the ballpark of 0.39–0.47 (two-loop, threshold-dependent)."""
        result = stability.confinement_scale()
        self.assertGreater(result['alpha_at_mc'], 0.30)
        self.assertLess(result['alpha_at_mc'], 0.55)

    def test_lambda_qcd(self):
        """Λ_QCD should be 200–400 MeV."""
        result = stability.confinement_scale()
        self.assertGreater(result['lambda_qcd_MeV'], 200.0)
        self.assertLess(result['lambda_qcd_MeV'], 400.0)

    def test_status_verified(self):
        result = stability.confinement_scale()
        self.assertEqual(result['status'], 'VERIFIED')


class TestAlpha3PatiSalam(unittest.TestCase):
    def test_alpha3_ps_positive(self):
        result = stability.alpha3_at_pati_salam()
        self.assertGreater(result['alpha3_ps'], 0)

    def test_alpha3_ps_less_than_alpha_gut(self):
        """SM-required α₃(PS) < PPM α_GUT = 0.1."""
        result = stability.alpha3_at_pati_salam()
        self.assertLess(result['alpha3_ps'], result['alpha_gut_ppm'])

    def test_normalization_ratio(self):
        """Normalization ratio should be 2–6 (known ~3.8)."""
        result = stability.alpha3_at_pati_salam()
        self.assertGreater(result['normalization_ratio'], 2.0)
        self.assertLess(result['normalization_ratio'], 6.0)

    def test_status_open(self):
        result = stability.alpha3_at_pati_salam()
        self.assertEqual(result['status'], 'KNOWN OPEN')


class TestEWSBBifurcation(unittest.TestCase):
    def test_ewsb_k_near_44_5(self):
        """EWSB k-level within Δk < 2 of known k = 44.5."""
        result = stability.ewsb_bifurcation(use_ppm_quartic=True)
        self.assertLess(result['delta_k'], 2.0)

    def test_ewsb_energy_order(self):
        """E_EWSB should be between 100 GeV and 1 TeV."""
        result = stability.ewsb_bifurcation()
        self.assertGreater(result['E_ewsb_GeV'], 100.0)
        self.assertLess(result['E_ewsb_GeV'], 1000.0)

    def test_c_T_full_SM(self):
        """Full SM thermal coefficient c_T ≈ 0.40."""
        result = stability.ewsb_bifurcation()
        self.assertAlmostEqual(result['c_T'], 0.40, delta=0.05)

    def test_higgs_mass_ppm(self):
        """PPM Higgs mass ≈ 131 GeV (from λ_PPM)."""
        result = stability.ewsb_bifurcation(use_ppm_quartic=True)
        self.assertAlmostEqual(result['m_H_GeV'], 131.0, delta=3.0)

    def test_observed_quartic(self):
        """With observed quartic, should still give Δk < 2."""
        result = stability.ewsb_bifurcation(use_ppm_quartic=False)
        self.assertLess(result['delta_k'], 2.0)

    def test_status_verified(self):
        result = stability.ewsb_bifurcation()
        self.assertEqual(result['status'], 'VERIFIED')


class TestCascadeIrreversibility(unittest.TestCase):
    def test_three_steps(self):
        """Cascade has exactly 3 breaking steps."""
        steps = stability.cascade_irreversibility()
        self.assertEqual(len(steps), 3)

    def test_all_irreversible(self):
        """Every breaking step has ΔF > 0."""
        for step in stability.cascade_irreversibility():
            self.assertTrue(step['irreversible'],
                            f"{step['name']} has ΔF = {step['delta_F']:.3f} ≤ 0")
            self.assertGreater(step['delta_F'], 0)

    def test_confinement_largest(self):
        """Confinement (SU(3)→1) has the largest ΔF."""
        steps = stability.cascade_irreversibility()
        delta_fs = [s['delta_F'] for s in steps]
        self.assertEqual(delta_fs.index(max(delta_fs)), 2)

    def test_pati_salam_delta_f(self):
        """ΔF(PS→SM) = ln(21/12) ≈ 0.56."""
        steps = stability.cascade_irreversibility()
        self.assertAlmostEqual(steps[0]['delta_F'], math.log(21 / 12), places=6)

    def test_dim_coset_positive(self):
        for step in stability.cascade_irreversibility():
            self.assertGreater(step['dim_coset'], 0)


class TestInformationTheory(unittest.TestCase):
    def test_signal_to_noise_decreases_with_k(self):
        """R(k) decreases with increasing k."""
        R_low = stability.signal_to_noise(40)
        R_high = stability.signal_to_noise(60)
        self.assertGreater(R_low, R_high)

    def test_channel_capacity_positive_at_pion(self):
        """I(k=51) > 0 at room temperature."""
        I = stability.channel_capacity(51, T_kelvin=300.0)
        self.assertGreater(I, 0)

    def test_channel_closed_at_high_k(self):
        """Channel closed (I=0) well above consciousness threshold."""
        I = stability.channel_capacity(80, T_kelvin=310.0)
        self.assertEqual(I, 0.0)

    def test_dual_efficiency_sums_to_one(self):
        """η_I + η_S = 1 at any k-level."""
        for k in [30, 51, 60, 70]:
            eff = stability.dual_efficiency(k)
            self.assertAlmostEqual(eff['eta_I'] + eff['eta_S'], 1.0, places=10)

    def test_eta_I_decreases_with_k(self):
        """Information efficiency decreases with k (higher k = more noise)."""
        eff_low = stability.dual_efficiency(30)
        eff_high = stability.dual_efficiency(60)
        self.assertGreater(eff_low['eta_I'], eff_high['eta_I'])


class TestConsciousnessAttractor(unittest.TestCase):
    def test_R_min_is_3(self):
        """F = R - 3 ln R has minimum at R = 3 (analytic result)."""
        result = stability.consciousness_attractor()
        self.assertEqual(result['R_min'], 3.0)

    def test_k_min_above_60(self):
        """Bare attractor k-level > 60 at biological temperature."""
        result = stability.consciousness_attractor(T_kelvin=310.0)
        self.assertGreater(result['k_min'], 60)

    def test_k_channel_closure_above_k_min(self):
        """Channel closure (R=1) occurs at higher k than F minimum (R=3)."""
        result = stability.consciousness_attractor(T_kelvin=310.0)
        self.assertGreater(result['k_channel_closure'], result['k_min'])

    def test_temperature_dependence(self):
        """Higher T shifts attractor to lower k (higher thermal energy)."""
        cold = stability.consciousness_attractor(T_kelvin=200.0)
        warm = stability.consciousness_attractor(T_kelvin=400.0)
        self.assertGreater(cold['k_min'], warm['k_min'])


class TestSummary(unittest.TestCase):
    def test_summary_has_four_rows(self):
        rows = stability.summary()
        self.assertEqual(len(rows), 4)

    def test_all_delta_k_finite(self):
        for row in stability.summary():
            self.assertTrue(math.isfinite(row['delta_k']),
                            f"{row['scale']}: Δk not finite")

    def test_all_delta_k_reasonable(self):
        """All Δk values should be < 10 (sanity check)."""
        for row in stability.summary():
            self.assertLess(row['delta_k'], 10.0,
                            f"{row['scale']}: Δk = {row['delta_k']:.1f}")


if __name__ == '__main__':
    unittest.main()

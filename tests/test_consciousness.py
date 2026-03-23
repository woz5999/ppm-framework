"""
Tests for ppm.consciousness — consciousness-scale predictions.
"""
import math
import pytest
from ppm import consciousness as con


class TestEntropyPerEvent:
    def test_delta_s_nats(self):
        ds = con.delta_s()
        assert abs(ds['nats'] - 5.514) < 0.01

    def test_delta_s_bits(self):
        ds = con.delta_s()
        assert abs(ds['bits'] - 7.95) < 0.02

    def test_delta_s_formula(self):
        expected = 3.0 * math.log(2.0 * math.pi)
        assert abs(con.DELTA_S_PER_EVENT - expected) < 1e-10


class TestChannelCapacity:
    def test_particle_regime_high_capacity(self):
        """At k=51 (pion), channel capacity should be large."""
        I = con.channel_capacity(51, T_K=310.0)
        assert I > 50.0  # many bits at particle scales

    def test_consciousness_regime_low_capacity(self):
        """At k≈75, channel capacity should be near zero."""
        I = con.channel_capacity(75, T_K=310.0)
        assert I < 5.0  # near zero at R≈1

    def test_beyond_consciousness_zero(self):
        """At k > k_c, channel capacity should be exactly 0."""
        I = con.channel_capacity(85, T_K=310.0)
        assert I == 0.0


class TestIntegratedInformation:
    def test_phi_awake_human(self):
        """Φ ≈ 200 nats for awake human brain."""
        phi = con.integrated_information()
        assert 190 < phi < 215  # 200 ± 15

    def test_phi_formula_components(self):
        """Verify Φ = c_Σ √N α²."""
        N = 1e14
        c = 0.38
        alpha = 1.0 / 137.036
        expected = c * math.sqrt(N) * alpha**2
        actual = con.integrated_information(N, c)
        assert abs(actual - expected) < 1e-10

    def test_phi_scaling_sqrt_N(self):
        """Φ should scale as √N."""
        phi1 = con.integrated_information(1e12)
        phi2 = con.integrated_information(4e12)
        ratio = phi2 / phi1
        assert abs(ratio - 2.0) < 0.01  # √4 = 2

    def test_phi_zero_for_no_boundaries(self):
        phi = con.integrated_information(0)
        assert phi == 0.0


class TestTauFiringRate:
    def test_nu_tau_order_of_magnitude(self):
        """ν_τ at 310 K should be ~10^13 Hz."""
        nu = con.tau_firing_rate(310.0)
        assert 1e13 < nu < 1e14

    def test_nu_tau_formula(self):
        """ν_τ = k_B T / ℏ."""
        T = 310.0
        expected = con.K_B_JK * T / con.HBAR_JS
        actual = con.tau_firing_rate(T)
        assert abs(actual - expected) / expected < 1e-6


class TestPhenomenalFlux:
    def test_psi_positive(self):
        psi = con.phenomenal_flux()
        assert psi > 0

    def test_psi_zero_no_integration(self):
        """Ψ = 0 when Φ = 0."""
        psi = con.phenomenal_flux(Phi=0.0)
        assert psi == 0.0

    def test_psi_formula(self):
        """Ψ = Φ × ν_τ × ΔS."""
        phi = 200.0
        nu = 4e13
        ds = 5.51
        expected = phi * nu * ds
        actual = con.phenomenal_flux(phi, nu, ds)
        assert abs(actual - expected) < 1e-6


class TestConsciousnessStates:
    def test_awake_phi(self):
        states = con.consciousness_states()
        assert abs(states['awake']['Phi_nats'] - 202.4) < 5.0

    def test_sleep_ordering(self):
        """Φ: awake > light sleep > deep sleep > anesthesia."""
        states = con.consciousness_states()
        assert states['awake']['Phi_nats'] > states['light_sleep_N1']['Phi_nats']
        assert states['light_sleep_N1']['Phi_nats'] > states['deep_sleep_N3']['Phi_nats']
        assert states['deep_sleep_N3']['Phi_nats'] > states['anesthesia']['Phi_nats']

    def test_anesthesia_low(self):
        states = con.consciousness_states()
        assert states['anesthesia']['Phi_nats'] < 10.0


class TestScalingPrediction:
    def test_human_in_scaling(self):
        rows = con.phi_scaling_prediction()
        human = [r for r in rows if r['species'] == 'Human'][0]
        assert abs(human['Phi_nats'] - 202.4) < 5.0

    def test_monotonic_increase(self):
        rows = con.phi_scaling_prediction()
        phis = [r['Phi_nats'] for r in rows]
        for i in range(len(phis) - 1):
            assert phis[i] <= phis[i+1]

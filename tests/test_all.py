"""
PPM Framework — Test Suite
============================

Tests for all framework modules. Run with:
    pytest tests/test_all.py -v
or:
    python -m unittest tests.test_all -v
"""

import unittest
import numpy as np
from ppm.hierarchy import hierarchy_energy, k_from_mass, actualization_timescale
from ppm.constraint_solver import (constraint_solver, default_initial_guess,
                                    direct_solve, predict_independent)
from ppm.phase_coherence import thermal_phase, quantum_phase, solve_alpha_from_coherence
from ppm.constants import PHYSICAL, FRAMEWORK, ENERGY_SCALES, CONVERSIONS


class TestHierarchy(unittest.TestCase):
    def test_planck_scale_order_of_magnitude(self):
        """E(0) should be within an order of magnitude of Planck energy."""
        E = hierarchy_energy(0)
        E_planck_MeV = 1.22e22  # 1.22e19 GeV in MeV
        ratio = E / E_planck_MeV
        self.assertGreater(ratio, 0.1)
        self.assertLess(ratio, 10.0)

    def test_confinement_reference(self):
        """E(51) is the reference energy = 140 MeV exactly."""
        E = hierarchy_energy(51)
        self.assertTrue(np.isclose(E, 140.0, rtol=1e-10))

    def test_consciousness_thermal_match(self):
        """E(k_conscious) must equal k_BT at T_bio — this is the defining condition."""
        k_c = FRAMEWORK['k_conscious']
        E_MeV = hierarchy_energy(k_c)
        kBT_MeV = FRAMEWORK['kBT_MeV']
        self.assertTrue(np.isclose(E_MeV, kBT_MeV, rtol=1e-6),
                        f"E({k_c:.2f}) = {E_MeV:.4e} vs kBT = {kBT_MeV:.4e}")

    def test_hierarchy_monotonically_decreasing(self):
        """Energy decreases with increasing k."""
        k_vals = [0, 10, 20, 30, 40, 51, 57, 61, 70, 75]
        energies = [hierarchy_energy(k) for k in k_vals]
        for i in range(len(energies) - 1):
            self.assertGreater(energies[i], energies[i+1])

    def test_inverse_consistency(self):
        """k_from_mass(hierarchy_energy(k)) == k for all k."""
        for k in [0, 13, 44.5, 51, 57, 61, 70, 75]:
            E = hierarchy_energy(k)
            k_recovered = k_from_mass(E)
            self.assertTrue(np.isclose(k, k_recovered, rtol=1e-6),
                            f"k={k}: recovered {k_recovered}")

    def test_electron_k_level(self):
        k_e = k_from_mass(0.511)
        self.assertAlmostEqual(k_e, 57.1, delta=0.5)

    def test_muon_k_level(self):
        k_mu = k_from_mass(105.7)
        self.assertAlmostEqual(k_mu, 51.5, delta=0.5)

    def test_top_k_level(self):
        k_top = k_from_mass(173000.0)
        self.assertAlmostEqual(k_top, 43.5, delta=1.5)

    def test_scaling_factor(self):
        """E(k)/E(k+2) = g for all k."""
        g = FRAMEWORK['g']
        for k in [10, 30, 51]:
            ratio = hierarchy_energy(k) / hierarchy_energy(k + 2)
            self.assertTrue(np.isclose(ratio, g, rtol=1e-10))

    def test_timescale_positive(self):
        for k in [0, 51, 57, 61, 75]:
            tau = actualization_timescale(k)
            self.assertGreater(tau['tau_quantum_s'], 0)

    def test_timescale_k_conscious_has_integration(self):
        """k_conscious should have integration window and sub-cycle counts."""
        k_c = FRAMEWORK['k_conscious']
        tau = actualization_timescale(k_c)
        self.assertIsNotNone(tau['integration_ms'])
        self.assertIsNotNone(tau['sub_cycles_k51'])
        self.assertIsNotNone(tau['sub_cycles_k57'])
        self.assertGreater(tau['sub_cycles_k51'], tau['sub_cycles_k57'])

    def test_rate_hierarchy_ordering(self):
        """Lower k must have faster actualization (smaller tau)."""
        tau_k51 = actualization_timescale(51)['tau_quantum_s']
        tau_k57 = actualization_timescale(57)['tau_quantum_s']
        k_c = FRAMEWORK['k_conscious']
        tau_kc = actualization_timescale(k_c)['tau_quantum_s']
        self.assertLess(tau_k51, tau_k57)
        self.assertLess(tau_k57, tau_kc)

    def test_k_conscious_derived_correctly(self):
        """k_conscious should be > 70 (not 61) with g=2pi and T_bio=310K."""
        k_c = FRAMEWORK['k_conscious']
        self.assertGreater(k_c, 70)
        self.assertLess(k_c, 80)


class TestConstraintSolver(unittest.TestCase):
    def test_direct_solve_finite(self):
        sol = direct_solve()
        self.assertTrue(np.isfinite(sol[7]))  # Lambda
        self.assertTrue(np.isfinite(sol[0]))  # K
        self.assertTrue(np.isfinite(sol[1]))  # T

    def test_direct_solve_with_observed_alpha(self):
        """Using observed alpha, all solutions should be finite and physical."""
        sol = direct_solve(use_observed_alpha=True)
        self.assertTrue(np.all(np.isfinite(sol)))
        self.assertTrue(np.isclose(sol[5], PHYSICAL['G'], rtol=0.15))

    def test_convergence(self):
        x, converged, info = constraint_solver()
        self.assertTrue(converged)

    def test_predict_independent_lambda(self):
        """Lambda prediction should be within 10% of observed."""
        results = predict_independent()
        self.assertLess(results['Lambda']['error_pct'], 10.0)

    def test_predict_independent_G(self):
        """G prediction (with observed alpha) should be within 15%."""
        results = predict_independent()
        self.assertLess(results['G']['error_pct'], 15.0)

    def test_predict_independent_alpha_w(self):
        results = predict_independent()
        self.assertTrue(np.isclose(results['alpha_w']['predicted'],
                                   1.0 / (3.0 * np.pi**2), rtol=1e-10))

    def test_predict_independent_T(self):
        results = predict_independent()
        self.assertLess(results['T']['error_pct'], 0.01)

    def test_alpha_status_is_open(self):
        results = predict_independent()
        self.assertEqual(results['alpha_EM']['status'], 'OPEN')

    def test_lambda_status_is_ok(self):
        results = predict_independent()
        self.assertEqual(results['Lambda']['status'], 'OK')


class TestPhaseCoherence(unittest.TestCase):
    def test_solve_alpha_algebraic_consistency(self):
        """solve_alpha must produce alpha such that Phi_thermal == Phi_quantum."""
        T, N, K = 310, 100, 10
        alpha = solve_alpha_from_coherence(T=T, N_boundaries=N, K=K)
        Phi_t = thermal_phase(T=T, N_boundaries=N)
        Phi_q = quantum_phase(alpha=alpha, K=K)
        self.assertTrue(np.isclose(Phi_t, Phi_q, rtol=1e-10))

    def test_alpha_positive(self):
        alpha = solve_alpha_from_coherence(T=310, N_boundaries=100, K=10)
        self.assertGreater(alpha, 0)

    def test_alpha_scales_with_N(self):
        a1 = solve_alpha_from_coherence(T=310, N_boundaries=100, K=10)
        a2 = solve_alpha_from_coherence(T=310, N_boundaries=200, K=10)
        self.assertTrue(np.isclose(a2 / a1, 2.0, rtol=1e-10))

    def test_alpha_scales_with_T(self):
        a1 = solve_alpha_from_coherence(T=310, N_boundaries=100, K=10)
        a2 = solve_alpha_from_coherence(T=620, N_boundaries=100, K=10)
        self.assertTrue(np.isclose(a2 / a1, 2.0, rtol=1e-10))

    def test_large_N_gives_correct_alpha(self):
        """With the correct N_eff, alpha should equal 1/137."""
        results = predict_independent()
        N_needed = results['alpha_EM']['N_eff_needed']
        K = FRAMEWORK['k_conscious']
        alpha = solve_alpha_from_coherence(T=310, N_boundaries=N_needed, K=K)
        self.assertTrue(np.isclose(1/alpha, 137.036, rtol=0.01))


class TestCosmology(unittest.TestCase):
    def test_G_present_value(self):
        from ppm.cosmology import G_evolution
        G0 = PHYSICAL['G']
        self.assertTrue(np.isclose(G_evolution(0, G0=G0), G0, rtol=1e-6))

    def test_G_evolution_scaling(self):
        from ppm.cosmology import G_evolution
        G0 = PHYSICAL['G']
        ratio = G_evolution(1, G0=G0) / G_evolution(0, G0=G0)
        self.assertTrue(np.isclose(ratio, 2 ** (3 / 2), rtol=1e-6))

    def test_Lambda_present_value(self):
        from ppm.cosmology import lambda_cosmological
        Lambda = lambda_cosmological()
        self.assertGreater(Lambda, 1e-53)
        self.assertLess(Lambda, 1e-51)

    def test_Lambda_evolution_scaling(self):
        from ppm.cosmology import lambda_evolution, lambda_cosmological
        L0 = lambda_cosmological()
        ratio = lambda_evolution(1, Lambda0=L0) / L0
        self.assertTrue(np.isclose(ratio, 4.0, rtol=1e-6))

    def test_G_newton_order_of_magnitude(self):
        from ppm.cosmology import G_newton
        G = G_newton()
        self.assertGreater(G, 1e-11)
        self.assertLess(G, 1e-10)

    def test_hubble_z0(self):
        from ppm.cosmology import hubble_parameter
        H0 = hubble_parameter(0)
        self.assertTrue(np.isclose(H0, 70.9, rtol=1e-6))


class TestConstants(unittest.TestCase):
    def test_g_exact(self):
        self.assertTrue(np.isclose(FRAMEWORK['g'], 2 * np.pi, rtol=1e-10))

    def test_k_conscious_is_float(self):
        """k_conscious should be a computed float, not hardcoded integer."""
        k_c = FRAMEWORK['k_conscious']
        self.assertIsInstance(k_c, float)
        self.assertNotEqual(k_c, int(k_c))

    def test_energy_scales_complete(self):
        required = ['Planck', 'EWSB', 'Confinement', 'Electron', 'Consciousness']
        for scale in required:
            self.assertIn(scale, ENERGY_SCALES)

    def test_physical_constants_positive(self):
        for name, val in PHYSICAL.items():
            self.assertGreater(val, 0, f"{name} must be positive")

    def test_conversions_consistent(self):
        self.assertTrue(np.isclose(CONVERSIONS['MeV_to_J'], 1.602e-13, rtol=0.01))

    def test_kBT_in_framework(self):
        self.assertIn('kBT_MeV', FRAMEWORK)
        self.assertIn('kBT_eV', FRAMEWORK)
        self.assertTrue(np.isclose(FRAMEWORK['kBT_eV'], 0.0267, rtol=0.01))

    def test_energy_scales_geometric_k_values(self):
        """ENERGY_SCALES k-values must be geometric (from topology or Z2 quantization)."""
        from ppm.hierarchy import hierarchy_energy
        # Topological levels have exact k-values
        self.assertEqual(ENERGY_SCALES['Planck']['k'], 0)
        self.assertEqual(ENERGY_SCALES['EWSB']['k'], 44.5)
        self.assertEqual(ENERGY_SCALES['Confinement']['k'], 51)
        # Z2 quantization levels: k = 44.5 + n/2
        self.assertEqual(ENERGY_SCALES['Electron']['k'], 57.0)      # n=25
        self.assertEqual(ENERGY_SCALES['Muon']['k'], 51.5)          # n=14
        self.assertEqual(ENERGY_SCALES['Tau']['k'], 48.0)           # n=7

    def test_energy_scales_predictions_vs_observation(self):
        """Predicted energies from geometric k should be order-of-magnitude correct.

        Z2 quantization (k = k_EWSB + n/2) gives the right scale but
        exponential amplification of small k-offsets produces 10-25% errors
        for leptons. Topologically fixed levels (EWSB, Top) are much better.
        """
        # Topologically fixed: Top quark — <1%
        top_pred = ENERGY_SCALES['Top']['E_GeV_predicted']
        top_obs = ENERGY_SCALES['Top']['E_GeV_observed']
        self.assertLess(abs(top_pred - top_obs) / top_obs, 0.02)
        # Z2 quantization: Electron — ~10% (k off by 0.11)
        e_pred = ENERGY_SCALES['Electron']['E_GeV_predicted']
        e_obs = ENERGY_SCALES['Electron']['E_GeV_observed']
        self.assertLess(abs(e_pred - e_obs) / e_obs, 0.15)
        # Z2 quantization: Muon — ~16% (k off by 0.19)
        mu_pred = ENERGY_SCALES['Muon']['E_GeV_predicted']
        mu_obs = ENERGY_SCALES['Muon']['E_GeV_observed']
        self.assertLess(abs(mu_pred - mu_obs) / mu_obs, 0.20)

    def test_energy_scales_have_source(self):
        """Every entry must declare its geometric source."""
        for name, entry in ENERGY_SCALES.items():
            self.assertIn('source', entry, f"{name} missing 'source' field")


class TestTwistor(unittest.TestCase):
    """Tests for twistor/RG module."""

    def test_cp3_euler_characteristic(self):
        from ppm.twistor import cp3_invariants
        inv = cp3_invariants()
        self.assertEqual(inv['euler_characteristic'], 4)

    def test_cp3_chern_numbers(self):
        from ppm.twistor import cp3_invariants
        cn = cp3_invariants()['chern_numbers']
        self.assertEqual(cn['c3'], 4)
        self.assertEqual(cn['c1_c2'], 24)
        self.assertEqual(cn['c1_cubed'], 64)

    def test_cp3_z2_quotient(self):
        from ppm.twistor import cp3_invariants
        self.assertEqual(cp3_invariants()['chi_CP3_mod_Z2'], 2)

    def test_neff_exponent_near_five_sixths(self):
        """N_eff exponent should be within 1% of 5/6 (holographic)."""
        from ppm.twistor import neff_exponent_analysis
        neff = neff_exponent_analysis()
        self.assertLess(neff['p_discrepancy_pct'], 1.0)

    def test_heat_kernel_monotone(self):
        """Heat kernel ratio should decrease as t decreases (more CP3 modes)."""
        from ppm.twistor import heat_kernel_ratio
        r1 = heat_kernel_ratio(0.1)
        r2 = heat_kernel_ratio(1.0)
        self.assertLess(r1, r2)

    def test_heat_kernel_alpha_scale_exists(self):
        """There should exist a t where the ratio ≈ α."""
        from ppm.twistor import heat_kernel_ratio
        r = heat_kernel_ratio(0.032)
        self.assertLess(abs(r - 1/137.036) / (1/137.036), 0.1)

    def test_spectral_zeta_positive(self):
        from ppm.twistor import spectral_zeta_CP3, spectral_zeta_RP3
        self.assertGreater(spectral_zeta_CP3(3.0), 0)
        self.assertGreater(spectral_zeta_RP3(3.0), 0)


class TestFSGeometry(unittest.TestCase):
    """Tests for Fubini-Study geometry: k↔distance, volume fraction, α conjecture."""

    def test_fs_distance_max(self):
        from ppm.twistor import fs_distance_max
        self.assertAlmostEqual(fs_distance_max(), np.pi / 4, places=10)

    def test_k_to_fs_roundtrip(self):
        """k → d → k should be identity."""
        from ppm.twistor import k_to_fs_distance, fs_distance_to_k
        for k in [0, 10, 30, 51, 57, 70]:
            d = k_to_fs_distance(k)
            k_back = fs_distance_to_k(d)
            self.assertAlmostEqual(k, k_back, places=6,
                                   msg=f"Roundtrip failed for k={k}")

    def test_planck_at_max_distance(self):
        """k=0 should map to d_max = π/4."""
        from ppm.twistor import k_to_fs_distance, fs_distance_max
        d = k_to_fs_distance(0)
        self.assertAlmostEqual(d, fs_distance_max(), places=10)

    def test_consciousness_near_zero_distance(self):
        """k_conscious should map to d ≈ 0."""
        from ppm.twistor import k_to_fs_distance
        k_c = FRAMEWORK['k_conscious']
        d = k_to_fs_distance(k_c)
        self.assertAlmostEqual(d, 0.0, places=10)

    def test_distance_monotonically_decreasing_with_k(self):
        """Higher k → smaller FS distance (closer to RP3)."""
        from ppm.twistor import k_to_fs_distance
        k_vals = [0, 20, 40, 51, 57, 70, 75]
        dists = [k_to_fs_distance(k) for k in k_vals]
        for i in range(len(dists) - 1):
            self.assertGreaterEqual(dists[i], dists[i+1])

    def test_volume_fraction_at_zero(self):
        from ppm.twistor import volume_fraction_within_distance
        self.assertAlmostEqual(volume_fraction_within_distance(0.0), 0.0, places=10)

    def test_volume_fraction_at_max(self):
        from ppm.twistor import volume_fraction_within_distance, fs_distance_max
        self.assertAlmostEqual(volume_fraction_within_distance(fs_distance_max()), 1.0, places=3)

    def test_volume_fraction_monotonic(self):
        from ppm.twistor import volume_fraction_within_distance
        dvals = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7]
        fracs = [volume_fraction_within_distance(d) for d in dvals]
        for i in range(len(fracs) - 1):
            self.assertLess(fracs[i], fracs[i+1])

    def test_volume_scaling_exponent_is_six(self):
        """Near d=0, legacy S5 model scales as d^6 where 6 = dim_R(CP3)."""
        from ppm.twistor import alpha_from_volume_fraction
        vf = alpha_from_volume_fraction(model='S5')
        self.assertAlmostEqual(vf['scaling_exponent'], 6.0, delta=0.15)

    def test_alpha_volume_fraction_match(self):
        """Volume fraction at d* should equal α to within 1%."""
        from ppm.twistor import alpha_from_volume_fraction
        vf = alpha_from_volume_fraction()
        self.assertLess(vf['match_pct'], 1.0)

    def test_d_alpha_over_d_max_near_one_third(self):
        """d*/d_max ≈ 1/3 for legacy S5 model; Jacobi model gives ~1/8."""
        from ppm.twistor import alpha_from_volume_fraction
        vf_s5 = alpha_from_volume_fraction(model='S5')
        self.assertAlmostEqual(vf_s5['d_alpha_over_d_max'], 1.0/3, delta=0.02)
        # Jacobi model (default) gives smaller ratio
        vf_jacobi = alpha_from_volume_fraction(model='jacobi')
        self.assertAlmostEqual(vf_jacobi['d_alpha_over_d_max'], 1.0/8, delta=0.02)

    def test_geometric_summary_keys(self):
        from ppm.twistor import alpha_geometric_summary
        gs = alpha_geometric_summary()
        self.assertIn('volume_fraction', gs)
        self.assertIn('unifying_dimension', gs)
        self.assertEqual(gs['unifying_dimension'], 6)
        self.assertEqual(gs['chi_quotient'], 2)


if __name__ == '__main__':
    unittest.main()

class TestJacobiFieldAnalysis(unittest.TestCase):
    """Tests for Jacobi field density and Schrödinger setup."""

    def test_jacobi_field_density_at_zero(self):
        from ppm.twistor import jacobi_field_density
        rho = jacobi_field_density(0.0)
        self.assertAlmostEqual(rho, 0.0, places=10)

    def test_jacobi_field_density_at_pi_8(self):
        from ppm.twistor import jacobi_field_density
        # At d=π/8: sin(π/4)=1/√2, cos(π/4)=1/√2
        # ρ = sin²(π/4)cos(π/4) = (1/2)(1/√2) = 1/(2√2) ≈ 0.3536
        rho = jacobi_field_density(np.pi / 8)
        expected = 0.5 * (1.0 / np.sqrt(2))
        self.assertAlmostEqual(rho, expected, places=4)

    def test_jacobi_field_density_at_max(self):
        from ppm.twistor import jacobi_field_density, fs_distance_max
        rho = jacobi_field_density(fs_distance_max())
        # At d=π/4: sin(π/2)=1, cos(π/2)=0
        self.assertAlmostEqual(rho, 0.0, places=10)

    def test_jacobi_field_density_is_positive_in_interior(self):
        from ppm.twistor import jacobi_field_density, fs_distance_max
        d_test = fs_distance_max() / 3
        rho = jacobi_field_density(d_test)
        self.assertGreater(rho, 0.0)

    def test_jacobi_cumulative_fraction_at_zero(self):
        from ppm.twistor import jacobi_cumulative_fraction
        f = jacobi_cumulative_fraction(0.0)
        self.assertAlmostEqual(f, 0.0, places=10)

    def test_jacobi_cumulative_fraction_at_max(self):
        from ppm.twistor import jacobi_cumulative_fraction, fs_distance_max
        f = jacobi_cumulative_fraction(fs_distance_max())
        # At d=π/4: sin(π/2)=1, sin³(π/2)=1
        self.assertAlmostEqual(f, 1.0, places=10)

    def test_jacobi_cumulative_fraction_monotonic(self):
        from ppm.twistor import jacobi_cumulative_fraction, fs_distance_max
        d_vals = np.linspace(0, fs_distance_max(), 20)
        f_vals = [jacobi_cumulative_fraction(d) for d in d_vals]
        for i in range(len(f_vals) - 1):
            self.assertLess(f_vals[i], f_vals[i+1])

    def test_jacobi_cumulative_fraction_at_pi_8(self):
        from ppm.twistor import jacobi_cumulative_fraction
        # At d=π/8: sin(π/4)=1/√2, sin³(π/4)=(1/√2)³=1/(2√2) ≈ 0.3536
        f = jacobi_cumulative_fraction(np.pi / 8)
        expected = (1.0 / np.sqrt(2))**3
        self.assertAlmostEqual(f, expected, places=4)

    def test_effective_potential_Q_at_zero(self):
        from ppm.twistor import effective_potential_Q
        Q = effective_potential_Q(0.0)
        self.assertAlmostEqual(Q, 0.0, places=10)

    def test_effective_potential_Q_at_pi_8(self):
        from ppm.twistor import effective_potential_Q
        Q = effective_potential_Q(np.pi / 8)
        # Expected ≈ 11.0 from manual calculation
        self.assertAlmostEqual(Q, 11.0, delta=0.5)

    def test_effective_potential_Q_is_positive_in_interior(self):
        from ppm.twistor import effective_potential_Q, fs_distance_max
        d_test = fs_distance_max() / 3
        Q = effective_potential_Q(d_test)
        self.assertGreater(Q, 0.0)

    def test_effective_potential_Q_grows_near_max(self):
        from ppm.twistor import effective_potential_Q, fs_distance_max
        d_max = fs_distance_max()
        Q_mid = effective_potential_Q(d_max * 0.45)
        Q_near = effective_potential_Q(d_max * 0.49)
        self.assertLess(Q_mid, Q_near)
        # Q grows but approaches finite limit before hitting singularity
        self.assertGreater(Q_near, 10.0)

    def test_schrodinger_setup_returns_dict(self):
        from ppm.twistor import schrodinger_setup
        setup = schrodinger_setup()
        self.assertIsInstance(setup, dict)

    def test_schrodinger_setup_has_required_keys(self):
        from ppm.twistor import schrodinger_setup
        setup = schrodinger_setup()
        required_keys = [
            'd_grid', 'd_max', 'n_grid', 'Q_values', 'observable',
            'target_expectation_value', 'density', 'boundary_conditions',
            'open_problem'
        ]
        for key in required_keys:
            self.assertIn(key, setup)

    def test_schrodinger_setup_grid_shape(self):
        from ppm.twistor import schrodinger_setup
        setup = schrodinger_setup()
        n = setup['n_grid']
        self.assertEqual(len(setup['d_grid']), n)
        self.assertEqual(len(setup['Q_values']), n)
        self.assertEqual(len(setup['observable']), n)

    def test_schrodinger_setup_Q_at_zero_is_zero(self):
        from ppm.twistor import schrodinger_setup
        setup = schrodinger_setup()
        Q_at_0 = setup['Q_values'][0]
        self.assertAlmostEqual(Q_at_0, 0.0, places=10)

    def test_schrodinger_setup_boundary_conditions_satisfied(self):
        from ppm.twistor import schrodinger_setup, fs_distance_max
        setup = schrodinger_setup()
        d_grid = setup['d_grid']
        d_max = fs_distance_max()
        # Grid should start at 0 and end at d_max
        self.assertAlmostEqual(d_grid[0], 0.0, places=6)
        self.assertAlmostEqual(d_grid[-1], d_max, places=6)

    def test_schrodinger_setup_observable_consistent(self):
        from ppm.twistor import schrodinger_setup
        setup = schrodinger_setup()
        d_grid = setup['d_grid']
        obs = setup['observable']
        expected_obs = np.sin(2 * d_grid)**3
        np.testing.assert_array_almost_equal(obs, expected_obs, decimal=10)

    def test_volume_density_jacobi_model(self):
        from ppm.twistor import volume_density_at_distance
        # Test that 'jacobi' model uses jacobi_field_density
        rho = volume_density_at_distance(np.pi/8, model='jacobi')
        from ppm.twistor import jacobi_field_density
        expected = jacobi_field_density(np.pi/8)
        self.assertAlmostEqual(rho, expected, places=10)

    def test_volume_fraction_jacobi_model_default(self):
        from ppm.twistor import volume_fraction_closed_form
        # Test that 'jacobi' is available and matches jacobi_cumulative_fraction
        f = volume_fraction_closed_form(np.pi/8, model='jacobi')
        from ppm.twistor import jacobi_cumulative_fraction
        expected = jacobi_cumulative_fraction(np.pi/8)
        self.assertAlmostEqual(f, expected, places=10)

    def test_volume_fraction_within_distance_jacobi_at_zero(self):
        from ppm.twistor import volume_fraction_within_distance
        f = volume_fraction_within_distance(0.0, model='jacobi')
        self.assertAlmostEqual(f, 0.0, places=10)

    def test_volume_fraction_within_distance_jacobi_at_max(self):
        from ppm.twistor import volume_fraction_within_distance, fs_distance_max
        f = volume_fraction_within_distance(fs_distance_max(), model='jacobi')
        self.assertAlmostEqual(f, 1.0, places=2)

    def test_alpha_from_volume_fraction_jacobi_uses_correct_model(self):
        from ppm.twistor import alpha_from_volume_fraction
        result = alpha_from_volume_fraction(model='jacobi')
        self.assertEqual(result['model_used'], 'jacobi')
        # For Jacobi: f(d) = sin³(2d) = α gives d* ≈ 0.0976, so d*/d_max ≈ 1/8
        self.assertAlmostEqual(result['d_alpha_over_d_max'], 1.0/8, delta=0.02)

    def test_alpha_from_volume_fraction_jacobi_exponent_is_three(self):
        from ppm.twistor import alpha_from_volume_fraction
        result = alpha_from_volume_fraction(model='jacobi')
        # Scaling exponent should be ~3 (codimension of RP3 in CP3)
        self.assertAlmostEqual(result['scaling_exponent'], 3.0, delta=0.2)

    def test_alpha_geometric_summary_has_jacobi_flag(self):
        from ppm.twistor import alpha_geometric_summary
        summary = alpha_geometric_summary()
        self.assertIn('jacobi_analysis', summary)
        self.assertTrue(summary['jacobi_analysis'])

    def test_volume_density_models_backward_compatible(self):
        from ppm.twistor import volume_density_at_distance
        # Legacy models should still work
        rho_s5 = volume_density_at_distance(np.pi/8, model='S5')
        rho_cp3 = volume_density_at_distance(np.pi/8, model='CP3')
        self.assertGreater(rho_s5, 0.0)
        self.assertGreater(rho_cp3, 0.0)

    def test_volume_fraction_models_backward_compatible(self):
        from ppm.twistor import volume_fraction_closed_form
        # Legacy models should still work
        f_s5 = volume_fraction_closed_form(np.pi/8, model='S5')
        f_cp3 = volume_fraction_closed_form(np.pi/8, model='CP3')
        self.assertGreater(f_s5, 0.0)
        self.assertGreater(f_cp3, 0.0)


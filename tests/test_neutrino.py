"""
PPM Framework — Neutrino Module Tests
=======================================

Tests for ppm.neutrino: strong-CP θ = 0, tribimaximal PMNS matrix,
sterile-neutrino mass window, neutrino mass bounds.

Run with:
    pytest tests/test_neutrino.py -v
"""

import unittest
from ppm import neutrino as NU


class TestThetaStrong(unittest.TestCase):

    def test_required_keys(self):
        result = NU.theta_strong()
        for key in ('theta', 'observed_bound', 'mechanism', 'status', 'note'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_theta_is_zero(self):
        self.assertEqual(NU.theta_strong()['theta'], 0.0)

    def test_observed_bound(self):
        """Neutron-EDM bound |θ| < 1e-10."""
        self.assertEqual(NU.theta_strong()['observed_bound'], 1e-10)

    def test_status_derived(self):
        self.assertEqual(NU.theta_strong()['status'], 'DERIVED')


class TestPmnsTribimaximal(unittest.TestCase):

    def test_required_keys(self):
        result = NU.pmns_tribimaximal()
        for key in ('sin2_theta12_ppm', 'sin2_theta23_ppm', 'sin2_theta13_ppm',
                    'sin2_theta12_obs', 'sin2_theta23_obs', 'sin2_theta13_obs',
                    'theta12_error_pct', 'theta23_error_pct',
                    'theta13_status', 'status', 'note'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_sin2_theta12_one_third(self):
        self.assertAlmostEqual(NU.pmns_tribimaximal()['sin2_theta12_ppm'],
                               1.0/3.0, places=12)

    def test_sin2_theta23_one_half(self):
        self.assertEqual(NU.pmns_tribimaximal()['sin2_theta23_ppm'], 0.5)

    def test_sin2_theta13_zero(self):
        """TBM zeroth order: sin²θ₁₃ = 0."""
        self.assertEqual(NU.pmns_tribimaximal()['sin2_theta13_ppm'], 0.0)

    def test_obs_tuples(self):
        """Observed values are (central, ±error) tuples."""
        result = NU.pmns_tribimaximal()
        for k in ('sin2_theta12_obs', 'sin2_theta23_obs', 'sin2_theta13_obs'):
            obs = result[k]
            self.assertEqual(len(obs), 2)
            self.assertGreater(obs[1], 0)  # error is positive

    def test_theta13_marked_excluded(self):
        result = NU.pmns_tribimaximal()
        self.assertIn('EXCLUDED', result['theta13_status'])


class TestSterileNeutrinoMassWindow(unittest.TestCase):

    def test_required_keys(self):
        result = NU.sterile_neutrino_mass_window()
        for key in ('k_lower', 'k_upper', 'E_lower_keV', 'E_upper_keV',
                    'xray_line_keV', 'brackets_xray', 'status', 'note'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_k_levels(self):
        result = NU.sterile_neutrino_mass_window()
        self.assertEqual(result['k_lower'], 62)
        self.assertEqual(result['k_upper'], 61)

    def test_lower_below_upper(self):
        """E_lower (k=62) < E_upper (k=61) since higher k = lower E."""
        result = NU.sterile_neutrino_mass_window()
        self.assertLess(result['E_lower_keV'], result['E_upper_keV'])

    def test_window_around_5_to_15_keV(self):
        result = NU.sterile_neutrino_mass_window()
        self.assertGreater(result['E_lower_keV'], 4.0)
        self.assertLess(result['E_lower_keV'], 7.0)
        self.assertGreater(result['E_upper_keV'], 12.0)
        self.assertLess(result['E_upper_keV'], 17.0)

    def test_xray_line_value(self):
        self.assertEqual(NU.sterile_neutrino_mass_window()['xray_line_keV'], 3.5)

    def test_brackets_xray_consistent(self):
        """brackets_xray flag is the literal E_lower < 3.5 < E_upper test."""
        result = NU.sterile_neutrino_mass_window()
        expected = (result['E_lower_keV'] < result['xray_line_keV']
                    < result['E_upper_keV'])
        self.assertEqual(result['brackets_xray'], expected)


class TestNeutrinoMassBounds(unittest.TestCase):

    def test_required_keys(self):
        result = NU.neutrino_mass_bounds()
        for key in ('k_range', 'E63_eV', 'E64_eV', 'delta_m2_obs',
                    'status', 'note'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_k_range(self):
        self.assertEqual(NU.neutrino_mass_bounds()['k_range'], (63, 64))

    def test_E63_above_E64(self):
        """E(k=63) > E(k=64) since higher k = lower E."""
        result = NU.neutrino_mass_bounds()
        self.assertGreater(result['E63_eV'], result['E64_eV'])


if __name__ == '__main__':
    unittest.main()

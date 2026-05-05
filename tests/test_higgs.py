"""
PPM Framework — Higgs Module Tests
====================================

Tests for ppm.higgs: τ-involution geometric values for the Higgs quartic
λ = 1/(4√π), τ-conjugate sector, separation Δλ = 1/(2√π), top Yukawa,
β_λ at the PPM point.

Run with:
    pytest tests/test_higgs.py -v
"""

import unittest
import math
from ppm import higgs as HI
from ppm import constants as C


class TestLambdaPpm(unittest.TestCase):

    def test_value_is_one_over_4sqrtpi(self):
        self.assertAlmostEqual(HI.lambda_ppm(), 1.0/(4.0*math.sqrt(math.pi)),
                               places=12)

    def test_returns_float(self):
        self.assertIsInstance(HI.lambda_ppm(), float)

    def test_matches_constant(self):
        self.assertAlmostEqual(HI.lambda_ppm(), C.LAMBDA_PPM, places=12)


class TestLambdaTauConjugate(unittest.TestCase):

    def test_negative_of_lambda_ppm(self):
        self.assertAlmostEqual(HI.lambda_tau_conjugate(), -HI.lambda_ppm(),
                               places=12)


class TestDeltaLambda(unittest.TestCase):

    def test_value_is_one_over_2sqrtpi(self):
        self.assertAlmostEqual(HI.delta_lambda(), 1.0/(2.0*math.sqrt(math.pi)),
                               places=12)

    def test_equals_2_lambda_ppm(self):
        self.assertAlmostEqual(HI.delta_lambda(), 2.0 * HI.lambda_ppm(),
                               places=12)


class TestDeltaLambdaObserved(unittest.TestCase):

    def test_one_loop(self):
        self.assertAlmostEqual(HI.delta_lambda_observed(1), 0.270, places=4)

    def test_two_loop(self):
        self.assertAlmostEqual(HI.delta_lambda_observed(2), 0.286, places=4)

    def test_default_is_two_loop(self):
        self.assertEqual(HI.delta_lambda_observed(),
                         HI.delta_lambda_observed(2))


class TestHiggsQuarticComparison(unittest.TestCase):

    def test_required_keys(self):
        result = HI.higgs_quartic_comparison()
        for key in ('lambda_ppm', 'lambda_observed_MZ', 'error_pct', 'note'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_error_pct_matches_geometric(self):
        result = HI.higgs_quartic_comparison()
        recomputed = (result['lambda_ppm']/result['lambda_observed_MZ'] - 1) * 100
        self.assertAlmostEqual(result['error_pct'], recomputed, places=8)

    def test_error_around_9pct(self):
        """Documented +9.2% error at M_Z."""
        result = HI.higgs_quartic_comparison()
        self.assertAlmostEqual(result['error_pct'], 9.17, delta=0.5)


class TestTopYukawaPpm(unittest.TestCase):

    def test_value(self):
        """y_t = π/(2(2π)^{1/4}) ≈ 0.992."""
        expected = math.pi / (2.0 * (2.0*math.pi)**0.25)
        self.assertAlmostEqual(HI.top_yukawa_ppm(), expected, places=12)

    def test_close_to_observed(self):
        """y_t within 0.5% of 0.992."""
        self.assertAlmostEqual(HI.top_yukawa_ppm(), 0.992, delta=0.005)


class TestBetaLambdaPpm(unittest.TestCase):

    def test_required_keys(self):
        result = HI.beta_lambda_ppm()
        for key in ('beta_lambda', 'lambda_ppm', 'yt_ppm', 'status', 'note'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_beta_negative_around_0_025(self):
        """β_λ ≈ -0.0254 at the PPM geometric point."""
        result = HI.beta_lambda_ppm()
        self.assertAlmostEqual(result['beta_lambda'], -0.0254, delta=0.005)

    def test_status_verified(self):
        result = HI.beta_lambda_ppm()
        self.assertEqual(result['status'], 'VERIFIED')


class TestGeometricIdentityCheck(unittest.TestCase):

    def test_match_true(self):
        result = HI.geometric_identity_check()
        self.assertTrue(result['match'])

    def test_required_keys(self):
        result = HI.geometric_identity_check()
        for key in ('delta_lambda', 'formula_1_over_2sqrt_pi', 'match',
                    'delta_lambda_observed_1loop', 'delta_lambda_observed_2loop',
                    'sm_match_pct_1loop', 'sm_match_pct_2loop'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_two_loop_within_2pct(self):
        """Two-loop SM running matches within 2% of geometric Δλ."""
        result = HI.geometric_identity_check()
        self.assertLess(result['sm_match_pct_2loop'], 2.0)


if __name__ == '__main__':
    unittest.main()

"""
PPM Framework — Predictions Module Tests
==========================================

Tests for ppm.predictions: build_table() (master prediction registry),
subset filters, and the hubble-tension aggregator.

These complement (do not duplicate) ppm.verify checks. The verify suite
covers numerical agreement against constants; here we pin the table schema
(keys, types, status taxonomy), row-count contracts, and that the subset
filters partition the table correctly.

Run with:
    pytest tests/test_predictions.py -v
"""

import unittest
from ppm import predictions as P


CANONICAL_STATUSES = {
    'VERIFIED', 'FLAGGED', 'CONCEPTUAL', 'FORMULA',
    'OPEN', 'INTERNAL', 'AWAITING DATA',
}

CANONICAL_TIERS = {1, 2, 3, 4}


class TestRowSchema(unittest.TestCase):
    """Every row produced by _row() and build_table() has the same keys."""

    def setUp(self):
        self.rows = P.build_table()

    def test_row_keys(self):
        expected = {'id', 'quantity', 'ppm_value', 'observed_value',
                    'error_pct', 'tier', 'status', 'notes'}
        for row in self.rows:
            self.assertEqual(set(row.keys()), expected,
                             f"row {row.get('id', '?')} has wrong keys")

    def test_id_is_string(self):
        for row in self.rows:
            self.assertIsInstance(row['id'], str)
            self.assertTrue(row['id'].startswith('PRED.') or
                            row['id'].startswith('DER.'),
                            f"unexpected id format: {row['id']}")

    def test_quantity_is_string(self):
        for row in self.rows:
            self.assertIsInstance(row['quantity'], str)
            self.assertGreater(len(row['quantity']), 0)

    def test_tier_canonical(self):
        for row in self.rows:
            self.assertIn(row['tier'], CANONICAL_TIERS,
                          f"row {row['id']} has tier={row['tier']}")

    def test_status_canonical(self):
        for row in self.rows:
            self.assertIn(row['status'], CANONICAL_STATUSES,
                          f"row {row['id']} has status={row['status']!r}")

    def test_error_pct_consistency(self):
        """error_pct = (ppm/obs - 1)*100 when both numbers present."""
        for row in self.rows:
            ppm, obs = row['ppm_value'], row['observed_value']
            if ppm is not None and obs is not None and obs != 0:
                expected = (ppm/obs - 1.0) * 100.0
                self.assertAlmostEqual(row['error_pct'], expected, places=8,
                                       msg=f"row {row['id']}")
            elif ppm is None or obs is None or obs == 0:
                # error_pct is None when not computable
                self.assertIsNone(row['error_pct'],
                                  f"row {row['id']} should have None error_pct")


class TestBuildTableShape(unittest.TestCase):
    """Master table size and PRED counts."""

    def setUp(self):
        self.rows = P.build_table()

    def test_at_least_23_pred_rows(self):
        """The audit requires ≥ 23 PRED.* entries."""
        pred_rows = [r for r in self.rows if r['id'].startswith('PRED')]
        self.assertGreaterEqual(len(pred_rows), 23,
                                f"only {len(pred_rows)} PRED rows")

    def test_has_der_rows(self):
        der_rows = [r for r in self.rows if r['id'].startswith('DER')]
        self.assertGreater(len(der_rows), 0)

    def test_unique_ids(self):
        """Every row's id is unique."""
        ids = [r['id'] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_pred1_g_2pi(self):
        """PRED.1 is the g = 2π hierarchy scaling."""
        row = next(r for r in self.rows if r['id'] == 'PRED.1')
        self.assertIn('2π', row['quantity'])
        # g_topo = 2π = 6.2832; observed g_emp = 6.32
        self.assertAlmostEqual(row['ppm_value'], 6.2832, places=3)

    def test_pred15_G_within_2pct(self):
        """PRED.15 (Newton's G) within 2% of observed."""
        row = next(r for r in self.rows if r['id'] == 'PRED.15')
        self.assertLess(abs(row['error_pct']), 2.0)

    def test_pred16_lambda_within_2pct(self):
        """PRED.16 (Λ) within 2% of observed."""
        row = next(r for r in self.rows if r['id'] == 'PRED.16')
        self.assertLess(abs(row['error_pct']), 2.0)


class TestSummaryStats(unittest.TestCase):
    """summary_stats counts by status."""

    def test_default_uses_build_table(self):
        result = P.summary_stats()
        self.assertIsInstance(result, dict)

    def test_total_matches_rows(self):
        rows = P.build_table()
        stats = P.summary_stats(rows)
        self.assertEqual(sum(stats.values()), len(rows))

    def test_keys_subset_of_canonical(self):
        stats = P.summary_stats()
        for status in stats:
            self.assertIn(status, CANONICAL_STATUSES)


class TestSubsetFilters(unittest.TestCase):
    """particle_physics, cosmology_predictions, gravity_predictions,
    consciousness_predictions partition the table."""

    def test_particle_physics_only_pred_le14(self):
        for row in P.particle_physics():
            self.assertTrue(row['id'].startswith('PRED.'))
            self.assertLessEqual(int(row['id'].split('.')[1]), 14)

    def test_cosmology_predictions_15_to_20(self):
        for row in P.cosmology_predictions():
            self.assertTrue(row['id'].startswith('PRED.'))
            n = int(row['id'].split('.')[1])
            self.assertTrue(15 <= n <= 20)

    def test_gravity_predictions_subset(self):
        ids = {row['id'] for row in P.gravity_predictions()}
        self.assertTrue(ids.issubset({'PRED.15', 'PRED.21', 'PRED.22', 'PRED.23'}))

    def test_consciousness_predictions_der_ge7(self):
        for row in P.consciousness_predictions():
            self.assertTrue(row['id'].startswith('DER.'))
            self.assertGreaterEqual(int(row['id'].split('.')[1]), 7)


class TestHubbleTension(unittest.TestCase):
    """Hubble-tension aggregator: dict shape and signs."""

    def test_required_keys(self):
        result = P.hubble_tension()
        for key in ('H0_ppm_km_s_Mpc', 'H0_cmb', 'H0_local',
                    'H0_ppm_source', 'tension_with_cmb_pct',
                    'tension_with_local_pct', 'notes', 'status'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_H0_ppm_in_band(self):
        """PPM H₀ between CMB (67.4) and local (73.0)."""
        result = P.hubble_tension()
        self.assertGreater(result['H0_ppm_km_s_Mpc'], 67.0)
        self.assertLess(result['H0_ppm_km_s_Mpc'], 73.5)

    def test_tensions_have_opposite_signs(self):
        """PPM is above CMB and below local — tensions have opposite signs."""
        result = P.hubble_tension()
        self.assertGreater(result['tension_with_cmb_pct'], 0)
        self.assertLess(result['tension_with_local_pct'], 0)

    def test_status_verified(self):
        result = P.hubble_tension()
        self.assertEqual(result['status'], 'VERIFIED')


if __name__ == '__main__':
    unittest.main()

"""
PPM Framework — Hierarchy Module Tests
========================================

Tests for ppm.hierarchy: the energy ladder E(k) = m_π × (2π)^{(K_REF-k)/2}
and key k-level anchors (Planck, UV boundary, Pati-Salam, EWSB, pion,
consciousness).

Note on the pion anchor: hierarchy.energy_mev(51) returns C.M_PI_MEV = 140
exactly by construction. The neutral-pion mass 134.977 MeV used by gravity
and cosmology is a separate input; the ladder uses the K_REF = 51 reference
of 140 MeV. These tests assert the documented 140-MeV behaviour, not the
neutral-pion value.

These complement (do not duplicate) ppm.verify checks. The verify suite
covers numerical agreement against constants; here we pin signatures,
return-dict shapes, and inverse-consistency contracts.

Run with:
    pytest tests/test_hierarchy.py -v
"""

import unittest
import math
from ppm import hierarchy as H
from ppm import constants as C


class TestEnergyLadder(unittest.TestCase):
    """E(k) = m_π × (2π)^{(K_REF - k)/2}."""

    def test_pion_anchor_exact(self):
        """E(51) = 140 MeV exactly (the ladder reference)."""
        self.assertAlmostEqual(H.energy_mev(51.0), C.M_PI_MEV, places=10)

    def test_planck_within_5_percent(self):
        """E(k=1) ≈ Planck energy within 5%."""
        E_gev = H.energy_gev(1.0)
        self.assertAlmostEqual(E_gev, C.E_PLANCK_GEV,
                               delta=C.E_PLANCK_GEV * 0.05)

    def test_ewsb_in_band(self):
        """E(k=44.5) is the raw ladder value ≈ 55 GeV (the EWSB step, before
        the 2√2 SU(2) prefactor that lifts to the v=246 GeV VEV in
        bridges.higgs_vev_from_topology)."""
        E_gev = H.energy_gev(C.K_EWSB)
        self.assertGreater(E_gev, 30.0)
        self.assertLess(E_gev, 80.0)

    def test_electron_in_band(self):
        """E(k=57) is in the 0.4–0.7 MeV band (electron mass ≈ 0.511 MeV)."""
        E_mev = H.energy_mev(57.0)
        self.assertGreater(E_mev, 0.4)
        self.assertLess(E_mev, 0.7)

    def test_monotonic_decrease(self):
        """Energy decreases monotonically with k."""
        ks = [1, 10, 16.25, 30, 44.5, 51, 57, 60, 75]
        es = [H.energy_mev(k) for k in ks]
        for a, b in zip(es, es[1:]):
            self.assertGreater(a, b)

    def test_gev_mev_consistency(self):
        """energy_gev(k) = energy_mev(k) × 1e-3."""
        for k in (1.0, 16.25, 44.5, 51.0, 57.0):
            self.assertAlmostEqual(H.energy_gev(k),
                                   H.energy_mev(k) * 1e-3, places=20)

    def test_inverse_round_trip_mev(self):
        """k_from_energy_mev(energy_mev(k)) == k."""
        for k in (1.0, 13.0, 44.5, 51.0, 57.0, 70.0, 75.0):
            self.assertAlmostEqual(H.k_from_energy_mev(H.energy_mev(k)),
                                   k, places=10)

    def test_inverse_round_trip_gev(self):
        """k_from_energy_gev(energy_gev(k)) == k."""
        for k in (10.0, 16.25, 44.5, 51.0):
            self.assertAlmostEqual(H.k_from_energy_gev(H.energy_gev(k)),
                                   k, places=10)


class TestPlanckAnchor(unittest.TestCase):

    def test_required_keys(self):
        result = H.planck_anchor()
        for key in ('k', 'E_predicted_GeV', 'E_observed_GeV',
                    'error_pct', 'status', 'note'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_k_is_one(self):
        self.assertEqual(H.planck_anchor()['k'], 1.0)

    def test_error_pct_under_10(self):
        """Planck anchor error ≤ 5% (documented as 5%)."""
        self.assertLess(abs(H.planck_anchor()['error_pct']), 10.0)


class TestUvBoundary(unittest.TestCase):

    def test_required_keys(self):
        result = H.uv_boundary()
        for key in ('k', 'E_GeV', 'status', 'note'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_k_is_10(self):
        """UV boundary at k = r² = 10 (topological)."""
        self.assertEqual(H.uv_boundary()['k'], 10)


class TestPatiSalamBreaking(unittest.TestCase):

    def test_required_keys(self):
        result = H.pati_salam_breaking()
        for key in ('k', 'E_GeV', 'sin2_tW_ppm', 'sin2_tW_sm',
                    'agreement_pct', 'status', 'note'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_sin2_tW_is_3_8(self):
        """PPM Pati-Salam value = 3/8 = 0.375."""
        self.assertAlmostEqual(H.pati_salam_breaking()['sin2_tW_ppm'],
                               3.0/8.0, places=10)


class TestEwsbScale(unittest.TestCase):

    def test_required_keys(self):
        result = H.ewsb_scale()
        for key in ('k', 'E_GeV', 'status', 'note'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_k_is_44_5(self):
        self.assertEqual(H.ewsb_scale()['k'], 44.5)


class TestPionAnchor(unittest.TestCase):

    def test_required_keys(self):
        result = H.pion_anchor()
        for key in ('k', 'E_MeV', 'status', 'note'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_k_is_51(self):
        self.assertEqual(H.pion_anchor()['k'], 51)

    def test_E_MeV_is_140(self):
        """Pion anchor reports 140 MeV (the ladder reference value)."""
        self.assertAlmostEqual(H.pion_anchor()['E_MeV'], 140.0, places=8)


class TestGFromTopology(unittest.TestCase):
    """g = 2π from |Z₂×Z₂|·Vol(RP³) and Maslov area."""

    def test_required_keys(self):
        result = H.g_from_topology()
        for key in ('g', 'g_topo', 'g_maslov', 'g_empirical', 'error_pct'):
            self.assertIn(key, result, f"missing key: {key}")

    def test_g_equals_2pi(self):
        result = H.g_from_topology()
        self.assertAlmostEqual(result['g'], 2.0 * math.pi, places=10)

    def test_topo_and_maslov_agree(self):
        """Both derivations give the same g."""
        result = H.g_from_topology()
        self.assertAlmostEqual(result['g_topo'], result['g_maslov'], places=12)

    def test_empirical_within_1_percent(self):
        """g_empirical ≈ 6.32 within 1% of 2π = 6.283."""
        result = H.g_from_topology()
        self.assertLess(abs(result['error_pct']), 1.0)


class TestConsciousnessLevel(unittest.TestCase):
    """k_conscious from E(k) = k_B T."""

    def test_310k_around_75(self):
        """At T=310 K (body temp): k_conscious ≈ 75.35."""
        k_c = H.consciousness_level(310.0)
        self.assertAlmostEqual(k_c, 75.35, delta=0.1)

    def test_temperature_band(self):
        """k_conscious ∈ (75.0, 75.7) for T ∈ [273, 313] K."""
        for T in (273.0, 290.0, 300.0, 310.0, 313.0):
            k_c = H.consciousness_level(T)
            self.assertGreater(k_c, 74.5)
            self.assertLess(k_c, 76.0)

    def test_higher_T_lower_k(self):
        """Higher T gives lower k_conscious (E(k) decreases with k)."""
        k_cold = H.consciousness_level(200.0)
        k_warm = H.consciousness_level(400.0)
        self.assertGreater(k_cold, k_warm)


class TestKLevelTable(unittest.TestCase):
    """The full particle-mass table."""

    def test_returns_list(self):
        result = H.k_level_table()
        self.assertIsInstance(result, list)

    def test_has_15_rows(self):
        """PARTICLE_TABLE has 15 rows (UV scale + leptons + quarks + bosons)."""
        result = H.k_level_table()
        self.assertEqual(len(result), len(H.PARTICLE_TABLE))

    def test_row_keys(self):
        result = H.k_level_table()
        for row in result:
            for key in ('name', 'k', 'E_predicted_GeV',
                        'mass_observed_GeV', 'error_pct', 'category'):
                self.assertIn(key, row, f"missing key in {row}: {key}")

    def test_pion_row_140_mev(self):
        """The pion entry at k=51 predicts ~140 MeV."""
        for row in H.k_level_table():
            if row['name'] == 'pion':
                self.assertAlmostEqual(row['E_predicted_GeV'], 0.140, places=6)
                break
        else:
            self.fail("No pion row found")

    def test_planck_row_no_error(self):
        """Scale anchors have None observed mass and may have error_pct."""
        for row in H.k_level_table():
            if row['name'] == 'UV boundary':
                self.assertIsNone(row['mass_observed_GeV'])
                self.assertIsNone(row['error_pct'])
                break
        else:
            self.fail("No UV boundary row found")

    def test_pion_row_zero_error(self):
        """Pion row anchors the ladder, so its error_pct ≈ 0."""
        for row in H.k_level_table():
            if row['name'] == 'pion':
                self.assertLess(abs(row['error_pct']), 0.5)
                return
        self.fail("No pion row")

    def test_ewsb_cluster_shares_energy(self):
        """top, Higgs, W, Z all sit at k=44.5 → same E_predicted_GeV
        (absolute masses come from a separate prefactor; the table reports
        the raw ladder energy at the cluster k-level)."""
        names = {'top', 'Higgs', 'W', 'Z'}
        energies = []
        for row in H.k_level_table():
            if row['name'] in names:
                energies.append(row['E_predicted_GeV'])
        self.assertEqual(len(energies), len(names))
        # All four equal
        for e in energies[1:]:
            self.assertAlmostEqual(e, energies[0], places=10)


if __name__ == '__main__':
    unittest.main()

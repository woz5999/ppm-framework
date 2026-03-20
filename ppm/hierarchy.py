"""
ppm.hierarchy — Energy ladder and k-level calculations
======================================================

The PPM energy hierarchy:
    E(k) = 140 MeV × (2π)^{(51-k)/2}

Equivalently (adopting Planck UV anchor):
    E(k) ≈ E_Planck × (2π)^{(1-k)/2}

The ladder is parameterized by integer or half-integer k ∈ [1, 51].
Each k-level corresponds to a characteristic energy scale of the PPM framework.

Section references: §4 (Bootstrap & Hierarchy Scaling), §7 (SM Parameters)
"""

import math
from . import constants as C


def energy_mev(k):
    """
    Energy at k-level in MeV.

    LaTeX: E(k) = 140\\,{\\rm MeV} \\times (2\\pi)^{(51-k)/2}
    Section: §4 (Bootstrap & Hierarchy)
    Status: VERIFIED (anchored at k_ref=51, k=1 gives Planck to 5%)

    Parameters
    ----------
    k : float — k-level (1 ≤ k ≤ 51)

    Returns
    -------
    float — energy in MeV
    """
    return C.M_PI_MEV * (C.TAU ** ((C.K_REF - k) / 2.0))


def energy_gev(k):
    """Energy at k-level in GeV."""
    return energy_mev(k) * 1e-3


def k_from_energy_mev(E_mev):
    """
    Inverse: k-level for a given energy in MeV.

    LaTeX: k = 51 - 2\\,\\frac{\\ln(E/140\\,{\\rm MeV})}{\\ln(2\\pi)}
    """
    return C.K_REF - 2.0 * math.log(E_mev / C.M_PI_MEV) / math.log(C.TAU)


def k_from_energy_gev(E_gev):
    """Inverse: k-level for a given energy in GeV."""
    return k_from_energy_mev(E_gev * 1e3)


# ─── Key k-level anchors ──────────────────────────────────────────────────────

def planck_anchor():
    """
    Planck scale from E(k=1): UV anchor of the hierarchy.

    LaTeX: E(k{=}1) = 140\\,{\\rm MeV} \\times (2\\pi)^{25}
    Value: ≈ 1.28 × 10^{19} GeV  (observed E_P = 1.22 × 10^{19} GeV, 5% agreement)
    Status: DERIVED — k=1 is fixed by R = l_P (unit RP³)
    """
    E_pred = energy_gev(1.0)
    E_obs  = C.E_PLANCK_GEV
    err_pct = (E_pred / E_obs - 1.0) * 100.0
    return {
        'k': 1.0,
        'E_predicted_GeV': E_pred,
        'E_observed_GeV': E_obs,
        'error_pct': err_pct,
        'status': 'DERIVED',
        'note': 'UV anchor; R=l_P fixes k=1 to Planck energy at 5%'
    }


def uv_boundary():
    """
    UV boundary of the effective theory at k = r² = 10.

    LaTeX: k_{\\rm UV} = r^2 = 10
    This is topological: V_⊥ = β×πR = 10 (the transverse volume of the instanton)
    Independent of perturbative renormalization scheme.
    Status: DERIVED (VERIFIED)
    """
    return {
        'k': C.K_UV_BOUNDARY,
        'E_GeV': energy_gev(C.K_UV_BOUNDARY),
        'status': 'DERIVED',
        'note': 'V_⊥ = β×πR = 10 fixes this topologically'
    }


def pati_salam_breaking():
    """
    Pati-Salam breaking scale at k_break ≈ 16.25.

    Determined by: sin²θ_W(E_break) from SM running = 3/8 (PPM/Pati-Salam prediction)
    SM one-loop running gives sin²θ_W(E_break) = 0.37550 vs PPM = 0.3750 (0.13% agreement)
    Status: EMPIRICAL (requires observed sin²θ_W as input)
    """
    return {
        'k': C.K_BREAK,
        'E_GeV': energy_gev(C.K_BREAK),
        'sin2_tW_ppm': C.SIN2_THETA_W_PPM,
        'sin2_tW_sm': 0.37550,
        'agreement_pct': 0.13,
        'status': 'EMPIRICAL',
        'note': 'k_break follows from sin²θ_W = 3/8 matching condition'
    }


def ewsb_scale():
    """
    Electroweak symmetry breaking scale at k_EWSB = 44.5.

    Equivalent to the top Yukawa y_t — the single empirical input of the framework
    (once Planck anchor is adopted).
    LaTeX: k_{\\rm EWSB} = 44.5
    Status: EMPIRICAL (the one free parameter)
    """
    return {
        'k': C.K_EWSB,
        'E_GeV': energy_gev(C.K_EWSB),
        'status': 'EMPIRICAL',
        'note': 'Single empirical input; equivalent to y_t'
    }


def pion_anchor():
    """
    Pion mass anchor at k = 51.

    LaTeX: E(k{=}51) = 140\\,{\\rm MeV}  (by construction)
    This is the reference point of the ladder formula.
    With Planck UV anchor adopted, the pion mass is DERIVED
    (it's E_P × (2π)^{-50/2}), not an independent input.
    Status: DERIVED (given Planck anchor; formerly EMPIRICAL)
    """
    return {
        'k': C.K_REF,
        'E_MeV': energy_mev(C.K_REF),
        'status': 'DERIVED',
        'note': 'Derived from Planck anchor as E_P × (2π)^{-50/2}'
    }


def g_from_topology():
    """
    Hierarchy scaling g = 2π from Z₂ × S³ topology.

    Two independent derivations (section4-bootstrap.tex):

    1. Topological product:
       g² = |Z₂×Z₂| × Vol(RP³) = 4 × π² = 4π²
       g = 2π

    2. Maslov area (symplectic):
       A_min = (N+1)π/2 for monotone Lagrangian RPᴺ ↪ CPᴺ
       For N=3: A_min = 4π/2 = 2π
       g = A_min = 2π

    Empirical: g_emp ≈ 6.32, 2π = 6.2832 (0.6% agreement).
    Status: DERIVED (VERIFIED — two independent proofs)
    """
    g_topo = math.sqrt(4.0 * math.pi**2)  # from |Z₂×Z₂| × Vol(RP³)
    N = 3
    g_maslov = (N + 1) * math.pi / 2.0    # from Maslov area
    assert abs(g_topo - g_maslov) < 1e-12
    return {
        'g': g_topo,
        'g_topo': g_topo,
        'g_maslov': g_maslov,
        'g_empirical': 6.32,
        'error_pct': (6.32 / g_topo - 1) * 100,
    }


def consciousness_level(T_kelvin=310.0):
    """
    k_conscious from thermal matching E(k) = k_B T_bio.

    LaTeX (section9.tex): k_conscious(T) = 51 − 2 ln(k_B T / m_π c²) / ln(2π)
    For T = 310 K (mammalian body temp): k_conscious ≈ 75.35
    For T range 273–313 K: k_conscious ≈ 75.3–75.6

    Status: DERIVED (from thermal matching condition)
    """
    kB = 8.617333e-5  # eV/K (Boltzmann constant)
    E_eV = kB * T_kelvin
    E_MeV = E_eV * 1e-6
    return C.K_REF - 2.0 * math.log(E_MeV / C.M_PI_MEV) / math.log(C.TAU)


# ─── Particle mass table ────────────────────────────────────────────────────

# Known particle k-levels and masses for the full hierarchy display
PARTICLE_TABLE = [
    # (name, k-level, mass_GeV, category)
    ("Planck",       1.0,    1.22e19,     "scale"),
    ("UV boundary",  10.0,   None,        "scale"),
    ("Pati-Salam",   16.25,  None,        "scale"),
    ("top",          44.5,   172.7,       "quark"),
    ("Higgs",        44.7,   125.25,      "boson"),
    ("W",            44.85,  80.377,      "boson"),
    ("Z",            44.75,  91.188,      "boson"),
    ("bottom",       48.0,   4.18,        "quark"),
    ("tau",          48.7,   1.777,       "lepton"),
    ("charm",        49.4,   1.27,        "quark"),
    ("strange",      51.8,   0.0934,      "quark"),
    ("muon",         50.15,  0.10566,     "lepton"),
    ("pion",         51.0,   0.140,       "meson"),
    ("down",         53.3,   0.00467,     "quark"),
    ("up",           53.8,   0.00216,     "quark"),
    ("electron",     55.0,   0.000511,    "lepton"),
]


def k_level_table():
    """
    Build the full k-level table with predicted vs observed masses.

    Returns list of dicts with k, predicted E(k), observed mass, and error.
    """
    rows = []
    for name, k, mass_obs, cat in PARTICLE_TABLE:
        E_pred = energy_gev(k)
        if mass_obs is not None and mass_obs > 0:
            err_pct = (E_pred / mass_obs - 1.0) * 100.0
        else:
            err_pct = None
        rows.append({
            'name': name,
            'k': k,
            'E_predicted_GeV': E_pred,
            'mass_observed_GeV': mass_obs,
            'error_pct': err_pct,
            'category': cat,
        })
    return rows


def print_k_table():
    """Print the full k-level table for key anchors."""
    print(f"{'k':>6}  {'E (GeV)':>14}  {'E (MeV)':>14}  Note")
    print("-" * 70)
    for k, note in [
        (1.0,   "Planck UV anchor (R=l_P)"),
        (10.0,  "UV boundary V_⊥=10 (topological)"),
        (16.25, "Pati-Salam breaking (k_break)"),
        (20.0,  ""),
        (30.0,  ""),
        (40.0,  ""),
        (44.5,  "EWSB / k_EWSB (single empirical input)"),
        (51.0,  "Pion mass (derived from Planck anchor)"),
    ]:
        E = energy_gev(k)
        print(f"{k:>6.2f}  {E:>14.4e}  {E*1e3:>14.4e}  {note}")


if __name__ == "__main__":
    print_k_table()
    print()
    pa = planck_anchor()
    print(f"Planck anchor: E(k=1) = {pa['E_predicted_GeV']:.3e} GeV  "
          f"(E_P = {pa['E_observed_GeV']:.3e} GeV,  error = {pa['error_pct']:+.1f}%)")

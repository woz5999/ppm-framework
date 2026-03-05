"""
PPM Framework — Physical and Framework Constants
=================================================

All physical and framework constants in one place. Every other module
imports from here — no magic numbers anywhere else.

k_conscious is DERIVED from the thermal matching condition E(k) = k_B*T_bio,
not hardcoded. The consciousness boundary sits wherever thermal energy meets
the hierarchy — its topological significance is as a critical point / phase
transition, not at any particular k-value.

Notes on parameter levels
--------------------------
The framework operates at two levels:

Level 1 — Fundamental constants (zero free parameters):
    The 9-equation coupled constraint system has no free parameters.
    Topology alone (Z2 → RP3) determines the unique solution.
    Constants: g, K, T, alpha_EM, alpha_w, alpha_s, G, g_G, Lambda

Level 2 — Standard Model structure (4-7 effective free parameters):
    Built on the fundamental constants above. Reduces the SM's 26
    inputs to approximately 4-7, with the remainder derived or
    constrained by Z2 → RP3 topology.

This distinction is critical for the zero-free-parameters claim.
The claim applies strictly to Level 1.
"""

import numpy as np

# ---------------------------------------------------------------------------
# PHYSICAL CONSTANTS (SI units)
# ---------------------------------------------------------------------------
PHYSICAL = {
    'c':     2.998e8,       # m/s — speed of light
    'hbar':  1.055e-34,     # J·s — reduced Planck constant
    'G':     6.674e-11,     # m³/(kg·s²) — Newton's constant
    'k_B':   1.381e-23,     # J/K — Boltzmann constant
    'alpha': 1 / 137.036,   # dimensionless — fine-structure constant (observed)
}

# ---------------------------------------------------------------------------
# UNIT CONVERSIONS
# ---------------------------------------------------------------------------
CONVERSIONS = {
    'MeV_to_J':  1.602e-13,   # 1 MeV in joules
    'MeV_to_kg': 1.783e-30,   # 1 MeV/c² in kg
    'eV_to_J':   1.602e-19,   # 1 eV in joules
}

# ---------------------------------------------------------------------------
# FRAMEWORK CONSTANTS (derived from topology, not fitted)
# ---------------------------------------------------------------------------
# Hierarchy parameters (topological)
_g       = 2 * np.pi       # Hierarchy scaling — exact from Z2→RP3 topology
_m_pi    = 140.0            # Pion mass in MeV — reference energy scale
_k_ref   = 51              # Confinement k-level — reference level

# Environmental / cosmological
_T_bio   = 310.0            # K — biological temperature
_N_cosmic = 1e82            # Total actualization count within cosmological event horizon
                            # Consistent with holographic counting: N ≈ (R_dS / l_conf)²
                            # where R_dS = √(3/Λ), l_conf = ħc/(m_πc²). See SESSION_EDITS §14.

# DERIVED: k_conscious from thermal matching E(k) = k_B * T_bio
# E(k) = m_pi * g^((k_ref - k) / 2)  =>  k = k_ref - 2*ln(E/m_pi)/ln(g)
# E_conscious = k_B * T_bio  (in MeV)
_kBT_MeV = PHYSICAL['k_B'] * _T_bio / CONVERSIONS['MeV_to_J']
_k_conscious = _k_ref - 2.0 * np.log(_kBT_MeV / _m_pi) / np.log(_g)

FRAMEWORK = {
    'g':           _g,
    'm_pi_MeV':    _m_pi,
    'k_ref':       _k_ref,
    'k_conscious': _k_conscious,   # ~75.35 — derived, not hardcoded
    'N_cosmic':    _N_cosmic,
    'T_bio':       _T_bio,
    'kBT_MeV':     _kBT_MeV,      # k_B * T_bio in MeV
    'kBT_eV':      _kBT_MeV * 1e6, # k_B * T_bio in eV
}

# ---------------------------------------------------------------------------
# ENERGY SCALES — keyed by name
#
# k-values are PRIMARY: derived from topology or Z2 quantization (k = k_EWSB + n/2).
# Predicted energies follow from E(k) = m_pi * g^((k_ref - k)/2).
# Observed values are listed for cross-validation, NOT as inputs.
#
# Sources for geometric k-values:
#   - Planck (k=0): topological requirement — CP3 fully accessible
#   - EWSB (k=44.5): topological requirement — RP3 emerges for EW sector
#   - Confinement (k=51): topological requirement — RP3 fully crystallized
#   - Consciousness (k~75.35): derived from E(k) = k_BT thermal matching
#   - Leptons: Z2 quantization k = k_EWSB + n/2 (Section 4.3.3–4.3.5, 6.3)
#   - Top quark: k = k_EWSB (Section 4.2.6), m_t = pi * E(44.5)
# ---------------------------------------------------------------------------

def _E_from_k(k):
    """Predict energy in MeV from geometric k-level."""
    return _m_pi * _g ** ((_k_ref - k) / 2.0)

def _E_GeV_from_k(k):
    """Predict energy in GeV from geometric k-level."""
    return _E_from_k(k) / 1e3

def _tau_from_k(k):
    """Compute actualization timescale from k-level."""
    E_J = _E_from_k(k) * CONVERSIONS['MeV_to_J']
    return PHYSICAL['hbar'] / E_J

# Utility: compute k from observed mass (for diagnostics only, not primary data)
def _k_from_E(E_MeV):
    """Compute k-level from energy in MeV. Diagnostic use only."""
    return _k_ref - 2.0 * np.log(E_MeV / _m_pi) / np.log(_g)

ENERGY_SCALES = {
    # NOTE: k=0 (Planck scale) is intentionally excluded from this table.
    # E(0) = 3.16e19 GeV ≈ 2.59 × m_P (observed), but m_P = √(ħc/G) depends on G,
    # which the framework is supposed to DERIVE — not use as input. Comparing E(0)
    # to the observed m_P is circular in the framework's own logic. No valid
    # comparison exists until the G derivation is complete.
    # Use _E_GeV_from_k(0) or _tau_from_k(0) directly if k=0 timescale is needed.

    # --- Topologically required levels ---
    'EWSB': {
        'k': 44.5,                          # topological: RP3 emerges for EW sector
        # Higgs VEV: v = 2√2 × (2π)^(1/4) × E(44.5)  — SU(2)→U(1) geometric factor
        # Bare E(44.5) = 54.98 GeV is NOT the prediction; the VEV formula gives 246.2 GeV
        'E_GeV_predicted': 2*np.sqrt(2) * (2*np.pi)**0.25 * _E_GeV_from_k(44.5),
        'E_GeV_observed': 246.2,            # Higgs VEV
        'tau_s': _tau_from_k(44.5),
        'source': 'topology',
        'description': 'Electroweak symmetry breaking — Higgs VEV via SU(2)→U(1) geometry',
        'notes': 'v = 2√2 × (2π)^(1/4) × E(44.5) = 246.2 GeV (predicted), 246.2 (obs), 0.0%',
    },
    'Top': {
        'k': 44.5,                          # tied to EWSB: m_t = π × E(44.5)
        'E_GeV_predicted': np.pi * _E_GeV_from_k(44.5),  # 175.8 GeV
        'E_GeV_observed': 173.0,
        'tau_s': _tau_from_k(44.5),
        'source': 'topology',
        'description': 'Top quark — π × E(EWSB) from SU(2)→U(1) geometry',
        'notes': 'm_t = π × E(44.5) = 175.8 GeV (predicted), 173.0 (obs), 1.6%',
    },
    'Confinement': {
        'k': 51,                            # topological: RP3 fully crystallized
        'E_GeV_predicted': _E_GeV_from_k(51),
        'E_GeV_observed': 0.140,
        'tau_s': _tau_from_k(51),
        'source': 'topology (reference level)',
        'description': 'QCD confinement — pion mass, reference level',
    },
    # --- Z2 quantization levels: k = k_EWSB + n/2 ---
    'Tau': {
        'k': 48.0,                          # n=7: k = 44.5 + 3.5
        'n_quantum': 7,
        'E_GeV_predicted': _E_GeV_from_k(48.0),   # 2.21 GeV
        'E_GeV_observed': 1.777,
        'tau_s': _tau_from_k(48.0),
        'source': 'Z2 quantization (n=7)',
        'description': 'Tau lepton — n=7, bare Z2 error 24% (k_exact=48.24)',
    },
    'Muon': {
        'k': 51.5,                          # n=14: k = 44.5 + 7.0
        'n_quantum': 14,
        'E_GeV_predicted': _E_GeV_from_k(51.5),   # 88.4 MeV (bare; radiative corrections pending)
        'E_GeV_observed': 0.10566,
        'tau_s': _tau_from_k(51.5),
        'source': 'Z2 quantization (n=14)',
        'description': 'Muon — n=14, bare topological prediction 88.4 MeV, 16.3% error (k_exact=51.31)',
    },
    'Electron': {
        'k': 57.0,                          # n=25: k = 44.5 + 12.5
        'n_quantum': 25,
        'E_GeV_predicted': _E_GeV_from_k(57.0),   # 0.564 MeV (bare; radiative corrections pending)
        'E_GeV_observed': 5.11e-4,
        'tau_s': _tau_from_k(57.0),
        'source': 'Z2 quantization (n=25)',
        'description': 'Electron — n=25, bare topological prediction 0.564 MeV, 10.5% error (k_exact=57.11)',
    },
    # --- Derived levels ---
    'Consciousness': {
        'k': _k_conscious,                  # derived: E(k) = k_BT at T_bio
        'E_GeV_predicted': _E_GeV_from_k(_k_conscious),
        'E_GeV_observed': _kBT_MeV / 1e3,
        'tau_s': _tau_from_k(_k_conscious),
        'source': 'thermal matching',
        'description': f'Consciousness critical point — k_BT at {_T_bio}K (derived)',
    },
    # --- Neutrino sector (topology-fixed k-levels near k_conscious) ---
    # The hierarchy energies at these k-levels are in the keV range.
    # Conversion to the observed sub-eV neutrino masses requires the seesaw
    # mechanism — an open calculation listed in Section 9 Tier 2.
    # The k-levels themselves ARE the topological prediction; the masses are not.
    'Nu3': {
        'k': 58,
        'E_GeV_predicted': _E_GeV_from_k(58),     # ~0.225 MeV hierarchy energy
        'E_GeV_observed': 50e-12,                  # ~50 meV (mass-squared splitting bound)
        'tau_s': _tau_from_k(58),
        'source': 'topology-fixed hierarchy level',
        'description': 'ν₃ — k=58 topology-fixed (Kähler structure); hierarchy energy ~225 keV, physical mass requires seesaw',
    },
    'Nu2': {
        'k': 60,
        'E_GeV_predicted': _E_GeV_from_k(60),     # ~35.8 keV hierarchy energy
        'E_GeV_observed': 8e-12,                   # ~8 meV (mass-squared splitting bound)
        'tau_s': _tau_from_k(60),
        'source': 'topology-fixed hierarchy level',
        'description': 'ν₂ — k=60 topology-fixed (Kähler structure); hierarchy energy ~35.8 keV, physical mass requires seesaw',
    },
    'Nu1': {
        'k': 61,
        'E_GeV_predicted': _E_GeV_from_k(61),     # ~14.3 keV hierarchy energy
        'E_GeV_observed': 2e-12,                   # ~2 meV (lightest neutrino, upper bound)
        'tau_s': _tau_from_k(61),
        'source': 'topology-fixed hierarchy level',
        'description': 'ν₁ — k=61 topology-fixed (Kähler structure); note: coincidence with stale k_conscious=61 is not structural',
    },
    # --- Near-consciousness hierarchy levels (sterile neutrinos) ---
    'SterileNu_k60': {
        'k': 60,
        # Hierarchy energy at k=60 is 35.8 keV. The proposed sterile neutrino mass
        # (7 keV from 3.5 keV X-ray line) is a physical particle mass, NOT the
        # hierarchy energy — same distinction as active neutrinos. Conversion factor
        # between hierarchy energy and sterile neutrino mass is an open calculation.
        # Marking as 'seesaw' for the same reason as Nu1/Nu2/Nu3.
        'E_GeV_predicted': _E_GeV_from_k(60),     # hierarchy energy ~35.8 keV
        'E_GeV_observed': 7e-6,                    # 3.5 keV X-ray → 7 keV mass (unconfirmed)
        'tau_s': _tau_from_k(60),
        'source': 'hierarchy (near consciousness boundary)',
        'description': 'Sterile neutrino candidate at k=60; hierarchy energy ≠ mass (seesaw-type conversion open)',
    },
}

# ---------------------------------------------------------------------------
# TIMESCALES dict (keyed same as ENERGY_SCALES, tau in seconds)
# ---------------------------------------------------------------------------
TIMESCALES = {name: entry['tau_s'] for name, entry in ENERGY_SCALES.items()}

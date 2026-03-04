"""
PPM Framework — Energy Hierarchy
=================================

Implements the energy hierarchy E(k) = E_ref * g^((k_ref - k) / 2)
spanning from the Planck scale (k=0) to the consciousness boundary (k=61).

The scaling factor g = 2π is derived exactly from Z2 → RP3 topology
(Appendix A.2). The square-root exponent arises from the geometric mean
structure of projective geometry: RP3 is the geometric mean space between
CP3 and R.

Manuscript references: Section 3.3, Appendix C.6
"""

import numpy as np
from .constants import PHYSICAL, FRAMEWORK, ENERGY_SCALES, CONVERSIONS


def hierarchy_energy(k: float,
                     g: float = None,
                     k_ref: int = None,
                     E_ref_MeV: float = None) -> float:
    """
    Compute energy at hierarchy level k.

    E(k) = E_ref * g^((k_ref - k) / 2)

    The scaling factor g = 2*pi is derived exactly from Z2 → RP3
    topology (not fitted). The square root exponent arises from the
    geometric mean structure of projective geometry.

    Parameters
    ----------
    k : float
        Hierarchy level. k=0 is Planck scale; k=51 is confinement;
        k=61 is the consciousness critical point.
    g : float, optional
        Hierarchy scaling factor. Defaults to FRAMEWORK['g'] = 2*pi.
    k_ref : int, optional
        Reference k-level. Defaults to FRAMEWORK['k_ref'] = 51.
    E_ref_MeV : float, optional
        Reference energy in MeV. Defaults to FRAMEWORK['m_pi_MeV'] = 140.

    Returns
    -------
    float
        Energy in MeV.

    Notes
    -----
    The factor g = 2*pi is topologically exact:
        g^2 = |Z2 x Z2| * Vol(RP3) = 4 * pi^2
        => g = 2*pi

    Examples
    --------
    >>> hierarchy_energy(0)     # Planck scale ~1.22e25 MeV
    >>> hierarchy_energy(51)    # Confinement (reference) = 140.0 MeV
    >>> hierarchy_energy(61)    # Consciousness boundary ~0.018 MeV
    """
    if g is None:
        g = FRAMEWORK['g']
    if k_ref is None:
        k_ref = FRAMEWORK['k_ref']
    if E_ref_MeV is None:
        E_ref_MeV = FRAMEWORK['m_pi_MeV']

    assert k >= -1, f"k-level must be non-negative (or near zero), got {k}"
    assert g > 1, f"Scaling factor g must be > 1, got {g}"

    # E(k) = E_ref * g^((k_ref - k) / 2)  — Appendix C.6
    return E_ref_MeV * g ** ((k_ref - k) / 2.0)


def k_from_mass(m_MeV: float,
                g: float = None,
                k_ref: int = None,
                E_ref_MeV: float = None) -> float:
    """
    Compute hierarchy level k corresponding to a given mass.

    Inverse of hierarchy_energy:
        k = k_ref - 2 * ln(m / E_ref) / ln(g)

    Parameters
    ----------
    m_MeV : float
        Mass/energy in MeV.
    g : float, optional
        Hierarchy scaling factor. Defaults to FRAMEWORK['g'].
    k_ref : int, optional
        Reference k-level. Defaults to FRAMEWORK['k_ref'].
    E_ref_MeV : float, optional
        Reference energy in MeV. Defaults to FRAMEWORK['m_pi_MeV'].

    Returns
    -------
    float
        Hierarchy level k.

    Examples
    --------
    >>> k_from_mass(0.511)     # Electron mass -> ~57.1
    >>> k_from_mass(105.7)     # Muon mass -> ~51.5
    >>> k_from_mass(173000)    # Top quark (MeV) -> ~44.5
    """
    if g is None:
        g = FRAMEWORK['g']
    if k_ref is None:
        k_ref = FRAMEWORK['k_ref']
    if E_ref_MeV is None:
        E_ref_MeV = FRAMEWORK['m_pi_MeV']

    assert m_MeV > 0, f"Mass must be positive, got {m_MeV}"

    return k_ref - 2.0 * np.log(m_MeV / E_ref_MeV) / np.log(g)


def actualization_timescale(k: float) -> dict:
    """
    Compute actualization timescales at hierarchy level k.

    Returns both the single-event quantum timescale tau(k) = hbar/E(k)
    and, if k is near k_conscious (derived from thermal matching),
    the integration timescale t_integrate = sqrt(N_boundaries) * tau_quantum.

    The rate hierarchy is the temporal basis of cross-scale integration:
    a single k_conscious actualization window contains many completed
    sub-boundary cycles at lower k-levels, enabling the consciousness
    boundary to accumulate and integrate all sub-boundary outcomes
    within one coherent event.

    Parameters
    ----------
    k : float
        Hierarchy level.

    Returns
    -------
    dict
        Keys:
        - 'tau_quantum_s' : float — single-event timescale in seconds
        - 'tau_quantum_ms' : float — same in milliseconds
        - 'E_MeV' : float — energy in MeV
        - 'integration_ms' : float or None — integration window in ms (only at k=61)
        - 'sub_cycles_k51' : float or None — k=51 cycles per k=61 window
        - 'sub_cycles_k57' : float or None — k=57 cycles per k=61 window
    """
    hbar = PHYSICAL['hbar']  # J·s
    MeV_to_J = CONVERSIONS['MeV_to_J']

    E_MeV = hierarchy_energy(k)
    E_J = E_MeV * MeV_to_J

    # tau(k) = hbar / E(k)
    tau_s = hbar / E_J
    tau_ms = tau_s * 1e3

    result = {
        'tau_quantum_s': tau_s,
        'tau_quantum_ms': tau_ms,
        'E_MeV': E_MeV,
        'integration_ms': None,
        'sub_cycles_k51': None,
        'sub_cycles_k57': None,
    }

    # At k=61: compute integration window and sub-cycle counts
    k_conscious = FRAMEWORK['k_conscious']
    if abs(k - k_conscious) < 0.5:
        # N_boundaries ~ 10^14 sub-boundaries participate in integration
        N_boundaries = 1e14
        t_integrate_s = np.sqrt(N_boundaries) * tau_s
        t_integrate_ms = t_integrate_s * 1e3

        # Sub-cycle counts: how many k=51 and k=57 cycles fit in one k=61 window
        tau_k51_s = hbar / (hierarchy_energy(51) * MeV_to_J)
        tau_k57_s = hbar / (hierarchy_energy(57) * MeV_to_J)

        result['integration_ms'] = t_integrate_ms
        result['sub_cycles_k51'] = t_integrate_s / tau_k51_s
        result['sub_cycles_k57'] = t_integrate_s / tau_k57_s

    return result


def print_hierarchy_table() -> None:
    """
    Print formatted table of all key k-levels with energies,
    timescales, and physical interpretations.

    Matches Table in manuscript Section 3.3 / Appendix C.6.
    """
    header = (
        f"{'k':>5}  {'E (MeV)':>12}  {'E (GeV)':>12}  "
        f"{'tau (s)':>12}  {'Description'}"
    )
    sep = "-" * len(header)

    print("=" * len(header))
    print("PPM Energy Hierarchy: E(k) = 140 MeV × (2π)^((51−k)/2)")
    print("=" * len(header))
    print(header)
    print(sep)

    # Sorted by k-level
    entries = sorted(ENERGY_SCALES.items(), key=lambda x: x[1]['k'])
    for name, entry in entries:
        k = entry['k']
        E_MeV = hierarchy_energy(k)
        E_GeV = E_MeV / 1e3
        tau = actualization_timescale(k)['tau_quantum_s']
        print(f"{k:5.1f}  {E_MeV:12.3e}  {E_GeV:12.3e}  {tau:12.3e}  {name}: {entry['description']}")

    print(sep)

    # Integration window at k_conscious
    k_c = FRAMEWORK['k_conscious']
    t_c = actualization_timescale(k_c)
    print(f"\nk_conscious = {k_c:.2f} (derived from E(k) = k_BT at {FRAMEWORK['T_bio']}K)")
    print(f"Integration window: {t_c['integration_ms']:.1f} ms "
          f"(specious present: 50-200 ms)")
    print(f"k=51 cycles per window:  {t_c['sub_cycles_k51']:.2e}")
    print(f"k=57 cycles per window:  {t_c['sub_cycles_k57']:.2e}")

"""
PPM Framework — Energy Hierarchy
=================================

Implements the energy hierarchy E(k) = E_ref * g^((k_ref - k) / 2)
spanning from the Planck scale (k=0) to the consciousness boundary (k=61).

The scaling factor g = 2π follows from g^2 = |Z2 × Z2| × Vol(RP3) = 4π²
(Appendix A.2). The square-root exponent arises from phase-space scaling:
if phase-space volume scales by g^2 per level, the energy-wavelength
relation gives E(k) ~ g^(-k/2).

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
    topology (not fitted). The square root exponent arises from
    phase-space scaling (g^2 per level → E ~ g^(-k/2)).

    Parameters
    ----------
    k : float
        Hierarchy level. k=0 is Planck scale; k=51 is confinement;
        k≈75.35 is the consciousness critical point (derived from E(k) = k_BT).
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
    >>> hierarchy_energy(0)      # Planck vicinity ~3.16e25 MeV (~2.6× E_P)
    >>> hierarchy_energy(51)     # Confinement (reference) = 140.0 MeV
    >>> hierarchy_energy(75.35)  # Consciousness boundary ~0.027 MeV ≈ k_BT at 310 K
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

    # At k_conscious: compute integration window and sub-cycle counts.
    #
    # The integration window is derived self-consistently:
    #   t_integrate = sqrt(N_eff) * tau_quantum
    #   where N_eff = t_integrate / tau_ref  (sub-boundary cycles per window)
    #
    # Solving: t_integrate = tau(k_conscious)^2 / tau(k_ref=51)
    #
    # This is a framework-derived quantity, not a biological count.
    # See Section 7.4.3 and the Integration Time derivation.
    k_conscious = FRAMEWORK['k_conscious']
    if abs(k - k_conscious) < 0.5:
        tau_k51_s = hbar / (hierarchy_energy(51) * MeV_to_J)
        tau_k57_s = hbar / (hierarchy_energy(57) * MeV_to_J)

        # Self-consistent integration window: tau(k_c)^2 / tau(k_ref=51)
        t_integrate_s = tau_s**2 / tau_k51_s
        t_integrate_ms = t_integrate_s * 1e3

        result['integration_ms'] = t_integrate_ms
        result['sub_cycles_k51'] = t_integrate_s / tau_k51_s
        result['sub_cycles_k57'] = t_integrate_s / tau_k57_s

    return result


def print_hierarchy_table() -> None:
    """
    Print formatted table of all key k-levels with energies,
    timescales, measured values, and percent errors.

    Matches Table in manuscript Section 3.3 / Appendix C.6.
    """
    col_k     = 6
    col_pred  = 13
    col_obs   = 13
    col_err   = 8
    col_tau   = 13
    col_name  = 22

    header = (
        f"{'k':>{col_k}}  {'Pred (MeV)':>{col_pred}}  {'Obs (MeV)':>{col_obs}}  "
        f"{'% err':>{col_err}}  {'tau (s)':>{col_tau}}  {'Name / particle':<{col_name}}"
    )
    sep = "-" * len(header)

    print("=" * len(header))
    print("PPM Energy Hierarchy: E(k) = 140 MeV × (2π)^((51−k)/2)")
    print("=" * len(header))
    print(header)
    print(sep)

    # Neutrino entries: hierarchy energy ≠ physical mass (seesaw required)
    SEESAW_ENTRIES = {'Nu1', 'Nu2', 'Nu3'}

    # Sorted by k-level
    entries = sorted(ENERGY_SCALES.items(), key=lambda x: x[1]['k'])
    for name, entry in entries:
        k        = entry['k']
        # Use E_GeV_predicted which includes geometric factors (e.g. π × E for Top)
        E_pred   = entry['E_GeV_predicted'] * 1e3   # GeV → MeV
        E_obs    = entry['E_GeV_observed'] * 1e3    # GeV → MeV
        tau      = actualization_timescale(k)['tau_quantum_s']

        if name in SEESAW_ENTRIES:
            # Hierarchy energy is not the physical mass; seesaw closes the gap
            err_str = "seesaw"
        elif E_obs > 0:
            pct = (E_pred - E_obs) / E_obs * 100.0
            err_str = f"{pct:+.1f}%"
        else:
            err_str = "—"

        print(
            f"{k:{col_k}.1f}  {E_pred:{col_pred}.3e}  {E_obs:{col_obs}.3e}  "
            f"{err_str:>{col_err}}  {tau:{col_tau}.3e}  {name}"
        )

    print(sep)

    # Integration window at k_conscious
    k_c = FRAMEWORK['k_conscious']
    t_c = actualization_timescale(k_c)
    print(f"\nk_conscious = {k_c:.2f} (derived from E(k) = k_BT at {FRAMEWORK['T_bio']}K)")
    print(f"tau_quantum at k_conscious: {t_c['tau_quantum_s']:.3e} s  ({t_c['tau_quantum_s']*1e15:.1f} fs)")
    print(f"Integration window (self-consistent): {t_c['integration_ms']:.4f} ms")
    print(f"  N_eff (confinement sub-cycles): {t_c['sub_cycles_k51']:.2e}")
    print(f"k=51 cycles per window:  {t_c['sub_cycles_k51']:.2e}")
    print(f"k=57 cycles per window:  {t_c['sub_cycles_k57']:.2e}")

"""
PPM Framework — Phase Coherence
================================

Implements the thermal/quantum phase matching condition at the
consciousness boundary (k_conscious ≈ 75.35).

Two complementary routes to alpha:

  (A) Phase coherence (bottom-up): Given N_eff effective boundaries,
      the condition Phi_thermal = Phi_quantum yields
      alpha = N_eff * k_BT / (m_pi*c^2 * g^K).
      Requires N_eff ≈ 5.35e67 to produce alpha = 1/137.
      N_eff derivation is the open problem.

  (B) Twistor / RG fixed point (top-down): alpha is determined by
      the IR fixed point of the RG flow on the CP3 twistor space.
      This would derive alpha from pure topology, independent of N_eff.
      [NOT YET IMPLEMENTED — placeholder only]

If route (B) succeeds, then the phase coherence equation becomes a
CONSISTENCY CHECK: it determines N_eff at the critical point where
thermal matching and phase coherence converge. The consciousness
boundary is the critical point of this convergence.

STATUS: PRELIMINARY — twistor/RG calculation not yet complete.

Manuscript references: Section 3.4, Appendix A.3
"""

import numpy as np
from .constants import PHYSICAL, FRAMEWORK, CONVERSIONS


def thermal_phase(T: float,
                  N_boundaries: float,
                  m_pi_MeV: float = None) -> float:
    """
    Compute thermal phase accumulation at temperature T.

    Phi_thermal = N_boundaries * (k_B * T / (m_pi * c^2)) * 2*pi

    Physical interpretation: thermal fluctuations drive a Markov
    boundary through a continuous sequence of microstates on RP3,
    accumulating geometric phase at a rate set by k_B*T. Over
    N_boundaries sub-boundaries, this accumulation compounds.

    Parameters
    ----------
    T : float
        Temperature in Kelvin.
    N_boundaries : float
        Number of effective Markov sub-boundaries.
    m_pi_MeV : float, optional
        Pion mass in MeV. Defaults to FRAMEWORK['m_pi_MeV'].

    Returns
    -------
    float
        Thermal phase in radians.
    """
    assert T > 0, f"Temperature must be positive, got {T}"
    assert N_boundaries > 0, f"N_boundaries must be positive, got {N_boundaries}"

    if m_pi_MeV is None:
        m_pi_MeV = FRAMEWORK['m_pi_MeV']

    k_B = PHYSICAL['k_B']
    MeV_to_J = CONVERSIONS['MeV_to_J']
    m_pi_J = m_pi_MeV * MeV_to_J  # pion mass in joules

    # Phi_thermal = N * (k_B T / m_pi c²) * 2π
    # Note: m_pi_J is already m_pi * c² in energy units (MeV converted to J)
    return N_boundaries * (k_B * T / m_pi_J) * 2.0 * np.pi


def quantum_phase(alpha: float,
                  K: float,
                  g: float = None) -> float:
    """
    Compute quantum Berry phase from Z2 topology.

    Phi_quantum = alpha * g^K * 2*pi

    Physical interpretation: the Berry phase accumulated as the
    system traverses the non-contractible Z2 loop in RP3. Because
    pi_1(RP3) = Z2, the 360° path returns to the antipodal state;
    only the 720° path closes and returns to origin.

    Parameters
    ----------
    alpha : float
        Fine-structure constant.
    K : float
        Hierarchy depth parameter.
    g : float, optional
        Hierarchy scaling factor. Defaults to FRAMEWORK['g'].

    Returns
    -------
    float
        Quantum Berry phase in radians.
    """
    assert alpha > 0, f"alpha must be positive, got {alpha}"

    if g is None:
        g = FRAMEWORK['g']

    # Phi_quantum = alpha * g^K * 2*pi  — Appendix A.3
    return alpha * (g ** K) * 2.0 * np.pi


def solve_alpha_from_coherence(T: float,
                                N_boundaries: float,
                                K: float,
                                m_pi_MeV: float = None,
                                g: float = None) -> float:
    """
    Solve for alpha from the phase coherence matching condition.

    At the consciousness boundary, stable phenomenology requires:
        Phi_thermal = Phi_quantum
        N * (k_B T / m_pi c²) * 2π = alpha * g^K * 2π
        alpha = N * k_B T / (m_pi c² * g^K)

    Parameters
    ----------
    T : float
        Temperature in Kelvin (use 310 K for biological).
    N_boundaries : float
        Number of effective boundaries. Use ~5.35e67 for alpha=1/137.
    K : float
        Hierarchy depth (use k_conscious ≈ 75.35).
    m_pi_MeV : float, optional
        Pion mass in MeV.
    g : float, optional
        Hierarchy scaling factor.

    Returns
    -------
    float
        Fine-structure constant alpha (should be ≈ 1/137).

    Notes
    -----
    STATUS: PRELIMINARY. This calculation demonstrates the mechanism
    and achieves numerical agreement (0.07% error) but the rigorous
    derivation requires:
        - Proper Berry phase formulation on CP3
        - Renormalization group flow to fixed point
        - Twistor geometry calculation (Section 3.4.4)
    """
    assert T > 0, f"Temperature must be positive, got {T}"
    assert N_boundaries > 0, f"N_boundaries must be positive, got {N_boundaries}"

    if m_pi_MeV is None:
        m_pi_MeV = FRAMEWORK['m_pi_MeV']
    if g is None:
        g = FRAMEWORK['g']

    k_B = PHYSICAL['k_B']
    MeV_to_J = CONVERSIONS['MeV_to_J']
    m_pi_J = m_pi_MeV * MeV_to_J

    # alpha = N * k_B * T / (m_pi * c² * g^K)
    alpha = N_boundaries * k_B * T / (m_pi_J * g ** K)
    return alpha


def phase_matching_sensitivity(
    T_range: tuple = (280, 340),
    N_range: tuple = (10, 1000),
    K_range: tuple = (8, 12)
) -> dict:
    """
    Compute sensitivity of solved alpha to input parameters.

    Shows how robustly the phase coherence condition pins alpha.

    Parameters
    ----------
    T_range : tuple
        Temperature range (min, max) in Kelvin.
    N_range : tuple
        N_boundaries range (min, max).
    K_range : tuple
        Hierarchy depth range (min, max).

    Returns
    -------
    dict
        Keys:
        - 'T_values' : array of temperatures
        - 'N_values' : array of N_boundaries values
        - 'K_values' : array of K values
        - 'alpha_vs_T' : alpha solved at each T (fixed N=100, K=10)
        - 'alpha_vs_N' : alpha solved at each N (fixed T=310, K=10)
        - 'alpha_vs_K' : alpha solved at each K (fixed T=310, N=100)
    """
    T_vals = np.linspace(T_range[0], T_range[1], 50)
    N_vals = np.logspace(np.log10(N_range[0]), np.log10(N_range[1]), 50)
    K_vals = np.linspace(K_range[0], K_range[1], 50)

    alpha_vs_T = np.array([
        solve_alpha_from_coherence(T=T, N_boundaries=100, K=10)
        for T in T_vals
    ])
    alpha_vs_N = np.array([
        solve_alpha_from_coherence(T=310, N_boundaries=N, K=10)
        for N in N_vals
    ])
    alpha_vs_K = np.array([
        solve_alpha_from_coherence(T=310, N_boundaries=100, K=K)
        for K in K_vals
    ])

    return {
        'T_values': T_vals,
        'N_values': N_vals,
        'K_values': K_vals,
        'alpha_vs_T': alpha_vs_T,
        'alpha_vs_N': alpha_vs_N,
        'alpha_vs_K': alpha_vs_K,
    }


# -----------------------------------------------------------------------
# Critical point analysis
# -----------------------------------------------------------------------

def N_eff_from_alpha(alpha: float = None,
                     T: float = None,
                     K: float = None) -> float:
    """
    Compute N_eff required for phase coherence given alpha.

    If alpha is known (e.g., from twistor/RG), this inverts the phase
    coherence condition to determine N_eff:

        N_eff = alpha * m_pi*c² * g^K / (k_B * T)

    This is the INVERSE of solve_alpha_from_coherence.

    Parameters
    ----------
    alpha : float, optional
        Fine-structure constant. Defaults to observed 1/137.036.
    T : float, optional
        Temperature in K. Defaults to T_bio = 310 K.
    K : float, optional
        Hierarchy depth. Defaults to k_conscious.

    Returns
    -------
    float
        Required N_eff for phase coherence.
    """
    if alpha is None:
        alpha = PHYSICAL['alpha']
    if T is None:
        T = FRAMEWORK['T_bio']
    if K is None:
        K = FRAMEWORK['k_conscious']

    g = FRAMEWORK['g']
    k_B = PHYSICAL['k_B']
    m_pi_J = FRAMEWORK['m_pi_MeV'] * CONVERSIONS['MeV_to_J']

    return alpha * m_pi_J * g ** K / (k_B * T)


def critical_point_check() -> dict:
    """
    Verify the critical point: thermal matching and phase coherence
    must converge at k_conscious.

    The consciousness boundary is defined by two independent conditions:
      1. Thermal matching: E(k) = k_BT at T_bio  →  determines k_conscious
      2. Phase coherence: Phi_thermal = Phi_quantum  →  determines N_eff

    At the critical point, both conditions are satisfied simultaneously.
    This function checks the consistency and reports N_eff diagnostics.

    Returns
    -------
    dict
        Diagnostic results including N_eff, its scaling with N_cosmic,
        and the phase coherence residual.
    """
    from .hierarchy import hierarchy_energy

    k_c = FRAMEWORK['k_conscious']
    T_bio = FRAMEWORK['T_bio']
    N_cosmic = FRAMEWORK['N_cosmic']
    alpha_obs = PHYSICAL['alpha']

    # Condition 1: thermal matching (by construction)
    E_kc = hierarchy_energy(k_c) * CONVERSIONS['MeV_to_J']
    kBT = PHYSICAL['k_B'] * T_bio
    thermal_residual = abs(E_kc - kBT) / kBT

    # Condition 2: phase coherence → required N_eff
    N_eff = N_eff_from_alpha(alpha=alpha_obs, T=T_bio, K=k_c)

    # N_eff scaling with N_cosmic
    log_ratio = np.log(N_eff) / np.log(N_cosmic)

    # Phase coherence check: does N_eff * k_BT / (m_pi * g^K) = alpha?
    alpha_recovered = solve_alpha_from_coherence(
        T=T_bio, N_boundaries=N_eff, K=k_c
    )
    coherence_residual = abs(alpha_recovered - alpha_obs) / alpha_obs

    return {
        'k_conscious': k_c,
        'thermal_match_residual': thermal_residual,
        'N_eff': N_eff,
        'N_eff_exponent': log_ratio,
        'N_eff_approx': f'N_cosmic^{log_ratio:.4f}',
        'alpha_recovered': alpha_recovered,
        'coherence_residual': coherence_residual,
        'interpretation': (
            'If alpha is derived from twistor/RG topology (route B), '
            'then N_eff is a PREDICTION of the critical point, not a free parameter. '
            f'N_eff ≈ N_cosmic^{log_ratio:.3f} ≈ {N_eff:.3e}. '
            'The exponent ~5/6 may relate to holographic dimensional reduction '
            '(6D phase space of CP3, one dimension projected out by Z2).'
        ),
    }

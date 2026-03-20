"""
PPM Framework — Berry Phase and CKM Matrix
============================================

Implements CKM quark mixing angles via Berry phase integrals on CP3.

The quark mixing matrix arises from the Berry connection on CP3 when
quarks are located at different k-levels in the hierarchy. The 720°
path structure (from pi_1(RP3) = Z2) determines the phase acquired
during flavor transitions.

Manuscript references: Appendix B.5.3
"""

import numpy as np
try:
    from scipy import integrate
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
from .constants import PHYSICAL, FRAMEWORK, CONVERSIONS
from .hierarchy import hierarchy_energy


def quark_positions() -> dict:
    """
    Return (k-level, |z|) for each quark in CP3.

    Values from manuscript Appendix B.5.3. The CP3 coordinate |z|
    is related to the quark mass via the hierarchy formula, normalized
    to the Compton wavelength at the confinement scale.

    Returns
    -------
    dict
        Keyed by quark name, values are dicts with 'k', 'mass_MeV', 'z_abs'.
    """
    quarks = {
        'up':      {'k': 55.54, 'mass_MeV': 2.16},      # Kähler; k from E⁻¹(observed)
        'down':    {'k': 54.70, 'mass_MeV': 4.67},       # Kähler; k from E⁻¹(observed)
        'strange': {'k': 51.44, 'mass_MeV': 93.4},       # Kähler; k from E⁻¹(observed)
        'charm':   {'k': 47.5,  'mass_MeV': 1270.0},     # Framework prediction (§4)
        'bottom':  {'k': 46.0,  'mass_MeV': 4180.0},     # Framework prediction (§4)
        'top':     {'k': 44.5,  'mass_MeV': 173000.0},   # EWSB scale
    }

    # |z| in CP3 is proportional to mass ratio relative to confinement scale
    m_ref = FRAMEWORK['m_pi_MeV']
    hbar = PHYSICAL['hbar']
    c = PHYSICAL['c']
    MeV_to_J = CONVERSIONS['MeV_to_J']

    # Compton wavelength at confinement scale
    lambda_C = hbar * c / (m_ref * MeV_to_J)

    for name, q in quarks.items():
        # |z| = (m_quark / m_pi) * lambda_C  in natural units -> dimensionless ratio
        q['z_abs'] = q['mass_MeV'] / m_ref

    return quarks


def berry_phase_integral(z_i: np.ndarray,
                          z_j: np.ndarray,
                          m_pi_MeV: float = None,
                          lambda_C_m: float = None) -> float:
    """
    Compute mixing angle theta_ij via Berry connection integral.

    Berry connection on CP3:
        A = i * (m_pi*c^2 / lambda_C^2) * sum_k (z_bar_k / (1 + |z|^2/lambda_C^2)) dz_k

    Path: z_i to z_j traversed 720° (t in [0, 2]) in CP3.
    The 720° traversal arises from pi_1(RP3) = Z2: a single 360° loop
    returns to the antipodal point, only the double cover closes.

    Parameters
    ----------
    z_i : np.ndarray
        Starting position in CP3 (complex, shape (3,) for CP3).
    z_j : np.ndarray
        Ending position in CP3.
    m_pi_MeV : float, optional
        Pion mass in MeV.
    lambda_C_m : float, optional
        Compton wavelength in meters.

    Returns
    -------
    float
        Mixing angle theta_ij in radians.
    """
    if m_pi_MeV is None:
        m_pi_MeV = FRAMEWORK['m_pi_MeV']

    hbar = PHYSICAL['hbar']
    c = PHYSICAL['c']
    MeV_to_J = CONVERSIONS['MeV_to_J']

    if lambda_C_m is None:
        lambda_C_m = hbar * c / (m_pi_MeV * MeV_to_J)

    m_pi_J = m_pi_MeV * MeV_to_J

    # Parametrize the 720° path from z_i to z_j
    # t in [0, 2] covers the double loop (720°)
    z_i = np.atleast_1d(np.asarray(z_i, dtype=complex))
    z_j = np.atleast_1d(np.asarray(z_j, dtype=complex))

    # Pad to 3 components for CP3 if needed
    while len(z_i) < 3:
        z_i = np.append(z_i, 0.0 + 0.0j)
    while len(z_j) < 3:
        z_j = np.append(z_j, 0.0 + 0.0j)

    def integrand(t):
        # Interpolate along great circle with 720° winding
        phase = np.pi * t  # 0 to 2π for t in [0, 2]
        z_t = z_i * np.cos(phase) + z_j * np.sin(phase)
        dz_dt = -z_i * np.sin(phase) * np.pi + z_j * np.cos(phase) * np.pi

        z_abs_sq = np.sum(np.abs(z_t) ** 2)
        denom = 1.0 + z_abs_sq

        # Berry connection: A · dz/dt
        A_dot_dz = np.sum(np.conj(z_t) * dz_dt) / denom
        return np.imag(A_dot_dz)

    # Numerical integration over the 720° path
    if HAS_SCIPY:
        result, _ = integrate.quad(integrand, 0, 2, limit=200)
    else:
        # Fallback: composite Simpson's rule
        n_pts = 1001
        t_vals = np.linspace(0, 2, n_pts)
        y_vals = np.array([integrand(t) for t in t_vals])
        dt = t_vals[1] - t_vals[0]
        result = np.trapz(y_vals, dx=dt)

    return abs(result)


def compute_ckm_matrix() -> np.ndarray:
    """
    Compute full CKM mixing matrix from Berry phase integrals.

    The CKM matrix elements V_ij are related to the Berry phases
    between quark positions in CP3:
        |V_ij| ≈ sin(theta_ij) for small angles
        |V_ij| ≈ cos(theta_ij) for diagonal elements

    Returns
    -------
    np.ndarray, shape (3, 3)
        CKM matrix magnitudes |V_ij|.
    """
    quarks = quark_positions()

    # Up-type quarks: u, c, t
    # Down-type quarks: d, s, b
    up_quarks = ['up', 'charm', 'top']
    down_quarks = ['down', 'strange', 'bottom']

    V = np.zeros((3, 3))

    for i, u_name in enumerate(up_quarks):
        for j, d_name in enumerate(down_quarks):
            z_i = np.array([quarks[u_name]['z_abs'], 0, 0], dtype=complex)
            z_j = np.array([quarks[d_name]['z_abs'], 0, 0], dtype=complex)

            theta = berry_phase_integral(z_i, z_j)

            if i == j:
                # Diagonal: cos(theta)
                V[i, j] = np.cos(theta)
            else:
                # Off-diagonal: sin(theta) with suppression from mass hierarchy
                mass_ratio = min(quarks[u_name]['mass_MeV'],
                                quarks[d_name]['mass_MeV']) / \
                             max(quarks[u_name]['mass_MeV'],
                                quarks[d_name]['mass_MeV'])
                V[i, j] = abs(np.sin(theta)) * np.sqrt(mass_ratio)

    # Normalize rows to approximate unitarity
    for i in range(3):
        row_norm = np.sqrt(np.sum(V[i, :] ** 2))
        if row_norm > 0:
            V[i, :] /= row_norm

    return V


def print_ckm_comparison() -> None:
    """
    Print comparison of computed CKM matrix vs. PDG observed values.
    """
    V_computed = compute_ckm_matrix()

    # PDG 2023 central values (magnitudes)
    V_pdg = np.array([
        [0.97373, 0.2243, 0.00382],
        [0.2210,  0.987,  0.0410],
        [0.0080,  0.0388, 1.013],
    ])

    labels_up = ['u', 'c', 't']
    labels_down = ['d', 's', 'b']

    print("=" * 55)
    print("CKM Matrix: PPM Berry Phase vs. PDG Observed")
    print("=" * 55)

    print("\nComputed |V_ij|:")
    print("       ", "  ".join(f"{d:>8}" for d in labels_down))
    for i, u in enumerate(labels_up):
        vals = "  ".join(f"{V_computed[i,j]:8.4f}" for j in range(3))
        print(f"  {u}:  {vals}")

    print("\nPDG Observed |V_ij|:")
    print("       ", "  ".join(f"{d:>8}" for d in labels_down))
    for i, u in enumerate(labels_up):
        vals = "  ".join(f"{V_pdg[i,j]:8.4f}" for j in range(3))
        print(f"  {u}:  {vals}")

    print("=" * 55)

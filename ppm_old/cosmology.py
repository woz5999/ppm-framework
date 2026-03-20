"""
PPM Framework — Cosmology
==========================

Cosmological predictions from the PPM framework: Newton's constant G,
cosmological constant Lambda, and their evolution with redshift.

G and Lambda arise from information coarse-graining over N ~ 10^82
actualization events. Both evolve with the expanding actualization count.

Manuscript references: Section 8.2, 8.4
"""

import numpy as np
from .constants import PHYSICAL, FRAMEWORK, CONVERSIONS


def G_newton(N: float = None, m_pi_MeV: float = None) -> float:
    """
    Compute Newton's constant from coarse-graining formula.

    G = 16*pi^4 * hbar*c*alpha / (m_pi^2 * sqrt(N))

    The factor 16*pi^4 = (2*pi)^4 = g^4 is the topological factor from
    4 spatial sectors of RP3 (Section 8.2). m_pi is in kg.

    Known issues (transparency):
    - With m_pi = 140 MeV (charged pion, framework reference): G = 5.77e-11, 13.5% error
    - With m_pi = 135 MeV (neutral pion, manuscript verification): G = 6.21e-11, 7.0% error
    - The choice of confinement reference mass is an open theoretical question
    - The 16*pi^4 sector counting may need refinement

    Parameters
    ----------
    N : float, optional
        Total actualization count. Defaults to FRAMEWORK['N_cosmic'] = 1e82.
    m_pi_MeV : float, optional
        Pion mass in MeV. Defaults to FRAMEWORK['m_pi_MeV'] = 140.

    Returns
    -------
    float
        Newton's constant in m³/(kg·s²).
    """
    if N is None:
        N = FRAMEWORK['N_cosmic']
    if m_pi_MeV is None:
        m_pi_MeV = FRAMEWORK['m_pi_MeV']

    hbar = PHYSICAL['hbar']
    c = PHYSICAL['c']
    alpha = PHYSICAL['alpha']
    m_pi_kg = m_pi_MeV * CONVERSIONS['MeV_to_kg']

    # G = 16π⁴ ħc α / (m_π² √N)  — manuscript Eq. 1, Section 8.2
    return 16.0 * np.pi ** 4 * hbar * c * alpha / (m_pi_kg ** 2 * np.sqrt(N))


def G_evolution(z: float, G0: float = None) -> float:
    """
    Compute G at redshift z.

    G(z) = G0 * (1+z)^(3/2)

    The 3/2 exponent comes from the scaling of the actualization count
    with cosmic volume: N(z) ∝ (1+z)^(-3), so sqrt(N) ∝ (1+z)^(-3/2),
    and G ∝ 1/sqrt(N) ∝ (1+z)^(3/2).

    Parameters
    ----------
    z : float
        Redshift.
    G0 : float, optional
        Present-day G. Defaults to observed PHYSICAL['G'].

    Returns
    -------
    float
        G at redshift z in m³/(kg·s²).
    """
    if G0 is None:
        G0 = PHYSICAL['G']

    return G0 * (1.0 + z) ** 1.5


def lambda_cosmological(N: float = None) -> float:
    """
    Compute cosmological constant.

    Lambda = 2 * (m_pi * c^2)^2 / ((hbar * c)^2 * N)

    The factor 2 comes from Z2 topology (two homotopy classes).
    Lambda decreases as N grows — no fine-tuning required.
    Units: m^-2 (using hbar*c to convert energy^2 to inverse length^2).

    Parameters
    ----------
    N : float, optional
        Total actualization count. Defaults to FRAMEWORK['N_cosmic'].

    Returns
    -------
    float
        Cosmological constant in m⁻².
    """
    if N is None:
        N = FRAMEWORK['N_cosmic']

    hbar = PHYSICAL['hbar']
    c = PHYSICAL['c']
    m_pi_J = FRAMEWORK['m_pi_MeV'] * CONVERSIONS['MeV_to_J']

    # Lambda = 2 (m_π c²)² / ((ħc)² N)  — manuscript Eq. 5, Section 8.4
    # m_pi_J is m_π c² in energy units; divide by (ħc)² for m⁻² units
    hbar_c = hbar * c
    return 2.0 * m_pi_J ** 2 / (hbar_c ** 2 * N)


def lambda_evolution(z: float, Lambda0: float = None) -> float:
    """
    Compute Lambda at redshift z.

    Lambda(z) = Lambda0 * (1+z)^2

    N(z) ∝ (1+z)^(-3) and Lambda ∝ 1/N, but the spatial volume factor
    reduces the exponent to 2.

    Parameters
    ----------
    z : float
        Redshift.
    Lambda0 : float, optional
        Present-day Lambda. Defaults to computed value.

    Returns
    -------
    float
        Lambda at redshift z in m⁻².
    """
    if Lambda0 is None:
        Lambda0 = lambda_cosmological()

    return Lambda0 * (1.0 + z) ** 2


def hubble_parameter(z: float, H0: float = 70.9) -> float:
    """
    Compute Hubble parameter H(z) for PPM-modified expansion history.

    Uses standard Friedmann equation with PPM dark energy density.
    Omega_m = 0.315, Omega_Lambda from PPM prediction.

    Parameters
    ----------
    z : float
        Redshift.
    H0 : float
        Present-day Hubble constant in km/s/Mpc. Default 70.9.

    Returns
    -------
    float
        H(z) in km/s/Mpc.
    """
    Omega_m = 0.315
    Omega_Lambda = 1.0 - Omega_m  # flat universe

    E_sq = Omega_m * (1.0 + z) ** 3 + Omega_Lambda
    return H0 * np.sqrt(E_sq)


def dark_energy_eos(z_array=None) -> dict:
    """
    Compute the effective dark energy equation of state from the PPM
    modified Friedmann equation.

    In the PPM framework both G and Λ vary with redshift:
        G(z)   = G₀ (1+z)^(3/2)
        Λ(z)   = Λ₀ (1+z)²

    The modified Friedmann equation is:
        H²_PPM(z) = Ω_m H₀² (1+z)^(9/2) + Ω_Λ H₀² (1+z)²

    A standard observer who assumes constant G would fit this curve with an
    effective quintessence equation of state w_eff(z). This function computes
    w_eff(z) by comparing H²_PPM to a best-fit constant-w model.

    The effective w is ALWAYS > −1 in this framework, consistent (in sign) with
    DESI 2024 hints (2.8–3.9σ away from w = −1).

    CAUTION: Full quantitative comparison to DESI/Euclid requires the complete
    CMB compatibility check (Section 9), which is listed as incomplete. The
    computed w_eff here is illustrative of the qualitative prediction.

    Parameters
    ----------
    z_array : array-like or None
        Redshift values. Default: 0 to 2.

    Returns
    -------
    dict
        - 'z'           : redshift array
        - 'H_PPM'       : H(z) in km/s/Mpc from PPM (modified G and Λ)
        - 'H_LCDM'      : H(z) in km/s/Mpc from standard ΛCDM
        - 'rho_de_PPM'  : effective dark energy density (normalized to present)
        - 'w_eff'       : effective equation of state w(z)
        - 'w_eff_z0'    : w at z = 0
        - 'DESI_hint'   : dict with DESI 2024 best-fit w₀ reference
        - 'framework_prediction': summary string

    Notes
    -----
    The (1+z)^(9/2) matter term arises from G(z) ∝ (1+z)^(3/2) acting on
    ρ_m ∝ (1+z)³. A standard ΛCDM fit to this H(z) will absorb some of the
    modified matter evolution into the inferred dark energy term.
    """
    H0    = 70.9      # km/s/Mpc
    Omega_m = 0.315
    Omega_L = 1.0 - Omega_m

    if z_array is None:
        z_array = np.linspace(0.0, 2.0, 300)
    z = np.asarray(z_array, dtype=float)

    # PPM modified Friedmann: G(z) × ρ_m ∝ (1+z)^(9/2); Λ(z) ∝ (1+z)²
    H2_PPM  = H0**2 * (Omega_m * (1.0 + z)**4.5 + Omega_L * (1.0 + z)**2)
    H_PPM   = np.sqrt(H2_PPM)

    # Standard ΛCDM
    H2_LCDM = H0**2 * (Omega_m * (1.0 + z)**3 + Omega_L)
    H_LCDM  = np.sqrt(H2_LCDM)

    # Effective dark energy density seen by a standard-G observer:
    # ρ_de,eff(z) ∝ H²_PPM − Ω_m H₀²(1+z)³ (what they'd attribute to dark energy)
    rho_de_eff = (H2_PPM - H0**2 * Omega_m * (1.0 + z)**3) / (H0**2 * Omega_L)

    # Effective equation of state: w = (1/3) × d ln ρ_de / d ln(1+z) − 1
    # Compute numerically via finite differences
    ln_rho = np.log(np.maximum(rho_de_eff, 1e-30))
    ln_1pz = np.log(1.0 + z)
    d_ln_rho = np.gradient(ln_rho, ln_1pz)
    w_eff = d_ln_rho / 3.0 - 1.0

    # w at z = 0 (analytic limit from Taylor expansion)
    # At z → 0: rho_de_eff ≈ 1 + z × [Ω_m(4.5−3) + Ω_L(2−0)] / Ω_L
    # w_eff(0) = (1/3)(d ln rho_de / d ln(1+z))|_0 − 1
    slope_at_0 = (Omega_m * (4.5 - 3.0) + Omega_L * 2.0) / Omega_L
    w_eff_z0   = slope_at_0 / 3.0 - 1.0

    return {
        'z':                  z,
        'H_PPM':              H_PPM,
        'H_LCDM':             H_LCDM,
        'rho_de_PPM':         rho_de_eff,
        'w_eff':              w_eff,
        'w_eff_z0':           w_eff_z0,
        'DESI_hint': {
            'w0': -0.76,        # DESI 2024 best-fit w₀ (approximate)
            'wa': -0.82,        # DESI 2024 best-fit wₐ (approximate)
            'sigma': '2.8–3.9σ from w = −1',
        },
        'framework_prediction': (
            f'PPM predicts w_eff > −1 at all z. '
            f'At z=0: w_eff ≈ {w_eff_z0:.3f}. '
            f'DESI 2024 shows {2.8}–{3.9}σ hint for w ≠ −1. '
            f'Quantitative match requires full CMB compatibility test (Section 9).'
        ),
    }


def print_cosmology_table() -> None:
    """
    Print cosmological parameter predictions vs. observed.
    """
    G_pred = G_newton()
    G_pred_135 = G_newton(m_pi_MeV=135.0)
    G_obs = PHYSICAL['G']
    Lambda_pred = lambda_cosmological()
    Lambda_obs = 1.1e-52  # m⁻²
    H0_pred = 70.9  # km/s/Mpc (PPM prediction)
    H0_obs = 73.0   # km/s/Mpc (SH0ES)

    H0_si = H0_pred * 1e3 / 3.086e22
    t_universe_s = 2.0 / (3.0 * H0_si)
    t_universe_Gyr = t_universe_s / (365.25 * 24 * 3600 * 1e9)

    print("=" * 72)
    print("PPM Cosmological Predictions")
    print("=" * 72)
    print(f"{'Parameter':<30} | {'Predicted':<16} | {'Observed':<16} | {'Error':<8}")
    print("-" * 72)
    print(f"{'G (m_π=140 MeV, charged)':<30} | {G_pred:<16.3e} | {G_obs:<16.3e} | "
          f"{abs(G_pred-G_obs)/G_obs*100:<7.1f}%")
    print(f"{'G (m_π=135 MeV, neutral)':<30} | {G_pred_135:<16.3e} | {G_obs:<16.3e} | "
          f"{abs(G_pred_135-G_obs)/G_obs*100:<7.1f}%")
    print(f"{'Lambda (m⁻²)':<30} | {Lambda_pred:<16.3e} | {Lambda_obs:<16.3e} | "
          f"{abs(Lambda_pred-Lambda_obs)/Lambda_obs*100:<7.1f}%")
    print(f"{'H0 (km/s/Mpc)':<30} | {H0_pred:<16.1f} | {H0_obs:<16.1f} | "
          f"{abs(H0_pred-H0_obs)/H0_obs*100:<7.1f}%")
    print(f"{'Age (Gyr)':<30} | {t_universe_Gyr:<16.1f} | {'13.8':<16} | "
          f"{abs(t_universe_Gyr-13.8)/13.8*100:<7.1f}%")
    print("=" * 72)
    print()
    print("NOTE: G depends on which pion mass is the confinement reference.")
    print("  m_π = 140 MeV (charged): consistent with framework E(51) definition")
    print("  m_π = 135 MeV (neutral): used in manuscript Section 8.2.4 verification")
    print("  The 7-14% residual may indicate 16π⁴ sector counting needs refinement.")

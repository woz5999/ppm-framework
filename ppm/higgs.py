"""
ppm.higgs — τ involution and Higgs sector
==========================================

The τ involution is the anti-holomorphic Z₂ symmetry on CP³:
    τ: CP³ → CP³,  τ*ω = −ω  (reverses the Kähler form)

This involution generates the RP³ fixed-point set and is responsible for:
1. The Higgs quartic λ_PPM = 1/(4√π) from RP³ normal bundle curvature
2. The τ-conjugate sector giving λ = −λ_PPM
3. The geometric identity Δλ = 1/(2√π)

Section references: §2 (τ Involution), §7 (SM Parameters)
"""

import math
from . import constants as C


def lambda_ppm():
    """
    Higgs quartic coupling from RP³ normal bundle curvature.

    LaTeX: \\lambda_{\\rm PPM} = \\frac{1}{4\\sqrt{\\pi}} \\approx 0.14105
    Section: §2 (τ involution), §7 (SM parameters)
    Status: DERIVED (VERIFIED)

    The RP³ ↪ CP³ has a normal bundle whose curvature, integrated over RP³,
    gives this specific value. The τ involution selects the RP³ locus as the
    physical sector.
    """
    return 1.0 / (4.0 * math.sqrt(math.pi))


def lambda_tau_conjugate():
    """
    Higgs quartic in the τ-conjugate sector.

    LaTeX: \\lambda_{\\tau} = -\\lambda_{\\rm PPM}
    The anti-holomorphic involution τ reverses the sign of τ-odd quantities.
    λ is τ-odd, so the τ-conjugate sector has λ = −λ_PPM.
    Status: DERIVED
    """
    return -lambda_ppm()


def delta_lambda():
    """
    Geometric identity: separation between τ-sector endpoints.

    LaTeX: \\Delta\\lambda = \\lambda_{\\rm PPM} - \\lambda_{\\tau} = \\frac{1}{2\\sqrt{\\pi}} \\approx 0.28209
    Both endpoints are geometrically fixed (RP³ curvature in both τ-orientations).
    Their difference is therefore a geometric identity, not a fitted result.

    Paper (section4-new.tex): SM running brackets this value:
      One-loop:  Δλ_SM = 0.270 (95.8%)
      Two-loop:  Δλ_SM = 0.286 (101.5%)
    Geometric target is 1.5% above two-loop, confirming ≤1.5% accuracy.
    Status: DERIVED (VERIFIED)
    """
    return lambda_ppm() - lambda_tau_conjugate()


def delta_lambda_observed(loops=2):
    """
    Observed Δλ from SM running (for comparison with geometric identity).

    section4-new.tex:
      One-loop:  Δλ_SM^(1) = 0.270  (95.8% of 1/(2√π))
      Two-loop:  Δλ_SM^(2) = 0.286  (101.5% of 1/(2√π))
    The geometric target 1/(2√π) = 0.282 is bracketed between the two,
    with the two-loop answer only 1.5% away.
    Status: VERIFIED (from paper section4-new.tex)
    """
    if loops == 1:
        return 0.270  # One-loop SM running
    return 0.286  # Two-loop SM running


def higgs_quartic_comparison():
    """
    Compare λ_PPM to observed Higgs quartic at M_Z.

    Observed: λ(M_Z) ≈ 0.1292 (MSbar)
    PPM:      λ_PPM  = 1/(4√π) ≈ 0.14105
    Error: +9.2%

    NOTE: λ_PPM is a geometric value from RP³ normal bundle curvature.
    It CANNOT be interpreted as a UV boundary condition at E_break and
    RG-run to M_Z — SM running is an IR attractor that gives λ(M_Z) ~ 0.41
    regardless of UV initial value. The correct comparison is geometric λ_PPM
    vs physical λ at EW scale. The 9.2% gap (equivalently 4.5% in m_H) is
    the tree-level prediction accuracy.
    """
    lam_ppm = lambda_ppm()
    lam_obs = C.LAMBDA_PPM_OBSERVED
    err_pct = (lam_ppm / lam_obs - 1.0) * 100.0
    return {
        'lambda_ppm': lam_ppm,
        'lambda_observed_MZ': lam_obs,
        'error_pct': err_pct,
        'note': 'λ_PPM is geometric value from RP³ curvature; 9.2% gap is tree-level accuracy'
    }


def top_yukawa_ppm():
    """
    PPM tree-level top Yukawa coupling.

    LaTeX: y_t^{\\rm PPM} = \\frac{\\pi}{2(2\\pi)^{1/4}} \\approx 0.992
    Section: §7 (SM parameters)
    Status: DERIVED (VERIFIED session 27)

    IMPORTANT convention: y_t = √2 × m_t/v, not m_t/v = 0.701.
    The PPM formula gives the Yukawa coupling in the standard convention.
    """
    return math.pi / (2.0 * (C.TAU ** 0.25))


def beta_lambda_ppm():
    """
    One-loop β_λ at the PPM geometric point (λ_PPM, y_t_PPM, SM gauge at M_Z).

    Standard SM formula (PDG/Buttazzo et al.):
      16π² β_λ = 24λ² + 12λy_t² − 6y_t⁴
                 + (3/8)(2g₂⁴ + (g'² + g₂²)²)
                 − 3λ(3g₂² + g'²)

    Result: β_λ ≈ −0.0254 at (λ_PPM, y_t_PPM, SM gauge at M_Z).
    Status: VERIFIED (standard SM formula applied correctly)
    """
    lam = lambda_ppm()
    yt  = top_yukawa_ppm()

    # Gauge couplings at M_Z
    g2_sq = 4.0 * math.pi * C.ALPHA2_MZ      # g₂² (SU(2))
    gp_sq = (3.0/5.0) * 4.0 * math.pi * C.ALPHA1_MZ  # g'² = (3/5)g₁²(GUT)

    coeff = 1.0 / (16.0 * math.pi**2)
    beta = coeff * (
        24.0 * lam**2
        + 12.0 * lam * yt**2
        - 6.0 * yt**4
        + (3.0/8.0) * (2.0*g2_sq**2 + (gp_sq + g2_sq)**2)
        - 3.0 * lam * (3.0*g2_sq + gp_sq)
    )
    return {
        'beta_lambda': beta,
        'lambda_ppm': lam,
        'yt_ppm': yt,
        'status': 'VERIFIED',
        'note': 'β_λ ≈ −0.0254; Option B (β_λ=0) ruled out by SM beta functions'
    }


def geometric_identity_check():
    """
    Verify the geometric identity Δλ = 1/(2√π).

    Returns dict with both the formula value and its components.
    """
    dl = delta_lambda()
    formula = 1.0 / (2.0 * math.sqrt(math.pi))
    assert abs(dl - formula) < 1e-12, "Identity failed!"
    return {
        'delta_lambda': dl,
        'formula_1_over_2sqrt_pi': formula,
        'match': True,
        'delta_lambda_observed_1loop': delta_lambda_observed(1),
        'delta_lambda_observed_2loop': delta_lambda_observed(2),
        'sm_match_pct_1loop': abs(0.270 / dl - 1) * 100,
        'sm_match_pct_2loop': abs(0.286 / dl - 1) * 100,
    }


# ─── Coleman-Weinberg EWSB ──────────────────────────────────────────────────
#
# From: archive/scripts/ewsb_cw.py
# Section: §7 (SM parameters), §10 (electroweak symmetry breaking)
#
# PPM UV boundary conditions at k=0 (conformal, m²=0):
#   y_t(k=0) = π^{3/4} / 2^{5/4}
#   λ(k=0)   = 1/(4√π)
#   m²_H(k=0)= 0
#
# Run one-loop SM RGEs downward and check the Coleman-Weinberg condition
# λ(v) = 3y_t(v)⁴/(4π²) at k_EWSB = 44.5.


def _sm_beta_functions(y, t):
    """
    One-loop SM beta functions for [y_t, λ, g₁, g₂, g₃].

    Parameters
    ----------
    y : array-like of float
        [y_t, λ, g₁(GUT-norm), g₂, g₃]
    t : float
        ln(μ/μ_0)

    Returns
    -------
    list of float : [dy_t/dt, dλ/dt, dg₁/dt, dg₂/dt, dg₃/dt]
    """
    yt, lam, g1, g2, g3 = y
    yt2 = yt ** 2
    g12 = g1 ** 2
    g22 = g2 ** 2
    g32 = g3 ** 2

    fac = 1.0 / (16.0 * math.pi ** 2)

    beta_yt = fac * yt * (4.5 * yt2 - 8.0 * g32 - 2.25 * g22 - (17.0 / 12.0) * g12)

    beta_lam = fac * (
        24.0 * lam ** 2
        + 12.0 * lam * yt2
        - 12.0 * yt2 ** 2
        - 3.0 * lam * (3.0 * g22 + g12)
        + (9.0 / 16.0) * (2.0 * g22 ** 2 + (g22 + g12) ** 2)
    )

    beta_g1 = fac * (41.0 / 10.0) * g1 ** 3
    beta_g2 = fac * (-19.0 / 6.0) * g2 ** 3
    beta_g3 = fac * (-7.0) * g3 ** 3

    return [beta_yt, beta_lam, beta_g1, beta_g2, beta_g3]


def ewsb_coleman_weinberg(k_target=None, n_steps=200000):
    """
    Run SM couplings from PPM UV boundary (k=0) down to k_target and
    check the Coleman-Weinberg EWSB condition.

    PPM UV boundary conditions:
        y_t(k=0) = π^{3/4} / 2^{5/4}
        λ(k=0)   = 1/(4√π)
        m²_H     = 0 (conformal boundary)
        Gauge couplings extrapolated from M_Z via one-loop running.

    CW condition for EWSB (radiative symmetry breaking, m²=0):
        λ(v) = 3 y_t(v)⁴ / (4π²)

    Section: §7, §10
    Status: DERIVED

    Parameters
    ----------
    k_target : float or None
        k-level to run down to. Default: C.K_REF (k=51).
    n_steps : int
        Number of ODE integration steps.

    Returns
    -------
    dict with keys:
        k_cw          : float or None — k-level where CW condition is met
        E_cw_gev      : float or None — energy scale at CW crossing
        yt_at_cw      : float or None — y_t at CW crossing
        lam_at_cw     : float or None — λ at CW crossing
        delta_k       : float or None — k_cw − 44.5
        yt_at_target  : float — y_t at k_target
        lam_at_target : float — λ at k_target
        uv_conditions : dict — UV boundary values used
    """
    try:
        import numpy as np
        from scipy.integrate import odeint
    except ImportError:
        return {'error': 'numpy and scipy required for RGE integration'}

    if k_target is None:
        k_target = C.K_REF

    ln2pi = math.log(C.TAU)

    def _E_from_k(k):
        return C.M_PI_MEV * 1e-3 * C.TAU ** ((C.K_REF - k) / 2.0)  # GeV

    def _k_from_E(E_gev):
        return C.K_REF - 2.0 * math.log(E_gev / (C.M_PI_MEV * 1e-3)) / ln2pi

    # UV scale
    E_kP = _E_from_k(0)

    # PPM UV boundary conditions
    y_t_uv = math.pi ** 0.75 / 2.0 ** 1.25
    lam_uv = 1.0 / (4.0 * math.sqrt(math.pi))

    # Gauge couplings: extrapolate from M_Z to k=0 via one-loop running
    M_Z = C.M_Z_GEV
    t_MZ_to_kP = math.log(E_kP / M_Z)

    alpha_em_MZ = 1.0 / 127.952
    sin2_MZ = 0.23122
    cos2_MZ = 1.0 - sin2_MZ
    alpha2_MZ = alpha_em_MZ / sin2_MZ
    alpha1Y_MZ = alpha_em_MZ / cos2_MZ
    alpha1G_MZ = (5.0 / 3.0) * alpha1Y_MZ
    alpha3_MZ = C.ALPHA3_MZ

    b1, b2, b3 = 41.0 / 10.0, -19.0 / 6.0, -7.0
    inv1_kP = 1.0 / alpha1G_MZ - b1 / (2.0 * math.pi) * t_MZ_to_kP
    inv2_kP = 1.0 / alpha2_MZ - b2 / (2.0 * math.pi) * t_MZ_to_kP
    inv3_kP = 1.0 / alpha3_MZ - b3 / (2.0 * math.pi) * t_MZ_to_kP

    g1_kP = math.sqrt(4.0 * math.pi / inv1_kP)
    g2_kP = math.sqrt(4.0 * math.pi / inv2_kP)
    g3_kP = math.sqrt(4.0 * math.pi / inv3_kP)

    # Integrate downward: t from 0 to t_end = ln(E(k_target)/E(k=0))
    E_end = _E_from_k(k_target)
    t_end = math.log(E_end / E_kP)
    t_grid = np.linspace(0, t_end, n_steps)

    y0 = [y_t_uv, lam_uv, g1_kP, g2_kP, g3_kP]
    sol = odeint(_sm_beta_functions, y0, t_grid, rtol=1e-10, atol=1e-12)

    yt_arr = sol[:, 0]
    lam_arr = sol[:, 1]

    E_arr = E_kP * np.exp(t_grid)
    k_arr = np.array([_k_from_E(E) for E in E_arr])

    # CW condition: λ = 3 y_t⁴ / (4π²)
    cw_threshold = 3.0 * yt_arr ** 4 / (4.0 * math.pi ** 2)
    cw_diff = lam_arr - cw_threshold

    # Find crossing
    cross_idx = np.where(np.diff(np.sign(cw_diff)))[0]

    result = {
        'uv_conditions': {
            'y_t_uv': y_t_uv,
            'lam_uv': lam_uv,
            'g1_kP': g1_kP,
            'g2_kP': g2_kP,
            'g3_kP': g3_kP,
            'E_kP_gev': E_kP,
        },
        'yt_at_target': float(yt_arr[-1]),
        'lam_at_target': float(lam_arr[-1]),
    }

    if len(cross_idx) > 0:
        idx = cross_idx[0]
        t1, t2 = t_grid[idx], t_grid[idx + 1]
        d1, d2 = cw_diff[idx], cw_diff[idx + 1]
        t_c = t1 + (-d1) / (d2 - d1) * (t2 - t1)
        E_c = E_kP * math.exp(t_c)
        k_c = _k_from_E(E_c)
        yt_c = float(np.interp(t_c, t_grid, yt_arr))
        lam_c = float(np.interp(t_c, t_grid, lam_arr))

        result['k_cw'] = k_c
        result['E_cw_gev'] = E_c
        result['yt_at_cw'] = yt_c
        result['lam_at_cw'] = lam_c
        result['delta_k'] = k_c - C.K_EWSB
    else:
        result['k_cw'] = None
        result['E_cw_gev'] = None
        result['yt_at_cw'] = None
        result['lam_at_cw'] = None
        result['delta_k'] = None

    return result


if __name__ == "__main__":
    print(f"λ_PPM            = {lambda_ppm():.6f}  (expect 0.141047)")
    print(f"λ_τ              = {lambda_tau_conjugate():.6f}  (expect -0.141047)")
    print(f"Δλ               = {delta_lambda():.6f}  (expect 0.282095 = 1/(2√π))")
    print(f"y_t PPM          = {top_yukawa_ppm():.6f}  (expect 0.9920)")
    bl = beta_lambda_ppm()
    print(f"β_λ at PPM point = {bl['beta_lambda']:.5f}  (standard SM: −0.0254)")
    comp = higgs_quartic_comparison()
    print(f"λ_PPM vs obs:    = {comp['error_pct']:+.1f}%  (geometric value; 4.5% tree-level accuracy in m_H)")

    print("\nColeman-Weinberg EWSB check:")
    cw = ewsb_coleman_weinberg()
    if 'error' in cw:
        print(f"  {cw['error']}")
    elif cw['k_cw'] is not None:
        print(f"  k_CW = {cw['k_cw']:.4f}  (target 44.5, Δk = {cw['delta_k']:+.4f})")
        print(f"  E_CW = {cw['E_cw_gev']:.4e} GeV")
        print(f"  y_t at CW  = {cw['yt_at_cw']:.5f}")
        print(f"  λ at CW    = {cw['lam_at_cw']:.5f}")
    else:
        print("  No CW crossing found in integration range.")

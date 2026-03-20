"""
ppm.alpha — Fine-structure constant derivations
================================================

PPM derives α ≈ 1/137.036 from three independent routes, all probing the
same geometric ratio: how much of CP³ is RP³.

Route I  (Spectral): Θ^τ/Θ_{CP³} at t*=1/32 → 1/α = 137.257 (0.16%)  [COMPLETE]
Route II (Cogito loop): Λ_obs → N → α via G formula → 1/α ≈ 137.6 (~0.4%)  [PARTIAL]
Route III (Instanton): R_τ = (1/2)e^{-30π} as τ fixed point  [PARKED — prefactor open]

Section reference: §5 (Three Derivations of α)
"""

import math
from . import constants as C


ALPHA_OBSERVED = 1.0 / C.ALPHA_EM_INV  # ≈ 7.2974e-3


# ─── Route I: Spectral Geometry ──────────────────────────────────────────────

def _twisted_heat_traces(t, nmax=200):
    """
    Compute Θ^τ(t) and Θ_{CP³}(t).

    Θ^τ(t)    = Σ_k tr(τ|V_k) e^{-λ_k t}
    Θ_{CP³}(t) = Σ_k d_k e^{-λ_k t}

    where:
      λ_k = k(k+3)                           (CP³ Laplacian eigenvalues)
      d_k = C(k+3,3)² − C(k+2,3)²           (total degeneracy)
      tr(τ|V_k) = C(k+3,3) − C(k+2,3)       (τ-even count)
    """
    theta_tau = 0.0
    theta_cp3 = 0.0
    for k in range(nmax):
        lam_k = k * (k + 3)
        tr_tau_k = math.comb(k + 3, 3) - math.comb(k + 2, 3)
        d_k = math.comb(k + 3, 3)**2 - math.comb(k + 2, 3)**2
        w = math.exp(-lam_k * t)
        theta_tau += tr_tau_k * w
        theta_cp3 += d_k * w
    return theta_tau, theta_cp3


def t_star(n=3):
    """
    Half-variance condition at the spectral gap.

    LaTeX (eq:half_variance): t* = 1/(2(n+1)²)
    For CP³ (n=3): t* = 1/(2×16) = 1/32

    The first nonzero eigenvalue of the CP^n Laplacian is λ₁ = n+1.
    The condition λ₁² · t* = 1/2 gives t* = 1/(2(n+1)²).
    Status: DERIVED (VERIFIED)
    """
    return 1.0 / (2.0 * (n + 1)**2)


def alpha_from_spectral_geometry(nmax=200):
    """
    Route I: α from the twisted heat trace ratio Θ^τ/Θ_{CP³} at t*=1/32.

    section5-alpha.tex: "the twisted ratio Θ^τ(t)/Θ_{CP³}(t) = α at t*=1/32,
    to 0.16% accuracy."

    Result: 1/α = 137.257 (error = −0.161% from 137.036)
    Converges by nmax ≈ 50.
    Status: VERIFIED (COMPLETE — parameter-free geometric derivation)
    """
    ts = t_star(n=3)
    theta_tau, theta_cp3 = _twisted_heat_traces(ts, nmax)
    alpha = theta_tau / theta_cp3
    return {
        'alpha': alpha,
        'alpha_inv': 1.0 / alpha,
        't_star': ts,
        'error_pct': (alpha / ALPHA_OBSERVED - 1.0) * 100.0,
        'status': 'COMPLETE',
    }


def alpha_cpn_family(n_range=range(1, 8), nmax=300):
    """
    Compute 1/α predictions across the CP^n family using the half-variance condition.

    section5-alpha.tex: CP¹→1/3.2, CP²→1/18, CP³→1/137.3, CP⁴→1/1258, CP⁵→1/13314.
    Only n=3 places 1/α in the physical range.
    Status: VERIFIED
    """
    results = {}
    for n in n_range:
        ts = t_star(n)
        theta_tau = 0.0
        theta_cp = 0.0
        for k in range(nmax):
            lam_k = k * (k + n)
            tr_tau = math.comb(k + n, n) - math.comb(k + n - 1, n)
            d_k = math.comb(k + n, n)**2 - math.comb(k + n - 1, n)**2
            w = math.exp(-lam_k * ts)
            theta_tau += tr_tau * w
            theta_cp += d_k * w
        alpha = theta_tau / theta_cp if theta_cp > 0 else float('nan')
        results[n] = {'alpha_inv': 1.0 / alpha, 't_star': ts}
    return results


# ─── Route II: Cogito Loop ───────────────────────────────────────────────────

def alpha_from_cogito_loop():
    """
    Route II: α from the cogito loop consistency check.

    Uses observed G and Λ to extract N, then derives α:
      Λ = 2(m_πc²)²/((ℏc)²N)  →  N = 2(m_πc²)²/((ℏc)²Λ_obs)
      G = 16π⁴ℏcα/(m_π²√N)    →  α = G·m_π²·√N/(16π⁴ℏc)

    This is NOT an independent derivation: it uses G_obs and Λ_obs as inputs.
    Full independence requires computing c_{1,topo} from the CP³ sigma model.

    Result: 1/α ≈ 137.6 (~0.4% from 137.036)
    Status: VERIFIED (PARTIAL — anchored to observed G and Λ)
    """
    # Natural units: G_N in GeV^{-2}, m_π in GeV, Λ in GeV²
    G_N = 6.70883e-39
    m_pi = 0.1349768  # GeV (neutral pion mass)

    # Λ_obs in natural units
    Lambda_nat = 1.089e-52 * (1.97326980e-16)**2

    # N = 2 m_π² / Λ_nat
    N = 2.0 * m_pi**2 / Lambda_nat

    # α = G_N · m_π² · √N / (16π⁴)
    alpha = G_N * m_pi**2 * math.sqrt(N) / (16.0 * math.pi**4)

    phi = C.PHI
    phi_196 = phi**196.0

    return {
        'alpha': alpha,
        'alpha_inv': 1.0 / alpha,
        'N': N,
        'sqrt_N': math.sqrt(N),
        'phi_196': phi_196,
        'sqrt_N_over_phi196': math.sqrt(N) / phi_196,
        'error_pct': (alpha / ALPHA_OBSERVED - 1.0) * 100.0,
        'status': 'PARTIAL (anchored to G_obs, Λ_obs)',
    }


# ─── Route III: Measurement Instanton ────────────────────────────────────────

def alpha_from_instanton():
    """
    Route III: α as the self-consistent τ firing rate.

    LaTeX: R_τ = R_τ^pert × e^{-S_inst} ≈ (1/2) e^{-30π} ≈ α

    CRITICAL NOTE: The bare value (1/2)e^{-30π} = 5.86×10^{-42} differs from
    α = 7.30×10^{-3} by a factor of ~10^{39}. The paper acknowledges the
    prefactor calculation (from 30 zero modes + determinant ratio) is PARKED.

    Status: PARKED (exponent motivated, prefactor open)
    """
    S_inst = C.INSTANTON_ACTION  # 30π ≈ 94.248
    R_tau_bare = 0.5 * math.exp(-S_inst)
    prefactor_needed = ALPHA_OBSERVED / R_tau_bare

    return {
        'R_tau_bare': R_tau_bare,
        'alpha_observed': ALPHA_OBSERVED,
        'prefactor_gap': prefactor_needed,
        'log10_prefactor_gap': math.log10(prefactor_needed),
        'S_inst': S_inst,
        'note': 'Bare (1/2)e^{-30π} = 5.86e-42; prefactor of ~10^39 needed from 30 zero modes',
        'status': 'PARKED (prefactor open)',
    }


# ─── Comparison ──────────────────────────────────────────────────────────────

def alpha_comparison():
    """
    Compare all three routes.

    Route I:   1/α = 137.257 (0.16% off) — COMPLETE
    Route II:  1/α ≈ 137.6  (0.4% off)  — PARTIAL (uses G_obs, Λ_obs)
    Route III: PARKED (prefactor gap ~10^39)
    """
    r1 = alpha_from_spectral_geometry()
    r2 = alpha_from_cogito_loop()
    r3 = alpha_from_instanton()
    return {
        'route_I': r1,
        'route_II': r2,
        'route_III': r3,
        'alpha_observed': ALPHA_OBSERVED,
        'alpha_inv_observed': 1.0 / ALPHA_OBSERVED,
    }


def alpha_observed():
    """Standard observed value 1/137.036."""
    return ALPHA_OBSERVED


if __name__ == "__main__":
    print("=== Route I: Spectral Geometry ===")
    r1 = alpha_from_spectral_geometry()
    print(f"  1/α = {r1['alpha_inv']:.3f}  (error = {r1['error_pct']:+.3f}%)  [{r1['status']}]")

    print("\n=== Route II: Cogito Loop ===")
    r2 = alpha_from_cogito_loop()
    print(f"  1/α = {r2['alpha_inv']:.3f}  (error = {r2['error_pct']:+.3f}%)  [{r2['status']}]")
    print(f"  N = {r2['N']:.3e}, √N = {r2['sqrt_N']:.3e}, φ¹⁹⁶ = {r2['phi_196']:.3e}")
    print(f"  √N/φ¹⁹⁶ = {r2['sqrt_N_over_phi196']:.4f}")

    print("\n=== Route III: Instanton ===")
    r3 = alpha_from_instanton()
    print(f"  R_τ(bare) = {r3['R_tau_bare']:.3e}")
    print(f"  Prefactor gap = {r3['prefactor_gap']:.3e} (~10^{r3['log10_prefactor_gap']:.1f})")
    print(f"  [{r3['status']}]")

    print(f"\n=== Observed: 1/α = {1/ALPHA_OBSERVED:.3f} ===")

    print("\n=== CP^n Family ===")
    fam = alpha_cpn_family()
    for n, d in fam.items():
        print(f"  CP^{n}: 1/α = {d['alpha_inv']:.1f}  (t* = {d['t_star']:.6f})")

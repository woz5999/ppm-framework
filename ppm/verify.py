"""
ppm.verify — Master verification runner
========================================

Runs all implemented computations and prints a pass/fail table comparing
PPM predictions to expected values from prior verified sessions.

Run this at the start of each new session to confirm the codebase state.
"""

import math
from . import constants as C
from . import hierarchy as H
from . import higgs as HI
from . import gauge as G
from . import instanton as I
from . import spectral as S
from . import alpha as A
from . import berry_phase as BP
from . import neutrino as NU
from . import golden_ratio as GR_phi
from . import cosmology as GR


PASS_THRESHOLD_PCT = 0.1   # <= 0.1% difference → PASS
WARN_THRESHOLD_PCT = 5.0   # <= 5% difference → WARN; else FAIL


def check(name, computed, expected, tol_pct=None):
    """Return a result dict for one check."""
    if tol_pct is None:
        tol_pct = PASS_THRESHOLD_PCT
    if expected == 0:
        diff_pct = abs(computed - expected)
    else:
        diff_pct = abs(computed / expected - 1.0) * 100.0

    if diff_pct <= tol_pct:
        status = "PASS"
    elif diff_pct <= WARN_THRESHOLD_PCT:
        status = "WARN"
    else:
        status = "FAIL"
    return {'name': name, 'computed': computed, 'expected': expected,
            'diff_pct': diff_pct, 'status': status}


def run_all():
    """Run all implemented checks. Returns list of result dicts."""
    results = []

    # ─── constants ────────────────────────────────────────────────────────────
    results.append(check("λ_PPM = 1/(4√π)",
                         C.LAMBDA_PPM, 0.141047, tol_pct=0.01))
    results.append(check("Δλ = 1/(2√π)",
                         C.DELTA_LAMBDA, 0.282095, tol_pct=0.01))
    results.append(check("y_t PPM = π/(2(2π)^{1/4})",
                         HI.top_yukawa_ppm(), 0.99200, tol_pct=0.1))
    results.append(check("S = 30π",
                         I.instanton_action(), 30*math.pi, tol_pct=0.001))
    results.append(check("α_GUT = 1/10",
                         C.ALPHA_GUT, 0.10000, tol_pct=0.001))
    results.append(check("sin²θ_W PPM = 3/8",
                         C.SIN2_THETA_W_PPM, 0.37500, tol_pct=0.001))

    # ─── hierarchy ────────────────────────────────────────────────────────────
    results.append(check("E(k=51) = 140 MeV",
                         H.energy_mev(51.0), 140.0, tol_pct=0.001))
    results.append(check("E(k=1) / E_Planck error < 6%",
                         H.energy_gev(1.0), C.E_PLANCK_GEV, tol_pct=6.0))

    # ─── alpha ────────────────────────────────────────────────────────────────
    r1 = A.alpha_from_spectral_geometry()
    results.append(check("1/α (Route I) = 137.257",
                         r1['alpha_inv'], 137.257, tol_pct=0.01))

    # ─── instanton ────────────────────────────────────────────────────────────
    ck = I.phi_196_check()
    results.append(check("e^{-30π}/φ^{-196} ratio near 1",
                         ck['ratio'], 1.0, tol_pct=8.0))
    results.append(check("φ^{-196} exponent mismatch < 0.1%",
                         ck['mismatch_pct'], 0.0, tol_pct=0.1))

    zm = I.zero_mode_count()
    results.append(check("Zero modes = 30",
                         float(zm['n_real']), 30.0, tol_pct=0.001))

    # ─── T² partition function ────────────────────────────────────────────────
    zt = I.zt2_per_scalar()
    results.append(check("log Z_T² per scalar",
                         zt['log_ZT2'], 0.5274, tol_pct=0.1))
    zt6 = I.zt2_total(6)
    results.append(check("log Z_T² total 6 dof",
                         zt6['log_ZT2_total'], 3.164, tol_pct=0.1))

    # ─── gauge ────────────────────────────────────────────────────────────────
    sin2_res = G.sin2_theta_W_sm_running()
    results.append(check("sin²θ_W(E_break) SM running",
                         sin2_res['sin2_tW_sm'], 0.37550, tol_pct=0.1))

    # ─── spectral ─────────────────────────────────────────────────────────────
    results.append(check("ζ_Δ(0) = -733/945",
                         S.zeta_delta_0(), -733.0/945.0, tol_pct=0.001))
    results.append(check("Z₁ ≈ 0.88",
                         S.Z1_oneloop(), 0.88, tol_pct=1.0))

    # ─── berry phase (new) ────────────────────────────────────────────────────
    dcp = BP.delta_cp()
    # π(1-1/φ) = π/φ² = 1.19998...
    delta_cp_exact = math.pi / C.PHI**2
    results.append(check("δ_CP = π(1−1/φ) ≈ 1.200 rad",
                         dcp['delta_cp_rad'], delta_cp_exact, tol_pct=0.01))

    # ─── neutrino (new) ──────────────────────────────────────────────────────
    ts = NU.theta_strong()
    results.append(check("θ_strong = 0",
                         ts['theta'], 0.0, tol_pct=0.001))

    # ─── golden ratio (new) ──────────────────────────────────────────────────
    pi_id = GR_phi.pyramidal_identity()
    results.append(check("P₃²·ln(φ) / (P₄·π) ≈ 1",
                         pi_id['ratio'], 1.0, tol_pct=0.1))

    # ─── cosmology ────────────────────────────────────────────────────────────
    h0 = GR.hubble_from_age()
    results.append(check("H₀ ≈ 70.9 km/s/Mpc",
                         h0['H0_km_s_Mpc'], 70.9, tol_pct=0.5))

    lam_cc = GR.cosmological_constant()
    results.append(check("Λ ≈ 1.1e-52 m⁻²",
                         lam_cc['Lambda_m2'], 1.1e-52, tol_pct=5.0))

    return results


def print_report():
    """Print the full verification report."""
    results = run_all()
    n_pass = sum(1 for r in results if r['status'] == 'PASS')
    n_warn = sum(1 for r in results if r['status'] == 'WARN')
    n_fail = sum(1 for r in results if r['status'] == 'FAIL')

    print("=" * 80)
    print("PPM VERIFICATION REPORT")
    print("=" * 80)
    print(f"{'Check':<45} {'Computed':>12} {'Expected':>12} {'Diff%':>8} Status")
    print("-" * 80)

    for r in results:
        flag = "✓" if r['status'] == 'PASS' else ("⚠" if r['status'] == 'WARN' else "✗")
        print(f"{r['name']:<45} {r['computed']:>12.6g} {r['expected']:>12.6g} "
              f"{r['diff_pct']:>7.4f}% {flag} {r['status']}")

    print("-" * 80)
    print(f"PASS: {n_pass}  WARN: {n_warn}  FAIL: {n_fail}  "
          f"Total: {len(results)}")
    print("=" * 80)

    if n_fail > 0:
        print("\nFAILED checks:")
        for r in results:
            if r['status'] == 'FAIL':
                print(f"  {r['name']}: computed={r['computed']:.6g} "
                      f"expected={r['expected']:.6g} ({r['diff_pct']:.2f}%)")

    return results


if __name__ == "__main__":
    print_report()

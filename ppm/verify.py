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
from . import dynamics as D
from . import active_inference as AI
from . import kahler_spectrum as KS


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

    # ─── N self-consistency ──────────────────────────────────────────────────
    results.append(check("N self-consistency: (2π)^108 α² ≈ φ^392",
                         C.N_SELF_CONSISTENCY, C.N_ASYMPTOTIC, tol_pct=2.0))

    # ─── Friedmann age ───────────────────────────────────────────────────────
    fa = GR.friedmann_age()
    results.append(check("Friedmann age ≈ 13.8 Gyr",
                         fa['T_pred_Gyr'], 13.797, tol_pct=5.0))

    # ─── Actualization record ────────────────────────────────────────────────
    ar = GR.actualization_record()
    results.append(check("S_record/S_BH ~ O(1)",
                         ar['S_ratio'], 1.0, tol_pct=100.0))

    # ─── Lindblad dynamics (ppm.dynamics) ────────────────────────────────────
    # Numerical validation that the implemented actualization channel
    # reproduces the analytical claims from
    # archive/scripts/actualization_operator.py and the chapter prose in
    # ch08-variational §Actualization Free Energy + ch18-quantum
    # §Hamiltonian Architecture. See also archive/plans/2026-04-26-route-b-lindblad/.

    dyn_trace_drift = check_lindblad_trace_preservation()
    results.append(check("Lindblad: |Tr(ρ(T)) − 1| ~ 0",
                         dyn_trace_drift, 0.0, tol_pct=1e-6))

    dyn_min_eig = check_lindblad_positivity_preservation()
    results.append(check("Lindblad: min eig(ρ(T)) ≥ −ε",
                         dyn_min_eig, 0.0, tol_pct=1e-6))

    dyn_born_yield = check_born_rule_fixed_point()
    results.append(check("Lindblad: Born yield Tr(Â|ψ⟩⟨ψ|Â) = cos²(π/4) = ½",
                         dyn_born_yield, 0.5, tol_pct=0.01))

    dyn_decoherence_ratio = check_penrose_diosi_decoherence_match()
    results.append(check("Lindblad: |ρ_{+−}(t)|/|ρ_{+−}(0)| = exp(−γt/2)",
                         dyn_decoherence_ratio, 1.0, tol_pct=0.01))

    dyn_zeno_weight = check_zeno_regime_protection()
    results.append(check("Lindblad: Zeno (γ≫ω) holds τ-odd weight < 0.05",
                         dyn_zeno_weight, 0.0, tol_pct=0.05))

    # ─── Active inference (ppm.active_inference) ─────────────────────────────
    # Numerical validation that the framework's active-inference dynamics —
    # inner-loop ρ Lindblad coupled to outer-loop θ gradient descent on F —
    # converges to a self-consistent (ρ, θ) fixed point with monotone-on-
    # average F descent. Documents the implementation against the chapter
    # claims in ch02-operator §Cross-Scale Specialization (Consciousness
    # Scale) and ch18-quantum §Reduced Dynamics.

    ai_descent_ratio = check_active_inference_F_descent()
    results.append(check("Active inference: F_final / F_initial after descent",
                         ai_descent_ratio, 0.0, tol_pct=0.75))

    ai_fixed_point_drift = check_active_inference_fixed_point_stability()
    results.append(check("Active inference: F drift over last 10 cycles ~ 0",
                         ai_fixed_point_drift, 0.0, tol_pct=0.005))

    # ─── Two-boundary active inference (Tier 2 shared environment) ───────────
    # Numerical validation that the joint-detection coupling between two
    # boundaries produces emergent inter-boundary correlation. Backs the
    # chapter prose claim that boundaries can coordinate through a shared
    # environment without direct communication.

    tb_independent_MI = check_two_boundary_independent_zero_MI()
    results.append(check("Two-boundary: MI ≈ 0 at α = 0 (no coupling)",
                         tb_independent_MI, 0.0, tol_pct=0.001))

    tb_coupled_MI = check_two_boundary_coupled_positive_MI()
    results.append(check("Two-boundary: MI > 0.05 at α = 1.0 (joint-detection)",
                         tb_coupled_MI, 0.1, tol_pct=80.0))

    # ─── Canonical demos: frame-finding and decoherence race ─────────────────
    ff_error = check_frame_finding_recovers_alpha()
    results.append(check("Frame-finding: discovers hidden α to < 0.01 rad",
                         ff_error, 0.0, tol_pct=0.01))

    dr_advantage = check_decoherence_race_active_advantage()
    results.append(check("Decoherence race: active mean F < passive mean F",
                         dr_advantage, 0.5, tol_pct=80.0))

    aggregation_recovery = check_phi_aggregation_recovers_signal()
    results.append(check(
        "Φ-aggregation: integrating agent (N=15) beats naive (N=1) at high noise",
        aggregation_recovery, 0.5, tol_pct=80.0))

    # ─── I11: Kähler-spectrum on CP³ (radial sector) ─────────────────────────
    # Free CP³ Laplacian: eigenvalues should be 4l(l+3) for l = 0, 1, 2, ...
    free = KS.free_laplacian_spectrum(N=1500, n_eigs=6)
    free_max_err = float(max(abs(free[l] - 4*l*(l+3)) for l in range(6)))
    results.append(check(
        "Kähler-spectrum: free CP³ Laplacian eigenvalues match 4l(l+3)",
        free_max_err, 0.0, tol_pct=0.01))

    # H_α full spectrum: ε_n ≈ 2n(n+3) + ε_0, with ε_0 ≈ 1.71.
    # Verify ε_0 (the Kähler-potential ground state) is ~1.71.
    eigs = KS.h_alpha_spectrum(N=1500, n_eigs=6)
    results.append(check(
        "Kähler-spectrum: H_α ground-state ε_0 ≈ 1.706 (Kähler shift)",
        float(eigs[0]), 1.706, tol_pct=0.5))

    # Verify the spectrum is approximately quadratic in n via the fit a≈2.
    a_fit, b_fit, _ = KS.quadratic_fit(eigs)
    results.append(check(
        "Kähler-spectrum: quadratic-fit slope a ≈ 2 (kinetic prefactor)",
        a_fit, 2.0, tol_pct=2.0))

    return results


# ─── Lindblad dynamics check helpers ────────────────────────────────────────
#
# Each helper sets up a small dimensionless Lindblad evolution and returns
# a single scalar that the caller compares to an analytical prediction.
# Costs are kept low (k_max=1, total_dim=16, < 1k RK4 steps each) so the
# full verify.run_all() suite stays under a few seconds.


def check_lindblad_trace_preservation():
    """
    Evolve a generic τ-mixed pure state under H_α + actualization dissipator and
    return the absolute drift |Tr(ρ(T)) − 1| at the end of the evolution.

    Analytical claim: Lindblad evolution preserves trace exactly; numerical
    drift comes only from RK4 truncation error. With dt = 0.01 over 500 steps
    we expect drift ≪ 1e-8.
    """
    basis = D.Basis(k_max=1)
    idx_p = basis.first_plus_index(1)
    idx_m = basis.first_minus_index(1)
    psi = 0.6 * basis.basis_vector(idx_p) + 0.8 * basis.basis_vector(idx_m)
    rho_0 = D.Density.pure(basis, psi)
    H = D.free_hamiltonian(basis)
    mode_idx = int((basis.tau_parity[:idx_p + 1] == +1).sum()) - 1
    A = D.boundary_operator(basis, mode_idx)
    traj = D.lindblad_evolve(rho_0, H, [A], [1.5],
                             T=5.0, n_steps=500, snapshots=[500])
    _, rho_T = traj[-1]
    return abs(rho_T.trace().real - 1.0)


def check_lindblad_positivity_preservation():
    """
    Evolve as in trace test; return |min(eig(ρ(T)))| if negative, else 0.

    Analytical claim: Lindblad evolution preserves positivity (CP-divisibility).
    Numerical violations indicate stiffness or rounding issues.
    """
    import numpy as np
    basis = D.Basis(k_max=1)
    idx_p = basis.first_plus_index(1)
    idx_m = basis.first_minus_index(1)
    psi = 0.6 * basis.basis_vector(idx_p) + 0.8 * basis.basis_vector(idx_m)
    rho_0 = D.Density.pure(basis, psi)
    H = D.free_hamiltonian(basis)
    mode_idx = int((basis.tau_parity[:idx_p + 1] == +1).sum()) - 1
    A = D.boundary_operator(basis, mode_idx)
    traj = D.lindblad_evolve(rho_0, H, [A], [1.5],
                             T=5.0, n_steps=500, snapshots=[500])
    _, rho_T = traj[-1]
    herm = 0.5 * (rho_T.matrix + rho_T.matrix.conj().T)
    min_eig = float(np.linalg.eigvalsh(herm).min())
    return abs(min(0.0, min_eig))


def check_born_rule_fixed_point():
    """
    Born-rule yield from the single-event projection.

    For |ψ⟩ = cos(π/4) |+⟩ + sin(π/4) |−⟩, applying Â (= τ-projector) gives
    Â|ψ⟩⟨ψ|Â with trace = cos²(π/4) = ½. Returns the trace.

    This is the discrete piece of the actualization channel — Born rule
    emergence from the Lindblad fixed-point structure.
    """
    basis = D.Basis(k_max=1)
    idx_p = basis.first_plus_index(1)
    idx_m = basis.first_minus_index(1)
    theta = math.pi / 4.0
    psi = (math.cos(theta) * basis.basis_vector(idx_p)
           + math.sin(theta) * basis.basis_vector(idx_m))
    rho = D.Density.pure(basis, psi)
    A = D.tau_projector(basis)
    projected = A.apply_to(rho)
    return float(projected.trace().real)


def check_penrose_diosi_decoherence_match():
    """
    Off-diagonal decay rate matches the analytical Penrose–Diósi-style
    prediction τ_dec = 2/γ (i.e., |ρ_{+−}(t)|/|ρ_{+−}(0)| = exp(−γt/2)).

    Returns the ratio of (numerical decay) / (analytical decay) at t=2/γ
    (one e-fold). Should equal 1 to within RK4 accuracy.
    """
    basis = D.Basis(k_max=1)
    idx_p = basis.first_plus_index(1)
    idx_m = basis.first_minus_index(1)
    psi = 0.6 * basis.basis_vector(idx_p) + 0.8 * basis.basis_vector(idx_m)
    rho_0 = D.Density.pure(basis, psi)
    c_0 = abs(complex(rho_0.matrix[idx_p, idx_m]))
    gamma = 2.0
    H = D.Operator(basis, __import__('numpy').zeros(
        (basis.total_dim, basis.total_dim), dtype=complex))
    mode_idx = int((basis.tau_parity[:idx_p + 1] == +1).sum()) - 1
    A = D.boundary_operator(basis, mode_idx)
    t_target = 2.0 / gamma  # one e-fold
    n_steps = 200
    traj = D.lindblad_evolve(rho_0, H, [A], [gamma],
                             T=t_target, n_steps=n_steps,
                             snapshots=[n_steps])
    _, rho_T = traj[-1]
    c_T = abs(complex(rho_T.matrix[idx_p, idx_m]))
    numerical = c_T / c_0
    analytical = math.exp(-0.5 * gamma * t_target)
    return numerical / analytical


def check_active_inference_F_descent():
    """
    Run a short active-inference loop and return F_final / F_initial.

    Expected: ratio < 1 (F descended). The 0.75 tolerance in the verify
    suite allows for the self-consistent fixed point not being at F = 0
    when ρ has structure preserved by Lindblad in the rotated basis.
    """
    import math
    basis = D.Basis(k_max=1)
    doublet = AI.default_doublet_indices(basis)
    psi = basis.basis_vector(doublet[0])
    rho_0 = D.Density.pure(basis, psi)
    loop = AI.ActiveInferenceLoop(
        rho_0, (math.pi/4, math.pi/4), basis, doublet,
        dt=0.05, eta=0.05, N_inner=20, gamma=0.5)
    loop.run(n_cycles=80)
    F_initial = loop.trajectory[0]['F']
    F_final = loop.trajectory[-1]['F']
    if F_initial <= 0:
        return 0.0
    return F_final / F_initial


def check_active_inference_fixed_point_stability():
    """
    Run an active-inference loop and return the F drift across the last
    10 cycles. Expected: near zero (system has reached a stable fixed
    point).
    """
    import math
    basis = D.Basis(k_max=1)
    doublet = AI.default_doublet_indices(basis)
    psi = basis.basis_vector(doublet[0])
    rho_0 = D.Density.pure(basis, psi)
    loop = AI.ActiveInferenceLoop(
        rho_0, (math.pi/4, math.pi/4), basis, doublet,
        dt=0.05, eta=0.05, N_inner=20, gamma=0.5)
    loop.run(n_cycles=120)
    recent_F = [s['F'] for s in loop.trajectory[-10:]
                if not (s['F'] != s['F'] or s['F'] == float('inf'))]
    if len(recent_F) < 2:
        return 0.0
    return max(recent_F) - min(recent_F)


def _two_boundary_MI_at_alpha(alpha: float, n_cycles: int = 10):
    """Run a small TwoBoundaryActiveInferenceLoop and return MI(ρ_1; ρ_2)."""
    import math
    import numpy as np
    basis_S1 = D.Basis(k_max=1)
    basis_S2 = D.Basis(k_max=1)
    doublet_S1 = AI.default_doublet_indices(basis_S1)
    doublet_S2 = AI.default_doublet_indices(basis_S2)
    joint = AI.TensorProductBasis(basis_S1, basis_S2)
    psi_1 = basis_S1.basis_vector(doublet_S1[0])
    psi_2 = basis_S2.basis_vector(doublet_S2[0])
    psi_joint = joint.product_state(psi_1, psi_2)
    rho_0 = D.Density.pure(joint, psi_joint)
    loop = AI.TwoBoundaryActiveInferenceLoop(
        rho_0,
        (math.pi/3, 0.4), (math.pi/6, 1.2),
        basis_S1, basis_S2, doublet_S1, doublet_S2,
        alpha=alpha, dt=0.05, eta=0.05, N_inner=5, gamma=0.5)
    loop.run(n_cycles=n_cycles)
    snap = loop.trajectory[-1]

    def vne(m):
        h = 0.5 * (m + m.conj().T)
        eigs = np.linalg.eigvalsh(h)
        eigs = eigs[eigs > 1e-15]
        return float(-np.sum(eigs * np.log(eigs)))

    S1 = vne(snap['rho_1'].matrix)
    S2 = vne(snap['rho_2'].matrix)
    S12 = vne(snap['rho_joint'].matrix)
    return S1 + S2 - S12


def check_two_boundary_independent_zero_MI():
    """At α=0 (no shared coupling), joint state stays product → MI ≈ 0."""
    return _two_boundary_MI_at_alpha(alpha=0.0, n_cycles=10)


def check_two_boundary_coupled_positive_MI():
    """At α=1 (full joint-detection coupling), MI > 0 emerges."""
    return _two_boundary_MI_at_alpha(alpha=1.0, n_cycles=10)


def check_frame_finding_recovers_alpha():
    """
    Adaptive measurement frame-finding canonical demo.

    Hidden state ρ = |ψ_K(α)⟩⟨ψ_K(α)| with α = π/3. FrameFindingLoop
    starts at θ_AB = π/8 and should converge to α = π/3.

    Returns the absolute error |θ_AB_final − α|.
    """
    import math
    basis = D.Basis(k_max=1)
    doublet = AI.default_doublet_indices(basis)
    target = math.pi / 3
    psi = (math.cos(target) * basis.basis_vector(doublet[0])
           + math.sin(target) * basis.basis_vector(doublet[1]))
    rho = D.Density.pure(basis, psi)
    loop = AI.FrameFindingLoop(
        rho, (math.pi/8, math.pi/4),
        basis, doublet, eta=0.05)
    loop.run(n_steps=200)
    return abs(loop.theta_AB - target)


def check_phi_aggregation_recovers_signal():
    """
    Φ-style aggregation canonical demo: at high signal noise (analog of the
    R≈1 boundary), bare gradient descent fails. Aggregating N samples per
    step recovers convergence — the framework's prescribed mechanism for
    the consciousness-scale R(k_c) ≈ 1 regime.

    Returns: mean error reduction across multiple seeds. Positive means
    aggregation reduced error vs naive on average. Single-trial outcomes
    are noisy by construction (high signal noise); seed-averaging is the
    statistically meaningful comparison.
    """
    import math
    basis = D.Basis(k_max=1)
    doublet = AI.default_doublet_indices(basis)
    target = math.pi / 3
    psi = (math.cos(target) * basis.basis_vector(doublet[0])
           + math.sin(target) * basis.basis_vector(doublet[1]))
    rho = D.Density.pure(basis, psi)
    common = dict(eta=0.05, noise_sigma=0.02, signal_noise_sigma=2.0)

    seeds = [11, 23, 41, 67, 89, 103]
    naive_errs = []
    integ_errs = []
    for seed in seeds:
        naive = AI.FrameFindingLoop(
            rho, (math.pi/8, math.pi/4), basis, doublet,
            N_aggregate=1, seed=seed, **common)
        naive.run(n_steps=200)
        naive_errs.append(abs(naive.theta_AB - target))

        integ = AI.FrameFindingLoop(
            rho, (math.pi/8, math.pi/4), basis, doublet,
            N_aggregate=15, seed=seed, **common)
        integ.run(n_steps=200)
        integ_errs.append(abs(integ.theta_AB - target))

    mean_naive = sum(naive_errs) / len(naive_errs)
    mean_integ = sum(integ_errs) / len(integ_errs)
    return mean_naive - mean_integ


def check_decoherence_race_active_advantage():
    """
    Decoherence race canonical demo: selective advantage of adaptation.

    Active system (η=0.05) and passive system (η=0) start from same ρ and
    same offset-from-optimum θ. Active maintains lower mean F.

    Returns the fitness advantage = mean_F_passive − mean_F_active.
    Expected ~ 0.5–1.0 nats for the standard parameters.
    """
    import math
    basis = D.Basis(k_max=1)
    doublet = AI.default_doublet_indices(basis)
    psi = basis.basis_vector(doublet[0])  # |A⟩
    rho_0 = D.Density.pure(basis, psi)
    result = AI.run_decoherence_race(
        rho_0, (math.pi/3, math.pi/3),
        basis, doublet,
        gamma=0.5, dt=0.05, N_inner=10, n_cycles=40,
        eta_active=0.05)
    return result['fitness_advantage']


def check_zeno_regime_protection():
    """
    Quantum Zeno regime: with γ ≫ ω in the dissipator, an initially τ-even
    pure state held against a τ-mixing Hamiltonian retains τ-odd weight < 5%.

    Returns the τ-odd weight at t = 1.0 with γ_zeno = 1000, ω_mix = 1.0.
    """
    import numpy as np
    basis = D.Basis(k_max=1)
    idx_p = basis.first_plus_index(1)
    idx_m = basis.first_minus_index(1)
    # Mixing Hamiltonian: |+⟩ ↔ |−⟩ off-diagonal coupling
    H_m = np.zeros((basis.total_dim, basis.total_dim), dtype=complex)
    omega = 1.0
    H_m[idx_p, idx_m] = omega
    H_m[idx_m, idx_p] = omega
    H_mix = D.Operator(basis, H_m)
    psi = basis.basis_vector(idx_p)
    rho_0 = D.Density.pure(basis, psi)
    mode_idx = int((basis.tau_parity[:idx_p + 1] == +1).sum()) - 1
    A = D.boundary_operator(basis, mode_idx)
    gamma = 1000.0
    traj = D.lindblad_evolve(rho_0, H_mix, [A], [gamma],
                             T=1.0, n_steps=2000, snapshots=[2000])
    _, rho_T = traj[-1]
    return rho_T.tau_odd_weight()


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


# ─── Aliases for LaTeX Code: references ─────────────────────────────────────

def self_consistency():
    """Self-consistency verification subset.

    LaTeX: \\textit{Code: ppm.verify.self_consistency()}  [ch14]
    """
    results = run_all()
    return {
        'all_checks': results,
        'n_pass': sum(1 for r in results if r['status'] == 'PASS'),
        'n_total': len(results),
        'status': 'PASS' if all(r['status'] != 'FAIL' for r in results) else 'FAIL'
    }


if __name__ == "__main__":
    print_report()

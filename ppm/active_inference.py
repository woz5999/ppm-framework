"""
ppm.active_inference — Computational active inference on the measurement torus
==============================================================================

Numerically demonstrates the framework's claim that consciousness dynamics emerge
from the same Lindblad geometry as physics, by coupling:

    Inner loop:  ρ-Lindblad evolution at fixed θ            (from ppm.dynamics)
    Outer loop:  θ-gradient descent on F[ρ, θ]              (this module)

θ = (θ_AB, θ_CD) ∈ T² parameterizes the measurement-torus rotation acting on the
actualization operator: A_b(θ) = R(θ) Â R†(θ), where R is an SO(2)×SO(2)
rotation in the Kähler doublet (|A⟩, |B⟩) plane and the gauge doublet
(|C⟩, |D⟩) plane. T² = PGL(4,R) / Stab(V_AB ⊕ V_CD), per ch07-information §7.5.

Provides:
    TensorProductBasis              # composes two Bases (system + environment)
    partial_trace                   # trace out one subsystem
    ParameterizedBoundaryOperator   # A_b(θ_AB, θ_CD) family       (Phase B)
    ActiveInferenceLoop             # alternating inner+outer dynamics  (Phase D)

Relationship to chapter prose
-----------------------------
- ch07-information.tex §7.5: defines T² and the doublet structure.
- ch04-fact-types.tex: fact types A, B (Kähler doublet) and C, D (gauge doublet).
- ch18-quantum.tex §Reduced Dynamics: inner-outer loop framing.
- ch02-operator.tex §Cross-Scale Specialization (Consciousness Scale):
  "Minimization over ρ gives the Lindblad dissipation. Minimization over θ
  gives the frame dynamics (active inference)."

Locked design decisions (see archive/plans/2026-04-26-active-inference/PLAN.md):
    A1 — A_b(θ) explicit form via principled-toy stipulation
    A2 — outer-loop θ via gradient descent (finite differences)
    A3 — inner-outer alternating, N inner steps per outer step
    A4 — Tier 2 coupling: shared environment
    A5 — Φ > 0 assumed, not computed

Section: active (Tier 1 + Tier 2 implemented: TensorProductBasis, partial_trace,
        ParameterizedBoundaryOperator, ActiveInferenceLoop, FrameFindingLoop,
        TwoBoundaryActiveInferenceLoop, run_decoherence_race; validated by
        ppm.verify active-inference checks and tests/test_active_inference.py)
"""

from __future__ import annotations

import numpy as np

from .dynamics import (
    Basis, Density, Operator,
    free_hamiltonian, lindblad_step,
)


# ─── TensorProductBasis ──────────────────────────────────────────────────────

class TensorProductBasis:
    """
    Hilbert space as the tensor product of two Basis objects.

    Indexing convention: the global index i corresponds to (i_S, i_env) via
    i = i_S * env.total_dim + i_env. This is the standard "row-major" tensor
    product layout consistent with numpy reshape conventions.

    Attributes
    ----------
    basis_S : Basis
    basis_env : Basis
    total_dim : int
        Equal to basis_S.total_dim * basis_env.total_dim.

    Notes
    -----
    The tensor product treats the two Bases as distinguishable subsystems. For
    the active-inference application, basis_S is the boundary's interior
    Hilbert space and basis_env is the environment that gets traced out.

    For the Tier 2 multi-boundary case (Phase G), this can be nested:
    TensorProductBasis(TensorProductBasis(B1, B2), env). The flat composition
    still works because total_dim is just the product.
    """

    def __init__(self, basis_S, basis_env):
        # Allow either Basis or TensorProductBasis on either side
        self.basis_S = basis_S
        self.basis_env = basis_env
        self.total_dim = basis_S.total_dim * basis_env.total_dim

    def __repr__(self) -> str:
        return (f"TensorProductBasis("
                f"basis_S={self.basis_S.total_dim}-dim, "
                f"basis_env={self.basis_env.total_dim}-dim, "
                f"total={self.total_dim})")

    # ─── Index conversions ────────────────────────────────────────────────────

    def to_global(self, i_S: int, i_env: int) -> int:
        """Convert subsystem indices (i_S, i_env) to a global basis index."""
        return i_S * self.basis_env.total_dim + i_env

    def from_global(self, i: int) -> tuple[int, int]:
        """Inverse of to_global: returns (i_S, i_env)."""
        D_env = self.basis_env.total_dim
        return divmod(i, D_env)

    # ─── State construction helpers ───────────────────────────────────────────

    def product_state(self, psi_S: np.ndarray, psi_env: np.ndarray) -> np.ndarray:
        """
        Build the global vector |ψ_S⟩ ⊗ |ψ_env⟩ from subsystem state vectors.

        Returns a complex column vector of length total_dim.
        """
        psi_S = np.asarray(psi_S, dtype=np.complex128).reshape(-1)
        psi_env = np.asarray(psi_env, dtype=np.complex128).reshape(-1)
        if psi_S.shape[0] != self.basis_S.total_dim:
            raise ValueError(
                f"psi_S length {psi_S.shape[0]} != basis_S.total_dim "
                f"{self.basis_S.total_dim}"
            )
        if psi_env.shape[0] != self.basis_env.total_dim:
            raise ValueError(
                f"psi_env length {psi_env.shape[0]} != basis_env.total_dim "
                f"{self.basis_env.total_dim}"
            )
        return np.kron(psi_S, psi_env)

    def product_density(self, rho_S: Density, rho_env: Density) -> Density:
        """
        Build the global ρ = ρ_S ⊗ ρ_env from subsystem densities.

        Returns a Density on the joint basis.
        """
        if rho_S.basis is not self.basis_S and rho_S.matrix.shape[0] != self.basis_S.total_dim:
            raise ValueError("rho_S basis mismatch")
        if rho_env.basis is not self.basis_env and rho_env.matrix.shape[0] != self.basis_env.total_dim:
            raise ValueError("rho_env basis mismatch")
        joint = np.kron(rho_S.matrix, rho_env.matrix)
        return Density(self, joint)


# ─── Partial trace ───────────────────────────────────────────────────────────

def partial_trace(rho_total: Density, joint_basis: TensorProductBasis,
                  trace_out: str = 'env') -> Density:
    """
    Trace out one subsystem from a density matrix on a TensorProductBasis.

    Parameters
    ----------
    rho_total : Density
        Density matrix on the joint basis (basis_S ⊗ basis_env).
    joint_basis : TensorProductBasis
        The TensorProductBasis describing the subsystem decomposition.
    trace_out : {'env', 'S'}
        Which subsystem to trace out. 'env' returns the reduced density
        matrix on basis_S; 'S' returns it on basis_env.

    Returns
    -------
    Density on the retained subsystem's Basis.

    Notes
    -----
    Standard partial-trace implementation: reshape the density matrix into a
    rank-4 tensor (D_S, D_env, D_S, D_env), then contract the subsystem to be
    traced out. The trace is preserved: Tr(rho_reduced) = Tr(rho_total).
    """
    if rho_total.matrix.shape[0] != joint_basis.total_dim:
        raise ValueError(
            f"rho_total has dim {rho_total.matrix.shape[0]} but joint_basis "
            f"has total_dim {joint_basis.total_dim}"
        )
    D_S = joint_basis.basis_S.total_dim
    D_env = joint_basis.basis_env.total_dim

    # Reshape into rank-4 tensor with index order (i_S, i_env, j_S, j_env)
    M = rho_total.matrix.reshape(D_S, D_env, D_S, D_env)

    if trace_out == 'env':
        # Trace over env indices (axes 1 and 3)
        rho_S = np.einsum('iaja->ij', M)
        return Density(joint_basis.basis_S, rho_S)
    elif trace_out == 'S':
        # Trace over S indices (axes 0 and 2)
        rho_env = np.einsum('aiaj->ij', M)
        return Density(joint_basis.basis_env, rho_env)
    else:
        raise ValueError(f"trace_out must be 'env' or 'S', got {trace_out!r}")


# ─── ParameterizedBoundaryOperator ───────────────────────────────────────────
#
# A1 (locked): the actualization operator at frame θ ∈ T² is the rank-2
# orthogonal projector onto the doublet-rotated states:
#
#     A_b(θ_AB, θ_CD) = |ψ_K(θ_AB)⟩⟨ψ_K(θ_AB)|
#                       + |ψ_G(θ_CD)⟩⟨ψ_G(θ_CD)|
#
# where:
#     |ψ_K(θ_AB)⟩ = cos(θ_AB) |A⟩ + sin(θ_AB) |B⟩       (Kähler doublet rotation)
#     |ψ_G(θ_CD)⟩ = cos(θ_CD) |C⟩ + sin(θ_CD) |D⟩       (gauge doublet rotation)
#
# |A⟩, |B⟩ are the basis vectors representing fact types A, B (Kähler doublet,
# SU(3)-triplet sector of U(3) isotropy irrep per ch07-information §7.5).
# |C⟩, |D⟩ are the basis vectors for fact types C, D (gauge doublet,
# singlet/chiral sector). All four are orthogonal τ-even basis vectors.
#
# Properties:
#     A_b(θ)² = A_b(θ)            (idempotent — orthogonal projector)
#     A_b(θ)† = A_b(θ)            (Hermitian)
#     Tr(A_b(θ)) = 2              (rank-2 always)
#     A_b(0, 0) = |A⟩⟨A| + |C⟩⟨C|             (pure spectral + chiral readout)
#     A_b(π/2, π/2) = |B⟩⟨B| + |D⟩⟨D|         (pure spatial + intensity readout)
#     A_b(π/4, π/4) = balanced superposition readout
#
# At each θ the operator is a candidate Lindblad jump operator. As θ evolves
# via the outer-loop active-inference dynamics, the channel "tilts" between
# different fact-type readouts.
#
# Reference: archive/plans/2026-04-26-active-inference/PLAN.md decision A1.
# Toy basis assignment for |A⟩, |B⟩, |C⟩, |D⟩ uses four consecutive τ-even
# modes at k=1; canonical isotropy-irrep alignment flagged as item AI-1.


def default_doublet_indices(basis: Basis) -> tuple[int, int, int, int]:
    """
    A1 toy stipulation: return four consecutive τ-even basis indices at k=1
    representing fact types (A, B, C, D).

    Requires basis.k_max ≥ 1 and at least 4 τ-even modes at k=1. At k=1 there
    are 9 τ-even modes (d_k⁺ = 9), so this always succeeds for k_max ≥ 1.

    Returns
    -------
    (idx_A, idx_B, idx_C, idx_D) : tuple of int
        Global basis indices, all τ-even.
    """
    if basis.k_max < 1:
        raise ValueError(
            "default_doublet_indices requires k_max >= 1 "
            "(need at least 4 τ-even modes at k=1)"
        )
    start = basis.first_plus_index(1)
    # k=1 has 9 τ-even modes — plenty for the 4 we need
    return (start, start + 1, start + 2, start + 3)


def parameterized_boundary_operator(basis: Basis,
                                    doublet_indices: tuple[int, int, int, int],
                                    theta_AB: float,
                                    theta_CD: float) -> Operator:
    """
    Construct the θ-parameterized actualization operator A_b(θ_AB, θ_CD).

    Returns the rank-2 projector onto the doublet-rotated states:
        A_b(θ) = |ψ_K(θ_AB)⟩⟨ψ_K(θ_AB)| + |ψ_G(θ_CD)⟩⟨ψ_G(θ_CD)|

    See module docstring for the geometric framing.

    Parameters
    ----------
    basis : Basis
    doublet_indices : (idx_A, idx_B, idx_C, idx_D)
        Global indices of the four τ-even basis vectors representing the
        Kähler doublet (A, B) and the gauge doublet (C, D). All four must
        be distinct and all four must be τ-even.
    theta_AB : float
        Angle in [0, π/2] parameterizing the Kähler doublet rotation.
        0 = pure Type A readout, π/2 = pure Type B readout.
    theta_CD : float
        Angle in [0, π/2] parameterizing the gauge doublet rotation.
        0 = pure Type C readout, π/2 = pure Type D readout.

    Returns
    -------
    Operator
        Rank-2 Hermitian idempotent projector A_b(θ).

    Raises
    ------
    ValueError
        If any doublet index is not τ-even or if indices are not distinct.
    """
    idx_A, idx_B, idx_C, idx_D = doublet_indices
    indices = [idx_A, idx_B, idx_C, idx_D]

    if len(set(indices)) != 4:
        raise ValueError(f"doublet indices must be distinct, got {indices}")

    for label, idx in zip(['A', 'B', 'C', 'D'], indices):
        if not 0 <= idx < basis.total_dim:
            raise ValueError(
                f"doublet index {label}={idx} out of range "
                f"[0, {basis.total_dim})"
            )
        if basis.tau_parity[idx] != +1:
            raise ValueError(
                f"doublet index {label}={idx} is not τ-even "
                f"(parity = {basis.tau_parity[idx]})"
            )

    # Build the two doublet-rotated basis vectors
    psi_K = np.zeros(basis.total_dim, dtype=np.complex128)
    psi_K[idx_A] = np.cos(theta_AB)
    psi_K[idx_B] = np.sin(theta_AB)

    psi_G = np.zeros(basis.total_dim, dtype=np.complex128)
    psi_G[idx_C] = np.cos(theta_CD)
    psi_G[idx_D] = np.sin(theta_CD)

    # A_b(θ) = |ψ_K⟩⟨ψ_K| + |ψ_G⟩⟨ψ_G|
    matrix = np.outer(psi_K, np.conj(psi_K)) + np.outer(psi_G, np.conj(psi_G))
    return Operator(basis, matrix)


# ─── Free energy at θ + gradient ─────────────────────────────────────────────
#
# The actualization free energy at frame θ is
#     F[ρ, θ] = -log Tr[A_b(θ) ρ A_b(θ)†]
# and the outer-loop active-inference dynamics descend ∂F/∂θ.
#
# A2 (locked): gradient computed via central finite differences. Analytical
# gradient is feasible (A_b(θ) is a closed-form rotation-conjugate) and could
# replace this if numerical performance becomes an issue.


def free_energy_at_theta(rho: Density, basis: Basis,
                         doublet_indices: tuple[int, int, int, int],
                         theta_AB: float, theta_CD: float) -> float:
    """
    Evaluate F[ρ, θ] = -log Tr[A_b(θ) ρ A_b(θ)†].

    Returns +inf when the yield is zero (ρ has no support in the doublet
    subspace at this θ).

    For a pure state |A⟩⟨A| at θ_CD = 0, the closed form is
    F(θ_AB) = -log(cos²(θ_AB)). This is a useful analytical reference for
    the test suite.
    """
    A = parameterized_boundary_operator(basis, doublet_indices,
                                         theta_AB, theta_CD)
    P = float(A.apply_to(rho).trace().real)
    if P <= 1e-15:
        return float('inf')
    return float(-np.log(P))


def gradient_F_theta(rho: Density, basis: Basis,
                     doublet_indices: tuple[int, int, int, int],
                     theta_AB: float, theta_CD: float,
                     h: float = 1e-4) -> np.ndarray:
    """
    Central-difference gradient of F[ρ, θ] in (θ_AB, θ_CD).

    Returns a 2-element ndarray [∂F/∂θ_AB, ∂F/∂θ_CD].

    Step size h defaults to 1e-4 which gives ~6-digit accuracy on smooth
    F surfaces. Reduce h if higher accuracy is needed; increase if F is
    numerically noisy near a singular point.

    Returns NaN entries if F is +inf at the sample points (gradient
    undefined at singularities).
    """
    F_pp = free_energy_at_theta(rho, basis, doublet_indices,
                                 theta_AB + h, theta_CD)
    F_mp = free_energy_at_theta(rho, basis, doublet_indices,
                                 theta_AB - h, theta_CD)
    F_pc = free_energy_at_theta(rho, basis, doublet_indices,
                                 theta_AB, theta_CD + h)
    F_mc = free_energy_at_theta(rho, basis, doublet_indices,
                                 theta_AB, theta_CD - h)

    if any(np.isinf(v) for v in [F_pp, F_mp, F_pc, F_mc]):
        return np.array([float('nan'), float('nan')])

    grad_AB = (F_pp - F_mp) / (2.0 * h)
    grad_CD = (F_pc - F_mc) / (2.0 * h)
    return np.array([grad_AB, grad_CD])


# ─── ActiveInferenceLoop ─────────────────────────────────────────────────────
#
# Couples the inner-loop Lindblad dynamics on ρ to the outer-loop gradient
# descent on θ. Per A3 (locked), the scheme is alternating: N inner steps
# at fixed θ, then one outer step that updates θ given the current ρ.
#
# Pseudocode for one cycle:
#     for i in range(N_inner):
#         A_b = parameterized_boundary_operator(basis, doublet, θ_AB, θ_CD)
#         ρ ← lindblad_step(ρ, H_α, [A_b], [γ], dt)
#     ∇F = gradient_F_theta(ρ, basis, doublet, θ_AB, θ_CD)
#     θ_AB ← θ_AB - η * ∇F[0]
#     θ_CD ← θ_CD - η * ∇F[1]
#     record (t, ρ, θ, F[ρ, θ])
#
# At convergence, ρ has equilibrated under the Lindblad with current θ AND
# θ has stopped moving (gradient near zero).
#
# Section: ch02-operator.tex §Cross-Scale Specialization Consciousness Scale
#         ch18-quantum.tex §Reduced Dynamics
#         archive/plans/2026-04-26-active-inference/PLAN.md decisions A3, A2


class ActiveInferenceLoop:
    """
    Coupled inner/outer active-inference dynamics on a single boundary.

    Maintains state (ρ, θ_AB, θ_CD) and exposes:
        inner_evolve(n_steps) : runs n Lindblad steps at the current θ
        outer_step()          : one gradient-descent step on θ at current ρ
        run_cycle()           : N inner steps + 1 outer step + record
        run(n_cycles)         : repeat run_cycle() and return trajectory

    The trajectory is a list of dicts with keys:
        't', 'rho', 'theta_AB', 'theta_CD', 'F'

    Defaults are tuned for the k_max = 1 toy: dt = 0.05, gamma = 1.0,
    eta = 0.05, N_inner = 20.

    Parameters
    ----------
    rho_init : Density
    theta_init : (float, float)
    basis : Basis
    doublet_indices : (int, int, int, int)
    H : Operator, optional
        Hamiltonian. Default: free_hamiltonian(basis).
    gamma : float, optional
        Lindblad rate for the (single) jump operator A_b(θ). Default 1.0.
    dt : float, optional
        Inner-loop RK4 timestep. Default 0.05.
    eta : float, optional
        Outer-loop gradient-descent step size. Default 0.05.
    N_inner : int, optional
        Number of inner steps per outer step. Default 20.
    grad_h : float, optional
        Finite-difference step for the θ gradient. Default 1e-4.
    """

    def __init__(self, rho_init: Density, theta_init: tuple[float, float],
                 basis: Basis,
                 doublet_indices: tuple[int, int, int, int],
                 H: Operator = None,
                 gamma: float = 1.0,
                 dt: float = 0.05,
                 eta: float = 0.05,
                 N_inner: int = 20,
                 grad_h: float = 1e-4):
        self.basis = basis
        self.doublet_indices = doublet_indices
        self.H = H if H is not None else free_hamiltonian(basis)
        self.gamma = gamma
        self.dt = dt
        self.eta = eta
        self.N_inner = N_inner
        self.grad_h = grad_h

        self.rho = rho_init
        self.theta_AB, self.theta_CD = theta_init
        self.t = 0.0

        # Trajectory log; first entry is the initial state.
        self.trajectory = []
        self._record()

    def _A_b_current(self) -> Operator:
        """Build the current A_b(θ) jump operator at this loop's θ."""
        return parameterized_boundary_operator(
            self.basis, self.doublet_indices,
            self.theta_AB, self.theta_CD)

    def _record(self):
        F = free_energy_at_theta(self.rho, self.basis, self.doublet_indices,
                                  self.theta_AB, self.theta_CD)
        self.trajectory.append({
            't': self.t,
            'rho': self.rho,
            'theta_AB': self.theta_AB,
            'theta_CD': self.theta_CD,
            'F': F,
        })

    def inner_evolve(self, n_steps: int = None):
        """Run n_steps Lindblad steps at the current θ."""
        n = n_steps if n_steps is not None else self.N_inner
        A = self._A_b_current()
        for _ in range(n):
            self.rho = lindblad_step(self.rho, self.H, [A], [self.gamma],
                                      self.dt)
            self.t += self.dt

    def outer_step(self):
        """One gradient-descent step on θ at the current ρ."""
        grad = gradient_F_theta(self.rho, self.basis, self.doublet_indices,
                                 self.theta_AB, self.theta_CD,
                                 h=self.grad_h)
        if not np.any(np.isnan(grad)):
            # Project the angle update so θ stays within [0, π/2]
            new_AB = self.theta_AB - self.eta * float(grad[0])
            new_CD = self.theta_CD - self.eta * float(grad[1])
            # Clip to the closed torus quadrant; small ε buffer to avoid
            # exact-singularity points where F → inf
            eps = 1e-6
            self.theta_AB = float(np.clip(new_AB, eps, np.pi/2 - eps))
            self.theta_CD = float(np.clip(new_CD, eps, np.pi/2 - eps))

    def run_cycle(self):
        """One inner_evolve + one outer_step + record snapshot."""
        self.inner_evolve()
        self.outer_step()
        self._record()

    def run(self, n_cycles: int):
        """Run n_cycles of (inner + outer). Returns the trajectory list."""
        for _ in range(n_cycles):
            self.run_cycle()
        return self.trajectory

    def converged(self, F_tol: float = 1e-3,
                  grad_tol: float = 1e-2,
                  window: int = 5) -> bool:
        """
        Heuristic convergence check.

        True if (a) the gradient magnitude at the current state is below
        grad_tol AND (b) F has changed less than F_tol over the last `window`
        recorded snapshots.
        """
        if len(self.trajectory) < window + 1:
            return False
        grad = gradient_F_theta(self.rho, self.basis, self.doublet_indices,
                                 self.theta_AB, self.theta_CD,
                                 h=self.grad_h)
        if np.any(np.isnan(grad)) or float(np.linalg.norm(grad)) > grad_tol:
            return False
        recent_F = [s['F'] for s in self.trajectory[-window:]]
        return (max(recent_F) - min(recent_F)) < F_tol


# ─── TwoBoundarySystem ───────────────────────────────────────────────────────
#
# Tier 2 multi-boundary structure with shared environment.
#
# Hilbert space:  H_S1 ⊗ H_S2 ⊗ H_env
# Two boundaries B1, B2 each with their own (ρ_i, θ_i). Coupling between them
# arises from a shared environment: both trace out the same H_env, producing
# correlated decoherence on (ρ_1, ρ_2). Per A4 (locked).
#
# This operationalizes ch18-quantum §Reduced Dynamics's claim that "the
# probabilistic Markov property of ch:boundaries and the dynamical Markov
# property of the master equation are the same property at different levels
# of description."
#
# Reference: archive/plans/2026-04-26-active-inference/PLAN.md decision A4.


class TwoBoundarySystem:
    """
    Three-way tensor product H_S1 ⊗ H_S2 ⊗ H_env with reduced-density helpers.

    Index convention: i_global = (i_S1, i_S2, i_env) flattened row-major
    via i_global = ((i_S1 * D_S2) + i_S2) * D_env + i_env.

    Attributes
    ----------
    basis_S1, basis_S2, basis_env : Basis
    total_dim : int
        D_S1 * D_S2 * D_env.
    joint_basis_full : TensorProductBasis
        Equivalent to TensorProductBasis(TensorProductBasis(S1, S2), env);
        treats (S1 ⊗ S2) as the "system" half of a two-way decomposition
        with env as the other half. This makes partial-tracing env trivial.
    """

    def __init__(self, basis_S1, basis_S2, basis_env):
        self.basis_S1 = basis_S1
        self.basis_S2 = basis_S2
        self.basis_env = basis_env
        # Build nested two-way decompositions for partial-trace operations
        self._S12 = TensorProductBasis(basis_S1, basis_S2)
        self.joint_basis_full = TensorProductBasis(self._S12, basis_env)
        self.total_dim = self.joint_basis_full.total_dim

    def __repr__(self) -> str:
        return (f"TwoBoundarySystem(S1={self.basis_S1.total_dim}, "
                f"S2={self.basis_S2.total_dim}, "
                f"env={self.basis_env.total_dim}, "
                f"total={self.total_dim})")

    # ─── Constructors ─────────────────────────────────────────────────────────

    def product_density(self, rho_S1: Density, rho_S2: Density,
                         rho_env: Density) -> Density:
        """Build ρ = ρ_S1 ⊗ ρ_S2 ⊗ ρ_env on the joint basis."""
        rho_S12 = self._S12.product_density(rho_S1, rho_S2)
        return self.joint_basis_full.product_density(rho_S12, rho_env)

    # ─── Reduced densities ────────────────────────────────────────────────────

    def reduced_S1S2(self, rho_total: Density) -> Density:
        """Trace out env. Returns ρ on S1 ⊗ S2."""
        return partial_trace(rho_total, self.joint_basis_full,
                              trace_out='env')

    def reduced_env(self, rho_total: Density) -> Density:
        """Trace out S1 and S2. Returns ρ on env."""
        return partial_trace(rho_total, self.joint_basis_full,
                              trace_out='S')

    def reduced_S1(self, rho_total: Density) -> Density:
        """Trace out env and S2. Returns ρ on S1."""
        rho_S12 = self.reduced_S1S2(rho_total)
        return partial_trace(rho_S12, self._S12, trace_out='env')
        # Note: for partial_trace's API, env is the second factor;
        # here that's basis_S2, which we trace out.

    def reduced_S2(self, rho_total: Density) -> Density:
        """Trace out env and S1. Returns ρ on S2."""
        rho_S12 = self.reduced_S1S2(rho_total)
        return partial_trace(rho_S12, self._S12, trace_out='S')


# ─── FrameFindingLoop (canonical demo: adaptive frame discovery) ────────────
#
# Pure outer-loop active inference: given a fixed (held) ρ that the system
# treats as a black-box external state, adapt θ via gradient descent on
# F[ρ, θ] to find the measurement frame that maximizes Born yield.
#
# This isolates the frame-discovery mechanism — no inner Lindblad loop, no
# state evolution. It answers: "given an unknown state, how does an active-
# inference system discover the right way to look at it?"
#
# Validates against analytical optima:
#   ρ = |ψ_K(α)⟩⟨ψ_K(α)|       → optimal θ_AB = α
#   ρ = (1/2)(|A⟩⟨A| + |B⟩⟨B|) → flat F over θ_AB (symmetric mixture)
#   ρ = pure |A⟩⟨A|             → optimal θ_AB = 0


class FrameFindingLoop:
    """
    Outer-loop-only active inference for adaptive measurement frame discovery.

    Given a fixed external state ρ, repeatedly compute ∇F[ρ, θ] and step
    θ in the descent direction. The state is NOT evolved (no inner Lindblad).

    Optional Gaussian step noise (`noise_sigma > 0`) makes the descent
    stochastic — closer to what realistic outer-loop dynamics look like
    when the underlying Lindblad firings are themselves stochastic. Default
    noise_sigma=0 keeps the deterministic-descent behavior.

    Convergence: θ → θ* that maximizes Tr[A_b(θ*) ρ A_b(θ*)†] = minimizes F.

    Parameters
    ----------
    rho_target : Density
        The fixed external state to find a frame for.
    theta_init : (float, float)
        Starting (θ_AB, θ_CD).
    basis : Basis
    doublet_indices : (int, int, int, int)
    eta : float
        Gradient-descent step size. Default 0.05.
    grad_h : float
        Finite-difference step. Default 1e-4.
    noise_sigma : float
        Execution noise: Gaussian noise added to the position step after
        the gradient decision. Cannot be averaged away by gradient
        aggregation. Default 0.0 (deterministic).
    signal_noise_sigma : float
        Perception noise: Gaussian noise added to each gradient sample
        before averaging. Reduces by √N under aggregation. Default 0.0.
    N_aggregate : int
        Number of gradient samples to average per step. N=1 is naive
        single-shot gradient descent. N>1 implements Φ-style aggregation
        (see ch18-consciousness.tex §Active Inference at the Consciousness
        Scale). Default 1.
    seed : int
        RNG seed for noise reproducibility. Default 0.
    """

    def __init__(self,
                 rho_target: Density,
                 theta_init: tuple[float, float],
                 basis: Basis,
                 doublet_indices: tuple[int, int, int, int],
                 eta: float = 0.05,
                 grad_h: float = 1e-4,
                 noise_sigma: float = 0.0,
                 signal_noise_sigma: float = 0.0,
                 N_aggregate: int = 1,
                 seed: int = 0):
        """
        Parameters
        ----------
        ...
        noise_sigma : float
            Execution noise: Gaussian noise added to the position step.
            Cannot be averaged away by gradient aggregation (it acts after
            the step decision). Models environmental fluctuations.
        signal_noise_sigma : float
            Perception noise: Gaussian noise added to each gradient sample
            before averaging. Reduces by √N under aggregation. Models the
            stochastic firing of underlying Lindblad events that produce the
            gradient signal.
        N_aggregate : int
            Number of gradient samples to average per step. N=1 is naive
            single-shot gradient descent (existing behavior). N>1 implements
            Φ-style aggregation: at the framework's R ≈ 1 boundary
            (k_consciousness ≈ 75), individual events carry near-zero
            information; aggregating ~10⁴ correlated firings is the
            framework's prescribed mechanism for extracting usable signal.
            See ch18-consciousness.tex §Active Inference at the
            Consciousness Scale.
        seed : int
            RNG seed for noise reproducibility.
        """
        if N_aggregate < 1:
            raise ValueError("N_aggregate must be at least 1")
        self.rho = rho_target
        self.basis = basis
        self.doublet_indices = doublet_indices
        self.eta = eta
        self.grad_h = grad_h
        self.noise_sigma = noise_sigma
        self.signal_noise_sigma = signal_noise_sigma
        self.N_aggregate = N_aggregate
        self.rng = np.random.default_rng(seed)
        self.theta_AB, self.theta_CD = theta_init

        self.trajectory = []
        self._record(step=0)

    def _record(self, step: int):
        F = free_energy_at_theta(self.rho, self.basis, self.doublet_indices,
                                  self.theta_AB, self.theta_CD)
        self.trajectory.append({
            'step': step,
            'theta_AB': self.theta_AB,
            'theta_CD': self.theta_CD,
            'F': F,
        })

    def step(self):
        # Sample gradient N_aggregate times with optional perception noise.
        # Averaging reduces perception noise by √N (Φ-style aggregation).
        grads = []
        for _ in range(self.N_aggregate):
            grad = gradient_F_theta(self.rho, self.basis,
                                     self.doublet_indices,
                                     self.theta_AB, self.theta_CD,
                                     h=self.grad_h)
            if np.any(np.isnan(grad)):
                continue
            if self.signal_noise_sigma > 0:
                grad = grad + self.rng.normal(
                    0.0, self.signal_noise_sigma, size=2)
            grads.append(grad)

        if not grads:
            return

        avg_grad = np.mean(grads, axis=0)
        eps = 1e-6
        new_AB = self.theta_AB - self.eta * float(avg_grad[0])
        new_CD = self.theta_CD - self.eta * float(avg_grad[1])
        # Execution noise: cannot be averaged away by gradient aggregation
        if self.noise_sigma > 0:
            new_AB += float(self.rng.normal(0.0, self.noise_sigma))
            new_CD += float(self.rng.normal(0.0, self.noise_sigma))
        self.theta_AB = float(np.clip(new_AB, eps, np.pi/2 - eps))
        self.theta_CD = float(np.clip(new_CD, eps, np.pi/2 - eps))

    def run(self, n_steps: int):
        for i in range(1, n_steps + 1):
            self.step()
            self._record(step=i)
        return self.trajectory


# ─── RandomFrameWalk (baseline for frame-finding contest) ──────────────────
#
# Pure-noise frame search: at each step θ wanders randomly without any
# gradient information. Demonstrates the contribution of gradient-driven
# active inference by contrast — the random walker has the same step budget
# but no directional signal.


class RandomFrameWalk:
    """
    Random-walk baseline for frame search.

    At each step, θ takes a Gaussian random step (clipped to T²). No use of
    F or its gradient — the walker has no idea where the optimum is.

    Same API surface as FrameFindingLoop so figures can swap them in/out.

    Parameters
    ----------
    rho_target : Density
    theta_init : (float, float)
    basis : Basis
    doublet_indices : (int, int, int, int)
    step_size : float
        Standard deviation of the Gaussian step. Default 0.05 (matches
        FrameFindingLoop's default eta scale).
    seed : int
        RNG seed for reproducibility.
    """

    def __init__(self,
                 rho_target: Density,
                 theta_init: tuple[float, float],
                 basis: Basis,
                 doublet_indices: tuple[int, int, int, int],
                 step_size: float = 0.05,
                 seed: int = 42):
        self.rho = rho_target
        self.basis = basis
        self.doublet_indices = doublet_indices
        self.step_size = step_size
        self.rng = np.random.default_rng(seed)
        self.theta_AB, self.theta_CD = theta_init

        self.trajectory = []
        self._record(step=0)

    def _record(self, step: int):
        F = free_energy_at_theta(self.rho, self.basis, self.doublet_indices,
                                  self.theta_AB, self.theta_CD)
        self.trajectory.append({
            'step': step,
            'theta_AB': self.theta_AB,
            'theta_CD': self.theta_CD,
            'F': F,
        })

    def step(self):
        eps = 1e-6
        d_AB = float(self.rng.normal(0.0, self.step_size))
        d_CD = float(self.rng.normal(0.0, self.step_size))
        self.theta_AB = float(np.clip(self.theta_AB + d_AB,
                                       eps, np.pi/2 - eps))
        self.theta_CD = float(np.clip(self.theta_CD + d_CD,
                                       eps, np.pi/2 - eps))

    def run(self, n_steps: int):
        for i in range(1, n_steps + 1):
            self.step()
            self._record(step=i)
        return self.trajectory


# ─── Decoherence race (canonical demo: selective advantage of adaptation) ───
#
# Compare two single-boundary trajectories under identical Lindblad dynamics:
#   Passive: θ frozen at the (random) initial value.
#   Active:  θ adapts via gradient descent (standard ActiveInferenceLoop).
#
# Both start from the same ρ_0 and use the same A_b family. The only
# difference is whether θ updates. Outcome metric: time-averaged F (lower =
# better aligned with actuality = "fitter" in the natural-selection sense).
#
# This operationalizes the framework's claim that active inference confers a
# selective advantage: systems that adapt their measurement frame to incoming
# data maintain lower free energy than passive systems whose frame is fixed.


def run_decoherence_race(rho_0: Density,
                          theta_init: tuple[float, float],
                          basis: Basis,
                          doublet_indices: tuple[int, int, int, int],
                          gamma: float = 0.5,
                          dt: float = 0.05,
                          N_inner: int = 10,
                          n_cycles: int = 60,
                          eta_active: float = 0.05) -> dict:
    """
    Run paired passive (η=0) and active (η>0) trajectories from the same
    initial state with the same Lindblad parameters.

    Returns a dict with both trajectories and summary metrics:
        {
            'passive_traj': [snapshots],
            'active_traj':  [snapshots],
            'mean_F_passive': float,
            'mean_F_active':  float,
            'fitness_advantage': mean_F_passive - mean_F_active,
        }

    Positive `fitness_advantage` means the active system maintained lower
    F on average — the selective-advantage signal.
    """
    passive = ActiveInferenceLoop(
        rho_0, theta_init, basis, doublet_indices,
        gamma=gamma, dt=dt, N_inner=N_inner, eta=0.0)
    active = ActiveInferenceLoop(
        rho_0, theta_init, basis, doublet_indices,
        gamma=gamma, dt=dt, N_inner=N_inner, eta=eta_active)

    passive.run(n_cycles=n_cycles)
    active.run(n_cycles=n_cycles)

    # Time-averaged F (skip +inf entries)
    def _mean_F(traj):
        vals = [s['F'] for s in traj if not (s['F'] == float('inf'))]
        return float(sum(vals) / len(vals)) if vals else float('inf')

    mean_F_passive = _mean_F(passive.trajectory)
    mean_F_active = _mean_F(active.trajectory)

    return {
        'passive_traj': passive.trajectory,
        'active_traj': active.trajectory,
        'mean_F_passive': mean_F_passive,
        'mean_F_active': mean_F_active,
        'fitness_advantage': mean_F_passive - mean_F_active,
    }


def fitness_vs_eta_sweep(rho_0: Density,
                          theta_init: tuple[float, float],
                          basis: Basis,
                          doublet_indices: tuple[int, int, int, int],
                          etas: list[float],
                          gamma: float = 0.5,
                          dt: float = 0.05,
                          N_inner: int = 10,
                          n_cycles: int = 60) -> dict:
    """
    Sweep η across a range and return mean-F per η. Demonstrates the
    selective-advantage gradient: faster adaptation → lower mean-F → fitter.

    Returns:
        {'etas': [...], 'mean_F': [...]}
    """
    mean_Fs = []
    for eta in etas:
        loop = ActiveInferenceLoop(
            rho_0, theta_init, basis, doublet_indices,
            gamma=gamma, dt=dt, N_inner=N_inner, eta=float(eta))
        loop.run(n_cycles=n_cycles)
        vals = [s['F'] for s in loop.trajectory
                if not (s['F'] == float('inf'))]
        mean_Fs.append(float(sum(vals) / len(vals)) if vals else float('inf'))
    return {'etas': list(etas), 'mean_F': mean_Fs}


# Note: an earlier draft of this module included a `run_natural_selection`
# function that simulated populations of agents with reproduction, mutation,
# and selection. That work was pulled back as out of scope for the active
# framework: PPM derives the cost gradient F[ρ, θ], not the evolutionary
# mechanism that climbs it. Per the anti-woo principle in
# .claude/skills/ppm-theory/SKILL.md, "biology EXPLOITS conditions created by
# the variational principle. Active inference is something biology DOES."
# The cost gradient is the framework's contribution; what climbs it lives
# downstream. See `fitness_vs_eta_sweep` above for the framework-native
# demonstration.


# ─── TwoBoundaryActiveInferenceLoop ─────────────────────────────────────────
#
# Joint dynamics on H_S1 ⊗ H_S2 (no explicit environment) with shared-
# environment Lindblad coupling. The shared environment is implicit: tracing
# out an explicit H_env after Born-Markov reduction gives a Lindblad on
# H_S1 ⊗ H_S2 with jump operators of the form L = L_1 + L_2 where L_i acts
# on subsystem S_i. Cross terms L_1 ρ L_2† in the dissipator are the
# operational signature of shared-environment correlation.
#
# Coupling parameter α ∈ [0, 1] interpolates:
#   α = 0  : two independent local jump operators, no cross terms.
#   α = 1  : single shared jump operator L = L_1 + L_2, full cross terms.
#   0 < α < 1 : convex combination of independent and shared.
#
# Each boundary maintains its own (ρ_i, θ_i). Outer-loop θ-gradient at each
# boundary is computed at the MARGINAL ρ_i = partial_trace(rho_total, S_other).
# This is the canonical active-inference form when the boundary has only
# local access to its own state, even though the joint dynamics is correlated.


def _embed_S1(op_local, basis_S2):
    """Embed an operator on S1 as op_local ⊗ I_S2 on the joint S1 ⊗ S2 basis."""
    D2 = basis_S2.total_dim
    eye_S2 = np.eye(D2, dtype=np.complex128)
    return np.kron(op_local.matrix, eye_S2)


def _embed_S2(op_local, basis_S1):
    """Embed an operator on S2 as I_S1 ⊗ op_local on the joint basis."""
    D1 = basis_S1.total_dim
    eye_S1 = np.eye(D1, dtype=np.complex128)
    return np.kron(eye_S1, op_local.matrix)


def shared_environment_jump_operators(joint_basis: TensorProductBasis,
                                       A_b1_local: Operator,
                                       A_b2_local: Operator,
                                       gamma: float,
                                       alpha: float
                                       ) -> tuple[list[Operator], list[float]]:
    """
    Build the joint Lindblad jump operators implementing the shared-environment
    coupling between two boundaries.

    Returns (A_ops, gammas) suitable for `lindblad_step(rho_joint, H, A_ops,
    gammas, dt)`.

    Form (joint-detection coupling)
    -------------------------------
    Three operators on the joint H_S1 ⊗ H_S2:
        L_local_1 = A_b1 ⊗ I_S2          with rate (1 − α) γ
        L_local_2 = I_S1 ⊗ A_b2          with rate (1 − α) γ
        L_cross   = A_b1 ⊗ A_b2          with rate α γ

    α = 0 → independent local channels (no cross correlations).
    α = 1 → only the joint-detection channel (full cross correlations).
    0 < α < 1 → convex combination.

    Why the joint-detection form
    ----------------------------
    A naive "shared bath" choice L = L_1 + L_2 produces correlations in the
    JOINT state but its cross terms cancel exactly under partial trace, so
    the marginal ρ_1 = Tr_2(ρ) evolves identically to the α=0 case. The
    outer-loop θ-gradient sees only the marginal, so no coordination signal
    reaches θ from a sum-form coupling.

    The product-form L_cross = A_b1 ⊗ A_b2 has cross-marginal effect:
        Tr_2(L_cross ρ L_cross†) for product ρ = ρ_1 ⊗ ρ_2 gives
        ⟨A_b2 ρ_2 A_b2⟩ · A_b1 ρ_1 A_b1
    so the rate of A_b1's effective dissipation on ρ_1 is modulated by
    ⟨A_b2⟩_{ρ_2}. This is the operational signature of coordinated
    decoherence: ρ_1's evolution depends on ρ_2's state through the
    joint-detection probability, and vice versa.

    Both forms are physically realizable shared-environment scenarios; they
    correspond to different microscopic models (collective dephasing vs.
    coincidence detection). For demonstrating emergent coordination the
    joint-detection form is the operative one.

    Parameters
    ----------
    joint_basis : TensorProductBasis
        TensorProductBasis(basis_S1, basis_S2).
    A_b1_local : Operator on basis_S1
    A_b2_local : Operator on basis_S2
    gamma : float
        Total Lindblad rate scale.
    alpha : float
        Coupling fraction in [0, 1].
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha must be in [0, 1], got {alpha}")
    if gamma <= 0.0:
        raise ValueError(f"gamma must be positive, got {gamma}")

    # Embeddings of local operators
    L1_mat = _embed_S1(A_b1_local, joint_basis.basis_env)  # S2 in naming
    L2_mat = _embed_S2(A_b2_local, joint_basis.basis_S)    # S1 in naming
    # Joint-detection cross operator: A_b1 ⊗ A_b2 directly
    L_cross_mat = np.kron(A_b1_local.matrix, A_b2_local.matrix)

    L1 = Operator(joint_basis, L1_mat)
    L2 = Operator(joint_basis, L2_mat)
    L_cross = Operator(joint_basis, L_cross_mat)

    A_ops = [L1, L2, L_cross]
    gammas = [(1.0 - alpha) * gamma, (1.0 - alpha) * gamma, alpha * gamma]
    return A_ops, gammas


class TwoBoundaryActiveInferenceLoop:
    """
    Coupled active-inference dynamics on two boundaries with shared-environment
    Lindblad coupling.

    State maintained: (ρ_joint on S1 ⊗ S2, θ_1_AB, θ_1_CD, θ_2_AB, θ_2_CD).

    Each cycle:
        1. Build current jump operators A_b1(θ_1), A_b2(θ_2) and their
           shared-environment embedding via shared_environment_jump_operators.
        2. Run N_inner Lindblad RK4 steps on ρ_joint.
        3. Compute marginal ρ_1 = partial_trace(ρ_joint over S2).
        4. Compute marginal ρ_2 = partial_trace(ρ_joint over S1).
        5. Update θ_1 via gradient descent on F[ρ_1, θ_1].
        6. Update θ_2 via gradient descent on F[ρ_2, θ_2].
        7. Record snapshot.

    Each boundary uses local information (its own marginal ρ_i) to update
    its own θ_i. Coupling between the boundaries flows entirely through the
    joint Lindblad dynamics (which mixes ρ_1 and ρ_2 via the shared-env
    cross terms).

    The order parameter for "coordination" is |θ_1_AB − θ_2_AB| (and same
    for CD): if the boundaries coordinate, these distances shrink.
    """

    def __init__(self,
                 rho_joint_init: Density,
                 theta_1_init: tuple[float, float],
                 theta_2_init: tuple[float, float],
                 basis_S1: Basis, basis_S2: Basis,
                 doublet_S1: tuple[int, int, int, int],
                 doublet_S2: tuple[int, int, int, int],
                 H_S1: Operator = None,
                 H_S2: Operator = None,
                 gamma: float = 1.0,
                 alpha: float = 0.5,
                 dt: float = 0.05,
                 eta: float = 0.05,
                 N_inner: int = 20,
                 grad_h: float = 1e-4):
        self.basis_S1 = basis_S1
        self.basis_S2 = basis_S2
        self.joint_basis = TensorProductBasis(basis_S1, basis_S2)
        self.doublet_S1 = doublet_S1
        self.doublet_S2 = doublet_S2

        # Joint Hamiltonian: H_S1 ⊗ I_S2 + I_S1 ⊗ H_S2
        H_S1 = H_S1 if H_S1 is not None else free_hamiltonian(basis_S1)
        H_S2 = H_S2 if H_S2 is not None else free_hamiltonian(basis_S2)
        H_joint_mat = (_embed_S1(H_S1, basis_S2)
                       + _embed_S2(H_S2, basis_S1))
        self.H = Operator(self.joint_basis, H_joint_mat)

        self.gamma = gamma
        self.alpha = alpha
        self.dt = dt
        self.eta = eta
        self.N_inner = N_inner
        self.grad_h = grad_h

        self.rho = rho_joint_init
        self.theta_1_AB, self.theta_1_CD = theta_1_init
        self.theta_2_AB, self.theta_2_CD = theta_2_init
        self.t = 0.0

        self.trajectory = []
        self._record()

    def _A_b1_current(self) -> Operator:
        return parameterized_boundary_operator(
            self.basis_S1, self.doublet_S1,
            self.theta_1_AB, self.theta_1_CD)

    def _A_b2_current(self) -> Operator:
        return parameterized_boundary_operator(
            self.basis_S2, self.doublet_S2,
            self.theta_2_AB, self.theta_2_CD)

    def _record(self):
        rho_1 = partial_trace(self.rho, self.joint_basis, trace_out='env')
        rho_2 = partial_trace(self.rho, self.joint_basis, trace_out='S')
        F_1 = free_energy_at_theta(rho_1, self.basis_S1, self.doublet_S1,
                                    self.theta_1_AB, self.theta_1_CD)
        F_2 = free_energy_at_theta(rho_2, self.basis_S2, self.doublet_S2,
                                    self.theta_2_AB, self.theta_2_CD)
        self.trajectory.append({
            't': self.t,
            'rho_joint': self.rho,
            'rho_1': rho_1,
            'rho_2': rho_2,
            'theta_1_AB': self.theta_1_AB,
            'theta_1_CD': self.theta_1_CD,
            'theta_2_AB': self.theta_2_AB,
            'theta_2_CD': self.theta_2_CD,
            'F_1': F_1,
            'F_2': F_2,
        })

    def inner_evolve(self, n_steps: int = None):
        n = n_steps if n_steps is not None else self.N_inner
        A_b1 = self._A_b1_current()
        A_b2 = self._A_b2_current()
        A_ops, gammas = shared_environment_jump_operators(
            self.joint_basis, A_b1, A_b2, self.gamma, self.alpha)
        for _ in range(n):
            self.rho = lindblad_step(self.rho, self.H, A_ops, gammas, self.dt)
            self.t += self.dt

    def outer_step(self):
        rho_1 = partial_trace(self.rho, self.joint_basis, trace_out='env')
        rho_2 = partial_trace(self.rho, self.joint_basis, trace_out='S')

        grad_1 = gradient_F_theta(
            rho_1, self.basis_S1, self.doublet_S1,
            self.theta_1_AB, self.theta_1_CD, h=self.grad_h)
        grad_2 = gradient_F_theta(
            rho_2, self.basis_S2, self.doublet_S2,
            self.theta_2_AB, self.theta_2_CD, h=self.grad_h)

        eps = 1e-6

        if not np.any(np.isnan(grad_1)):
            self.theta_1_AB = float(np.clip(
                self.theta_1_AB - self.eta * float(grad_1[0]),
                eps, np.pi/2 - eps))
            self.theta_1_CD = float(np.clip(
                self.theta_1_CD - self.eta * float(grad_1[1]),
                eps, np.pi/2 - eps))
        if not np.any(np.isnan(grad_2)):
            self.theta_2_AB = float(np.clip(
                self.theta_2_AB - self.eta * float(grad_2[0]),
                eps, np.pi/2 - eps))
            self.theta_2_CD = float(np.clip(
                self.theta_2_CD - self.eta * float(grad_2[1]),
                eps, np.pi/2 - eps))

    def run_cycle(self):
        self.inner_evolve()
        self.outer_step()
        self._record()

    def run(self, n_cycles: int):
        for _ in range(n_cycles):
            self.run_cycle()
        return self.trajectory

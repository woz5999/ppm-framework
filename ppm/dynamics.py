"""
ppm.dynamics — Lindblad dynamical infrastructure for the actualization channel
==============================================================================

Numerical implementation of the actualization Lindblad dynamics analytically
derived in archive/scripts/actualization_operator.py and documented in
core/ontology/ch08-variational.tex and core/technical/ch18-quantum.tex.

Provides:
    Basis      : truncated CP³ spectral basis with τ-parity tracking
    Density    : density matrices on a Basis (positivity, trace, expectation)
    Operator   : bounded operators (Phase 2)
    lindblad_* : evolution functions (Phase 3)

Theoretical setting
-------------------
CP³ Laplacian eigenspaces V_k carry the τ involution; each V_k decomposes as
V_k = V_k⁺ ⊕ V_k⁻ where:
    V_k⁺ : τ-even subspace, RP³-compatible content (the "actuality" sector)
    V_k⁻ : τ-odd subspace, off-stratum content (the "imaginary" sector)

Spectral data (eigenvalues, dimensions) come from `consciousness.cp3_spectral_data`,
which is the active-framework promotion of the analytical derivation.

Truncation convention
---------------------
A `Basis(k_max)` allocates the direct sum ⊕_{k=0}^{k_max} V_k. The total
Hilbert dimension is Σ_k d_k, which grows quickly:
    k_max = 2  →  total_dim =   100
    k_max = 3  →  total_dim =   400
    k_max = 4  →  total_dim =  1225

For development we default to k_max = 2 (total_dim = 100), which is large enough
to demonstrate Lindblad dynamics and validate Born-rule emergence while staying
numerically light.

Locked design decisions (see archive/plans/2026-04-26-route-b-lindblad/PLAN.md
and NOTES.md):
    D2 — A_b operators built as projections onto specific (k, α) τ-even modes
    D3 — H_α is the free CP³ Laplacian only (no Kähler potential at this stage)

Section: ch08-variational §Actualization Free Energy
        ch18-quantum    §Hamiltonian Architecture
Status: active (Phases 1-5 complete; validated by ppm.verify Lindblad checks
        and tests/test_dynamics.py)
"""

from __future__ import annotations

import numpy as np

from .consciousness import cp3_spectral_data


# ─── Basis ───────────────────────────────────────────────────────────────────

class Basis:
    """
    Truncated spectral basis for the CP³ Hilbert space.

    For each k = 0..k_max, allocates d_k⁺ τ-even basis vectors followed by
    d_k⁻ τ-odd basis vectors. Within each k-block, the first d_k⁺ indices are
    τ-even (parity +1) and the remaining d_k⁻ are τ-odd (parity −1).

    This convention makes the τ-projector operator block-diagonal and trivially
    diagonal within each block (1 on +1-parity indices, 0 on −1-parity).

    Attributes
    ----------
    k_max : int
        Maximum eigenspace index included in the truncation.
    total_dim : int
        Total Hilbert space dimension Σ_k d_k.
    spectral_data : list of dict
        Per-k spectral information from `cp3_spectral_data(k_max)`.
    k_blocks : list of (k, start_index, dim_plus, dim_minus, eigenvalue) tuples
        Block descriptors. Block k occupies indices [start, start+dim_plus+dim_minus).
    tau_parity : np.ndarray of shape (total_dim,)
        +1 or −1 per basis index.
    eigenvalues : np.ndarray of shape (total_dim,)
        Laplacian eigenvalue λ_k = k(k+3) per basis index (dimensionless).
    k_index : np.ndarray of shape (total_dim,)
        k-level per basis index.

    Examples
    --------
    >>> b = Basis(k_max=2)
    >>> b.total_dim
    100
    >>> int((b.tau_parity == +1).sum())  # τ-even subspace dimension
    55
    >>> int((b.tau_parity == -1).sum())  # τ-odd subspace dimension
    45
    """

    def __init__(self, k_max: int = 2):
        if k_max < 0:
            raise ValueError("k_max must be non-negative")
        self.k_max = k_max
        self.spectral_data = cp3_spectral_data(k_max)

        # Build per-index arrays
        parities = []
        eigenvalues = []
        k_index = []
        k_blocks = []

        running_index = 0
        for entry in self.spectral_data:
            k = entry['k']
            d_plus = entry['d_plus']
            d_minus = entry['d_minus']
            lam = entry['eigenvalue']

            block_start = running_index
            # τ-even indices first, then τ-odd
            parities.extend([+1] * d_plus + [-1] * d_minus)
            eigenvalues.extend([lam] * (d_plus + d_minus))
            k_index.extend([k] * (d_plus + d_minus))

            k_blocks.append((k, block_start, d_plus, d_minus, lam))
            running_index += d_plus + d_minus

        self.total_dim = running_index
        self.k_blocks = k_blocks
        self.tau_parity = np.array(parities, dtype=np.int8)
        self.eigenvalues = np.array(eigenvalues, dtype=np.float64)
        self.k_index = np.array(k_index, dtype=np.int32)

    # ─── Convenience accessors ────────────────────────────────────────────────

    @property
    def dim_plus(self) -> int:
        """Total τ-even subspace dimension."""
        return int((self.tau_parity == +1).sum())

    @property
    def dim_minus(self) -> int:
        """Total τ-odd subspace dimension."""
        return int((self.tau_parity == -1).sum())

    def block(self, k: int) -> tuple[int, int, int, int, int]:
        """Return (k, start, dim_plus, dim_minus, eigenvalue) for level k."""
        for entry in self.k_blocks:
            if entry[0] == k:
                return entry
        raise ValueError(f"k = {k} not in this basis (k_max = {self.k_max})")

    def basis_vector(self, index: int) -> np.ndarray:
        """Return the index-th basis vector as a column vector of shape (total_dim,)."""
        if not 0 <= index < self.total_dim:
            raise IndexError(f"index {index} out of range [0, {self.total_dim})")
        v = np.zeros(self.total_dim, dtype=np.complex128)
        v[index] = 1.0
        return v

    def first_plus_index(self, k: int) -> int:
        """Return the global index of the first τ-even basis vector at level k."""
        _, start, d_plus, _, _ = self.block(k)
        if d_plus == 0:
            raise ValueError(f"V_{k}⁺ is empty (no τ-even modes at level {k})")
        return start

    def first_minus_index(self, k: int) -> int:
        """Return the global index of the first τ-odd basis vector at level k."""
        _, start, d_plus, d_minus, _ = self.block(k)
        if d_minus == 0:
            raise ValueError(f"V_{k}⁻ is empty (no τ-odd modes at level {k})")
        return start + d_plus

    def __repr__(self) -> str:
        return (f"Basis(k_max={self.k_max}, total_dim={self.total_dim}, "
                f"dim_plus={self.dim_plus}, dim_minus={self.dim_minus})")


# ─── Density ─────────────────────────────────────────────────────────────────

class Density:
    """
    Density matrix on a `Basis`.

    Stores a complex matrix of shape (basis.total_dim, basis.total_dim).
    A valid quantum state satisfies:
        ρ = ρ†       (Hermitian)
        ρ ≥ 0        (positive semidefinite)
        Tr(ρ) = 1    (normalized)

    Constructors enforce these by construction; arithmetic operations may not.
    Use `is_hermitian`, `is_positive`, `trace` to check.

    Attributes
    ----------
    basis : Basis
        The basis this density matrix lives on.
    matrix : np.ndarray of shape (total_dim, total_dim), complex128
        The density matrix in the basis ordering.
    """

    def __init__(self, basis: Basis, matrix: np.ndarray):
        if matrix.shape != (basis.total_dim, basis.total_dim):
            raise ValueError(
                f"matrix shape {matrix.shape} does not match basis "
                f"({basis.total_dim}, {basis.total_dim})"
            )
        self.basis = basis
        self.matrix = matrix.astype(np.complex128)

    # ─── Constructors ─────────────────────────────────────────────────────────

    @classmethod
    def zero(cls, basis: Basis) -> "Density":
        """Zero matrix (not a valid quantum state — Tr = 0)."""
        return cls(basis, np.zeros((basis.total_dim, basis.total_dim),
                                    dtype=np.complex128))

    @classmethod
    def maximally_mixed(cls, basis: Basis) -> "Density":
        """Maximally mixed state ρ = I / D."""
        D = basis.total_dim
        return cls(basis, np.eye(D, dtype=np.complex128) / D)

    @classmethod
    def pure(cls, basis: Basis, state_vector: np.ndarray) -> "Density":
        """
        Pure state ρ = |ψ⟩⟨ψ| / ⟨ψ|ψ⟩.

        Accepts an unnormalized state vector and normalizes it.
        """
        psi = np.asarray(state_vector, dtype=np.complex128).reshape(-1)
        if psi.shape[0] != basis.total_dim:
            raise ValueError(
                f"state vector length {psi.shape[0]} does not match "
                f"basis dim {basis.total_dim}"
            )
        norm_sq = float(np.real(np.vdot(psi, psi)))
        if norm_sq <= 0:
            raise ValueError("cannot build pure state from zero vector")
        psi = psi / np.sqrt(norm_sq)
        rho = np.outer(psi, np.conj(psi))
        return cls(basis, rho)

    @classmethod
    def thermal(cls, basis: Basis, temperature_units: float = 1.0) -> "Density":
        """
        Thermal state ρ = exp(−H/T) / Z where H is diagonal in the basis with
        eigenvalues equal to the Laplacian eigenvalues k(k+3). The temperature
        is in the same dimensionless units.

        At high T this approaches the maximally mixed state; at low T it
        concentrates on the k=0 sector (which is purely τ-even).

        Parameters
        ----------
        temperature_units : float
            Temperature in dimensionless units of λ_k = k(k+3). Must be > 0.
        """
        if temperature_units <= 0:
            raise ValueError("temperature must be positive")
        beta = 1.0 / temperature_units
        weights = np.exp(-beta * basis.eigenvalues)
        weights = weights / weights.sum()
        return cls(basis, np.diag(weights.astype(np.complex128)))

    # ─── Validation methods ───────────────────────────────────────────────────

    def trace(self) -> complex:
        """Return Tr(ρ). For valid normalized states this equals 1."""
        return complex(np.trace(self.matrix))

    def is_hermitian(self, atol: float = 1e-10) -> bool:
        """True if ρ = ρ† to within tolerance."""
        return bool(np.allclose(self.matrix, self.matrix.conj().T, atol=atol))

    def is_positive(self, atol: float = 1e-10) -> bool:
        """True if all eigenvalues of ρ are ≥ −atol."""
        # Symmetrize to avoid spurious complex eigenvalues from roundoff
        herm = 0.5 * (self.matrix + self.matrix.conj().T)
        eigs = np.linalg.eigvalsh(herm)
        return bool(eigs.min() >= -atol)

    def normalize(self) -> "Density":
        """Return a new Density with Tr(ρ) rescaled to 1."""
        tr = self.trace()
        if abs(tr) < 1e-15:
            raise ValueError("cannot normalize: trace is zero")
        return Density(self.basis, self.matrix / tr)

    # ─── Quantities ───────────────────────────────────────────────────────────

    def expectation(self, operator_matrix: np.ndarray) -> complex:
        """Return Tr(O ρ) for a given operator matrix."""
        return complex(np.trace(operator_matrix @ self.matrix))

    def tau_odd_weight(self) -> float:
        """
        Return the total weight ρ assigns to the τ-odd subspace V⁻.

        Equals Tr(P⁻ ρ) where P⁻ is the projector onto V⁻ (diagonal with 1
        on −1-parity indices, 0 elsewhere). For a normalized state this is
        in [0, 1] and represents the off-stratum imaginary content carried
        by ρ — the quantity the actualization free energy F = −log P
        measures.
        """
        diag = np.real(np.diag(self.matrix))
        mask = (self.basis.tau_parity == -1)
        return float(diag[mask].sum())

    def tau_even_weight(self) -> float:
        """Return the total weight ρ assigns to the τ-even subspace V⁺."""
        diag = np.real(np.diag(self.matrix))
        mask = (self.basis.tau_parity == +1)
        return float(diag[mask].sum())

    # ─── Dunder ───────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (f"Density(basis={self.basis!r}, "
                f"trace={self.trace().real:.4f}, "
                f"tau_odd_weight={self.tau_odd_weight():.4f})")


# ─── Operator ────────────────────────────────────────────────────────────────

class Operator:
    """
    Bounded linear operator on a `Basis`.

    Stores a complex matrix of shape (basis.total_dim, basis.total_dim).
    Supports arithmetic (+, −, scalar *), composition (@ for AB), adjoint,
    commutator/anticommutator, and action on `Density` via `apply_to`.

    No positivity or self-adjointness is enforced at construction; use
    `is_hermitian()` to check when needed.

    Attributes
    ----------
    basis : Basis
    matrix : np.ndarray, complex128
    """

    def __init__(self, basis: Basis, matrix: np.ndarray):
        if matrix.shape != (basis.total_dim, basis.total_dim):
            raise ValueError(
                f"matrix shape {matrix.shape} does not match basis "
                f"({basis.total_dim}, {basis.total_dim})"
            )
        self.basis = basis
        self.matrix = matrix.astype(np.complex128)

    # ─── Algebra ──────────────────────────────────────────────────────────────

    def adjoint(self) -> "Operator":
        """Return A† = (A*)ᵀ."""
        return Operator(self.basis, self.matrix.conj().T)

    def __matmul__(self, other: "Operator") -> "Operator":
        """Operator product A @ B."""
        if not isinstance(other, Operator):
            return NotImplemented
        if other.basis is not self.basis and other.basis.total_dim != self.basis.total_dim:
            raise ValueError("operator bases mismatch")
        return Operator(self.basis, self.matrix @ other.matrix)

    def __add__(self, other: "Operator") -> "Operator":
        if not isinstance(other, Operator):
            return NotImplemented
        return Operator(self.basis, self.matrix + other.matrix)

    def __sub__(self, other: "Operator") -> "Operator":
        if not isinstance(other, Operator):
            return NotImplemented
        return Operator(self.basis, self.matrix - other.matrix)

    def __mul__(self, scalar) -> "Operator":
        """Scalar multiplication: A * c."""
        return Operator(self.basis, self.matrix * scalar)

    def __rmul__(self, scalar) -> "Operator":
        """Scalar multiplication: c * A."""
        return Operator(self.basis, scalar * self.matrix)

    def __neg__(self) -> "Operator":
        return Operator(self.basis, -self.matrix)

    def commutator(self, other: "Operator") -> "Operator":
        """[A, B] = AB − BA."""
        return Operator(self.basis,
                        self.matrix @ other.matrix - other.matrix @ self.matrix)

    def anticommutator(self, other: "Operator") -> "Operator":
        """{A, B} = AB + BA."""
        return Operator(self.basis,
                        self.matrix @ other.matrix + other.matrix @ self.matrix)

    # ─── Properties ───────────────────────────────────────────────────────────

    def is_hermitian(self, atol: float = 1e-10) -> bool:
        """True if A = A† to within tolerance."""
        return bool(np.allclose(self.matrix, self.matrix.conj().T, atol=atol))

    def trace(self) -> complex:
        """Tr(A)."""
        return complex(np.trace(self.matrix))

    # ─── Action ───────────────────────────────────────────────────────────────

    def apply_to(self, rho: Density) -> Density:
        """
        Return A ρ A† as a new Density (without normalization).

        For a Lindblad jump operator A_b, this gives the unnormalized
        post-jump density. The actual jump probability is Tr(A ρ A†) and
        the normalized post-jump state is A ρ A† / Tr(A ρ A†).
        """
        if rho.basis is not self.basis and rho.basis.total_dim != self.basis.total_dim:
            raise ValueError("operator and density bases mismatch")
        new = self.matrix @ rho.matrix @ self.matrix.conj().T
        return Density(self.basis, new)

    def expectation(self, rho: Density) -> complex:
        """Tr(A ρ) — the expectation value of A in state ρ."""
        return complex(np.trace(self.matrix @ rho.matrix))

    # ─── Dunder ───────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (f"Operator(basis={self.basis!r}, "
                f"trace={self.trace().real:.4f}, "
                f"hermitian={self.is_hermitian()})")


# ─── Pre-built operators ─────────────────────────────────────────────────────

def tau_projector(basis: Basis) -> Operator:
    """
    The global τ-projector Â = projection onto V⁺ = ⊕_k V_k⁺.

    Diagonal in the basis: 1 on indices with parity +1, 0 on parity −1.
    Properties:
        Â² = Â                  (idempotent)
        Â† = Â                  (Hermitian)
        Tr(Â) = dim_plus        (rank equals τ-even dimension)
        [Â, H_α] = 0            (since τ is an isometry of the metric)

    This operator represents the actualization channel as a single global
    object. Per-boundary operators A_b are built by `boundary_operator`.

    Section: ch08-variational §Actualization Free Energy
            archive/scripts/actualization_operator.py items (i)–(iii)
    """
    diag = np.where(basis.tau_parity == +1, 1.0, 0.0).astype(np.complex128)
    return Operator(basis, np.diag(diag))


def free_hamiltonian(basis: Basis) -> Operator:
    """
    Free CP³ Laplacian Hamiltonian H_α (D3 default form: free Laplacian only).

    Diagonal in the harmonic basis with eigenvalues λ_k = k(k+3) (the CP³
    Laplacian spectrum on the Fubini–Study metric of unit radius squared).

    Returned in dimensionless units: H[i,i] = k_index[i] * (k_index[i] + 3).
    Physical conversion to SI energy is:
        E_k = (ℏ² / (2 m_eff R²)) × λ_k
    where m_eff = m_π and R² = 10 (Fubini–Study radius squared from
    `constants.R_SQUARED`). An SI-units helper can be added when needed.

    Properties:
        H_α† = H_α              (Hermitian)
        [H_α, Â] = 0            (commutes with τ-projector)
        spectrum = {k(k+3) : k = 0..k_max}, with multiplicities d_k

    Relationship to chapter prose
    -----------------------------
    ch18-quantum §Hamiltonian Architecture states the full form of H_α as
    the Schrödinger operator on CP³ with both the Laplacian and the Kähler
    potential. This implementation returns the Laplacian piece only — a
    deliberate simplification (D3 default per
    archive/plans/2026-04-26-route-b-lindblad/PLAN.md). The Kähler
    contribution is omitted because the analytical claims this module
    validates (Born-rule emergence, Penrose–Diósi decoherence rate,
    quantum Zeno regime, trace/positivity preservation under the Lindblad
    flow) do not depend on it. Adding the Kähler term is a Phase 6 item
    if/when downstream figures or chapter results require it.

    Section: ch18-quantum §Hamiltonian Architecture
            archive/scripts/actualization_operator.py item (ii) commutators
    """
    diag = basis.eigenvalues.astype(np.complex128)
    return Operator(basis, np.diag(diag))


def boundary_operator(basis: Basis, mode_index: int) -> Operator:
    """
    Rank-1 boundary actualization operator A_b (D2 mode-projection convention).

    Each "boundary" b is identified with a single τ-even basis mode. The
    operator A_b is the rank-1 orthogonal projector onto that mode:
        A_b = |b⟩⟨b|     where |b⟩ is the b-th τ-even basis vector.

    Properties:
        A_b² = A_b              (idempotent)
        A_b† = A_b              (Hermitian)
        Σ_{b in V⁺} A_b = Â     (the τ-even projectors sum to the global
                                 τ-projector)
        [A_b, A_b'] = 0         for b ≠ b' (orthogonal rank-1 projectors)

    Parameters
    ----------
    basis : Basis
    mode_index : int
        Index into the τ-even subspace, 0 ≤ mode_index < basis.dim_plus.
        mode_index = 0 selects the first (lowest-k, first-α) τ-even mode.

    Notes
    -----
    The mode-projection convention defers spatial localization of boundaries
    to a higher-fidelity model. Locked as the Phase 2 default in
    archive/plans/2026-04-26-route-b-lindblad/PLAN.md (decision D2).

    Section: ch08-variational §Actualization Free Energy
            archive/scripts/actualization_operator.py items (i), (ii)
    """
    if not 0 <= mode_index < basis.dim_plus:
        raise IndexError(
            f"mode_index {mode_index} out of range "
            f"[0, dim_plus={basis.dim_plus})"
        )
    # Find the global basis index of the mode_index-th τ-even basis vector
    plus_indices = np.where(basis.tau_parity == +1)[0]
    global_idx = int(plus_indices[mode_index])

    matrix = np.zeros((basis.total_dim, basis.total_dim), dtype=np.complex128)
    matrix[global_idx, global_idx] = 1.0
    return Operator(basis, matrix)


def all_boundary_operators(basis: Basis) -> list[Operator]:
    """
    Return the full set of boundary operators {A_b : b ∈ τ-even modes}.

    Length equals basis.dim_plus. Sum equals tau_projector(basis).

    Convenience constructor for Lindblad evolution where Σ_b appears
    naturally in the dissipator.
    """
    return [boundary_operator(basis, i) for i in range(basis.dim_plus)]


# ─── Lindblad evolution ──────────────────────────────────────────────────────
#
# The actualization channel obeys the GKLS / Lindblad master equation:
#
#     dρ/dt = -i/ℏ [H, ρ] + Σ_b γ_b ( A_b ρ A_b† − ½ {A_b†A_b, ρ} )
#
# where H is the unitary Hamiltonian, A_b are jump operators (boundary
# actualization operators), and γ_b ≥ 0 are the corresponding rates.
#
# For the actualization channel each A_b is a Hermitian rank-1 projector
# (D2 mode-projection convention), so A_b† = A_b and A_b†A_b = A_b. The
# dissipator simplifies to γ_b ( A_b ρ A_b − ½{A_b, ρ} ), but the general
# Lindblad form is implemented here so the same machinery can later carry
# non-Hermitian or non-idempotent jump operators if Phase 6 needs them.
#
# All evolution functions accept a `hbar` parameter so the same code can run
# in dimensionless units (default ℏ=1, used for development and Phase 1–5
# tests) or SI units (set ℏ = HBAR_SI from constants.py for matching against
# Penrose–Diósi rates in physical seconds).
#
# Section: ch08-variational §Actualization Free Energy
#         ch18-quantum    §Hamiltonian Architecture
#         archive/scripts/actualization_operator.py "LINDBLAD DYNAMICS"


def _lindblad_rhs_matrix(rho_m: np.ndarray, H_m: np.ndarray,
                         A_matrices: list[np.ndarray],
                         gammas: list[float],
                         hbar: float) -> np.ndarray:
    """
    Pure-matrix Lindblad right-hand side. Returns dρ/dt as a complex matrix.

    Caller is responsible for matching shapes and unit conventions. This is
    the inner loop; user-facing API is `lindblad_rhs`.
    """
    drho = -1j / hbar * (H_m @ rho_m - rho_m @ H_m)
    for A, gamma in zip(A_matrices, gammas):
        Adag = A.conj().T
        AdagA = Adag @ A
        drho = drho + gamma * (
            A @ rho_m @ Adag
            - 0.5 * (AdagA @ rho_m + rho_m @ AdagA)
        )
    return drho


def lindblad_rhs(rho: Density, H: Operator,
                 A_ops: list[Operator],
                 gammas: list[float],
                 hbar: float = 1.0) -> np.ndarray:
    """
    Compute dρ/dt under the Lindblad master equation.

    Returns the time derivative as a complex matrix (not a Density —
    intermediate dρ/dt values are not states themselves).

    Parameters
    ----------
    rho : Density
        Current state.
    H : Operator
        Hamiltonian.
    A_ops : list of Operator
        Lindblad jump operators.
    gammas : list of float
        Rates for each jump operator. Must match length of A_ops.
    hbar : float
        Reduced Planck constant in the units being used (default 1.0 for
        dimensionless evolution).

    Returns
    -------
    np.ndarray of shape (basis.total_dim, basis.total_dim), complex128.
    """
    if len(A_ops) != len(gammas):
        raise ValueError(
            f"length mismatch: {len(A_ops)} A_ops vs {len(gammas)} gammas"
        )
    A_matrices = [A.matrix for A in A_ops]
    return _lindblad_rhs_matrix(rho.matrix, H.matrix,
                                A_matrices, list(gammas), hbar)


def lindblad_step(rho: Density, H: Operator,
                  A_ops: list[Operator],
                  gammas: list[float],
                  dt: float,
                  hbar: float = 1.0) -> Density:
    """
    Advance ρ by one timestep dt using fourth-order Runge–Kutta (RK4).

    Returns a new Density (does NOT mutate the input). Intermediate matrices
    are not validated as states — RK4 evaluates dρ/dt at non-state points.
    Validity (trace, positivity, Hermiticity) is preserved by the Lindblad
    structure to within numerical accuracy; check the returned Density if
    you need to confirm.

    Parameters
    ----------
    rho : Density
    H : Operator
    A_ops : list of Operator
    gammas : list of float
    dt : float
        Timestep in the same units as 1/γ and 1/ω. For RK4 stability with
        Hamiltonian H, dt should satisfy roughly dt × ω_max < 2 where
        ω_max is the largest H eigenvalue/ℏ.
    hbar : float, default 1.0
    """
    if len(A_ops) != len(gammas):
        raise ValueError(
            f"length mismatch: {len(A_ops)} A_ops vs {len(gammas)} gammas"
        )
    A_matrices = [A.matrix for A in A_ops]
    H_m = H.matrix
    rho_m = rho.matrix

    def f(m):
        return _lindblad_rhs_matrix(m, H_m, A_matrices, list(gammas), hbar)

    k1 = f(rho_m)
    k2 = f(rho_m + 0.5 * dt * k1)
    k3 = f(rho_m + 0.5 * dt * k2)
    k4 = f(rho_m + dt * k3)
    new_m = rho_m + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return Density(rho.basis, new_m)


def lindblad_evolve(rho_0: Density, H: Operator,
                    A_ops: list[Operator],
                    gammas: list[float],
                    T: float,
                    n_steps: int,
                    snapshots: list[int] = None,
                    hbar: float = 1.0) -> list[tuple[float, Density]]:
    """
    Evolve ρ from t=0 to t=T using `n_steps` RK4 steps of size dt = T/n_steps.

    Returns a trajectory: a list of (time, Density) tuples at the requested
    snapshot step indices. By default, snapshots = [0, n_steps] (initial and
    final state only).

    For trajectory analysis (e.g., fitting a decoherence rate), pass an
    explicit list of step indices.

    Parameters
    ----------
    rho_0 : Density
        Initial state.
    H : Operator
    A_ops : list of Operator
    gammas : list of float
    T : float
        Total evolution time.
    n_steps : int
        Number of RK4 steps. dt = T / n_steps.
    snapshots : list of int, optional
        Step indices at which to record the state. Indices in [0, n_steps].
        If None, defaults to [0, n_steps].
    hbar : float, default 1.0

    Returns
    -------
    list of (time, Density) tuples, sorted by time.
    """
    if T <= 0:
        raise ValueError("T must be positive")
    if n_steps < 1:
        raise ValueError("n_steps must be at least 1")

    if snapshots is None:
        snapshots = [0, n_steps]
    snapshots = sorted(set(snapshots))
    for s in snapshots:
        if not 0 <= s <= n_steps:
            raise ValueError(f"snapshot step {s} out of range [0, {n_steps}]")

    dt = T / n_steps
    history = []
    rho = rho_0
    if 0 in snapshots:
        history.append((0.0, rho))

    snapshot_set = set(snapshots)
    for step in range(1, n_steps + 1):
        rho = lindblad_step(rho, H, A_ops, gammas, dt, hbar=hbar)
        if step in snapshot_set:
            history.append((step * dt, rho))

    return history


# ─── Yield and free-energy helpers ───────────────────────────────────────────


def yield_distribution(rho: Density, A_ops: list[Operator]) -> dict:
    """
    Return {b: P_b} where P_b = Tr(A_b ρ A_b†) is the actualization yield
    for jump operator b.

    For Hermitian rank-1 projectors A_b = |b⟩⟨b|, this reduces to the
    diagonal element ρ_{bb}. For more general A_b it gives the standard
    quantum-channel transition probability.

    The yield distribution is the Born-rule probability over which
    boundary operator fires next.
    """
    return {
        b: float(np.real(np.trace(A.matrix @ rho.matrix @ A.matrix.conj().T)))
        for b, A in enumerate(A_ops)
    }


def free_energy(rho: Density, A_ops: list[Operator],
                agg: str = 'max') -> float:
    """
    Actualization free energy F = -log P, aggregated across the operator set.

    Aggregation modes:
        'max'  : F = -log(max_b P_b)        — the easiest available firing
        'mean' : F = -log(mean_b P_b)       — symmetric average
        'sum'  : F = -log(sum_b P_b)        — total τ-even support
                                              (= -log Tr(P⁺ ρ) when A_ops
                                               is the full mode-projector
                                               family)

    The mode of aggregation is a modeling choice. For a single-event
    actualization the per-operator F_b = -log P_b is the relevant quantity;
    a global F is an aggregate summary used in figures and dashboards.
    """
    yields = yield_distribution(rho, A_ops)
    values = list(yields.values())
    if agg == 'max':
        P = max(values)
    elif agg == 'mean':
        P = sum(values) / len(values)
    elif agg == 'sum':
        P = sum(values)
    else:
        raise ValueError(f"unknown agg mode: {agg!r} "
                         "(use 'max', 'mean', or 'sum')")
    if P <= 0:
        return float('inf')
    return float(-np.log(P))

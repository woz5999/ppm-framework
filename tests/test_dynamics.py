"""
ppm.dynamics — Phase 1 test suite (Basis + Density)

Tests:
    Basis dimensions match cp3_spectral_data totals.
    Maximally mixed Density: Tr=1, positive, Hermitian.
    Pure τ-even basis vector: tau_odd_weight = 0.
    Pure τ-odd basis vector: tau_odd_weight = 1.
    Superposition cos(θ)|+⟩ + sin(θ)|−⟩: tau_odd_weight = sin²(θ).
    Thermal state: positive, Hermitian, Tr=1, low-T concentration on k=0.
    Block accessor: returns correct (k, start, dim_plus, dim_minus, eigenvalue).

Section: ch08-variational §Actualization Free Energy
        ch18-quantum    §Hamiltonian Architecture
"""

import math
import unittest

import numpy as np

from ppm.consciousness import cp3_spectral_data
from ppm.dynamics import (
    Basis, Density, Operator,
    tau_projector, free_hamiltonian, boundary_operator, all_boundary_operators,
    lindblad_rhs, lindblad_step, lindblad_evolve,
    yield_distribution, free_energy,
)


class TestBasis(unittest.TestCase):

    def test_total_dim_matches_spectral_data(self):
        """Basis(k_max).total_dim equals Σ_k d_k from cp3_spectral_data."""
        for k_max in [0, 1, 2, 3]:
            with self.subTest(k_max=k_max):
                b = Basis(k_max=k_max)
                expected = sum(d['d_total'] for d in cp3_spectral_data(k_max))
                self.assertEqual(b.total_dim, expected)

    def test_dim_plus_minus_split(self):
        """dim_plus + dim_minus = total_dim and matches per-block totals."""
        b = Basis(k_max=2)
        self.assertEqual(b.dim_plus + b.dim_minus, b.total_dim)
        expected_plus = sum(d['d_plus'] for d in cp3_spectral_data(2))
        expected_minus = sum(d['d_minus'] for d in cp3_spectral_data(2))
        self.assertEqual(b.dim_plus, expected_plus)
        self.assertEqual(b.dim_minus, expected_minus)

    def test_k_max_2_concrete_dims(self):
        """At k_max=2, total_dim should be 100 with the known parity split."""
        b = Basis(k_max=2)
        # k=0:  d_plus=1, d_minus=0
        # k=1:  d_plus=9, d_minus=6
        # k=2:  d_plus=45, d_minus=39
        # totals: dim_plus = 55, dim_minus = 45, total = 100
        self.assertEqual(b.total_dim, 100)
        self.assertEqual(b.dim_plus, 55)
        self.assertEqual(b.dim_minus, 45)

    def test_block_accessor(self):
        """block(k) returns correct descriptor for each k in the basis."""
        b = Basis(k_max=2)
        # k=0 block
        k, start, dp, dm, lam = b.block(0)
        self.assertEqual((k, start, dp, dm, lam), (0, 0, 1, 0, 0))
        # k=1 block: starts after the k=0 block (1 vector)
        k, start, dp, dm, lam = b.block(1)
        self.assertEqual(k, 1)
        self.assertEqual(start, 1)
        self.assertEqual(dp, 9)
        self.assertEqual(dm, 6)
        self.assertEqual(lam, 4)
        # k=2 block: starts after k=0 (1) + k=1 (15) = 16
        k, start, dp, dm, lam = b.block(2)
        self.assertEqual((k, start, dp, dm, lam), (2, 16, 45, 39, 10))

    def test_block_out_of_range(self):
        """Asking for a k beyond k_max raises ValueError."""
        b = Basis(k_max=1)
        with self.assertRaises(ValueError):
            b.block(2)

    def test_basis_vector_canonical(self):
        """basis_vector(i) returns a unit vector with 1 at index i."""
        b = Basis(k_max=1)
        v = b.basis_vector(3)
        self.assertEqual(v.shape, (b.total_dim,))
        self.assertEqual(v[3], 1.0)
        self.assertEqual(np.sum(np.abs(v)), 1.0)

    def test_first_plus_minus_indices(self):
        """first_plus_index and first_minus_index point at the right parity."""
        b = Basis(k_max=2)
        # k=1 first plus index
        idx_plus = b.first_plus_index(1)
        self.assertEqual(b.tau_parity[idx_plus], +1)
        # k=1 first minus index = first plus + d_plus = 1 + 9 = 10
        idx_minus = b.first_minus_index(1)
        self.assertEqual(idx_minus, 10)
        self.assertEqual(b.tau_parity[idx_minus], -1)

    def test_first_minus_raises_when_empty(self):
        """k=0 has no τ-odd modes; first_minus_index should raise."""
        b = Basis(k_max=2)
        with self.assertRaises(ValueError):
            b.first_minus_index(0)

    def test_eigenvalues_per_index(self):
        """All indices in block k have eigenvalue = k(k+3)."""
        b = Basis(k_max=2)
        for k, start, dp, dm, lam in b.k_blocks:
            block_eigs = b.eigenvalues[start:start + dp + dm]
            self.assertTrue(np.all(block_eigs == lam))
            self.assertEqual(lam, k * (k + 3))

    def test_negative_k_max_raises(self):
        with self.assertRaises(ValueError):
            Basis(k_max=-1)


class TestDensity(unittest.TestCase):

    def setUp(self):
        self.basis = Basis(k_max=2)

    def test_zero_density(self):
        """Zero density: Tr=0, Hermitian, positive trivially."""
        rho = Density.zero(self.basis)
        self.assertAlmostEqual(rho.trace().real, 0.0)
        self.assertTrue(rho.is_hermitian())
        self.assertTrue(rho.is_positive())

    def test_maximally_mixed_trace(self):
        """Maximally mixed: Tr = 1."""
        rho = Density.maximally_mixed(self.basis)
        self.assertAlmostEqual(rho.trace().real, 1.0)

    def test_maximally_mixed_hermitian(self):
        """Maximally mixed is Hermitian."""
        rho = Density.maximally_mixed(self.basis)
        self.assertTrue(rho.is_hermitian())

    def test_maximally_mixed_positive(self):
        """Maximally mixed is positive (eigenvalues = 1/D)."""
        rho = Density.maximally_mixed(self.basis)
        self.assertTrue(rho.is_positive())

    def test_maximally_mixed_parity_split(self):
        """Maximally mixed assigns weight dim_plus/D to V⁺ and dim_minus/D to V⁻."""
        rho = Density.maximally_mixed(self.basis)
        D = self.basis.total_dim
        expected_minus = self.basis.dim_minus / D
        expected_plus = self.basis.dim_plus / D
        self.assertAlmostEqual(rho.tau_odd_weight(), expected_minus)
        self.assertAlmostEqual(rho.tau_even_weight(), expected_plus)

    def test_pure_tau_even_basis_vector(self):
        """Pure |+⟩ basis vector has tau_odd_weight = 0, tau_even_weight = 1."""
        # Use first τ-even basis vector at k=1
        idx = self.basis.first_plus_index(1)
        psi = self.basis.basis_vector(idx)
        rho = Density.pure(self.basis, psi)
        self.assertAlmostEqual(rho.trace().real, 1.0)
        self.assertAlmostEqual(rho.tau_odd_weight(), 0.0)
        self.assertAlmostEqual(rho.tau_even_weight(), 1.0)
        self.assertTrue(rho.is_hermitian())
        self.assertTrue(rho.is_positive())

    def test_pure_tau_odd_basis_vector(self):
        """Pure |−⟩ basis vector has tau_odd_weight = 1, tau_even_weight = 0."""
        # Use first τ-odd basis vector at k=1 (k=0 has no τ-odd modes)
        idx = self.basis.first_minus_index(1)
        psi = self.basis.basis_vector(idx)
        rho = Density.pure(self.basis, psi)
        self.assertAlmostEqual(rho.trace().real, 1.0)
        self.assertAlmostEqual(rho.tau_odd_weight(), 1.0)
        self.assertAlmostEqual(rho.tau_even_weight(), 0.0)

    def test_superposition_born_weight(self):
        """
        Superposition cos(θ)|+⟩ + sin(θ)|−⟩ has tau_odd_weight = sin²(θ).

        This is the Born-rule structure: the τ-odd weight of ρ equals the
        squared amplitude of the τ-odd component, which is exactly the
        probability of NOT actualizing on the next firing.
        """
        idx_plus = self.basis.first_plus_index(1)
        idx_minus = self.basis.first_minus_index(1)
        for theta_frac in [0.0, 0.1, 0.25, 0.333, 0.5, 0.75, 1.0]:
            with self.subTest(theta_frac=theta_frac):
                theta = theta_frac * math.pi / 2.0  # range [0, π/2]
                psi = (math.cos(theta) * self.basis.basis_vector(idx_plus)
                       + math.sin(theta) * self.basis.basis_vector(idx_minus))
                rho = Density.pure(self.basis, psi)
                expected = math.sin(theta) ** 2
                self.assertAlmostEqual(rho.tau_odd_weight(), expected, places=10)
                # Trace stays 1 throughout
                self.assertAlmostEqual(rho.trace().real, 1.0, places=10)

    def test_pure_unnormalized_input(self):
        """pure() accepts unnormalized vectors and normalizes them."""
        v = np.zeros(self.basis.total_dim, dtype=np.complex128)
        v[0] = 3.0  # unnormalized
        v[10] = 4.0
        rho = Density.pure(self.basis, v)
        self.assertAlmostEqual(rho.trace().real, 1.0)

    def test_pure_zero_vector_raises(self):
        v = np.zeros(self.basis.total_dim, dtype=np.complex128)
        with self.assertRaises(ValueError):
            Density.pure(self.basis, v)

    def test_pure_wrong_length_raises(self):
        v = np.zeros(self.basis.total_dim + 1, dtype=np.complex128)
        v[0] = 1.0
        with self.assertRaises(ValueError):
            Density.pure(self.basis, v)

    def test_density_wrong_shape_raises(self):
        bad_matrix = np.zeros((10, 10), dtype=np.complex128)
        with self.assertRaises(ValueError):
            Density(self.basis, bad_matrix)

    def test_thermal_state_validity(self):
        """Thermal state is Hermitian, positive, and has Tr = 1."""
        rho = Density.thermal(self.basis, temperature_units=1.0)
        self.assertTrue(rho.is_hermitian())
        self.assertTrue(rho.is_positive())
        self.assertAlmostEqual(rho.trace().real, 1.0)

    def test_thermal_low_T_concentrates_on_k0(self):
        """At very low T, almost all weight sits on the k=0 (eigenvalue=0) mode."""
        rho = Density.thermal(self.basis, temperature_units=0.01)
        # k=0 occupies index 0 (single τ-even vector)
        diag0 = float(np.real(rho.matrix[0, 0]))
        self.assertGreater(diag0, 0.99)
        # τ-odd weight should be tiny since k=0 has no τ-odd modes and higher
        # k are exponentially suppressed
        self.assertLess(rho.tau_odd_weight(), 0.01)

    def test_thermal_high_T_approaches_mixed(self):
        """At very high T, thermal state approaches maximally mixed."""
        rho_T = Density.thermal(self.basis, temperature_units=1000.0)
        D = self.basis.total_dim
        diag = np.real(np.diag(rho_T.matrix))
        # Each diagonal entry should be close to 1/D
        self.assertTrue(np.allclose(diag, 1.0 / D, atol=1e-3))

    def test_thermal_negative_T_raises(self):
        with self.assertRaises(ValueError):
            Density.thermal(self.basis, temperature_units=-1.0)

    def test_normalize_recovers_trace_one(self):
        """normalize() rescales so Tr(ρ) = 1."""
        rho = Density.maximally_mixed(self.basis)
        # Inflate it
        rho_inflated = Density(self.basis, rho.matrix * 7.5)
        self.assertAlmostEqual(rho_inflated.trace().real, 7.5)
        rho_normalized = rho_inflated.normalize()
        self.assertAlmostEqual(rho_normalized.trace().real, 1.0)

    def test_expectation_of_identity(self):
        """⟨I⟩ = Tr(ρ) for any ρ."""
        rho = Density.maximally_mixed(self.basis)
        I = np.eye(self.basis.total_dim, dtype=np.complex128)
        self.assertAlmostEqual(rho.expectation(I).real, 1.0)


class TestOperator(unittest.TestCase):
    """Generic Operator class behavior."""

    def setUp(self):
        self.basis = Basis(k_max=1)

    def test_construction_wrong_shape_raises(self):
        with self.assertRaises(ValueError):
            Operator(self.basis, np.zeros((10, 10), dtype=np.complex128))

    def test_adjoint(self):
        D = self.basis.total_dim
        # Build a non-Hermitian operator: A[0,1] = 1+1j, others zero
        m = np.zeros((D, D), dtype=np.complex128)
        m[0, 1] = 1.0 + 1.0j
        A = Operator(self.basis, m)
        Adag = A.adjoint()
        self.assertEqual(Adag.matrix[1, 0], 1.0 - 1.0j)

    def test_matmul(self):
        D = self.basis.total_dim
        I = Operator(self.basis, np.eye(D, dtype=np.complex128))
        A = Operator(self.basis, np.eye(D, dtype=np.complex128) * 2.0)
        product = I @ A
        self.assertTrue(np.allclose(product.matrix, np.eye(D) * 2.0))

    def test_commutator_of_diagonal_is_zero(self):
        """Diagonal operators always commute."""
        diag1 = np.diag(np.arange(self.basis.total_dim, dtype=np.complex128))
        diag2 = np.diag(np.arange(self.basis.total_dim, dtype=np.complex128) * 2.0)
        A = Operator(self.basis, diag1)
        B = Operator(self.basis, diag2)
        comm = A.commutator(B)
        self.assertTrue(np.allclose(comm.matrix, 0.0))

    def test_anticommutator_of_identity(self):
        """{I, A} = 2A."""
        D = self.basis.total_dim
        I = Operator(self.basis, np.eye(D, dtype=np.complex128))
        m = np.random.RandomState(42).randn(D, D).astype(np.complex128)
        A = Operator(self.basis, m)
        anti = I.anticommutator(A)
        self.assertTrue(np.allclose(anti.matrix, 2.0 * m))

    def test_scalar_multiplication(self):
        D = self.basis.total_dim
        A = Operator(self.basis, np.eye(D, dtype=np.complex128))
        self.assertTrue(np.allclose((A * 3).matrix, 3.0 * np.eye(D)))
        self.assertTrue(np.allclose((3 * A).matrix, 3.0 * np.eye(D)))
        self.assertTrue(np.allclose((-A).matrix, -np.eye(D)))

    def test_apply_to_density(self):
        """A ρ A† for A = identity returns ρ unchanged."""
        I = Operator(self.basis, np.eye(self.basis.total_dim, dtype=np.complex128))
        rho = Density.maximally_mixed(self.basis)
        out = I.apply_to(rho)
        self.assertTrue(np.allclose(out.matrix, rho.matrix))

    def test_expectation_with_density(self):
        """⟨I⟩ = Tr(ρ) for any density."""
        I = Operator(self.basis, np.eye(self.basis.total_dim, dtype=np.complex128))
        rho = Density.maximally_mixed(self.basis)
        self.assertAlmostEqual(I.expectation(rho).real, 1.0)


class TestTauProjector(unittest.TestCase):
    """Pre-built τ-projector operator (the global Â)."""

    def setUp(self):
        self.basis = Basis(k_max=2)
        self.A = tau_projector(self.basis)

    def test_idempotent(self):
        """Â² = Â."""
        sq = self.A @ self.A
        self.assertTrue(np.allclose(sq.matrix, self.A.matrix))

    def test_hermitian(self):
        """Â† = Â."""
        self.assertTrue(self.A.is_hermitian())

    def test_trace_equals_dim_plus(self):
        """Tr(Â) = dim_plus (orthogonal projection rank)."""
        self.assertAlmostEqual(self.A.trace().real, float(self.basis.dim_plus))

    def test_annihilates_tau_odd_state(self):
        """Â |−⟩⟨−| Â† = 0 for a τ-odd basis state."""
        idx = self.basis.first_minus_index(1)
        psi = self.basis.basis_vector(idx)
        rho = Density.pure(self.basis, psi)
        out = self.A.apply_to(rho)
        self.assertAlmostEqual(out.trace().real, 0.0, places=12)
        self.assertTrue(np.allclose(out.matrix, 0.0, atol=1e-12))

    def test_preserves_tau_even_state(self):
        """Â |+⟩⟨+| Â† = |+⟩⟨+|."""
        idx = self.basis.first_plus_index(1)
        psi = self.basis.basis_vector(idx)
        rho = Density.pure(self.basis, psi)
        out = self.A.apply_to(rho)
        self.assertTrue(np.allclose(out.matrix, rho.matrix))


class TestFreeHamiltonian(unittest.TestCase):
    """Pre-built free Hamiltonian H_α = CP³ Laplacian."""

    def setUp(self):
        self.basis = Basis(k_max=2)
        self.H = free_hamiltonian(self.basis)

    def test_hermitian(self):
        self.assertTrue(self.H.is_hermitian())

    def test_eigenvalues_match_spectral_data(self):
        """H[i,i] = k_i (k_i + 3) per basis index."""
        diag = np.real(np.diag(self.H.matrix))
        for i in range(self.basis.total_dim):
            k = int(self.basis.k_index[i])
            expected = k * (k + 3)
            self.assertEqual(diag[i], expected)

    def test_off_diagonal_zero(self):
        """H is purely diagonal."""
        m = self.H.matrix
        off_diag = m - np.diag(np.diag(m))
        self.assertTrue(np.allclose(off_diag, 0.0))

    def test_commutes_with_tau_projector(self):
        """[H_α, Â] = 0 (analytical claim from actualization_operator.py item ii)."""
        A = tau_projector(self.basis)
        comm = self.H.commutator(A)
        self.assertTrue(np.allclose(comm.matrix, 0.0, atol=1e-12))


class TestBoundaryOperator(unittest.TestCase):
    """Per-boundary actualization operators A_b (rank-1 τ-even projectors)."""

    def setUp(self):
        self.basis = Basis(k_max=2)

    def test_idempotent(self):
        """A_b² = A_b."""
        for b in [0, 5, 20, 50]:
            with self.subTest(b=b):
                A = boundary_operator(self.basis, b)
                sq = A @ A
                self.assertTrue(np.allclose(sq.matrix, A.matrix))

    def test_hermitian(self):
        for b in [0, 10, 40]:
            with self.subTest(b=b):
                A = boundary_operator(self.basis, b)
                self.assertTrue(A.is_hermitian())

    def test_trace_equals_one(self):
        """Each A_b is rank-1, so Tr(A_b) = 1."""
        for b in [0, 1, 30]:
            with self.subTest(b=b):
                A = boundary_operator(self.basis, b)
                self.assertAlmostEqual(A.trace().real, 1.0)

    def test_distinct_boundaries_commute(self):
        """[A_b, A_b'] = 0 for b ≠ b' (orthogonal rank-1 projectors)."""
        for b1, b2 in [(0, 1), (5, 20), (10, 40)]:
            with self.subTest(b1=b1, b2=b2):
                A1 = boundary_operator(self.basis, b1)
                A2 = boundary_operator(self.basis, b2)
                comm = A1.commutator(A2)
                self.assertTrue(np.allclose(comm.matrix, 0.0))

    def test_distinct_boundaries_orthogonal(self):
        """A_b A_b' = 0 for b ≠ b' (orthogonal)."""
        A1 = boundary_operator(self.basis, 0)
        A2 = boundary_operator(self.basis, 1)
        prod = A1 @ A2
        self.assertTrue(np.allclose(prod.matrix, 0.0))

    def test_acts_on_tau_even_target_only(self):
        """A_b |b⟩⟨b| A_b = |b⟩⟨b| but A_b |b'⟩⟨b'| A_b = 0 for b' ≠ b."""
        b = 5
        A = boundary_operator(self.basis, b)
        plus_indices = np.where(self.basis.tau_parity == +1)[0]
        global_idx = int(plus_indices[b])

        # Same mode: preserved
        psi_same = self.basis.basis_vector(global_idx)
        rho_same = Density.pure(self.basis, psi_same)
        out = A.apply_to(rho_same)
        self.assertTrue(np.allclose(out.matrix, rho_same.matrix))

        # Different τ-even mode: annihilated
        other_global_idx = int(plus_indices[10])
        psi_other = self.basis.basis_vector(other_global_idx)
        rho_other = Density.pure(self.basis, psi_other)
        out_other = A.apply_to(rho_other)
        self.assertTrue(np.allclose(out_other.matrix, 0.0, atol=1e-12))

    def test_out_of_range_raises(self):
        with self.assertRaises(IndexError):
            boundary_operator(self.basis, self.basis.dim_plus)
        with self.assertRaises(IndexError):
            boundary_operator(self.basis, -1)


class TestAllBoundaryOperatorsSumToTauProjector(unittest.TestCase):
    """Σ_b A_b = Â (the τ-even rank-1 projectors sum to the global projector)."""

    def test_sum_equals_tau_projector(self):
        basis = Basis(k_max=2)
        A_global = tau_projector(basis)
        boundaries = all_boundary_operators(basis)
        # Sum
        accum = np.zeros((basis.total_dim, basis.total_dim), dtype=np.complex128)
        for A in boundaries:
            accum = accum + A.matrix
        self.assertTrue(np.allclose(accum, A_global.matrix, atol=1e-12))

    def test_count_equals_dim_plus(self):
        basis = Basis(k_max=2)
        boundaries = all_boundary_operators(basis)
        self.assertEqual(len(boundaries), basis.dim_plus)


# ─── Phase 3: Lindblad evolution ─────────────────────────────────────────────


def _zero_hamiltonian(basis):
    """Helper: Operator with zero matrix, for purely dissipative dynamics."""
    return Operator(basis, np.zeros((basis.total_dim, basis.total_dim),
                                     dtype=np.complex128))


def _two_state_initial(basis, k=1, alpha_plus=0.6, alpha_minus=0.8):
    """
    Helper: build a normalized superposition cos|+⟩ + sin|−⟩ (real coefficients
    rescaled so |a|²+|b|²=1) at level k. Returns (Density, |+⟩ index, |−⟩ index).
    """
    idx_plus = basis.first_plus_index(k)
    idx_minus = basis.first_minus_index(k)
    a = alpha_plus
    b = alpha_minus
    norm = math.sqrt(a * a + b * b)
    a /= norm
    b /= norm
    psi = a * basis.basis_vector(idx_plus) + b * basis.basis_vector(idx_minus)
    return Density.pure(basis, psi), idx_plus, idx_minus


def _mode_index_for_global(basis, global_idx):
    """
    Helper: convert a global basis index (must point at a τ-even vector) to the
    corresponding mode_index argument for `boundary_operator`.
    """
    plus_indices = np.where(basis.tau_parity == +1)[0]
    matches = np.where(plus_indices == global_idx)[0]
    if len(matches) == 0:
        raise ValueError(f"global index {global_idx} is not τ-even")
    return int(matches[0])


class TestLindbladRhs(unittest.TestCase):
    """The dρ/dt operator is correctly assembled."""

    def test_zero_dynamics(self):
        """With H=0 and no jump operators, dρ/dt = 0."""
        basis = Basis(k_max=1)
        rho = Density.maximally_mixed(basis)
        H = _zero_hamiltonian(basis)
        drho = lindblad_rhs(rho, H, A_ops=[], gammas=[])
        self.assertTrue(np.allclose(drho, 0.0, atol=1e-12))

    def test_unitary_only_preserves_trace(self):
        """With H ≠ 0 but no dissipation, Tr(dρ/dt) = 0."""
        basis = Basis(k_max=2)
        rho = Density.maximally_mixed(basis)
        H = free_hamiltonian(basis)
        drho = lindblad_rhs(rho, H, A_ops=[], gammas=[])
        self.assertAlmostEqual(np.trace(drho), 0.0, places=12)

    def test_dissipator_preserves_trace_globally(self):
        """Tr(dρ/dt) = 0 for the actualization channel."""
        basis = Basis(k_max=2)
        rho = Density.maximally_mixed(basis)
        H = _zero_hamiltonian(basis)
        A = boundary_operator(basis, 5)
        drho = lindblad_rhs(rho, H, A_ops=[A], gammas=[1.5])
        self.assertAlmostEqual(np.trace(drho), 0.0, places=12)

    def test_length_mismatch_raises(self):
        basis = Basis(k_max=1)
        rho = Density.maximally_mixed(basis)
        H = _zero_hamiltonian(basis)
        A = boundary_operator(basis, 0)
        with self.assertRaises(ValueError):
            lindblad_rhs(rho, H, A_ops=[A], gammas=[1.0, 2.0])


class TestLindbladStep(unittest.TestCase):
    """RK4 step: trace, positivity, hermiticity preservation."""

    def setUp(self):
        self.basis = Basis(k_max=1)
        rho_init, _, _ = _two_state_initial(self.basis)
        self.rho_0 = rho_init
        self.H = free_hamiltonian(self.basis)
        self.A_ops = [boundary_operator(self.basis, 0)]
        self.gammas = [1.0]
        self.dt = 0.01

    def test_returns_density(self):
        rho_1 = lindblad_step(self.rho_0, self.H, self.A_ops,
                              self.gammas, self.dt)
        self.assertIsInstance(rho_1, Density)
        self.assertEqual(rho_1.matrix.shape,
                         (self.basis.total_dim, self.basis.total_dim))

    def test_single_step_trace_preserved(self):
        rho_1 = lindblad_step(self.rho_0, self.H, self.A_ops,
                              self.gammas, self.dt)
        self.assertAlmostEqual(rho_1.trace().real, 1.0, places=10)

    def test_single_step_hermitian(self):
        rho_1 = lindblad_step(self.rho_0, self.H, self.A_ops,
                              self.gammas, self.dt)
        self.assertTrue(rho_1.is_hermitian(atol=1e-10))

    def test_single_step_positive(self):
        rho_1 = lindblad_step(self.rho_0, self.H, self.A_ops,
                              self.gammas, self.dt)
        self.assertTrue(rho_1.is_positive(atol=1e-10))


class TestLindbladEvolve(unittest.TestCase):
    """Long-evolution validity invariants and analytical match-ups."""

    def setUp(self):
        self.basis = Basis(k_max=1)

    def test_trace_preservation_long(self):
        """Tr(ρ(t)) = 1 across a long evolution."""
        rho_0, _, _ = _two_state_initial(self.basis)
        H = free_hamiltonian(self.basis)
        A = boundary_operator(self.basis, 0)
        snapshots = [0, 50, 100, 250, 500]
        traj = lindblad_evolve(rho_0, H, [A], [1.0],
                               T=5.0, n_steps=500, snapshots=snapshots)
        for t, rho in traj:
            with self.subTest(t=t):
                self.assertAlmostEqual(rho.trace().real, 1.0, places=8)

    def test_hermiticity_preservation_long(self):
        rho_0, _, _ = _two_state_initial(self.basis)
        H = free_hamiltonian(self.basis)
        A = boundary_operator(self.basis, 0)
        traj = lindblad_evolve(rho_0, H, [A], [1.0],
                               T=5.0, n_steps=500,
                               snapshots=[0, 100, 250, 500])
        for t, rho in traj:
            self.assertTrue(rho.is_hermitian(atol=1e-8))

    def test_positivity_preservation_long(self):
        rho_0, _, _ = _two_state_initial(self.basis)
        H = free_hamiltonian(self.basis)
        A = boundary_operator(self.basis, 0)
        traj = lindblad_evolve(rho_0, H, [A], [1.0],
                               T=5.0, n_steps=500,
                               snapshots=[0, 100, 250, 500])
        for t, rho in traj:
            self.assertTrue(rho.is_positive(atol=1e-8))

    def test_population_conservation_under_pure_dissipative(self):
        """
        With H=0 and a single rank-1 jump operator A = |+⟩⟨+| acting on the
        τ-even mode where the state has support, the diagonal elements ρ_++
        and ρ_−− (populations) are conserved — only off-diagonals decay.
        """
        rho_0, idx_plus, idx_minus = _two_state_initial(self.basis)
        H = _zero_hamiltonian(self.basis)
        # Use the boundary operator that actually acts on idx_plus
        mode_idx = _mode_index_for_global(self.basis, idx_plus)
        A = boundary_operator(self.basis, mode_idx)
        rho_init = rho_0
        p_plus_0 = float(np.real(rho_init.matrix[idx_plus, idx_plus]))
        p_minus_0 = float(np.real(rho_init.matrix[idx_minus, idx_minus]))

        traj = lindblad_evolve(rho_init, H, [A], [2.0],
                               T=5.0, n_steps=500,
                               snapshots=[0, 100, 250, 500])
        for t, rho in traj:
            with self.subTest(t=t):
                p_plus_t = float(np.real(rho.matrix[idx_plus, idx_plus]))
                p_minus_t = float(np.real(rho.matrix[idx_minus, idx_minus]))
                self.assertAlmostEqual(p_plus_t, p_plus_0, places=8)
                self.assertAlmostEqual(p_minus_t, p_minus_0, places=8)

    def test_off_diagonal_decay_rate(self):
        """
        For A = |+⟩⟨+| acting on the τ-even mode where ρ has support and ρ
        initially having coherence ρ_{+−}, the off-diagonal decays as
        exp(-γt/2).

        This is the analytical decoherence prediction from
        archive/scripts/actualization_operator.py: dρ_{+-}/dt = -½γ ρ_{+-},
        so τ_dec = 2/γ.
        """
        rho_0, idx_plus, idx_minus = _two_state_initial(self.basis)
        c0 = complex(rho_0.matrix[idx_plus, idx_minus])
        gamma = 2.0
        H = _zero_hamiltonian(self.basis)
        # The boundary operator must act on the same mode where idx_plus lives.
        mode_idx = _mode_index_for_global(self.basis, idx_plus)
        A = boundary_operator(self.basis, mode_idx)

        # Sample at several times for rate fit
        T = 4.0
        n_steps = 800
        snapshots = [0, 100, 200, 400, 600, 800]
        traj = lindblad_evolve(rho_0, H, [A], [gamma],
                               T=T, n_steps=n_steps, snapshots=snapshots)

        # Compute |c(t)| / |c(0)| and compare to exp(-γt/2)
        for t, rho in traj[1:]:  # skip t=0
            with self.subTest(t=t):
                c_t = complex(rho.matrix[idx_plus, idx_minus])
                ratio = abs(c_t) / abs(c0)
                expected = math.exp(-0.5 * gamma * t)
                # RK4 with dt = 0.005 gives <1e-6 on this exponential
                self.assertAlmostEqual(ratio, expected, places=4)

    def test_long_time_decoherence_to_diagonal(self):
        """
        Long-time fixed point: off-diagonals between |+⟩ and |−⟩ vanish.
        The state becomes diagonal in the +/− decomposition.
        """
        rho_0, idx_plus, idx_minus = _two_state_initial(self.basis)
        gamma = 5.0
        H = _zero_hamiltonian(self.basis)
        mode_idx = _mode_index_for_global(self.basis, idx_plus)
        A = boundary_operator(self.basis, mode_idx)
        traj = lindblad_evolve(rho_0, H, [A], [gamma],
                               T=10.0, n_steps=2000,
                               snapshots=[2000])
        _, rho_inf = traj[-1]
        c_inf = abs(complex(rho_inf.matrix[idx_plus, idx_minus]))
        self.assertLess(c_inf, 1e-6)

    def test_zeno_regime_protects_tau_even(self):
        """
        In the fast-bath (Zeno) limit γ ≫ ω, a state initially in V⁺ is
        protected against drift to V⁻ even when the Hamiltonian would mix
        them in absence of dissipation.

        Setup: initial state slightly tilted from pure |+⟩ toward |−⟩ (so
        H drives it further toward |−⟩ at small times). Apply huge γ on
        the τ-even projector. Check that ρ stays predominantly in V⁺.
        """
        # Need a non-diagonal H to even attempt a τ-even/τ-odd mix; the free
        # H is diagonal so [H, A] = 0 means H alone won't mix sectors. Build
        # a small mixing perturbation H_mix that couples |+⟩ to |−⟩.
        idx_plus = self.basis.first_plus_index(1)
        idx_minus = self.basis.first_minus_index(1)
        H_mix_m = np.zeros((self.basis.total_dim, self.basis.total_dim),
                           dtype=np.complex128)
        omega = 1.0
        H_mix_m[idx_plus, idx_minus] = omega
        H_mix_m[idx_minus, idx_plus] = omega
        H_mix = Operator(self.basis, H_mix_m)

        # Initial state: pure |+⟩
        psi = self.basis.basis_vector(idx_plus)
        rho_0 = Density.pure(self.basis, psi)

        # Without dissipation: Hamiltonian Rabi mixing would drive ρ_minus up
        # to ~sin²(ωt) ≈ 0.84 by t = 1.0 with ω = 1.0
        traj_no_diss = lindblad_evolve(rho_0, H_mix, [], [],
                                       T=1.0, n_steps=200, snapshots=[200])
        rho_no_diss = traj_no_diss[-1][1]
        p_minus_no_diss = rho_no_diss.tau_odd_weight()

        # With huge γ on the τ-even projector at the |+⟩ mode: should stay near |+⟩
        A = boundary_operator(self.basis, 0)  # |+⟩ mode (alpha=0 at k=1)
        # Actually need the mode_index that corresponds to idx_plus.
        # idx_plus at k=1 is the FIRST τ-even index at k=1, but mode_index=0 is
        # the FIRST τ-even GLOBALLY (which is at k=0). So we need mode_index=1.
        plus_indices = np.where(self.basis.tau_parity == +1)[0]
        mode_idx_for_idx_plus = int(np.where(plus_indices == idx_plus)[0][0])
        A = boundary_operator(self.basis, mode_idx_for_idx_plus)

        gamma_zeno = 1000.0
        traj_zeno = lindblad_evolve(rho_0, H_mix, [A], [gamma_zeno],
                                    T=1.0, n_steps=10000, snapshots=[10000])
        rho_zeno = traj_zeno[-1][1]
        p_minus_zeno = rho_zeno.tau_odd_weight()

        # Without dissipation: significant τ-odd weight builds up
        self.assertGreater(p_minus_no_diss, 0.1)
        # With Zeno: τ-odd weight stays small
        self.assertLess(p_minus_zeno, 0.05)
        # And specifically much smaller than the dissipationless case
        self.assertLess(p_minus_zeno, p_minus_no_diss / 10.0)


class TestSingleEventBornRule(unittest.TestCase):
    """
    Born rule from the single-event projection (the discrete piece of the
    actualization channel, distinct from continuous Lindblad averaging).

    For pure |ψ⟩ = a|+⟩ + b|−⟩, applying Â (= τ-projector) once gives
    Â |ψ⟩⟨ψ| Â with trace = |a|². Normalized post-projection state is
    |+⟩⟨+|.
    """

    def setUp(self):
        self.basis = Basis(k_max=1)

    def test_yield_equals_squared_amplitude(self):
        idx_plus = self.basis.first_plus_index(1)
        idx_minus = self.basis.first_minus_index(1)
        for theta_frac in [0.0, 0.1, 0.25, 0.333, 0.5, 0.75, 1.0]:
            with self.subTest(theta_frac=theta_frac):
                theta = theta_frac * math.pi / 2.0
                psi = (math.cos(theta) * self.basis.basis_vector(idx_plus)
                       + math.sin(theta) * self.basis.basis_vector(idx_minus))
                rho = Density.pure(self.basis, psi)
                A = tau_projector(self.basis)
                projected = A.apply_to(rho)
                # Yield = trace of unnormalized projected state = |cos(theta)|²
                yield_value = projected.trace().real
                self.assertAlmostEqual(yield_value, math.cos(theta) ** 2,
                                       places=10)

    def test_normalized_post_projection_is_tau_even(self):
        """After projection and renormalization, ρ has zero τ-odd weight."""
        idx_plus = self.basis.first_plus_index(1)
        idx_minus = self.basis.first_minus_index(1)
        psi = (0.6 * self.basis.basis_vector(idx_plus)
               + 0.8 * self.basis.basis_vector(idx_minus))
        rho = Density.pure(self.basis, psi)
        A = tau_projector(self.basis)
        projected = A.apply_to(rho)
        normalized = projected.normalize()
        self.assertAlmostEqual(normalized.tau_odd_weight(), 0.0, places=10)
        self.assertAlmostEqual(normalized.tau_even_weight(), 1.0, places=10)


class TestYieldAndFreeEnergy(unittest.TestCase):
    """yield_distribution and free_energy helpers."""

    def setUp(self):
        self.basis = Basis(k_max=1)

    def test_yield_sums_to_one_for_complete_set(self):
        """Σ_b P_b = Tr(P⁺ ρ) when A_ops = all_boundary_operators."""
        rho = Density.maximally_mixed(self.basis)
        A_ops = all_boundary_operators(self.basis)
        yields = yield_distribution(rho, A_ops)
        total = sum(yields.values())
        # Maximally mixed has weight dim_plus / D in V⁺
        expected = self.basis.dim_plus / self.basis.total_dim
        self.assertAlmostEqual(total, expected, places=12)

    def test_yield_for_pure_tau_even_state(self):
        """Yield is concentrated entirely on the matched mode."""
        idx = self.basis.first_plus_index(1)  # global = 1, mode = 1
        psi = self.basis.basis_vector(idx)
        rho = Density.pure(self.basis, psi)
        A_ops = all_boundary_operators(self.basis)
        yields = yield_distribution(rho, A_ops)
        # mode 1 (the second τ-even mode globally) should have P=1
        self.assertAlmostEqual(yields[1], 1.0, places=10)
        for b, P in yields.items():
            if b != 1:
                self.assertAlmostEqual(P, 0.0, places=10)

    def test_free_energy_max(self):
        """F = -log(max P_b) for a state where some mode is fully occupied."""
        idx = self.basis.first_plus_index(1)
        psi = self.basis.basis_vector(idx)
        rho = Density.pure(self.basis, psi)
        A_ops = all_boundary_operators(self.basis)
        F = free_energy(rho, A_ops, agg='max')
        self.assertAlmostEqual(F, 0.0, places=10)

    def test_free_energy_unknown_agg_raises(self):
        rho = Density.maximally_mixed(self.basis)
        A_ops = all_boundary_operators(self.basis)
        with self.assertRaises(ValueError):
            free_energy(rho, A_ops, agg='bogus')


if __name__ == '__main__':
    unittest.main()

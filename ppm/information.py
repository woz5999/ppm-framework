"""
ppm.information — Information-theoretic quantities
====================================================

Computes channel capacity, entropy, Holevo bound, and Landauer limit
within the PPM fiber-coherence framework. These quantities characterize
the information-processing capacity at each k-level.

LaTeX: ch07 (Information Theory)
"""

import math
from . import constants as C
from . import hierarchy as H


# ─── Constants ───────────────────────────────────────────────────────────────

K_B_NAT = 1.0  # Boltzmann constant in natural units (nats)
LN2 = math.log(2)


def channel_capacity(k=None):
    """Channel capacity at k-level from fiber coherence.

    LaTeX: C(k) = log₂(d_k) where d_k = dim of fiber representation at level k
    \\textit{Code: ppm.information.channel_capacity()}  [ch07]
    For the CP³ sigma model, the fiber at level k carries a representation
    of dimension scaling as φ^k.
    Section: §7.1
    Status: FORMULA
    """
    if k is None:
        k = C.K_PION  # default to pion scale
    d_k = C.PHI ** k
    C_bits = math.log2(d_k)
    return {
        'k': k,
        'd_k': d_k,
        'capacity_bits': C_bits,
        'capacity_nats': C_bits * LN2,
        'formula': 'C(k) = k * log2(phi)',
        'status': 'FORMULA'
    }


def entropy(k=None):
    """Von Neumann entropy of projected state at k-level.

    LaTeX: S(k) = ln(d_k) where d_k is the fiber dimension
    \\textit{Code: ppm.information.entropy()}  [ch07]
    Projection CP³ → RP³ discards fiber information, producing entropy.
    Section: §7.2
    Status: FORMULA
    """
    if k is None:
        k = C.K_PION
    d_k = C.PHI ** k
    S_nats = math.log(d_k)
    return {
        'k': k,
        'S_nats': S_nats,
        'S_bits': S_nats / LN2,
        'formula': 'S(k) = k * ln(phi)',
        'status': 'FORMULA'
    }


def efficiency(k=None):
    """Information efficiency: ratio of accessible to total information.

    LaTeX: η(k) = dim(RP³-fiber) / dim(CP³-fiber)
    \\textit{Code: ppm.information.efficiency()}  [ch07]
    Section: §7.3
    Status: FORMULA
    """
    if k is None:
        k = C.K_PION
    # RP³ is 3-real-dimensional, CP³ is 6-real-dimensional
    # Efficiency = fraction of information surviving projection
    eta = 3.0 / 6.0  # dim(RP³)/dim(CP³) at each level
    return {
        'k': k,
        'efficiency': eta,
        'accessible_dims': 3,
        'total_dims': 6,
        'lost_dims': 3,
        'interpretation': 'Half of fiber information survives Z2 projection',
        'status': 'FORMULA'
    }


def holevo():
    """Holevo bound from fiber geometry.

    LaTeX: χ = S(ρ) - Σ p_i S(ρ_i)  ≤  log(d_k)
    \\textit{Code: ppm.information.holevo()}  [ch07]
    Section: §7.6
    Status: FORMULA
    """
    # At the pion scale
    k = C.K_PION
    d_k = C.PHI ** k
    chi_max = math.log(d_k)
    return {
        'k': k,
        'holevo_bound_nats': chi_max,
        'holevo_bound_bits': chi_max / LN2,
        'formula': 'chi <= ln(d_k) = k * ln(phi)',
        'interpretation': 'Maximum classical information extractable '
                          'from quantum state at k-level',
        'status': 'FORMULA'
    }


def landauer():
    """Landauer limit from PPM thermodynamics.

    LaTeX: E_erase ≥ k_B T ln 2
    \\textit{Code: ppm.information.landauer()}  [ch07]
    In PPM, this bound is saturated at the consciousness-scale k-window
    boundary.
    Section: §7.7
    Status: FORMULA
    """
    T = 310.0  # mammalian body temperature
    k_B = 1.3806e-23  # J/K
    E_landauer = k_B * T * LN2
    return {
        'T_K': T,
        'E_landauer_J': E_landauer,
        'E_landauer_eV': E_landauer / 1.602e-19,
        'formula': 'E_erase >= k_B T ln 2',
        'interpretation': 'Minimum energy to erase one bit; sets upper '
                          'k-boundary of consciousness window',
        'status': 'FORMULA'
    }

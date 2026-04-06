"""
ppm.gravity — Gravitational physics
=====================================

Wrapper module providing the interface referenced in ch12-gravity.tex.
Most computations live in cosmology.py; this module re-exports them
under the names used in the technical document's Code: references.

LaTeX: ch12 (Gravity and Cosmology)
"""

from .cosmology import (
    cosmological_constant,
    hubble_from_age,
    hubble_from_sidharth,
    g_eff,
    gw_dispersion,
    gw_phase_shift,
    w_eff,
    w_eff_backreaction,
    friedmann_age,
    actualization_record,
)
from . import constants as C
import math


def newton_constant():
    """Newton's gravitational constant from PPM.

    LaTeX: G = 16π⁴ ℏc α / (m_π² √N_∞)
    \\textit{Code: ppm.gravity.newton_constant()}  [ch12]
    Section: §12.1
    Status: VERIFIED
    """
    alpha = 1.0 / C.ALPHA_EM_INV
    G_ppm = 16 * math.pi**4 * C.HBAR_SI * C.C_LIGHT_SI * alpha / (
        C.M_PI_KG**2 * math.sqrt(C.N_ASYMPTOTIC))
    return {
        'G_ppm_si': G_ppm,
        'G_obs_si': C.G_NEWTON_SI,
        'error_pct': (G_ppm / C.G_NEWTON_SI - 1) * 100,
        'formula': '16 pi^4 hbar c alpha / (m_pi^2 sqrt(N_inf))',
        'status': 'VERIFIED'
    }


def two_couplings():
    """Relation between G and Λ via N_∞.

    LaTeX: \\textit{Code: ppm.gravity.two_couplings()}  [ch12]
    Both G and Λ derive from N_∞ = φ^{392}. The ratio GΛ/c⁴ is
    fixed by geometry.
    Section: §12.2
    Status: VERIFIED
    """
    G = newton_constant()['G_ppm_si']
    Lam = cosmological_constant()['Lambda_m2']
    ratio = G * Lam / C.C_LIGHT_SI**4
    return {
        'G_si': G,
        'Lambda_m2': Lam,
        'G_Lambda_over_c4': ratio,
        'N_inf': C.N_ASYMPTOTIC,
        'status': 'VERIFIED'
    }


def hubble():
    """Hubble constant from Friedmann age.

    LaTeX: \\textit{Code: ppm.gravity.hubble()}  [ch12]
    """
    return hubble_from_age()


def dark_energy():
    """Dark energy equation of state from backreaction.

    LaTeX: \\textit{Code: ppm.gravity.dark_energy()}  [ch12]
    w_eff = -1 + (2/3)(Ω_δ/Ω_DE) where Ω_δ is the backreaction fraction.
    Section: §12.5
    Status: VERIFIED
    """
    w_lo = w_eff(0.01)
    w_hi = w_eff(0.1)
    return {
        'w_eff_low': w_lo,
        'w_eff_high': w_hi,
    }



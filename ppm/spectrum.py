"""
ppm.spectrum — Particle mass spectrum
=======================================

Mass eigenvalue assignments from fiber geometry on CP³/RP³.
The Bohr-Sommerfeld quantization condition on the RP³ fiber
determines which k-levels correspond to physical particles.

NOTE: Precise mass predictions for heavy quarks and leptons
beyond leading order are BLOCKED on R1 (FFS sigma-model
coefficients) and R2 (Fubini-Study normalization). The
functions here implement the framework structure and
leading-order results.

LaTeX: ch05 (Generations), ch10 (Particle Spectrum)
"""

import math
from . import constants as C
from . import hierarchy as H
from . import gauge as G


def fiber_modes():
    """Fiber mode structure on RP³.

    LaTeX: \\textit{Code: ppm.spectrum.fiber_modes()}  [ch10]
    The Z₂-equivariant fiber bundle over RP³ has modes labeled
    by the k-level. Each mode corresponds to a physical degree
    of freedom when it satisfies the Bohr-Sommerfeld condition.
    Section: §10.1
    Status: FORMULA
    """
    modes = []
    key_levels = [
        (C.K_BREAK, 'Pati-Salam scale'),
        (C.K_EWSB, 'EWSB scale'),
        (48, 'tau lepton'),
        (C.K_PION, 'pion/confinement'),
        (51.5, 'muon'),
        (57, 'electron'),
    ]
    for k, label in key_levels:
        modes.append({
            'k': k,
            'label': label,
            'E_gev': H.energy_gev(k),
            'E_mev': H.energy_mev(k),
        })
    return {
        'modes': modes,
        'mechanism': 'Z2-equivariant fiber modes on RP3',
        'quantization': 'Bohr-Sommerfeld on closed orbits in RP3',
        'status': 'FORMULA'
    }


def bohr_sommerfeld():
    """Bohr-Sommerfeld quantization condition.

    LaTeX: \\textit{Code: ppm.spectrum.bohr_sommerfeld()}  [ch10]
    ∮ p·dq = 2πn on closed geodesics of RP³ selects allowed k-levels.
    The pion mass (k=51) is the empirical anchor; all other masses
    follow from the geometric hierarchy g=2π.
    Section: §10.2
    Status: FORMULA
    """
    return {
        'condition': 'oint p dq = 2 pi n  on RP3 geodesics',
        'anchor': {'k': C.K_PION, 'particle': 'pion', 'mass_mev': 134.977},
        'hierarchy_base': C.PHI,
        'level_spacing': 'E(k) = E_Planck / g^k, g = 2pi',
        'status': 'FORMULA'
    }


def top_quark():
    """Top quark mass from Yukawa coupling.

    LaTeX: y_t = π/(2(2π)^{1/4}), m_t = y_t v/√2
    \\textit{Code: ppm.spectrum.top_quark()}  [ch10]
    Section: §10.3
    Status: VERIFIED
    """
    from . import higgs as HI
    yt = HI.top_yukawa_ppm()
    v = 246.22
    m_t = yt * v / math.sqrt(2)
    return {
        'y_top_ppm': yt,
        'm_top_gev': m_t,
        'm_top_obs_gev': 173.0,
        'error_pct': (m_t / 173.0 - 1) * 100,
        'status': 'VERIFIED'
    }


def heavy_quarks():
    """Heavy quark mass predictions (leading order).

    LaTeX: \\textit{Code: ppm.spectrum.heavy_quarks()}  [ch10]
    Section: §10.4
    Status: OPEN (blocked on R1, R2 for precision)
    """
    return {
        'top': top_quark(),
        'bottom_mechanism': 'Fiber-mode at k ~ 47, ratio from SU(4) Clebsch-Gordan',
        'charm_mechanism': 'Fiber-mode at k ~ 49.5',
        'blocked_on': ['R1 (FFS sigma-model coefficients)',
                       'R2 (Fubini-Study normalization)'],
        'status': 'OPEN'
    }


def tau_mass():
    """Tau lepton mass from hierarchy.

    LaTeX: \\textit{Code: ppm.spectrum.tau_mass()}  [ch10]
    Section: §10.5
    Status: FORMULA
    """
    k_tau = 48
    E_tau = H.energy_mev(k_tau)
    return {
        'k_tau': k_tau,
        'E_mev': E_tau,
        'E_obs_mev': 1776.86,
        'mechanism': 'k=48 level in geometric hierarchy',
        'status': 'FORMULA'
    }


def muon_electron():
    """Muon-electron mass ratio.

    LaTeX: m_μ/m_e = (3/2)e^{π²/2}  (wall suppression)
    \\textit{Code: ppm.spectrum.muon_electron()}  [ch10]
    Section: §10.6
    Status: VERIFIED
    """
    lmr = G.lepton_mass_ratios()
    return {
        'mu_e_ppm': lmr['mu_e_ppm'],
        'mu_e_obs': lmr['mu_e_obs'],
        'error_pct': lmr['mu_e_err_pct'],
        'formula': '(3/2) exp(pi^2 / 2)',
        'mechanism': 'Wall suppression factor for third generation',
        'status': 'VERIFIED'
    }


def lepton_mass_ratios():
    """All lepton mass ratios.

    LaTeX: \\textit{Code: ppm.spectrum.lepton_mass_ratios()}  [ch05, ch10]
    Section: §5.4, §10.6
    Status: VERIFIED (μ/e), FLAGGED (τ/μ)
    """
    return G.lepton_mass_ratios()

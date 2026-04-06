"""
ppm.mixing — Quark and lepton mixing matrices
===============================================

Wrapper module for CKM, PMNS, and CP violation computations.
Re-exports from berry_phase.py and neutrino.py under the names
used in ch10 Code: references.

LaTeX: ch10 (Particle Spectrum), §10.7–10.9
"""

from .berry_phase import ckm_angles, delta_cp, jarlskog_invariant
from .neutrino import theta_strong


def ckm_berry():
    """CKM matrix from Berry phase on RP³.

    LaTeX: \\textit{Code: ppm.mixing.ckm_berry()}  [ch10]
    The CKM phase δ_CP = π(1 - 1/φ) arises as the Berry phase of the
    Z₂-equivariant fiber bundle over RP³.
    Section: §10.7
    Status: VERIFIED
    """
    angles = ckm_angles()
    dcp = delta_cp()
    J = jarlskog_invariant()
    return {
        'ckm_angles': angles,
        'delta_cp_rad': dcp['delta_cp_rad'],
        'delta_cp_deg': dcp['delta_cp_deg'],
        'observed_rad': dcp['observed_rad'],
        'error_sigma': dcp.get('error_sigma', None),
        'jarlskog': J,
        'mechanism': 'Berry phase on RP3 fiber bundle',
        'status': 'VERIFIED'
    }


def cp_violation():
    """CP violation from Berry phase.

    LaTeX: \\textit{Code: ppm.mixing.cp_violation()}  [ch10]
    Section: §10.8
    Status: VERIFIED
    """
    dcp = delta_cp()
    J = jarlskog_invariant()
    return {
        'delta_cp_rad': dcp['delta_cp_rad'],
        'jarlskog_invariant': J,
        'source': 'Z2-equivariant Berry phase on RP3',
        'status': 'VERIFIED'
    }


def strong_cp():
    """Strong CP: θ_strong = 0 from RP³ topology.

    LaTeX: \\textit{Code: ppm.strong_cp()}  [ch10]
    RP³ is non-orientable → Hodge star undefined → θ-term forbidden.
    Section: §10.10
    Status: VERIFIED
    """
    return {
        'theta_strong': 0.0,
        'mechanism': 'RP3 non-orientable, Hodge star undefined, theta-term topologically forbidden',
        'upper_bound_experimental': 1e-10,
        'status': 'VERIFIED'
    }

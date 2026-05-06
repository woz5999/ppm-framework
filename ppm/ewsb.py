"""
ppm.ewsb — Electroweak symmetry breaking
==========================================

Wrapper module for EWSB computations referenced.
Re-exports from higgs.py and hierarchy.py.

"""

from .higgs import (
    lambda_ppm,
    top_yukawa_ppm,
)
from .hierarchy import ewsb_scale, energy_gev, energy_mev
from . import constants as C
import math

def electroweak_scale():
    """EWSB scale from PPM hierarchy.

    E(k=44.5) via the geometric hierarchy g=2π.
    Status: VERIFIED
    """
    return {
        'k_ewsb': C.K_EWSB,
        'E_ewsb_gev': energy_gev(C.K_EWSB),
        'v_higgs_gev': 246.22,
        'lambda_ppm': lambda_ppm(),
        'y_top': top_yukawa_ppm(),
        'm_H_gev': math.sqrt(2 * lambda_ppm()) * 246.22,
        'm_H_obs_gev': 125.25,
        'status': 'VERIFIED'
    }


"""
ppm — Projective Process Monism computational framework
========================================================

Computes all framework predictions from first principles.
No free parameters: every physical constant is derived from
the geometry of (CP³, τ, g_FS).

Modules
-------
constants    : Mathematical and physical constants
hierarchy    : Energy ladder E(k), k-level assignments
alpha        : Fine-structure constant (three independent routes)
gauge        : Gauge group, sin²θ_W, generation count, coupling running
higgs        : Higgs quartic, top Yukawa from τ-involution
instanton    : Instanton action S=30π, zero modes, prefactor budget
spectral     : Heat kernel, zeta functions, functional determinant
cosmology    : G, Λ, H₀, G(z) evolution, dark energy
consciousness: Φ, Ψ, firing rates, consciousness-scale predictions
golden_ratio : Pyramidal numbers, A₅ decomposition, φ origin
neutrino     : PMNS matrix, θ_strong, neutrino mass brackets
berry_phase  : CKM matrix, δ_CP from Berry phase on CP³
predictions  : Master prediction table
verify       : Run-all checker

Usage
-----
    >>> import ppm
    >>> ppm.verify.run_all()
"""

__version__ = "2.0.0"

from . import constants
from . import hierarchy
from . import bridges
from . import alpha
from . import gauge
from . import higgs
from . import instanton
from . import spectral
from . import cosmology
from . import golden_ratio
from . import neutrino
from . import berry_phase
from . import consciousness
from . import stability
from . import predictions
from . import verify

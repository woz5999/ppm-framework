"""
PPM Framework — Process-Phenomenology Mapping
===============================================

Deriving physical constants from Z2 → RP3 topology.

Public API
----------
hierarchy_energy, k_from_mass, actualization_timescale
    Energy hierarchy computations (hierarchy module)

constraint_solver, predict_independent, direct_solve
    Constraint system solver and independent prediction evaluator

thermal_phase, quantum_phase, solve_alpha_from_coherence,
N_eff_from_alpha, critical_point_check
    Phase coherence and critical point analysis

cp3_invariants, neff_exponent_analysis, print_twistor_analysis
    Twistor/RG analysis of α from CP3 topology (twistor module)

PHYSICAL, FRAMEWORK, ENERGY_SCALES, TIMESCALES
    All constants (constants module)
"""

from .hierarchy import hierarchy_energy, k_from_mass, actualization_timescale
from .constraint_solver import constraint_solver, predict_independent, direct_solve
from .phase_coherence import (thermal_phase, quantum_phase, solve_alpha_from_coherence,
                              N_eff_from_alpha, critical_point_check)
from .twistor import (cp3_invariants, neff_exponent_analysis, print_twistor_analysis,
                      k_to_fs_distance, fs_distance_to_k, fs_distance_max,
                      volume_fraction_within_distance, alpha_from_volume_fraction,
                      alpha_geometric_summary)
from .constants import PHYSICAL, FRAMEWORK, ENERGY_SCALES, TIMESCALES
from .predictions import (lepton_masses, neutrino_k_levels,
                          k_conscious_temperatures, brain_power_budget,
                          gravitational_decoherence_rate,
                          self_referential_consistency,
                          ckm_cp_phase, pmns_tribimaximal,
                          hubble_constant_prediction, weak_coupling_prediction,
                          print_predictions_summary)
from .cosmology import (G_newton, G_evolution, lambda_cosmological,
                        lambda_evolution, hubble_parameter, dark_energy_eos,
                        print_cosmology_table)

__version__ = "0.1.0"

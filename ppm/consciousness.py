"""
ppm.consciousness — Consciousness-scale predictions
=====================================================

Computes integrated information Φ, phenomenal flux Ψ, and related
quantities from the fiber-coherence framework.

Key formulas (§9, sec09-consciousness.tex):

    Φ  ≈  c_Σ √N α²                    (eq:phi_formula)
    Ψ  =  Φ × ν_τ × ΔS                 (eq:phenomenal_flux)
    ΔS =  3 ln(2π) k_B  ≈  5.51 k_B    (eq:entropy_per_firing)
    ν_τ = k_B T / ℏ  (at consciousness scale, τ-firing rate)

The area-law scaling Φ ∝ √N arises from the minimum bipartition
of a 2D cortical boundary network (§9.3, eq:phi_formula).
"""

import math
from . import constants as C

# ─── Consciousness constants ─────────────────────────────────────────────────

ALPHA_EM = 1.0 / 137.036    # Fine-structure constant (observed)

DELTA_S_PER_EVENT = 3.0 * math.log(2.0 * math.pi)
# LaTeX: \Delta S = 3 k_B \ln(2\pi) \approx 5.51 k_B per event
# Section §3 (Six Bridges, eq:entropy_per_firing)
# Status: DERIVED

C_SIGMA = 0.38
# LaTeX: c_{\Sigma} \approx 0.38
# Geometric constant from cortical connectivity graph
# Determined by minimum bisection width of folded cortical sheet
# (~2600 cm² with ~10^14 synaptic sites)
# In principle computable from DTI tractography data
# Section §9.3 (eq:phi_brain)
# Status: DERIVED (geometry-dependent, not a free parameter)

N_SYNAPSES_HUMAN = 1e14      # Typical human synapse count
T_BODY_K = 310.0             # Mammalian body temperature (K)

# Physical constants
HBAR_JS = 1.0546e-34         # ℏ in J·s
K_B_JK = 1.3806e-23          # k_B in J/K

# ─── Core predictions ────────────────────────────────────────────────────────


def delta_s():
    """
    Entropy production per τ-firing event.

    LaTeX: ΔS = 3 k_B ln(2π) ≈ 5.51 k_B ≈ 7.95 bits
    Section: §3 (eq:entropy_per_firing), §9 (multiple references)

    Returns
    -------
    dict with 'nats' (in units of k_B) and 'bits' entries.
    """
    nats = DELTA_S_PER_EVENT
    bits = nats / math.log(2)
    return {'nats': nats, 'bits': bits}


def channel_capacity(k, T_K=T_BODY_K):
    """
    Information capacity per τ-firing at hierarchy level k.

    LaTeX: I(k) = 3 log₂ R(k),  where R(k) = E(k)/(k_B T)
    Section: §4 (measurement), §3 (actualization channel)

    Parameters
    ----------
    k : float
        Hierarchy level.
    T_K : float
        Temperature in Kelvin.

    Returns
    -------
    float : channel capacity in bits per event.
    """
    from .hierarchy import energy_mev
    E_mev = energy_mev(k)
    E_joules = E_mev * 1.602e-13       # MeV to J
    k_BT = K_B_JK * T_K
    R = E_joules / k_BT
    if R <= 1.0:
        return 0.0
    return 3.0 * math.log2(R)


def integrated_information(N_synapses=N_SYNAPSES_HUMAN, c_sigma=C_SIGMA, d_sigma=2):
    """
    Integrated information Φ from area-law scaling.

    LaTeX: Φ ≈ c_Σ N^{(d_Σ-1)/d_Σ} α²
    Section: §9.3 (eq:phi_formula, eq:phi_brain)

    The factors:
      N^{(d-1)/d} : minimum-cut area on d-dimensional boundary network
      α²          : per-synapse actualization probability (two τ-firings)
      c_Σ         : cortical connectivity geometry

    Parameters
    ----------
    N_synapses : float
        Number of Markov boundaries (synapses).
    c_sigma : float
        Geometric cortical constant (~0.38 for human cortex).
    d_sigma : int
        Effective dimension of boundary network.
        2 for cortical sheet (mammals), 3 for distributed ganglia (cephalopods).

    Returns
    -------
    float : Φ in nats.
    """
    exponent = (d_sigma - 1) / d_sigma
    return c_sigma * (N_synapses ** exponent) * ALPHA_EM**2


def tau_firing_rate(T_K=T_BODY_K):
    """
    τ-firing frequency at consciousness scale.

    At R(k_c) = 1, the characteristic τ-firing timescale is
    set by the thermal time: τ_sys = ℏ/(k_B T).
    The firing rate is its inverse.

    LaTeX: ν_τ = k_B T / ℏ
    Section: §9 (eq:phenomenal_flux context)

    Parameters
    ----------
    T_K : float
        Temperature in Kelvin.

    Returns
    -------
    float : ν_τ in Hz (firings per second).
    """
    return K_B_JK * T_K / HBAR_JS


def phenomenal_flux(Phi=None, nu_tau=None, Delta_S=None):
    """
    Phenomenal flux: rate of integrated entropy production.

    LaTeX: Ψ = Φ × ν_τ × ΔS
    Section: §9 (eq:phenomenal_flux)
    Units: nats · k_B · s⁻¹

    Parameters
    ----------
    Phi : float or None
        Integrated information in nats. Default: compute for human brain.
    nu_tau : float or None
        τ-firing rate in Hz. Default: compute at 310 K.
    Delta_S : float or None
        Entropy per event in units of k_B. Default: 3 ln(2π).

    Returns
    -------
    float : Ψ in nats · k_B · s⁻¹
    """
    if Phi is None:
        Phi = integrated_information()
    if nu_tau is None:
        nu_tau = tau_firing_rate()
    if Delta_S is None:
        Delta_S = DELTA_S_PER_EVENT
    return Phi * nu_tau * Delta_S


def consciousness_states():
    """
    Φ values for different consciousness states.

    Reduced Φ in sleep/anesthesia modeled as reduced effective N
    (decreased thalamocortical coupling reduces the number of
    coherently integrated synapses).

    Section: §9.3 (sec:phi_predictions), §12

    Returns
    -------
    dict : state → {'Phi_nats': float, 'N_eff': float, 'description': str}
    """
    states = {}
    # Awake: full integration
    N_awake = N_SYNAPSES_HUMAN
    states['awake'] = {
        'Phi_nats': integrated_information(N_awake),
        'N_eff': N_awake,
        'description': 'Full thalamocortical integration'
    }
    # Light sleep (N1): reduced coupling
    # Φ ~ 80 nats → N_eff = (80/(c_Σ α²))² ≈ 2.2e13
    N_n1 = (80.0 / (C_SIGMA * ALPHA_EM**2))**2
    states['light_sleep_N1'] = {
        'Phi_nats': integrated_information(N_n1),
        'N_eff': N_n1,
        'description': 'Reduced thalamocortical coupling'
    }
    # Deep sleep (N3): local columns only
    N_n3 = (10.0 / (C_SIGMA * ALPHA_EM**2))**2
    states['deep_sleep_N3'] = {
        'Phi_nats': integrated_information(N_n3),
        'N_eff': N_n3,
        'description': 'Fiber coherence confined to local cortical columns'
    }
    # Anesthesia
    N_anes = (5.0 / (C_SIGMA * ALPHA_EM**2))**2
    states['anesthesia'] = {
        'Phi_nats': integrated_information(N_anes),
        'N_eff': N_anes,
        'description': 'Global fiber section destroyed; local fragments only'
    }
    return states


def phi_scaling_prediction(N_values=None):
    """
    Testable prediction: Φ ∝ √N across species/systems.

    Section: §9.3 (sec:phi_predictions)

    Parameters
    ----------
    N_values : list of float or None
        Synapse counts to evaluate. Default: representative species.

    Returns
    -------
    list of dict : [{species, N, Phi_nats}, ...]
    """
    if N_values is None:
        # Note: c_sigma=0.38 is calibrated for human cortex (d=2).
        # For d=3 architectures, c_sigma would differ (depends on
        # specific connectivity graph). The d=3 entries show the
        # exponent effect only, not absolute Phi.
        species_data = [
            ('C. elegans', 7000, 2),
            ('Drosophila', 1e7, 2),
            ('Mouse', 8e10, 2),
            ('Octopus (d=2)', 5e11, 2),
            ('Cat', 1e13, 2),
            ('Human', 1e14, 2),
            ('Elephant', 3e14, 2),
        ]
    else:
        species_data = [(f'N={N:.1e}', N, 2) for N in N_values]

    return [
        {'species': name, 'N': N, 'd_sigma': d,
         'Phi_nats': integrated_information(N, d_sigma=d)}
        for name, N, d in species_data
    ]


# ─── Standalone runner ────────────────────────────────────────────────────────

def _verify():
    """Print all consciousness-scale predictions for verification."""
    print("=" * 60)
    print("PPM Consciousness-Scale Predictions")
    print("=" * 60)

    ds = delta_s()
    print(f"\nΔS per event: {ds['nats']:.3f} nats = {ds['bits']:.3f} bits")

    phi_awake = integrated_information()
    print(f"\nΦ (awake human): {phi_awake:.1f} nats")
    print(f"  √N = {math.sqrt(N_SYNAPSES_HUMAN):.2e}")
    print(f"  α² = {ALPHA_EM**2:.5e}")
    print(f"  c_Σ = {C_SIGMA}")

    nu = tau_firing_rate()
    print(f"\nν_τ (310 K): {nu:.3e} Hz")

    psi = phenomenal_flux()
    print(f"\nΨ (phenomenal flux): {psi:.3e} nats·k_B·s⁻¹")

    print(f"\nChannel capacity at k=51 (particle): {channel_capacity(51):.1f} bits")
    print(f"Channel capacity at k=75 (consciousness): {channel_capacity(75):.3f} bits")

    print("\nConsciousness states:")
    for state, data in consciousness_states().items():
        print(f"  {state:20s}: Φ = {data['Phi_nats']:7.1f} nats  "
              f"(N_eff = {data['N_eff']:.2e})")

    print("\nScaling prediction (Φ ∝ N^{(d-1)/d}):")
    for row in phi_scaling_prediction():
        print(f"  {row['species']:20s}: N = {row['N']:.1e}, d={row['d_sigma']}, "
              f"Φ = {row['Phi_nats']:.2f} nats")


if __name__ == '__main__':
    _verify()

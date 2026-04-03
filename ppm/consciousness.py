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

Additional sections:
    CP³ spectral Z₂ decomposition (§2, actualization operator formalism)
    Lindblad decoherence rates (§2, Penrose-Diósi gravitational decoherence)
    Consciousness k-window (§9, Zeno lower bound and Landauer upper bound)
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


# ─── CP³ spectral Z₂ decomposition ──────────────────────────────────────────
#
# From: archive/scripts/actualization_operator.py
# Section: §2 (τ involution, actualization operator formalism)
#
# The τ involution (complex conjugation on CP³) decomposes each Laplacian
# eigenspace V_k into τ-even (RP³-compatible) and τ-odd subspaces.
# The actualization operator Â is the orthogonal projection onto V⁺ = ⊕_k V_k⁺.


def cp3_spectral_data(k_max=20):
    """
    Z₂ decomposition of CP³ Laplacian eigenspaces under τ.

    For each eigenspace V_k:
        eigenvalue:       λ_k = k(k+3)
        total dimension:  d_k = C(k+3,3)² − C(k+2,3)²   [k>0]
        τ-even dimension: d_k⁺ = (d_k + tr(τ|V_k)) / 2
        τ-odd dimension:  d_k⁻ = (d_k − tr(τ|V_k)) / 2
        where tr(τ|V_k)  = C(k+3,3) − C(k+2,3)          [k>0]

    The τ-even states span the harmonic analysis on RP³ = Fix(τ).
    Asymptotically d⁺/d → 1/2 (spectral democracy at high k).

    Section: §2 (actualization operator)
    Status: DERIVED

    Parameters
    ----------
    k_max : int
        Maximum eigenspace index to compute.

    Returns
    -------
    list of dict : [{k, eigenvalue, d_total, d_plus, d_minus, tr_tau}, ...]
    """
    def _comb(n, r):
        """Binomial coefficient C(n, r)."""
        if r < 0 or r > n:
            return 0
        result = 1
        for i in range(min(r, n - r)):
            result = result * (n - i) // (i + 1)
        return result

    data = []
    for k in range(k_max + 1):
        eigenvalue = k * (k + 3)
        d_total = _comb(k + 3, 3) ** 2 - (_comb(k + 2, 3) ** 2 if k > 0 else 0)
        tr_tau = _comb(k + 3, 3) - (_comb(k + 2, 3) if k > 0 else 0)
        d_plus = (d_total + tr_tau) // 2
        d_minus = (d_total - tr_tau) // 2
        data.append({
            'k': k,
            'eigenvalue': eigenvalue,
            'd_total': d_total,
            'd_plus': d_plus,
            'd_minus': d_minus,
            'tr_tau': tr_tau,
        })
    return data


# ─── Lindblad decoherence rates ─────────────────────────────────────────────
#
# From: archive/scripts/actualization_operator.py
# Section: §2 (Lindblad master equation for actualization)
#
# The actualization dissipator D[ρ] = Σ_b Γ_b (Â ρ Â − ½{Â, ρ}) drives
# τ-odd components to zero with rate Γ_b = Gm²/ℏ (Penrose-Diósi).
# The decoherence time for τ-odd suppression: τ_dec = 2ℏ/(Gm²).


def decoherence_time(m_kg):
    """
    Lindblad decoherence time for τ-odd suppression.

    LaTeX: τ_{\\rm dec} = \\frac{2\\hbar}{G m^2}
    Section: §2 (Lindblad dynamics)
    Status: DERIVED

    This is the Penrose-Diósi gravitational decoherence time,
    recovered here as the Lindblad dissipation timescale for the
    actualization operator Â on CP³.

    Parameters
    ----------
    m_kg : float
        Mass of the boundary system in kg.

    Returns
    -------
    float : decoherence time in seconds.
    """
    return 2.0 * HBAR_JS / (C.G_NEWTON_SI * m_kg ** 2)


def decoherence_rate(m_kg):
    """
    Lindblad dissipation rate Γ = Gm²/ℏ.

    Section: §2 (Lindblad dynamics)
    Status: DERIVED

    Parameters
    ----------
    m_kg : float
        Mass of the boundary system in kg.

    Returns
    -------
    float : rate in Hz.
    """
    return C.G_NEWTON_SI * m_kg ** 2 / HBAR_JS


def decoherence_table():
    """
    Decoherence times at representative mass scales.

    Returns
    -------
    list of dict : [{label, m_kg, gamma_hz, tau_dec_s}, ...]
    """
    eV_per_c2 = 1.602e-19 / (3e8) ** 2  # eV/c² in kg
    entries = [
        ('Planck mass', 2.176e-8),
        ('Dust grain (1μm)', 1e-15),
        ('Proton', 1.673e-27),
        ('Pion', 134.98e6 * eV_per_c2),
        ('Bacterium', 1e-15),
        ('Cat', 5.0),
        ('Human brain', 1.4),
    ]
    return [
        {
            'label': label,
            'm_kg': m,
            'gamma_hz': decoherence_rate(m),
            'tau_dec_s': decoherence_time(m),
        }
        for label, m in entries
    ]


# ─── Consciousness k-window ─────────────────────────────────────────────────
#
# From: archive/scripts/k_conscious_window.py
# Section: §9 (consciousness constraints)
#
# Two independent constraints bound the k-level at which consciousness
# can operate:
#   Lower (Zeno): E(k) < m_π / (4π)  →  k > 53.8
#   Upper (Landauer): E(k) > k_BT ln 2  →  k < ~75.75 at 310 K
#
# The universal margin Δk = 2 ln(1/ln 2) / ln(2π) ≈ 0.40 is
# temperature-independent.


def consciousness_window(T_K=T_BODY_K):
    """
    Allowed k-window for consciousness at temperature T.

    Lower bound (Zeno protection):
        The Zeno-protected coherence time t_Z = τ_sys²/τ_bath must exceed
        the 720° completion time τ_720 = 4π τ_sys. This requires
        E_bath/E(k) > 4π, i.e. E(k) < m_π/(4π).

    Upper bound (Landauer maintenance):
        The Z₂ boundary must carry at least one bit of topological
        information per cycle: E(k) > k_BT ln 2.

    Universal margin:
        Δk = k_max − k_thermal = 2 ln(1/ln 2) / ln(2π) ≈ 0.40
        This is temperature-independent.

    Section: §9 (consciousness constraints)
    Status: DERIVED

    Parameters
    ----------
    T_K : float
        Temperature in Kelvin.

    Returns
    -------
    dict with keys:
        k_min        : float — Zeno lower bound
        k_max        : float — Landauer upper bound
        k_thermal    : float — k-level where E(k) = k_BT
        width        : float — window width in k-levels
        margin       : float — universal margin Δk ≈ 0.40
        E_min_eV     : float — energy at lower bound (eV)
        E_max_eV     : float — energy at upper bound (eV)
    """
    from .hierarchy import energy_mev

    # Energy scales
    E_pi_J = C.M_PI_MEV * 1e6 * 1.602e-19  # pion mass in Joules
    k_BT = K_B_JK * T_K
    ln2pi = math.log(C.TAU)

    # k from energy: k = 51 - 2 ln(E_J / E_pi_J) / ln(2π)
    # where E_J is energy in Joules
    def _k_from_E_J(E_J):
        return C.K_REF - 2.0 * math.log(E_J / E_pi_J) / ln2pi

    # Lower bound: E(k) < E_pi / (4π)
    k_min = _k_from_E_J(E_pi_J / (4.0 * math.pi))

    # Upper bound: E(k) > k_BT ln 2
    k_max = _k_from_E_J(k_BT * math.log(2.0))

    # Thermal k-level: E(k) = k_BT
    k_thermal = _k_from_E_J(k_BT)

    # Universal margin (temperature-independent)
    margin = 2.0 * math.log(1.0 / math.log(2.0)) / ln2pi

    # Convert boundary energies to eV
    E_min_eV = (E_pi_J / (4.0 * math.pi)) / 1.602e-19
    E_max_eV = (k_BT * math.log(2.0)) / 1.602e-19

    return {
        'k_min': k_min,
        'k_max': k_max,
        'k_thermal': k_thermal,
        'width': k_max - k_min,
        'margin': margin,
        'E_min_eV': E_min_eV,
        'E_max_eV': E_max_eV,
    }


def consciousness_window_temperature_scan(T_values=None):
    """
    Consciousness window parameters across a range of temperatures.

    Section: §9 (temperature dependence of consciousness window)
    Status: DERIVED

    Parameters
    ----------
    T_values : list of float or None
        Temperatures in Kelvin. Default: biologically relevant range.

    Returns
    -------
    list of dict : [{T_K, k_min, k_max, k_thermal, width}, ...]
    """
    if T_values is None:
        T_values = [4, 77, 200, 273, 300, 310, 350, 500, 1000, 5000]

    results = []
    for T in T_values:
        w = consciousness_window(T)
        results.append({
            'T_K': T,
            'k_min': w['k_min'],
            'k_max': w['k_max'],
            'k_thermal': w['k_thermal'],
            'width': w['width'],
        })
    return results


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

    # CP³ spectral decomposition
    print(f"\nCP³ spectral Z₂ decomposition (first 10 levels):")
    print(f"  {'k':>3s} {'λ_k':>6s} {'d_k':>6s} {'d⁺':>6s} {'d⁻':>6s} {'d⁺/d_k':>8s}")
    for d in cp3_spectral_data(9):
        ratio = d['d_plus'] / d['d_total'] if d['d_total'] > 0 else 0
        print(f"  {d['k']:3d} {d['eigenvalue']:6d} {d['d_total']:6d} "
              f"{d['d_plus']:6d} {d['d_minus']:6d} {ratio:8.4f}")

    # Decoherence table
    print(f"\nLindblad decoherence times τ_dec = 2ℏ/(Gm²):")
    for row in decoherence_table():
        print(f"  {row['label']:>20s}: Γ = {row['gamma_hz']:.2e} Hz, "
              f"τ_dec = {row['tau_dec_s']:.2e} s")

    # Consciousness window
    print(f"\nConsciousness k-window (T = 310 K):")
    w = consciousness_window()
    print(f"  k_min (Zeno)     = {w['k_min']:.2f}")
    print(f"  k_max (Landauer) = {w['k_max']:.2f}")
    print(f"  k_thermal        = {w['k_thermal']:.2f}")
    print(f"  Width            = {w['width']:.2f} levels")
    print(f"  Universal margin = {w['margin']:.4f}")


if __name__ == '__main__':
    _verify()

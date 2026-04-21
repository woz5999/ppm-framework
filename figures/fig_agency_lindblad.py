"""
fig_agency_lindblad.py — Decoherence hierarchy and motor reliability

Two-panel figure:
  Panel 1: Decoherence time τ_dec vs mass (log-log)
           Marks key masses: proton, pion, dust grain, bacterium
  Panel 2: N_reliable vs motor response time
           Matches corticospinal tract anatomy (~10⁵-10⁶ fibers)
           PPM prediction ≈ 4.9×10⁵

Run: python fig_agency_lindblad.py
"""

import sys
sys.path.insert(0, '../')

import numpy as np
import matplotlib.pyplot as plt
from _style import new_figure_multi, save, GOLD, CYAN, WHITE, GRAY, ORANGE

from ppm.cosmology import n_reliable, integration_time


def decoherence_time(m_kg):
    """Penrose-Diósi decoherence time: τ_dec = 2ℏ² / (Gm³c)"""
    G = 6.674e-11
    hbar = 1.0546e-34
    c = 2.998e8
    return 2.0 * hbar**2 / (G * m_kg**3 * c)


def main():
    fig, (ax1, ax2) = new_figure_multi(1, 2, width=14, height=5.5)

    # ─── Panel 1: Decoherence time vs mass ───────────────────────────────────
    # Log-log plot from Planck mass to 10 kg
    masses_kg = np.logspace(-8, 1, 200)  # Planck to 10 kg
    tau_dec_s = [decoherence_time(m) for m in masses_kg]

    ax1.loglog(masses_kg, tau_dec_s, color=GOLD, linewidth=2.5, label=r'$\tau_{\rm dec} = 2\hbar^2/(Gm^3c)$')

    # Mark key particles/objects
    particles = [
        (1.673e-27, 'Proton', CYAN),
        (2.407e-28, 'Pion', ORANGE),
        (1e-15, 'Dust grain', CYAN),
        (1e-12, 'Bacterium', ORANGE),
    ]

    for mass, name, color in particles:
        tau = decoherence_time(mass)
        ax1.plot(mass, tau, 'o', color=color, markersize=9, zorder=10)
        # Offset labels for readability
        offset_x = 10**(np.log10(mass) + 0.4)
        offset_y = 10**(np.log10(tau) + 0.3)
        ax1.text(offset_x, offset_y, name, fontsize=10, color=color, weight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a1a', edgecolor=color, alpha=0.8))

    ax1.set_xlabel('Mass [kg]', fontsize=12, color=WHITE, weight='bold')
    ax1.set_ylabel(r'Decoherence Time $\tau_{\rm dec}$ [s]', fontsize=12, color=WHITE, weight='bold')
    ax1.set_title('Penrose-Diósi Decoherence Hierarchy\nGravity-Induced Wave Function Collapse',
                  fontsize=12, color=WHITE, weight='bold')
    ax1.grid(True, which='both', alpha=0.3, color='#1a1a2e')
    ax1.legend(fontsize=11, loc='upper left')

    # ─── Panel 2: N_reliable vs motor response time ──────────────────────────
    t_motor_ms = np.linspace(50, 250, 100)
    t_motor_s = t_motor_ms / 1000.0

    N_rel_vals = []
    for t_m in t_motor_s:
        result = n_reliable(Delta_m=1e-14, t_motor=t_m, T_K=310.0)
        N_rel_vals.append(result['N_reliable'])

    ax2.plot(t_motor_ms, N_rel_vals, color=GOLD, linewidth=2.5, label='PPM prediction')
    ax2.fill_between(t_motor_ms, 0, N_rel_vals, alpha=0.15, color=GOLD)

    # Mark PPM baseline (t=150 ms)
    t_baseline = 150.0  # ms
    N_baseline = n_reliable(Delta_m=1e-14, t_motor=t_baseline/1000.0, T_K=310.0)['N_reliable']
    ax2.plot(t_baseline, N_baseline, 'o', color=CYAN, markersize=12, zorder=10)
    ax2.annotate(f'Standard motor response\nt = {t_baseline:.0f} ms\n$N_{{rel}} = {N_baseline:.1e}$',
                 xy=(t_baseline, N_baseline), xytext=(t_baseline+40, N_baseline*1.2),
                 fontsize=11, color=WHITE, weight='bold',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='#0a0a1a',
                          edgecolor=CYAN, alpha=0.9, linewidth=2),
                 arrowprops=dict(arrowstyle='->', color=CYAN, lw=2, mutation_scale=20))

    # Shade corticospinal tract range (10^5 to 10^6 fibers)
    ax2.axhspan(1e5, 1e6, alpha=0.15, color='#00CED1', label='Corticospinal anatomy (10⁵–10⁶)')

    ax2.set_xlabel('Motor Response Time [ms]', fontsize=12, color=WHITE, weight='bold')
    ax2.set_ylabel(r'Reliability Threshold: $N_{\rm reliable}$', fontsize=12, color=WHITE, weight='bold')
    ax2.set_title('Motor Agency and Quantum Reliability\nPPM matches neural anatomy',
                  fontsize=12, color=WHITE, weight='bold')
    ax2.set_yscale('log')
    ax2.grid(True, which='both', alpha=0.3, color='#1a1a2e')
    ax2.legend(fontsize=11, loc='upper right')

    plt.tight_layout()
    save(fig, 'fig_agency_lindblad.png')


if __name__ == '__main__':
    main()

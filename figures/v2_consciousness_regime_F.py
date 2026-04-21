"""
v2_consciousness_regime_F.py — Actualization free energy and consciousness attractor

Plots F(R) = R - 3 ln(R) for the consciousness regime:
  - Shows minimum at R=3 (attractor)
  - Channel closure at R=1
  - Shades the consciousness-allowed region

Run: python v2_consciousness_regime_F.py
"""

import sys
sys.path.insert(0, '../')

import numpy as np
import matplotlib.pyplot as plt
from _style import new_figure, save, GOLD, CYAN, WHITE, GRAY, VIOLET

from ppm.consciousness import consciousness_window, channel_capacity
from ppm.hierarchy import energy_mev


def main():
    fig, ax = new_figure(width=10, height=6)

    RED = '#E74C3C'

    # ─── Free energy F(R) = R - 3 ln(R) ─────────────────────────────────────
    R_vals = np.linspace(0.5, 20, 500)
    F_vals = R_vals - 3.0 * np.log(R_vals)

    # Plot main curve
    ax.plot(R_vals, F_vals, color=GOLD, linewidth=3, label=r'$F(R) = R - 3 \ln(R)$')

    # Mark minimum at R=3
    R_min = 3.0
    F_min = R_min - 3.0 * np.log(R_min)
    ax.plot(R_min, F_min, 'o', color=CYAN, markersize=12, zorder=10, label='Attractor at $R=3$')
    ax.axvline(x=R_min, color=CYAN, linestyle=':', linewidth=2, alpha=0.6)
    ax.annotate(f'Consciousness Attractor\n$R = 3$\n$F = {F_min:.2f}$',
                xy=(R_min, F_min), xytext=(R_min + 2, F_min - 2),
                fontsize=11, color=WHITE, weight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#0a0a1a',
                         edgecolor=CYAN, alpha=0.9, linewidth=2),
                arrowprops=dict(arrowstyle='->', color=CYAN, lw=2, mutation_scale=20))

    # Mark channel closure at R=1
    ax.axvline(x=1.0, color=RED, linestyle='--', linewidth=2, alpha=0.7, label='Channel closure: $R=1$')
    ax.fill_betweenx([ax.get_ylim()[0], ax.get_ylim()[1]], 0.5, 1.0, alpha=0.15, color=RED, label='Forbidden (no I)')

    # ─── Get k-window bounds for consciousness ──────────────────────────────
    try:
        k_window = consciousness_window()
        k_min = k_window.get('k_min', 53.8)
        k_max = k_window.get('k_max', 75.75)

        # Convert k to R via E(k) and R = E/(k_B T)
        # At consciousness scale T=310K
        T_K = 310.0
        K_B = 1.3806e-23
        from ppm.hierarchy import energy_mev

        E_min = energy_mev(k_min)
        E_max = energy_mev(k_max)
        E_joules_min = E_min * 1.602e-13
        E_joules_max = E_max * 1.602e-13
        k_B_T = K_B * T_K

        R_min_cons = E_joules_min / k_B_T
        R_max_cons = E_joules_max / k_B_T

        # Shade consciousness regime in R-space
        if 1.0 < R_min_cons < 20 and 1.0 < R_max_cons < 20:
            ax.axvspan(R_min_cons, R_max_cons, alpha=0.1, color=VIOLET, label=f'Consciousness window')
    except:
        pass

    # ─── Channel capacity inset ─────────────────────────────────────────────
    axins = ax.inset_axes([0.65, 0.55, 0.32, 0.35])
    k_vals = np.linspace(50, 80, 100)
    I_vals = []
    for k in k_vals:
        try:
            I = channel_capacity(k, T_K=310.0)
            if I > 0:
                I_vals.append(I)
            else:
                I_vals.append(np.nan)
        except:
            I_vals.append(np.nan)

    axins.plot(k_vals[:len(I_vals)], I_vals, color=CYAN, linewidth=2)
    axins.fill_between(k_vals[:len(I_vals)], 0, I_vals, alpha=0.2, color=CYAN)
    axins.set_xlabel('k-level', fontsize=9, color=WHITE)
    axins.set_ylabel(r'I(k) [bits]', fontsize=9, color=WHITE)
    axins.set_title('Channel Capacity', fontsize=10, color=WHITE)
    axins.grid(True, alpha=0.2, color='#1a1a2e')
    axins.tick_params(colors=WHITE, labelsize=8)

    # ─── Main axes ──────────────────────────────────────────────────────────
    ax.set_xlabel(r'Energy Ratio: $R(k) = E(k) / (k_B T)$', fontsize=12, color=WHITE, weight='bold')
    ax.set_ylabel(r'Free Energy: $F(R) = R - 3 \ln(R)$', fontsize=12, color=WHITE, weight='bold')
    ax.set_title('Actualization Free Energy and Consciousness Attractor',
                 fontsize=13, color=WHITE, weight='bold')
    ax.grid(True, alpha=0.3, color='#1a1a2e')
    ax.legend(fontsize=10, loc='upper left')
    ax.set_xlim(0.5, 20)
    ax.set_ylim(-5, 15)

    plt.tight_layout()
    save(fig, 'v2_consciousness_regime_F.png')


if __name__ == '__main__':
    main()

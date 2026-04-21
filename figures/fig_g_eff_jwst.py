"""
fig_g_eff_jwst.py — G_eff(z) enhancement and PPM collapse threshold

Two subplots showing:
  - Left: G_eff/G_0 = (1+z)^{3/2} vs z (JWST early galaxies prediction)
  - Right: δ_c^PPM(z) vs z compared to standard threshold

Run: python fig_g_eff_jwst.py
"""

import sys
sys.path.insert(0, '../')

import numpy as np
import matplotlib.pyplot as plt
from _style import new_figure_multi, save, GOLD, GRAY, WHITE, CYAN

# Import PPM modules
from ppm.cosmology import g_eff, delta_c_ppm


def main():
    fig, (ax1, ax2) = new_figure_multi(1, 2, width=14, height=5)

    # ─── Left panel: G_eff(z) ───────────────────────────────────────────────
    z_vals = np.linspace(0, 15, 200)
    g_eff_vals = [g_eff(z) for z in z_vals]

    ax1.plot(z_vals, g_eff_vals, color=GOLD, linewidth=2.5, label=r'$G_{\rm eff}(z) = (1+z)^{3/2}$')
    ax1.axhline(y=1, color=GRAY, linestyle='--', linewidth=1, alpha=0.7, label=r'$G_0$')

    # Mark key redshifts
    z_markers = [6, 10, 12]
    for z in z_markers:
        g = g_eff(z)
        ax1.plot(z, g, 'o', color=CYAN, markersize=8)
        ax1.annotate(f'z={z}\n$G_{{eff}}$={g:.1f}$G_0$',
                     xy=(z, g), xytext=(z+0.5, g+3),
                     fontsize=10, color=WHITE,
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a1a', edgecolor=CYAN, alpha=0.8),
                     arrowprops=dict(arrowstyle='->', color=CYAN, lw=1.5))

    ax1.set_xlabel('Redshift $z$', fontsize=12, color=WHITE)
    ax1.set_ylabel(r'$G_{\rm eff}/G_0$', fontsize=12, color=WHITE)
    ax1.set_title('Early Structure Formation\nG$_{\\mathrm{eff}}$(z) Enhancement', fontsize=13, color=WHITE)
    ax1.grid(True, alpha=0.3, color='#1a1a2e')
    ax1.legend(fontsize=11, loc='upper left')
    ax1.set_xlim(0, 15)
    ax1.set_ylim(0, 50)

    # ─── Right panel: δ_c^PPM(z) ────────────────────────────────────────────
    delta_c_ppm_vals = [delta_c_ppm(z) for z in z_vals]
    delta_c_std = 1.686

    ax2.plot(z_vals, delta_c_ppm_vals, color=GOLD, linewidth=2.5, label=r'$\delta_c^{\rm PPM}(z)$')
    ax2.axhline(y=delta_c_std, color=GRAY, linestyle='--', linewidth=1.5, alpha=0.7, label=r'$\delta_c^{\rm std} = 1.686$')
    ax2.fill_between(z_vals, 0, delta_c_ppm_vals, alpha=0.15, color=GOLD)

    # Annotate enhancement at z=10
    z_test = 10
    dc_ppm = delta_c_ppm(z_test)
    ratio = delta_c_std / dc_ppm
    ax2.plot(z_test, dc_ppm, 'o', color=CYAN, markersize=8)
    ax2.annotate(f'z={z_test}\n$\\delta_c^{{PPM}}$={dc_ppm:.3f}\n{ratio:.1f}× easier',
                 xy=(z_test, dc_ppm), xytext=(z_test+2, dc_ppm+0.3),
                 fontsize=10, color=WHITE,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a1a', edgecolor=CYAN, alpha=0.8),
                 arrowprops=dict(arrowstyle='->', color=CYAN, lw=1.5))

    ax2.set_xlabel('Redshift $z$', fontsize=12, color=WHITE)
    ax2.set_ylabel(r'Collapse Threshold $\delta_c$', fontsize=12, color=WHITE)
    ax2.set_title('Modified Collapse Threshold\nEnables Early Halo Formation', fontsize=13, color=WHITE)
    ax2.grid(True, alpha=0.3, color='#1a1a2e')
    ax2.legend(fontsize=11, loc='upper right')
    ax2.set_xlim(0, 15)
    ax2.set_ylim(0.5, 2.0)

    plt.tight_layout()
    save(fig, 'fig_g_eff_jwst.png')


if __name__ == '__main__':
    main()

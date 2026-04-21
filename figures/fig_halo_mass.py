"""
fig_halo_mass.py — Halo mass function enhancement at high redshift

Visualizes how lower collapse threshold enables higher halo abundance at z > 6.
Shows δ_c^PPM / δ_c^std and corresponding enhancement factor.

Run: python fig_halo_mass.py
"""

import sys
sys.path.insert(0, '../')

import numpy as np
import matplotlib.pyplot as plt
from _style import new_figure, save, GOLD, CYAN, WHITE, GRAY

from ppm.cosmology import delta_c_ppm


def main():
    fig, ax = new_figure(width=10, height=6)

    z_vals = np.linspace(0, 15, 200)
    delta_c_std = 1.686

    # Collapse threshold ratio
    delta_c_ppm_vals = np.array([delta_c_ppm(z) for z in z_vals])
    ratio = delta_c_std / delta_c_ppm_vals  # Higher = more abundant halos

    # Plot enhancement factor
    ax.plot(z_vals, ratio, color=GOLD, linewidth=3, label='Halo abundance enhancement')
    ax.fill_between(z_vals, 1.0, ratio, alpha=0.2, color=GOLD)

    # Mark key redshifts (JWST era)
    z_jwst = [6, 8, 10, 12]
    for z in z_jwst:
        r = delta_c_std / delta_c_ppm(z)
        ax.plot(z, r, 'o', color=CYAN, markersize=10)

    # Special annotation for z=10
    z_test = 10
    r_test = delta_c_std / delta_c_ppm(z_test)
    ax.annotate(f'z={z_test}\n{r_test:.2f}× more halos\nδ_c 2.5× lower',
                xy=(z_test, r_test), xytext=(z_test+1.5, r_test+0.3),
                fontsize=11, color=WHITE, weight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#0a0a1a',
                         edgecolor=CYAN, alpha=0.9, linewidth=2),
                arrowprops=dict(arrowstyle='->', color=CYAN, lw=2, mutation_scale=20))

    # Add z=6 JWST marker
    r_6 = delta_c_std / delta_c_ppm(6)
    ax.plot(6, r_6, 's', color=CYAN, markersize=8)
    ax.text(6, r_6-0.08, 'z=6\nJWST', fontsize=9, ha='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a1a',
                     edgecolor=CYAN, alpha=0.8, linewidth=1))

    ax.axhline(y=1.0, color=GRAY, linestyle='--', linewidth=1.5, alpha=0.6, label='ΛCDM baseline')
    ax.set_xlabel('Redshift $z$', fontsize=12, color=WHITE, weight='bold')
    ax.set_ylabel(r'Halo Abundance Ratio: $\delta_c^{\rm std} / \delta_c^{\rm PPM}$',
                  fontsize=12, color=WHITE, weight='bold')
    ax.set_title('Halo Mass Function Enhancement at High Redshift\nPPM enables abundant structure before z=6',
                 fontsize=13, color=WHITE, weight='bold')
    ax.grid(True, alpha=0.3, color='#1a1a2e')
    ax.legend(fontsize=11, loc='upper right')
    ax.set_xlim(0, 15)
    ax.set_ylim(0.9, 2.8)

    # Info box
    info = ('Lower collapse threshold → lower matter density needed\n'
            'for gravitational collapse → earlier galaxy formation\n'
            'Resolves JWST "impossible galaxies" at z>6 without\n'
            'invoking extreme (Z>10) metallicities or mergers')
    ax.text(0.02, 0.35, info, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='#1a1a2e', edgecolor=GOLD, alpha=0.85, pad=0.8),
            color=WHITE, family='monospace')

    plt.tight_layout()
    save(fig, 'fig_halo_mass.png')


if __name__ == '__main__':
    main()

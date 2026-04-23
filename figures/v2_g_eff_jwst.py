"""
v2_g_eff_jwst.py — G_eff(z) Enhancement and JWST Early Galaxy Anomalies

Redesigned single panel showing:
  - PPM prediction: G_eff = (1+z)^{3/2}
  - GR baseline: G_eff = 1
  - JWST observational data: stellar mass excess factors with error bars
  - Visual connection between enhancement factors and PPM curve

Run: python v2_g_eff_jwst.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from _style import apply_style, save, GOLD, GRAY, WHITE, CYAN, RED, BG
from ppm.cosmology import g_eff

apply_style()

# Override key sizes
plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 22,
    'axes.labelsize': 18,
    'xtick.labelsize': 15,
    'ytick.labelsize': 15,
    'legend.fontsize': 15,
})

fig, ax = plt.subplots(figsize=(14, 9))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# PPM prediction curve
z_vals = np.linspace(0, 15, 300)
g_eff_vals = [g_eff(z) for z in z_vals]
ax.plot(z_vals, g_eff_vals, color=GOLD, linewidth=3.5,
        label=r'PPM: $G_{\rm eff}(z) = (1+z)^{3/2}$', zorder=3)

# GR baseline
ax.axhline(1.0, color=GRAY, linewidth=2.5, linestyle='--', alpha=0.7,
           label=r'GR: $G_{\rm eff} = G_0$')

# JWST observational data (approximate excess factors from Labbé+ 2023, Boylan-Kolchin 2023)
z_obs = np.array([6.0, 7.5, 9.0, 10.5, 12.0])
excess_obs = np.array([3.5, 6.0, 10.0, 16.0, 25.0])
excess_err = np.array([1.5, 2.5, 4.0, 6.0, 10.0])

# Plot JWST data with error bars
ax.errorbar(z_obs, excess_obs, yerr=excess_err, fmt='o', color=CYAN, markersize=13,
            markeredgecolor=WHITE, markeredgewidth=2, capsize=6, capthick=2.5,
            elinewidth=2.5, label='JWST excess (approx.)', zorder=4)

# Fill between PPM curve and GR to show enhancement
ax.fill_between(z_vals, 1, g_eff_vals, alpha=0.12, color=GOLD)

ax.set_xlabel('Redshift $z$', fontsize=18, color=WHITE)
ax.set_ylabel(r'$G_{\rm eff}/G_0$ (or mass excess factor)', fontsize=18, color=WHITE)
ax.set_title(r'$G_{\rm eff}(z)$ Enhancement and JWST Early Galaxy Anomalies',
             fontsize=22, color=WHITE, pad=15)
ax.set_xlim(0, 15)
ax.set_ylim(0, 70)
ax.grid(True, alpha=0.3, linestyle=':', which='both')
ax.legend(fontsize=19, loc='upper left', markerscale=1.3,
          handlelength=2.5, framealpha=0.85)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(1.5)
ax.spines['left'].set_linewidth(1.5)

plt.tight_layout()
save(fig, 'v2_g_eff_jwst.png')

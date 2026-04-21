"""
fig_energy_hierarchy.py — PPM energy hierarchy: predicted vs observed masses

Plots the energy ladder E(k) = 140 MeV × (2π)^{(51-k)/2} with observed particle
masses scattered at their k-levels, colored by category (lepton, quark, boson, meson).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, new_figure, save, CAT_COLORS, GRAY, WHITE
from ppm import hierarchy
from ppm.constants import TAU

# Get k-level table
k_table = hierarchy.k_level_table()

# Create figure
fig, ax = new_figure(width=11, height=7)

# Generate continuous E(k) curve
k_curve = np.logspace(0, 1.8, 300)  # k from 1 to ~60
E_curve = np.array([hierarchy.energy_gev(k) for k in k_curve])

# Plot E(k) curve
ax.loglog(k_curve, E_curve, color=WHITE, linewidth=2.5, label='E(k) = 140 MeV × (2π)$^{(51-k)/2}$', zorder=1)

# Plot particles
for row in k_table:
    if row['mass_observed_GeV'] is not None and row['mass_observed_GeV'] > 0:
        cat = row['category']
        color = CAT_COLORS.get(cat, GRAY)
        ax.scatter(row['k'], row['mass_observed_GeV'], s=120, color=color,
                  edgecolor=WHITE, linewidth=1.5, zorder=3, alpha=0.85)

        # Label particles
        if row['name'] not in ['UV boundary', 'Pati-Salam']:
            ax.text(row['k'] * 1.08, row['mass_observed_GeV'] * 1.05,
                   row['name'], fontsize=9, color=WHITE, ha='left', va='bottom')

# Mark key scales with vertical lines
key_scales = [
    (1.0, 'Planck', GRAY),
    (16.25, 'Pati-Salam', GRAY),
    (44.5, 'EWSB', GRAY),
    (51.0, 'Pion', GRAY),
    (57.0, 'Electron', GRAY),
]

for k, label, color in key_scales:
    E = hierarchy.energy_gev(k)
    ax.axvline(k, color=color, linestyle=':', alpha=0.4, linewidth=1)

# Formatting
ax.set_xlabel('k-level', fontsize=13, fontweight='bold')
ax.set_ylabel('Energy (GeV)', fontsize=13, fontweight='bold')
ax.set_title('PPM energy hierarchy: predicted vs observed', fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(0.5, 100)
ax.set_ylim(1e-4, 1e20)
ax.grid(True, alpha=0.2, which='both', linestyle='-')

# Legend for categories
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=CAT_COLORS['lepton'], edgecolor=WHITE, label='Lepton'),
    Patch(facecolor=CAT_COLORS['quark'], edgecolor=WHITE, label='Quark'),
    Patch(facecolor=CAT_COLORS['boson'], edgecolor=WHITE, label='Boson'),
    Patch(facecolor=CAT_COLORS['meson'], edgecolor=WHITE, label='Meson'),
    Patch(facecolor=CAT_COLORS['scale'], edgecolor=WHITE, label='Scale'),
]
ax.legend(handles=legend_elements, fontsize=10, loc='upper right')

plt.tight_layout()
save(fig, 'fig_energy_hierarchy.png')

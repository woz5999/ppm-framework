"""
fig_mass_spectrum.py — Mass spectrum predictions vs observed values

Plots the ratio E_predicted / m_observed for all particles in the PPM hierarchy,
colored by particle category.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, new_figure, save, GOLD, WHITE, VIOLET, CYAN, GRAY, CAT_COLORS

from ppm.hierarchy import k_from_energy_mev, energy_mev

# Particle data: (name, mass_mev, category)
particles_data = [
    ('electron', 0.511, 'lepton'),
    ('muon', 105.66, 'lepton'),
    ('tau', 1776.86, 'lepton'),
    ('pion', 139.57, 'meson'),
    ('kaon', 493.68, 'meson'),
    ('down', 4.67, 'quark'),
    ('up', 2.16, 'quark'),
    ('strange', 93.2, 'quark'),
    ('charm', 1275, 'quark'),
    ('bottom', 4180, 'quark'),
    ('top', 173210, 'quark'),
    ('W boson', 80385, 'boson'),
    ('Z boson', 91188, 'boson'),
    ('Higgs', 125100, 'boson'),
]

# Compute ratios and categories
names = []
ratios = []
colors = []

for name, mass_mev, cat in particles_data:
    # Find nearest k-level
    k = k_from_energy_mev(mass_mev)
    E_pred = energy_mev(k)
    ratio = E_pred / mass_mev

    names.append(name)
    ratios.append(ratio)
    colors.append(CAT_COLORS.get(cat, GRAY))

# Create figure
fig, ax = new_figure(width=12, height=7)

# Plot dots
x_pos = np.arange(len(names))
ax.scatter(x_pos, ratios, s=200, c=colors, edgecolor=WHITE, linewidth=2, zorder=5, alpha=0.85)

# Horizontal line at ratio = 1.0 (perfect agreement)
ax.axhline(1.0, color=WHITE, linestyle='-', linewidth=2, alpha=0.5, label='Perfect agreement')

# Add ratio labels
for i, (name, ratio) in enumerate(zip(names, ratios)):
    label = f'{ratio:.3f}'
    ax.text(i, ratio + 0.03, label, ha='center', va='bottom',
           fontsize=9, color=WHITE, fontweight='bold')

# Formatting
ax.set_xticks(x_pos)
ax.set_xticklabels(names, rotation=45, ha='right', fontsize=11)
ax.set_ylabel('E$_{\\mathrm{predicted}}$ / m$_{\\mathrm{observed}}$ (ratio)',
             fontsize=13, fontweight='bold')
ax.set_title('Mass spectrum: PPM predicted / observed ratio',
            fontsize=14, fontweight='bold', pad=15)
ax.set_ylim(0.8, 1.25)
ax.grid(True, alpha=0.3, linestyle=':', axis='y')

# Add legend for categories
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=CAT_COLORS['lepton'], edgecolor=WHITE, label='Lepton', linewidth=1.5),
    Patch(facecolor=CAT_COLORS['quark'], edgecolor=WHITE, label='Quark', linewidth=1.5),
    Patch(facecolor=CAT_COLORS['boson'], edgecolor=WHITE, label='Boson', linewidth=1.5),
    Patch(facecolor=CAT_COLORS['meson'], edgecolor=WHITE, label='Meson', linewidth=1.5),
]
ax.legend(handles=legend_elements, fontsize=11, loc='upper left', framealpha=0.95)

plt.tight_layout()
save(fig, 'fig_mass_spectrum.png')

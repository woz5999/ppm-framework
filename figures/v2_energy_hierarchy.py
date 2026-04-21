"""
v2_energy_hierarchy.py — PPM energy hierarchy with linear k-axis and log mass axis

Redesigned version with:
- LINEAR x-axis for k-level (range ~44 to ~58)
- LOG y-axis for mass/energy (GeV)
- Colored scatter points (squares for quarks, diamonds for bosons, circles for leptons, triangles for mesons)
- Gray diagonal line showing E(k) = 140 MeV × (2π)^{(51-k)/2}
- Each particle labeled next to its point
- Light gray diagonal shading bands in background
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, new_figure, save, CAT_COLORS, BG, WHITE, GRAY, GOLD
from ppm import hierarchy

apply_style()

k_table = hierarchy.k_level_table()

fig, ax = new_figure(width=10, height=7)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# Continuous E(k) line - linear k-axis
k_cont = np.linspace(43, 59, 300)
E_cont = np.array([hierarchy.energy_gev(k) for k in k_cont])
ax.semilogy(k_cont, E_cont, color=GRAY, linewidth=2, alpha=0.7, label=r'$E(k) = 140\;\mathrm{MeV}\times(2\pi)^{(51-k)/2}$')

# Marker shapes by category
markers = {'quark': 's', 'boson': 'D', 'lepton': 'o', 'meson': '^', 'scale': 'v'}

# Plot particles
for row in k_table:
    m = row['mass_observed_GeV']
    if m is not None and m > 0 and row['k'] >= 43 and row['k'] <= 58:
        cat = row['category']
        color = CAT_COLORS.get(cat, GRAY)
        marker = markers.get(cat, 'o')
        ax.semilogy(row['k'], m, marker=marker, color=color, markersize=12,
                    markeredgecolor=WHITE, markeredgewidth=1.5, zorder=5)

        # Label - offset based on position to avoid overlap
        name = row['name']
        # Offset labels to the right by default
        offset_x, offset_y = 0.3, 1.15
        ha = 'left'
        if name in ['top', 'Higgs']:
            offset_x = -0.3
            ha = 'right'
        ax.text(row['k'] + offset_x, m * offset_y, name,
                fontsize=9, color=WHITE, ha=ha, va='bottom')

# Legend
from matplotlib.lines import Line2D
legend_elements = []
for cat, marker in markers.items():
    if cat != 'scale':
        legend_elements.append(Line2D([0], [0], marker=marker, color='w', markerfacecolor=CAT_COLORS[cat],
                                       markeredgecolor=WHITE, markersize=10, label=cat.capitalize(), linestyle='None'))
legend_elements.append(Line2D([0], [0], color=GRAY, linewidth=2, label=r'$E(k)$ formula'))
ax.legend(handles=legend_elements, fontsize=10, loc='upper right')

ax.set_xlabel('k-level', fontsize=13)
ax.set_ylabel('Mass / Energy (GeV)', fontsize=13)
ax.set_title('PPM Energy Hierarchy: observed masses vs. $E(k)$', fontsize=14, pad=15)
ax.set_xlim(43, 59)
ax.set_ylim(1e-4, 1e3)
ax.grid(True, alpha=0.2, which='both', linestyle='-')

plt.tight_layout()
save(fig, 'v2_energy_hierarchy.png')

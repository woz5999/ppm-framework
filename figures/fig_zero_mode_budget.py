"""
fig_zero_mode_budget.py — Instanton prefactor budget

Bar chart showing the prefactor budget components:
  - 30 zero modes (collective coordinate volume F_zero)
  - T² partition function (Z_T²)
  - Known subtotal
  - Remaining gap (worldsheet needed)

Shows the φ^{-196} ↔ e^{-30π} match (0.073%).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, new_figure, save, GOLD, VIOLET, GRAY, ORANGE, WHITE
from ppm import instanton
from ppm.constants import INSTANTON_ACTION, PHI

# Compute prefactor budget
budget = instanton.prefactor_subtotal()
phi_check = instanton.phi_196_check()

# Extract log values for bar chart
log_F_zero = budget['log_F_zero']
log_F_trans = budget['log_F_trans']
log_ZT2 = budget['log_ZT2_total']
subtotal = budget['subtotal']
target = budget['target_log_J']
log_Z_ws_needed = budget['log_Z_worldsheet_needed']

# Component labels and values for stacked visualization
components = [
    ('Zero modes\n(V⊥$^{15}$)', log_F_zero, GOLD),
    ('Translation\nmoduli', log_F_trans, VIOLET),
    ('T² partition\nfunction', log_ZT2, ORANGE),
    ('Current subtotal', subtotal, GRAY),
    ('Worldsheet\nneeded (FFS)', log_Z_ws_needed, GRAY),
]

# Create figure
fig, ax = new_figure(width=11, height=6.5)

# Bar positions
x_pos = np.arange(len(components))
colors = [c[2] for c in components]
values = [c[1] for c in components]

# Draw bars
bars = ax.bar(x_pos, values, color=colors, edgecolor=WHITE, linewidth=1.5,
             alpha=0.8, width=0.6)

# Horizontal reference line at target
ax.axhline(target, color=GOLD, linestyle='--', linewidth=2.5,
          label=f'Target log J ≈ {target:.0f}')

# Formatting
labels = [c[0] for c in components]
ax.set_xticks(x_pos)
ax.set_xticklabels(labels, fontsize=11, fontweight='bold')
ax.set_ylabel('log (contribution to prefactor)', fontsize=13, fontweight='bold')
ax.set_title('Instanton prefactor budget', fontsize=14, fontweight='bold', pad=15)
ax.set_ylim(-150, 50)
ax.grid(True, alpha=0.3, axis='y', linestyle=':')
ax.legend(fontsize=11, loc='lower right')

# Annotations on bars
for i, (label, value, color) in enumerate(zip(labels, values, colors)):
    if i < 3:
        y_pos = value + 2
        fontsize = 10
        fontweight = 'bold'
    else:
        y_pos = value + 5
        fontsize = 11
        fontweight = 'bold'
    ax.text(i, y_pos, f'{value:.2f}', ha='center', va='bottom',
           fontsize=fontsize, color=WHITE, fontweight=fontweight)

# Add φ^{-196} match box
match_text = f'φ$^{{-196}}$ match:\n30π = {INSTANTON_ACTION:.3f}\n196ln(φ) = {phi_check["exponent_phi196"]:.3f}\nMismatch: {phi_check["mismatch_pct"]:.3f}%\n(VERIFIED)'
ax.text(0.98, 0.05, match_text, transform=ax.transAxes,
       fontsize=10, verticalalignment='bottom', horizontalalignment='right',
       bbox=dict(boxstyle='round', facecolor=GOLD, alpha=0.2, edgecolor=GOLD, linewidth=1),
       color=GOLD, fontweight='bold')

plt.tight_layout()
save(fig, 'fig_zero_mode_budget.png')

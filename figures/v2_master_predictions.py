"""
v2_master_predictions.py — PPM Master Predictions Horizontal Bar Chart

Redesigned from dense 37-row table to readable horizontal bar chart.
Shows error % for each prediction, grouped and colored by tier.
Only displays predictions with actual error values (skip conceptual/None).

Run: python v2_master_predictions.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, save, BG, WHITE, GRAY, GOLD, CYAN, GREEN, RED, VIOLET, ORANGE
from ppm.predictions import build_table

apply_style()

rows = build_table()

# Filter to rows with actual error values and sort
plot_rows = [r for r in rows if r['error_pct'] is not None]
plot_rows.sort(key=lambda r: (r['tier'], abs(r['error_pct'])))

# Distinct tier colors (improved from original)
tier_colors = {1: GREEN, 2: CYAN, 3: ORANGE, 4: RED}

fig, ax = plt.subplots(figsize=(12, max(8, len(plot_rows) * 0.35 + 2)))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

y_positions = range(len(plot_rows))
errors = [r['error_pct'] for r in plot_rows]
colors = [tier_colors.get(r['tier'], GRAY) for r in plot_rows]
labels = [f"{r['id']}: {r['quantity'][:35]}" for r in plot_rows]

bars = ax.barh(y_positions, errors, color=colors, edgecolor='none', height=0.7, alpha=0.85)

ax.axvline(0, color=WHITE, linewidth=1, alpha=0.5)

# Add value labels on bars
for i, (err, row) in enumerate(zip(errors, plot_rows)):
    x_pos = err + (0.3 if err >= 0 else -0.3)
    ha = 'left' if err >= 0 else 'right'
    ax.text(x_pos, i, f'{err:+.1f}%', fontsize=9, color=WHITE, va='center', ha=ha)

ax.set_yticks(y_positions)
ax.set_yticklabels(labels, fontsize=9, color=WHITE)
ax.set_xlabel('Error: (Predicted/Observed − 1) × 100%', fontsize=12, color=WHITE)
ax.set_title('PPM Master Prediction Table: All Derived Quantities vs Observation',
             fontsize=14, color=WHITE, pad=15)
ax.grid(True, alpha=0.2, linestyle=':', axis='x')

# Legend with clear tier definitions
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=GREEN, label='Tier 1: <2%'),
    Patch(facecolor=CYAN, label='Tier 2: 2-10%'),
    Patch(facecolor=ORANGE, label='Tier 3: 10-25%'),
    Patch(facecolor=RED, label='Tier 4: Cosmological'),
]
ax.legend(handles=legend_elements, fontsize=10, loc='lower right')

ax.invert_yaxis()
plt.tight_layout()
save(fig, 'v2_master_predictions.png')

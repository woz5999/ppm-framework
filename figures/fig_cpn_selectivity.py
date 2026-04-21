"""
fig_cpn_selectivity.py — CP^n selectivity of the fine-structure constant

Plots 1/α predictions across the CP^n family (n=1..7), showing that only CP³
yields the observed value. Uses the half-variance condition at t* = 1/(2(n+1)²).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib.pyplot as plt
from _style import apply_style, new_figure, save, GOLD, GRAY, WHITE
from ppm import alpha

# Compute 1/α for CP^n family
family = alpha.alpha_cpn_family(n_range=range(1, 8), nmax=300)

# Extract data
n_values = sorted(family.keys())
alpha_inv_values = [family[n]['alpha_inv'] for n in n_values]
alpha_obs_inv = 137.036

# Create figure
fig, ax = new_figure(width=9, height=5.5)

# Bar chart
x_pos = range(len(n_values))
colors = [GOLD if n == 3 else GRAY for n in n_values]
bars = ax.bar(x_pos, alpha_inv_values, color=colors, edgecolor=WHITE, linewidth=1.5, alpha=0.8)

# Horizontal line at observed value
ax.axhline(y=alpha_obs_inv, color=GOLD, linestyle='--', linewidth=2.5, label=f'Observed: 1/α = {alpha_obs_inv:.3f}')

# Formatting
ax.set_xlabel('CP$^n$ dimension', fontsize=13, fontweight='bold')
ax.set_ylabel('1/α prediction', fontsize=13, fontweight='bold')
ax.set_title('Only CP³ yields the observed fine-structure constant', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x_pos)
ax.set_xticklabels([f'CP$^{n}$' for n in n_values], fontsize=12)
ax.set_ylim(0, max(alpha_inv_values) * 1.15)
ax.grid(True, alpha=0.3, linestyle=':', axis='y')
ax.legend(fontsize=11, loc='upper left')

# Annotate CP^3
for i, n in enumerate(n_values):
    if n == 3:
        ax.text(i, alpha_inv_values[i] + 30, f'{alpha_inv_values[i]:.1f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold', color=GOLD)

plt.tight_layout()
save(fig, 'fig_cpn_selectivity.png')

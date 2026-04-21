"""
v2_cpn_selectivity.py — CP^n family selectivity for α

Shows the RATIO of predicted/observed for each CP^n.
CP³ ratio ≈ 1, others diverge wildly. Uses log scale y-axis.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, save, GOLD, GRAY, WHITE, VIOLET, BG
from ppm import alpha

apply_style()

family = alpha.alpha_cpn_family(n_range=range(1, 8), nmax=300)
n_values = sorted(family.keys())
alpha_obs_inv = 137.036

fig, ax = plt.subplots(figsize=(9, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ratios = [family[n]['alpha_inv'] / alpha_obs_inv for n in n_values]
colors = [GOLD if n == 3 else VIOLET for n in n_values]

bars = ax.bar(range(len(n_values)), ratios, color=colors, edgecolor=WHITE, linewidth=1.5, alpha=0.85)

# Reference line at ratio = 1
ax.axhline(y=1.0, color=GOLD, linestyle='--', linewidth=2.5, alpha=0.8, label='Observed (ratio = 1)')

# Annotate each bar with its 1/α value
for i, (n, r) in enumerate(zip(n_values, ratios)):
    label = f'{family[n]["alpha_inv"]:.1f}'
    y_pos = r + 0.02 if r < 5 else r * 1.05
    ax.text(i, y_pos, label, ha='center', va='bottom', fontsize=9, color=WHITE, fontweight='bold')

ax.set_yscale('log')
ax.set_xlabel(r'$\mathbb{CP}^n$ dimension $n$', fontsize=13)
ax.set_ylabel(r'Predicted $1/\alpha$ / Observed $1/\alpha$', fontsize=13)
ax.set_title(r'$\mathbb{CP}^n$ Selectivity: Only $n=3$ gives $1/\alpha \approx 137$', fontsize=14, pad=15)
ax.set_xticks(range(len(n_values)))
ax.set_xticklabels([f'$\\mathbb{{CP}}^{n}$' for n in n_values], fontsize=12)
ax.set_ylim(0.005, 200)
ax.grid(True, alpha=0.3, linestyle=':', axis='y', which='both')
ax.legend(fontsize=11, loc='upper left')

plt.tight_layout()
save(fig, 'v2_cpn_selectivity.png')

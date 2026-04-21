"""
fig_duality_coverage.py — Cross-doublet coverage matrix

Strategic positioning figure showing which fundamental quantities
different unification programs address.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, new_figure, save, GOLD, WHITE, VIOLET, CYAN, GRAY

# Programs and quantities
programs = [
    'PPM',
    'String/M-theory',
    'Loop QG',
    'Asymptotic Safety',
    'Causal Sets',
    'E₈×E₈',
    'Twistor',
    'SO(10) GUT',
    'Kaluza-Klein',
    'Non-commutative',
    'Emergent Gravity',
]

quantities = [
    'α',
    'θ_W',
    'G',
    'Λ',
    'N_gen',
    'm_H',
    'δ_CP',
    'Consciousness'
]

# Coverage matrix: 1=full (GOLD), 0.5=partial (VIOLET), 0=none (GRAY)
coverage = np.array([
    [1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0],      # PPM
    [0.5,  0.5,  1.0,  1.0,  0.0,  0.5,  0.0,  0.0],      # String
    [0.5,  0.0,  1.0,  0.0,  0.0,  0.0,  0.0,  0.0],      # Loop QG
    [1.0,  0.5,  1.0,  0.5,  0.0,  0.0,  0.0,  0.0],      # Asymptotic Safety
    [0.0,  0.0,  1.0,  0.0,  0.0,  0.0,  0.0,  0.0],      # Causal Sets
    [0.5,  0.5,  0.0,  0.0,  1.0,  0.0,  0.0,  0.0],      # E8
    [0.5,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.0],      # Twistor
    [1.0,  1.0,  0.0,  0.0,  1.0,  0.5,  0.0,  0.0],      # SO(10)
    [0.5,  0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],      # Kaluza-Klein
    [0.5,  0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],      # Non-comm
    [0.0,  0.0,  1.0,  0.5,  0.0,  0.0,  0.0,  0.0],      # Emergent gravity
])

# Create figure with larger size for readability
fig, ax = new_figure(width=13, height=10)

# Color map: 1.0=GOLD, 0.5=VIOLET, 0.0=GRAY
im = ax.imshow(coverage, cmap=None, aspect='auto', vmin=0, vmax=1)

# Set ticks and labels
ax.set_xticks(np.arange(len(quantities)))
ax.set_yticks(np.arange(len(programs)))
ax.set_xticklabels(quantities, fontsize=12, fontweight='bold')
ax.set_yticklabels(programs, fontsize=11)

# Rotate x labels
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

# Add cell colors and text
for i in range(len(programs)):
    for j in range(len(quantities)):
        val = coverage[i, j]
        if val == 1.0:
            color = GOLD
            symbol = '●'  # Full circle
        elif val == 0.5:
            color = VIOLET
            symbol = '◐'  # Half circle
        else:
            color = GRAY
            symbol = '○'  # Empty circle

        # Cell background
        rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=True,
                            facecolor=color if val > 0 else '#0a0a1a',
                            edgecolor=WHITE, linewidth=1.5, alpha=0.3)
        ax.add_patch(rect)

        # Symbol
        ax.text(j, i, symbol, ha='center', va='center', fontsize=16,
               color=WHITE if val > 0 else GRAY, fontweight='bold')

# Formatting
ax.set_xlabel('Fundamental Quantity', fontsize=13, fontweight='bold', labelpad=10)
ax.set_ylabel('Unification Program', fontsize=13, fontweight='bold', labelpad=10)
ax.set_title('Cross-doublet coverage: PPM vs other programs',
            fontsize=14, fontweight='bold', pad=20)

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=GOLD, edgecolor=WHITE, label='Full coverage (●)', linewidth=1.5),
    Patch(facecolor=VIOLET, edgecolor=WHITE, label='Partial coverage (◐)', linewidth=1.5),
    Patch(facecolor=GRAY, edgecolor=WHITE, label='Not addressed (○)', linewidth=1.5),
]
ax.legend(handles=legend_elements, fontsize=11, loc='upper right', framealpha=0.95, bbox_to_anchor=(1.15, 1))

# Remove axis spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.tight_layout()
save(fig, 'fig_duality_coverage.png')

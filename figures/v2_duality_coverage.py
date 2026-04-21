"""
v2_duality_coverage.py — Cross-doublet coverage matrix (improved)

Cleaner visualization using matplotlib table with:
  - Colored cells for coverage levels
  - Filled circles (●) for full, half-filled (◐) for partial, empty (○) for none
  - PPM row highlighted with gold background
  - Larger, more readable fonts (11-12pt)
  - Wide layout to prevent column compression

Run: python v2_duality_coverage.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from _style import apply_style, save, GOLD, WHITE, VIOLET, CYAN, GRAY, GREEN, RED, ORANGE, BG

apply_style()

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

# Create figure with wider dimensions to avoid compression
fig, ax = plt.subplots(figsize=(14, 10))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# Build table data with symbols
cell_text = []
cell_colors = []
cell_edgecolors = []

for i in range(len(programs)):
    row_text = []
    row_colors = []
    row_edges = []

    # Program name column
    row_text.append(programs[i])
    if i == 0:
        row_colors.append(GOLD)  # PPM row background
        row_edges.append(GOLD)
    else:
        row_colors.append('none')
        row_edges.append(GRAY)

    # Coverage columns
    for j in range(len(quantities)):
        val = coverage[i, j]
        if val == 1.0:
            symbol = '●'  # Full circle
            color = GREEN
        elif val == 0.5:
            symbol = '◐'  # Half circle
            color = VIOLET
        else:
            symbol = '○'  # Empty circle
            color = GRAY

        row_text.append(symbol)
        row_colors.append(color)
        row_edges.append(GRAY)

    cell_text.append(row_text)
    cell_colors.append(row_colors)
    cell_edgecolors.append(row_edges)

# Create table
col_labels = ['Program'] + quantities
table = ax.table(cellText=cell_text, colLabels=col_labels,
                 cellLoc='center', loc='center',
                 bbox=[0, 0, 1, 1])

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.2)

# Style header
for i in range(len(col_labels)):
    cell = table[(0, i)]
    cell.set_facecolor(GOLD)
    cell.set_text_props(weight='bold', color=BG, size=12)
    cell.set_edgecolor(WHITE)
    cell.set_linewidth(2)

# Style data cells
for i in range(len(programs)):
    for j in range(len(col_labels)):
        cell = table[(i + 1, j)]

        # PPM row special treatment
        if i == 0:
            cell.set_facecolor(GOLD)
            cell.set_alpha(0.15)
        else:
            if j == 0:
                cell.set_facecolor('none')
            else:
                color = cell_colors[i][j]
                cell.set_facecolor(color)
                cell.set_alpha(0.2)

        cell.set_text_props(color=WHITE, size=11, weight='bold')
        cell.set_edgecolor(GRAY)
        cell.set_linewidth(1.5)

# Legend
legend_elements = [
    Patch(facecolor=GREEN, alpha=0.2, edgecolor=GRAY, label='Full coverage (●)'),
    Patch(facecolor=VIOLET, alpha=0.2, edgecolor=GRAY, label='Partial coverage (◐)'),
    Patch(facecolor=GRAY, alpha=0.2, edgecolor=GRAY, label='Not addressed (○)'),
]
ax.legend(handles=legend_elements, fontsize=11, loc='upper right',
         framealpha=0.95, bbox_to_anchor=(1.0, 1.0))

ax.set_title('Cross-doublet coverage: PPM vs other unification programs',
            fontsize=14, color=WHITE, weight='bold', pad=20)

ax.axis('off')

plt.tight_layout()
save(fig, 'v2_duality_coverage.png')

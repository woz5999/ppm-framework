"""
v2_experimental_roadmap.py — Testable predictions on experimental timeline

Gantt-style chart showing PPM predictions and the planned experimental timeline
for testing them.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, new_figure, save, GOLD, WHITE, VIOLET, CYAN, GRAY, GREEN

# Hardcoded experimental roadmap data
roadmap = [
    {'name': 'δ$_{\\mathrm{CP}}$ = 68.8°', 'experiment': 'DUNE', 'start': 2025, 'end': 2035, 'status': 'Running'},
    {'name': 'GW dispersion', 'experiment': 'LIGO/LISA', 'start': 2025, 'end': 2040, 'status': 'Planned'},
    {'name': 'G$_{\\mathrm{eff}}$(z) galaxies', 'experiment': 'JWST/Roman', 'start': 2024, 'end': 2032, 'status': 'Active'},
    {'name': 'w$_0$, w$_a$ constraints', 'experiment': 'DESI/Euclid', 'start': 2024, 'end': 2030, 'status': 'Active'},
    {'name': 'τ$_{\\mathrm{proton}}$ > 10$^{40}$ yr', 'experiment': 'Hyper-K', 'start': 2027, 'end': 2040, 'status': 'Planned'},
    {'name': 'Sterile ν (5–14 keV)', 'experiment': 'X-ray surveys', 'start': 2025, 'end': 2035, 'status': 'Planned'},
    {'name': 'Decoherence rate', 'experiment': 'Optomech.', 'start': 2025, 'end': 2035, 'status': 'Proposed'},
    {'name': 'sin$^2$θ$_{23}$ precision', 'experiment': 'DUNE/HK', 'start': 2027, 'end': 2038, 'status': 'Planned'},
]

# Status color map
status_colors = {
    'Active': GREEN,
    'Running': GOLD,
    'Planned': VIOLET,
    'Proposed': CYAN,
}

# Create figure with more vertical space
fig, ax = new_figure(width=12, height=8)

# Reverse order for top-to-bottom reading
roadmap = roadmap[::-1]

# Draw bars
y_pos = np.arange(len(roadmap))
for i, item in enumerate(roadmap):
    color = status_colors.get(item['status'], GRAY)
    duration = item['end'] - item['start']
    ax.barh(i, duration, left=item['start'], height=0.6, color=color, alpha=0.85,
           edgecolor=WHITE, linewidth=1.5)

    # Add label with experiment name
    label_text = f"{item['name']} ({item['experiment']})"
    ax.text(item['start'] - 0.5, i, label_text, ha='right', va='center',
           fontsize=10, fontweight='bold', color=WHITE)

# Formatting
ax.set_yticks([])
ax.set_xlabel('Year', fontsize=13, fontweight='bold')
ax.set_title('Experimental roadmap for PPM predictions',
            fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(2023, 2041)
ax.set_ylim(-1, len(roadmap))
ax.grid(True, alpha=0.3, linestyle=':', axis='x')

# Add vertical line for "now"
ax.axvline(2026, color=WHITE, linestyle=':', linewidth=2, alpha=0.5, label='2026 (now)')

# Create legend from status colors
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=GREEN, edgecolor=WHITE, label='Active', linewidth=1.5),
    Patch(facecolor=GOLD, edgecolor=WHITE, label='Running', linewidth=1.5),
    Patch(facecolor=VIOLET, edgecolor=WHITE, label='Planned', linewidth=1.5),
    Patch(facecolor=CYAN, edgecolor=WHITE, label='Proposed', linewidth=1.5),
]
ax.legend(handles=legend_elements, fontsize=11, loc='lower right', framealpha=0.95)

plt.tight_layout()
save(fig, 'v2_experimental_roadmap.png')

"""
v2_mixing_predictions.py — Mixing angles and CP phase predictions (FIXED)

Grouped bar chart comparing PPM predictions with observed values.
FIXED: EXCLUDED label moved above the bars, not overlapping them.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, save, GOLD, WHITE, VIOLET, CYAN, GRAY, RED, ORANGE

from ppm.neutrino import pmns_tribimaximal
from ppm.mixing import ckm_berry, strong_cp

apply_style()

# Gather all mixing data
pmns = pmns_tribimaximal()
ckm = ckm_berry()
theta_strong = strong_cp()

# Data structure: (parameter_name, ppm_value, obs_value, obs_error, flagged)
mixing_data = [
    ('sin²θ$_{12}$', pmns['sin2_theta12_ppm'], pmns['sin2_theta12_obs'][0], pmns['sin2_theta12_obs'][1], False),
    ('sin²θ$_{23}$', pmns['sin2_theta23_ppm'], pmns['sin2_theta23_obs'][0], pmns['sin2_theta23_obs'][1], False),
    ('sin²θ$_{13}$', pmns['sin2_theta13_ppm'], pmns['sin2_theta13_obs'][0], pmns['sin2_theta13_obs'][1], True),  # Flagged
    ('δ$_{\\mathrm{CP}}$ (rad)', ckm['delta_cp_rad'] / np.pi, (ckm['observed_rad'] / np.pi if ckm['observed_rad'] else 1.2), 0.3, False),
    ('θ$_{\\mathrm{strong}}$ (rad)', theta_strong['theta_strong'], 1e-10, 1e-10, False),
]

# Create figure
fig, ax = plt.subplots(figsize=(12, 7))

# Bar positions and widths
n_params = len(mixing_data)
x = np.arange(n_params)
width = 0.35

ppm_vals = []
obs_vals = []
obs_errs = []
colors_ppm = []
colors_obs = []
param_names = []

for name, ppm, obs, err, flagged in mixing_data:
    ppm_vals.append(ppm)
    obs_vals.append(obs)
    obs_errs.append(err)
    param_names.append(name)

    if flagged:
        colors_ppm.append(RED)
        colors_obs.append(RED)
    else:
        colors_ppm.append(GOLD)
        colors_obs.append(CYAN)

# Draw bars
bars1 = ax.bar(x - width/2, ppm_vals, width, label='PPM prediction',
              color=colors_ppm, edgecolor=WHITE, linewidth=1.5, alpha=0.85)
bars2 = ax.bar(x + width/2, obs_vals, width, label='Observed',
              color=colors_obs, edgecolor=WHITE, linewidth=1.5, alpha=0.85,
              yerr=obs_errs, capsize=5, error_kw={'elinewidth': 2, 'capthick': 2})

# Add error percentage labels
for i, (ppm, obs, err) in enumerate(zip(ppm_vals, obs_vals, obs_errs)):
    if obs > 0:
        err_pct = abs((ppm - obs) / obs) * 100
        label = f'{err_pct:.1f}%'
        y_pos = max(ppm, obs) * 1.15
        color = RED if i == 2 else WHITE
        ax.text(i, y_pos, label, ha='center', va='bottom',
               fontsize=10, color=color, fontweight='bold')

# Special flagging for θ₁₃ — moved ABOVE the bars
# Place the annotation well above the bars at index 2
y_annotation = max(ppm_vals[2], obs_vals[2]) * 1.35
ax.annotate('EXCLUDED\n(>5σ)', xy=(2, obs_vals[2]), xytext=(2, y_annotation),
           fontsize=11, color=WHITE, fontweight='bold', ha='center',
           bbox=dict(boxstyle='round,pad=0.6', facecolor=RED, edgecolor=WHITE, linewidth=2, alpha=0.9),
           arrowprops=dict(arrowstyle='->', color=RED, lw=2))

# Formatting
ax.set_ylabel('Value', fontsize=13, fontweight='bold')
ax.set_title('Mixing angle and CP phase predictions',
            fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(param_names, fontsize=12, fontweight='bold')
ax.legend(fontsize=12, loc='upper left', framealpha=0.95)
ax.grid(True, alpha=0.3, linestyle=':', axis='y')

# Adjusted y-limits to accommodate the annotation
ax.set_ylim(-0.05, 1.7)

plt.tight_layout()
save(fig, 'v2_mixing_predictions.png')

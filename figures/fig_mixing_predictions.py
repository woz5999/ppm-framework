"""
fig_mixing_predictions.py — Mixing angles and CP phase predictions

Grouped bar chart comparing PPM predictions (sin²θ_ij, δ_CP, θ_strong)
with observed values.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, new_figure, save, GOLD, WHITE, VIOLET, CYAN, GRAY, RED, ORANGE

from ppm.neutrino import pmns_tribimaximal
from ppm.mixing import ckm_berry, strong_cp

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
fig, ax = new_figure(width=12, height=7)

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

# Special flagging for θ₁₃
ax.text(2, ppm_vals[2] * 0.5, 'EXCLUDED\n(>5σ)', ha='center', va='center',
       fontsize=11, color=WHITE, fontweight='bold',
       bbox=dict(boxstyle='round,pad=0.6', facecolor=RED, edgecolor=WHITE, linewidth=2, alpha=0.9))

# Formatting
ax.set_ylabel('Value', fontsize=13, fontweight='bold')
ax.set_title('Mixing angle and CP phase predictions',
            fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(param_names, fontsize=12, fontweight='bold')
ax.legend(fontsize=12, loc='upper left', framealpha=0.95)
ax.grid(True, alpha=0.3, linestyle=':', axis='y')

# Set appropriate y-limits depending on parameter
ax.set_ylim(-0.05, 1.5)

plt.tight_layout()
save(fig, 'fig_mixing_predictions.png')

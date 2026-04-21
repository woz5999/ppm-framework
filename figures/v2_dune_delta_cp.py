"""
v2_dune_delta_cp.py — DUNE δ_CP Measurement vs PPM Prediction

Redesigned to remove obscuring text boxes. Cleaner layout with:
  - Current NOvA+T2K sensitivity curve
  - DUNE projected sensitivity
  - PPM prediction and current best fit lines only
  - Minimal annotation positioned away from curves

Run: python v2_dune_delta_cp.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from _style import apply_style, save, GOLD, CYAN, WHITE, GRAY, RED, BG
from ppm.berry_phase import delta_cp

apply_style()

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

dcp_result = delta_cp()
delta_cp_ppm_deg = dcp_result['delta_cp_deg']

x = np.linspace(0, 360, 1000)

# Current NOvA+T2K sensitivity
exp_center_deg = 68.0
exp_sigma_deg = 15.0
current_prob = norm.pdf(x, exp_center_deg, exp_sigma_deg)
current_prob /= current_prob.max()  # normalize to 1

# DUNE projected
dune_sigma_deg = 4.5
dune_prob = norm.pdf(x, exp_center_deg, dune_sigma_deg)
dune_prob /= dune_prob.max()

# Plot filled areas
ax.fill_between(x, 0, current_prob, alpha=0.2, color=GRAY, zorder=1)
ax.plot(x, current_prob, color=GRAY, linewidth=2, alpha=0.7, label='Current (NOvA+T2K)')

ax.fill_between(x, 0, dune_prob, alpha=0.25, color=CYAN, zorder=1)
ax.plot(x, dune_prob, color=CYAN, linewidth=2.5, label='DUNE projected')

# PPM prediction
ax.axvline(x=delta_cp_ppm_deg, color=GOLD, linewidth=3, linestyle='-',
           label=f'PPM: δ_CP = {delta_cp_ppm_deg:.1f}°', zorder=3)

# Current best fit
ax.axvline(x=exp_center_deg, color=RED, linewidth=2, linestyle='--', alpha=0.7,
           label=f'Current best: {exp_center_deg}°', zorder=2)

ax.set_xlabel(r'CP-Violating Phase $\delta_{\rm CP}$ [degrees]', fontsize=12, color=WHITE)
ax.set_ylabel('Relative Sensitivity (normalized)', fontsize=12, color=WHITE)
ax.set_title(r'DUNE $\delta_{\rm CP}$ Measurement vs PPM Prediction',
             fontsize=14, color=WHITE, pad=15)
ax.set_xlim(0, 360)
ax.set_ylim(0, 1.15)
ax.legend(fontsize=11, loc='upper right')
ax.grid(True, alpha=0.2, linestyle=':', axis='x')

plt.tight_layout()
save(fig, 'v2_dune_delta_cp.png')

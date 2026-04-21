"""
v2_sin2_theta_w.py — Weinberg angle running and Pati-Salam matching

Plots sin²θ_W running from M_Z up to Pati-Salam scale using SM one-loop RGE.
Shows the match with PPM prediction sin²θ_W = 3/8 at k_break.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, new_figure, save, GOLD, WHITE, VIOLET
from ppm import gauge, hierarchy
from ppm.constants import M_Z_GEV, K_BREAK, K_EWSB

# Compute sin²θ_W running from M_Z to Pati-Salam
E_break = hierarchy.energy_gev(K_BREAK)
E_z = M_Z_GEV

# Generate energy scale range
E_scales = np.logspace(np.log10(E_z), np.log10(E_break * 2), 150)

sin2_tw_values = []
for E in E_scales:
    result = gauge.sin2_theta_W_sm_running(E_break_GeV=E)
    sin2_tw_values.append(result['sin2_tW_sm'])

sin2_tw_ppm = gauge.sin2_theta_W_pati_salam()

# Create figure
fig, ax = new_figure(width=10, height=6)

# Plot running
ax.semilogx(E_scales, sin2_tw_values, color=VIOLET, linewidth=2.5,
           label='SM one-loop running')

# PPM prediction line
ax.axhline(sin2_tw_ppm, color=GOLD, linestyle='--', linewidth=2.5,
          label=f'PPM: sin²θ$_W$ = 3/8 = {sin2_tw_ppm:.4f}')

# Mark the Pati-Salam scale
ax.axvline(E_break, color=VIOLET, linestyle=':', linewidth=2,
          alpha=0.6, label=f'E$_break$ = {E_break:.2e} GeV')

# Mark M_Z
ax.axvline(M_Z_GEV, color=WHITE, linestyle=':', linewidth=1.5, alpha=0.4)
ax.text(M_Z_GEV * 0.7, 0.225, 'M$_Z$', fontsize=10, color=WHITE, rotation=90, va='center')

# Highlight intersection
sin2_at_break = gauge.sin2_theta_W_sm_running(E_break)
ax.scatter([E_break], [sin2_at_break['sin2_tW_sm']], s=200, color=GOLD,
          edgecolor=WHITE, linewidth=2.5, zorder=5, marker='*')

agreement = sin2_at_break['agreement_pct']
ax.text(E_break * 1.5, sin2_at_break['sin2_tW_sm'] + 0.002,
       f'Match: {agreement:.2f}%',
       fontsize=11, color=GOLD, fontweight='bold')

# Formatting
ax.set_xlabel('Energy scale E (GeV)', fontsize=13, fontweight='bold')
ax.set_ylabel('sin²θ$_W$', fontsize=13, fontweight='bold')
ax.set_title('Weinberg angle running matches PPM at Pati-Salam', fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(E_z, E_break * 2)
ax.set_ylim(0.215, 0.385)
ax.grid(True, alpha=0.3, linestyle=':')
ax.legend(fontsize=11, loc='upper left')

plt.tight_layout()
save(fig, 'v2_sin2_theta_w.png')

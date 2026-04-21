"""
fig_alpha_s_twoloop.py — Two-loop α_s running to confinement

Plots α_s(μ) from M_Z down to ~200 MeV using two-loop RGE with flavor thresholds.
Shows confinement onset where α_s → 1 (~800 MeV). Includes threshold crossings.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, new_figure, save, WHITE, ORANGE, CYAN, RED
from ppm import stability
from ppm.constants import M_Z_GEV, ALPHA3_MZ

# Define quark mass thresholds
M_TOP_GEV = 172.7
M_BOTTOM_GEV = 4.18
M_CHARM_GEV = 1.27

# Run α_s in segments with flavor threshold changes
# Segment 1: M_Z down to m_b (n_f = 5)
mus_5f, alphas_5f = stability.run_alpha_s_twoloop(M_Z_GEV, M_BOTTOM_GEV, ALPHA3_MZ, n_f=5, n_steps=100000)

# Segment 2: m_b to m_c (n_f = 4) - need to adjust starting value
alpha_at_mb = alphas_5f[-1]
mus_4f, alphas_4f = stability.run_alpha_s_twoloop(M_BOTTOM_GEV, M_CHARM_GEV, alpha_at_mb, n_f=4, n_steps=100000)

# Segment 3: m_c down to ~200 MeV (n_f = 3)
alpha_at_mc = alphas_4f[-1]
mus_3f, alphas_3f = stability.run_alpha_s_twoloop(M_CHARM_GEV, 0.2, alpha_at_mc, n_f=3, n_steps=150000)

# Combine all segments
mus_all = np.concatenate([mus_5f, mus_4f[1:], mus_3f[1:]])
alphas_all = np.concatenate([alphas_5f, alphas_4f[1:], alphas_3f[1:]])

# Find confinement scale (where α_s ≈ 1)
conf_idx = np.argmin(np.abs(np.array(alphas_all) - 1.0))
mu_confinement = mus_all[conf_idx]

# Create figure
fig, ax = new_figure(width=10, height=6.5)

# Main running curve
ax.semilogx(mus_all, alphas_all, color=ORANGE, linewidth=2.8, label='Two-loop α$_s$ running')

# Confinement line
ax.axhline(1.0, color=RED, linestyle='--', linewidth=2.5, alpha=0.8,
          label='Confinement (α$_s$ = 1)')

# Threshold crossings
ax.axvline(M_TOP_GEV, color=CYAN, linestyle=':', linewidth=1.5, alpha=0.5)
ax.text(M_TOP_GEV * 0.85, 0.135, 'm$_t$', fontsize=9, color=CYAN, rotation=90, va='center')

ax.axvline(M_BOTTOM_GEV, color=CYAN, linestyle=':', linewidth=1.5, alpha=0.5)
ax.text(M_BOTTOM_GEV * 0.85, 0.135, 'm$_b$', fontsize=9, color=CYAN, rotation=90, va='center')

ax.axvline(M_CHARM_GEV, color=CYAN, linestyle=':', linewidth=1.5, alpha=0.5)
ax.text(M_CHARM_GEV * 0.85, 0.135, 'm$_c$', fontsize=9, color=CYAN, rotation=90, va='center')

# Mark confinement scale
ax.scatter([mu_confinement], [1.0], s=200, color=RED, edgecolor=WHITE,
          linewidth=2, zorder=5, marker='*')
ax.text(mu_confinement * 1.3, 1.02, f'μ$_{{conf}}$ ≈ {mu_confinement:.0f} MeV',
       fontsize=10, color=RED, fontweight='bold')

# Mark M_Z
ax.scatter([M_Z_GEV], [ALPHA3_MZ], s=150, color=WHITE, edgecolor=ORANGE,
          linewidth=2, zorder=5, marker='o')
ax.text(M_Z_GEV * 1.3, ALPHA3_MZ + 0.005, f'M$_Z$: α$_s$ = {ALPHA3_MZ:.4f}',
       fontsize=10, color=WHITE, fontweight='bold')

# Flavor regions (n_f)
ax.text(10, 0.25, 'n$_f$ = 5', fontsize=11, color=WHITE, fontweight='bold', alpha=0.6)
ax.text(3, 0.27, 'n$_f$ = 4', fontsize=11, color=WHITE, fontweight='bold', alpha=0.6)
ax.text(0.5, 0.30, 'n$_f$ = 3', fontsize=11, color=WHITE, fontweight='bold', alpha=0.6)

# Formatting
ax.set_xlabel('Energy scale μ (GeV)', fontsize=13, fontweight='bold')
ax.set_ylabel('α$_s$(μ)', fontsize=13, fontweight='bold')
ax.set_title('Two-loop α$_s$ running to confinement', fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(0.15, M_Z_GEV * 2)
ax.set_ylim(0.08, 0.35)
ax.grid(True, alpha=0.3, linestyle=':', which='both')
ax.legend(fontsize=11, loc='upper right')

plt.tight_layout()
save(fig, 'fig_alpha_s_twoloop.png')

"""
v2_alpha_s_twoloop.py — Two-loop α_s running to confinement

Shows α_s running from M_Z down to confinement with flavor thresholds.
Full running from M_Z to confinement with ylim extended to 1.15.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, save, WHITE, ORANGE, CYAN, RED, BG, GRAY
from ppm import stability
from ppm.constants import M_Z_GEV, ALPHA3_MZ

apply_style()

M_BOTTOM_GEV = 4.18
M_CHARM_GEV = 1.27

# Run α_s segments with flavor thresholds
mus_5f, alphas_5f = stability.run_alpha_s_twoloop(M_Z_GEV, M_BOTTOM_GEV, ALPHA3_MZ, n_f=5, n_steps=100000)
alpha_at_mb = alphas_5f[-1]
mus_4f, alphas_4f = stability.run_alpha_s_twoloop(M_BOTTOM_GEV, M_CHARM_GEV, alpha_at_mb, n_f=4, n_steps=100000)
alpha_at_mc = alphas_4f[-1]
mus_3f, alphas_3f = stability.run_alpha_s_twoloop(M_CHARM_GEV, 0.2, alpha_at_mc, n_f=3, n_steps=150000)

mus_all = np.concatenate([mus_5f, mus_4f[1:], mus_3f[1:]])
alphas_all = np.concatenate([alphas_5f, alphas_4f[1:], alphas_3f[1:]])

# Clip to reasonable range to avoid blowup
mask = np.array(alphas_all) < 1.5
mus_plot = np.array(mus_all)[mask]
alphas_plot = np.array(alphas_all)[mask]

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# Main running curve
ax.semilogx(mus_plot, alphas_plot, color=ORANGE, linewidth=2.8, label=r'Two-loop $\alpha_s$ running')

# Confinement line
ax.axhline(1.0, color=RED, linestyle='--', linewidth=2, alpha=0.7, label=r'Confinement ($\alpha_s = 1$)')

# Threshold crossings
for mu, label in [(M_BOTTOM_GEV, r'$m_b$'), (M_CHARM_GEV, r'$m_c$')]:
    ax.axvline(mu, color=CYAN, linestyle=':', linewidth=1.5, alpha=0.5)
    ax.text(mu * 1.1, 0.95, label, fontsize=10, color=CYAN, va='top')

# Flavor region labels
ax.text(30, 0.15, r'$n_f = 5$', fontsize=11, color=WHITE, alpha=0.5)
ax.text(2.0, 0.15, r'$n_f = 4$', fontsize=11, color=WHITE, alpha=0.5)
ax.text(0.4, 0.15, r'$n_f = 3$', fontsize=11, color=WHITE, alpha=0.5)

# Mark M_Z point
ax.scatter([M_Z_GEV], [ALPHA3_MZ], s=120, color=WHITE, edgecolor=ORANGE, linewidth=2, zorder=5)
ax.text(M_Z_GEV * 0.6, ALPHA3_MZ + 0.02, f'$M_Z$: $\\alpha_s$ = {ALPHA3_MZ:.4f}',
        fontsize=10, color=WHITE, ha='right')

# Find and mark confinement scale
conf_idx = np.argmin(np.abs(np.array(alphas_all) - 1.0))
mu_conf = mus_all[conf_idx]
ax.scatter([mu_conf], [1.0], s=150, color=RED, edgecolor=WHITE, linewidth=2, zorder=5, marker='*')
ax.text(mu_conf * 1.5, 1.03, f'$\\mu_{{conf}} \\approx$ {mu_conf*1000:.0f} MeV', fontsize=10, color=RED)

ax.set_xlabel('Energy scale μ (GeV)', fontsize=13)
ax.set_ylabel(r'$\alpha_s(\mu)$', fontsize=13)
ax.set_title(r'Two-loop $\alpha_s$ running to confinement', fontsize=14, pad=15)
ax.set_xlim(0.15, M_Z_GEV * 2)
ax.set_ylim(0.05, 1.15)
ax.grid(True, alpha=0.3, linestyle=':', which='both')
ax.legend(fontsize=11, loc='upper right')

plt.tight_layout()
save(fig, 'v2_alpha_s_twoloop.png')

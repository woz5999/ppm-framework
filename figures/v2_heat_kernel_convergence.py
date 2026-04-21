"""
v2_heat_kernel_convergence.py — Heat kernel convergence to α at t* = 1/32

Two subplots:
  Left: Twisted heat trace ratio Θ^τ/Θ_{CP³} vs t (log scale) showing convergence at t*=1/32
  Right: Convergence of 1/α prediction vs nmax showing numerical stability
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, new_figure_multi, save, WHITE, GOLD, VIOLET
from ppm import alpha as alpha_module

# Left panel: ratio vs t
t_values = np.logspace(-3, 0, 200)  # t from 0.001 to 1.0
t_star = alpha_module.t_star(n=3)  # = 1/32 ≈ 0.03125

ratio_values = []
for t in t_values:
    theta_tau, theta_cp3 = alpha_module._twisted_heat_traces(t, nmax=300)
    if theta_cp3 > 0:
        ratio_values.append(theta_tau / theta_cp3)
    else:
        ratio_values.append(np.nan)

# Right panel: convergence in nmax
nmax_values = [10, 20, 50, 100, 200, 300]
alpha_pred_values = []

for nmax in nmax_values:
    theta_tau, theta_cp3 = alpha_module._twisted_heat_traces(t_star, nmax=nmax)
    alpha_pred = theta_tau / theta_cp3
    alpha_pred_values.append(1.0 / alpha_pred)

alpha_obs_inv = 137.036

# Create figure with two panels
fig, axes = new_figure_multi(1, 2, width=13, height=5.5)

# LEFT PANEL: ratio vs t
ax1 = axes[0]
ax1.loglog(t_values, ratio_values, color=GOLD, linewidth=2.5, label='Θ$^τ$/Θ$_{CP³}$(t)')
ax1.axvline(t_star, color=VIOLET, linestyle='--', linewidth=2, label=f't$^*$ = 1/32 ≈ {t_star:.5f}')
ax1.axhline(1/alpha_obs_inv, color=GOLD, linestyle=':', linewidth=2,
           label=f'α = 1/{alpha_obs_inv:.1f}')

# Mark the intersection
ax1.scatter([t_star], [1/alpha_obs_inv], s=150, color=GOLD, edgecolor=WHITE,
           linewidth=2, zorder=5, marker='*')

ax1.set_xlabel('t (log scale)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Θ$^τ$/Θ$_{CP³}$', fontsize=12, fontweight='bold')
ax1.set_title('Heat kernel ratio vs parameter', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.2, which='both')
ax1.legend(fontsize=10, loc='upper left')
ax1.set_xlim(0.0008, 1.2)

# RIGHT PANEL: convergence vs nmax
ax2 = axes[1]
ax2.semilogx(nmax_values, alpha_pred_values, 'o-', color=VIOLET, linewidth=2.5,
            markersize=8, markeredgecolor=WHITE, markeredgewidth=1.5,
            label='1/α(nmax) at t$^*$')
ax2.axhline(alpha_obs_inv, color=GOLD, linestyle='--', linewidth=2,
           label=f'Observed: 1/α = {alpha_obs_inv:.3f}')

# Annotation
ax2.text(50, alpha_pred_values[2] + 0.3, f'{alpha_pred_values[2]:.2f}',
        fontsize=10, color=VIOLET, fontweight='bold', ha='center')

ax2.set_xlabel('nmax (number of eigenvalues)', fontsize=12, fontweight='bold')
ax2.set_ylabel('1/α prediction', fontsize=12, fontweight='bold')
ax2.set_title('Convergence by nmax', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3, linestyle=':')
ax2.legend(fontsize=10, loc='lower right')
ax2.set_ylim(136.5, 137.5)

plt.tight_layout()
save(fig, 'v2_heat_kernel_convergence.png')

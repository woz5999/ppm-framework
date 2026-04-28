"""
fig_active_inference_torus.py — θ trajectory in T² overlaid on F-landscape

Plots the outer-loop θ-dynamics in the measurement torus T² = [0, π/2]²,
overlaid as colored paths on a contour plot of F[ρ, θ] for the initial state.

Multiple trajectories from different initial θ converge to fixed points,
demonstrating active inference as gradient descent on the actualization
free-energy landscape over the projective frame.

Run: python fig_active_inference_torus.py
"""

import sys
sys.path.insert(0, '../')

import math
import numpy as np
import matplotlib.pyplot as plt

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE

from ppm.dynamics import Basis, Density
from ppm.active_inference import (
    default_doublet_indices, free_energy_at_theta, ActiveInferenceLoop,
)


def main():
    apply_style()

    basis = Basis(k_max=1)
    doublet = default_doublet_indices(basis)
    idx_A = doublet[0]
    psi = basis.basis_vector(idx_A)
    rho_0 = Density.pure(basis, psi)

    # Build F-landscape contour for the initial ρ
    N_grid = 80
    eps = 1e-3
    theta_grid = np.linspace(eps, math.pi/2 - eps, N_grid)
    F_grid = np.zeros((N_grid, N_grid))
    for i, t_AB in enumerate(theta_grid):
        for j, t_CD in enumerate(theta_grid):
            F_grid[i, j] = free_energy_at_theta(
                rho_0, basis, doublet, float(t_AB), float(t_CD))
    # Cap +inf values for plotting
    finite_max = np.nanmax(F_grid[np.isfinite(F_grid)])
    F_grid_capped = np.where(np.isfinite(F_grid), F_grid, finite_max)

    fig, ax = plt.subplots(figsize=(9, 8), facecolor=BG)
    ax.set_facecolor(BG)

    # Contour: F-landscape (using θ_AB on x, θ_CD on y; transpose since F[i,j] uses i=AB, j=CD)
    cs = ax.contourf(theta_grid, theta_grid, F_grid_capped.T,
                     levels=20, cmap='magma', alpha=0.7)
    cb = plt.colorbar(cs, ax=ax, pad=0.02)
    cb.set_label(r'$\mathcal{F}[\rho_0, \theta]$', color=WHITE, fontsize=11)
    cb.ax.yaxis.set_tick_params(color=WHITE)
    plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color=WHITE)

    # Three trajectories from different initial θ
    initial_thetas = [
        (math.pi/4, math.pi/4),
        (math.pi/3, math.pi/6),
        (1.0, 1.0),
        (0.4, 1.2),
    ]
    colors = [GOLD, CYAN, VIOLET, '#2ECC71']  # green for variety
    labels = [
        r'$\theta_0 = (\pi/4, \pi/4)$',
        r'$\theta_0 = (\pi/3, \pi/6)$',
        r'$\theta_0 = (1.0, 1.0)$',
        r'$\theta_0 = (0.4, 1.2)$',
    ]

    for theta_init, color, label in zip(initial_thetas, colors, labels):
        loop = ActiveInferenceLoop(
            rho_0, theta_init, basis, doublet,
            dt=0.05, eta=0.05, N_inner=20, gamma=0.5)
        loop.run(n_cycles=150)
        thetas_AB = [s['theta_AB'] for s in loop.trajectory]
        thetas_CD = [s['theta_CD'] for s in loop.trajectory]
        ax.plot(thetas_AB, thetas_CD, color=color, linewidth=2.0,
                marker='o', markersize=2.5, alpha=0.95, label=label)
        # Start marker (large)
        ax.plot(thetas_AB[0], thetas_CD[0], marker='o', markersize=12,
                color=color, markeredgecolor=WHITE, markeredgewidth=1.5,
                zorder=10)
        # End marker (square)
        ax.plot(thetas_AB[-1], thetas_CD[-1], marker='s', markersize=12,
                color=color, markeredgecolor=WHITE, markeredgewidth=1.5,
                zorder=10)

    # Axis labels and torus annotations
    ax.set_xlabel(r'$\theta_{AB}$  (Kähler doublet angle)',
                  fontsize=12, color=WHITE, weight='bold')
    ax.set_ylabel(r'$\theta_{CD}$  (gauge doublet angle)',
                  fontsize=12, color=WHITE, weight='bold')
    ax.set_title('Active Inference Trajectories on the Measurement Torus '
                 r'$T^2 = [0, \pi/2]^2$',
                 fontsize=13, color=WHITE, weight='bold')

    ax.set_xticks([0, math.pi/8, math.pi/4, 3*math.pi/8, math.pi/2])
    ax.set_xticklabels(['$0$', r'$\pi/8$', r'$\pi/4$',
                         r'$3\pi/8$', r'$\pi/2$'])
    ax.set_yticks([0, math.pi/8, math.pi/4, 3*math.pi/8, math.pi/2])
    ax.set_yticklabels(['$0$', r'$\pi/8$', r'$\pi/4$',
                         r'$3\pi/8$', r'$\pi/2$'])
    ax.set_xlim(0, math.pi/2)
    ax.set_ylim(0, math.pi/2)
    ax.legend(fontsize=10, loc='upper right',
              facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.8)

    # Corner annotations: which fact-type is read out at each torus corner
    ax.annotate('A & C readout', xy=(0.02, 0.02), xytext=(0.05, 0.03),
                fontsize=9, color=WHITE, style='italic',
                xycoords='data')
    ax.annotate('B & D readout', xy=(math.pi/2 - 0.05, math.pi/2 - 0.05),
                xytext=(math.pi/2 - 0.4, math.pi/2 - 0.05),
                fontsize=9, color=WHITE, style='italic',
                ha='right', xycoords='data')

    plt.tight_layout()
    save(fig, 'fig_active_inference_torus.png')


if __name__ == '__main__':
    main()

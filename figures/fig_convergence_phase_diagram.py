"""
fig_convergence_phase_diagram.py — Noise × integration regime map

A phase-diagram-style portrait of active inference's convergence regime
in the (perception noise σ, integration count N) plane at fixed adaptation
rate η. Each cell is the seed-averaged in-goal residence (fraction of the
last 50 steps the agent stays inside the goal radius). Brighter = better
convergence.

Reveals the framework's regime structure:
  - Bottom-left  (low noise, low N):  agent succeeds with bare gradient.
  - Top-right    (high noise, high N): aggregation recovers signal.
  - Bottom-right (low noise, high N):  diminishing returns; success.
  - Top-left     (high noise, low N):  agent fails — noise dominates.

The diagonal failure boundary is the framework's R ≈ 1 surface in this
experimental projection. Crossing it requires either reducing noise
(impossible if the noise is intrinsic) or growing N — the framework's
prescribed mechanism.

Two-panel composition:
  Top:    Heatmap of in-goal residence in (σ, N) plane.
  Bottom: 1-D slices through the heatmap at three N values, showing
          residence as a function of noise. Crossover inflections visible.

Run: python fig_convergence_phase_diagram.py
"""

import sys
sys.path.insert(0, '../')

import math
import time
import numpy as np
import matplotlib.pyplot as plt

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE

from ppm.dynamics import Basis, Density
from ppm.active_inference import default_doublet_indices, FrameFindingLoop


def _hidden_state_with_2d_structure(basis, doublet, alpha_K, alpha_G, mix=0.7):
    idx_A, idx_B, idx_C, idx_D = doublet
    a = mix
    b = math.sqrt(1.0 - mix * mix)
    psi = (a * math.cos(alpha_K) * basis.basis_vector(idx_A)
           + a * math.sin(alpha_K) * basis.basis_vector(idx_B)
           + b * math.cos(alpha_G) * basis.basis_vector(idx_C)
           + b * math.sin(alpha_G) * basis.basis_vector(idx_D))
    return Density.pure(basis, psi)


def _residence_at(rho, basis, doublet, theta_init, target,
                   eta, exec_noise, signal_noise, N_aggregate,
                   n_steps, n_seeds, goal_radius):
    """Run n_seeds trials, return mean in-goal residence (last 50 steps)."""
    target_AB, target_CD = target
    residences = []
    for seed in range(11, 11 + n_seeds):
        loop = FrameFindingLoop(
            rho, theta_init, basis, doublet,
            eta=eta, noise_sigma=exec_noise,
            signal_noise_sigma=signal_noise,
            N_aggregate=N_aggregate, seed=seed)
        loop.run(n_steps=n_steps)
        last_n = loop.trajectory[-50:]
        in_goal = sum(
            1 for s in last_n
            if math.hypot(s['theta_AB'] - target_AB,
                           s['theta_CD'] - target_CD) < goal_radius)
        residences.append(in_goal / len(last_n))
    return float(np.mean(residences))


def main():
    apply_style()

    basis = Basis(k_max=1)
    doublet = default_doublet_indices(basis)
    target_AB = math.pi / 3
    target_CD = math.pi / 6
    rho = _hidden_state_with_2d_structure(
        basis, doublet, target_AB, target_CD, mix=0.7)
    target = (target_AB, target_CD)
    GOAL_RADIUS = 0.08

    theta_init = (math.pi / 8, 3 * math.pi / 8)
    n_steps = 200
    n_seeds = 4
    eta = 0.05
    exec_noise = 0.025

    sigma_grid = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
    N_grid = np.array([1, 2, 4, 8, 16, 32])

    print(f"Sweeping {len(sigma_grid)} × {len(N_grid)} × {n_seeds} = "
          f"{len(sigma_grid) * len(N_grid) * n_seeds} simulations...")
    t0 = time.time()
    residence_grid = np.zeros((len(N_grid), len(sigma_grid)))
    for i, N in enumerate(N_grid):
        for j, sigma in enumerate(sigma_grid):
            residence_grid[i, j] = _residence_at(
                rho, basis, doublet, theta_init, target,
                eta, exec_noise, float(sigma), int(N),
                n_steps, n_seeds, GOAL_RADIUS)
        print(f"  N={int(N):3d}: row done ({time.time()-t0:.1f}s)")

    # ─── Build figure ───────────────────────────────────────────────────────
    fig = plt.figure(figsize=(11, 11), facecolor=BG)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.4, 1.0], hspace=0.32)
    ax_map = fig.add_subplot(gs[0, 0])
    ax_slice = fig.add_subplot(gs[1, 0])
    for ax in [ax_map, ax_slice]:
        ax.set_facecolor(BG)
        ax.tick_params(colors=WHITE)

    # ─── Top: heatmap ───────────────────────────────────────────────────────
    im = ax_map.imshow(residence_grid, origin='lower', aspect='auto',
                        cmap='viridis', vmin=0, vmax=1,
                        extent=[sigma_grid[0] - 0.25,
                                 sigma_grid[-1] + 0.25,
                                 -0.5, len(N_grid) - 0.5])
    cb = plt.colorbar(im, ax=ax_map, pad=0.02)
    cb.set_label('in-goal residence (fraction of last 50 steps)',
                  color=WHITE, fontsize=11)
    cb.ax.yaxis.set_tick_params(color=WHITE)
    plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color=WHITE)

    # Annotate cell values
    for i in range(len(N_grid)):
        for j in range(len(sigma_grid)):
            v = residence_grid[i, j]
            txt_color = WHITE if v < 0.55 else BG
            ax_map.text(sigma_grid[j], i, f'{v*100:.0f}',
                         color=txt_color, fontsize=9,
                         ha='center', va='center', weight='bold')

    # Sketch the failure boundary (residence drops below 30% threshold)
    boundary_sigmas = []
    boundary_Ns = []
    for j, sigma in enumerate(sigma_grid):
        # Find smallest N where residence > 0.3
        col = residence_grid[:, j]
        for i in range(len(N_grid)):
            if col[i] > 0.3:
                boundary_sigmas.append(sigma)
                boundary_Ns.append(i)
                break
    if len(boundary_sigmas) > 1:
        ax_map.plot(boundary_sigmas, boundary_Ns, color='#FFE066',
                     linestyle='--', linewidth=2.5, alpha=0.85,
                     label='30% residence threshold')
        ax_map.legend(loc='lower right', fontsize=10,
                       facecolor='#0a0a1a', edgecolor=WHITE,
                       framealpha=0.92)

    # Annotate regime corners
    ax_map.text(sigma_grid[0] + 0.1, len(N_grid) - 0.7,
                 'easy: low noise + high N',
                 color='#FFE066', fontsize=9, style='italic',
                 ha='left', va='center', weight='bold')
    ax_map.text(sigma_grid[-1] - 0.1, 0.4,
                 'fails: high noise + low N',
                 color='#FF6B6B', fontsize=9, style='italic',
                 ha='right', va='center', weight='bold')

    ax_map.set_xticks(sigma_grid)
    ax_map.set_xticklabels([f'{s:.1f}' for s in sigma_grid],
                            color=WHITE)
    ax_map.set_yticks(range(len(N_grid)))
    ax_map.set_yticklabels([f'$N = {int(n)}$' for n in N_grid],
                            color=WHITE)
    ax_map.set_xlabel(r'perception noise $\sigma_{\rm signal}$',
                      color=WHITE, fontsize=12, weight='bold')
    ax_map.set_ylabel(r'integration count $N$ (Φ-aggregation depth)',
                      color=WHITE, fontsize=12, weight='bold')
    ax_map.set_title(r'Convergence Regime Map: where active inference works '
                      r'in the (noise, integration) plane',
                      color=WHITE, fontsize=12.5, weight='bold')

    # ─── Bottom: 1-D slices ─────────────────────────────────────────────────
    slice_N_indices = [0, 2, 5]   # N=1, 4, 32
    slice_colors = [ORANGE, VIOLET, CYAN]
    for idx, color in zip(slice_N_indices, slice_colors):
        N = int(N_grid[idx])
        ax_slice.plot(sigma_grid, residence_grid[idx, :],
                       color=color, linewidth=2.8,
                       marker='o', markersize=9, markerfacecolor=color,
                       markeredgecolor=WHITE, markeredgewidth=1.0,
                       label=fr'$N = {N}$')
    ax_slice.axhline(y=0.3, color=GOLD, linestyle=':', linewidth=1.5,
                      alpha=0.6, label='30% residence threshold')
    ax_slice.set_xlabel(r'perception noise $\sigma_{\rm signal}$',
                        color=WHITE, fontsize=12, weight='bold')
    ax_slice.set_ylabel('in-goal residence',
                        color=WHITE, fontsize=12, weight='bold')
    ax_slice.set_title('Slices through the regime map: residence vs noise '
                        'at three integration levels',
                        color=WHITE, fontsize=12, weight='bold')
    ax_slice.set_ylim(0, 1.05)
    ax_slice.set_xlim(sigma_grid[0] - 0.05, sigma_grid[-1] + 0.05)
    ax_slice.grid(True, alpha=0.3, color='#1a1a2e')
    ax_slice.legend(loc='upper right', fontsize=10,
                     facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.92)

    # Footer
    fig.text(0.5, 0.012,
              fr'Each cell is the mean over {n_seeds} seeds at '
              fr'$\eta = {eta}$, $\sigma_{{\rm exec}} = {exec_noise}$. '
              r'The yellow dashed line is the 30%-residence iso-contour: '
              r'the framework''s noise boundary in this projection. '
              r'Crossing it requires either reducing noise or growing $N$.',
              ha='center', color=GRAY, fontsize=9, style='italic',
              wrap=True)

    plt.tight_layout(rect=[0, 0.025, 1, 1])
    save(fig, 'fig_convergence_phase_diagram.png')


if __name__ == '__main__':
    main()

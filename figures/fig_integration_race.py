"""
fig_integration_race.py — Integration matters: race at fixed η, varying N

Companion to fig_frame_finding.py. The frame-finding race held noise fixed
and varied η to show that adaptation rate matters. This figure holds η fixed
(in the noise-dominated regime) and varies the integration count N to show
that aggregation capacity matters in exactly that regime.

Setup:
  - Same hidden state ρ with 2D doublet structure.
  - All agents share η, perception noise σ_signal, execution noise σ_exec,
    and the same starting frame θ_0. Only N_aggregate differs.
  - Six contestants at N ∈ {1, 2, 5, 15, 30, 60}.
  - Plus three random walkers as the no-gradient baseline.

Demonstration: at fixed η in the noise regime, low-N agents thrash and fail
to reach the goal. As N grows, the gradient signal emerges from the noise
and the agent converges. Time-to-goal decreases monotonically with N until
execution noise (which aggregation cannot suppress) becomes the bottleneck.

Run: python fig_integration_race.py
"""

import sys
sys.path.insert(0, '../')

import math
import numpy as np
import matplotlib.pyplot as plt

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE

from ppm.dynamics import Basis, Density
from ppm.active_inference import (
    default_doublet_indices, free_energy_at_theta,
    FrameFindingLoop, RandomFrameWalk,
)


def _hidden_state_with_2d_structure(basis, doublet, alpha_K, alpha_G, mix=0.7):
    idx_A, idx_B, idx_C, idx_D = doublet
    a = mix
    b = math.sqrt(1.0 - mix * mix)
    psi = (a * math.cos(alpha_K) * basis.basis_vector(idx_A)
           + a * math.sin(alpha_K) * basis.basis_vector(idx_B)
           + b * math.cos(alpha_G) * basis.basis_vector(idx_C)
           + b * math.sin(alpha_G) * basis.basis_vector(idx_D))
    return Density.pure(basis, psi)


def _in_goal_fraction(traj, target_AB, target_CD, radius=0.08, window=50):
    """
    Fraction of the last `window` steps the agent spends inside the goal
    radius. Higher = agent has actually CONVERGED and is staying near the
    optimum. Replaces first-entry time as the metric, since the latter
    rewards lucky noise excursions over genuine convergence.
    """
    last_n = traj[-window:] if len(traj) >= window else traj
    in_goal = sum(1 for s in last_n
                  if math.hypot(s['theta_AB'] - target_AB,
                                 s['theta_CD'] - target_CD) < radius)
    return in_goal / len(last_n)


def main():
    apply_style()

    basis = Basis(k_max=1)
    doublet = default_doublet_indices(basis)
    target_AB = math.pi / 3
    target_CD = math.pi / 6
    rho_target = _hidden_state_with_2d_structure(
        basis, doublet, target_AB, target_CD, mix=0.7)
    target = (target_AB, target_CD)
    GOAL_RADIUS = 0.08

    theta_init = (math.pi / 8, 3 * math.pi / 8)
    n_steps = 200

    # All agents share η + noise; only N_aggregate differs
    ETA = 0.05
    SIGNAL_NOISE = 1.5    # high — pushes us into the R≈1 regime
    EXEC_NOISE = 0.025
    N_values = [1, 2, 5, 15, 30, 60]
    seeds = [11, 23, 41, 67, 89, 103]

    cmap = plt.get_cmap('cool')
    colors = [cmap(i / max(1, len(N_values) - 1)) for i in range(len(N_values))]

    rw_configs = [
        ('RW-1', 0.05, 7),
        ('RW-2', 0.07, 17),
    ]

    print(f"Running {len(N_values)} integration levels + "
          f"{len(rw_configs)} random walks...")
    integration_runs = []
    for N, color, seed in zip(N_values, colors, seeds):
        loop = FrameFindingLoop(
            rho_target, theta_init, basis, doublet,
            eta=ETA, noise_sigma=EXEC_NOISE,
            signal_noise_sigma=SIGNAL_NOISE,
            N_aggregate=N, seed=seed)
        loop.run(n_steps=n_steps)
        residence = _in_goal_fraction(loop.trajectory, target_AB, target_CD,
                                       radius=GOAL_RADIUS, window=50)
        integration_runs.append({
            'label': fr'$N = {N}$',
            'N': N,
            'color': color,
            'trajectory': loop.trajectory,
            'residence': residence,
        })

    random_runs = []
    for label, step_size, seed in rw_configs:
        loop = RandomFrameWalk(rho_target, theta_init, basis, doublet,
                                step_size=step_size, seed=seed)
        loop.run(n_steps=n_steps)
        residence = _in_goal_fraction(loop.trajectory, target_AB, target_CD,
                                       radius=GOAL_RADIUS, window=50)
        random_runs.append({
            'label': fr'{label} (step={step_size})',
            'color': GRAY,
            'trajectory': loop.trajectory,
            'residence': residence,
        })

    # ─── F-landscape contour ────────────────────────────────────────────────
    N_grid = 70
    eps = 1e-3
    theta_grid = np.linspace(eps, math.pi/2 - eps, N_grid)
    F_grid = np.zeros((N_grid, N_grid))
    for i, t_AB in enumerate(theta_grid):
        for j, t_CD in enumerate(theta_grid):
            F_grid[i, j] = free_energy_at_theta(
                rho_target, basis, doublet, float(t_AB), float(t_CD))
    finite_max = np.nanmax(F_grid[np.isfinite(F_grid)])
    F_grid_capped = np.where(np.isfinite(F_grid), F_grid, finite_max)

    # ─── Figure ─────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(13, 12), facecolor=BG)
    gs = fig.add_gridspec(2, 2, width_ratios=[2, 1],
                           height_ratios=[1.5, 1.0],
                           wspace=0.20, hspace=0.32)
    ax = fig.add_subplot(gs[0, 0])
    ax_score = fig.add_subplot(gs[0, 1])
    ax_F = fig.add_subplot(gs[1, :])
    for a in [ax, ax_score, ax_F]:
        a.set_facecolor(BG)
        a.tick_params(colors=WHITE)

    cs = ax.contourf(theta_grid, theta_grid, F_grid_capped.T,
                     levels=24, cmap='magma', alpha=0.85)
    cb = plt.colorbar(cs, ax=ax, pad=0.10, location='left')
    cb.set_label(r'$\mathcal{F}[\rho_{\rm hidden}, \theta]$',
                  color=WHITE, fontsize=11)
    cb.ax.yaxis.set_tick_params(color=WHITE)
    plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color=WHITE)

    # Goal radius
    goal_circle = plt.Circle(target, GOAL_RADIUS, fill=False,
                              color='#FFE066', linestyle='--', linewidth=1.8,
                              alpha=0.9, zorder=10)
    ax.add_patch(goal_circle)

    # Random walks (underneath)
    for run in random_runs:
        traj = run['trajectory']
        AB = np.array([s['theta_AB'] for s in traj])
        CD = np.array([s['theta_CD'] for s in traj])
        ax.plot(AB, CD, color=run['color'], linewidth=0.9,
                 alpha=0.5, zorder=6)
        ax.plot(AB[-1], CD[-1], marker='D', markersize=10,
                 color=run['color'], markeredgecolor=WHITE,
                 markeredgewidth=1.2, alpha=0.8, zorder=11)

    # Integration agents (top) — draw FULL trajectory; the score is now
    # based on settled residence, not first-entry time.
    for run in integration_runs:
        traj = run['trajectory']
        AB = np.array([s['theta_AB'] for s in traj])
        CD = np.array([s['theta_CD'] for s in traj])
        ax.plot(AB, CD, color=run['color'], linewidth=1.6, alpha=0.85,
                 zorder=8)
        ax.plot(AB[-1], CD[-1], marker='s', markersize=12,
                 color=run['color'], markeredgecolor=WHITE,
                 markeredgewidth=1.5, zorder=12)

    # Common start
    ax.plot(theta_init[0], theta_init[1], marker='o', markersize=18,
             color=WHITE, markeredgecolor=BG, markeredgewidth=2,
             zorder=13, alpha=0.95)
    ax.annotate('start', xy=theta_init,
                xytext=(theta_init[0] - 0.06, theta_init[1] + 0.06),
                color=WHITE, fontsize=10, weight='bold', ha='right')

    # Goal star (no annotation per the convention)
    ax.plot(target_AB, target_CD, marker='*', markersize=24,
             color='#FFE066', markeredgecolor=WHITE, markeredgewidth=1.5,
             zorder=14)

    ax.set_xlabel(r'$\theta_{AB}$', color=WHITE, fontsize=12, weight='bold')
    ax.set_ylabel(r'$\theta_{CD}$', color=WHITE, fontsize=12, weight='bold')
    ax.set_title('Integration Race: Fixed η, Varying Aggregation Count N',
                 color=WHITE, fontsize=13, weight='bold')
    ax.set_xticks([0, math.pi/8, math.pi/4, 3*math.pi/8, math.pi/2])
    ax.set_xticklabels(['$0$', r'$\pi/8$', r'$\pi/4$',
                         r'$3\pi/8$', r'$\pi/2$'])
    ax.set_yticks([0, math.pi/8, math.pi/4, 3*math.pi/8, math.pi/2])
    ax.set_yticklabels(['$0$', r'$\pi/8$', r'$\pi/4$',
                         r'$3\pi/8$', r'$\pi/2$'])
    ax.set_xlim(0, math.pi/2)
    ax.set_ylim(0, math.pi/2)

    # Right: scoreboard — in-goal residence (last 50 steps)
    ax_score.set_title('In-Goal Residence (last 50 steps)',
                        color=WHITE, fontsize=12, weight='bold')
    rows = []
    for run in integration_runs:
        rows.append((run['label'], run['color'], run['residence']))
    for run in random_runs:
        rows.append((run['label'], run['color'], run['residence']))

    bar_values = [r for _, _, r in rows]
    y_pos = np.arange(len(rows))
    bars = ax_score.barh(y_pos, bar_values,
                          color=[c for _, c, _ in rows],
                          edgecolor=WHITE, linewidth=1.0, alpha=0.9)
    ax_score.set_yticks(y_pos)
    ax_score.set_yticklabels([lbl for lbl, _, _ in rows],
                              color=WHITE, fontsize=10)
    ax_score.invert_yaxis()
    ax_score.set_xlabel('fraction of time at goal',
                         color=WHITE, fontsize=11)
    ax_score.set_xlim(0, 1.05)
    ax_score.axvline(x=1.0, color=GRAY, linestyle=':', linewidth=1.0,
                      alpha=0.5)

    for bar, (label, color, residence) in zip(bars, rows):
        x = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        ax_score.text(x + 0.015, y, f'{residence * 100:.0f}%',
                       color=WHITE, fontsize=9, va='center',
                       weight='bold')

    ax_score.grid(axis='x', alpha=0.3, color='#1a1a2e')
    ax_score.set_facecolor(BG)

    # ─── Bottom: F(t) descent for all contestants ───────────────────────────
    for run in integration_runs:
        traj = run['trajectory']
        steps = np.array([s['step'] for s in traj])
        Fs = np.array([s['F'] for s in traj])
        ax_F.plot(steps, Fs, color=run['color'], linewidth=2.0,
                   label=run['label'], alpha=0.92)
    for run in random_runs:
        traj = run['trajectory']
        steps = np.array([s['step'] for s in traj])
        Fs = np.array([s['F'] for s in traj])
        ax_F.plot(steps, Fs, color=run['color'], linewidth=1.0,
                   linestyle='--', label=run['label'].split(' ')[0],
                   alpha=0.55)
    ax_F.axhline(y=0, color=GRAY, linestyle=':', linewidth=1.2, alpha=0.6)
    ax_F.set_xlabel('descent step', color=WHITE, fontsize=11, weight='bold')
    ax_F.set_ylabel(r'$\mathcal{F}[\rho_{\rm hidden}, \theta(t)]$',
                    color=WHITE, fontsize=11, weight='bold')
    ax_F.set_title(r'$\mathcal{F}$-Descent for All Contestants',
                    color=WHITE, fontsize=12, weight='bold')
    ax_F.legend(loc='upper right', fontsize=9, ncol=2,
                 facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.92)
    ax_F.set_xlim(0, n_steps)
    ax_F.grid(True, alpha=0.3, color='#1a1a2e')

    # Footer
    fig.text(0.5, 0.027,
              fr'Goal radius = {GOAL_RADIUS} rad. All agents share '
              fr'$\eta = {ETA}$, perception noise $\sigma_{{\rm signal}} = {SIGNAL_NOISE}$, '
              fr'execution noise $\sigma_{{\rm exec}} = {EXEC_NOISE}$, and starting frame. '
              fr'Only $N_{{\rm aggregate}}$ differs.',
              ha='center', color=GRAY, fontsize=9, style='italic')
    fig.text(0.5, 0.005,
              r'Higher $N$ recovers the gradient signal from noise as $1/\sqrt{N}$ — '
              r'the framework''s prescribed mechanism for the resolvability '
              r'boundary. Plateau at high $N$: execution noise (which '
              r'aggregation cannot suppress) becomes the bottleneck.',
              ha='center', color=GRAY, fontsize=9, style='italic')

    plt.tight_layout(rect=[0, 0.045, 1, 1])
    save(fig, 'fig_integration_race.png')


if __name__ == '__main__':
    main()

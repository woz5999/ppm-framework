"""
fig_frame_finding.py — Multi-competitor race for the optimal measurement frame

A field of contestants tries to find the hidden optimal frame θ* on the
measurement torus T². Each starts from the same offset position; all are
allowed the same number of steps.

Contestants:
  - Four ACTIVE INFERENCE agents at varying adaptation rates η ∈
    {0.01, 0.03, 0.07, 0.15}.
  - Three RANDOM WALKERS with varying step sizes / seeds (no gradient info).

Visuals:
  - F-landscape contour as backdrop.
  - Each agent's path drawn with color-coded markers/line.
  - "Goal" radius around θ* marked with a dashed circle.
  - For each agent that reached the goal: annotation with η and
    time-to-goal (number of steps).
  - Failed agents (random walks that never reach) end wherever they wander.

Demonstration: increasing η monotonically decreases time-to-goal. Random
walks generally fail to reach the goal at all. Active inference's
selective advantage is the gradient information that turns frame search
from random exploration into directed descent.

Run: python fig_frame_finding.py
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


def _hidden_state_with_2d_structure(basis, doublet, alpha_K, alpha_G,
                                     mix=0.7):
    """ρ = |ψ⟩⟨ψ| with structure in both Kähler and gauge doublets."""
    idx_A, idx_B, idx_C, idx_D = doublet
    a = mix
    b = math.sqrt(1.0 - mix * mix)
    psi = (a * math.cos(alpha_K) * basis.basis_vector(idx_A)
           + a * math.sin(alpha_K) * basis.basis_vector(idx_B)
           + b * math.cos(alpha_G) * basis.basis_vector(idx_C)
           + b * math.sin(alpha_G) * basis.basis_vector(idx_D))
    return Density.pure(basis, psi)


def _time_to_goal(traj, target_AB, target_CD, radius=0.08):
    """Return the first step index at which the trajectory enters the
    goal radius around θ*, or None if it never does."""
    for snap in traj:
        d = math.hypot(snap['theta_AB'] - target_AB,
                        snap['theta_CD'] - target_CD)
        if d < radius:
            return snap['step']
    return None


def main():
    apply_style()

    basis = Basis(k_max=1)
    doublet = default_doublet_indices(basis)

    # Hidden state with structure in BOTH doublets so optimum is genuinely 2D
    target_AB = math.pi / 3        # ~1.047
    target_CD = math.pi / 6        # ~0.524
    rho_target = _hidden_state_with_2d_structure(
        basis, doublet, target_AB, target_CD, mix=0.7)
    target = (target_AB, target_CD)
    GOAL_RADIUS = 0.08

    # All contestants start from same offset frame
    theta_init = (math.pi / 8, 3 * math.pi / 8)
    n_steps = 250

    # Active inference agents at four adaptation rates, each with its own
    # RNG seed so noisy paths differentiate visually. Same noise_sigma across
    # agents so the only systematic difference is η.
    eta_values = [0.01, 0.03, 0.07, 0.15]
    seeds = [11, 23, 41, 67]
    NOISE_SIGMA = 0.04
    cmap_active = plt.get_cmap('cool')
    active_colors = [cmap_active(i / max(1, len(eta_values) - 1))
                     for i in range(len(eta_values))]

    # Random walkers (varying seeds + step sizes)
    rw_configs = [
        ('RW-1', 0.04, 7),
        ('RW-2', 0.06, 17),
        ('RW-3', 0.08, 29),
    ]

    print("Running competitors...")
    active_runs = []
    for eta, color, seed in zip(eta_values, active_colors, seeds):
        loop = FrameFindingLoop(rho_target, theta_init, basis, doublet,
                                 eta=eta,
                                 noise_sigma=NOISE_SIGMA, seed=seed)
        loop.run(n_steps=n_steps)
        ttg = _time_to_goal(loop.trajectory, target_AB, target_CD,
                             radius=GOAL_RADIUS)
        active_runs.append({
            'label': fr'$\eta = {eta}$',
            'eta': eta,
            'color': color,
            'trajectory': loop.trajectory,
            'time_to_goal': ttg,
        })

    random_runs = []
    for label, step_size, seed in rw_configs:
        loop = RandomFrameWalk(rho_target, theta_init, basis, doublet,
                                step_size=step_size, seed=seed)
        loop.run(n_steps=n_steps)
        ttg = _time_to_goal(loop.trajectory, target_AB, target_CD,
                             radius=GOAL_RADIUS)
        random_runs.append({
            'label': fr'{label} (step={step_size})',
            'step_size': step_size,
            'color': GRAY,
            'trajectory': loop.trajectory,
            'time_to_goal': ttg,
        })

    # ─── F-landscape contour ────────────────────────────────────────────────
    N_grid = 80
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
                           wspace=0.18, hspace=0.32)
    ax = fig.add_subplot(gs[0, 0])
    ax_score = fig.add_subplot(gs[0, 1])
    ax_F = fig.add_subplot(gs[1, :])
    for a in [ax, ax_score, ax_F]:
        a.set_facecolor(BG)
        a.tick_params(colors=WHITE)

    # Backdrop: F-landscape contour
    cs = ax.contourf(theta_grid, theta_grid, F_grid_capped.T,
                     levels=24, cmap='magma', alpha=0.85)
    cb = plt.colorbar(cs, ax=ax, pad=0.10, location='left')
    cb.set_label(r'$\mathcal{F}[\rho_{\rm hidden}, \theta]$',
                  color=WHITE, fontsize=11)
    cb.ax.yaxis.set_tick_params(color=WHITE)
    plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color=WHITE)

    # Draw goal radius
    goal_circle = plt.Circle(target, GOAL_RADIUS, fill=False,
                              color='#FFE066', linestyle='--', linewidth=1.8,
                              alpha=0.9, zorder=10)
    ax.add_patch(goal_circle)

    # Random walk paths (drawn first so they sit underneath)
    for run in random_runs:
        traj = run['trajectory']
        AB = np.array([s['theta_AB'] for s in traj])
        CD = np.array([s['theta_CD'] for s in traj])
        ax.plot(AB, CD, color=run['color'], linewidth=0.9, alpha=0.55,
                 zorder=6)
        ax.plot(AB[-1], CD[-1], marker='D', markersize=10,
                 color=run['color'], markeredgecolor=WHITE,
                 markeredgewidth=1.2, alpha=0.8, zorder=11)

    # Active inference paths (drawn on top)
    for run in active_runs:
        traj = run['trajectory']
        AB = np.array([s['theta_AB'] for s in traj])
        CD = np.array([s['theta_CD'] for s in traj])
        ttg = run['time_to_goal']
        # Cap drawn path at time-to-goal if reached, else full trajectory
        end_idx = ttg if ttg is not None else len(traj) - 1
        ax.plot(AB[:end_idx + 1], CD[:end_idx + 1],
                 color=run['color'], linewidth=2.2, alpha=0.92, zorder=8)
        # Final marker
        ax.plot(AB[end_idx], CD[end_idx], marker='s', markersize=12,
                 color=run['color'], markeredgecolor=WHITE,
                 markeredgewidth=1.5, zorder=12)

    # Common start
    ax.plot(theta_init[0], theta_init[1], marker='o', markersize=18,
             color=WHITE, markeredgecolor=BG, markeredgewidth=2,
             zorder=13, alpha=0.95)
    ax.annotate('start', xy=theta_init,
                xytext=(theta_init[0] - 0.06, theta_init[1] + 0.06),
                color=WHITE, fontsize=10, weight='bold', ha='right')

    # Hidden goal
    ax.plot(target_AB, target_CD, marker='*', markersize=24,
             color='#FFE066', markeredgecolor=WHITE, markeredgewidth=1.5,
             zorder=14)

    # Axis formatting
    ax.set_xlabel(r'$\theta_{AB}$', color=WHITE, fontsize=12, weight='bold')
    ax.set_ylabel(r'$\theta_{CD}$', color=WHITE, fontsize=12, weight='bold')
    ax.set_title('Frame-Finding Race: Active Inference vs Random Walk',
                 color=WHITE, fontsize=13, weight='bold')
    ax.set_xticks([0, math.pi/8, math.pi/4, 3*math.pi/8, math.pi/2])
    ax.set_xticklabels(['$0$', r'$\pi/8$', r'$\pi/4$',
                         r'$3\pi/8$', r'$\pi/2$'])
    ax.set_yticks([0, math.pi/8, math.pi/4, 3*math.pi/8, math.pi/2])
    ax.set_yticklabels(['$0$', r'$\pi/8$', r'$\pi/4$',
                         r'$3\pi/8$', r'$\pi/2$'])
    ax.set_xlim(0, math.pi/2)
    ax.set_ylim(0, math.pi/2)

    # ─── Right panel: time-to-goal scoreboard ───────────────────────────────
    ax_score.set_title('Time to Goal (steps)',
                        color=WHITE, fontsize=12, weight='bold')
    # Build sorted list: active first by η (ascending), then random
    rows = []
    for run in active_runs:
        rows.append(('AI', run['label'], run['color'], run['time_to_goal']))
    for run in random_runs:
        rows.append(('RW', run['label'], run['color'], run['time_to_goal']))

    bar_colors = []
    bar_values = []
    bar_labels = []
    for kind, label, color, ttg in rows:
        bar_labels.append(label)
        bar_colors.append(color)
        bar_values.append(ttg if ttg is not None else n_steps)

    y_pos = np.arange(len(rows))
    bars = ax_score.barh(y_pos, bar_values, color=bar_colors,
                          edgecolor=WHITE, linewidth=1.0, alpha=0.9)
    ax_score.set_yticks(y_pos)
    ax_score.set_yticklabels(bar_labels, color=WHITE, fontsize=10)
    ax_score.invert_yaxis()
    ax_score.set_xlabel('steps', color=WHITE, fontsize=11)
    ax_score.set_xlim(0, n_steps * 1.05)

    # Mark the "did not finish" line at n_steps
    ax_score.axvline(x=n_steps, color=GRAY, linestyle=':', linewidth=1.2,
                      alpha=0.6)
    ax_score.text(n_steps * 1.01, len(rows) - 0.5, 'DNF',
                   color=GRAY, fontsize=8, ha='right', va='center',
                   style='italic')

    # Annotate each bar with the actual outcome
    for bar, (kind, label, color, ttg) in zip(bars, rows):
        x = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        if ttg is None:
            txt = 'did not reach'
            color_txt = GRAY
        else:
            txt = f'{ttg} steps'
            color_txt = WHITE
        ax_score.text(x + n_steps * 0.01, y, txt,
                       color=color_txt, fontsize=9, va='center',
                       weight='bold')

    ax_score.grid(axis='x', alpha=0.3, color='#1a1a2e')
    ax_score.set_facecolor(BG)

    # ─── Bottom: F(t) descent for all contestants ───────────────────────────
    for run in active_runs:
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

    # Footer (two-line)
    fig.text(0.5, 0.027,
              fr'Goal radius = {GOAL_RADIUS} rad. All contestants start at '
              fr'$\theta_0 = (\pi/8, 3\pi/8)$ and have {n_steps} steps. '
              fr'Active inference: $\theta$ steps along $-\nabla\mathcal{{F}}$ '
              fr'with $\mathcal{{N}}(0, {NOISE_SIGMA})$ step noise per agent. '
              fr'Random walk: Gaussian steps with no gradient information.',
              ha='center', color=GRAY, fontsize=9, style='italic')
    fig.text(0.5, 0.005,
              r"The $\eta$ below which active inference fails sits on the "
              r"framework's resolvability-ratio boundary $R(k) \approx 1$, "
              r"where per-event information drops to near zero.",
              ha='center', color=GRAY, fontsize=9, style='italic')

    plt.tight_layout(rect=[0, 0.045, 1, 1])
    save(fig, 'fig_frame_finding.png')


if __name__ == '__main__':
    main()

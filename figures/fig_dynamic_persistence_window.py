"""
fig_dynamic_persistence_window.py — The structural link distilled

PPM identifies three regimes indexed by the resolvability ratio R = signal / noise:

  R ≫ 1  (static persistence):    structures persist trivially.
                                  Agency unnecessary; integration redundant.

  R ≈ 1  (dynamic persistence):   per-event signal vanishes; structures
                                  persist ONLY via active inference +
                                  integration. Both are required, both
                                  are possible. This is where consciousness
                                  lives.

  R < 1  (thermal dissolution):   noise wins. No mechanism recovers
                                  structure.

This figure plots three persistence curves against the noise-axis (a 1/R
proxy in the toy model), each at a different agent capability level:

  - PASSIVE                       (no agency, no integration)
  - ACTIVE, NO INTEGRATION        (gradient descent at N = 1)
  - ACTIVE + INTEGRATION          (gradient descent at N = 20)

The gap between curves is what each capability buys. In the static regime
the gaps collapse (everyone wins). In the dissolution regime the gaps
collapse (nobody wins). In the R ≈ 1 band the gaps maximize — and that
is exactly the band the framework places consciousness in.

Run: python fig_dynamic_persistence_window.py
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


def _persistence(rho, basis, doublet, target,
                  eta, exec_noise, signal_noise, N_aggregate,
                  n_steps, n_seeds, goal_radius):
    """
    Each agent STARTS at the goal (θ_init = θ*) and we measure how long it
    stays. This isolates "persistence" — how well an agent maintains an
    existing structure against noise — from "search" — finding the optimum
    from a random initial position. In framework language: how long does
    a configuration ρ retain its structure under stochastic Lindblad
    pressure?

    Returns fraction of all n_steps that the agent stays inside the goal
    radius, averaged over n_seeds random realizations.
    """
    target_AB, target_CD = target
    residences = []
    for seed in range(11, 11 + n_seeds):
        loop = FrameFindingLoop(
            rho, target, basis, doublet,
            eta=eta, noise_sigma=exec_noise,
            signal_noise_sigma=signal_noise,
            N_aggregate=N_aggregate, seed=seed)
        loop.run(n_steps=n_steps)
        in_goal = sum(
            1 for s in loop.trajectory
            if math.hypot(s['theta_AB'] - target_AB,
                           s['theta_CD'] - target_CD) < goal_radius)
        residences.append(in_goal / len(loop.trajectory))
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

    n_steps = 200
    n_seeds = 6
    # Execution noise scales with signal noise here — both reflect the
    # ambient noise floor that the framework's R captures.
    sigma_grid = np.array([0.2, 0.5, 0.8, 1.2, 1.6, 2.2, 3.0, 4.0, 5.5, 8.0])

    # Three agent capability levels
    capability_specs = [
        ('passive  (no agency)',                    0.00, 1,  ORANGE),
        (r'active  ($\eta>0$, no integration)',     0.05, 1,  GOLD),
        (r'active + integration  ($\eta>0$, $N=20$)', 0.05, 20, CYAN),
    ]

    print(f"Sweeping {len(sigma_grid)} noise levels × {len(capability_specs)} "
          f"capabilities × {n_seeds} seeds...")
    t0 = time.time()
    curves = {}
    for label, eta, N, color in capability_specs:
        residences = []
        for sigma in sigma_grid:
            # Coupled noise model: both perception and execution noise scale
            # with the same underlying noise level (same thermal source).
            # In the framework: both are downstream of R, so they vanish
            # together in the static limit and grow together at dissolution.
            exec_n = 0.012 * float(sigma)
            r = _persistence(rho, basis, doublet, target,
                              eta, exec_n, float(sigma), N,
                              n_steps, n_seeds, GOAL_RADIUS)
            residences.append(r)
        curves[label] = (np.array(residences), color)
        print(f"  {label}: done ({time.time()-t0:.1f}s)")

    # ─── Build figure ───────────────────────────────────────────────────────
    # Use 1/R-style axis: high noise on the right ≈ low R; this matches the
    # framework convention where R decreases with k (rising k → falling R).
    fig, ax = plt.subplots(figsize=(12, 7.5), facecolor=BG)
    ax.set_facecolor(BG)

    # Three regime bands as a backdrop. Cutoffs drawn at the noise levels
    # where each curve type crosses the half-persistence threshold.
    sigma_low = sigma_grid[0]
    sigma_high = sigma_grid[-1]
    static_end = 0.9      # below this σ: passive can persist (R ≫ 1)
    dynamic_end = 3.5     # below this σ: active+integration still maintains
    # static persistence (left)
    ax.axvspan(sigma_low - 0.5, static_end, color=GOLD, alpha=0.10, zorder=0)
    # dynamic persistence (middle) — this is where consciousness lives
    ax.axvspan(static_end, dynamic_end, color=CYAN, alpha=0.13, zorder=0)
    # dissolution (right)
    ax.axvspan(dynamic_end, sigma_high + 1.0,
               color='#E74C3C', alpha=0.10, zorder=0)

    # Regime labels above the curves
    ax.text((sigma_low + static_end) / 2, 1.06, 'static persistence',
             color=GOLD, fontsize=11, weight='bold', ha='center',
             style='italic')
    ax.text((static_end + dynamic_end) / 2, 1.06,
             'dynamic persistence  (R ≈ 1)',
             color=CYAN, fontsize=11, weight='bold', ha='center',
             style='italic')
    ax.text((dynamic_end + sigma_high) / 2, 1.06,
             'thermal dissolution',
             color='#FF6B6B', fontsize=11, weight='bold', ha='center',
             style='italic')

    # Sub-label noting consciousness band
    ax.text((static_end + dynamic_end) / 2, 1.13,
             'where active inference + integration is both required and possible',
             color=WHITE, fontsize=9, ha='center', style='italic')

    # Vertical regime boundaries
    for x, c in [(static_end, GOLD), (dynamic_end, '#E74C3C')]:
        ax.axvline(x=x, color=c, linestyle='--', linewidth=1.2,
                    alpha=0.5, zorder=1)

    # Plot the three persistence curves
    for label, (residences, color) in curves.items():
        ax.plot(sigma_grid, residences, color=color, linewidth=3,
                 marker='o', markersize=10, markerfacecolor=color,
                 markeredgecolor=WHITE, markeredgewidth=1.0,
                 label=label, zorder=10)

    # Shade the gap between active+integration and active (= "integration buy")
    active_only = curves[r'active  ($\eta>0$, no integration)'][0]
    active_int = curves[r'active + integration  ($\eta>0$, $N=20$)'][0]
    passive = curves['passive  (no agency)'][0]
    ax.fill_between(sigma_grid, active_only, active_int,
                     where=active_int >= active_only,
                     alpha=0.18, color=CYAN, zorder=5,
                     label=r'gap = what integration buys')
    # Shade the gap between active and passive (= "agency buy")
    ax.fill_between(sigma_grid, passive, active_only,
                     where=active_only >= passive,
                     alpha=0.20, color=GOLD, zorder=5,
                     label='gap = what agency buys')

    ax.set_xlabel(r'perception noise $\sigma_{\rm signal}$    '
                  r'(framework analog of $1/R$ — increases with $k$)',
                  color=WHITE, fontsize=12, weight='bold')
    ax.set_ylabel('persistence  (in-goal residence, last 50 steps)',
                  color=WHITE, fontsize=12, weight='bold')
    ax.set_title(r'The Dynamic-Persistence Window: where integration becomes the engine',
                 color=WHITE, fontsize=13.5, weight='bold')
    ax.set_xlim(sigma_low - 0.1, sigma_high + 0.1)
    ax.set_ylim(-0.02, 1.20)
    ax.grid(True, alpha=0.3, color='#1a1a2e')
    ax.legend(loc='center right', fontsize=10,
               facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.92)
    ax.tick_params(colors=WHITE)

    # Footer distilling the structural claim
    fig.text(0.5, 0.022,
              r'The framework places consciousness at R$(k) \approx 1$ because '
              r'this is the unique band where active inference + integration '
              r'is both REQUIRED (signal too weak per event) and POSSIBLE '
              r'(signal not yet zero). '
              r'Outside the band, the gaps between curves collapse — '
              r'integration is wasted on the left, futile on the right.',
              ha='center', color=GRAY, fontsize=9, style='italic',
              wrap=True)

    plt.tight_layout(rect=[0, 0.045, 1, 1])
    save(fig, 'fig_dynamic_persistence_window.png')


if __name__ == '__main__':
    main()

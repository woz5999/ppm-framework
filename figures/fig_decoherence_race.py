"""
fig_decoherence_race.py — Actualization cost vs. adaptation rate (static)

Framework-native claim only: F[ρ, θ] is the actualization free energy — a
real quantitative cost the system pays per unit time. Adaptive θ-dynamics
descends F; frozen θ does not. Time-averaged F is monotone-decreasing in
adaptation rate η.

What the framework provides: this gradient. What climbs it (biology,
neuroscience, etc.) is downstream of the framework, not derivable from it.

Two-panel composition:
  Top:    F(t) trajectories for six contestants at varying η values.
          Frozen baseline (η=0) at top, fastest adapter at bottom.
          Visualizes that the framework's dynamics produces a divergence:
          systems with adaptive measurement frames pay lower cost.
  Bottom: Time-averaged ⟨F⟩ vs η — the cost gradient. Monotone-decreasing.
          This is the property of the framework's dynamics that downstream
          processes (biology) can exploit by implementing adaptation.

Run: python fig_decoherence_race.py
"""

import sys
sys.path.insert(0, '../')

import math
import time
import numpy as np
import matplotlib.pyplot as plt

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE

from ppm.dynamics import Basis, Density
from ppm.active_inference import default_doublet_indices, ActiveInferenceLoop


def main():
    apply_style()

    basis = Basis(k_max=1)
    doublet = default_doublet_indices(basis)

    psi = basis.basis_vector(doublet[0])
    rho_0 = Density.pure(basis, psi)
    theta_init = (math.pi/3, math.pi/3)

    etas = [0.0, 0.01, 0.02, 0.05, 0.10, 0.15]
    n_cycles = 60
    N_inner = 10
    dt = 0.05
    gamma = 0.5

    cmap = plt.get_cmap('cool')
    colors = [cmap(i / max(1, len(etas) - 1)) for i in range(len(etas))]
    colors[0] = GOLD  # frozen baseline gets the warm color

    print(f"Running {len(etas)} contestants...")
    t0 = time.time()
    trajectories = []
    mean_Fs = []
    for eta in etas:
        loop = ActiveInferenceLoop(
            rho_0, theta_init, basis, doublet,
            gamma=gamma, dt=dt, N_inner=N_inner, eta=float(eta))
        loop.run(n_cycles=n_cycles)
        trajectories.append(loop.trajectory)
        Fs = [s['F'] for s in loop.trajectory if not math.isinf(s['F'])]
        mean_Fs.append(float(sum(Fs) / len(Fs)) if Fs else float('inf'))
    print(f"  {time.time()-t0:.1f}s")

    # ─── Build figure ───────────────────────────────────────────────────────
    fig = plt.figure(figsize=(11, 9), facecolor=BG)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.3, 1.0], hspace=0.35)
    ax_traj = fig.add_subplot(gs[0, 0])
    ax_grad = fig.add_subplot(gs[1, 0])
    for ax in [ax_traj, ax_grad]:
        ax.set_facecolor(BG)
        ax.tick_params(colors=WHITE)
        ax.grid(True, alpha=0.3, color='#1a1a2e')

    # Top: F(t) trajectories for all contestants
    for traj, eta, color in zip(trajectories, etas, colors):
        ts = np.array([s['t'] for s in traj])
        Fs = np.array([s['F'] for s in traj])
        if eta == 0.0:
            label = fr'$\eta = 0$  (frozen frame)'
            ax_traj.plot(ts, Fs, color=color, linewidth=3,
                          linestyle='--', label=label, alpha=0.95)
        else:
            label = fr'$\eta = {eta}$'
            ax_traj.plot(ts, Fs, color=color, linewidth=2.5,
                          label=label, alpha=0.92)

    # Annotate the gap between frozen and fastest at t_final
    t_final = trajectories[0][-1]['t']
    F_frozen_final = trajectories[0][-1]['F']
    F_fast_final = trajectories[-1][-1]['F']
    ax_traj.annotate('', xy=(t_final * 0.92, F_fast_final),
                     xytext=(t_final * 0.92, F_frozen_final),
                     arrowprops=dict(arrowstyle='<->', color=VIOLET,
                                     lw=2, alpha=0.8))
    ax_traj.text(t_final * 0.94,
                 (F_frozen_final + F_fast_final) / 2,
                 fr'cost gap $\approx$ {F_frozen_final - F_fast_final:.2f} nats',
                 color=VIOLET, fontsize=10, weight='bold',
                 ha='left', va='center', style='italic')

    ax_traj.set_xlabel('time (dimensionless units)',
                       color=WHITE, fontsize=12, weight='bold')
    ax_traj.set_ylabel(r'actualization cost $\mathcal{F}[\rho(t), \theta(t)]$',
                       color=WHITE, fontsize=12, weight='bold')
    ax_traj.set_title(r'$\mathcal{F}$-Descent at Varying Adaptation Rates',
                       color=WHITE, fontsize=13, weight='bold')
    ax_traj.legend(loc='center right', fontsize=10,
                    facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.9,
                    ncol=2)
    ax_traj.set_xlim(0, t_final * 1.05)

    # Bottom: mean-F vs η (the gradient)
    ax_grad.plot(etas, mean_Fs, color=VIOLET, linewidth=3,
                  marker='o', markersize=11, markerfacecolor=GOLD,
                  markeredgecolor=WHITE, markeredgewidth=1.5)
    ax_grad.fill_between(etas, 0, mean_Fs, alpha=0.18, color=VIOLET)
    ax_grad.axhline(y=mean_Fs[0], color=GOLD, linestyle=':', linewidth=1.5,
                     alpha=0.7,
                     label=fr'frozen-frame cost: $\langle\mathcal{{F}}\rangle = {mean_Fs[0]:.3f}$')
    for eta, mF in zip(etas, mean_Fs):
        ax_grad.annotate(f'{mF:.2f}', xy=(eta, mF),
                          xytext=(0, 12), textcoords='offset points',
                          color=WHITE, fontsize=9, ha='center')
    ax_grad.set_xlabel(r'adaptation rate $\eta$  (outer-loop step size)',
                       color=WHITE, fontsize=12, weight='bold')
    ax_grad.set_ylabel(r'time-averaged actualization cost $\langle \mathcal{F} \rangle$',
                       color=WHITE, fontsize=12, weight='bold')
    ax_grad.set_title(r'The Cost Gradient: $\langle\mathcal{F}\rangle$ Decreases Monotonically with $\eta$',
                       color=WHITE, fontsize=12, weight='bold')
    ax_grad.set_xlim(min(etas) - 0.005, max(etas) + 0.015)
    ax_grad.set_ylim(0, max(mean_Fs) * 1.20)
    ax_grad.legend(loc='upper right', fontsize=10,
                    facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.85)

    # Two-line footer with framework-native framing
    fig.text(0.5, 0.027,
              r'$\mathcal{F} = -\log P$ is the framework-native cost of the next actualization. '
              r'All six systems share $\rho_0 = |A\rangle\langle A|$, $\theta_0 = (\pi/3, \pi/3)$, '
              r'identical Lindblad dynamics; only $\eta$ differs.',
              ha='center', color=GRAY, fontsize=9, style='italic')
    fig.text(0.5, 0.005,
              r'The framework provides this cost gradient. What climbs it (biology, '
              r'neural dynamics, etc.) is downstream of what PPM derives.',
              ha='center', color=GRAY, fontsize=9, style='italic')

    plt.tight_layout(rect=[0, 0.045, 1, 1])
    save(fig, 'fig_decoherence_race.png')


if __name__ == '__main__':
    main()

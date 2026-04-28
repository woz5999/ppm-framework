"""
fig_phi_aggregation.py — Φ-style aggregation: what it does, how, and why

Three-panel composition that explains aggregation operationally:

  Top-left:  GRADIENT-SAMPLE CLOUD at a representative θ point.
             Each dot is one noisy gradient measurement; the bullseye is
             the true (noise-free) gradient. Single samples scatter wide;
             the mean of N samples (large arrow) lands near the true
             value. This is the mechanism: averaging N samples reduces
             noise as 1/√N.

  Top-right: F-DESCENT trajectories side-by-side.
             Naive (N=1) thrashes — each step is a noise sample and the
             system never settles into a descent. Integrating (N=15)
             descends cleanly because each step is a √N-sharper estimate
             of the true gradient.

  Bottom:    1/√N NOISE-REDUCTION CURVE.
             Shows |averaged-gradient − true-gradient| as a function of N.
             The 1/√N theoretical envelope is the framework's own
             prediction; numerical samples sit on it.

Concept: Φ in the framework is the integrated-information capacity — a
measure of how many correlated firings a system can pool before acting.
Higher Φ = larger N. Aggregation is what Φ buys: the ability to extract a
gradient from individually-uninformative noisy events.

Run: python fig_phi_aggregation.py
"""

import sys
sys.path.insert(0, '../')

import math
import numpy as np
import matplotlib.pyplot as plt

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE

from ppm.dynamics import Basis, Density
from ppm.active_inference import (
    default_doublet_indices, free_energy_at_theta, gradient_F_theta,
    FrameFindingLoop,
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


def main():
    apply_style()

    basis = Basis(k_max=1)
    doublet = default_doublet_indices(basis)
    target_AB = math.pi / 3
    target_CD = math.pi / 6
    rho = _hidden_state_with_2d_structure(
        basis, doublet, target_AB, target_CD, mix=0.7)

    theta_init = (math.pi / 8, 3 * math.pi / 8)
    n_steps = 200
    eta = 0.05
    signal_noise = 2.0
    exec_noise = 0.02
    seed = 42

    print("Running naive agent (N=1)...")
    naive = FrameFindingLoop(
        rho, theta_init, basis, doublet,
        eta=eta, noise_sigma=exec_noise,
        signal_noise_sigma=signal_noise,
        N_aggregate=1, seed=seed)
    naive.run(n_steps=n_steps)

    print("Running integrating agent (N=15)...")
    integ = FrameFindingLoop(
        rho, theta_init, basis, doublet,
        eta=eta, noise_sigma=exec_noise,
        signal_noise_sigma=signal_noise,
        N_aggregate=15, seed=seed)
    integ.run(n_steps=n_steps)

    # ─── Generate gradient-sample cloud at a representative point ──────────
    # Pick a θ along the trajectory midway to the goal — the gradient there
    # has nonzero magnitude, so the noise vs true contrast is visible.
    sample_theta = (math.pi/4, math.pi/4)
    true_grad = gradient_F_theta(rho, basis, doublet,
                                  sample_theta[0], sample_theta[1], h=1e-4)
    # Build N=15 noisy samples (separate RNG so seed doesn't conflict)
    rng = np.random.default_rng(seed=99)
    N_samples = 15
    samples = np.array([
        true_grad + rng.normal(0.0, signal_noise, size=2)
        for _ in range(N_samples)
    ])
    sample_mean = samples.mean(axis=0)

    # 1/√N noise-reduction curve: average over many trials, plot |mean − true|
    Ns = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256])
    n_trials = 50
    rng2 = np.random.default_rng(seed=137)
    measured_errors = []
    for N in Ns:
        trial_errors = []
        for _ in range(n_trials):
            samples_N = true_grad + rng2.normal(0.0, signal_noise, size=(N, 2))
            mean_N = samples_N.mean(axis=0)
            trial_errors.append(float(np.linalg.norm(mean_N - true_grad)))
        measured_errors.append(np.mean(trial_errors))
    measured_errors = np.array(measured_errors)
    # Theoretical 1/√N envelope: noise-norm scales as σ * √(2/N) for 2-D
    theoretical = signal_noise * np.sqrt(2.0 / Ns)

    # ─── Build figure ───────────────────────────────────────────────────────
    fig = plt.figure(figsize=(13, 10), facecolor=BG)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.3, 1.0], hspace=0.40,
                           wspace=0.28)
    ax_cloud = fig.add_subplot(gs[0, 0])
    ax_F = fig.add_subplot(gs[0, 1])
    ax_sqrtN = fig.add_subplot(gs[1, :])

    for ax in [ax_cloud, ax_F, ax_sqrtN]:
        ax.set_facecolor(BG)
        ax.tick_params(colors=WHITE)
        ax.grid(True, alpha=0.3, color='#1a1a2e')

    # ─── Top-left: gradient-sample cloud ────────────────────────────────────
    # Each dot = one noisy gradient sample in (∂F/∂θ_AB, ∂F/∂θ_CD) space
    ax_cloud.scatter(samples[:, 0], samples[:, 1], s=70, c=ORANGE,
                      edgecolor=WHITE, linewidth=0.8, alpha=0.7,
                      label=fr'individual samples ($N={N_samples}$)')
    # Highlight one single sample for emphasis
    ax_cloud.scatter([samples[3, 0]], [samples[3, 1]], s=180, c=ORANGE,
                      edgecolor='#FFE066', linewidth=2.5, alpha=0.95,
                      label='single sample (any one)', zorder=11)
    # Mean of samples
    ax_cloud.scatter([sample_mean[0]], [sample_mean[1]], s=260, c=CYAN,
                      edgecolor=WHITE, linewidth=2,
                      label=fr'mean of $N={N_samples}$ samples',
                      zorder=12, marker='X')
    # True gradient
    ax_cloud.scatter([true_grad[0]], [true_grad[1]], s=320, c='#FFE066',
                      edgecolor=WHITE, linewidth=2,
                      label='true gradient', zorder=13, marker='*')
    # Crosshair at origin
    ax_cloud.axhline(y=0, color=GRAY, linestyle=':', linewidth=1, alpha=0.5)
    ax_cloud.axvline(x=0, color=GRAY, linestyle=':', linewidth=1, alpha=0.5)
    ax_cloud.set_xlabel(r'$\partial \mathcal{F} / \partial \theta_{AB}$',
                        color=WHITE, fontsize=11, weight='bold')
    ax_cloud.set_ylabel(r'$\partial \mathcal{F} / \partial \theta_{CD}$',
                        color=WHITE, fontsize=11, weight='bold')
    ax_cloud.set_title(r'WHAT aggregation does: '
                        r'$N$ noisy samples cluster around the true gradient',
                        color=WHITE, fontsize=11, weight='bold')
    ax_cloud.legend(loc='upper right', fontsize=8.5,
                     facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.92)

    # ─── Top-right: F-descent comparison ────────────────────────────────────
    ts_n = np.array([s['step'] for s in naive.trajectory])
    Fs_n = np.array([s['F'] for s in naive.trajectory])
    ts_i = np.array([s['step'] for s in integ.trajectory])
    Fs_i = np.array([s['F'] for s in integ.trajectory])
    ax_F.plot(ts_n, Fs_n, color=ORANGE, linewidth=2.0,
               label=r'naive ($N=1$): each step is one noise sample',
               alpha=0.9)
    ax_F.plot(ts_i, Fs_i, color=CYAN, linewidth=2.5,
               label=r'integrating ($N=15$): each step is averaged',
               alpha=0.95)
    ax_F.axhline(y=0, color=GRAY, linestyle=':', linewidth=1.2, alpha=0.6)
    ax_F.set_xlabel('descent step', color=WHITE, fontsize=11, weight='bold')
    ax_F.set_ylabel(r'$\mathcal{F}[\rho, \theta(t)]$',
                    color=WHITE, fontsize=11, weight='bold')
    ax_F.set_title(r'WHY it matters: '
                    r'aggregated agent descends; naive agent thrashes',
                    color=WHITE, fontsize=11, weight='bold')
    ax_F.legend(loc='upper right', fontsize=9,
                 facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.92)

    # ─── Bottom: 1/√N noise-reduction curve ─────────────────────────────────
    ax_sqrtN.plot(Ns, theoretical, color=GOLD, linewidth=2.5,
                   linestyle='--', alpha=0.85,
                   label=r'theoretical $1/\sqrt{N}$ envelope: $\sigma\sqrt{2/N}$')
    ax_sqrtN.plot(Ns, measured_errors, color=CYAN, linewidth=2,
                   marker='o', markersize=10, markerfacecolor=CYAN,
                   markeredgecolor=WHITE, markeredgewidth=1.2,
                   label='measured: average of 50 trials')
    ax_sqrtN.set_xscale('log', base=2)
    ax_sqrtN.set_yscale('log')
    ax_sqrtN.set_xlabel(r'aggregation count $N$  '
                        r'(samples averaged per step)',
                        color=WHITE, fontsize=11, weight='bold')
    ax_sqrtN.set_ylabel(r'gradient error $|\bar{\nabla}_N - \nabla_{\rm true}|$',
                        color=WHITE, fontsize=11, weight='bold')
    ax_sqrtN.set_title(r'HOW it works: noise reduces as $1/\sqrt{N}$ '
                        r'($\Phi$ is the framework''s name for this $N$)',
                        color=WHITE, fontsize=11, weight='bold')
    ax_sqrtN.legend(loc='upper right', fontsize=10,
                     facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.92)

    # Footer (no file/chapter references)
    fig.text(0.5, 0.012,
              r'Active inference at the framework''s noise boundary fails '
              r'because each gradient sample carries near-zero information. '
              r'Aggregating $N$ correlated samples per step recovers the '
              r'signal as $1/\sqrt{N}$. '
              r'$\Phi$ is the framework''s name for the integrated-information '
              r'capacity that determines how large $N$ a system can sustain.',
              ha='center', color=GRAY, fontsize=9, style='italic',
              wrap=True)

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    save(fig, 'fig_phi_aggregation.png')


if __name__ == '__main__':
    main()

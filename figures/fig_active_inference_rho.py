"""
fig_active_inference_rho.py — ρ occupation evolution under active inference

Stacked-area plot of the diagonal populations of ρ on the four doublet basis
vectors (|A⟩, |B⟩, |C⟩, |D⟩) over the active-inference trajectory.

Demonstrates that as θ descends, ρ shifts to a self-consistent mixture
matching the rotated A_b(θ) readout. Starting from pure |A⟩⟨A|, the system
develops weight on |B⟩ as θ_AB rotates and the basis adjusts, eventually
reaching a stable mixture corresponding to the (ρ, θ) fixed point.

Run: python fig_active_inference_rho.py
"""

import sys
sys.path.insert(0, '../')

import math
import numpy as np
import matplotlib.pyplot as plt

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE

from ppm.dynamics import Basis, Density
from ppm.active_inference import (
    default_doublet_indices, ActiveInferenceLoop,
)


def main():
    apply_style()

    basis = Basis(k_max=1)
    doublet = default_doublet_indices(basis)
    idx_A, idx_B, idx_C, idx_D = doublet
    psi = basis.basis_vector(idx_A)
    rho_0 = Density.pure(basis, psi)

    loop = ActiveInferenceLoop(
        rho_0, (math.pi/3, math.pi/3),
        basis, doublet,
        dt=0.05, eta=0.05, N_inner=20, gamma=0.5)
    loop.run(n_cycles=120)

    ts = np.array([s['t'] for s in loop.trajectory])
    rho_diag = np.array([
        np.real(np.diag(s['rho'].matrix))
        for s in loop.trajectory
    ])
    pop_A = rho_diag[:, idx_A]
    pop_B = rho_diag[:, idx_B]
    pop_C = rho_diag[:, idx_C]
    pop_D = rho_diag[:, idx_D]
    # Total weight of doublet subspace
    pop_other = 1.0 - (pop_A + pop_B + pop_C + pop_D)

    fig, (ax_pops, ax_theta) = plt.subplots(2, 1, figsize=(11, 8),
                                             facecolor=BG, sharex=True,
                                             gridspec_kw={'height_ratios': [2, 1]})
    for ax in [ax_pops, ax_theta]:
        ax.set_facecolor(BG)

    # ─── Top: stacked populations ────────────────────────────────────────────
    ax_pops.stackplot(
        ts, pop_A, pop_B, pop_C, pop_D, pop_other,
        labels=[r'$\rho_{AA}$  (Type A)', r'$\rho_{BB}$  (Type B)',
                r'$\rho_{CC}$  (Type C)', r'$\rho_{DD}$  (Type D)',
                'remainder'],
        colors=[GOLD, ORANGE, CYAN, VIOLET, GRAY],
        alpha=0.85,
    )
    ax_pops.set_ylabel('Diagonal populations',
                       fontsize=12, color=WHITE, weight='bold')
    ax_pops.set_title('Density Matrix Populations Under Active Inference',
                      fontsize=13, color=WHITE, weight='bold')
    ax_pops.legend(loc='center right', fontsize=10,
                   facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.85)
    ax_pops.set_ylim(0, 1)
    ax_pops.tick_params(colors=WHITE)
    ax_pops.grid(True, alpha=0.3, color='#1a1a2e')

    # ─── Bottom: θ trajectory over the same time axis ────────────────────────
    thetas_AB = np.array([s['theta_AB'] for s in loop.trajectory])
    thetas_CD = np.array([s['theta_CD'] for s in loop.trajectory])
    ax_theta.plot(ts, thetas_AB, color=GOLD, linewidth=2.0,
                  label=r'$\theta_{AB}$')
    ax_theta.plot(ts, thetas_CD, color=CYAN, linewidth=2.0,
                  label=r'$\theta_{CD}$')
    ax_theta.set_xlabel('Time (dimensionless units)',
                        fontsize=12, color=WHITE, weight='bold')
    ax_theta.set_ylabel(r'$\theta$  [rad]',
                        fontsize=12, color=WHITE, weight='bold')
    ax_theta.legend(loc='upper right', fontsize=10,
                    facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.85)
    ax_theta.set_yticks([0, math.pi/8, math.pi/4, 3*math.pi/8, math.pi/2])
    ax_theta.set_yticklabels(['$0$', r'$\pi/8$', r'$\pi/4$',
                               r'$3\pi/8$', r'$\pi/2$'])
    ax_theta.set_ylim(0, math.pi/2)
    ax_theta.tick_params(colors=WHITE)
    ax_theta.grid(True, alpha=0.3, color='#1a1a2e')

    plt.tight_layout()
    save(fig, 'fig_active_inference_rho.png')


if __name__ == '__main__':
    main()

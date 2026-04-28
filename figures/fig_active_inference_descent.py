"""
fig_active_inference_descent.py — F(t) descent under coupled ρ-θ dynamics

Plots the actualization free energy F[ρ, θ] over time as the active-inference
loop alternates inner Lindblad steps (ρ at fixed θ) and outer gradient steps
(θ at fixed ρ). Demonstrates that the coupled dynamics monotonically reduces
F until reaching a self-consistent fixed point.

Three trajectories shown, starting from the same pure |A⟩⟨A| state but
different initial θ values, illustrating that descent direction depends on
where the system starts on the F landscape.

Run: python fig_active_inference_descent.py
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
    idx_A = doublet[0]
    psi = basis.basis_vector(idx_A)
    rho_0 = Density.pure(basis, psi)

    # Three trajectories from different initial θ
    initial_thetas = [
        (math.pi/4, math.pi/4),
        (math.pi/3, math.pi/6),
        (1.0, 1.0),
    ]
    colors = [GOLD, CYAN, VIOLET]
    labels = [
        r'$\theta_0 = (\pi/4, \pi/4)$',
        r'$\theta_0 = (\pi/3, \pi/6)$',
        r'$\theta_0 = (1.0, 1.0)$',
    ]

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG)
    ax.set_facecolor(BG)

    for theta_init, color, label in zip(initial_thetas, colors, labels):
        loop = ActiveInferenceLoop(
            rho_0, theta_init, basis, doublet,
            dt=0.05, eta=0.05, N_inner=20, gamma=0.5)
        loop.run(n_cycles=120)
        ts = [s['t'] for s in loop.trajectory]
        Fs = [s['F'] for s in loop.trajectory]
        ax.plot(ts, Fs, color=color, linewidth=2.5, label=label, alpha=0.9)

    ax.set_xlabel('Time (dimensionless units)',
                  fontsize=12, color=WHITE, weight='bold')
    ax.set_ylabel(r'Actualization Free Energy $\mathcal{F}[\rho, \theta]$',
                  fontsize=12, color=WHITE, weight='bold')
    ax.set_title('Active Inference: Coupled $\\rho$-$\\theta$ Descent of $\\mathcal{F}$',
                 fontsize=13, color=WHITE, weight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3, color='#1a1a2e')
    ax.tick_params(colors=WHITE)

    # Annotate the "self-consistent fixed point" region
    ax.axhline(y=0, color=GRAY, linestyle=':', linewidth=1, alpha=0.5)
    ax.text(0.02, 0.05, r'$\mathcal{F} = -\log P$ where '
                       r'$P = \mathrm{Tr}[A_b(\theta)\,\rho\,A_b(\theta)^\dagger]$',
            transform=ax.transAxes, color=GRAY, fontsize=9, style='italic',
            verticalalignment='bottom')

    plt.tight_layout()
    save(fig, 'fig_active_inference_descent.png')


if __name__ == '__main__':
    main()

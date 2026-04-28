"""
fig_variational_lyapunov_descent.py — F descent over the full actualization cycle

The actualization free energy F = -log(max_b P_b) is a Lyapunov functional for
the FULL actualization cycle: continuous Lindblad evolution between firings PLUS
stochastic POVM firings ρ → A_b ρ A_b†/P_b drawn under the Born rule. Pure
Lindblad alone with the framework's Hermitian rank-1 projector convention does
NOT change Tr(A_b ρ A_b†) (the dissipator commutes with A_b†A_b for projector
A_b); F descent emerges only when stochastic firings collapse ρ into A_b
eigenstates and unitary mixing redistributes between firings.

Plots: 32 Monte Carlo trajectories of F(t) over the cycle, plus their
ensemble mean. Initial state is pure τ-odd (worst case: F starts at +∞);
each trajectory drops to F ≈ 0 after a few firings; the ensemble mean
descends monotonically.

Run: python fig_variational_lyapunov_descent.py
"""

import sys
sys.path.insert(0, '../')

import math
import numpy as np
import matplotlib.pyplot as plt

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE

from ppm.dynamics import (
    Basis, Density, Operator,
    boundary_operator,
    lindblad_step, free_energy, yield_distribution,
)


def run_one_cycle(basis, H, A_ops, gamma, T, dt, rho_0, rng):
    """One Monte Carlo trajectory. Returns (times, F_traj)."""
    n = int(T / dt)
    rho = rho_0
    times = [0.0]
    F_max_init = free_energy(rho, A_ops, 'max')
    F0 = F_max_init if F_max_init < float('inf') else 5.5
    F_traj = [F0]

    for step in range(1, n + 1):
        # Continuous Lindblad step
        rho = lindblad_step(rho, H, A_ops, [gamma] * len(A_ops), dt)
        # Stochastic POVM firings (Born rule)
        yields = yield_distribution(rho, A_ops)
        for b, A in enumerate(A_ops):
            p_fire = gamma * yields[b] * dt
            if rng.random() < p_fire:
                # Project: ρ → A ρ A†/p
                new = A.matrix @ rho.matrix @ A.matrix.conj().T
                trace_new = float(np.real(np.trace(new)))
                if trace_new > 1e-15:
                    new = new / trace_new
                    rho = Density(basis, new)
                break  # at most one firing per dt
        times.append(step * dt)
        F_now = free_energy(rho, A_ops, 'max')
        F_traj.append(F_now if F_now < float('inf') else 5.5)

    return np.array(times), np.array(F_traj)


def main():
    apply_style()

    basis = Basis(k_max=1)
    A_ops = [boundary_operator(basis, i) for i in range(basis.dim_plus)]

    # Random Hermitian mixing Hamiltonian (couples τ-even and τ-odd content
    # so the system can flow into A_b-aligned states between firings).
    rng_H = np.random.default_rng(7)
    M = (rng_H.standard_normal((basis.total_dim, basis.total_dim))
         + 1j * rng_H.standard_normal((basis.total_dim, basis.total_dim)))
    H = Operator(basis, (M + M.conj().T) / 2 * 0.5)

    # Worst-case initial: pure τ-odd state (F = +∞ until parity flips)
    odd_idx = [i for i in range(basis.total_dim)
               if basis.tau_parity[i] == -1]
    psi = np.zeros(basis.total_dim, dtype=complex)
    psi[odd_idx[0]] = 1.0
    rho_0 = Density.pure(basis, psi)

    # Cycle parameters
    T = 4.0
    dt = 0.01
    gamma = 1.0

    # Run ensemble
    n_trajectories = 40
    rng_mc = np.random.default_rng(42)
    F_ensemble = []
    times_ref = None
    for _ in range(n_trajectories):
        t_arr, F_arr = run_one_cycle(basis, H, A_ops, gamma, T, dt,
                                      rho_0, rng_mc)
        if times_ref is None:
            times_ref = t_arr
        F_ensemble.append(F_arr)
    F_ensemble = np.array(F_ensemble)
    F_mean = F_ensemble.mean(axis=0)

    # ─── Figure ─────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 6), facecolor=BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=WHITE)
    ax.grid(True, alpha=0.3, color='#1a1a2e')

    # Individual trajectories — first one labeled for legend, rest faint.
    ax.plot(times_ref, F_ensemble[0], color=VIOLET, linewidth=0.7,
             alpha=0.45,
             label='individual Monte Carlo trajectory ($n=40$)')
    for traj in F_ensemble[1:]:
        ax.plot(times_ref, traj, color=VIOLET, linewidth=0.7, alpha=0.18)

    # Ensemble mean (thick gold)
    ax.plot(times_ref, F_mean, color=GOLD, linewidth=3.2,
             label='ensemble mean', zorder=10)

    # F = 0 floor
    ax.axhline(y=0.0, color=CYAN, linestyle=':', linewidth=1.6, alpha=0.8,
                label=r'$\mathcal{F} = 0$ (eigenstate of $\hat{A}_b^\dagger\hat{A}_b$)')

    ax.set_xlabel(r'time  $t$  (units of $1/\gamma$)',
                  color=WHITE, fontsize=12, weight='bold')
    ax.set_ylabel(r'actualization free energy  $\mathcal{F}(t)$',
                  color=WHITE, fontsize=12, weight='bold')
    ax.set_xlim(0, T)
    ax.set_ylim(0, 6.0)
    ax.legend(loc='upper right', fontsize=10,
              facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.92)

    plt.tight_layout()
    save(fig, 'fig_variational_lyapunov_descent.png')


if __name__ == '__main__':
    main()

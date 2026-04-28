"""
fig_two_boundary_coordination.py — Emergent coordination from shared environment

Two PPM boundaries B1, B2, each running active inference (inner ρ-Lindblad +
outer θ-gradient). The boundaries couple through a shared-environment Lindblad
(post-Born-Markov form: cross-correlated jump operator L = L_1 + L_2 with
weight α; local independent jumps with weight 1−α).

Three-panel layout:
  Top-left:  θ trajectories at α = 0 (no shared env).  Independent dynamics.
  Top-right: θ trajectories at α = 0.85 (strongly shared env).  Coordinated.
  Bottom:    Order parameter ⟨|θ^(1)_AB − θ^(2)_AB|⟩_final swept across α.

Because the joint H_S1 ⊗ H_S2 dynamics is computationally heavy (256-dim with
RK4 Lindblad), the simulation work is split into precompute + render phases.
Trajectories are cached to .npz files in computed/. If cache exists, render
from cache directly.

Usage:
    python fig_two_boundary_coordination.py precompute_showcase
    python fig_two_boundary_coordination.py precompute_sweep_lo
    python fig_two_boundary_coordination.py precompute_sweep_hi
    python fig_two_boundary_coordination.py render

    Or:  python fig_two_boundary_coordination.py all
    (runs everything in sequence — may be slow)
"""

import sys
sys.path.insert(0, '../')

import os
import math
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE

from ppm.dynamics import Basis, Density
from ppm.active_inference import (
    TensorProductBasis, default_doublet_indices,
    TwoBoundaryActiveInferenceLoop,
)


# ─── Simulation params (tuned for sandbox 40s budget per chunk) ─────────────

THETA_1_INIT = (math.pi/3, 0.4)
THETA_2_INIT = (math.pi/6, 1.2)
SHOWCASE_N_CYCLES = 30
SHOWCASE_N_INNER = 8
SWEEP_N_CYCLES = 20
SWEEP_N_INNER = 5
GAMMA = 0.5
DT = 0.05
ETA = 0.05

CACHE_DIR = 'computed'
SHOWCASE_FILE = os.path.join(CACHE_DIR, 'two_boundary_showcase.npz')
SWEEP_LO_FILE = os.path.join(CACHE_DIR, 'two_boundary_sweep_lo.npz')
SWEEP_HI_FILE = os.path.join(CACHE_DIR, 'two_boundary_sweep_hi.npz')
SWEEP_ALPHAS_LO = [0.0, 0.15, 0.3, 0.45]
SWEEP_ALPHAS_HI = [0.6, 0.75, 0.9, 1.0]


def _setup():
    basis_S1 = Basis(k_max=1)
    basis_S2 = Basis(k_max=1)
    doublet_S1 = default_doublet_indices(basis_S1)
    doublet_S2 = default_doublet_indices(basis_S2)
    return basis_S1, basis_S2, doublet_S1, doublet_S2


def _initial_density(basis_S1, basis_S2, doublet_S1, doublet_S2):
    joint = TensorProductBasis(basis_S1, basis_S2)
    psi_1 = basis_S1.basis_vector(doublet_S1[0])
    psi_2 = basis_S2.basis_vector(doublet_S2[0])
    psi_joint = joint.product_state(psi_1, psi_2)
    return Density.pure(joint, psi_joint)


def _run(theta_1, theta_2, alpha, n_cycles, n_inner):
    basis_S1, basis_S2, doublet_S1, doublet_S2 = _setup()
    rho_0 = _initial_density(basis_S1, basis_S2, doublet_S1, doublet_S2)
    loop = TwoBoundaryActiveInferenceLoop(
        rho_0, theta_1, theta_2, basis_S1, basis_S2,
        doublet_S1, doublet_S2,
        alpha=alpha, dt=DT, eta=ETA, N_inner=n_inner, gamma=GAMMA)
    loop.run(n_cycles=n_cycles)
    return loop.trajectory


def _trajectory_to_arrays(traj):
    return {
        't':         np.array([s['t'] for s in traj]),
        'theta_1_AB': np.array([s['theta_1_AB'] for s in traj]),
        'theta_1_CD': np.array([s['theta_1_CD'] for s in traj]),
        'theta_2_AB': np.array([s['theta_2_AB'] for s in traj]),
        'theta_2_CD': np.array([s['theta_2_CD'] for s in traj]),
        'F_1':       np.array([s['F_1'] for s in traj]),
        'F_2':       np.array([s['F_2'] for s in traj]),
    }


def precompute_showcase():
    os.makedirs(CACHE_DIR, exist_ok=True)
    print('Showcase α=0.0...')
    t0 = time.time()
    traj_indep = _run(THETA_1_INIT, THETA_2_INIT, 0.0,
                       SHOWCASE_N_CYCLES, SHOWCASE_N_INNER)
    print(f'  {time.time()-t0:.1f}s')
    print('Showcase α=0.85...')
    t0 = time.time()
    traj_coupled = _run(THETA_1_INIT, THETA_2_INIT, 0.85,
                         SHOWCASE_N_CYCLES, SHOWCASE_N_INNER)
    print(f'  {time.time()-t0:.1f}s')
    A = _trajectory_to_arrays(traj_indep)
    B = _trajectory_to_arrays(traj_coupled)
    np.savez(SHOWCASE_FILE,
             indep_t=A['t'],
             indep_theta_1_AB=A['theta_1_AB'],
             indep_theta_2_AB=A['theta_2_AB'],
             coupled_t=B['t'],
             coupled_theta_1_AB=B['theta_1_AB'],
             coupled_theta_2_AB=B['theta_2_AB'])
    print(f'Saved {SHOWCASE_FILE}')


def _von_neumann_entropy(rho_matrix):
    """S(ρ) = -Tr(ρ ln ρ). Returns 0 for pure states, ln(D) for max-mixed."""
    herm = 0.5 * (rho_matrix + rho_matrix.conj().T)
    eigs = np.linalg.eigvalsh(herm)
    eigs = eigs[eigs > 1e-15]
    return float(-np.sum(eigs * np.log(eigs)))


def _mutual_information_S1_S2(traj_snap, basis_S1, basis_S2):
    """
    MI(ρ_1; ρ_2) = S(ρ_1) + S(ρ_2) − S(ρ_12).

    At α=0 the joint state stays a product if it started as one, so MI = 0.
    Under coupling, the joint state develops correlations and MI > 0.

    This is the unambiguous quantitative measure of cross-boundary correlation.
    """
    rho_1 = traj_snap['rho_1'].matrix
    rho_2 = traj_snap['rho_2'].matrix
    rho_12 = traj_snap['rho_joint'].matrix
    S1 = _von_neumann_entropy(rho_1)
    S2 = _von_neumann_entropy(rho_2)
    S12 = _von_neumann_entropy(rho_12)
    return S1 + S2 - S12


def _sweep_chunk(alphas, out_file):
    os.makedirs(CACHE_DIR, exist_ok=True)
    order_param = []
    mutual_info = []
    basis_S1, basis_S2, _, _ = _setup()
    for alpha in alphas:
        t0 = time.time()
        traj = _run(THETA_1_INIT, THETA_2_INIT, float(alpha),
                     SWEEP_N_CYCLES, SWEEP_N_INNER)
        last = traj[-min(10, len(traj)):]
        d = float(np.mean([abs(s['theta_1_AB'] - s['theta_2_AB'])
                            for s in last]))
        order_param.append(d)
        # Mutual information at the final snapshot
        mi = _mutual_information_S1_S2(traj[-1], basis_S1, basis_S2)
        mutual_info.append(mi)
        print(f'  α={alpha:.2f}: ⟨|Δθ_AB|⟩={d:.3f}  MI={mi:.4f}  '
              f'({time.time()-t0:.1f}s)')
    np.savez(out_file,
             alphas=np.array(alphas),
             order_param=np.array(order_param),
             mutual_info=np.array(mutual_info))
    print(f'Saved {out_file}')


def precompute_sweep_lo():
    print(f'Sweep low α: {SWEEP_ALPHAS_LO}')
    _sweep_chunk(SWEEP_ALPHAS_LO, SWEEP_LO_FILE)


def precompute_sweep_hi():
    print(f'Sweep high α: {SWEEP_ALPHAS_HI}')
    _sweep_chunk(SWEEP_ALPHAS_HI, SWEEP_HI_FILE)


def render():
    apply_style()
    if not all(os.path.exists(p) for p in
               [SHOWCASE_FILE, SWEEP_LO_FILE, SWEEP_HI_FILE]):
        missing = [p for p in [SHOWCASE_FILE, SWEEP_LO_FILE, SWEEP_HI_FILE]
                    if not os.path.exists(p)]
        raise FileNotFoundError(
            f'Missing cache files: {missing}. '
            f'Run precompute_* first.')

    show = np.load(SHOWCASE_FILE)
    sweep_lo = np.load(SWEEP_LO_FILE)
    sweep_hi = np.load(SWEEP_HI_FILE)
    alphas = np.concatenate([sweep_lo['alphas'], sweep_hi['alphas']])
    order_param = np.concatenate([sweep_lo['order_param'],
                                   sweep_hi['order_param']])
    mutual_info = np.concatenate([sweep_lo['mutual_info'],
                                   sweep_hi['mutual_info']])
    # Sort by alpha
    sort_idx = np.argsort(alphas)
    alphas = alphas[sort_idx]
    order_param = order_param[sort_idx]
    mutual_info = mutual_info[sort_idx]

    fig = plt.figure(figsize=(14, 9), facecolor=BG)
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.1], hspace=0.35,
                           wspace=0.25)
    ax_indep = fig.add_subplot(gs[0, 0])
    ax_coupled = fig.add_subplot(gs[0, 1])
    ax_order = fig.add_subplot(gs[1, :])
    for ax in [ax_indep, ax_coupled, ax_order]:
        ax.set_facecolor(BG)
        ax.tick_params(colors=WHITE)
        ax.grid(True, alpha=0.3, color='#1a1a2e')

    # Top-left: independent
    ax_indep.plot(show['indep_t'], show['indep_theta_1_AB'],
                   color=GOLD, linewidth=2.5, label=r'$\theta^{(1)}_{AB}$')
    ax_indep.plot(show['indep_t'], show['indep_theta_2_AB'],
                   color=CYAN, linewidth=2.5, label=r'$\theta^{(2)}_{AB}$')
    ax_indep.set_title(r'$\alpha = 0$: independent dynamics',
                        color=WHITE, fontsize=12, weight='bold')
    ax_indep.set_xlabel('time', color=WHITE, fontsize=11)
    ax_indep.set_ylabel(r'$\theta_{AB}$  [rad]', color=WHITE, fontsize=11)
    ax_indep.set_yticks([0, math.pi/8, math.pi/4, 3*math.pi/8, math.pi/2])
    ax_indep.set_yticklabels(['$0$', r'$\pi/8$', r'$\pi/4$',
                               r'$3\pi/8$', r'$\pi/2$'])
    ax_indep.set_ylim(0, math.pi/2)
    ax_indep.legend(loc='upper right', fontsize=10,
                     facecolor='#0a0a1a', edgecolor=WHITE)

    # Top-right: coupled
    ax_coupled.plot(show['coupled_t'], show['coupled_theta_1_AB'],
                     color=GOLD, linewidth=2.5, label=r'$\theta^{(1)}_{AB}$')
    ax_coupled.plot(show['coupled_t'], show['coupled_theta_2_AB'],
                     color=CYAN, linewidth=2.5, label=r'$\theta^{(2)}_{AB}$')
    ax_coupled.set_title(r'$\alpha = 0.85$: shared environment couples them',
                          color=WHITE, fontsize=12, weight='bold')
    ax_coupled.set_xlabel('time', color=WHITE, fontsize=11)
    ax_coupled.set_ylabel(r'$\theta_{AB}$  [rad]', color=WHITE, fontsize=11)
    ax_coupled.set_yticks([0, math.pi/8, math.pi/4, 3*math.pi/8, math.pi/2])
    ax_coupled.set_yticklabels(['$0$', r'$\pi/8$', r'$\pi/4$',
                                 r'$3\pi/8$', r'$\pi/2$'])
    ax_coupled.set_ylim(0, math.pi/2)
    ax_coupled.legend(loc='upper right', fontsize=10,
                       facecolor='#0a0a1a', edgecolor=WHITE)

    # Bottom: mutual information vs α (the unambiguous coordination metric)
    ax_order.plot(alphas, mutual_info, color=VIOLET, linewidth=3,
                   marker='o', markersize=10, markerfacecolor=GOLD,
                   markeredgecolor=WHITE, markeredgewidth=1.5)
    ax_order.fill_between(alphas, 0, mutual_info, alpha=0.2, color=VIOLET)
    ax_order.set_xlabel(r'shared-environment coupling $\alpha$',
                         color=WHITE, fontsize=12, weight='bold')
    ax_order.set_ylabel(r'mutual information $I(\rho_1; \rho_2)$  [nats]',
                         color=WHITE, fontsize=12, weight='bold')
    ax_order.set_title('Emergent Coordination: Cross-Boundary Mutual Information vs. Coupling',
                        color=WHITE, fontsize=13, weight='bold')
    ax_order.set_xlim(0, 1)
    mi_max = float(mutual_info.max())
    ax_order.set_ylim(0, mi_max * 1.20 if mi_max > 0 else 0.1)

    ax_order.axvspan(0, 0.3, alpha=0.08, color=GOLD)
    ax_order.text(0.15, mi_max * 1.10, 'independent (MI = 0)',
                   color=GOLD, fontsize=10, ha='center', weight='bold',
                   style='italic')
    ax_order.axvspan(0.6, 1.0, alpha=0.08, color=CYAN)
    ax_order.text(0.8, mi_max * 1.10, 'correlated (MI > 0)',
                   color=CYAN, fontsize=10, ha='center', weight='bold',
                   style='italic')

    fig.suptitle('Active-Inference Coordination from Shared-Environment Lindblad Coupling',
                  color=WHITE, fontsize=14, weight='bold', y=0.99)
    fig.text(0.5, 0.005,
              r'Two boundaries each run inner $\rho$-Lindblad and outer $\theta$-gradient '
              r'on $\mathcal{F}[\rho, \theta]$. '
              r'Coupling $\alpha$ weights joint-detection dissipator '
              r'$L_{\rm cross} = A_{b_1} \otimes A_{b_2}$ relative to local channels.',
              ha='center', va='bottom', color=GRAY, fontsize=9, style='italic')

    plt.tight_layout(rect=[0, 0.02, 1, 0.97])
    save(fig, 'fig_two_boundary_coordination.png')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=[
        'precompute_showcase', 'precompute_sweep_lo',
        'precompute_sweep_hi', 'render', 'all'])
    args = parser.parse_args()
    if args.mode == 'precompute_showcase':
        precompute_showcase()
    elif args.mode == 'precompute_sweep_lo':
        precompute_sweep_lo()
    elif args.mode == 'precompute_sweep_hi':
        precompute_sweep_hi()
    elif args.mode == 'render':
        render()
    elif args.mode == 'all':
        precompute_showcase()
        precompute_sweep_lo()
        precompute_sweep_hi()
        render()


if __name__ == '__main__':
    main()

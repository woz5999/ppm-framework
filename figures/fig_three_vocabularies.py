"""
fig_three_vocabularies.py — same θ-trajectory under three mathematical lenses

Runs one ActiveInferenceLoop trajectory and plots the resulting (θ_AB(t),
θ_CD(t)) curve three ways, illustrating the §Three Vocabularies claim that
the same dynamical step admits an information-theoretic, thermodynamic,
and projective reading.

Panel 1 — Information-theoretic.
    The complementarity budget I(k) is partitioned by θ across the four
    fact types: (A spectral, B spatial) by θ_AB, (C chiral, D intensity)
    by θ_CD. Plot fractional allocations cos²θ_AB(t), sin²θ_AB(t),
    cos²θ_CD(t), sin²θ_CD(t) over time. The trajectory is a continuous
    reallocation of the budget.

Panel 2 — Thermodynamic.
    F_eff(θ) over T² = [0, π/2]² as a contour landscape (computed at
    the initial ρ as a fixed reference). The trajectory's actual
    (θ_AB(t), θ_CD(t)) path is drawn on top, colored by time.

Panel 3 — Projective.
    The trajectory rendered on a 3D torus surface (T² in three-quarter
    perspective). Same (θ_AB, θ_CD) curve as Panel 2; the torus is the
    measurement-frame space PGL(4,R) acts on. Curve colored by time
    using the same colormap as Panel 2.

Run: python fig_three_vocabularies.py
"""

import sys
sys.path.insert(0, '../')

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE

from ppm.dynamics import Basis, Density
from ppm.active_inference import (
    default_doublet_indices, ActiveInferenceLoop, free_energy_at_theta,
)


def main():
    apply_style()

    # ─── Set up the boundary state and run a single AI trajectory ──────────
    # Use an asymmetric superposition over all four fact types so the F
    # landscape has gradient in BOTH θ directions (a |A><A| pure state has
    # no θ_CD dependence and gives a flat-CD landscape — boring).
    basis = Basis(k_max=1)
    doublet = default_doublet_indices(basis)
    psi = np.zeros(basis.total_dim, dtype=complex)
    psi[doublet[0]] = 1.0   # Type A weight
    psi[doublet[1]] = 0.55  # Type B weight
    psi[doublet[2]] = 0.75  # Type C weight
    psi[doublet[3]] = 0.4   # Type D weight
    psi = psi / np.linalg.norm(psi)
    rho_0 = Density.pure(basis, psi)

    # Pick a starting θ in a high-F corner so the trajectory has visible
    # descent in both directions.
    theta_init = (1.3, 0.35)

    loop = ActiveInferenceLoop(
        rho_0, theta_init, basis, doublet,
        dt=0.05, eta=0.12, N_inner=10, gamma=0.5,
    )
    loop.run(n_cycles=80)
    traj = loop.trajectory

    ts = np.array([s['t'] for s in traj])
    theta_AB = np.array([s['theta_AB'] for s in traj])
    theta_CD = np.array([s['theta_CD'] for s in traj])
    F_along_traj = np.array([s['F'] for s in traj])

    # ─── Compute the F-landscape over T² at the initial ρ for reference ────
    n_grid = 60
    AB_grid = np.linspace(1e-3, math.pi / 2 - 1e-3, n_grid)
    CD_grid = np.linspace(1e-3, math.pi / 2 - 1e-3, n_grid)
    F_grid = np.zeros((n_grid, n_grid))
    for i, ab in enumerate(AB_grid):
        for j, cd in enumerate(CD_grid):
            F_grid[i, j] = free_energy_at_theta(
                rho_0, basis, doublet, ab, cd
            )
    # Clip extreme values for cleaner contours
    F_grid = np.clip(F_grid, 0, np.percentile(F_grid, 95))

    # ─── Figure ────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(16, 5.5), facecolor=BG)

    # Panel layout: 1 row, 3 columns; panel 3 is a 3D axes
    ax_info = fig.add_subplot(1, 3, 1, facecolor=BG)
    ax_thermo = fig.add_subplot(1, 3, 2, facecolor=BG)
    ax_proj = fig.add_subplot(1, 3, 3, projection='3d', facecolor=BG)

    # ━━━ Panel 1 — Information-theoretic capacity partition ━━━━━━━━━━━━━━━━
    # Kähler doublet split (A spectral vs B spatial) by θ_AB
    # Gauge doublet split (C chiral vs D intensity) by θ_CD
    A_frac = np.cos(theta_AB) ** 2
    B_frac = np.sin(theta_AB) ** 2
    C_frac = np.cos(theta_CD) ** 2
    D_frac = np.sin(theta_CD) ** 2

    ax_info.fill_between(ts, 0, A_frac, color=GOLD, alpha=0.85,
                          label='Type A (spectral)')
    ax_info.fill_between(ts, A_frac, 1.0, color=ORANGE, alpha=0.5,
                          label='Type B (spatial)')
    ax_info.plot(ts, A_frac, color=WHITE, linewidth=1.0, alpha=0.6)

    ax_info.fill_between(ts, -C_frac, 0, color=CYAN, alpha=0.85,
                          label='Type C (chiral)')
    ax_info.fill_between(ts, -1.0, -C_frac, color=VIOLET, alpha=0.5,
                          label='Type D (intensity)')
    ax_info.plot(ts, -C_frac, color=WHITE, linewidth=1.0, alpha=0.6)

    ax_info.axhline(y=0, color=WHITE, linewidth=1.5, alpha=0.7)
    ax_info.set_xlim(ts[0], ts[-1])
    ax_info.set_ylim(-1.05, 1.05)
    ax_info.set_xlabel('time', fontsize=11, color=WHITE, weight='bold')
    ax_info.set_ylabel(
        r'capacity allocation  '
        r'$\leftarrow$ gauge doublet $\;|\;$ Kähler doublet $\rightarrow$',
        fontsize=10, color=WHITE)
    ax_info.set_title('1. Information-theoretic\n'
                       'budget partition across fact types',
                       fontsize=11.5, color=WHITE, weight='bold')
    ax_info.tick_params(colors=WHITE)
    ax_info.grid(True, alpha=0.2, color='#1a1a2e')
    ax_info.legend(loc='center right', fontsize=8,
                    facecolor='#0a0a1a', edgecolor=GRAY, framealpha=0.92,
                    labelcolor=WHITE)

    # ━━━ Panel 2 — Thermodynamic F-landscape with trajectory ━━━━━━━━━━━━━━
    AB_mesh, CD_mesh = np.meshgrid(AB_grid, CD_grid, indexing='ij')
    contour = ax_thermo.contourf(
        AB_mesh, CD_mesh, F_grid,
        levels=20, cmap='magma', alpha=0.85,
    )
    cbar = plt.colorbar(contour, ax=ax_thermo, fraction=0.046, pad=0.04)
    cbar.set_label(r'$\mathcal{F}_{\rm eff}$',
                    fontsize=11, color=WHITE, weight='bold')
    cbar.ax.tick_params(colors=WHITE)
    cbar.outline.set_edgecolor(WHITE)

    # Trajectory drawn as a colored line (color = time)
    points = np.array([theta_AB, theta_CD]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    norm = plt.Normalize(ts.min(), ts.max())
    lc = LineCollection(segments, cmap='cool', norm=norm,
                         linewidth=2.5, alpha=0.95)
    lc.set_array(ts[:-1])
    ax_thermo.add_collection(lc)

    # Mark start and end
    ax_thermo.scatter([theta_AB[0]], [theta_CD[0]], s=80,
                       c=CYAN, edgecolors=WHITE, linewidths=1.5,
                       zorder=10, label='start')
    ax_thermo.scatter([theta_AB[-1]], [theta_CD[-1]], s=120,
                       c=GOLD, edgecolors=WHITE, linewidths=1.5,
                       marker='*', zorder=11, label='fixed point')

    ax_thermo.set_xlim(0, math.pi / 2)
    ax_thermo.set_ylim(0, math.pi / 2)
    ax_thermo.set_xticks([0, math.pi / 4, math.pi / 2])
    ax_thermo.set_xticklabels(['0', r'$\pi/4$', r'$\pi/2$'])
    ax_thermo.set_yticks([0, math.pi / 4, math.pi / 2])
    ax_thermo.set_yticklabels(['0', r'$\pi/4$', r'$\pi/2$'])
    ax_thermo.set_xlabel(r'$\theta_{AB}$', fontsize=12,
                          color=WHITE, weight='bold')
    ax_thermo.set_ylabel(r'$\theta_{CD}$', fontsize=12,
                          color=WHITE, weight='bold')
    ax_thermo.set_title('2. Thermodynamic\n'
                         r'free-energy descent on $T^2$',
                         fontsize=11.5, color=WHITE, weight='bold')
    ax_thermo.tick_params(colors=WHITE)
    ax_thermo.set_aspect('equal')
    ax_thermo.legend(loc='upper right', fontsize=8,
                      facecolor='#0a0a1a', edgecolor=GRAY, framealpha=0.92,
                      labelcolor=WHITE)

    # ━━━ Panel 3 — Projective: trajectory on T² torus surface ━━━━━━━━━━━━━
    # Map [0, π/2] → [0, 2π] for full torus wrapping.
    R_major = 2.0
    r_minor = 0.7
    n_torus = 50
    u = np.linspace(0, 2 * np.pi, n_torus)
    v = np.linspace(0, 2 * np.pi, n_torus)
    U, V = np.meshgrid(u, v, indexing='ij')
    Xs = (R_major + r_minor * np.cos(V)) * np.cos(U)
    Ys = (R_major + r_minor * np.cos(V)) * np.sin(U)
    Zs = r_minor * np.sin(V)

    ax_proj.plot_surface(Xs, Ys, Zs, color=VIOLET, alpha=0.18,
                          edgecolor=CYAN, linewidth=0.15)

    # Trajectory: same θ values, mapped to torus surface (slightly inflated
    # so the curve sits visibly above the surface).
    u_traj = 4 * theta_AB        # [0, π/2] → [0, 2π]
    v_traj = 4 * theta_CD
    inflate = 1.05
    Xt = (R_major + inflate * r_minor * np.cos(v_traj)) * np.cos(u_traj)
    Yt = (R_major + inflate * r_minor * np.cos(v_traj)) * np.sin(u_traj)
    Zt = inflate * r_minor * np.sin(v_traj)

    pts3 = np.array([Xt, Yt, Zt]).T.reshape(-1, 1, 3)
    segs3 = np.concatenate([pts3[:-1], pts3[1:]], axis=1)
    lc3 = Line3DCollection(segs3, cmap='cool', norm=norm,
                            linewidth=3.0, alpha=0.95)
    lc3.set_array(ts[:-1])
    ax_proj.add_collection3d(lc3)

    ax_proj.scatter([Xt[0]], [Yt[0]], [Zt[0]], s=80,
                     c=CYAN, edgecolors=WHITE, linewidths=1.5)
    ax_proj.scatter([Xt[-1]], [Yt[-1]], [Zt[-1]], s=140,
                     c=GOLD, edgecolors=WHITE, linewidths=1.5, marker='*')

    # Clean up the 3D axes
    ax_proj.set_box_aspect([1, 1, 0.5])
    ax_proj.view_init(elev=28, azim=-55)
    ax_proj.set_xticks([])
    ax_proj.set_yticks([])
    ax_proj.set_zticks([])
    # Hide the panes / grid for a cleaner look
    for axis in (ax_proj.xaxis, ax_proj.yaxis, ax_proj.zaxis):
        axis.pane.set_visible(False)
        axis.line.set_color((0, 0, 0, 0))
    ax_proj.grid(False)
    ax_proj.set_title('3. Projective\n'
                       r'trajectory on $T^2$ '
                       '(PGL(4,$\\mathbb{R}$) frame space)',
                       fontsize=11.5, color=WHITE, weight='bold')

    # ─── Footer ────────────────────────────────────────────────────────────
    fig.suptitle(
        'Three vocabularies of one active-inference step',
        fontsize=14, color=WHITE, weight='bold', y=0.99,
    )
    fig.text(
        0.5, 0.01,
        r'Same $(\theta_{AB}(t), \theta_{CD}(t))$ trajectory in all three '
        r'panels.  The cycle is a single dynamical step on the measurement '
        r'torus; information theory, thermodynamics, and projective '
        r'geometry are three readings of that step.',
        ha='center', color=GRAY, fontsize=9, style='italic',
    )

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    save(fig, 'fig_three_vocabularies.png')


if __name__ == '__main__':
    main()

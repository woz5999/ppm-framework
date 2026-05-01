"""
fig_rp3_landscape.py — local surprisal landscape near a single point of RP³.

Companion to fig_rp3_saddle.py.  This figure visualizes the framework's
actual surprisal:

    F(ρ) = -log( Tr[ρ τρτ] / Tr[ρ²] )

For pure states on the Bloch sphere (CP¹) with τ acting as complex
conjugation (so r_y → -r_y), this evaluates to

    F(r) = -log(1 - r_y²)

extended here to a 2D imaginary-content slice (y₁, y₂):

    F(y) = -log(1 - |y|²)

F has a TRUE MINIMUM at |y| = 0 (the τ-even / RP³ surface) — i.e., the
actualization basis selects RP³ as the lowest-surprisal configuration.
The walls of the bowl rise as imaginary content grows; F → ∞ as |y| → 1.

The structural contention this figure depicts:
  - Surprisal F says RP³ is STABLE (a min, not a saddle).
  - The Kähler flow is symplectic, NOT gradient flow on F.  It does
    work AGAINST ∇F, pumping the state UP the bowl walls into higher
    surprisal regions.
  - The actualization cycle is the system oscillating between F's
    "stay at the bottom" verdict and the Kähler flow's "climb the
    walls" verdict.

Color semantics (framework convention):
  - Orange near the bowl bottom → τ-even (RP³, surprisal minimum)
  - Violet near the rim          → τ-odd content (high surprisal)
  - Cyan dot at the bottom       → actualization event placing state at RP³
  - Violet arrows up the walls    → Kähler-flow direction (against ∇F)
  - Cyan→violet spiral trajectory → the state climbing the walls
  - Larger ball mid-spiral        → state mid-ascent ("ball rolling up")

Run: python fig_rp3_landscape.py
"""

import sys
sys.path.insert(0, '../')

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE


def plot_gradient_line_3d(ax, points, c_start, c_end, linewidth=2.6,
                          alpha=0.95, zorder=9):
    segs = [(points[i], points[i + 1]) for i in range(len(points) - 1)]
    if not segs:
        return
    c0 = np.array(to_rgb(c_start))
    c1 = np.array(to_rgb(c_end))
    n = len(segs)
    colors = [tuple(c0 + (c1 - c0) * (i / max(n - 1, 1))) + (alpha,)
              for i in range(n)]
    lc = Line3DCollection(segs, colors=colors, linewidths=linewidth,
                          zorder=zorder)
    ax.add_collection3d(lc)


# ─── Framework-derived F-landscape ─────────────────────────────────────────

def F_surprisal(r):
    """Framework surprisal: F = -log(Tr[ρ τρτ]/Tr[ρ²]) restricted to the
    imaginary-content magnitude r = |y|.  For pure qubit states under
    τ = complex conjugation, this reduces to -log(1 - r²)."""
    return -np.log(1.0 - r ** 2)


def dF_dr(r):
    """Gradient of F in the radial direction (slope of the bowl wall)."""
    return 2.0 * r / (1.0 - r ** 2)


# ─── Figure ─────────────────────────────────────────────────────────────────

def make_figure():
    apply_style()

    fig = plt.figure(figsize=(11, 9), facecolor=BG)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor(BG)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_pane_color((0, 0, 0, 0))
        axis.line.set_color((0, 0, 0, 0))

    # ── Bowl surface F(y) = -log(1 - |y|²) ─────────────────────────────────

    R_MAX = 0.86          # cut off before F → ∞ at |y| = 1
    n_r, n_theta = 48, 84
    r_grid = np.linspace(0.001, R_MAX, n_r)
    theta_grid = np.linspace(0, 2 * np.pi, n_theta)
    R_mesh, T_mesh = np.meshgrid(r_grid, theta_grid)
    X = R_mesh * np.cos(T_mesh)
    Y = R_mesh * np.sin(T_mesh)
    Z = F_surprisal(R_mesh)

    cmap = LinearSegmentedColormap.from_list(
        'rp3_bowl', [to_rgb(ORANGE), to_rgb(VIOLET)], N=256)
    facecolors = cmap(R_mesh / R_MAX)

    # Per-vertex alpha: front of the bowl (facing the camera) is more
    # transparent so the spiral / ball / apex inside the bowl are not
    # obscured.  Camera azimuth ~42°, so the front-most theta is around
    # 42°.  Compute angular distance from front and modulate alpha.
    cam_azim_rad = np.radians(42.0)
    delta = np.abs(np.angle(np.exp(1j * (T_mesh - cam_azim_rad))))  # [0, π]
    # delta ≈ 0 at the front; delta ≈ π at the back.
    # Want low alpha at front (delta=0), normal alpha at back (delta=π).
    alpha_front = 0.18
    alpha_back  = 0.65
    alpha_field = alpha_front + (alpha_back - alpha_front) * (delta / np.pi)
    facecolors[..., 3] = alpha_field

    ax.plot_surface(X, Y, Z, facecolors=facecolors, rstride=1, cstride=1,
                    linewidth=0, antialiased=True, shade=True, zorder=2)

    # Faint wireframe overlay (constant alpha — keeps bowl shape readable
    # even where the front is highly transparent)
    ax.plot_wireframe(X, Y, Z, color=WHITE, alpha=0.18, linewidth=0.4,
                      rcount=10, ccount=24, zorder=3)

    # ── Cyan dot at the bowl bottom (actualization event) ─────────────────

    ax.scatter([0], [0], [0.05], color=CYAN, s=200,
               edgecolors=WHITE, linewidths=1.8, zorder=12)

    # ── Arrows up the bowl walls (Kähler-flow direction, against ∇F) ───────

    n_arrow_r = 3
    n_arrow_theta = 12
    arrow_radii = np.linspace(0.32, R_MAX * 0.84, n_arrow_r)
    arrow_thetas = np.linspace(0, 2 * np.pi, n_arrow_theta, endpoint=False)
    arrow_len = 0.30

    for ri in arrow_radii:
        for tj in arrow_thetas:
            x0 = ri * np.cos(tj)
            y0 = ri * np.sin(tj)
            z0 = F_surprisal(ri)

            # Tangent up the wall: (cos θ, sin θ, dF/dr).
            radial_xy = np.array([np.cos(tj), np.sin(tj)])
            slope = dF_dr(ri)
            tangent = np.array([radial_xy[0], radial_xy[1], slope])
            tangent = tangent / np.linalg.norm(tangent) * arrow_len

            ax.quiver(x0, y0, z0,
                      tangent[0], tangent[1], tangent[2],
                      color=VIOLET, arrow_length_ratio=0.40,
                      linewidth=1.5, alpha=0.85, zorder=8)

    # ── Spiral trajectory: ball rolling UP the bowl ────────────────────────

    n_pts = 280
    t = np.linspace(0, 1, n_pts)
    # Linear radial growth: state pumped outward from r=0 to r≈R_MAX*0.93
    r_traj = 0.04 + (R_MAX * 0.93 - 0.04) * t
    # Smooth angular sweep — about 2.6 turns for a clear spiral
    theta_traj = 5.2 * np.pi * t
    x_traj = r_traj * np.cos(theta_traj)
    y_traj = r_traj * np.sin(theta_traj)
    z_traj = F_surprisal(r_traj)
    traj = np.column_stack([x_traj, y_traj, z_traj])

    plot_gradient_line_3d(ax, traj, CYAN, VIOLET,
                          linewidth=3.0, alpha=0.98, zorder=10)

    # The "ball" at trajectory midpoint, to make the metaphor concrete
    ball_idx = int(0.65 * n_pts)
    bx, by, bz = traj[ball_idx]
    ball_t = ball_idx / (n_pts - 1)
    c_ball = (np.array(to_rgb(CYAN))
              + (np.array(to_rgb(VIOLET)) - np.array(to_rgb(CYAN))) * ball_t)
    ax.scatter([bx], [by], [bz], color=c_ball, s=260,
               edgecolors=WHITE, linewidths=2.0, zorder=13)

    # Arrowhead at trajectory endpoint
    if n_pts >= 3:
        v = traj[-1] - traj[-3]
        v = v / (np.linalg.norm(v) + 1e-9) * 0.18
        ax.quiver(traj[-1, 0], traj[-1, 1], traj[-1, 2],
                  v[0], v[1], v[2],
                  color=VIOLET, arrow_length_ratio=0.7,
                  linewidth=2.4, alpha=0.95, zorder=11)

    # ── Compact key (just colors → roles) ──────────────────────────────────

    legend_text = (
        "Bowl height: " r"$F = -\log(1 - |y|^2)$" "\n"
        "Orange: " r"$\tau$-even (" r"$\mathbb{RP}^3$" ")" "\n"
        "Violet: " r"$\tau$-odd content" "\n"
        "Cyan dot: actualization event\n"
        "Purple arrows: K\u00e4hler flow"
    )
    ax.text2D(0.02, 0.04, legend_text,
              transform=ax.transAxes, color=WHITE, fontsize=11,
              verticalalignment='bottom',
              bbox=dict(boxstyle='round,pad=0.4', facecolor='#0a0a1a',
                        edgecolor=GRAY, alpha=0.92))

    # ── Camera ─────────────────────────────────────────────────────────────

    ax.view_init(elev=24, azim=42)
    ax.set_xlim(-0.95, 0.95)
    ax.set_ylim(-0.95, 0.95)
    ax.set_zlim(-0.15, 2.35)
    ax.set_box_aspect((1, 1, 0.85))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    plt.tight_layout()
    save(fig, 'rp3-saddle-landscape.png')


def main():
    make_figure()


if __name__ == '__main__':
    main()

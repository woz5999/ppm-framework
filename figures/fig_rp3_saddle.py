"""
fig_rp3_saddle.py — RP³ as the unstable saddle of the Kähler flow.

Visualizes the structural fact that RP^n = Fix(τ) ⊂ CP^n is unstable
under the Kähler flow on the arena.  Shown on the simplest non-trivial
case: CP¹ ≅ S² (Bloch sphere) with τ acting as complex conjugation.
The fixed-point set is the great circle r_y = 0 (the x–z plane).  Under
the Kähler structure, perturbations in the imaginary direction r_y are
unstable: states sitting on the great circle drift off into the upper
or lower hemisphere.

The visual claim:
  - Gold great circle: RP¹ = Fix(τ).  States on this circle have zero
    imaginary content.
  - Cyan arrows: Kähler-flow vector field, normal to the equator,
    pointing into the imaginary direction.
  - Orange trajectories: representative states starting near RP¹ and
    spiraling into one hemisphere as imaginary content rebuilds.

The same structural fact holds on RP³ ⊂ CP³ in higher dimensions; the
toy model exhibits the geometry transparently.

Run: python fig_rp3_saddle.py
"""

import sys
sys.path.insert(0, '../')

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE


def plot_gradient_line_3d(ax, points, c_start, c_end, linewidth=2.6,
                          alpha=0.95, zorder=9):
    """Draw a 3D polyline with a color gradient from c_start to c_end."""
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


# ─── Trajectory integrator ─────────────────────────────────────────────────

def integrate_trajectory(start, t_max=2.5, dt=0.025, growth=0.9):
    """
    Integrate the Kähler-instability flow on the unit sphere starting near
    the equator.  Model: dr/dt = projection_to_tangent(growth * sign(r_y) * ŷ),
    constrained to ||r|| = 1.  Captures the qualitative claim that r_y = 0
    is unstable.
    """
    r = np.array(start, dtype=float)
    r = r / np.linalg.norm(r)
    pts = [r.copy()]
    n_steps = int(t_max / dt)
    for _ in range(n_steps):
        sign = 1.0 if r[1] >= 0 else -1.0
        force = np.array([0.0, sign * growth, 0.0])
        # tangent component (orthogonal to radial)
        tangent = force - np.dot(force, r) * r
        r = r + tangent * dt
        r = r / np.linalg.norm(r)
        pts.append(r.copy())
    return np.array(pts)


# ─── Figure ────────────────────────────────────────────────────────────────

def make_figure():
    apply_style()

    fig = plt.figure(figsize=(11, 10), facecolor=BG)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor(BG)
    ax.xaxis.set_pane_color((0, 0, 0, 0))
    ax.yaxis.set_pane_color((0, 0, 0, 0))
    ax.zaxis.set_pane_color((0, 0, 0, 0))
    ax.xaxis.line.set_color((0, 0, 0, 0))
    ax.yaxis.line.set_color((0, 0, 0, 0))
    ax.zaxis.line.set_color((0, 0, 0, 0))

    # ── Sphere wireframe and surface ───────────────────────────────────────

    n_u, n_v = 36, 18
    u = np.linspace(0, 2 * np.pi, n_u)
    v = np.linspace(0, np.pi, n_v)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))

    # Soft violet surface (CP¹ as the full possibility space)
    ax.plot_surface(xs, ys, zs, color=VIOLET, alpha=0.07,
                    linewidth=0, antialiased=True, zorder=1)
    # Faint wireframe for 3D depth cues
    ax.plot_wireframe(xs, ys, zs, color=VIOLET, alpha=0.18,
                      linewidth=0.4, rcount=12, ccount=18, zorder=2)

    # ── Equator: RP¹ = Fix(τ), the y = 0 great circle (τ-even, ORANGE) ────

    t = np.linspace(0, 2 * np.pi, 240)
    eqx, eqy, eqz = np.cos(t), np.zeros_like(t), np.sin(t)
    ax.plot(eqx, eqy, eqz, color=ORANGE, linewidth=4.2, alpha=0.98, zorder=8)

    # ── Kähler-flow vector field (purple — direction of departure into  ───
    #    τ-odd / imaginary sector / CP³ content)

    n_arrows = 14
    arrow_alphas = np.linspace(0, 2 * np.pi, n_arrows, endpoint=False)
    for alpha in arrow_alphas:
        x0 = np.cos(alpha)
        z0 = np.sin(alpha)
        # Two arrows per sample: one into +y, one into -y
        for sign in (+1, -1):
            ax.quiver(x0, sign * 0.02, z0,
                      0.0, sign * 0.32, 0.0,
                      color=VIOLET, arrow_length_ratio=0.32,
                      linewidth=1.6, alpha=0.90, zorder=7)

    # (Trajectories and per-event markers removed: the equator + arrows
    # already carry the inherent dynamical claim.  Trajectory clutter
    # added noise without new structural content.)

    # ── Reference axes ─────────────────────────────────────────────────────

    L = 1.45
    # Real axes (x, z) in pale white
    ax.plot([0, L], [0, 0], [0, 0], color=WHITE, linewidth=0.8, alpha=0.4)
    ax.plot([-L, 0], [0, 0], [0, 0], color=WHITE, linewidth=0.8, alpha=0.4)
    ax.plot([0, 0], [0, 0], [0, L], color=WHITE, linewidth=0.8, alpha=0.4)
    ax.plot([0, 0], [0, 0], [-L, 0], color=WHITE, linewidth=0.8, alpha=0.4)
    # Imaginary axis (y) in violet — the τ-odd direction
    ax.plot([0, 0], [0, L], [0, 0], color=VIOLET, linewidth=1.6, alpha=0.85)
    ax.plot([0, 0], [-L, 0], [0, 0], color=VIOLET, linewidth=1.6, alpha=0.85)

    ax.text(L * 1.08, 0, 0, r'$r_x$', color=WHITE, fontsize=14, alpha=0.7)
    ax.text(0, L * 1.10, 0, 'imaginary\ndirection', color=VIOLET,
            fontsize=13, weight='bold')
    ax.text(0, 0, L * 1.08, r'$r_z$', color=WHITE, fontsize=14, alpha=0.7)

    # ── Compact key (just colors → roles) ──────────────────────────────────

    legend_text = (
        "Orange: " r"$\mathbb{RP}^1 = \mathrm{Fix}(\tau)$" "\n"
        "Purple arrows: K\u00e4hler flow"
    )
    ax.text2D(0.02, 0.06, legend_text,
              transform=ax.transAxes, color=WHITE, fontsize=11,
              verticalalignment='bottom',
              bbox=dict(boxstyle='round,pad=0.4', facecolor='#0a0a1a',
                        edgecolor=GRAY, alpha=0.92))

    # ── Camera and limits ──────────────────────────────────────────────────

    ax.view_init(elev=20, azim=38)
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_zlim(-1.3, 1.3)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    plt.tight_layout()
    save(fig, 'rp3-saddle-instability.png')


def main():
    make_figure()


if __name__ == '__main__':
    main()

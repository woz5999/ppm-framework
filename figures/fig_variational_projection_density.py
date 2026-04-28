"""
fig_variational_projection_density.py — Actualization free energy as fiber + projection density

Single-panel schematic for ch08-variational §Actualization Free Energy.

Visual:
  - Faint gold horizontal baseline at bottom = RP³ stratum
  - Violet vertical fibers of varied heights = imaginary content of ρ
    (length encodes magnitude of off-stratum weight in that normal direction)
  - Cyan horizontal lines at varied y-heights = candidate projection events
    (line density at height h = firing probability density at that distance from RP³)
  - Density gradient: sparse near baseline, dense near top → asymmetric cut field
  - Reading: tall fibers thread dense cuts → likely clipped; short fibers persist

This is the Route A illustrative version: synthetic but representative numbers
chosen for visual clarity. Numerical content (fiber heights, cyan density profile)
is parameterized so it can later be sourced from PPM Lindblad/spectral machinery
(see archive/scripts/actualization_operator.py for the math).

Run: python fig_variational_projection_density.py
"""

import sys
sys.path.insert(0, '../')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY


# ─── Figure parameters ─────────────────────────────────────────────────────
WIDTH_IN, HEIGHT_IN = 12.0, 8.0
N_FIBERS = 11
N_CYAN_LINES = 22

# Frame layout (figure-fraction units, 0..1)
BASELINE_Y = 0.08
TOP_Y = 0.95
LEFT_X = 0.06
RIGHT_X = 0.97

# Random seed for reproducibility of synthetic distribution
SEED = 7


def add_glow(line_artist, color, base_lw, n_layers=4, max_extra=8.0, base_alpha=0.10):
    """Layer thick faint strokes under a line to fake luminous glow."""
    effects = []
    for i in range(n_layers, 0, -1):
        lw = base_lw + (i / n_layers) * max_extra
        alpha = base_alpha * (i / n_layers)
        effects.append(pe.Stroke(linewidth=lw, foreground=color, alpha=alpha))
    effects.append(pe.Normal())
    line_artist.set_path_effects(effects)


def draw_star_scatter(ax, n_stars=180):
    """Faint star scatter across the frame."""
    rng = np.random.default_rng(SEED + 1)
    xs = rng.uniform(0, 1, n_stars)
    ys = rng.uniform(0, 1, n_stars)
    sizes = rng.uniform(0.3, 2.5, n_stars)
    alphas = rng.uniform(0.15, 0.55, n_stars)
    for x, y, s, a in zip(xs, ys, sizes, alphas):
        ax.plot(x, y, marker='.', markersize=s, color=WHITE,
                alpha=a, transform=ax.transAxes, zorder=0)


def draw_baseline(ax):
    """Faint gold horizontal RP³ baseline — thin razor edge with subtle glow."""
    line = Line2D([LEFT_X, RIGHT_X], [BASELINE_Y, BASELINE_Y],
                  transform=ax.transAxes, color=GOLD, linewidth=1.0,
                  alpha=0.80, zorder=3)
    ax.add_line(line)
    # Much subtler glow — keep it as a razor edge, not a bar
    add_glow(line, GOLD, base_lw=1.0, n_layers=2, max_extra=3.5, base_alpha=0.08)

    # Small "RP³" label on the left margin near the baseline
    ax.text(LEFT_X - 0.018, BASELINE_Y, r'$\mathbb{RP}^3$',
            transform=ax.transAxes,
            color=GOLD, fontsize=12, ha='right', va='center',
            alpha=0.85, zorder=4)


def draw_fibers(ax):
    """Violet vertical fibers of scattered heights."""
    rng = np.random.default_rng(SEED)
    span = RIGHT_X - LEFT_X
    # Irregular x positions with jitter, well-distributed
    base_xs = np.linspace(LEFT_X + 0.04 * span, RIGHT_X - 0.04 * span, N_FIBERS)
    jitter = rng.uniform(-0.03, 0.03, N_FIBERS) * span
    xs = base_xs + jitter

    # Heights drawn to span the full visual range with good mid-range coverage,
    # so fibers actually thread the cyan stratum rather than splitting into
    # "short cluster at bottom" and "tall cluster at top." Tallest fibers
    # are capped well below the top of the frame so they terminate INSIDE
    # the densest cyan zone (visually clipped by the cut field).
    # Distribution: roughly uniform over a controlled range, with mild bias
    # toward shorter fibers (consistent with equilibrium Lindblad descent).
    raw = rng.beta(a=1.8, b=2.2, size=N_FIBERS)
    raw = 0.18 + 0.62 * raw   # range: ~[0.18, 0.80] of frame height
    rng.shuffle(raw)
    max_height = TOP_Y - BASELINE_Y
    heights = BASELINE_Y + raw * max_height

    # Per-fiber slight opacity variation
    opacities = rng.uniform(0.75, 0.95, N_FIBERS)

    for x, top_y, alpha in zip(xs, heights, opacities):
        line = Line2D([x, x], [BASELINE_Y, top_y],
                      transform=ax.transAxes, color=VIOLET,
                      linewidth=1.8, alpha=alpha, solid_capstyle='round',
                      zorder=5)
        ax.add_line(line)
        add_glow(line, VIOLET, base_lw=1.8, n_layers=4,
                 max_extra=7.0, base_alpha=0.08)


def cyan_density(y_normalized):
    """
    Probability-density profile for the projection field as a function of
    normalized height above the baseline (0 = at baseline, 1 = top of frame).

    Functional form: increases monotonically with height. Shape is chosen
    to match the variational principle's selection bias — fibers that
    extend far from RP³ are statistically more likely to be projected.

    A Route B version would source this from the actual Penrose-Diósi rate
    structure: Γ_b ∝ m_b² ∝ (mode level)², so cumulative cut density at
    height h scales as the integral of mode weights up to that level.
    Here we use a simple monotone shape that matches that qualitative form.
    """
    # Power-law profile: dense at top, sparse but nonzero at bottom.
    # The baseline floor (0.10) ensures a few cyan lines still appear in the
    # lower zone — even short fibers can be cut, just much less frequently.
    return 0.10 + 0.90 * y_normalized ** 1.5


def draw_cyan_stratum(ax):
    """Horizontal cyan projection lines with vertical density gradient."""
    rng = np.random.default_rng(SEED + 2)
    max_height = TOP_Y - BASELINE_Y

    # Place cyan lines using inverse-CDF sampling for smoother coverage
    # (rejection sampling can leave visible gaps at certain heights).
    # Build the CDF of cyan_density on [0, 1], then invert at uniform points.
    y_grid = np.linspace(0.02, 1.0, 400)
    rates = np.array([cyan_density(y) for y in y_grid])
    cdf = np.cumsum(rates)
    cdf /= cdf[-1]
    # Quasi-uniform u-points for even spread along the CDF, with tiny jitter
    u = (np.arange(N_CYAN_LINES) + 0.5) / N_CYAN_LINES
    u = u + rng.uniform(-0.02, 0.02, N_CYAN_LINES)
    u = np.clip(u, 0.001, 0.999)
    accepted = sorted(np.interp(u, cdf, y_grid).tolist())

    for y_norm in accepted:
        y = BASELINE_Y + y_norm * max_height

        # Line length and lateral offset slightly irregular for atmosphere
        line_span = rng.uniform(0.65, 1.0) * (RIGHT_X - LEFT_X)
        x_offset = rng.uniform(0, (RIGHT_X - LEFT_X) - line_span)
        x_start = LEFT_X + x_offset
        x_end = x_start + line_span

        # Opacity rises with height (denser zones also brighter)
        alpha = 0.20 + 0.55 * y_norm
        lw = 0.8 + 0.4 * y_norm

        line = Line2D([x_start, x_end], [y, y],
                      transform=ax.transAxes, color=CYAN,
                      linewidth=lw, alpha=alpha,
                      solid_capstyle='round', zorder=4)
        ax.add_line(line)
        add_glow(line, CYAN, base_lw=lw, n_layers=3,
                 max_extra=4.5, base_alpha=0.06)


def draw_annotations(ax):
    """Three minimal labels — no axes, no ticks, no legend."""
    # Vertical label on left margin
    ax.text(LEFT_X - 0.035, (BASELINE_Y + TOP_Y) / 2,
            'distance from $\\mathbb{RP}^3$',
            transform=ax.transAxes, color=GRAY, fontsize=10,
            ha='center', va='center', rotation=90, alpha=0.85)

    # Top right: P(projection) with up-arrow
    ax.text(RIGHT_X + 0.005, TOP_Y - 0.02,
            r'$P(\mathrm{projection})\ \uparrow$',
            transform=ax.transAxes, color=CYAN, fontsize=11,
            ha='right', va='top', alpha=0.95,
            weight='bold')

    # Quiet inline F formula
    ax.text(LEFT_X + 0.020, TOP_Y - 0.03,
            r'$\mathcal{F} = -\log P$',
            transform=ax.transAxes, color=GRAY, fontsize=13,
            ha='left', va='top', alpha=0.90)


def render_one(filename):
    """Build the figure and save it to the given filename."""
    apply_style()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    draw_star_scatter(ax)
    draw_baseline(ax)
    draw_cyan_stratum(ax)   # behind fibers so fibers visually pierce them
    draw_fibers(ax)
    draw_annotations(ax)

    save(fig, filename)


def main():
    render_one('fig_variational_projection_density.png')
    render_one('fig_variational_projection_density.pdf')


if __name__ == '__main__':
    main()

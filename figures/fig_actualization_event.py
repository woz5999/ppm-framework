"""
fig_actualization_event.py — schematic of a single actualization event.

Shows the complete per-event data set:
  - τ-projection (the operator) descending from CP³
  - 2π fiber step (Hopf circumference being collapsed)
  - α survival fraction (at the projection interface)
  - position k of N_∞ tiles on the RP³ boundary
  - 4 facts inside the tile: (A,B) Kähler doublet × (C,D) gauge doublet
  - E(k) energy at this hierarchy level
  - the dormant surrounding tessellation (other boundary positions)

Visual claim: this list of local data, through the master self-consistency
relation, determines every cosmological quantity the framework produces.

Run: python fig_actualization_event.py
"""

import sys
sys.path.insert(0, '../')

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyArrowPatch

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE


# ─── Geometry helpers ──────────────────────────────────────────────────────

def rhomb_vertices(cx, cy, size, half_angle_deg=36):
    """
    Return four vertices of a rhomb centered at (cx, cy) with given size,
    oriented horizontally (long axis along x).  half_angle_deg is half of
    the acute angle: 36° gives a thick Penrose rhomb (72° acute).
    """
    a = math.radians(half_angle_deg)
    dx = size * math.cos(a)
    dy = size * math.sin(a)
    return np.array([
        [cx - dx, cy],
        [cx,      cy + dy],
        [cx + dx, cy],
        [cx,      cy - dy],
    ])


# ─── Figure ────────────────────────────────────────────────────────────────

def make_figure():
    apply_style()

    fig, ax = plt.subplots(figsize=(17, 10), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')

    # ── Header ─────────────────────────────────────────────────────────────

    ax.text(8.5, 9.55, 'A Single Actualization Event',
            color=WHITE, fontsize=24, weight='bold', ha='center')
    ax.text(8.5, 9.10,
            'the complete set of local data defining one projection',
            color=GRAY, fontsize=14, ha='center', style='italic')

    # ── Surrounding dormant tessellation (faded) ───────────────────────────

    rng = np.random.default_rng(7)
    tile_centers_drawn = []
    for i in range(-7, 8):
        for j in range(-5, 6):
            if i == 0 and j == 0:
                continue
            # slight offset / jitter for organic look
            ox = 8.5 + i * 1.05 + rng.uniform(-0.1, 0.1)
            oy = 4.5 + j * 0.62 + rng.uniform(-0.1, 0.1)
            if 0.8 < ox < 16.2 and 1.4 < oy < 7.6:
                # alternate orientation
                ang = 36 if (i + j) % 2 == 0 else 54
                v = rhomb_vertices(ox, oy, 0.40, half_angle_deg=ang)
                tile = Polygon(v, closed=True, facecolor=GOLD,
                               alpha=0.07, edgecolor=GOLD, linewidth=0.5,
                               zorder=2)
                ax.add_patch(tile)
                tile_centers_drawn.append((ox, oy))

    # ── Central tile (the active one) ──────────────────────────────────────

    cx, cy = 8.5, 4.5
    tile_size = 1.6
    half_ang = 36  # thick Penrose rhomb (72° acute angle)
    tv = rhomb_vertices(cx, cy, tile_size, half_angle_deg=half_ang)

    # Slight glow halo
    halo = Polygon(rhomb_vertices(cx, cy, tile_size + 0.25, half_angle_deg=half_ang),
                   closed=True, facecolor=GOLD, alpha=0.12,
                   edgecolor='none', zorder=4)
    ax.add_patch(halo)

    # Main tile
    tile = Polygon(tv, closed=True, facecolor=GOLD, alpha=0.40,
                   edgecolor=GOLD, linewidth=3.0, zorder=5)
    ax.add_patch(tile)

    # Inner cross — partitions the tile into the 4 fact-quadrants
    dx = tile_size * math.cos(math.radians(half_ang))
    dy = tile_size * math.sin(math.radians(half_ang))
    ax.plot([cx - dx, cx + dx], [cy, cy], color=WHITE,
            linewidth=1.2, alpha=0.7, zorder=6)
    ax.plot([cx, cx], [cy - dy, cy + dy], color=WHITE,
            linewidth=1.2, alpha=0.7, zorder=6)

    # Four-fact letters in each quadrant
    fact_label_off_x = 0.50
    fact_label_off_y = 0.18
    for label, ox, oy in [
        ('A', cx - fact_label_off_x, cy + fact_label_off_y),
        ('B', cx + fact_label_off_x, cy + fact_label_off_y),
        ('C', cx - fact_label_off_x, cy - fact_label_off_y),
        ('D', cx + fact_label_off_x, cy - fact_label_off_y),
    ]:
        ax.text(ox, oy, label, color=WHITE, fontsize=18, weight='bold',
                ha='center', va='center', zorder=7)

    # ── Descending column (τ-projection) ────────────────────────────────────

    col_top = 8.0
    col_bot = cy + dy + 0.05
    col_w = 0.30

    column = Polygon([
        [cx - col_w, col_bot],
        [cx - col_w, col_top],
        [cx + col_w, col_top],
        [cx + col_w, col_bot],
    ], closed=True, facecolor=VIOLET, alpha=0.40, edgecolor=VIOLET,
       linewidth=2.0, zorder=4)
    ax.add_patch(column)

    # Hopf-fiber circle on the column (mid-height)
    fiber_y = col_bot + (col_top - col_bot) * 0.55
    fiber_r = 0.55
    fiber = Circle((cx, fiber_y), fiber_r, facecolor=BG, edgecolor=CYAN,
                   linewidth=2.5, zorder=7)
    ax.add_patch(fiber)
    ax.text(cx, fiber_y, r'$2\pi$', color=CYAN, fontsize=18, weight='bold',
            ha='center', va='center', zorder=8)

    # Arrow on column showing direction of projection
    arrow = FancyArrowPatch(
        (cx + col_w + 0.05, col_top - 0.3),
        (cx + col_w + 0.05, col_bot + 0.2),
        arrowstyle='-|>', mutation_scale=18,
        color=VIOLET, linewidth=1.8, alpha=0.85, zorder=6
    )
    ax.add_patch(arrow)

    # ── Annotations with leader lines ──────────────────────────────────────

    def annotate(target, anchor, label, sublabel, color, ha='center'):
        ax.annotate('', xy=target, xytext=anchor,
                    arrowprops=dict(arrowstyle='-', color=color,
                                    linewidth=1.2, alpha=0.85,
                                    shrinkA=0, shrinkB=4))
        text = label if not sublabel else f'{label}\n{sublabel}'
        ax.text(anchor[0], anchor[1], text, color=color,
                fontsize=12, ha=ha, va='center',
                bbox=dict(boxstyle='round,pad=0.45',
                          facecolor='#0a0a1a', edgecolor=color,
                          alpha=0.95, linewidth=1.3))

    # Above column
    annotate(target=(cx, col_top + 0.05),
             anchor=(2.3, 8.4),
             label=r"$\mathbb{CP}^3$ possibility content",
             sublabel="(input to the projection)",
             color=VIOLET)

    # τ-projection (column itself)
    annotate(target=(cx + col_w + 0.05, fiber_y - 0.5),
             anchor=(14.5, 8.0),
             label=r"$\tau$-projection",
             sublabel=r"the operator: $\mathbb{CP}^3 \to \mathbb{RP}^3$",
             color=VIOLET)

    # Fiber step
    annotate(target=(cx + fiber_r + 0.05, fiber_y + 0.05),
             anchor=(14.7, 6.6),
             label=r"$2\pi$ fiber step",
             sublabel="Hopf circumference\n(elementary projection unit)",
             color=CYAN)

    # Survival fraction at the interface
    annotate(target=(cx - col_w - 0.05, col_bot + 0.02),
             anchor=(2.3, 6.6),
             label=r"$\alpha \approx 1/137$",
             sublabel=r"survival fraction; $(1-\alpha)$"
                      "\nstripped as entropy",
             color=GOLD)

    # Tile = position on the boundary
    annotate(target=(cx + dx - 0.05, cy + 0.20),
             anchor=(14.5, 4.6),
             label=r"position $k$ of $N_\infty$ tiles",
             sublabel=r"Compton cell on $\mathbb{RP}^3$"
                      "\nboundary",
             color=GOLD)

    # 4 facts inside
    annotate(target=(cx - 0.55, cy),
             anchor=(2.3, 4.6),
             label="4 facts deposited",
             sublabel=r"$(A,B)$ K\"ahler doublet"
                      "\n"
                      r"$(C,D)$ gauge doublet",
             color=WHITE)

    # Energy E(k)
    annotate(target=(cx + 0.05, cy - dy - 0.05),
             anchor=(8.5, 2.1),
             label=r"$E(k) = m_\pi (2\pi)^{(51-k)/2}$",
             sublabel=r"energy at hierarchy level $k$"
                      "\n(per-event mass equivalent)",
             color=ORANGE)

    # Surrounding dormant tessellation
    annotate(target=(5.7, 3.0),
             anchor=(2.3, 2.7),
             label="other boundary tiles",
             sublabel=r"(dormant; $N_\infty - 1$ of them)",
             color=GRAY)

    # ── Footer ─────────────────────────────────────────────────────────────

    ax.text(8.5, 1.10,
            r"Through $(2\pi)^{27}\sqrt{\alpha} = \varphi^{98}$, this local data "
            r"determines $G$, $\Lambda$, $H_0$, $R$, the cosmic age, "
            r"and the depth of the energy hierarchy.",
            color=WHITE, fontsize=13, ha='center', style='italic')
    ax.text(8.5, 0.62,
            "Each event contains the cosmos.",
            color=CYAN, fontsize=15, ha='center', weight='bold', style='italic')

    plt.tight_layout()
    save(fig, 'actualization-event.png')


def main():
    make_figure()


if __name__ == '__main__':
    main()

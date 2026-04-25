"""
v2_measurement_torus.py — Measurement torus T^2 at three scales.

Three panels, each a square [0, pi/2] x [0, pi/2] in doublet axes
(theta_AB, theta_CD).  Grid spacing is the angular resolution bound

    delta_theta >= (pi/2) * R^{-3/2}

so the grid cell count is exactly R^{3/2} per axis.  At R = 1 the grid
degenerates to a single cell: the four fact types fuse.  Corner labels
associate each corner with one of the four canonical measurement
configurations {(A or B) x (C or D)}.

Run:  python v2_measurement_torus.py
Output: figures/computed/v2_measurement_torus.png
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from figures._style import apply_style, BG, GOLD, VIOLET, CYAN, WHITE, GRAY

apply_style()

plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 13,
})

# ── Three representative R values and their cell counts ──
# cell_count = R^{3/2}.  We draw the grid at the exact spacing implied by
# the bound, capping the visible cell count so the densest panel stays
# legible.
panels = [
    # (R, display_cells, regime_label)
    (4.0,  8, r'$R=4$  (particle scale)'),
    (2.0,  3, r'$R=2$  (boundary approach)'),
    (1.0,  1, r'$R=1$  (consciousness: types fuse)'),
]

fig, axes = plt.subplots(1, 3, figsize=(15, 6))
fig.patch.set_facecolor(BG)

TYPE_COLORS = {
    'A': GOLD,       # spectral  (Kahler doublet)
    'B': VIOLET,     # spatial   (Kahler doublet)
    'C': CYAN,       # chiral    (gauge doublet)
    'D': '#F39C12',  # intensity (gauge doublet)
}

# Pi/2 endpoint
PI2 = np.pi / 2.0

def draw_panel(ax, R, n_cells, label):
    ax.set_facecolor(BG)
    # Extra room on bottom for axis labels + delta_theta annotation
    ax.set_xlim(-0.14, PI2 + 0.14)
    ax.set_ylim(-0.42, PI2 + 0.22)
    ax.set_aspect('equal')

    # ── Background shading: continuous info-capacity gradient ──
    bg_rect = Rectangle((0, 0), PI2, PI2,
                        facecolor=VIOLET, alpha=0.06, edgecolor='none',
                        zorder=1)
    ax.add_patch(bg_rect)

    # ── Grid lines at delta_theta spacing ──
    if n_cells > 1:
        spacing = PI2 / n_cells
        for i in range(1, n_cells):
            pos = i * spacing
            ax.plot([pos, pos], [0, PI2], color=WHITE,
                    linewidth=0.7, alpha=0.35, zorder=2)
            ax.plot([0, PI2], [pos, pos], color=WHITE,
                    linewidth=0.7, alpha=0.35, zorder=2)

    # ── Highlighted representative cell ──
    if n_cells > 1:
        spacing = PI2 / n_cells
        ci = n_cells // 2
        cj = n_cells // 2
        cell = Rectangle((ci * spacing, cj * spacing), spacing, spacing,
                         facecolor=GOLD, alpha=0.30, edgecolor=GOLD,
                         linewidth=1.6, zorder=3)
        ax.add_patch(cell)
    else:
        cell = Rectangle((0, 0), PI2, PI2,
                         facecolor=GOLD, alpha=0.18, edgecolor=GOLD,
                         linewidth=1.8, zorder=3)
        ax.add_patch(cell)

    # ── Outer box ──
    outer = Rectangle((0, 0), PI2, PI2,
                      facecolor='none', edgecolor=CYAN, linewidth=2.2,
                      zorder=4)
    ax.add_patch(outer)

    # ── Corner fact-type labels (just outside each corner) ──
    corner_offset_x = 0.10
    corner_offset_y = 0.06
    ax.text(-corner_offset_x, PI2 + corner_offset_y, r'$(A,D)$',
            color=WHITE, fontsize=10.5, ha='right', va='bottom', alpha=0.9)
    ax.text(PI2 + corner_offset_x, PI2 + corner_offset_y, r'$(B,D)$',
            color=WHITE, fontsize=10.5, ha='left', va='bottom', alpha=0.9)
    ax.text(-corner_offset_x, -corner_offset_y, r'$(A,C)$',
            color=WHITE, fontsize=10.5, ha='right', va='top', alpha=0.9)
    ax.text(PI2 + corner_offset_x, -corner_offset_y, r'$(B,C)$',
            color=WHITE, fontsize=10.5, ha='left', va='top', alpha=0.9)

    # ── Axis tick labels (0 and pi/2) drawn manually ──
    ax.text(0, -0.03, '0', color=WHITE, fontsize=10,
            ha='center', va='top', alpha=0.75)
    ax.text(PI2, -0.03, r'$\pi/2$', color=WHITE, fontsize=10,
            ha='center', va='top', alpha=0.75)
    ax.text(-0.03, 0, '0', color=WHITE, fontsize=10,
            ha='right', va='center', alpha=0.75)
    ax.text(-0.03, PI2, r'$\pi/2$', color=WHITE, fontsize=10,
            ha='right', va='center', alpha=0.75)

    # Kill default ticks
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # ── Axis-name labels, manually positioned ──
    ax.text(PI2/2, -0.18, r'$\theta_{AB}$  (spectral $\leftrightarrow$ spatial)',
            color=WHITE, fontsize=11, ha='center', va='center', alpha=0.9)
    ax.text(-0.22, PI2/2, r'$\theta_{CD}$  (chiral $\leftrightarrow$ intensity)',
            color=WHITE, fontsize=11, ha='center', va='center',
            rotation=90, alpha=0.9)

    # ── Panel title (R regime) ──
    ax.set_title(label, color=WHITE, fontsize=13, pad=12, weight='bold')

    # ── delta_theta annotation (below the axis label) ──
    dtheta = PI2 * R**(-1.5)
    if n_cells > 1:
        dtheta_frac = r'$\delta\theta \geq \frac{\pi}{2}\,R^{-3/2} \approx %.3f$' % dtheta
        cell_text = r'$R^{3/2} \approx %.1f$ cells per axis' % (R**1.5)
    else:
        dtheta_frac = r'$\delta\theta \geq \pi/2$'
        cell_text = 'single cell — no resolution'

    ax.text(PI2/2, -0.29, dtheta_frac,
            color=WHITE, fontsize=11, ha='center', va='center', alpha=0.85)
    ax.text(PI2/2, -0.37, cell_text,
            color=GOLD, fontsize=10.5, ha='center', va='center',
            style='italic', alpha=0.95)


for ax, (R, n_cells, label) in zip(axes, panels):
    draw_panel(ax, R, n_cells, label)

# ── Figure title ──
fig.suptitle(r'Measurement torus $T^2 = [0, \pi/2]^2$: angular resolution across scales',
             color=WHITE, fontsize=15, y=0.98, weight='bold')

# ── Bottom caption ──
fig.text(0.5, 0.02,
         r'At high $R$ the torus supports many distinct $\tau$-projection configurations; '
         r'as $R \to 1$ the angular bound $\delta\theta \geq (\pi/2)\,R^{-3/2}$ '
         r'forces the four fact types to fuse into undifferentiated content.',
         color=WHITE, fontsize=11, ha='center', va='bottom',
         alpha=0.80, style='italic')

plt.tight_layout(rect=[0, 0.06, 1, 0.95])

# ── Save ──
outdir = os.path.join(os.path.dirname(__file__), '..', '..', 'figures', 'computed')
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, 'v2_measurement_torus.png')
fig.savefig(outpath, dpi=200)
plt.close(fig)
print(f"Saved: {outpath}")

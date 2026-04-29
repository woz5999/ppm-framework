"""
v2_measurement_torus.py — Measurement torus T^2 at three scales.

Three panels, each a square [0, pi/2] x [0, pi/2] in doublet axes
(theta_AB, theta_CD).  Grid spacing is the angular resolution bound

    delta_theta >= (pi/2) * R^{-3/2}

so the grid cell count is exactly R^{3/2} per axis.  At R = 1 the grid
degenerates to a single cell: the four fact types fuse.  Corner labels
associate each corner with one of the four canonical measurement
configurations {(A or B) x (C or D)}.

This figure uses a LIGHT palette (overrides the project's default dark
style) for legibility — three nearly-empty squares against a black
background read as a visual black hole.

Run:  python v2_measurement_torus.py
Output: figures/computed/v2_measurement_torus.png
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle

# ── Local LIGHT palette (overrides shared dark style) ──
BG_LIGHT      = '#F2F2F6'   # light gray background
PANEL_BG      = '#FAFAFC'   # near-white panel fill
TEXT_DARK     = '#1A1A2E'   # near-black text
TEXT_MUTED    = '#4A4A5C'   # muted dark gray for secondary text
GRID_LINE     = '#9999AA'   # mid-gray grid lines
ORANGE_BRIGHT = '#FF8A1E'   # bright orange highlight
ORANGE_EDGE   = '#D86A0A'   # darker orange for cell border
BORDER_TEAL   = '#1F7A85'   # darker teal for outer box (readable on light)
ANNOT_ORANGE  = '#C95A0E'   # bold orange for cell-count annotation

mpl.rcParams.update({
    'figure.facecolor': BG_LIGHT,
    'axes.facecolor':   PANEL_BG,
    'savefig.facecolor': BG_LIGHT,
    'text.color':       TEXT_DARK,
    'axes.labelcolor':  TEXT_DARK,
    'xtick.color':      TEXT_DARK,
    'ytick.color':      TEXT_DARK,
    'font.family':      'serif',
    'font.size':        12,
    'axes.titlesize':   14,
    'axes.labelsize':   13,
})

# ── Three representative R values and their cell counts ──
panels = [
    (4.0,  8, r'$R=4$  (particle scale)'),
    (2.0,  3, r'$R=2$  (boundary approach)'),
    (1.0,  1, r'$R=1$  (consciousness: types fuse)'),
]

fig, axes = plt.subplots(1, 3, figsize=(15, 6))
fig.patch.set_facecolor(BG_LIGHT)

PI2 = np.pi / 2.0


def draw_panel(ax, R, n_cells, label):
    ax.set_facecolor(PANEL_BG)
    ax.set_xlim(-0.14, PI2 + 0.14)
    ax.set_ylim(-0.42, PI2 + 0.22)
    ax.set_aspect('equal')

    # ── Subtle panel fill ──
    bg_rect = Rectangle((0, 0), PI2, PI2,
                        facecolor=PANEL_BG, edgecolor='none', zorder=1)
    ax.add_patch(bg_rect)

    # ── Grid lines at delta_theta spacing ──
    if n_cells > 1:
        spacing = PI2 / n_cells
        for i in range(1, n_cells):
            pos = i * spacing
            ax.plot([pos, pos], [0, PI2], color=GRID_LINE,
                    linewidth=0.8, alpha=0.55, zorder=2)
            ax.plot([0, PI2], [pos, pos], color=GRID_LINE,
                    linewidth=0.8, alpha=0.55, zorder=2)

    # ── Highlighted representative cell (bright orange) ──
    if n_cells > 1:
        spacing = PI2 / n_cells
        ci = n_cells // 2
        cj = n_cells // 2
        cell = Rectangle((ci * spacing, cj * spacing), spacing, spacing,
                         facecolor=ORANGE_BRIGHT, alpha=0.70,
                         edgecolor=ORANGE_EDGE, linewidth=1.8, zorder=3)
        ax.add_patch(cell)
    else:
        cell = Rectangle((0, 0), PI2, PI2,
                         facecolor=ORANGE_BRIGHT, alpha=0.55,
                         edgecolor=ORANGE_EDGE, linewidth=2.0, zorder=3)
        ax.add_patch(cell)

    # ── Outer box (darker teal — readable on light bg) ──
    outer = Rectangle((0, 0), PI2, PI2,
                      facecolor='none', edgecolor=BORDER_TEAL, linewidth=2.4,
                      zorder=4)
    ax.add_patch(outer)

    # ── Corner fact-type labels ──
    corner_offset_x = 0.10
    corner_offset_y = 0.06
    ax.text(-corner_offset_x, PI2 + corner_offset_y, r'$(A,D)$',
            color=TEXT_DARK, fontsize=10.5, ha='right', va='bottom')
    ax.text(PI2 + corner_offset_x, PI2 + corner_offset_y, r'$(B,D)$',
            color=TEXT_DARK, fontsize=10.5, ha='left', va='bottom')
    ax.text(-corner_offset_x, -corner_offset_y, r'$(A,C)$',
            color=TEXT_DARK, fontsize=10.5, ha='right', va='top')
    ax.text(PI2 + corner_offset_x, -corner_offset_y, r'$(B,C)$',
            color=TEXT_DARK, fontsize=10.5, ha='left', va='top')

    # ── Axis tick labels (0 and pi/2) ──
    ax.text(0, -0.03, '0', color=TEXT_MUTED, fontsize=10,
            ha='center', va='top')
    ax.text(PI2, -0.03, r'$\pi/2$', color=TEXT_MUTED, fontsize=10,
            ha='center', va='top')
    ax.text(-0.03, 0, '0', color=TEXT_MUTED, fontsize=10,
            ha='right', va='center')
    ax.text(-0.03, PI2, r'$\pi/2$', color=TEXT_MUTED, fontsize=10,
            ha='right', va='center')

    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # ── Axis-name labels ──
    ax.text(PI2/2, -0.18, r'$\theta_{AB}$  (spectral $\leftrightarrow$ spatial)',
            color=TEXT_DARK, fontsize=11, ha='center', va='center')
    ax.text(-0.22, PI2/2, r'$\theta_{CD}$  (chiral $\leftrightarrow$ intensity)',
            color=TEXT_DARK, fontsize=11, ha='center', va='center',
            rotation=90)

    # ── Panel title ──
    ax.set_title(label, color=TEXT_DARK, fontsize=13, pad=12, weight='bold')

    # ── delta_theta annotation ──
    dtheta = PI2 * R**(-1.5)
    if n_cells > 1:
        dtheta_frac = r'$\delta\theta \geq \frac{\pi}{2}\,R^{-3/2} \approx %.3f$' % dtheta
        cell_text = r'$R^{3/2} \approx %.1f$ cells per axis' % (R**1.5)
    else:
        dtheta_frac = r'$\delta\theta \geq \pi/2$'
        cell_text = 'single cell — no resolution'

    ax.text(PI2/2, -0.29, dtheta_frac,
            color=TEXT_DARK, fontsize=11, ha='center', va='center')
    ax.text(PI2/2, -0.37, cell_text,
            color=ANNOT_ORANGE, fontsize=10.5, ha='center', va='center',
            style='italic', weight='bold')


for ax, (R, n_cells, label) in zip(axes, panels):
    draw_panel(ax, R, n_cells, label)

# ── Figure title ──
fig.suptitle(r'Measurement torus $T^2 = [0, \pi/2]^2$: angular resolution across scales',
             color=TEXT_DARK, fontsize=15, y=0.98, weight='bold')

# ── Bottom caption ──
fig.text(0.5, 0.02,
         r'At high $R$ the torus supports many distinct $\tau$-projection configurations; '
         r'as $R \to 1$ the angular bound $\delta\theta \geq (\pi/2)\,R^{-3/2}$ '
         r'forces the four fact types to fuse into undifferentiated content.',
         color=TEXT_MUTED, fontsize=11, ha='center', va='bottom',
         style='italic')

plt.tight_layout(rect=[0, 0.06, 1, 0.95])

# ── Save ──
outdir = os.path.join(os.path.dirname(__file__), '..', '..', 'figures', 'computed')
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, 'v2_measurement_torus.png')
fig.savefig(outpath, dpi=200)
plt.close(fig)
print(f"Saved: {outpath}")

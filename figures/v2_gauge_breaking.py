"""
Gauge symmetry breaking chain — v7.
Changes: dim labels inside boxes, SO(4) grouping around SU(2)_L × SU(2)_R,
U(1)_em intermediate box for EWSB, output to figures/computed/.
Fix overlap between U(1)_{B-L} and SU(2)_L.
"""
import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Resolve paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
OUTPUT_DIR = os.path.join(REPO_ROOT, 'figures', 'computed')
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'v2_gauge_breaking.png')

# ── Colors ──
VIOLET  = '#7B68EE'
CYAN    = '#00CED1'
GOLD    = '#D4A843'
BG      = '#0d1117'
WHITE   = '#e8e8e8'
DIM     = '#555555'
DIM_LT  = '#777777'
VIO_LT  = '#9B88FF'
GOLD_LT = '#E8C870'
CYAN_DK = '#009AA0'
RED_DIM = '#CC4444'

fig, ax = plt.subplots(figsize=(12, 12), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(-6.5, 7)
ax.set_ylim(-1.2, 11.5)
ax.axis('off')


def box(x, y, text, color, w=4.2, h=0.6, fs=12, alpha=0.2, tc=WHITE, lw=1.5, dim=None):
    b = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.1",
                        facecolor=color, edgecolor=color, alpha=alpha, lw=lw, zorder=2)
    ax.add_patch(b)
    border = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.1",
                             facecolor='none', edgecolor=color, alpha=0.55, lw=lw, zorder=3)
    ax.add_patch(border)
    if dim:
        ax.text(x, y + 0.09, text, ha='center', va='center', fontsize=fs, color=tc,
                fontfamily='serif', zorder=4, fontweight='medium')
        ax.text(x, y - 0.16, dim, ha='center', va='center', fontsize=max(fs-3, 7),
                color=DIM, fontfamily='serif', zorder=4)
    else:
        ax.text(x, y, text, ha='center', va='center', fontsize=fs, color=tc,
                fontfamily='serif', zorder=4, fontweight='medium')


def arrow(x0, y0, x1, y1, color, lw=1.8):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw))


# ── k-scale on left margin ──
kx = -5.8
ax.plot([kx, kx], [0.3, 10.7], color=DIM, lw=1, alpha=0.4, zorder=0)
ax.text(kx, 11.0, '$k$', ha='center', fontsize=10, color=DIM_LT)

k_ticks = [
    (10.5, '$k \\approx 1$\nPlanck', VIOLET),
    (8.8, '$k \\approx 16$', CYAN),
    (5.5, '$k \\approx 44.5$', CYAN),
    (2.8, '$k \\approx 44.5$', CYAN_DK),
    (1.0, '$k \\approx 51$', GOLD),
]
for y, label, color in k_ticks:
    ax.plot([kx - 0.15, kx + 0.15], [y, y], color=color, lw=1.2, alpha=0.5)
    ax.text(kx - 0.25, y, label, ha='right', va='center', fontsize=7.5,
            color=color, alpha=0.7)

# ════════════════════════════════════════════
# LEVEL 1: PSU(4) — full isometry
# ════════════════════════════════════════════
y1 = 10.5
box(0, y1, r'PSU(4)  —  full arena isometry', VIOLET, w=6.0, h=0.75, fs=14,
    alpha=0.2, dim='dim 15')

# ════════════════════════════════════════════
# Arrow: PSU(4) → Pati-Salam
# ════════════════════════════════════════════
arrow(0, y1 - 0.55, 0, 9.55, DIM_LT, lw=1.3)
ax.text(0.3, 9.85, r'tangent/normal split reveals SO(4) structure',
        ha='left', fontsize=8.5, color=DIM_LT, fontstyle='italic')

# ════════════════════════════════════════════
# LEVEL 2: Pati-Salam
# ════════════════════════════════════════════
y2 = 8.8

# Background band spanning all three factors
ps_band = FancyBboxPatch((-4.5, y2 - 0.75), 10.5, 1.5, boxstyle="round,pad=0.1",
                          facecolor=CYAN, edgecolor=CYAN, alpha=0.06, lw=0, zorder=0.5)
ax.add_patch(ps_band)
ps_border = FancyBboxPatch((-4.5, y2 - 0.75), 10.5, 1.5, boxstyle="round,pad=0.1",
                            facecolor='none', edgecolor=CYAN, alpha=0.2, lw=1,
                            linestyle='--', zorder=0.5)
ax.add_patch(ps_border)

ax.text(6.5, y2 + 0.15, 'Pati-Salam', ha='left', fontsize=11, color=CYAN,
        fontweight='bold')
ax.text(6.5, y2 - 0.2, 'dim 21', ha='left', fontsize=9, color=CYAN, alpha=0.5)

# Factor positions — spread wider to prevent overlap downstream
x_su4 = -2.8
x_su2l = 1.2
x_su2r = 3.8

# SO(4) grouping around SU(2)_L × SU(2)_R
so4_cx = (x_su2l + x_su2r) / 2
so4_w = 5.0
so4_h = 1.1
so4_band = FancyBboxPatch((so4_cx - so4_w/2, y2 - so4_h/2), so4_w, so4_h,
                           boxstyle="round,pad=0.1",
                           facecolor=GOLD, edgecolor=GOLD, alpha=0.04, lw=0, zorder=1)
ax.add_patch(so4_band)
so4_border = FancyBboxPatch((so4_cx - so4_w/2, y2 - so4_h/2), so4_w, so4_h,
                             boxstyle="round,pad=0.1",
                             facecolor='none', edgecolor=GOLD, alpha=0.25, lw=1,
                             linestyle=':', zorder=1)
ax.add_patch(so4_border)
ax.text(so4_cx, y2 + so4_h/2 + 0.12,
        r'SO(4) $\cong$ SU(2)$_L$ $\times$ SU(2)$_R$',
        ha='center', fontsize=8.5, color=GOLD_LT, alpha=0.7)
ax.text(so4_cx + so4_w/2 + 0.15, y2, 'dim 6', ha='left', fontsize=8,
        color=GOLD, alpha=0.5)

box(x_su4, y2, r'SU(4)$_C$', VIOLET, w=2.8, h=0.7, fs=13, alpha=0.15, dim='dim 15')
box(x_su2l, y2, r'SU(2)$_L$', CYAN, w=2.0, h=0.7, fs=13, alpha=0.15, dim='dim 3')
box(x_su2r, y2, r'SU(2)$_R$', GOLD, w=2.0, h=0.7, fs=13, alpha=0.15, dim='dim 3')

# × signs
ax.text((x_su4 + x_su2l) / 2, y2, r'$\times$', ha='center', va='center',
        fontsize=14, color=DIM_LT)
ax.text((x_su2l + x_su2r) / 2, y2, r'$\times$', ha='center', va='center',
        fontsize=14, color=DIM_LT)

# ════════════════════════════════════════════
# Constraint labels
# ════════════════════════════════════════════
y_label = 7.6

ax.text(x_su4, y_label + 0.3, r'Isotropy at $p$', ha='center', fontsize=11,
        color=VIO_LT, fontweight='bold')
ax.text(x_su4, y_label - 0.05, r'"actualization picks a point"', ha='center',
        fontsize=8, color=DIM, fontstyle='italic')

ax.text(x_su2r, y_label + 0.3, r'$\tau$ involution', ha='center', fontsize=11,
        color=GOLD_LT, fontweight='bold')
ax.text(x_su2r, y_label - 0.05, r'"actuality is real"', ha='center',
        fontsize=8, color=DIM, fontstyle='italic')

# ════════════════════════════════════════════
# LEVEL 3: Results of the two constraints
# ════════════════════════════════════════════
y3 = 6.2

# LEFT: SU(4)_C → SU(3)_C + U(1)_{B-L}
# Position these so they don't overlap with SU(2)_L
x_su3c = x_su4 - 1.0
x_u1bl = x_su4 + 1.0

arrow(x_su4 - 0.4, y_label - 0.25, x_su3c, y3 + 0.5, VIOLET, lw=1.5)
arrow(x_su4 + 0.4, y_label - 0.25, x_u1bl, y3 + 0.5, VIOLET, lw=1.5)

box(x_su3c, y3, r'SU(3)$_C$', VIOLET, w=2.0, h=0.65, fs=11, alpha=0.15, dim='dim 8')
box(x_u1bl, y3, r'U(1)$_{B\text{-}L}$', VIOLET, w=1.8, h=0.65, fs=11, alpha=0.1, dim='dim 1')
ax.text(x_su4, y3 - 0.55, r'6 generators broken', ha='center', fontsize=7.5,
        color=RED_DIM, fontstyle='italic', alpha=0.6)

# CENTER: SU(2)_L passes through
arrow(x_su2l, y2 - 0.5, x_su2l, y3 + 0.5, CYAN, lw=1.5)
box(x_su2l, y3, r'SU(2)$_L$', CYAN, w=2.0, h=0.65, fs=11, alpha=0.15, dim='dim 3')
ax.text(x_su2l, y3 - 0.55, 'survives intact', ha='center', fontsize=7.5,
        color=CYAN_DK, fontstyle='italic', alpha=0.6)

# RIGHT: SU(2)_R → U(1)_R
arrow(x_su2r, y_label - 0.25, x_su2r, y3 + 0.5, GOLD, lw=1.5)
box(x_su2r, y3, r'U(1)$_R$', GOLD, w=2.0, h=0.65, fs=11, alpha=0.1, dim='dim 1')
ax.text(x_su2r, y3 - 0.55, r'2 generators broken', ha='center', fontsize=7.5,
        color=RED_DIM, fontstyle='italic', alpha=0.6)

# ════════════════════════════════════════════
# U(1) combination: U(1)_{B-L} + U(1)_R → U(1)_Y
# ════════════════════════════════════════════
y_comb = 5.0

# Arrows from the two U(1)s converging
x_u1y = (x_u1bl + x_su2r) / 2
arrow(x_u1bl, y3 - 0.5, x_u1y, y_comb + 0.42, VIOLET, lw=1.2)
arrow(x_su2r, y3 - 0.5, x_u1y, y_comb + 0.42, GOLD, lw=1.2)

box(x_u1y, y_comb, r'U(1)$_Y$', CYAN, w=1.8, h=0.65, fs=11, alpha=0.15, dim='dim 1')
ax.text(x_u1y, y_comb - 0.52, r'$Y = \frac{B\text{-}L}{2} + T_{3R}$', ha='center',
        fontsize=9, color=WHITE, fontfamily='serif', alpha=0.8)

# ════════════════════════════════════════════
# LEVEL 4: Standard Model assembly
# ════════════════════════════════════════════
y4 = 3.5

arrow(x_su3c, y3 - 0.5, -1.0, y4 + 0.55, VIOLET, lw=1.3)
arrow(x_su2l, y3 - 0.5, 0.2, y4 + 0.55, CYAN, lw=1.3)
arrow(x_u1y, y_comb - 0.52, 1.2, y4 + 0.55, CYAN, lw=1.3)

box(0, y4, r'SU(3)$_C$ × SU(2)$_L$ × U(1)$_Y$', CYAN, w=6.0, h=0.75,
    fs=14, alpha=0.3, dim='dim 12')
ax.text(0, y4 - 0.6, 'Standard Model', ha='center', fontsize=12,
        color=CYAN, fontweight='bold')

# ════════════════════════════════════════════
# EWSB: SU(2)_L × U(1)_Y → U(1)_em  (intermediate box)
# ════════════════════════════════════════════
y_ewsb = 2.3
arrow(0, y4 - 0.6, 0, y_ewsb + 0.55, DIM_LT, lw=1.3)
ax.text(0.3, y4 - 1.0, r'EWSB: SU(2)$_L$ × U(1)$_Y$ $\to$ U(1)$_{\rm em}$',
        ha='left', fontsize=8.5, color=DIM_LT, fontstyle='italic')

box(0, y_ewsb, r'SU(3)$_C$ × U(1)$_{\rm em}$', CYAN, w=5.0, h=0.65,
    fs=12, alpha=0.12, dim='dim 9')
ax.text(0, y_ewsb - 0.52, r'$Q = T_{3L} + Y/2$', ha='center',
        fontsize=9, color=WHITE, fontfamily='serif', alpha=0.7)

# ════════════════════════════════════════════
# Confinement: SU(3)_C → confined → U(1)_em
# ════════════════════════════════════════════
y6 = 0.5
arrow(0, y_ewsb - 0.52, 0, y6 + 0.5, DIM_LT, lw=1.0)
ax.text(0.3, y_ewsb - 0.95, r'color confinement: $\alpha_s \to 1$',
        ha='left', fontsize=8.5, color=DIM_LT, fontstyle='italic')

box(0, y6, r'U(1)$_{\rm em}$  —  classical electromagnetism', GOLD,
    w=5.5, h=0.65, fs=11, alpha=0.1, dim='dim 1')

# ── Faint arcs ──
for r, a in [(8, 0.02), (10, 0.015), (12, 0.01)]:
    arc = plt.Circle((0, y1 + 2), r, facecolor='none', edgecolor=VIOLET,
                      alpha=a, linewidth=1, zorder=0)
    ax.add_patch(arc)

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=200, facecolor=BG, bbox_inches='tight', pad_inches=0.3)
plt.close()
print(f"Saved: {OUTPUT_PATH}")

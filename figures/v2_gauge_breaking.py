"""
Gauge symmetry breaking chain — computed schematic.

Generates the PSU(4) → Pati-Salam → SM → confinement cascade figure.
Layout: SO(4) [SU(2)_L × SU(2)_R] on left, SU(4)_C on right at PS level.
U(1)_R and U(1)_{B-L} adjacent at level 3 for clean arrow layout.

Usage:
    python v2_gauge_breaking.py              # ontology version (dark BG)
    python v2_gauge_breaking.py --technical  # technical version (_style.py palette)
"""
import os
import sys
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
OUTPUT_DIR = os.path.join(REPO_ROOT, 'figures', 'computed')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Color themes ──
THEMES = {
    'ontology': {
        'BG':      '#0d1117',
        'VIOLET':  '#7B68EE',
        'CYAN':    '#00CED1',
        'GOLD':    '#D4A843',
        'WHITE':   '#f0f0f0',
        'DIM':     '#888888',
        'DIM_LT':  '#aaaaaa',
        'VIO_LT':  '#C4B8FF',
        'GOLD_LT': '#F0D880',
        'CYAN_DK': '#00BBBB',
        'CYAN_LT': '#40E8E0',
        'RED_DIM': '#DD6666',
        'SM_RING': '#FFD27F',
        'output':  'v2_gauge_breaking.png',
    },
    'technical': {
        'BG':      '#040812',
        'VIOLET':  '#7B68EE',
        'CYAN':    '#00CED1',
        'GOLD':    '#D4A843',
        'WHITE':   '#f0f0f0',
        'DIM':     '#888888',
        'DIM_LT':  '#aaaaaa',
        'VIO_LT':  '#C4B8FF',
        'GOLD_LT': '#F0D880',
        'CYAN_DK': '#00BBBB',
        'CYAN_LT': '#40E8E0',
        'RED_DIM': '#DD6666',
        'SM_RING': '#FFD27F',
        'output':  'v2_gauge_breaking_tech.png',
    },
}


def main():
    parser = argparse.ArgumentParser(description='Generate gauge breaking chain figure')
    parser.add_argument('--technical', action='store_true',
                        help='Use technical document color palette')
    args = parser.parse_args()

    theme_name = 'technical' if args.technical else 'ontology'
    T = THEMES[theme_name]
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, T['output'])

    BG      = T['BG']
    VIOLET  = T['VIOLET']
    CYAN    = T['CYAN']
    GOLD    = T['GOLD']
    WHITE   = T['WHITE']
    DIM     = T['DIM']
    DIM_LT  = T['DIM_LT']
    VIO_LT  = T['VIO_LT']
    GOLD_LT = T['GOLD_LT']
    CYAN_DK = T['CYAN_DK']
    CYAN_LT = T['CYAN_LT']
    RED_DIM = T['RED_DIM']
    SM_RING = T['SM_RING']

    LABEL_BG = dict(boxstyle='round,pad=0.08', facecolor=BG, edgecolor='none',
                    alpha=0.85)

    fig, ax = plt.subplots(figsize=(18, 16), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-9.5, 11)
    ax.set_ylim(-0.5, 14)
    ax.axis('off')

    BOX_H = 0.90
    BOX_FS = 20

    def box(x, y, text, color, w=4.5, h=BOX_H, fs=BOX_FS, alpha=0.2,
            tc=WHITE, lw=2.0, dim=None, glow=False, sm=False):
        # Glow effect
        if glow:
            for i in range(3):
                pad = 0.05 + i * 0.06
                g = FancyBboxPatch((x-w/2-pad, y-h/2-pad), w+2*pad, h+2*pad,
                                   boxstyle="round,pad=0.12",
                                   facecolor=color, edgecolor='none',
                                   alpha=0.04*(3-i), lw=0, zorder=1)
                ax.add_patch(g)

        b = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.12",
                            facecolor=color, edgecolor='none', alpha=alpha,
                            lw=0, zorder=2)
        ax.add_patch(b)
        border = FancyBboxPatch((x-w/2, y-h/2), w, h,
                                 boxstyle="round,pad=0.12",
                                 facecolor='none', edgecolor=color,
                                 alpha=0.7, lw=lw, zorder=3)
        ax.add_patch(border)
        # SM gauge-factor outer ring
        if sm:
            pad_sm = 0.13
            sm_outer = FancyBboxPatch((x-w/2-pad_sm, y-h/2-pad_sm),
                                       w + 2*pad_sm, h + 2*pad_sm,
                                       boxstyle="round,pad=0.12",
                                       facecolor='none', edgecolor=SM_RING,
                                       alpha=0.95, lw=3.2, zorder=3.5)
            ax.add_patch(sm_outer)
        if dim:
            ax.text(x, y + 0.14, text, ha='center', va='center', fontsize=fs,
                    color=tc, fontfamily='serif', zorder=4,
                    fontweight='bold')
            ax.text(x, y - 0.22, dim, ha='center', va='center',
                    fontsize=max(fs - 4, 13), color=DIM_LT, fontfamily='serif',
                    zorder=4)
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=fs,
                    color=tc, fontfamily='serif', zorder=4,
                    fontweight='bold')

    def arrow(x0, y0, x1, y1, color, lw=2.2):
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                    mutation_scale=18, alpha=0.75))

    def label(x, y, text, color, fs=15, ha='center', style='italic',
              alpha=0.9, weight='normal', bg=True):
        kw = dict(ha=ha, va='center', fontsize=fs, color=color,
                  fontstyle=style, fontweight=weight, zorder=5)
        if bg:
            kw['bbox'] = LABEL_BG
        ax.text(x, y, text, **kw)

    # ── k-scale on left margin ──
    kx = -8.0
    ax.plot([kx, kx], [0.3, 13.2], color=DIM, lw=2.0, alpha=0.6, zorder=0)
    ax.text(kx, 13.6, '$k$', ha='center', fontsize=28, color=DIM_LT,
            fontweight='bold')

    k_ticks = [
        (13.0, '$k \\approx 1$\nPlanck', VIOLET),
        (11.0, '$k \\approx 16$', CYAN),
        (5.0,  '$k \\approx 44.5$', CYAN),
        (3.0,  '$k \\approx 44.5$', CYAN_DK),
        (1.0,  '$k \\approx 51$', GOLD),
    ]
    for y, lbl, clr in k_ticks:
        ax.plot([kx - 0.2, kx + 0.2], [y, y], color=clr, lw=2.5, alpha=0.8)
        ax.text(kx - 0.5, y - 0.5, lbl, ha='right', va='center', fontsize=20,
                color=clr, alpha=0.95, fontweight='bold')

    # ════════════════════════════════════════════
    # Layout coordinates
    # ════════════════════════════════════════════
    y1 = 13.0
    y2 = 11.0

    x_su2l = -2.8
    x_su2r = 1.2
    x_su4  = 5.8

    ps_x0 = x_su2l - 2.2
    ps_x1 = x_su4 + 2.4
    ps_w = ps_x1 - ps_x0
    ps_cx = (ps_x0 + ps_x1) / 2

    # Background texture
    import numpy as np
    for r in np.linspace(1, 18, 35):
        c = plt.Circle((ps_cx, 7), r, facecolor='none',
                        edgecolor=VIOLET, alpha=0.006, lw=0.8, zorder=0)
        ax.add_patch(c)

    # ════════════════════════════════════════════
    # PPM-derived vs Standard Model zone demarcation
    # ════════════════════════════════════════════
    DIVIDER_Y = 7.05
    zone_x0 = -7.0
    zone_x1 = 10.2

    ppm_zone = FancyBboxPatch((zone_x0, DIVIDER_Y + 0.05),
                                zone_x1 - zone_x0,
                                14.0 - DIVIDER_Y - 0.05,
                                boxstyle="round,pad=0.05",
                                facecolor=VIOLET, edgecolor='none',
                                alpha=0.05, lw=0, zorder=0.15)
    ax.add_patch(ppm_zone)

    sm_zone = FancyBboxPatch((zone_x0, -0.4),
                              zone_x1 - zone_x0,
                              (DIVIDER_Y - 0.05) - (-0.4),
                              boxstyle="round,pad=0.05",
                              facecolor=GOLD, edgecolor='none',
                              alpha=0.05, lw=0, zorder=0.15)
    ax.add_patch(sm_zone)

    ax.plot([zone_x0 + 0.4, zone_x1 - 0.4], [DIVIDER_Y, DIVIDER_Y],
            color=DIM_LT, lw=1.2, alpha=0.5, linestyle='--', zorder=0.25)

    # Zone labels — placed in the left-margin whitespace between the k-scale
    # and the leftmost boxes, aligned to the divider
    ax.text(zone_x0 + 0.35, DIVIDER_Y + 0.32,
            'PPM-derived', ha='left', va='bottom',
            fontsize=15, color=VIO_LT, fontweight='bold', alpha=0.95,
            fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.22', facecolor=BG,
                      edgecolor=VIO_LT, alpha=0.95, lw=1.0), zorder=4)
    ax.text(zone_x0 + 0.35, DIVIDER_Y - 0.32,
            'Standard Model', ha='left', va='top',
            fontsize=15, color=GOLD_LT, fontweight='bold', alpha=0.95,
            fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.22', facecolor=BG,
                      edgecolor=GOLD_LT, alpha=0.95, lw=1.0), zorder=4)

    # ════════════════════════════════════════════
    # LEVEL 1: PSU(4)
    # ════════════════════════════════════════════
    box(ps_cx, y1, r'PSU(4)  —  full arena isometry', VIOLET, w=ps_w, h=1.0,
        fs=22, alpha=0.25, dim='dim 15', glow=True)

    # Arrow → SO(4)
    so4_cx = (x_su2l + x_su2r) / 2
    arrow(so4_cx, y1 - 0.6, so4_cx, 11.85, DIM_LT, lw=1.8)
    label(so4_cx - 0.5, 12.2,
          r'tangent/normal split reveals SO(4) structure',
          DIM_LT, fs=14, ha='right')

    # ════════════════════════════════════════════
    # LEVEL 2: Pati-Salam
    # ════════════════════════════════════════════
    ps_band = FancyBboxPatch((ps_x0, y2 - 0.85), ps_w, 1.7,
                              boxstyle="round,pad=0.14",
                              facecolor=CYAN, edgecolor=CYAN, alpha=0.06,
                              lw=0, zorder=0.5)
    ax.add_patch(ps_band)
    ps_border = FancyBboxPatch((ps_x0, y2 - 0.85), ps_w, 1.7,
                                boxstyle="round,pad=0.14",
                                facecolor='none', edgecolor=CYAN, alpha=0.4,
                                lw=1.5, linestyle='--', zorder=0.5)
    ax.add_patch(ps_border)

    ax.text(ps_x1 + 0.4, y2 + 0.2, 'Pati-Salam', ha='left', fontsize=20,
            color=CYAN, fontweight='bold')
    ax.text(ps_x1 + 0.4, y2 - 0.25, 'dim 21', ha='left', fontsize=16,
            color=CYAN, alpha=0.7)

    # SO(4) grouping
    so4_w = (x_su2r - x_su2l) + 3.0
    so4_h = 1.3
    so4_band = FancyBboxPatch((so4_cx - so4_w/2, y2 - so4_h/2), so4_w, so4_h,
                               boxstyle="round,pad=0.1",
                               facecolor=GOLD, edgecolor=GOLD, alpha=0.04,
                               lw=0, zorder=1)
    ax.add_patch(so4_band)
    so4_border = FancyBboxPatch((so4_cx - so4_w/2, y2 - so4_h/2), so4_w,
                                 so4_h, boxstyle="round,pad=0.1",
                                 facecolor='none', edgecolor=GOLD, alpha=0.5,
                                 lw=1.5, linestyle=':', zorder=1)
    ax.add_patch(so4_border)
    ax.text(so4_cx, y2 + so4_h/2 + 0.18,
            r'SO(4) $\cong$ SU(2)$_L$ $\times$ SU(2)$_R$',
            ha='center', fontsize=16, color=GOLD_LT, alpha=0.9)
    ax.text(so4_cx, y2 - so4_h/2 - 0.18, 'dim 6', ha='center', fontsize=14,
            color=GOLD, alpha=0.7)

    box(x_su2l, y2, r'SU(2)$_L$', CYAN, w=2.8, h=0.95, fs=22, alpha=0.18,
        dim='dim 3', glow=True)
    box(x_su2r, y2, r'SU(2)$_R$', GOLD, w=2.8, h=0.95, fs=22, alpha=0.18,
        dim='dim 3', glow=True)
    box(x_su4, y2, r'SU(4)$_C$', VIOLET, w=3.5, h=0.95, fs=22, alpha=0.18,
        dim='dim 15', glow=True)

    ax.text((x_su2l + x_su2r) / 2, y2, r'$\times$', ha='center',
            va='center', fontsize=22, color=DIM_LT, fontweight='bold')
    ax.text((x_su2r + x_su4) / 2, y2, r'$\times$', ha='center',
            va='center', fontsize=22, color=DIM_LT, fontweight='bold')

    # ════════════════════════════════════════════
    # Constraint labels
    # ════════════════════════════════════════════
    y_label = 9.5

    label(x_su2r, y_label + 0.35, r'$\tau$ involution', GOLD_LT, fs=18,
          weight='bold', style='normal', bg=False)
    label(x_su2r, y_label - 0.15, r'"actuality is real"', DIM, fs=14,
          bg=False)

    label(x_su4, y_label + 0.35, r'Isotropy at $p$', VIO_LT, fs=18,
          weight='bold', style='normal', bg=False)
    label(x_su4, y_label - 0.15, r'"actualization picks a point"', DIM,
          fs=14, bg=False)

    # ════════════════════════════════════════════
    # LEVEL 3: Constraint results
    # ════════════════════════════════════════════
    y3 = 8.0

    x_su2l_3 = x_su2l
    x_u1r    = 0.6
    x_u1bl   = 3.8
    x_su3c   = 7.0

    # SU(2)_L passes through
    arrow(x_su2l, y2 - 0.55, x_su2l_3, y3 + 0.55, CYAN, lw=1.8)
    box(x_su2l_3, y3, r'SU(2)$_L$', CYAN, w=2.8, h=BOX_H, fs=BOX_FS,
        alpha=0.18, dim='dim 3', glow=True, sm=True)
    label(x_su2l_3, y3 - 0.72, 'survives intact', CYAN_DK, fs=14)

    # SU(2)_R → U(1)_R
    arrow(x_su2r, y_label - 0.3, x_u1r, y3 + 0.55, GOLD, lw=1.8)
    box(x_u1r, y3, r'U(1)$_R$', GOLD, w=2.4, h=BOX_H, fs=BOX_FS, alpha=0.12,
        dim='dim 1', glow=True)
    label(x_u1r, y3 - 0.72, r'2 gen. broken', RED_DIM, fs=14)

    # SU(4)_C → U(1)_{B-L} + SU(3)_C
    arrow(x_su4 - 0.5, y_label - 0.3, x_u1bl, y3 + 0.55, VIOLET, lw=1.8)
    arrow(x_su4 + 0.5, y_label - 0.3, x_su3c, y3 + 0.55, VIOLET, lw=1.8)

    box(x_u1bl, y3, r'U(1)$_{B\text{-}L}$', VIOLET, w=2.6, h=BOX_H,
        fs=BOX_FS, alpha=0.12, dim='dim 1', glow=True)
    box(x_su3c, y3, r'SU(3)$_C$', VIOLET, w=2.8, h=BOX_H, fs=BOX_FS,
        alpha=0.18, dim='dim 8', glow=True, sm=True)
    label((x_u1bl + x_su3c) / 2, y3 - 0.72, r'6 gen. broken', RED_DIM, fs=14)

    # ════════════════════════════════════════════
    # U(1)_Y combination
    # ════════════════════════════════════════════
    y_u1y = 6.5
    x_u1y = (x_u1r + x_u1bl) / 2

    arrow(x_u1r, y3 - 0.55, x_u1y - 0.15, y_u1y + 0.5, GOLD, lw=1.5)
    arrow(x_u1bl, y3 - 0.55, x_u1y + 0.15, y_u1y + 0.5, VIOLET, lw=1.5)

    box(x_u1y, y_u1y, r'U(1)$_Y$', CYAN, w=2.2, h=BOX_H, fs=BOX_FS,
        alpha=0.18, dim='dim 1', glow=True, sm=True)
    label(x_u1y, y_u1y - 0.65,
          r'$Y = \frac{B\text{-}L}{2} + T_{3R}$',
          WHITE, fs=16, style='normal')

    # ════════════════════════════════════════════
    # EWSB: SU(2)_L + U(1)_Y → U(1)_em
    # ════════════════════════════════════════════
    y_u1em = 5.0
    x_u1em = (x_su2l_3 + x_u1y) / 2

    arrow(x_su2l_3, y3 - 0.55, x_u1em - 0.3, y_u1em + 0.5, CYAN, lw=1.8)
    arrow(x_u1y, y_u1y - 0.6, x_u1em + 0.3, y_u1em + 0.5, CYAN, lw=1.8)

    box(x_u1em, y_u1em, r'U(1)$_{\rm em}$', GOLD, w=2.2, h=BOX_H,
        fs=BOX_FS, alpha=0.18, dim='dim 1', glow=True, sm=True)
    label(x_u1em, y_u1em - 0.65, r'$Q = T_{3L} + Y/2$',
          WHITE, fs=16, style='normal')

    label(x_u1em + 2.5, y_u1em + 0.3, r'EWSB', DIM_LT, fs=18,
          ha='left', weight='bold', style='normal', bg=False)
    label(x_u1em + 2.5, y_u1em - 0.15,
          r'SU(2)$_L$ × U(1)$_Y$ $\to$ U(1)$_{\rm em}$',
          DIM_LT, fs=14, ha='left', bg=False)
    label(x_u1em + 2.5, y_u1em - 0.5, r'3 gen. broken',
          RED_DIM, fs=14, ha='left', bg=False)

    # ════════════════════════════════════════════
    # LEVEL 4: SU(3)_C × U(1)_em
    # ════════════════════════════════════════════
    y4 = 3.0
    x_sm = (x_su3c + x_u1em) / 2

    arrow(x_su3c, y3 - 0.55, x_sm + 0.8, y4 + 0.55, VIOLET, lw=1.8)
    arrow(x_u1em, y_u1em - 0.6, x_sm - 0.5, y4 + 0.55, GOLD, lw=1.8)

    box(x_sm, y4, r'SU(3)$_C$ × U(1)$_{\rm em}$', CYAN, w=5.0, h=1.0,
        fs=21, alpha=0.22, dim='dim 9', glow=True, sm=True)

    # ════════════════════════════════════════════
    # Confinement → U(1)_em
    # ════════════════════════════════════════════
    y6 = 1.0
    arrow(x_sm, y4 - 0.6, x_sm, y6 + 0.55, DIM_LT, lw=1.5)
    label(x_sm + 0.5, y4 - 1.1,
          r'color confinement: $\alpha_s \to 1$',
          DIM_LT, fs=14, ha='left')

    box(x_sm, y6, r'U(1)$_{\rm em}$  —  classical EM', GOLD,
        w=5.0, h=1.0, fs=20, alpha=0.15, dim='dim 1', glow=True, sm=True)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200, facecolor=BG, bbox_inches='tight',
                pad_inches=0.4)
    plt.close()
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()

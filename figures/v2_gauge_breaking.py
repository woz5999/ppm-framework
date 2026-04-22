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
        'WHITE':   '#eeeeee',
        'DIM':     '#888888',
        'DIM_LT':  '#999999',
        'VIO_LT':  '#B0A0FF',
        'GOLD_LT': '#F0D880',
        'CYAN_DK': '#00BBBB',
        'RED_DIM': '#DD6666',
        'output':  'v2_gauge_breaking.png',
    },
    'technical': {
        'BG':      '#040812',
        'VIOLET':  '#7B68EE',
        'CYAN':    '#00CED1',
        'GOLD':    '#D4A843',
        'WHITE':   '#eeeeee',
        'DIM':     '#888888',
        'DIM_LT':  '#999999',
        'VIO_LT':  '#B0A0FF',
        'GOLD_LT': '#F0D880',
        'CYAN_DK': '#00BBBB',
        'RED_DIM': '#DD6666',
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
    RED_DIM = T['RED_DIM']

    LABEL_BG = dict(boxstyle='round,pad=0.08', facecolor=BG, edgecolor='none',
                    alpha=0.85)

    fig, ax = plt.subplots(figsize=(14, 14), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-7.5, 8.5)
    ax.set_ylim(-0.5, 14)
    ax.axis('off')

    BOX_H = 0.75
    BOX_FS = 15

    def box(x, y, text, color, w=4.2, h=BOX_H, fs=BOX_FS, alpha=0.2,
            tc=WHITE, lw=1.5, dim=None):
        b = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.1",
                            facecolor=color, edgecolor=color, alpha=alpha,
                            lw=lw, zorder=2)
        ax.add_patch(b)
        border = FancyBboxPatch((x-w/2, y-h/2), w, h,
                                 boxstyle="round,pad=0.1",
                                 facecolor='none', edgecolor=color,
                                 alpha=0.55, lw=lw, zorder=3)
        ax.add_patch(border)
        if dim:
            ax.text(x, y + 0.1, text, ha='center', va='center', fontsize=fs,
                    color=tc, fontfamily='serif', zorder=4,
                    fontweight='medium')
            ax.text(x, y - 0.18, dim, ha='center', va='center',
                    fontsize=max(fs - 2, 11), color=DIM_LT, fontfamily='serif',
                    zorder=4)
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=fs,
                    color=tc, fontfamily='serif', zorder=4,
                    fontweight='medium')

    def arrow(x0, y0, x1, y1, color, lw=1.8):
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='->', color=color, lw=lw))

    def label(x, y, text, color, fs=12, ha='center', style='italic',
              alpha=0.9, weight='normal', bg=True):
        kw = dict(ha=ha, va='center', fontsize=fs, color=color,
                  fontstyle=style, fontweight=weight, zorder=5)
        if bg:
            kw['bbox'] = LABEL_BG
        ax.text(x, y, text, **kw)

    # ── k-scale on left margin ──
    kx = -6.8
    ax.plot([kx, kx], [0.3, 13.2], color=DIM, lw=1.2, alpha=0.5, zorder=0)
    ax.text(kx, 13.5, '$k$', ha='center', fontsize=14, color=DIM_LT)

    k_ticks = [
        (13.0, '$k \\approx 1$\nPlanck', VIOLET),
        (11.0, '$k \\approx 16$', CYAN),
        (5.0,  '$k \\approx 44.5$', CYAN),
        (3.0,  '$k \\approx 44.5$', CYAN_DK),
        (1.0,  '$k \\approx 51$', GOLD),
    ]
    for y, lbl, clr in k_ticks:
        ax.plot([kx - 0.15, kx + 0.15], [y, y], color=clr, lw=1.5, alpha=0.7)
        ax.text(kx - 0.3, y, lbl, ha='right', va='center', fontsize=11,
                color=clr, alpha=0.9)

    # ════════════════════════════════════════════
    # Layout coordinates
    # ════════════════════════════════════════════
    y1 = 13.0
    y2 = 11.0

    x_su2l = -2.5
    x_su2r = 0.8
    x_su4  = 4.8

    ps_x0 = x_su2l - 1.6
    ps_x1 = x_su4 + 1.8
    ps_w = ps_x1 - ps_x0
    ps_cx = (ps_x0 + ps_x1) / 2

    # ════════════════════════════════════════════
    # LEVEL 1: PSU(4)
    # ════════════════════════════════════════════
    box(ps_cx, y1, r'PSU(4)  —  full arena isometry', VIOLET, w=ps_w, h=0.85,
        fs=17, alpha=0.2, dim='dim 15')

    # Arrow → SO(4)
    so4_cx = (x_su2l + x_su2r) / 2
    arrow(so4_cx, y1 - 0.6, so4_cx, 11.85, DIM_LT, lw=1.5)
    label(so4_cx - 0.5, 12.2,
          r'tangent/normal split reveals SO(4) structure',
          DIM_LT, fs=12, ha='right')

    # ════════════════════════════════════════════
    # LEVEL 2: Pati-Salam
    # ════════════════════════════════════════════
    # PS background band
    ps_band = FancyBboxPatch((ps_x0, y2 - 0.8), ps_w, 1.6,
                              boxstyle="round,pad=0.12",
                              facecolor=CYAN, edgecolor=CYAN, alpha=0.05,
                              lw=0, zorder=0.5)
    ax.add_patch(ps_band)
    ps_border = FancyBboxPatch((ps_x0, y2 - 0.8), ps_w, 1.6,
                                boxstyle="round,pad=0.12",
                                facecolor='none', edgecolor=CYAN, alpha=0.35,
                                lw=1.2, linestyle='--', zorder=0.5)
    ax.add_patch(ps_border)

    ax.text(ps_x1 + 0.3, y2 + 0.2, 'Pati-Salam', ha='left', fontsize=16,
            color=CYAN, fontweight='bold')
    ax.text(ps_x1 + 0.3, y2 - 0.2, 'dim 21', ha='left', fontsize=13,
            color=CYAN, alpha=0.7)

    # SO(4) grouping
    so4_w = (x_su2r - x_su2l) + 2.8
    so4_h = 1.2
    so4_band = FancyBboxPatch((so4_cx - so4_w/2, y2 - so4_h/2), so4_w, so4_h,
                               boxstyle="round,pad=0.1",
                               facecolor=GOLD, edgecolor=GOLD, alpha=0.04,
                               lw=0, zorder=1)
    ax.add_patch(so4_band)
    so4_border = FancyBboxPatch((so4_cx - so4_w/2, y2 - so4_h/2), so4_w,
                                 so4_h, boxstyle="round,pad=0.1",
                                 facecolor='none', edgecolor=GOLD, alpha=0.4,
                                 lw=1.2, linestyle=':', zorder=1)
    ax.add_patch(so4_border)
    ax.text(so4_cx, y2 + so4_h/2 + 0.15,
            r'SO(4) $\cong$ SU(2)$_L$ $\times$ SU(2)$_R$',
            ha='center', fontsize=13, color=GOLD_LT, alpha=0.9)
    ax.text(so4_cx, y2 - so4_h/2 - 0.15, 'dim 6', ha='center', fontsize=12,
            color=GOLD, alpha=0.7)

    box(x_su2l, y2, r'SU(2)$_L$', CYAN, w=2.2, h=0.85, fs=17, alpha=0.15,
        dim='dim 3')
    box(x_su2r, y2, r'SU(2)$_R$', GOLD, w=2.2, h=0.85, fs=17, alpha=0.15,
        dim='dim 3')
    box(x_su4, y2, r'SU(4)$_C$', VIOLET, w=3.0, h=0.85, fs=17, alpha=0.15,
        dim='dim 15')

    ax.text((x_su2l + x_su2r) / 2, y2, r'$\times$', ha='center',
            va='center', fontsize=18, color=DIM_LT)
    ax.text((x_su2r + x_su4) / 2, y2, r'$\times$', ha='center',
            va='center', fontsize=18, color=DIM_LT)

    # ════════════════════════════════════════════
    # Constraint labels
    # ════════════════════════════════════════════
    y_label = 9.5

    label(x_su2r, y_label + 0.35, r'$\tau$ involution', GOLD_LT, fs=15,
          weight='bold', style='normal', bg=False)
    label(x_su2r, y_label - 0.15, r'"actuality is real"', DIM, fs=12,
          bg=False)

    label(x_su4, y_label + 0.35, r'Isotropy at $p$', VIO_LT, fs=15,
          weight='bold', style='normal', bg=False)
    label(x_su4, y_label - 0.15, r'"actualization picks a point"', DIM,
          fs=12, bg=False)

    # ════════════════════════════════════════════
    # LEVEL 3: Constraint results
    # ════════════════════════════════════════════
    y3 = 8.0

    x_su2l_3 = x_su2l
    x_u1r    = 0.4
    x_u1bl   = 3.2
    x_su3c   = 5.8

    # SU(2)_L passes through
    arrow(x_su2l, y2 - 0.55, x_su2l_3, y3 + 0.55, CYAN, lw=1.5)
    box(x_su2l_3, y3, r'SU(2)$_L$', CYAN, w=2.2, h=BOX_H, fs=BOX_FS,
        alpha=0.15, dim='dim 3')
    label(x_su2l_3, y3 - 0.62, 'survives intact', CYAN_DK, fs=12)

    # SU(2)_R → U(1)_R
    arrow(x_su2r, y_label - 0.3, x_u1r, y3 + 0.55, GOLD, lw=1.5)
    box(x_u1r, y3, r'U(1)$_R$', GOLD, w=1.8, h=BOX_H, fs=BOX_FS, alpha=0.1,
        dim='dim 1')
    label(x_u1r, y3 - 0.62, r'2 gen. broken', RED_DIM, fs=12)

    # SU(4)_C → U(1)_{B-L} + SU(3)_C
    arrow(x_su4 - 0.5, y_label - 0.3, x_u1bl, y3 + 0.55, VIOLET, lw=1.5)
    arrow(x_su4 + 0.5, y_label - 0.3, x_su3c, y3 + 0.55, VIOLET, lw=1.5)

    box(x_u1bl, y3, r'U(1)$_{B\text{-}L}$', VIOLET, w=1.8, h=BOX_H,
        fs=BOX_FS, alpha=0.1, dim='dim 1')
    box(x_su3c, y3, r'SU(3)$_C$', VIOLET, w=2.2, h=BOX_H, fs=BOX_FS,
        alpha=0.15, dim='dim 8')
    label((x_u1bl + x_su3c) / 2, y3 - 0.62, r'6 gen. broken', RED_DIM, fs=12)

    # ════════════════════════════════════════════
    # U(1)_Y combination
    # ════════════════════════════════════════════
    y_u1y = 6.5
    x_u1y = (x_u1r + x_u1bl) / 2

    arrow(x_u1r, y3 - 0.55, x_u1y - 0.15, y_u1y + 0.5, GOLD, lw=1.3)
    arrow(x_u1bl, y3 - 0.55, x_u1y + 0.15, y_u1y + 0.5, VIOLET, lw=1.3)

    box(x_u1y, y_u1y, r'U(1)$_Y$', CYAN, w=2.0, h=BOX_H, fs=BOX_FS,
        alpha=0.15, dim='dim 1')
    label(x_u1y, y_u1y - 0.6,
          r'$Y = \frac{B\text{-}L}{2} + T_{3R}$',
          WHITE, fs=13, style='normal')

    # ════════════════════════════════════════════
    # EWSB: SU(2)_L + U(1)_Y → U(1)_em
    # ════════════════════════════════════════════
    y_u1em = 5.0
    x_u1em = (x_su2l_3 + x_u1y) / 2

    arrow(x_su2l_3, y3 - 0.55, x_u1em - 0.3, y_u1em + 0.5, CYAN, lw=1.5)
    arrow(x_u1y, y_u1y - 0.6, x_u1em + 0.3, y_u1em + 0.5, CYAN, lw=1.5)

    box(x_u1em, y_u1em, r'U(1)$_{\rm em}$', GOLD, w=2.0, h=BOX_H,
        fs=BOX_FS, alpha=0.15, dim='dim 1')
    label(x_u1em, y_u1em - 0.6, r'$Q = T_{3L} + Y/2$',
          WHITE, fs=13, style='normal')

    label(x_u1em + 2.2, y_u1em + 0.3, r'EWSB', DIM_LT, fs=14,
          ha='left', weight='bold', style='normal', bg=False)
    label(x_u1em + 2.2, y_u1em - 0.15,
          r'SU(2)$_L$ × U(1)$_Y$ $\to$ U(1)$_{\rm em}$',
          DIM_LT, fs=12, ha='left', bg=False)
    label(x_u1em + 2.2, y_u1em - 0.5, r'3 gen. broken',
          RED_DIM, fs=12, ha='left', bg=False)

    # ════════════════════════════════════════════
    # LEVEL 4: SU(3)_C × U(1)_em
    # ════════════════════════════════════════════
    y4 = 3.0
    x_sm = (x_su3c + x_u1em) / 2

    arrow(x_su3c, y3 - 0.55, x_sm + 0.8, y4 + 0.55, VIOLET, lw=1.5)
    arrow(x_u1em, y_u1em - 0.6, x_sm - 0.5, y4 + 0.55, GOLD, lw=1.5)

    box(x_sm, y4, r'SU(3)$_C$ × U(1)$_{\rm em}$', CYAN, w=4.5, h=0.85,
        fs=16, alpha=0.2, dim='dim 9')

    # ════════════════════════════════════════════
    # Confinement → U(1)_em
    # ════════════════════════════════════════════
    y6 = 1.0
    arrow(x_sm, y4 - 0.6, x_sm, y6 + 0.55, DIM_LT, lw=1.2)
    label(x_sm + 0.4, y4 - 1.1,
          r'color confinement: $\alpha_s \to 1$',
          DIM_LT, fs=12, ha='left')

    box(x_sm, y6, r'U(1)$_{\rm em}$  —  classical EM', GOLD,
        w=4.5, h=0.85, fs=15, alpha=0.12, dim='dim 1')

    # ── Faint arcs ──
    for r, a in [(8, 0.02), (10, 0.015), (12, 0.01)]:
        arc = plt.Circle((ps_cx, y1 + 2), r, facecolor='none',
                          edgecolor=VIOLET, alpha=a, linewidth=1, zorder=0)
        ax.add_patch(arc)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200, facecolor=BG, bbox_inches='tight',
                pad_inches=0.3)
    plt.close()
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()

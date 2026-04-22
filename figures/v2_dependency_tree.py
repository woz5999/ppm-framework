"""
v2_dependency_tree.py — PPM derivation dependency / self-consistency figure.

Central concept: three independent geometric quantities (g, α, φ/N_∞) are
derived from separate features of the CP³ embedding, then converge on a
single self-consistency relation (2π)^27 √α = φ^98. Physical constants
sit downstream. The figure shows convergence, not just hierarchy.

Layout:
  Top: CP³ + τ axiom
  Three independent derivation paths fan out (left, center, right)
  They converge at the self-consistency relation in the center
  Physical constants hang below as outputs

Usage:
    python v2_dependency_tree.py              # ontology version
    python v2_dependency_tree.py --technical  # technical version
"""
import os
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
OUTPUT_DIR = os.path.join(REPO_ROOT, 'figures', 'computed')
os.makedirs(OUTPUT_DIR, exist_ok=True)

THEMES = {
    'ontology': {
        'BG':      '#0d1117',
        'VIOLET':  '#7B68EE',
        'CYAN':    '#00CED1',
        'GOLD':    '#D4A843',
        'WHITE':   '#eeeeee',
        'DIM':     '#777777',
        'DIM_LT':  '#999999',
        'VIO_LT':  '#B0A0FF',
        'GOLD_LT': '#F0D880',
        'CYAN_DK': '#009999',
        'ARR':     '#bbbbbb',
        'output':  'v2_dependency_tree.png',
    },
    'technical': {
        'BG':      '#040812',
        'VIOLET':  '#7B68EE',
        'CYAN':    '#00CED1',
        'GOLD':    '#D4A843',
        'WHITE':   '#eeeeee',
        'DIM':     '#777777',
        'DIM_LT':  '#999999',
        'VIO_LT':  '#B0A0FF',
        'GOLD_LT': '#F0D880',
        'CYAN_DK': '#009999',
        'ARR':     '#bbbbbb',
        'output':  'v2_dependency_tree_tech.png',
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--technical', action='store_true')
    args = parser.parse_args()

    T = THEMES['technical' if args.technical else 'ontology']
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
    ARR     = T['ARR']

    # ════════════════════════════════════════════
    # Canvas
    # ════════════════════════════════════════════
    fig, ax = plt.subplots(figsize=(14, 14), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-7, 7)
    ax.set_ylim(-1, 13)
    ax.axis('off')

    # ════════════════════════════════════════════
    # Drawing helpers
    # ════════════════════════════════════════════
    def draw_box(x, y, text, color, w=3.2, h=0.80, fs=15, alpha=0.18,
                 tc=WHITE, lw=1.4, sub=None, sub_color=None, sub_fs=11):
        b = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle="round,pad=0.10",
                           facecolor=color, edgecolor=color,
                           alpha=alpha, lw=lw, zorder=2)
        ax.add_patch(b)
        border = FancyBboxPatch((x - w/2, y - h/2), w, h,
                                boxstyle="round,pad=0.10",
                                facecolor='none', edgecolor=color,
                                alpha=0.55, lw=lw, zorder=3)
        ax.add_patch(border)
        if sub:
            ax.text(x, y + 0.14, text, ha='center', va='center', fontsize=fs,
                    color=tc, fontfamily='serif', fontweight='medium', zorder=4)
            ax.text(x, y - 0.19, sub, ha='center', va='center',
                    fontsize=sub_fs, color=sub_color or DIM_LT,
                    fontfamily='serif', zorder=4)
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=fs,
                    color=tc, fontfamily='serif', fontweight='medium', zorder=4)

    def arr(x0, y0, x1, y1, color=ARR, lw=1.3, dashed=False):
        style = 'dashed' if dashed else 'solid'
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='->', color=color,
                                    lw=lw, linestyle=style, alpha=0.65))

    def curved_arr(x0, y0, x1, y1, color=ARR, lw=1.3, curve='arc3,rad=0.3'):
        """Curved arrow for convergence paths."""
        arrow = FancyArrowPatch(
            (x0, y0), (x1, y1),
            arrowstyle='->', color=color, lw=lw,
            connectionstyle=curve, alpha=0.65, zorder=1)
        ax.add_patch(arrow)

    # ════════════════════════════════════════════
    # Layout
    # ════════════════════════════════════════════
    Y_axiom = 12.0
    Y_paths = 9.5     # three independent paths
    Y_conv  = 6.5     # convergence point (self-consistency)
    Y_out   = 3.5     # output constants row 1
    Y_out2  = 1.5     # output constants row 2

    # Three path x-positions
    XL, XC, XR = -4.0, 0, 4.0

    # ════════════════════════════════════════════
    #  AXIOM — top
    # ════════════════════════════════════════════
    draw_box(0, Y_axiom,
             r'CP$^3$  +  $\tau$  (complex conjugation)',
             VIOLET, w=6.5, h=0.90, fs=17, alpha=0.22,
             sub=r'Fix($\tau$) = RP$^3$',
             sub_color=VIO_LT, sub_fs=13)

    # ════════════════════════════════════════════
    #  THREE INDEPENDENT PATHS
    # ════════════════════════════════════════════

    # Left path: Hopf fiber → g = 2π → hierarchy
    draw_box(XL, Y_paths,
             r'$g = 2\pi$', VIOLET, w=3.2, fs=16,
             sub='symplectic area of\nactualization disk',
             sub_color=VIO_LT, sub_fs=10)

    # Center path: spectral geometry → α
    draw_box(XC, Y_paths,
             r'$\alpha \approx 1/137$', CYAN, w=3.5, fs=16,
             sub='three routes converge\n(spectral, gravity, instanton)',
             sub_color=CYAN_DK, sub_fs=10)

    # Right path: packing / instanton → N_∞
    draw_box(XR, Y_paths,
             r'$N_\infty = \varphi^{392}$', GOLD, w=3.5, fs=16,
             sub='boundary capacity\n(packing + instanton)',
             sub_color=GOLD_LT, sub_fs=10)

    # Path labels — what feature of CP³ each uses
    label_y = Y_paths + 1.3
    ax.text(XL, label_y, 'Kähler structure', ha='center', fontsize=11,
            color=VIO_LT, fontstyle='italic', alpha=0.7)
    ax.text(XC, label_y, 'spectral geometry', ha='center', fontsize=11,
            color=CYAN_DK, fontstyle='italic', alpha=0.7)
    ax.text(XR, label_y, 'topology + action', ha='center', fontsize=11,
            color=GOLD_LT, fontstyle='italic', alpha=0.7)

    # Axiom → three paths
    arr(-1.5, Y_axiom - 0.50, XL, Y_paths + 0.65, VIOLET)
    arr(0, Y_axiom - 0.50, XC, Y_paths + 0.65, CYAN)
    arr(1.5, Y_axiom - 0.50, XR, Y_paths + 0.65, GOLD)

    # ════════════════════════════════════════════
    #  CONVERGENCE — self-consistency relation
    # ════════════════════════════════════════════

    # Highlight region around convergence
    conv_w, conv_h = 6.5, 1.3
    glow = FancyBboxPatch((-conv_w/2, Y_conv - conv_h/2), conv_w, conv_h,
                          boxstyle="round,pad=0.15",
                          facecolor=WHITE, edgecolor=WHITE,
                          alpha=0.04, lw=0, zorder=0.5)
    ax.add_patch(glow)

    draw_box(0, Y_conv,
             r'$(2\pi)^{27}\,\sqrt{\alpha} \;=\; \varphi^{98}$',
             CYAN, w=6.0, h=1.1, fs=19, alpha=0.22, lw=1.8,
             sub='self-consistency relation  —  three paths, one equation',
             sub_color=WHITE, sub_fs=12)

    # Three paths converge into the relation
    # Use slightly curved arrows to emphasize convergence
    curved_arr(XL, Y_paths - 0.55, -1.8, Y_conv + 0.60,
               color=VIOLET, lw=1.5, curve='arc3,rad=0.15')
    arr(XC, Y_paths - 0.55, 0, Y_conv + 0.60, CYAN, lw=1.5)
    curved_arr(XR, Y_paths - 0.55, 1.8, Y_conv + 0.60,
               color=GOLD, lw=1.5, curve='arc3,rad=-0.15')

    # Convergence annotation
    ax.text(5.5, Y_conv,
            'independent paths\nmust agree\n→ no tuning possible',
            ha='left', va='center', fontsize=10, color=DIM_LT,
            fontstyle='italic', alpha=0.7)

    # ════════════════════════════════════════════
    #  OUTPUT CONSTANTS — downstream from convergence
    # ════════════════════════════════════════════

    # Row 1: G, Λ, H₀, α_w
    x_o = [-4.8, -1.6, 1.6, 4.8]

    draw_box(x_o[0], Y_out,
             r'$G \propto \alpha/\!\sqrt{N_\infty}$', GOLD, w=3.2, fs=13,
             sub='Newton constant', sub_color=GOLD_LT, sub_fs=10)
    draw_box(x_o[1], Y_out,
             r'$\Lambda \propto 1/N_\infty$', GOLD, w=2.8, fs=13,
             sub='cosmological constant', sub_color=GOLD_LT, sub_fs=10)
    draw_box(x_o[2], Y_out,
             r'$H_0 \approx 70.9$', GOLD, w=2.8, fs=13,
             sub='km/s/Mpc', sub_color=GOLD_LT, sub_fs=10)
    draw_box(x_o[3], Y_out,
             r'$\sin^2\!\theta_W = 3/8$', GOLD, w=3.0, fs=13,
             sub='Weinberg angle', sub_color=GOLD_LT, sub_fs=10)

    # Row 2: α_w, α_GUT, k_c
    x_o2 = [-3.5, 0, 3.5]

    draw_box(x_o2[0], Y_out2,
             r'$\alpha_w^{-1} \approx 29.6$', GOLD, w=3.0, fs=13,
             sub='weak coupling', sub_color=GOLD_LT, sub_fs=10)
    draw_box(x_o2[1], Y_out2,
             r'$\alpha_{\mathrm{GUT}} = 1/10$', GOLD, w=3.0, fs=13,
             sub='at Pati-Salam scale', sub_color=GOLD_LT, sub_fs=10)
    draw_box(x_o2[2], Y_out2,
             r'$k_c \approx 75.35$', GOLD, w=3.0, fs=13,
             sub='consciousness boundary', sub_color=GOLD_LT, sub_fs=10)

    # Arrows from convergence to outputs
    for x in x_o:
        arr(0, Y_conv - 0.60, x, Y_out + 0.45, ARR, lw=1.0)
    for x in x_o2:
        arr(0, Y_conv - 0.60, x, Y_out2 + 0.45, ARR, lw=1.0)

    # ════════════════════════════════════════════
    #  Footer + legend
    # ════════════════════════════════════════════
    ax.text(0, -0.6,
            'Three independent geometric measurements of the same manifold.\n'
            'Self-consistency fixes the constants — no parameter is free to vary.',
            ha='center', va='center', fontsize=11, color=DIM, fontstyle='italic')

    # Faint decorative arcs
    for r, a in [(7, 0.015), (10, 0.01), (13, 0.007)]:
        arc = plt.Circle((0, Y_axiom + 1.5), r, facecolor='none',
                          edgecolor=VIOLET, alpha=a, linewidth=1, zorder=0)
        ax.add_patch(arc)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200, facecolor=BG, bbox_inches='tight',
                pad_inches=0.3)
    plt.close()
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()

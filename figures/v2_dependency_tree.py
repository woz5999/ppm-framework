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
from matplotlib.colors import to_rgba
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
        'WHITE':   '#f0f0f0',
        'DIM':     '#777777',
        'DIM_LT':  '#aaaaaa',
        'VIO_LT':  '#C4B8FF',
        'GOLD_LT': '#F0D880',
        'CYAN_LT': '#40E8E0',
        'CYAN_DK': '#00AAB0',
        'ARR':     '#cccccc',
        'output':  'v2_dependency_tree.png',
    },
    'technical': {
        'BG':      '#040812',
        'VIOLET':  '#7B68EE',
        'CYAN':    '#00CED1',
        'GOLD':    '#D4A843',
        'WHITE':   '#f0f0f0',
        'DIM':     '#777777',
        'DIM_LT':  '#aaaaaa',
        'VIO_LT':  '#C4B8FF',
        'GOLD_LT': '#F0D880',
        'CYAN_LT': '#40E8E0',
        'CYAN_DK': '#00AAB0',
        'ARR':     '#cccccc',
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
    CYAN_LT = T['CYAN_LT']
    CYAN_DK = T['CYAN_DK']
    ARR     = T['ARR']

    # ════════════════════════════════════════════
    # Canvas — taller to give breathing room
    # ════════════════════════════════════════════
    fig, ax = plt.subplots(figsize=(16, 16), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-9, 9)
    ax.set_ylim(-1, 14)
    ax.axis('off')

    # ════════════════════════════════════════════
    # Drawing helpers
    # ════════════════════════════════════════════
    def draw_box(x, y, text, color, w=3.6, h=1.0, fs=18, fill_alpha=0.22,
                 tc=WHITE, lw=2.0, sub=None, sub_color=None, sub_fs=13,
                 glow_radius=0):
        """Draw a rounded box with optional outer glow."""
        # Outer glow (layered translucent copies)
        if glow_radius > 0:
            for i in range(3):
                pad = 0.05 + i * 0.06
                g = FancyBboxPatch((x - w/2 - pad, y - h/2 - pad),
                                   w + 2*pad, h + 2*pad,
                                   boxstyle=f"round,pad=0.12",
                                   facecolor=color, edgecolor='none',
                                   alpha=0.04 * (3 - i), lw=0, zorder=1)
                ax.add_patch(g)

        # Fill
        b = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle="round,pad=0.12",
                           facecolor=color, edgecolor='none',
                           alpha=fill_alpha, lw=0, zorder=2)
        ax.add_patch(b)
        # Border
        border = FancyBboxPatch((x - w/2, y - h/2), w, h,
                                boxstyle="round,pad=0.12",
                                facecolor='none', edgecolor=color,
                                alpha=0.7, lw=lw, zorder=3)
        ax.add_patch(border)
        if sub:
            ax.text(x, y + 0.18, text, ha='center', va='center', fontsize=fs,
                    color=tc, fontfamily='serif', fontweight='bold', zorder=4)
            ax.text(x, y - 0.24, sub, ha='center', va='center',
                    fontsize=sub_fs, color=sub_color or DIM_LT,
                    fontfamily='serif', zorder=4)
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=fs,
                    color=tc, fontfamily='serif', fontweight='bold', zorder=4)

    def arr(x0, y0, x1, y1, color=ARR, lw=1.8, dashed=False):
        style = 'dashed' if dashed else 'solid'
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='->', color=color,
                                    lw=lw, linestyle=style, alpha=0.75,
                                    mutation_scale=18))

    def curved_arr(x0, y0, x1, y1, color=ARR, lw=1.8, curve='arc3,rad=0.3'):
        arrow = FancyArrowPatch(
            (x0, y0), (x1, y1),
            arrowstyle='->', color=color, lw=lw,
            connectionstyle=curve, alpha=0.75, zorder=1,
            mutation_scale=18)
        ax.add_patch(arrow)

    # ════════════════════════════════════════════
    # Layout — more vertical space between tiers
    # ════════════════════════════════════════════
    Y_axiom = 13.0
    Y_paths = 10.0
    Y_conv  = 7.0
    Y_out   = 3.8
    Y_out2  = 1.2

    XL, XC, XR = -4.5, 0, 4.5

    # ════════════════════════════════════════════
    #  Background texture — subtle radial gradient via concentric circles
    # ════════════════════════════════════════════
    for r in np.linspace(1, 18, 40):
        c = plt.Circle((0, 7), r, facecolor='none',
                        edgecolor=VIOLET, alpha=0.008, lw=0.8, zorder=0)
        ax.add_patch(c)

    # ════════════════════════════════════════════
    #  AXIOM — top
    # ════════════════════════════════════════════
    draw_box(0, Y_axiom,
             r'CP$^3$  +  $\tau$  (complex conjugation)',
             VIOLET, w=7.5, h=1.25, fs=26, fill_alpha=0.28,
             sub=r'Fix($\tau$) = RP$^3$',
             sub_color=VIO_LT, sub_fs=19, glow_radius=1)

    # ════════════════════════════════════════════
    #  THREE INDEPENDENT PATHS
    # ════════════════════════════════════════════

    draw_box(XL, Y_paths,
             r'$g = 2\pi$', VIOLET, w=3.8, h=1.15, fs=26,
             sub='symplectic area of\nactualization disk',
             sub_color=VIO_LT, sub_fs=14, glow_radius=1)

    draw_box(XC, Y_paths,
             r'$\alpha \approx 1/137$', CYAN, w=4.0, h=1.15, fs=26,
             sub='three routes converge\n(spectral, gravity, instanton)',
             sub_color=WHITE, sub_fs=14, glow_radius=1)

    draw_box(XR, Y_paths,
             r'$N_\infty = \varphi^{392}$', GOLD, w=4.0, h=1.15, fs=26,
             sub='boundary capacity\n(packing + instanton)',
             sub_color=GOLD_LT, sub_fs=14, glow_radius=1)

    # Path labels
    label_y = Y_paths + 1.55
    ax.text(XL, label_y, 'Kähler structure', ha='center', fontsize=16,
            color=VIO_LT, fontstyle='italic', alpha=0.85)
    ax.text(XC - 1.3, label_y - 0.3, 'spectral geometry', ha='center', fontsize=16,
            color=CYAN_LT, fontstyle='italic', alpha=0.85)
    ax.text(XR, label_y, 'topology + action', ha='center', fontsize=16,
            color=GOLD_LT, fontstyle='italic', alpha=0.85)

    # Axiom → three paths
    arr(-2.0, Y_axiom - 0.62, XL, Y_paths + 0.75, VIOLET, lw=2.0)
    arr(0, Y_axiom - 0.62, XC, Y_paths + 0.75, CYAN, lw=2.0)
    arr(2.0, Y_axiom - 0.62, XR, Y_paths + 0.75, GOLD, lw=2.0)

    # ════════════════════════════════════════════
    #  CONVERGENCE — self-consistency relation
    # ════════════════════════════════════════════

    # Glow behind convergence box
    for i in range(5):
        pad = 0.08 * (i + 1)
        glow = FancyBboxPatch((-3.5 - pad, Y_conv - 0.7 - pad),
                              7.0 + 2*pad, 1.4 + 2*pad,
                              boxstyle="round,pad=0.18",
                              facecolor=CYAN, edgecolor='none',
                              alpha=0.015 * (5 - i), lw=0, zorder=0.5)
        ax.add_patch(glow)

    draw_box(0, Y_conv,
             r'$(2\pi)^{27}\,\sqrt{\alpha} \;=\; \varphi^{98}$',
             CYAN, w=7.5, h=1.45, fs=28, fill_alpha=0.25, lw=2.5,
             sub='self-consistency relation  —  three paths, one equation',
             sub_color=WHITE, sub_fs=16, glow_radius=0)

    # Convergence arrows
    curved_arr(XL, Y_paths - 0.62, -2.2, Y_conv + 0.78,
               color=VIOLET, lw=2.0, curve='arc3,rad=0.15')
    arr(XC, Y_paths - 0.62, 0, Y_conv + 0.78, CYAN, lw=2.0)
    curved_arr(XR, Y_paths - 0.62, 2.2, Y_conv + 0.78,
               color=GOLD, lw=2.0, curve='arc3,rad=-0.15')


    # ════════════════════════════════════════════
    #  OUTPUT CONSTANTS
    # ════════════════════════════════════════════

    # Row 1: G, Λ, H₀
    x_o = [-5.0, 0, 5.0]

    draw_box(x_o[0], Y_out,
             r'$G \propto \alpha/\!\sqrt{N_\infty}$', GOLD, w=3.8, h=1.15, fs=21,
             sub='Newton constant', sub_color=GOLD_LT, sub_fs=15,
             glow_radius=1)
    draw_box(x_o[1], Y_out,
             r'$\Lambda \propto 1/N_\infty$', GOLD, w=3.8, h=1.15, fs=21,
             sub='cosmological constant', sub_color=GOLD_LT, sub_fs=15,
             glow_radius=1)
    draw_box(x_o[2], Y_out,
             r'$H_0 = c\,/\sqrt{N_\infty}\,\lambda_C$', GOLD, w=4.2, h=1.15, fs=19,
             sub='Hubble parameter', sub_color=GOLD_LT, sub_fs=15,
             glow_radius=1)

    # Row 2: α_w — centered
    draw_box(0, Y_out2,
             r'$\alpha_w = \alpha\,/\sin^2\!\theta_W$', GOLD, w=5.0, h=1.15, fs=22,
             sub=r'$\sin^2\!\theta_W = 3/8$  from  dim(RP$^3$) $/\, 2\chi$(CP$^3$)',
             sub_color=GOLD_LT, sub_fs=14,
             glow_radius=1)

    # Arrows from convergence to outputs
    for x in x_o:
        arr(0, Y_conv - 0.78, x, Y_out + 0.62, ARR, lw=1.5)
    arr(0, Y_conv - 0.78, 0, Y_out2 + 0.62, ARR, lw=1.5)

    # ════════════════════════════════════════════
    #  Save
    # ════════════════════════════════════════════
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200, facecolor=BG, bbox_inches='tight',
                pad_inches=0.4)
    plt.close()
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()

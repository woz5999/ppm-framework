"""
v2_dependency_tree_C.py — "Over-determined constraint web" concept.

Constants as nodes, geometric relationships as edges.
The system has more constraints than unknowns → over-determined → testable.
Visual: a web/network, not a tree. Edges labeled with the relationship.

Nodes: g=2π, α, N_∞, G, Λ, H₀, sin²θ_W, α_w, α_GUT
Edges: each is a derived relationship (equation connecting two+ nodes)

The visual point: count nodes vs edges. More edges than needed to
determine the system → every "extra" edge is a testable prediction.
"""
import os
import argparse
import math
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
        'BG': '#0d1117', 'VIOLET': '#7B68EE', 'CYAN': '#00CED1',
        'GOLD': '#D4A843', 'WHITE': '#eeeeee', 'DIM': '#555555',
        'DIM_LT': '#999999', 'VIO_LT': '#B0A0FF', 'GOLD_LT': '#F0D880',
        'CYAN_DK': '#009999', 'GREEN': '#2ECC71',
        'output': 'v2_dependency_tree_C.png',
    },
    'technical': {
        'BG': '#040812', 'VIOLET': '#7B68EE', 'CYAN': '#00CED1',
        'GOLD': '#D4A843', 'WHITE': '#eeeeee', 'DIM': '#555555',
        'DIM_LT': '#999999', 'VIO_LT': '#B0A0FF', 'GOLD_LT': '#F0D880',
        'CYAN_DK': '#009999', 'GREEN': '#2ECC71',
        'output': 'v2_dependency_tree_C_tech.png',
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--technical', action='store_true')
    args = parser.parse_args()

    T = THEMES['technical' if args.technical else 'ontology']
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, T['output'])

    BG = T['BG']; VIOLET = T['VIOLET']; CYAN = T['CYAN']; GOLD = T['GOLD']
    WHITE = T['WHITE']; DIM = T['DIM']; DIM_LT = T['DIM_LT']
    VIO_LT = T['VIO_LT']; GOLD_LT = T['GOLD_LT']; CYAN_DK = T['CYAN_DK']
    GREEN = T['GREEN']

    fig, ax = plt.subplots(figsize=(14, 14), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-7, 7)
    ax.set_ylim(-7, 7)
    ax.set_aspect('equal')
    ax.axis('off')

    # ── helpers ──
    def node(x, y, text, color, r=0.65, fs=13, sub=None, sub_color=None, sub_fs=9):
        circle = plt.Circle((x, y), r, facecolor=color, edgecolor=color,
                            alpha=0.15, lw=1.4, zorder=2)
        ax.add_patch(circle)
        border = plt.Circle((x, y), r, facecolor='none', edgecolor=color,
                            alpha=0.55, lw=1.4, zorder=3)
        ax.add_patch(border)
        if sub:
            ax.text(x, y + 0.12, text, ha='center', va='center', fontsize=fs,
                    color=WHITE, fontfamily='serif', fontweight='medium', zorder=4)
            ax.text(x, y - 0.22, sub, ha='center', va='center',
                    fontsize=sub_fs, color=sub_color or DIM_LT,
                    fontfamily='serif', zorder=4)
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=fs,
                    color=WHITE, fontfamily='serif', fontweight='medium', zorder=4)
        return (x, y)

    def edge(x0, y0, x1, y1, color=DIM_LT, lw=1.2, alpha=0.4,
             label=None, label_color=None, label_fs=9, rad=0):
        """Draw an edge between two nodes, optionally curved and labeled."""
        if rad != 0:
            arrow = FancyArrowPatch(
                (x0, y0), (x1, y1),
                arrowstyle='-', color=color, lw=lw, alpha=alpha,
                connectionstyle=f'arc3,rad={rad}', zorder=1)
            ax.add_patch(arrow)
        else:
            ax.plot([x0, x1], [y0, y1], color=color, lw=lw, alpha=alpha, zorder=1)

        if label:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            # Offset label perpendicular to the edge
            dx, dy = x1 - x0, y1 - y0
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                nx, ny = -dy/length * 0.3, dx/length * 0.3
            else:
                nx, ny = 0, 0.3
            ax.text(mx + nx, my + ny, label, ha='center', va='center',
                    fontsize=label_fs, color=label_color or DIM_LT,
                    fontstyle='italic', alpha=0.8,
                    bbox=dict(boxstyle='round,pad=0.1', facecolor=BG,
                              edgecolor='none', alpha=0.85),
                    zorder=5)

    # ════════════════════════════════════════════
    #  Node positions — arranged in tiers but connected as a web
    # ════════════════════════════════════════════

    # Tier 0: geometric inputs (top)
    g_pos = node(-3.5, 5.0, r'$g = 2\pi$', VIOLET, r=0.70, fs=15,
                 sub='scaling', sub_color=VIO_LT)
    chi_pos = node(0, 5.5, r'$\chi = 4$', VIOLET, r=0.65, fs=15,
                   sub='Euler', sub_color=VIO_LT)
    vol_pos = node(3.5, 5.0, r'Vol $= \pi^2$', VIOLET, r=0.70, fs=15,
                   sub='Lagrangian', sub_color=VIO_LT)

    # Tier 1: spectral
    alpha_pos = node(-2.0, 2.2, r'$\alpha$', CYAN, r=0.75, fs=17,
                     sub=r'$\approx 1/137$', sub_color=CYAN_DK, sub_fs=11)
    N_pos = node(3.0, 2.5, r'$N_\infty$', GOLD, r=0.75, fs=15,
                 sub=r'$\varphi^{392}$', sub_color=GOLD_LT, sub_fs=11)

    # Tier 2: derived constants (spread around)
    G_pos = node(-5.0, -0.5, r'$G$', GOLD, r=0.60, fs=15)
    Lam_pos = node(-2.5, -1.5, r'$\Lambda$', GOLD, r=0.60, fs=15)
    H0_pos = node(0.5, -0.8, r'$H_0$', GOLD, r=0.60, fs=14,
                  sub='70.9', sub_color=GOLD_LT)
    sin2_pos = node(3.5, -0.5, r'$\sin^2\!\theta_W$', GOLD, r=0.75, fs=13,
                    sub='3/8', sub_color=GOLD_LT)
    aw_pos = node(-4.5, -3.5, r'$\alpha_w^{-1}$', GOLD, r=0.65, fs=13,
                  sub='29.6', sub_color=GOLD_LT)
    aGUT_pos = node(0, -3.8, r'$\alpha_{\mathrm{GUT}}$', GOLD, r=0.70, fs=13,
                    sub='1/10', sub_color=GOLD_LT)
    kc_pos = node(4.5, -3.0, r'$k_c$', GOLD, r=0.60, fs=14,
                  sub='75.35', sub_color=GOLD_LT)

    # Self-consistency (special node)
    sc_pos = node(-0.5, -6.0,
                  r'$(2\pi)^{27}\!\sqrt{\alpha} = \varphi^{98}$',
                  CYAN, r=0.0, fs=1)  # invisible circle, draw as box instead

    # Actually draw self-consistency as a box
    scx, scy = -0.5, -6.0
    eqbox = FancyBboxPatch((scx - 3.0, scy - 0.45), 6.0, 0.90,
                           boxstyle="round,pad=0.10",
                           facecolor=CYAN, edgecolor=CYAN,
                           alpha=0.18, lw=1.6, zorder=2)
    ax.add_patch(eqbox)
    eqborder = FancyBboxPatch((scx - 3.0, scy - 0.45), 6.0, 0.90,
                              boxstyle="round,pad=0.10",
                              facecolor='none', edgecolor=CYAN,
                              alpha=0.55, lw=1.6, zorder=3)
    ax.add_patch(eqborder)
    ax.text(scx, scy + 0.08,
            r'$(2\pi)^{27}\,\sqrt{\alpha} \;=\; \varphi^{98}$',
            ha='center', va='center', fontsize=16, color=WHITE,
            fontfamily='serif', fontweight='medium', zorder=4)
    ax.text(scx, scy - 0.25, 'self-consistency closure',
            ha='center', va='center', fontsize=10, color=CYAN_DK, zorder=4)

    # ════════════════════════════════════════════
    #  Edges — geometric relationships
    # ════════════════════════════════════════════

    # Geometric inputs → spectral results
    edge(*g_pos, *alpha_pos, VIOLET, 1.2, 0.5,
         'instanton\nRoute III', VIO_LT)
    edge(*vol_pos, *alpha_pos, VIOLET, 1.2, 0.4,
         'heat kernel\nRoute I', VIO_LT, rad=-0.3)
    edge(*vol_pos, *N_pos, GOLD, 1.2, 0.5,
         'packing', GOLD_LT)
    edge(*g_pos, *N_pos, VIOLET, 1.0, 0.3,
         r'$S = 30\pi$', VIO_LT, rad=-0.2)

    # α, N_∞ → derived constants
    edge(*alpha_pos, *G_pos, CYAN, 1.0, 0.4,
         r'$G \propto \alpha/\sqrt{N}$', CYAN_DK)
    edge(*N_pos, *G_pos, GOLD, 1.0, 0.3)
    edge(*N_pos, *Lam_pos, GOLD, 1.0, 0.4,
         r'$\Lambda \propto 1/N$', GOLD_LT)
    edge(*G_pos, *H0_pos, DIM_LT, 1.0, 0.3)
    edge(*Lam_pos, *H0_pos, DIM_LT, 1.0, 0.3)

    # χ → sin²θ_W
    edge(*chi_pos, *sin2_pos, VIOLET, 1.2, 0.4,
         'Pati-Salam\ngroup theory', VIO_LT)

    # sin²θ_W → α_w
    edge(*sin2_pos, *aw_pos, GOLD, 1.0, 0.3)
    edge(*alpha_pos, *aw_pos, CYAN, 1.0, 0.3)

    # α → α_GUT
    edge(*alpha_pos, *aGUT_pos, CYAN, 1.0, 0.3,
         'Fubini-Study\ncurvature', CYAN_DK)

    # g → k_c
    edge(*g_pos, *kc_pos, VIOLET, 1.0, 0.3, 'hierarchy + $k_BT$', VIO_LT,
         rad=-0.2)

    # self-consistency edges: g, α, N_∞ all connect to it
    edge(*g_pos, scx - 1.5, scy + 0.50, VIOLET, 1.3, 0.4)
    edge(*alpha_pos, scx - 0.5, scy + 0.50, CYAN, 1.3, 0.4)
    edge(*N_pos, scx + 1.0, scy + 0.50, GOLD, 1.3, 0.4)

    # ════════════════════════════════════════════
    #  Annotations
    # ════════════════════════════════════════════

    # Count annotation
    ax.text(5.5, -5.5,
            '9 constants\n13 constraints\n→ over-determined',
            ha='center', va='center', fontsize=12, color=GREEN,
            fontweight='bold', alpha=0.8,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=BG,
                      edgecolor=GREEN, alpha=0.3, lw=1.2))

    ax.text(5.5, -6.5,
            'every "extra" constraint\nis a testable prediction',
            ha='center', va='center', fontsize=10, color=GREEN,
            fontstyle='italic', alpha=0.6)

    # Tier labels
    ax.text(-6.5, 5.5, 'geometric\ninputs', ha='center', fontsize=10,
            color=VIO_LT, fontstyle='italic', alpha=0.6)
    ax.text(-6.5, 2.2, 'spectral\nresults', ha='center', fontsize=10,
            color=CYAN_DK, fontstyle='italic', alpha=0.6)
    ax.text(-6.5, -2.0, 'derived\nconstants', ha='center', fontsize=10,
            color=GOLD_LT, fontstyle='italic', alpha=0.6)

    # Decorative
    for r, a in [(8, 0.010), (11, 0.006)]:
        arc = plt.Circle((0, 0), r, facecolor='none',
                          edgecolor=VIOLET, alpha=a, linewidth=1, zorder=0)
        ax.add_patch(arc)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200, facecolor=BG, bbox_inches='tight',
                pad_inches=0.3)
    plt.close()
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()

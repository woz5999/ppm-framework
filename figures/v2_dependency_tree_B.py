"""
v2_dependency_tree_B.py — "Elimination trace" concept.

Shows three equations from three independent physical sectors.
Algebraic elimination of dimensionful quantities (m_π, G) leaves
the self-consistency relation. Visual: proof sketch, not flowchart.

Three equations:
  1. Hierarchy:    E(k) = m_π (2π)^{(51-k)/2}         → at k=1: E_P = m_π (2π)^{25}
  2. Gravity:      G = 16π⁴ ℏc α / (m_π² √N_∞)
  3. Planck:       E_P = √(ℏc⁵/G)

Eliminate m_π between (1) and (2), substitute into (3), get:
  (2π)^27 √α = φ^98    [since √N_∞ = φ^196]
"""
import os
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
OUTPUT_DIR = os.path.join(REPO_ROOT, 'figures', 'computed')
os.makedirs(OUTPUT_DIR, exist_ok=True)

THEMES = {
    'ontology': {
        'BG': '#0d1117', 'VIOLET': '#7B68EE', 'CYAN': '#00CED1',
        'GOLD': '#D4A843', 'WHITE': '#eeeeee', 'DIM': '#777777',
        'DIM_LT': '#999999', 'VIO_LT': '#B0A0FF', 'GOLD_LT': '#F0D880',
        'CYAN_DK': '#009999', 'RED': '#E07070',
        'output': 'v2_dependency_tree_B.png',
    },
    'technical': {
        'BG': '#040812', 'VIOLET': '#7B68EE', 'CYAN': '#00CED1',
        'GOLD': '#D4A843', 'WHITE': '#eeeeee', 'DIM': '#777777',
        'DIM_LT': '#999999', 'VIO_LT': '#B0A0FF', 'GOLD_LT': '#F0D880',
        'CYAN_DK': '#009999', 'RED': '#E07070',
        'output': 'v2_dependency_tree_B_tech.png',
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
    RED = T['RED']

    fig, ax = plt.subplots(figsize=(14, 12), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-7, 7)
    ax.set_ylim(-0.5, 12.5)
    ax.axis('off')

    # ── helpers ──
    def eqbox(x, y, text, color, w=5.5, h=0.75, fs=15, sub=None,
              sub_color=None, sub_fs=11, alpha=0.15, lw=1.4):
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
            ax.text(x, y + 0.13, text, ha='center', va='center', fontsize=fs,
                    color=WHITE, fontfamily='serif', fontweight='medium', zorder=4)
            ax.text(x, y - 0.17, sub, ha='center', va='center',
                    fontsize=sub_fs, color=sub_color or DIM_LT,
                    fontfamily='serif', zorder=4)
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=fs,
                    color=WHITE, fontfamily='serif', fontweight='medium', zorder=4)

    def arr(x0, y0, x1, y1, color=DIM_LT, lw=1.3):
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='->', color=color, lw=lw, alpha=0.6))

    # ════════════════════════════════════════════
    #  Title area
    # ════════════════════════════════════════════
    ax.text(0, 12.0, 'Three equations from three sectors',
            ha='center', fontsize=16, color=WHITE, fontweight='bold')
    ax.text(0, 11.5, 'each derived independently from CP³ geometry',
            ha='center', fontsize=12, color=DIM_LT, fontstyle='italic')

    # ════════════════════════════════════════════
    #  Three source equations — spread across top
    # ════════════════════════════════════════════
    Y_eq = 10.0
    spacing = 4.5
    XL, XC, XR = -spacing, 0, spacing

    # Equation 1: Hierarchy (Planck anchor)
    eqbox(XL, Y_eq,
          r'$E_P = m_\pi \cdot (2\pi)^{25}$',
          VIOLET, w=4.5, fs=15,
          sub='hierarchy at k = 1', sub_color=VIO_LT)
    ax.text(XL, Y_eq + 0.7, 'energy hierarchy', ha='center', fontsize=11,
            color=VIO_LT, fontstyle='italic')

    # Equation 2: Gravity
    eqbox(XC, Y_eq,
          r'$G = \frac{16\pi^4 \hbar c\, \alpha}{m_\pi^2 \sqrt{N_\infty}}$',
          CYAN, w=4.8, h=0.85, fs=15,
          sub='information loss → curvature', sub_color=CYAN_DK)
    ax.text(XC, Y_eq + 0.75, 'gravitational sector', ha='center', fontsize=11,
            color=CYAN_DK, fontstyle='italic')

    # Equation 3: Planck mass definition
    eqbox(XR, Y_eq,
          r'$E_P = \sqrt{\hbar c^5 / G}$',
          GOLD, w=4.0, fs=15,
          sub='dimensional analysis', sub_color=GOLD_LT)
    ax.text(XR, Y_eq + 0.7, 'Planck scale', ha='center', fontsize=11,
            color=GOLD_LT, fontstyle='italic')

    # ════════════════════════════════════════════
    #  Step 1: Eliminate G
    # ════════════════════════════════════════════
    Y_s1 = 7.8

    ax.text(-6.2, Y_s1, 'Step 1', ha='left', fontsize=12,
            color=RED, fontweight='bold', alpha=0.8)
    ax.text(-6.2, Y_s1 - 0.35, 'eliminate $G$', ha='left', fontsize=11,
            color=RED, fontstyle='italic', alpha=0.7)

    # Arrows from eq2 and eq3 converging
    arr(XC, Y_eq - 0.50, 0, Y_s1 + 0.45, CYAN)
    arr(XR, Y_eq - 0.50, 0.5, Y_s1 + 0.45, GOLD)

    eqbox(0, Y_s1,
          r'$E_P^2 = \frac{\hbar c^5 \cdot m_\pi^2 \sqrt{N_\infty}}{16\pi^4 \hbar c\, \alpha}$',
          DIM_LT, w=6.5, h=0.80, fs=14, alpha=0.08)

    # Strikethrough on G (visual: G is gone)
    ax.text(5.0, Y_s1, '$G$ cancelled', ha='left', fontsize=11,
            color=RED, fontstyle='italic', alpha=0.6)

    # ════════════════════════════════════════════
    #  Step 2: Substitute E_P from hierarchy
    # ════════════════════════════════════════════
    Y_s2 = 6.0

    ax.text(-6.2, Y_s2, 'Step 2', ha='left', fontsize=12,
            color=RED, fontweight='bold', alpha=0.8)
    ax.text(-6.2, Y_s2 - 0.35, 'eliminate $m_\\pi$', ha='left', fontsize=11,
            color=RED, fontstyle='italic', alpha=0.7)

    arr(XL, Y_eq - 0.50, -0.5, Y_s2 + 0.45, VIOLET)
    arr(0, Y_s1 - 0.45, 0, Y_s2 + 0.45, DIM_LT, lw=1.0)

    eqbox(0, Y_s2,
          r'$m_\pi^2 (2\pi)^{50} = \frac{c^4\, m_\pi^2\, \sqrt{N_\infty}}{16\pi^4\, \alpha}$',
          DIM_LT, w=7.0, h=0.80, fs=14, alpha=0.08)

    ax.text(5.2, Y_s2, '$m_\\pi$ cancelled', ha='left', fontsize=11,
            color=RED, fontstyle='italic', alpha=0.6)

    # ════════════════════════════════════════════
    #  Step 3: Simplify → self-consistency
    # ════════════════════════════════════════════
    Y_s3 = 4.2

    ax.text(-6.2, Y_s3, 'Step 3', ha='left', fontsize=12,
            color=RED, fontweight='bold', alpha=0.8)
    ax.text(-6.2, Y_s3 - 0.35, 'simplify', ha='left', fontsize=11,
            color=RED, fontstyle='italic', alpha=0.7)

    arr(0, Y_s2 - 0.45, 0, Y_s3 + 0.45, DIM_LT, lw=1.0)

    eqbox(0, Y_s3,
          r'$(2\pi)^{54} \cdot \alpha = \sqrt{N_\infty}$',
          DIM_LT, w=5.5, h=0.75, fs=15, alpha=0.08)

    # ════════════════════════════════════════════
    #  Result: self-consistency relation
    # ════════════════════════════════════════════
    Y_res = 2.2

    ax.text(-6.2, Y_res + 0.3, 'Result', ha='left', fontsize=12,
            color=CYAN, fontweight='bold', alpha=0.9)
    ax.text(-6.2, Y_res - 0.1,
            r'with $\sqrt{N_\infty} = \varphi^{196}$',
            ha='left', fontsize=11, color=CYAN_DK, fontstyle='italic', alpha=0.7)

    arr(0, Y_s3 - 0.45, 0, Y_res + 0.55, CYAN, lw=1.5)

    # Glow
    glow = FancyBboxPatch((-3.5, Y_res - 0.55), 7.0, 1.1,
                          boxstyle="round,pad=0.15",
                          facecolor=WHITE, edgecolor=WHITE,
                          alpha=0.04, lw=0, zorder=0.5)
    ax.add_patch(glow)

    eqbox(0, Y_res,
          r'$(2\pi)^{27}\,\sqrt{\alpha} \;=\; \varphi^{98}$',
          CYAN, w=6.0, h=1.0, fs=20, alpha=0.22, lw=1.8,
          sub='no dimensionful quantities remain — pure geometry',
          sub_color=WHITE, sub_fs=12)

    # ════════════════════════════════════════════
    #  Footer
    # ════════════════════════════════════════════
    ax.text(0, 0.5,
            'Three equations, each from a different sector of the framework.\n'
            'Eliminate the two dimensionful quantities ($G$ and $m_\\pi$).\n'
            'What remains is a relation between three geometric invariants — '
            'satisfied to 1.5%.',
            ha='center', va='center', fontsize=11, color=DIM, fontstyle='italic',
            linespacing=1.6)

    # Decorative arcs
    for r, a in [(7, 0.012), (10, 0.008)]:
        arc = plt.Circle((0, 12.5), r, facecolor='none',
                          edgecolor=VIOLET, alpha=a, linewidth=1, zorder=0)
        ax.add_patch(arc)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200, facecolor=BG, bbox_inches='tight',
                pad_inches=0.3)
    plt.close()
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()

"""
fig_three_routes_phi_exponent.py — three routes to α, two complementary axes.

Panel A (1/α axis): Routes I and II predict α directly.  Their predicted
1/α values are plotted against the observed value.  Route III is absent
from this panel because it does not predict α directly — only the
exponent structure of α's master-relation form.

Panel B (φ-exponent axis): all three routes plot on a unified axis K
where φ^K = (2π)^{54} · α (the squared master self-consistency
relation, with master integer K = 196).  Routes I and II compute K
indirectly via their α-predictions; Route III computes K directly
from the instanton action via K_III = 30π / ln(φ).  No route is parked
on this axis.

Color convention is deliberately neutral (blue/green/red) so the
markers don't conflict with the framework's semantic palette
(gold = τ-even, violet = τ-odd, cyan = actualization).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from _style import (apply_style, save,
                    BG, WHITE, GRAY, BLUE, GREEN, RED)


# ─── Compute values ────────────────────────────────────────────────────────

PHI = (1.0 + math.sqrt(5.0)) / 2.0
LN_PHI = math.log(PHI)
LN_TWOPI = math.log(2 * math.pi)

ALPHA_OBS_INV = 137.035999
ALPHA_I_INV   = 137.257
ALPHA_II_INV  = 137.56
S_INST        = 30.0 * math.pi


def K_from_alpha(alpha_inv):
    return (54.0 * LN_TWOPI - math.log(alpha_inv)) / LN_PHI


def K_from_instanton(S):
    return S / LN_PHI


K_master    = 196.0
K_obs       = K_from_alpha(ALPHA_OBS_INV)
K_route_I   = K_from_alpha(ALPHA_I_INV)
K_route_II  = K_from_alpha(ALPHA_II_INV)
K_route_III = K_from_instanton(S_INST)


# ─── Figure ─────────────────────────────────────────────────────────────────

def make_figure():
    apply_style()

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(17, 8), facecolor=BG)

    # ── Panel A: 1/α axis (wide y-range; dots cluster on observed line) ──

    axA.set_facecolor(BG)
    axA.axhline(y=ALPHA_OBS_INV, color=WHITE, linestyle='--',
                linewidth=1.5, alpha=0.6, zorder=3)
    axA.text(2.0, ALPHA_OBS_INV - 0.7,
             f'observed:  $1/\\alpha = {ALPHA_OBS_INV:.3f}$',
             color=WHITE, fontsize=11.5, ha='center', va='top',
             alpha=0.9, weight='bold')

    # Route markers with full value labels
    axA.scatter([1], [ALPHA_I_INV], s=320, color=BLUE,
                edgecolors=WHITE, linewidths=1.6, zorder=10)
    dev_I = abs(ALPHA_I_INV - ALPHA_OBS_INV) / ALPHA_OBS_INV * 100.0
    axA.annotate(
        f'$1/\\alpha_I = {ALPHA_I_INV:.3f}$\n({dev_I:.2f}%)',
        xy=(1, ALPHA_I_INV), xytext=(0.55, 141.5),
        color=BLUE, fontsize=11, weight='bold',
        ha='left', va='center',
        arrowprops=dict(arrowstyle='-', color=BLUE, alpha=0.55,
                        connectionstyle='arc3,rad=-0.20'),
    )

    axA.scatter([2], [ALPHA_II_INV], s=320, color=GREEN,
                edgecolors=WHITE, linewidths=1.6, zorder=10)
    dev_II = abs(ALPHA_II_INV - ALPHA_OBS_INV) / ALPHA_OBS_INV * 100.0
    axA.annotate(
        f'$1/\\alpha_{{II}} = {ALPHA_II_INV:.3f}$\n({dev_II:.2f}%)',
        xy=(2, ALPHA_II_INV), xytext=(2.05, 142.5),
        color=GREEN, fontsize=11, weight='bold',
        ha='left', va='center',
        arrowprops=dict(arrowstyle='-', color=GREEN, alpha=0.55,
                        connectionstyle='arc3,rad=0.20'),
    )

    axA.set_xlim(0.4, 2.6)
    axA.set_ylim(130, 145)
    axA.set_xticks([1, 2])
    axA.set_xticklabels(['Route I\n(Spectral)', 'Route II\n(Cogito)'],
                        fontsize=11.5, color=WHITE)
    axA.set_ylabel(r'$1/\alpha$', color=WHITE, fontsize=14)
    axA.set_title('(A) Direct $\\alpha$ predictions',
                  color=WHITE, fontsize=14, weight='bold', pad=12)
    axA.tick_params(colors=WHITE, labelsize=11)
    axA.grid(True, axis='y', alpha=0.18, color='#2a2a3e')

    # Route III absence note (small, lower-corner)
    axA.text(0.5, 0.04,
             "Route III absent here:  predicts the exponent\n"
             "structure, not " r"$\alpha$" " directly.  See Panel B.",
             transform=axA.transAxes, color=GRAY, fontsize=10,
             va='bottom', ha='center', style='italic',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#0a0a1a',
                       edgecolor=GRAY, alpha=0.88))

    # ── Panel B: φ-exponent axis (tight zoom) ─────────────────────────────

    axB.set_facecolor(BG)

    # Self-consistency reference line at K = 196
    axB.axhline(y=K_master, color=WHITE, linestyle='--',
                linewidth=1.5, alpha=0.6, zorder=3)
    # Label placed in lower portion of panel where there are no markers
    axB.text(2.0, 195.62,
             r'self-consistency:  $K = 196$',
             color=WHITE, fontsize=11.5, ha='center', va='bottom',
             alpha=0.9, weight='bold')

    # Observed K reference (dotted)
    axB.axhline(y=K_obs, color=GRAY, linestyle=':',
                linewidth=1.0, alpha=0.6, zorder=2)
    axB.text(3.45, K_obs + 0.018,
             f'observed:  $K = {K_obs:.3f}$',
             color=GRAY, fontsize=10, ha='right', va='bottom',
             style='italic', alpha=0.85)

    # Route I marker — label upper-left
    axB.scatter([1], [K_route_I], s=320, color=BLUE,
                edgecolors=WHITE, linewidths=1.6, zorder=10)
    axB.annotate(
        f'$K_I = {K_route_I:.3f}$\n'
        f'({abs(K_route_I - K_master)/K_master*100:.3f}%)',
        xy=(1, K_route_I), xytext=(0.55, 196.30),
        color=BLUE, fontsize=11, weight='bold',
        ha='left', va='center',
        arrowprops=dict(arrowstyle='-', color=BLUE, alpha=0.55,
                        connectionstyle='arc3,rad=-0.20'),
    )

    # Route II marker — label upper-right
    axB.scatter([2], [K_route_II], s=320, color=GREEN,
                edgecolors=WHITE, linewidths=1.6, zorder=10)
    axB.annotate(
        f'$K_{{II}} = {K_route_II:.3f}$\n'
        f'({abs(K_route_II - K_master)/K_master*100:.3f}%)',
        xy=(2, K_route_II), xytext=(2.05, 196.36),
        color=GREEN, fontsize=11, weight='bold',
        ha='left', va='center',
        arrowprops=dict(arrowstyle='-', color=GREEN, alpha=0.55,
                        connectionstyle='arc3,rad=0.20'),
    )

    # Route III marker — label lower-right (K_III is below master)
    axB.scatter([3], [K_route_III], s=320, color=RED,
                edgecolors=WHITE, linewidths=1.6, zorder=10)
    axB.annotate(
        f'$K_{{III}} = {K_route_III:.3f}$\n'
        f'({abs(K_route_III - K_master)/K_master*100:.3f}%)',
        xy=(3, K_route_III), xytext=(2.50, 195.74),
        color=RED, fontsize=11, weight='bold',
        ha='center', va='center',
        arrowprops=dict(arrowstyle='-', color=RED, alpha=0.55,
                        connectionstyle='arc3,rad=-0.15'),
    )

    axB.set_xlim(0.4, 3.6)
    axB.set_ylim(195.55, 196.45)
    axB.set_xticks([1, 2, 3])
    axB.set_xticklabels(['Route I\n(Spectral)',
                         'Route II\n(Cogito)',
                         'Route III\n(Instanton)'],
                        fontsize=11.5, color=WHITE)
    axB.set_ylabel(r'$K$  ($\varphi^K = (2\pi)^{54}\,\alpha$)',
                   color=WHITE, fontsize=14)
    axB.set_title(
        '(B) Unified $\\varphi$-exponent axis',
        color=WHITE, fontsize=14, weight='bold', pad=12,
    )
    axB.tick_params(colors=WHITE, labelsize=11)
    axB.grid(True, axis='y', alpha=0.18, color='#2a2a3e')

    plt.tight_layout()
    save(fig, 'three-alpha-routes-two-panel.png')

    # Numerical summary
    print(f"  K_master    = {K_master:.4f}")
    print(f"  K_observed  = {K_obs:.4f}")
    print(f"  K_Route_I   = {K_route_I:.4f}  "
          f"({abs(K_route_I - K_master)/K_master*100:.4f}%)")
    print(f"  K_Route_II  = {K_route_II:.4f}  "
          f"({abs(K_route_II - K_master)/K_master*100:.4f}%)")
    print(f"  K_Route_III = {K_route_III:.4f}  "
          f"({abs(K_route_III - K_master)/K_master*100:.4f}%)")


def main():
    make_figure()


if __name__ == '__main__':
    main()

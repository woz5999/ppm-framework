"""
fig_alpha_route3.py — Route III: instanton-action vs master-relation match.

The framework's degree-3 holomorphic map CP¹ → CP³ has instanton action
S = (N-1) × r² × π = 3 × 10 × π = 30π, where 30 is the fourth pyramidal
number 1² + 2² + 3² + 4².  The corresponding exponential suppression
e^{-S} matches the master self-consistency relation's prediction
φ^{-196} to 0.07% in the exponent — i.e., 30π ≈ 196 ln(φ).

The integer 196 = 2 × 98, where 98 is the exponent in the master
relation (2π)^{27}√α = φ^{98}.  Route III is therefore an independent
verification of the same exponent structure that Routes I and II
converge on, through entirely disjoint mathematics (semiclassical
tunneling on CP³ vs. heat-kernel spectral geometry vs. holographic
gravitational coupling).

Visual: two markers on a number line showing the action 30π and the
master-relation prediction 196 ln(φ) agreeing to 0.07%.

Run: python fig_alpha_route3.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import numpy as np
import matplotlib.pyplot as plt

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE
from ppm import instanton


def make_figure():
    apply_style()

    fig, ax = plt.subplots(figsize=(14, 8), facecolor=BG)
    ax.set_facecolor(BG)

    # ── Compute the two values ─────────────────────────────────────────────

    PHI = (1.0 + math.sqrt(5.0)) / 2.0
    S_inst = instanton.instanton_action()           # 30π
    S_phi  = 196.0 * math.log(PHI)                  # 196 ln φ
    mismatch_pct = abs(S_phi - S_inst) / S_inst * 100.0
    e_S_inst = math.exp(-S_inst)
    phi_neg_196 = PHI ** (-196.0)

    # Center the x-range on the two values, give some breathing room
    center = 0.5 * (S_inst + S_phi)
    half_window = 0.6
    x_lo = center - half_window
    x_hi = center + half_window

    # ── Number line ────────────────────────────────────────────────────────

    y_axis = 0.0
    ax.hlines(y_axis, x_lo, x_hi, colors=WHITE, linewidth=2.0, zorder=4)

    # Tick marks at integer-ish values
    tick_vals = [round(x_lo, 1) + 0.2 * i for i in range(int((x_hi - x_lo) / 0.2) + 2)]
    for tv in tick_vals:
        if x_lo <= tv <= x_hi:
            ax.vlines(tv, y_axis - 0.04, y_axis + 0.04,
                      colors=GRAY, linewidth=1.0, alpha=0.6, zorder=3)
            ax.text(tv, y_axis - 0.18, f'{tv:.1f}',
                    color=GRAY, fontsize=10, ha='center', alpha=0.7)

    # ── Marker 1: instanton action S = 30π ─────────────────────────────────

    ax.scatter([S_inst], [y_axis], s=380, color=GOLD,
               edgecolors=WHITE, linewidths=1.6, zorder=10)
    ax.vlines(S_inst, y_axis, 0.85, colors=GOLD,
              linewidth=2.0, alpha=0.85, zorder=8)
    ax.text(S_inst, 0.95,
            r'$S_{\rm inst} = 30\pi$',
            color=GOLD, fontsize=20, weight='bold', ha='center')
    ax.text(S_inst, 1.15,
            f'$={S_inst:.4f}$',
            color=GOLD, fontsize=14, ha='center', alpha=0.9)
    ax.text(S_inst, 1.40,
            'instanton action\n'
            r'on $\mathbb{CP}^3$',
            color=GOLD, fontsize=12, ha='center', style='italic',
            alpha=0.85)

    # ── Marker 2: master-relation prediction 196 ln φ ──────────────────────

    ax.scatter([S_phi], [y_axis], s=380, color=VIOLET,
               edgecolors=WHITE, linewidths=1.6, zorder=10)
    ax.vlines(S_phi, y_axis, -0.85, colors=VIOLET,
              linewidth=2.0, alpha=0.85, zorder=8)
    ax.text(S_phi, -0.95,
            r'$196 \ln\varphi$',
            color=VIOLET, fontsize=20, weight='bold', ha='center', va='top')
    ax.text(S_phi, -1.15,
            f'$={S_phi:.4f}$',
            color=VIOLET, fontsize=14, ha='center', va='top', alpha=0.9)
    ax.text(S_phi, -1.40,
            'master self-consistency\n'
            r'$(2\pi)^{27}\sqrt{\alpha} = \varphi^{98}$',
            color=VIOLET, fontsize=12, ha='center', va='top',
            style='italic', alpha=0.85)

    # ── Mismatch arc / annotation ──────────────────────────────────────────

    ax.annotate('',
                xy=(S_phi, 0.45), xytext=(S_inst, 0.45),
                arrowprops=dict(arrowstyle='<->', color=CYAN, linewidth=1.8,
                                alpha=0.85))
    ax.text(center, 0.55,
            f'exponent match: {mismatch_pct:.3f}% mismatch',
            color=CYAN, fontsize=14, weight='bold', ha='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#0a0a1a',
                      edgecolor=CYAN, alpha=0.95))

    # ── Title (single line, replaces in-figure block) ──────────────────────

    ax.text(0.5, 0.97,
            "Route III: the instanton action and the master relation "
            "predict the same exponent",
            transform=ax.transAxes, color=WHITE, fontsize=16, weight='bold',
            ha='center')

    # ── Compact key (lower-left) ───────────────────────────────────────────

    legend_text = (
        r"$30 = 1^2 + 2^2 + 3^2 + 4^2$" "  (4th pyramidal)\n"
        r"$196 = 2 \times 98$" "  (master-relation exponent)\n"
        r"$e^{-30\pi} \approx \varphi^{-196}$"
        "  (independent verification of master)"
    )
    ax.text(0.02, 0.04, legend_text,
            transform=ax.transAxes, color=WHITE, fontsize=11,
            verticalalignment='bottom',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#0a0a1a',
                      edgecolor=GRAY, alpha=0.92))

    # ── Cosmetics ─────────────────────────────────────────────────────────

    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(-2.0, 1.9)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    plt.tight_layout()
    save(fig, 'alpha-route3-instanton.png')

    # Print numerical sanity check
    print(f"  S_inst = 30π        = {S_inst:.6f}")
    print(f"  S_phi  = 196 ln(φ)  = {S_phi:.6f}")
    print(f"  mismatch            = {mismatch_pct:.4f}%")
    print(f"  e^{{-30π}}            = {e_S_inst:.6e}")
    print(f"  φ^{{-196}}            = {phi_neg_196:.6e}")
    print(f"  ratio               = {e_S_inst/phi_neg_196:.6f}")


def main():
    make_figure()


if __name__ == '__main__':
    main()

"""
fig_geometric_mean_hinge.py — the master self-consistency relation as
the placement of N_∞^{1/4} λ_C at the geometric midpoint of the
framework's length scales.

Visual claim: on a logarithmic length axis from λ_C (Compton wavelength
of the pion, ~10^{-15} m) out to R = sqrt(N_∞) λ_C (Hubble radius,
~10^{26} m), the relation places φ^{98} λ_C exactly at the geometric
midpoint.  Two halves of the axis (λ_C → midpoint and midpoint → R)
are equal in log-units, and each half is "× N_∞^{1/4}".

Run: python fig_geometric_mean_hinge.py
"""

import sys
sys.path.insert(0, '../')

import math
import numpy as np
import matplotlib.pyplot as plt

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE, BLUE, GREEN, RED

from ppm import constants as C


# ─── Compute the scales ─────────────────────────────────────────────────────

def compute_scales():
    # Pion Compton wavelength (the framework's local unit)
    lambda_C = C.HBAR_SI / (C.M_PI_KG * C.C_LIGHT_SI)
    # Boundary capacity
    PHI = (1 + math.sqrt(5)) / 2
    N_inf = PHI ** 392
    # Hubble radius and geometric midpoint
    R_hubble = math.sqrt(N_inf) * lambda_C
    midpoint = (N_inf ** 0.25) * lambda_C  # = sqrt(R * lambda_C)
    # Planck length (for context, falls left of lambda_C)
    L_PLANCK = math.sqrt(C.HBAR_SI * 6.674e-11 / C.C_LIGHT_SI ** 3)
    return {
        'lambda_C': lambda_C,
        'midpoint': midpoint,
        'R_hubble': R_hubble,
        'L_planck': L_PLANCK,
        'N_inf': N_inf,
        'phi': PHI,
        'phi98': PHI ** 98,
        'phi196': PHI ** 196,
    }


# ─── Figure ─────────────────────────────────────────────────────────────────

def make_figure(s):
    apply_style()

    fig, ax = plt.subplots(figsize=(15, 5.5), facecolor=BG)
    ax.set_facecolor(BG)

    # Log axis bounds — from a hair below λ_C to a hair above R, on log scale.
    log_lo = math.log10(s['lambda_C']) - 1.0
    log_hi = math.log10(s['R_hubble']) + 1.0

    # Draw the main horizontal axis
    y_axis = 0.0
    ax.hlines(y_axis, log_lo, log_hi, colors=WHITE, linewidth=2.0, zorder=4)

    # Three anchor scales: lambda_C (gold), midpoint (cyan), R (violet)
    log_lc = math.log10(s['lambda_C'])
    log_mid = math.log10(s['midpoint'])
    log_R = math.log10(s['R_hubble'])

    # Tick marks for the three anchors (oversized).
    # Colors are deliberately neutral (BLUE/GREEN/RED) — the framework's
    # gold/violet/cyan palette is reserved for τ-even / τ-odd /
    # actualization-event semantics, and would mislead here since all
    # three scales live on the same actualized boundary.
    C_LAMBDA = BLUE
    C_MID    = GREEN
    C_HUBBLE = RED
    for x, color, height in [(log_lc, C_LAMBDA, 0.45),
                             (log_mid, C_MID, 0.55),
                             (log_R, C_HUBBLE, 0.45)]:
        ax.vlines(x, y_axis - height/2, y_axis + height/2,
                  colors=color, linewidth=3.5, zorder=6)
        ax.scatter([x], [y_axis], s=180, color=color,
                   edgecolors=WHITE, linewidths=1.2, zorder=7)

    # Anchor labels (above the axis)
    ax.text(log_lc, 0.85, r'$\lambda_C$',
            color=C_LAMBDA, fontsize=24, weight='bold', ha='center')
    ax.text(log_lc, 1.30,
            'Compton wavelength\n(per-event scale)',
            color=C_LAMBDA, fontsize=13, ha='center', style='italic')
    ax.text(log_lc, -0.55, fr'$\sim 10^{{{log_lc:.0f}}}$ m',
            color=C_LAMBDA, fontsize=14, ha='center', alpha=0.85)

    ax.text(log_mid, 0.95, r'$\varphi^{98}\,\lambda_C\;=\;N_\infty^{1/4}\,\lambda_C$',
            color=C_MID, fontsize=22, weight='bold', ha='center')
    ax.text(log_mid, 1.40,
            "geometric midpoint\nof the framework's length hierarchy",
            color=C_MID, fontsize=13, ha='center', style='italic')
    midpoint_km = s['midpoint'] / 1000.0
    ax.text(log_mid, -0.55, fr'$\sim {midpoint_km:.0f}$ km',
            color=C_MID, fontsize=14, ha='center', alpha=0.85)

    ax.text(log_R, 0.85, r'$R = \sqrt{N_\infty}\,\lambda_C$',
            color=C_HUBBLE, fontsize=22, weight='bold', ha='center')
    ax.text(log_R, 1.30,
            'Hubble radius\n(global scale)',
            color=C_HUBBLE, fontsize=13, ha='center', style='italic')
    ax.text(log_R, -0.55, fr'$\sim 10^{{{log_R:.0f}}}$ m',
            color=C_HUBBLE, fontsize=14, ha='center', alpha=0.85)

    # Brackets showing each half is "× N_∞^{1/4}" wide in log-units
    bracket_y = -1.15
    bracket_h = 0.18
    # Left half
    ax.plot([log_lc, log_lc, log_mid, log_mid],
            [bracket_y + bracket_h, bracket_y, bracket_y, bracket_y + bracket_h],
            color=WHITE, linewidth=1.8, alpha=0.9, zorder=4)
    ax.text((log_lc + log_mid) / 2, bracket_y - 0.30,
            r'$\times\,N_\infty^{1/4}$',
            color=WHITE, fontsize=18, ha='center', weight='bold')
    ax.text((log_lc + log_mid) / 2, bracket_y - 0.62,
            f'({log_mid - log_lc:.1f} decades)',
            color=GRAY, fontsize=12, ha='center', style='italic')
    # Right half
    ax.plot([log_mid, log_mid, log_R, log_R],
            [bracket_y + bracket_h, bracket_y, bracket_y, bracket_y + bracket_h],
            color=WHITE, linewidth=1.8, alpha=0.9, zorder=4)
    ax.text((log_mid + log_R) / 2, bracket_y - 0.30,
            r'$\times\,N_\infty^{1/4}$',
            color=WHITE, fontsize=18, ha='center', weight='bold')
    ax.text((log_mid + log_R) / 2, bracket_y - 0.62,
            f'({log_R - log_mid:.1f} decades)',
            color=GRAY, fontsize=12, ha='center', style='italic')

    # Reference scales for context — tiny ticks below the axis, no labels
    # crowding the main story.
    ref_scales = [
        (-15, '1 fm',         'pion'),
        (-10, u'1 \u00c5',    'atom'),
        (-3,  '1 mm',          None),
        (0,   '1 m',          'human'),
        (7,   r'$10^{7}$ m',  'Earth'),
        (16,  r'$10^{16}$ m', 'light-year'),
        (21,  r'$10^{21}$ m', 'galaxy'),
    ]
    for lx, label, name in ref_scales:
        if log_lo + 0.4 < lx < log_hi - 0.4:
            ax.vlines(lx, y_axis - 0.10, y_axis + 0.10,
                      colors=GRAY, linewidth=1.0, alpha=0.55, zorder=3)
            tag = f'{label}'
            if name:
                tag = f'{tag}\n{name}'
            ax.text(lx, 0.30, tag,
                    color=GRAY, fontsize=10, ha='center', alpha=0.75,
                    style='italic')

    # Title block (bottom of figure, not the axes title — gives more room)
    ax.text((log_lo + log_hi) / 2, -2.55,
            "The self-consistency relation places "
            r"$\varphi^{98}$ at the geometric midpoint of the length hierarchy.",
            color=WHITE, fontsize=15, ha='center', style='italic')

    # The relation as a banner across the top
    ax.text((log_lo + log_hi) / 2, 2.30,
            r'$(2\pi)^{27}\sqrt{\alpha} \;=\; \varphi^{98} \;=\; N_\infty^{1/4}$',
            color=WHITE, fontsize=22, weight='bold', ha='center',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor='#0a0a1a', edgecolor=CYAN, alpha=0.95))

    # Axis cosmetics
    ax.set_xlim(log_lo, log_hi)
    ax.set_ylim(-3.0, 2.7)
    ax.set_xlabel(r'$\log_{10}(\mathrm{length} / \mathrm{m})$',
                  color=WHITE, fontsize=14)
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(colors=WHITE, labelsize=12)
    ax.grid(False)

    plt.tight_layout()
    save(fig, 'geometric-mean-hinge.png')


def main():
    s = compute_scales()
    print(f"  lambda_C  = {s['lambda_C']:.3e} m  (log10 = {math.log10(s['lambda_C']):.2f})")
    print(f"  midpoint  = {s['midpoint']:.3e} m  (log10 = {math.log10(s['midpoint']):.2f})")
    print(f"  R_hubble  = {s['R_hubble']:.3e} m  (log10 = {math.log10(s['R_hubble']):.2f})")
    print(f"  N_inf     = {s['N_inf']:.3e}")
    print(f"  phi^98    = {s['phi98']:.3e}")
    print(f"  phi^196   = {s['phi196']:.3e}")
    print(f"  phi^196 ≈ N_inf^{{1/2}}? {s['phi196']:.3e} vs {math.sqrt(s['N_inf']):.3e}")
    make_figure(s)


if __name__ == '__main__':
    main()

"""
fig_page_curve.py — Page curve: PPM monotonic prediction vs unitary recovery.

Both curves are computed from closed-form Schwarzschild evaporation. The two
predictions diverge after the Page time, providing a clean discriminator
between unitary and non-unitary fundamental dynamics.

Setup
-----
For a Schwarzschild black hole evaporating via Hawking radiation:

  dM/dt = -hbar c^6 / (15360 pi G^2 M^2)        (Hawking 1975)

Integrating gives M(t) = M_0 (1 - t/t_evap)^(1/3), with
t_evap = 5120 pi G^2 M_0^3 / (hbar c^4) the total evaporation time.

Bekenstein-Hawking entropy (in units of k_B):

  S_BH(M) = 4 pi G M^2 / (hbar c)

Hawking radiation entropy accumulates as the integral of dE/T_H where
T_H = hbar c^3 / (8 pi G M k_B). This gives, in the same units,

  S_rad(t) = (4 pi G / (hbar c)) * (M_0^2 - M(t)^2)
           = S_BH(0) * [1 - (1 - t/t_evap)^(2/3)].

Two predictions
---------------
* Standard unitary (Page 1993):
    S_ent(t) = min(S_rad(t), S_BH(t))
  rises with S_rad until the Page time t_Page where the two curves cross,
  then descends with S_BH back to zero at complete evaporation. The
  symmetry is the textbook signature of unitary information recovery.

* PPM:
    S_ent(t) = S_rad(t)
  rises monotonically; once a Hawking quantum has carried entropy out,
  subsequent emissions can only add. There is no interior subsystem to
  re-correlate with the radiation, so no information recovery is needed
  or possible. (See ch12-gravity §Black Hole Information Paradox.)

The Page time in this normalization satisfies S_rad(t_Page) = S_BH(t_Page),
giving t_Page / t_evap = 1 - (1/2)^(3/2) ~ 0.646, matching app-A.11's
quoted t_Page ~ 0.65 t_evap.

Run: python fig_page_curve.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt

from _style import (apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE,
                    GRAY, ORANGE, GREEN, BLUE, RED)


# ─── Closed-form curves (normalized: S_BH(0) = 1, t_evap = 1) ───────────────

def m_of_tau(tau):
    """Mass as fraction of initial mass."""
    return np.power(np.maximum(1.0 - tau, 0.0), 1.0 / 3.0)


def S_BH_normalized(tau):
    """Bekenstein-Hawking entropy in units of S_BH(0)."""
    return np.power(np.maximum(1.0 - tau, 0.0), 2.0 / 3.0)


def S_rad_normalized(tau):
    """Cumulative radiation entropy in units of S_BH(0)."""
    return 1.0 - np.power(np.maximum(1.0 - tau, 0.0), 2.0 / 3.0)


def S_ent_unitary(tau):
    """Standard Page curve: min(S_rad, S_BH)."""
    return np.minimum(S_rad_normalized(tau), S_BH_normalized(tau))


def S_ent_ppm(tau):
    """PPM prediction: S_rad alone, no turnover."""
    return S_rad_normalized(tau)


def t_page():
    """Page time where S_rad = S_BH; tau_Page = 1 - (1/2)^(3/2)."""
    return 1.0 - 0.5 ** 1.5


# ─── Figure ─────────────────────────────────────────────────────────────────

def main():
    apply_style()

    tau = np.linspace(0.0, 1.0, 4000)
    tp = t_page()
    peak_value = S_ent_unitary(tp)  # = S_rad(tp) = S_BH(tp) ~ 0.5

    # Split into pre-peak and post-peak segments
    pre  = tau <= tp
    post = tau >= tp
    tau_pre,  tau_post  = tau[pre],  tau[post]

    fig, ax = plt.subplots(figsize=(8.6, 5.4))

    # Reference: shrinking horizon entropy.
    ax.plot(tau, S_BH_normalized(tau), color=GRAY, linewidth=1.2,
            linestyle='--',
            label=r'$S_{\rm BH}(t)/S_{\rm BH}(0)$  (horizon entropy, '
                  r'declines as hole shrinks)',
            alpha=0.85)

    # Coincident rising segment: both predictions agree here.
    ax.plot(tau_pre, S_ent_ppm(tau_pre), color=WHITE, linewidth=3.4,
            label='Both predictions (rising, $t < t_{\\rm Page}$)')

    # Post-peak: predictions visibly fan out.
    ax.plot(tau_post, S_ent_unitary(tau_post), color=VIOLET, linewidth=2.6,
            label='Unitary (Page 1993): turns over and descends with '
                  r'$S_{\rm BH}(t)$')
    ax.plot(tau_post, S_ent_ppm(tau_post), color=GOLD, linewidth=2.6,
            label=r'PPM: continues as $S_{\rm rad}(t) = '
                  r'1 - S_{\rm BH}(t)/S_{\rm BH}(0)$')

    # Page-time peak marker (where the unitary curve turns over).
    ax.plot([tp], [peak_value], marker='o', markersize=9,
            markerfacecolor=CYAN, markeredgecolor=WHITE,
            markeredgewidth=1.2, zorder=5)
    ax.axvline(tp, color=CYAN, linewidth=1.0, linestyle='-', alpha=0.45,
               zorder=1)
    ax.annotate('Peak (unitary)\nat $t_{\\rm Page} \\approx 0.65\\, '
                't_{\\rm evap}$',
                xy=(tp, peak_value),
                xytext=(tp - 0.22, peak_value + 0.22),
                color=CYAN, fontsize=10, ha='left', va='bottom',
                arrowprops=dict(arrowstyle='->', color=CYAN,
                                alpha=0.85, lw=1.0))

    # Endpoint labels make the divergence final result obvious.
    ax.annotate(r'PPM: $S_{\rm BH}(0)$',
                xy=(1.0, 1.0), xytext=(0.78, 0.93),
                color=GOLD, fontsize=10, ha='left',
                arrowprops=dict(arrowstyle='->', color=GOLD,
                                alpha=0.75, lw=0.9))
    ax.annotate('Unitary: 0',
                xy=(1.0, 0.0), xytext=(0.78, 0.10),
                color=VIOLET, fontsize=10, ha='left',
                arrowprops=dict(arrowstyle='->', color=VIOLET,
                                alpha=0.75, lw=0.9))

    # Cosmetics
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel(r'$t / t_{\rm evap}$  (Hawking-evaporation time)')
    ax.set_ylabel(r'Entanglement entropy / $S_{\rm BH}(0)$')
    ax.set_title('Page Curve: PPM vs Unitary Predictions',
                 color=WHITE, pad=10)
    ax.legend(loc='upper left', fontsize=9.5, framealpha=0.85)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    save(fig, 'page-curve')


if __name__ == '__main__':
    main()

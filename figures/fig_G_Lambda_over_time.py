"""
fig_G_Lambda_over_time.py — G_eff(z) and Λ(z): where PPM and standard physics
agree, and where they don't.

Two panels share a redshift x-axis:

  Top: G_eff(z) / G_0 plotted as a multiplier on Newton's constant.
       Newton/GR sits flat at G_eff/G_0 = 1 — gravity is constant.
       PPM rises as (1+z)^{3/2} — gravity is amplified at earlier
       cosmic times because the holographic count N(z) was smaller.
       JWST early-galaxy excess data points overlaid as the testable
       observation.

  Bottom: Λ in m⁻² plotted vs redshift.
       PPM and standard cosmology AGREE: both treat Λ as constant.
       PPM additionally DERIVES the value Λ = 2(m_πc²)² / ((ℏc)² N_∞),
       where N_∞ = φ^{392}.  The naive QFT vacuum-energy estimate sits
       ~120 orders of magnitude above; the gap is the cosmological
       constant problem.  PPM has no such gap because Λ is not a vacuum
       energy in PPM — it is a topological floor set by the
       boundary capacity.

The figure makes the agreement/disagreement structure visible:
  - At z = 0 (today), every theory matches at the observed values.
  - At high z, G predictions diverge sharply — and JWST is sitting in
    the gap between PPM's curve and Newton's flat line.
  - For Λ, PPM and ΛCDM agree on time-evolution everywhere — the floor
    is invariant.  PPM's contribution is the geometric derivation of
    that floor, not a different time-evolution.

Run: python fig_G_Lambda_over_time.py
"""

import sys
sys.path.insert(0, '../')

import math
import numpy as np
import matplotlib.pyplot as plt

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE

from ppm.gravity import newton_constant
from ppm.cosmology import cosmological_constant


def main():
    apply_style()

    # ─── Compute framework values today ─────────────────────────────────────
    G_today = newton_constant()
    Lambda_today = cosmological_constant()
    G0_ppm = G_today['G_ppm_si']
    G0_obs = G_today['G_obs_si']
    Lam_ppm = Lambda_today['Lambda_m2']
    Lam_obs = 1.10e-52    # observed (Planck 2018)
    Lam_qft_estimate = 1.0  # QFT vacuum energy in m⁻² (order-of-magnitude)
    # Standard "120-order disaster" reference: ~10^120 above observed
    Lam_qft_ref = Lam_obs * 1e120

    # Redshift axis
    z_grid = np.linspace(0, 14, 200)

    # G_eff / G_0
    G_eff_PPM = (1 + z_grid) ** 1.5
    G_eff_Newton = np.ones_like(z_grid)

    # JWST early-galaxy mass excess (approximate, illustrative)
    z_jwst = np.array([6, 7.5, 9, 10.5, 12])
    excess_jwst = np.array([3, 6, 10, 16, 25])
    excess_jwst_err = np.array([1, 2, 3, 5, 9])

    # Λ — both PPM and ΛCDM are flat
    Lam_PPM_curve = np.full_like(z_grid, Lam_ppm)
    Lam_LCDM_curve = np.full_like(z_grid, Lam_obs)

    # ─── Figure ─────────────────────────────────────────────────────────────
    fig, (ax_G, ax_L) = plt.subplots(2, 1, figsize=(12, 10), facecolor=BG,
                                      sharex=True,
                                      gridspec_kw={'hspace': 0.18,
                                                    'height_ratios': [1, 1]})
    for ax in [ax_G, ax_L]:
        ax.set_facecolor(BG)
        ax.tick_params(colors=WHITE)
        ax.grid(True, alpha=0.3, color='#1a1a2e')

    # ─── Top panel: G_eff(z) / G_0 with explicit floor framing ─────────────
    # Floor (PPM derivation from N_∞): G_0 today; horizontal reference at 1.
    ax_G.axhline(y=1.0, color=CYAN, linestyle='-', linewidth=2.5, alpha=0.85,
                  label=r'FLOOR: $G_0$ derived from $N_\infty$'
                        r' (PPM static value)',
                  zorder=6)
    # Newton/GR effective = floor always
    ax_G.plot(z_grid, G_eff_Newton, color=GRAY, linewidth=2,
               linestyle='--', alpha=0.85,
               label=r'Newton / GR effective: $G_{\rm eff}(z) = G_0$ '
                     r'(sits AT floor at every epoch)',
               zorder=7)
    # PPM effective rises above floor at high z
    ax_G.plot(z_grid, G_eff_PPM, color=GOLD, linewidth=3,
               label=r'PPM effective: $G_{\rm eff}(z) = G_0 (1+z)^{3/2}$ '
                     r'(rises ABOVE floor at early epochs)',
               zorder=10)
    ax_G.fill_between(z_grid, G_eff_Newton, G_eff_PPM,
                       alpha=0.18, color=GOLD,
                       label='where PPM and Newton disagree (PPM enhancement)',
                       zorder=4)
    ax_G.errorbar(z_jwst, excess_jwst, yerr=excess_jwst_err,
                   fmt='o', color='#FFE066', markersize=10,
                   ecolor='#FFE066', elinewidth=1.5, capsize=4,
                   markeredgecolor=WHITE, markeredgewidth=1.0,
                   label='JWST early-galaxy mass excess (illustrative)',
                   zorder=11)
    ax_G.axvline(x=0, color=WHITE, linestyle=':', linewidth=1.0, alpha=0.5)
    # Epoch annotations
    ax_G.text(0.18, 56, 'today  (z=0)\nPPM effective\n= floor\n= Newton',
               color=CYAN, fontsize=9, style='italic', weight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a1a',
                          edgecolor=CYAN, alpha=0.9))
    ax_G.text(13.0, 56, 'early universe (z≈12)\nPPM effective far above floor\nNewton still = floor\nJWST sits in the gap',
               color=GOLD, fontsize=9, style='italic', weight='bold',
               ha='right',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a1a',
                          edgecolor=GOLD, alpha=0.9))
    ax_G.set_ylabel(r'$G_{\rm eff}(z) / G_0$  '
                    r'(multiples of the PPM floor)',
                    color=WHITE, fontsize=12, weight='bold')
    ax_G.set_title('Newton''s Constant — effective value vs PPM floor',
                    color=WHITE, fontsize=13, weight='bold')
    ax_G.set_ylim(0, max(G_eff_PPM) * 1.05)
    ax_G.legend(loc='upper left', fontsize=9,
                 facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.92)

    # ─── Bottom panel: Λ(z) — effective vs floor ──────────────────────────
    Lam_unit = 1e-52  # plot in units of 10^-52 m^-2
    floor_y = Lam_ppm / Lam_unit
    # The PPM-derived floor as a thick reference line
    ax_L.axhline(y=floor_y, color=CYAN, linestyle='-', linewidth=3, alpha=0.9,
                  label=r'FLOOR: $\Lambda = 2(m_\pi c^2)^2 / '
                        r'((\hbar c)^2 N_\infty)$  (PPM static value)',
                  zorder=10)
    # PPM effective — sits ON the floor at every epoch
    ax_L.plot(z_grid, Lam_PPM_curve / Lam_unit, color=CYAN, linewidth=4,
               alpha=0.6,
               label=r'PPM effective: $\Lambda(z) = $ floor everywhere '
                     r'(no time evolution)',
               zorder=9)
    # ΛCDM effective — also flat at observed value (matches the floor)
    ax_L.plot(z_grid, Lam_LCDM_curve / Lam_unit, color=GOLD, linewidth=2,
               linestyle='--', alpha=0.95,
               label=r'$\Lambda$CDM effective (observed): also sits AT '
                     r'the floor at every epoch',
               zorder=8)
    # Epoch annotations — same story at every z
    ax_L.text(0.18, 0.16, 'today  (z=0)\nPPM effective\n= floor = ΛCDM',
               color=CYAN, fontsize=9, style='italic', weight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a1a',
                          edgecolor=CYAN, alpha=0.9))
    ax_L.text(13.0, 0.16, 'early universe (z≈12)\nsame answer\nat every epoch',
               color=CYAN, fontsize=9, style='italic', weight='bold',
               ha='right',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a1a',
                          edgecolor=CYAN, alpha=0.9))
    # The "floor" callout above the line
    ax_L.text(7, floor_y + 0.40,
               r'the floor: derived from '
               r'$N_\infty = \varphi^{392}$ — topologically invariant',
               color=CYAN, fontsize=10, ha='center', weight='bold',
               style='italic',
               bbox=dict(boxstyle='round,pad=0.35',
                          facecolor='#0a0a1a',
                          edgecolor=CYAN, alpha=0.9))
    # QFT side note (linear-scale ceiling reference)
    ax_L.text(7, 1.85,
               r'QFT naive expectation lives '
               r'${\sim}10^{120}{\times}$ above the floor.'
               '\n'
               r'PPM has no such overhang: the floor IS the value '
               r'(the ``cosmological-constant problem'' is QFT''s, '
               r'not the framework''s).',
               color=ORANGE, fontsize=9.5, ha='center', style='italic',
               bbox=dict(boxstyle='round,pad=0.4',
                          facecolor='#0a0a1a',
                          edgecolor=ORANGE, alpha=0.85))
    ax_L.set_ylim(0, 2.2)
    ax_L.axvline(x=0, color=WHITE, linestyle=':', linewidth=1.0, alpha=0.5)
    ax_L.set_xlabel('Redshift z  (earlier universe →)',
                    color=WHITE, fontsize=12, weight='bold')
    ax_L.set_ylabel(r'$\Lambda$  [units of $10^{-52}$ m$^{-2}$]',
                    color=WHITE, fontsize=12, weight='bold')
    ax_L.set_title('Cosmological Constant — effective value vs PPM floor',
                    color=WHITE, fontsize=13, weight='bold')
    ax_L.legend(loc='center left', fontsize=9,
                 facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.92,
                 bbox_to_anchor=(0.0, 0.42))

    # Footer
    fig.suptitle(r'PPM Floor vs Effective Values Across Cosmic Time',
                  color=WHITE, fontsize=14, weight='bold', y=0.99)
    fig.text(0.5, 0.005,
              r'The framework derives a static FLOOR for both $G$ and $\Lambda$ '
              r'from $N_\infty = \varphi^{392}$.  '
              r'For $\Lambda$ the effective value sits AT the floor at every '
              r'epoch (PPM and $\Lambda$CDM agree).  '
              r'For $G$ the effective value sits at the floor today '
              r'but rises ABOVE it at early epochs — the regime where '
              r'PPM and Newton diverge and where JWST data lives.',
              ha='center', color=GRAY, fontsize=9, style='italic',
              wrap=True)

    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    save(fig, 'fig_G_Lambda_over_time.png')


if __name__ == '__main__':
    main()

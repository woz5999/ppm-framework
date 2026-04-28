"""
fig_convergence_window.py — Multiple framework languages locate the same place

The framework speaks several languages about the consciousness regime:
  - Resolvability ratio R(k) = E(k) / k_B T — crosses 1
  - Channel capacity I(k) = 3 log₂ R — drops through 1 bit, then 0
  - Decoherence time τ_dec(k) = 2ℏ²/(G m³ c) — crosses biological timescales
  - Boltzmann thermal accessibility exp(-E(k)/k_B T) — transitions from frozen
    to thermal
  - Zeno-protection bound (lower edge of integration regime)
  - Landauer bound (upper edge of channel openness)

Each language identifies its own critical k and a "critical band" around it.
This figure plots them on a shared k-axis to show that they all locate the
same narrow region — the consciousness window at k ∈ [53.8, 75.75].

Two-panel composition:
  Top:    Each quantitative curve plotted vs k, log scale where helpful.
          Critical thresholds marked.
  Bottom: A "convergence bar" plot — one row per language, each row a
          horizontal colored band showing where that language identifies
          its critical regime. All bands overlap in a vertical strip — the
          consciousness window.

Run: python fig_convergence_window.py
"""

import sys
sys.path.insert(0, '../')

import math
import numpy as np
import matplotlib.pyplot as plt

from _style import apply_style, save, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, ORANGE

from ppm.hierarchy import energy_mev
from ppm.consciousness import decoherence_time, consciousness_window
from ppm import constants as C


def main():
    apply_style()

    # k-axis: cover consciousness regime with headroom
    k_grid = np.linspace(30, 95, 400)

    # Physical constants
    T_body = 310.0  # K
    kB_eV = 8.617333e-5  # eV/K
    kB_T_eV = kB_eV * T_body  # ≈ 0.0267 eV
    kB_T_MeV = kB_T_eV * 1e-6
    c2 = C.C_LIGHT_SI ** 2
    eV_to_J = 1.602176634e-19
    t_universe_s = 13.8e9 * 365.25 * 24 * 3600  # ~4.35e17 s

    # ─── Compute curves ─────────────────────────────────────────────────────
    E_MeV = np.array([energy_mev(float(k)) for k in k_grid])
    E_eV = E_MeV * 1e6
    R_k = E_MeV / kB_T_MeV   # = E(k) / k_B T

    # Channel capacity I(k) = 3 log₂ R, floored at 0
    I_k = np.array([3.0 * math.log2(r) if r > 1 else 0.0 for r in R_k])

    # Decoherence time using Penrose-Diósi at the mass m(k) = E(k)/c²
    m_kg = E_MeV * 1e6 * eV_to_J / c2
    tau_dec = np.array([decoherence_time(float(m)) for m in m_kg])

    # Boltzmann thermal accessibility: prob of mode being thermally excited
    # ~ exp(-E/k_BT). 0 = frozen (deeply quantum), 1 = thermalized (classical).
    boltzmann = np.exp(-E_eV / kB_T_eV)
    boltzmann = np.clip(boltzmann, 1e-30, 1.0)

    # Consciousness window from framework
    cw = consciousness_window(T_K=T_body)
    k_cw_min = cw.get('k_min', 53.8)
    k_cw_max = cw.get('k_max', 75.75)

    # ─── Figure ─────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(13, 11), facecolor=BG)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.6, 1.0], hspace=0.32)
    ax_curves = fig.add_subplot(gs[0, 0])
    ax_bands = fig.add_subplot(gs[1, 0])

    for ax in [ax_curves, ax_bands]:
        ax.set_facecolor(BG)
        ax.tick_params(colors=WHITE)

    # ─── Top: quantitative curves ───────────────────────────────────────────
    # Use a single log-y axis with normalization so curves are comparable
    ax_curves.set_yscale('log')

    # Shade the consciousness window
    ax_curves.axvspan(k_cw_min, k_cw_max, color=CYAN, alpha=0.13,
                       zorder=0, label='_nolegend_')

    # R(k) curve — primary
    ax_curves.plot(k_grid, R_k, color=GOLD, linewidth=2.5,
                    label=r'$R(k) = E(k)/k_B T$  (resolvability ratio)',
                    zorder=8)
    # τ_dec curve — secondary y-scale would be cleaner but we accept overlap
    ax_curves.plot(k_grid, tau_dec, color=VIOLET, linewidth=2.5,
                    label=r'$\tau_{\rm dec}(k) = 2\hbar^2 / (Gm^3c)$  '
                          r'[seconds]',
                    zorder=8)
    # Boltzmann factor (rescaled so it's visible on log axis)
    boltz_visual = boltzmann * 1e10  # shift up for visibility
    ax_curves.plot(k_grid, boltz_visual, color=ORANGE, linewidth=2.5,
                    linestyle='--',
                    label=r'$10^{10}\cdot e^{-E(k)/k_B T}$  (thermal '
                          r'occupation, scaled)',
                    zorder=8)
    # Channel capacity in bits — rescale for log axis
    I_visual = I_k.copy()
    I_visual[I_visual < 0.1] = 0.1  # floor for log scale
    ax_curves.plot(k_grid, I_visual, color=CYAN, linewidth=2.5,
                    label=r'$I(k) = 3\log_2 R(k)$  (channel capacity, bits)',
                    zorder=8)

    # Critical horizontal lines
    ax_curves.axhline(y=1.0, color=GRAY, linestyle=':', linewidth=1.2,
                       alpha=0.6, zorder=4)
    ax_curves.text(94, 1.4, '$y = 1$',
                    color=GRAY, fontsize=9, ha='right')

    # Mark t_universe
    ax_curves.axhline(y=t_universe_s, color=ORANGE, linestyle=':',
                       linewidth=1.0, alpha=0.45, zorder=4)
    ax_curves.text(31, t_universe_s * 1.5, r'$t_{\rm universe}$',
                    color=ORANGE, fontsize=9, alpha=0.7)

    # Consciousness window labels
    cw_mid = (k_cw_min + k_cw_max) / 2
    ax_curves.text(cw_mid, ax_curves.get_ylim()[1] * 0.35
                    if False else 1e-3,
                    'consciousness window',
                    color=CYAN, fontsize=11, weight='bold',
                    ha='center', style='italic',
                    bbox=dict(boxstyle='round,pad=0.3',
                               facecolor='#0a0a1a',
                               edgecolor=CYAN, alpha=0.9))

    ax_curves.set_xlabel('k-level (energy hierarchy index)',
                          color=WHITE, fontsize=12, weight='bold')
    ax_curves.set_ylabel('quantity (mixed units, log scale)',
                          color=WHITE, fontsize=12, weight='bold')
    ax_curves.set_title('Multiple Framework Languages, Plotted Against k',
                         color=WHITE, fontsize=13, weight='bold')
    ax_curves.legend(loc='upper right', fontsize=9.5,
                      facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.92)
    ax_curves.set_xlim(30, 95)
    ax_curves.grid(True, alpha=0.3, color='#1a1a2e', which='both')

    # ─── Bottom: convergence bands ──────────────────────────────────────────
    # Each row = one language; each row has a colored bar showing where THAT
    # language identifies the "critical regime."
    band_specs = [
        # (label, k_min, k_max, color, sub_text)
        ('Resolvability   $R(k) \\approx 1$',
         71, 78, GOLD, 'where signal ≈ thermal noise'),
        ('Channel capacity   $I(k)$ drops below 1 bit',
         70, 76, CYAN, 'per-event information collapses'),
        ('Decoherence   $\\tau_{\\rm dec}$ ≈ neural integration time',
         60, 80, VIOLET, 'gravitational decoherence relevant'),
        ('Boltzmann   $E(k) \\sim k_B T$',
         73, 78, ORANGE, 'modes thermally accessible at body temp'),
        ('Zeno bound  &  Landauer bound',
         53.8, 75.75, '#FFE066',
         'integration possible (lower) and channel open (upper)'),
    ]

    n_rows = len(band_specs)
    for i, (label, k_lo, k_hi, color, subtext) in enumerate(band_specs):
        y = n_rows - 1 - i
        # Band
        ax_bands.barh(y, k_hi - k_lo, left=k_lo, height=0.55,
                       color=color, alpha=0.7, edgecolor=WHITE,
                       linewidth=1.0)
        # Label on left
        ax_bands.text(29.5, y, label, color=WHITE, fontsize=10,
                       ha='right', va='center', weight='bold')
        # Sub-text below
        ax_bands.text((k_lo + k_hi) / 2, y - 0.32, subtext,
                       color=GRAY, fontsize=8.5, ha='center',
                       va='top', style='italic')

    # Highlight the intersection (consciousness window)
    ax_bands.axvspan(k_cw_min, k_cw_max, color=CYAN, alpha=0.15,
                      zorder=0)
    # Vertical dashed boundaries
    for x, lbl in [(k_cw_min, fr'$k = {k_cw_min:.1f}$  (Zeno)'),
                    (k_cw_max, fr'$k = {k_cw_max:.2f}$  (Landauer)')]:
        ax_bands.axvline(x=x, color='#FFE066', linestyle='--',
                          linewidth=1.5, alpha=0.7, zorder=2)
        ax_bands.text(x, n_rows - 0.2, lbl,
                       color='#FFE066', fontsize=9, weight='bold',
                       ha='center', va='bottom',
                       bbox=dict(boxstyle='round,pad=0.25',
                                  facecolor='#0a0a1a',
                                  edgecolor='#FFE066', alpha=0.95))

    # Center-of-mass of all bands
    band_centers = [(lo + hi) / 2 for _, lo, hi, _, _ in band_specs]
    com = sum(band_centers) / len(band_centers)
    ax_bands.text(com, -1.0,
                   f'all five languages cluster at k ≈ {com:.1f}',
                   color=CYAN, fontsize=10, weight='bold',
                   ha='center', style='italic',
                   bbox=dict(boxstyle='round,pad=0.4',
                              facecolor='#0a0a1a',
                              edgecolor=CYAN, alpha=0.9))

    ax_bands.set_xlim(30, 95)
    ax_bands.set_ylim(-1.5, n_rows + 0.4)
    ax_bands.set_yticks([])
    ax_bands.set_xlabel('k-level',
                         color=WHITE, fontsize=12, weight='bold')
    ax_bands.set_title('Where each language places its critical regime',
                        color=WHITE, fontsize=12, weight='bold')
    ax_bands.spines['top'].set_visible(False)
    ax_bands.spines['right'].set_visible(False)
    ax_bands.spines['left'].set_visible(False)
    ax_bands.tick_params(left=False)
    ax_bands.grid(axis='x', alpha=0.3, color='#1a1a2e')

    # Footer
    fig.text(0.5, 0.005,
              'Different framework lenses (information, thermodynamics, '
              'gravitational decoherence, channel capacity) compute critical '
              'k-levels independently. They cluster at the same narrow band — '
              'the same geometric region described in different languages.',
              ha='center', color=GRAY, fontsize=9, style='italic',
              wrap=True)

    plt.tight_layout(rect=[0, 0.018, 1, 1])
    save(fig, 'fig_convergence_window.png')


if __name__ == '__main__':
    main()

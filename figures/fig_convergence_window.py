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

This script produces TWO independent figures (each rendered at single-panel
size with large fonts):

  1. consciousness-convergence-curves.png — quantitative curves of R, τ_dec,
     Boltzmann, I plotted vs k.  Lives in the technical document
     (ch07-info-thermo).

  2. consciousness-convergence-window.png — "rosetta" bands chart showing
     where each language places its critical regime; all converge at k ≈ 71.
     Lives in the ontology document (ch19-boundaries §Quantum-Thermal Threshold).

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


# ─── Compute shared data ────────────────────────────────────────────────────

def compute_data():
    k_grid = np.linspace(30, 95, 400)

    T_body = 310.0
    kB_eV = 8.617333e-5
    kB_T_eV = kB_eV * T_body
    kB_T_MeV = kB_T_eV * 1e-6
    c2 = C.C_LIGHT_SI ** 2
    eV_to_J = 1.602176634e-19
    t_universe_s = 13.8e9 * 365.25 * 24 * 3600

    E_MeV = np.array([energy_mev(float(k)) for k in k_grid])
    E_eV = E_MeV * 1e6
    R_k = E_MeV / kB_T_MeV

    I_k = np.array([3.0 * math.log2(r) if r > 1 else 0.0 for r in R_k])

    m_kg = E_MeV * 1e6 * eV_to_J / c2
    tau_dec = np.array([decoherence_time(float(m)) for m in m_kg])

    boltzmann = np.exp(-E_eV / kB_T_eV)
    boltzmann = np.clip(boltzmann, 1e-30, 1.0)

    cw = consciousness_window(T_K=T_body)
    k_cw_min = cw.get('k_min', 53.8)
    k_cw_max = cw.get('k_max', 75.75)

    return {
        'k_grid': k_grid, 'R_k': R_k, 'I_k': I_k,
        'tau_dec': tau_dec, 'boltzmann': boltzmann,
        't_universe_s': t_universe_s,
        'k_cw_min': k_cw_min, 'k_cw_max': k_cw_max,
    }


# ─── Figure 1: curves only (technical doc) ───────────────────────────────────

def make_curves_figure(data):
    apply_style()

    k_grid = data['k_grid']
    R_k = data['R_k']
    I_k = data['I_k']
    tau_dec = data['tau_dec']
    boltzmann = data['boltzmann']
    t_universe_s = data['t_universe_s']
    k_cw_min = data['k_cw_min']
    k_cw_max = data['k_cw_max']

    fig, ax = plt.subplots(figsize=(14, 9), facecolor=BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=WHITE, labelsize=16)
    ax.set_yscale('log')

    # Consciousness window shading
    ax.axvspan(k_cw_min, k_cw_max, color=CYAN, alpha=0.13,
               zorder=0, label='_nolegend_')

    # Curves
    ax.plot(k_grid, R_k, color=GOLD, linewidth=3.0,
            label=r'$R(k) = E(k)/k_B T$  (resolvability ratio)', zorder=8)
    ax.plot(k_grid, tau_dec, color=VIOLET, linewidth=3.0,
            label=r'$\tau_{\rm dec}(k) = 2\hbar^2 / (Gm^3c)$  [seconds]',
            zorder=8)
    boltz_visual = boltzmann * 1e10
    ax.plot(k_grid, boltz_visual, color=ORANGE, linewidth=3.0,
            linestyle='--',
            label=r'$10^{10}\cdot e^{-E(k)/k_B T}$  (thermal occupation, scaled)',
            zorder=8)
    I_visual = I_k.copy()
    I_visual[I_visual < 0.1] = 0.1
    ax.plot(k_grid, I_visual, color=CYAN, linewidth=3.0,
            label=r'$I(k) = 3\log_2 R(k)$  (channel capacity, bits)', zorder=8)

    # Reference lines
    ax.axhline(y=1.0, color=GRAY, linestyle=':', linewidth=1.6,
               alpha=0.75, zorder=4)
    ax.text(94, 1.4, r'$y = 1$',
            color=GRAY, fontsize=18, ha='right', weight='bold')

    ax.axhline(y=t_universe_s, color=ORANGE, linestyle=':',
               linewidth=1.4, alpha=0.55, zorder=4)
    ax.text(31, t_universe_s * 1.5, r'$t_{\rm universe}$',
            color=ORANGE, fontsize=18, alpha=0.85, weight='bold')

    # Consciousness window label
    cw_mid = (k_cw_min + k_cw_max) / 2
    ax.text(cw_mid, 1e-3, 'consciousness window',
            color=CYAN, fontsize=22, weight='bold',
            ha='center', style='italic',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor='#0a0a1a', edgecolor=CYAN, alpha=0.9))

    ax.set_xlabel('k-level (energy hierarchy index)',
                  color=WHITE, fontsize=22, weight='bold')
    ax.set_ylabel('quantity (mixed units, log scale)',
                  color=WHITE, fontsize=22, weight='bold')
    ax.set_title('Framework languages of the consciousness regime, vs. $k$',
                 color=WHITE, fontsize=24, weight='bold', pad=15)
    ax.legend(loc='upper right', fontsize=17,
              facecolor='#0a0a1a', edgecolor=WHITE, framealpha=0.92)
    ax.set_xlim(30, 95)
    ax.grid(True, alpha=0.3, color='#1a1a2e', which='both')

    plt.tight_layout()
    save(fig, 'consciousness-convergence-curves.png')


# ─── Figure 2: rosetta bands only (ontology doc) ────────────────────────────

def make_rosetta_figure(data):
    apply_style()

    k_cw_min = data['k_cw_min']
    k_cw_max = data['k_cw_max']

    # Each entry: (legend_label, k_lo, k_hi, color)
    band_specs = [
        ('Resolvability   $R(k) \\approx 1$\n(signal $\\approx$ thermal noise)',
         71, 78, GOLD),
        ('Channel capacity   $I(k) < 1$ bit\n(per-event information collapses)',
         70, 76, CYAN),
        ('Decoherence   $\\tau_{\\rm dec} \\sim$ integration time\n(gravitational decoherence relevant)',
         60, 80, VIOLET),
        ('Boltzmann   $E(k) \\sim k_B T$\n(modes thermally accessible)',
         73, 78, ORANGE),
        ('Zeno + Landauer bounds\n(integration window opens / closes)',
         53.8, 75.75, '#FFE066'),
    ]

    fig, ax = plt.subplots(figsize=(16, 8), facecolor=BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=WHITE, labelsize=18)

    n_rows = len(band_specs)
    for i, (label, k_lo, k_hi, color) in enumerate(band_specs):
        y = n_rows - 1 - i
        ax.barh(y, k_hi - k_lo, left=k_lo, height=0.6,
                color=color, alpha=0.85, edgecolor=WHITE, linewidth=1.2,
                label=label)

    # Consciousness window highlight
    ax.axvspan(k_cw_min, k_cw_max, color=CYAN, alpha=0.13, zorder=0)

    # Zeno / Landauer dashed boundaries
    for x, lbl in [(k_cw_min, fr'$k = {k_cw_min:.1f}$  (Zeno)'),
                   (k_cw_max, fr'$k = {k_cw_max:.2f}$  (Landauer)')]:
        ax.axvline(x=x, color='#FFE066', linestyle='--',
                   linewidth=2.0, alpha=0.75, zorder=2)
        ax.text(x, n_rows - 0.15, lbl,
                color='#FFE066', fontsize=17, weight='bold',
                ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.35',
                          facecolor='#0a0a1a',
                          edgecolor='#FFE066', alpha=0.95))

    # Hierarchy anchors along the wider k-axis
    anchors = [
        (1, 'Planck'),
        (16, 'Pati--Salam'),
        (44.5, 'EWSB'),
        (51, 'QCD'),
    ]
    for k_anchor, name in anchors:
        ax.axvline(x=k_anchor, color=GRAY, linestyle=':',
                   linewidth=1.2, alpha=0.55, zorder=1)
        ax.text(k_anchor, -1.4, name,
                color=GRAY, fontsize=13, ha='center', va='top',
                style='italic')

    band_centers = [(lo + hi) / 2 for _, lo, hi, _ in band_specs]
    com = sum(band_centers) / len(band_centers)
    ax.text(com, -0.95,
            f'all five languages cluster at $k \\approx {com:.1f}$',
            color=CYAN, fontsize=20, weight='bold',
            ha='center', style='italic',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor='#0a0a1a',
                      edgecolor=CYAN, alpha=0.9))

    ax.set_xlim(1, 95)
    ax.set_ylim(-1.7, n_rows + 0.6)
    ax.set_yticks([])
    ax.set_xlabel('k-level',
                  color=WHITE, fontsize=22, weight='bold')
    ax.set_title('Where each framework language places its critical regime',
                 color=WHITE, fontsize=22, weight='bold', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(left=False)
    ax.grid(axis='x', alpha=0.3, color='#1a1a2e')

    # Legend lives in the wide empty left side of the chart
    leg = ax.legend(loc='center left', bbox_to_anchor=(0.0, 0.55),
                    fontsize=14, facecolor='#0a0a1a',
                    edgecolor=WHITE, framealpha=0.92,
                    labelcolor=WHITE, handlelength=2.2,
                    handleheight=1.6, borderpad=1.0,
                    labelspacing=1.0, title='Framework languages',
                    title_fontsize=16)
    leg.get_title().set_color(WHITE)
    leg.get_title().set_weight('bold')

    plt.tight_layout()
    save(fig, 'consciousness-convergence-window.png')


def main():
    data = compute_data()
    make_curves_figure(data)
    make_rosetta_figure(data)


if __name__ == '__main__':
    main()

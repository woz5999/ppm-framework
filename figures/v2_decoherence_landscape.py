"""
Decoherence-k landscape — phase diagram showing quantum/classical/consciousness regimes.

X-axis: k-level (energy hierarchy parameter)
Y-axis: temperature T (log scale)
Color field: resolvability ratio R(k,T) = E(k)/(k_B T)
  - R >> 1 (violet): quantum regime, CP³ dominates
  - R ≈ 1 (cyan): consciousness window, Z₂ boundary
  - R << 1 (gold): classical regime, RP³ dominates

Usage:
    python v2_decoherence_landscape.py              # ontology version
    python v2_decoherence_landscape.py --technical  # technical version
"""
import os
import sys
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
OUTPUT_DIR = os.path.join(REPO_ROOT, 'figures', 'computed')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── PPM constants ──
M_PI_MEV = 140.0          # pion mass (MeV)
K_REF = 51.0              # k-level for pion mass
K_PLANCK = 1.0
K_BREAK = 16.25           # Pati-Salam
K_EWSB = 44.5             # electroweak symmetry breaking
K_CONFINE = 51.0           # QCD confinement
K_CONSCIOUS_LO = 53.8      # consciousness window lower bound
K_CONSCIOUS_HI = 75.75     # consciousness window upper bound
K_CONSCIOUS = 75.35        # registry value (310 K crossing)
T_BIO = 310.0              # biological temperature (K)

KB_EV = 8.617333262e-5     # Boltzmann constant (eV/K)
KB_MEV = KB_EV * 1e-6      # Boltzmann constant (MeV/K)  [1 MeV = 1e6 eV]


def E_k(k):
    """Energy at k-level in MeV."""
    return M_PI_MEV * (2 * np.pi) ** ((K_REF - k) / 2.0)


def R_field(k_arr, T_arr):
    """Resolvability ratio R(k,T) = E(k) / (k_B T)."""
    K, T = np.meshgrid(k_arr, T_arr)
    E = M_PI_MEV * (2 * np.pi) ** ((K_REF - K) / 2.0)
    return E / (KB_MEV * T)


def T_at_R1(k):
    """Temperature where R=1 for given k."""
    return E_k(k) / KB_MEV


# ── Color themes ──
THEMES = {
    'ontology': {
        'BG':      '#0d1117',
        'VIOLET':  '#7B68EE',
        'CYAN':    '#00CED1',
        'GOLD':    '#D4A843',
        'WHITE':   '#eeeeee',
        'DIM':     '#888888',
        'DIM_LT':  '#999999',
        'output':  'v2_decoherence_landscape.png',
    },
    'technical': {
        'BG':      '#040812',
        'VIOLET':  '#7B68EE',
        'CYAN':    '#00CED1',
        'GOLD':    '#D4A843',
        'WHITE':   '#eeeeee',
        'DIM':     '#888888',
        'DIM_LT':  '#999999',
        'output':  'v2_decoherence_landscape_tech.png',
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--technical', action='store_true')
    args = parser.parse_args()

    theme = 'technical' if args.technical else 'ontology'
    T = THEMES[theme]
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, T['output'])

    BG     = T['BG']
    VIOLET = T['VIOLET']
    CYAN   = T['CYAN']
    GOLD   = T['GOLD']
    WHITE  = T['WHITE']
    DIM    = T['DIM']
    DIM_LT = T['DIM_LT']

    # ── Build the R(k,T) field ──
    k_arr = np.linspace(1, 82, 800)
    T_lo, T_hi = 1e-1, 1e18      # temperature range (K) — up to ~GUT scale
    T_arr = np.logspace(np.log10(T_lo), np.log10(T_hi), 600)
    R = R_field(k_arr, T_arr)

    # Map R to color: log10(R) from -4 to +4
    log_R = np.log10(np.clip(R, 1e-6, 1e6))
    # Normalize: -4 → 0.0 (gold), 0 → 0.5 (cyan), +4 → 1.0 (violet)
    norm = (log_R + 4.0) / 8.0
    norm = np.clip(norm, 0, 1)

    # Build colormap: gold → cyan → violet
    # Parse hex to RGB
    def hex2rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    g_rgb = hex2rgb(GOLD)
    c_rgb = hex2rgb(CYAN)
    v_rgb = hex2rgb(VIOLET)

    cmap_data = {
        'red':   [(0.0, g_rgb[0], g_rgb[0]),
                  (0.5, c_rgb[0], c_rgb[0]),
                  (1.0, v_rgb[0], v_rgb[0])],
        'green': [(0.0, g_rgb[1], g_rgb[1]),
                  (0.5, c_rgb[1], c_rgb[1]),
                  (1.0, v_rgb[1], v_rgb[1])],
        'blue':  [(0.0, g_rgb[2], g_rgb[2]),
                  (0.5, c_rgb[2], c_rgb[2]),
                  (1.0, v_rgb[2], v_rgb[2])],
    }
    cmap = LinearSegmentedColormap('ppm_R', cmap_data, N=512)

    # ── Plot ──
    fig, ax = plt.subplots(figsize=(14, 8), facecolor=BG)
    ax.set_facecolor(BG)

    # Image
    extent = [k_arr[0], k_arr[-1], np.log10(T_lo), np.log10(T_hi)]
    ax.imshow(norm, aspect='auto', origin='lower', extent=extent,
              cmap=cmap, interpolation='bilinear')

    # ── R=1 curve ──
    k_curve = np.linspace(1, 82, 500)
    T_R1 = T_at_R1(k_curve)
    log_T_R1 = np.log10(T_R1)
    ax.plot(k_curve, log_T_R1, color=CYAN, lw=2.5, alpha=0.9, zorder=5)

    # ── R=1 band (half-decade above and below) ──
    band_width = 0.5  # decades
    ax.fill_between(k_curve,
                    log_T_R1 - band_width,
                    log_T_R1 + band_width,
                    color=CYAN, alpha=0.08, zorder=3)
    ax.plot(k_curve, log_T_R1 - band_width, color=CYAN, lw=0.8, alpha=0.3,
            linestyle='--', zorder=4)
    ax.plot(k_curve, log_T_R1 + band_width, color=CYAN, lw=0.8, alpha=0.3,
            linestyle='--', zorder=4)

    # ── T_bio horizontal line ──
    log_T_bio = np.log10(T_BIO)
    ax.axhline(log_T_bio, color=GOLD, lw=2.0, alpha=0.8, linestyle='-',
               zorder=6)
    ax.text(3, log_T_bio + 0.5, r'$T_{\rm bio} = 310\;$K',
            color=GOLD, fontsize=14, fontfamily='serif', zorder=7,
            alpha=0.95, fontweight='medium')

    # ── Label background style ──
    LABEL_BG = dict(boxstyle='round,pad=0.3', facecolor=BG, edgecolor='none',
                    alpha=0.75)

    # ── Consciousness-possible region ──
    # 2D region along R≈1 band for k > K_CONSCIOUS_LO
    # Bounded by R ∈ [0.1, 10] (i.e. log10(R) ∈ [-1, 1])
    # R = E(k)/(k_B T)  →  T = E(k)/(k_B R)
    # Upper edge (R=0.1): T_upper = E(k)/(k_B * 0.1) = 10 * T_R1
    # Lower edge (R=10):  T_lower = E(k)/(k_B * 10)  = 0.1 * T_R1
    k_region = np.linspace(K_CONSCIOUS_LO, 82, 300)
    T_R1_region = T_at_R1(k_region)
    log_T_upper = np.log10(10.0 * T_R1_region)  # R = 0.1
    log_T_lower = np.log10(0.1 * T_R1_region)   # R = 10
    # Clip to plot bounds
    log_T_upper = np.clip(log_T_upper, np.log10(T_lo), np.log10(T_hi))
    log_T_lower = np.clip(log_T_lower, np.log10(T_lo), np.log10(T_hi))
    ax.fill_between(k_region, log_T_lower, log_T_upper,
                    color=CYAN, alpha=0.18, zorder=2.5)
    # Visible border on the region — use lighter gray for contrast
    REGION_BORDER = '#AACCCC'
    ax.plot(k_region, log_T_upper, color=REGION_BORDER, lw=1.5, alpha=0.6,
            linestyle='--', zorder=3)
    ax.plot(k_region, log_T_lower, color=REGION_BORDER, lw=1.5, alpha=0.6,
            linestyle='--', zorder=3)
    # Left edge of region — solid vertical bar
    ax.plot([K_CONSCIOUS_LO, K_CONSCIOUS_LO],
            [log_T_lower[0], log_T_upper[0]],
            color=REGION_BORDER, lw=2.0, alpha=0.7, linestyle='-', zorder=3)

    # ── Dot where T_bio intersects R=1 ──
    # k at R=1 for T_bio: E(k)/(k_B T_bio) = 1 → k = K_REF - 2*log(T_bio*k_B/M_PI)/log(2π)
    k_R1_at_Tbio = K_REF - 2.0 * np.log(KB_MEV * T_BIO / M_PI_MEV) / np.log(2 * np.pi)
    ax.plot(k_R1_at_Tbio, log_T_bio, 'o', color=CYAN, markersize=10,
            markeredgecolor=WHITE, markeredgewidth=1.5, zorder=9)
    ax.text(k_R1_at_Tbio + 0.5, log_T_bio - 1.2,
            f'$k_c \\approx {k_R1_at_Tbio:.1f}$',
            ha='left', va='top', fontsize=13, color=CYAN,
            fontfamily='serif', fontweight='medium', zorder=9,
            bbox=LABEL_BG)

    # ── Distinguished k-level markers ──
    k_marks = [
        (K_PLANCK,  'Planck'),
        (K_BREAK,   'Pati-Salam'),
        (K_EWSB,    'EWSB'),
        (K_CONFINE, 'confinement'),
    ]
    log_T_max = np.log10(T_hi)
    log_T_min = np.log10(T_lo)
    for km, lbl in k_marks:
        ax.axvline(km, color=DIM, lw=1.0, alpha=0.3, linestyle='--',
                   zorder=1)
        # Place label at top of visible area
        ax.text(km, log_T_max - 0.3, lbl, ha='center', fontsize=12,
                color=WHITE, alpha=0.7, fontfamily='serif', rotation=0,
                va='top', zorder=7,
                bbox=dict(boxstyle='round,pad=0.15', facecolor=BG,
                          edgecolor='none', alpha=0.7))

    # ── Region labels ──

    # Quantum regime — place in solidly violet region, above T_bio line
    ax.text(20, 7, r'$R \gg 1$' + '\nquantum regime',
            ha='center', va='center', fontsize=16, color='#B0A0FF',
            fontfamily='serif', fontweight='medium', zorder=8,
            bbox=LABEL_BG, linespacing=1.6)
    ax.text(20, 5, 'fiber modes hard-quantized\nparticles, atoms stable',
            ha='center', va='center', fontsize=12, color=DIM_LT,
            fontfamily='serif', fontstyle='italic', zorder=8,
            bbox=LABEL_BG, linespacing=1.5)

    # Classical regime — place in solidly gold region, clear of confinement bar
    ax.text(68, 16, r'$R \ll 1$' + '\nclassical regime',
            ha='center', va='center', fontsize=16, color='#C49530',
            fontfamily='serif', fontweight='medium', zorder=8,
            bbox=LABEL_BG, linespacing=1.6)
    ax.text(68, 13.5, 'actualization events unresolvable\nagainst thermal noise',
            ha='center', va='center', fontsize=12, color=DIM_LT,
            fontfamily='serif', fontstyle='italic', zorder=8,
            bbox=LABEL_BG, linespacing=1.5)

    # R=1 label — on the cyan band, clear of vertical bars
    # At k=55, R=1 is at log10(T) ≈ 7.6
    ax.text(55, 9,
            r'$R(k,T) = 1$',
            ha='center', va='center', fontsize=15, color=CYAN,
            fontfamily='serif', fontweight='medium', zorder=8,
            bbox=LABEL_BG)

    # Consciousness-possible region label — inside the shaded region
    ax.text(68, 5.5,
            'consciousness\npossible',
            ha='center', va='center', fontsize=14, color=CYAN,
            fontfamily='serif', fontweight='medium', zorder=8,
            bbox=LABEL_BG, linespacing=1.4, alpha=0.9)

    # ── Axes ──
    ax.set_xlabel('$k$-level', fontsize=15, color=WHITE, fontfamily='serif',
                  labelpad=8)
    ax.set_ylabel(r'Temperature  $T$  (K)', fontsize=15, color=WHITE,
                  fontfamily='serif', labelpad=8)

    # x-axis
    ax.set_xlim(1, 82)
    x_ticks = [1, 10, 16.25, 20, 30, 40, 44.5, 51, 54, 60, 70, 80]
    x_labels = ['1', '10', '16', '20', '30', '40', '44.5', '51', '54', '60', '70', '80']
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, fontsize=11, color=WHITE)

    # y-axis: log10(T), show as actual T values
    ax.set_ylim(np.log10(T_lo), np.log10(T_hi))
    y_tick_vals = [-1, 2, 5, 8, 11, 14, 17]
    y_tick_labels = [r'$10^{' + str(v) + r'}$' for v in y_tick_vals]
    ax.set_yticks(y_tick_vals)
    ax.set_yticklabels(y_tick_labels, fontsize=11, color=WHITE)

    # Secondary x-axis for energy
    ax2 = ax.twiny()
    ax2.set_xlim(1, 82)
    e_ticks = [1, 16.25, 44.5, 51, 75.35]
    e_labels = [
        r'$10^{19}$ GeV',
        r'$10^{13}$ GeV',
        r'$55$ GeV',
        r'$140$ MeV',
        r'$27$ meV',
    ]
    ax2.set_xticks(e_ticks)
    ax2.set_xticklabels(e_labels, fontsize=10, color=DIM_LT)
    ax2.tick_params(axis='x', colors=DIM_LT, length=4)
    ax2.set_xlabel('$E(k)$', fontsize=13, color=DIM_LT, fontfamily='serif',
                   labelpad=8)

    # Tick styling
    ax.tick_params(axis='both', colors=WHITE, length=5)
    for spine in ax.spines.values():
        spine.set_color(DIM)
        spine.set_alpha(0.4)
    for spine in ax2.spines.values():
        spine.set_color(DIM)
        spine.set_alpha(0.4)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200, facecolor=BG, bbox_inches='tight',
                pad_inches=0.2)
    plt.close()
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()

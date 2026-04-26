"""
v2_decoherence_k_scale.py — Decoherence time vs k-level.

Plots the framework's intrinsic gravitational decoherence ceiling as
a function of the k-energy hierarchy.  Each k indexes an energy via
E(k) = m_pi c^2 (2*pi)^((51-k)/2); the candidate "object at k" has
rest mass m(k) = E(k)/c^2.

Curve: tau_grav(k) = hbar^2 / (G m(k)^3 c)
    Penrose-Diosi gravitational decoherence time.  Depends only on
    mass and fundamental constants.  This is a ceiling: any actual
    environmental coupling makes the realised coherence time shorter.
    The framework's intrinsic prediction.

Regime bands:
    - Above t_universe (4.35e17 s): gravity is irrelevant
      (coherence is bounded only by environment, never by gravity)
    - Below tau_Planck: gravitational decoherence formula breaks down,
      coherent superposition is gravitationally forbidden

Named objects mark physical systems on the gravitational curve:
    electron, proton, 10 kDa protein, ribosome (~4 MDa), 1 fg virus,
    1 pg bacterium, 1 microgram dust grain.  A red star at (k~37.2,
    tau=1 s) marks the Penrose mass scale where the framework's
    intrinsic prediction enters the experimentally testable regime.
    A separate annotation notes that human-scale masses lie far below
    the Planck floor (gravitationally forbidden).

The Joos-Zeh environmental decoherence rate in the long-wavelength
regime is mass-independent (Lambda_th * Delta x^2), so it would appear
as a horizontal floor, not a curve, and is omitted to keep the figure
focused on the framework's intrinsic mass-dependent prediction.  The
caption notes the environmental floor in plain terms.

Usage:
    python v2_decoherence_k_scale.py              # ontology palette
    python v2_decoherence_k_scale.py --technical  # technical palette
"""
import os
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
OUTPUT_DIR = os.path.join(REPO_ROOT, 'figures', 'computed')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── physical constants (SI) ──
G_NEWTON = 6.67430e-11
HBAR = 1.054571817e-34
C_LIGHT = 2.99792458e8
KB = 1.380649e-23
EV_J = 1.602176634e-19

# pion mass in kg
M_PI_KG = 0.13957 * 1e9 * EV_J / C_LIGHT**2
K_REF = 51.0

# environmental parameters (room-temperature atmosphere)
T_AIR = 300.0
N_AIR = 2.5e25            # number density (m^-3)
SIGMA_AIR = 1e-19         # scattering cross-section (m^2)
M_AIR = 5e-26             # mean air-molecule mass (kg)
DX_ENV = 1.0e-9           # superposition separation (m)

# Planck time and age of universe (s)
TAU_PLANCK = np.sqrt(HBAR * G_NEWTON / C_LIGHT**5)   # ~5.39e-44
T_UNIV = 4.35e17                                     # ~13.8 Gyr


def m_k(k):
    """Object mass at level k: m = E(k)/c^2 with E(k) = m_pi c^2 (2pi)^((51-k)/2)."""
    return M_PI_KG * (2.0 * np.pi) ** ((K_REF - k) / 2.0)


def k_of_mass(m):
    """Inverse: which k-level corresponds to a given mass (in kg)?"""
    return K_REF - 2.0 * np.log(m / M_PI_KG) / np.log(2.0 * np.pi)


def tau_grav(k):
    """Penrose-Diosi gravitational decoherence time (s)."""
    m = m_k(k)
    return HBAR**2 / (G_NEWTON * m**3 * C_LIGHT)


def lambda_air():
    """Joos-Zeh thermal-scattering localization rate (1 / (m^2 s))."""
    return (8.0 * np.sqrt(2.0 * np.pi) * N_AIR * SIGMA_AIR
            * np.sqrt(M_AIR * KB * T_AIR)) / (3.0 * HBAR**2)


def tau_env(k):
    """Joos-Zeh decoherence time at room-temp air, Delta x = 1 nm (s)."""
    return 1.0 / (lambda_air() * DX_ENV**2 * m_k(k))


# ── color themes ──
THEMES = {
    'ontology': {
        'BG':      '#0d1117',
        'VIOLET':  '#7B68EE',
        'CYAN':    '#00CED1',
        'GOLD':    '#D4A843',
        'WHITE':   '#f0f0f0',
        'DIM':     '#888888',
        'DIM_LT':  '#aaaaaa',
        'VIO_LT':  '#C4B8FF',
        'GOLD_LT': '#F0D880',
        'CYAN_LT': '#40E8E0',
        'RED_DIM': '#DD6666',
        'RED_HOT': '#FF7A6E',
        'output':  'v2_decoherence_k_scale.png',
    },
    'technical': {
        'BG':      '#040812',
        'VIOLET':  '#7B68EE',
        'CYAN':    '#00CED1',
        'GOLD':    '#D4A843',
        'WHITE':   '#f0f0f0',
        'DIM':     '#888888',
        'DIM_LT':  '#aaaaaa',
        'VIO_LT':  '#C4B8FF',
        'GOLD_LT': '#F0D880',
        'CYAN_LT': '#40E8E0',
        'RED_DIM': '#DD6666',
        'RED_HOT': '#FF7A6E',
        'output':  'v2_decoherence_k_scale_tech.png',
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--technical', action='store_true')
    args = parser.parse_args()

    theme_name = 'technical' if args.technical else 'ontology'
    T = THEMES[theme_name]
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, T['output'])

    BG      = T['BG']
    VIOLET  = T['VIOLET']
    CYAN    = T['CYAN']
    GOLD    = T['GOLD']
    WHITE   = T['WHITE']
    DIM     = T['DIM']
    DIM_LT  = T['DIM_LT']
    VIO_LT  = T['VIO_LT']
    GOLD_LT = T['GOLD_LT']
    CYAN_LT = T['CYAN_LT']
    RED_DIM = T['RED_DIM']
    RED_HOT = T['RED_HOT']

    # ── compute curves ──
    k_arr = np.linspace(1.0, 80.0, 1600)
    tg = tau_grav(k_arr)

    # ── plot ──
    fig, ax = plt.subplots(figsize=(15, 9.2), facecolor=BG)
    ax.set_facecolor(BG)

    Y_LO, Y_HI = 1e-46, 1e28
    K_LO, K_HI = 1.0, 80.0

    # ── shaded regime bands ──
    # Top band: gravity is irrelevant (coherence ceiling > age of universe)
    ax.axhspan(T_UNIV, Y_HI, color=VIOLET, alpha=0.07, zorder=0.1)
    # Bottom band: gravitationally forbidden (formula breakdown below Planck)
    ax.axhspan(Y_LO, TAU_PLANCK, color=RED_HOT, alpha=0.08, zorder=0.1)

    # Regime labels — bold band names only.  The condition
    # (tau_grav > t_univ etc.) is conveyed by the band itself plus the
    # caption.  Adding it here as a subtitle just collides with the
    # horizontal reference lines.  Keep it clean.
    ax.text(28.0, np.sqrt(T_UNIV * Y_HI),
            r'GRAVITY IRRELEVANT  ($\tau_{\rm grav} > t_{\rm univ}$)',
            ha='center', va='center', fontsize=13, color=VIO_LT,
            fontweight='bold', alpha=0.97, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.40', facecolor=BG,
                      edgecolor=VIO_LT, alpha=0.95, lw=0.9), zorder=3)

    ax.text(58.0, np.sqrt(Y_LO * TAU_PLANCK),
            r'GRAVITATIONALLY FORBIDDEN  ($\tau_{\rm grav} < \tau_{\rm Planck}$)',
            ha='center', va='center', fontsize=13, color=RED_HOT,
            fontweight='bold', alpha=0.97, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.40', facecolor=BG,
                      edgecolor=RED_HOT, alpha=0.95, lw=0.9), zorder=3)

    # ── horizontal reference timescales ──
    refs = [
        (TAU_PLANCK,  r'$\tau_{\rm Planck}$',          RED_HOT),
        (1e-15,       r'$1\,$fs',                       DIM_LT),
        (1e-9,        r'$1\,$ns',                       DIM_LT),
        (1e-3,        r'$1\,$ms (neural)',              CYAN_LT),
        (1.0,         r'$1\,$s',                        DIM_LT),
        (3.15e7,      r'$1\,$yr',                       DIM_LT),
        (T_UNIV,      r'$t_{\rm univ}$',                VIO_LT),
    ]
    for y, lbl, c in refs:
        ax.axhline(y, color=c, lw=0.7, alpha=0.40, linestyle=':', zorder=1)
        # Tick labels on the LEFT edge.  GRAVITY IRRELEVANT label sits
        # mid-left at very high y, well above the topmost tick; object
        # labels (left-of-dot) start at k>=4 so the leftmost half-unit is
        # clear.
        ax.text(K_LO + 0.35, y * 1.7, lbl, ha='left', va='bottom',
                fontsize=10, color=c, alpha=0.95,
                bbox=dict(boxstyle='round,pad=0.15', facecolor=BG,
                          edgecolor='none', alpha=0.85), zorder=2)

    # ── vertical k-markers ──
    # Planck (k=1) is now anchored by the gold "Planck origin" dot at the
    # curve's bottom-left, so it is omitted from the top-of-chart markers.
    k_marks = [
        (16.25, 'Pati-Salam',      VIOLET),
        (44.5,  'EWSB',            CYAN),
        (51.0,  r'$m_\pi$',        GOLD),
        (57.0,  r'$m_e$',          GOLD),
        (75.4,  'cons. scale',     CYAN_LT),
    ]
    for k, lbl, c in k_marks:
        ax.axvline(k, color=c, lw=1.0, alpha=0.35, linestyle='--', zorder=1)
        # Place k-marker labels along the TOP edge of the plot just below
        # the secondary x-axis tick labels (out of the way of curve content)
        ax.text(k, Y_HI / 4.0, lbl, ha='center', va='top', fontsize=10,
                color=c, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.15', facecolor=BG,
                          edgecolor=c, alpha=0.85, lw=0.7), zorder=4)

    # ── primary curve: gravitational decoherence ceiling ──
    ax.semilogy(k_arr, tg, color=VIOLET, lw=3.8, alpha=0.97, zorder=6)

    # Curve identifier — small label tucked at the top-right end of the
    # curve, where it leaves the plot at upper-right.  The y-axis already
    # names the quantity; this just attaches the formula to the line.
    ax.text(K_HI - 1.2, tau_grav(K_HI - 1.2) * 10.0**(-2.2),
            r'$\tau_{\rm grav}(k) = \dfrac{\hbar^{2}}{G\,m(k)^{3}\,c}$',
            ha='right', va='top', fontsize=12, color=VIO_LT,
            bbox=dict(boxstyle='round,pad=0.30', facecolor=BG,
                      edgecolor=VIOLET, alpha=0.9, lw=0.8),
            zorder=7)

    # ── Planck origin: where the curve emerges ──
    # At k=1, m(k) = m_pi (2pi)^25 ~ 2.3e-8 kg (the Planck mass) and
    # tau_grav = hbar^2/(G m^3 c) coincides with tau_Planck.  The curve
    # starts at exactly this corner — the (Planck mass, Planck time)
    # intersection.  Anchor it visibly with a gold dot at the bottom-left.
    k_pl = K_LO
    tau_pl_curve = tau_grav(k_pl)
    ax.plot(k_pl, tau_pl_curve, marker='o', markersize=14, color=GOLD,
            markeredgecolor=WHITE, markeredgewidth=1.8, zorder=11)
    # Place the label well above the dust-grain label, with a longer
    # arrow back down to the dot so the two labels don't compete.
    ax.annotate('Planck origin\n'
                r'$m(1) = m_{\rm Planck}$,  '
                r'$\tau_{\rm grav}(1) = \tau_{\rm Planck}$',
                xy=(k_pl, tau_pl_curve),
                xytext=(k_pl + 1.5, tau_pl_curve * 10.0**12.0),
                fontsize=10, color=GOLD,
                ha='left', va='bottom',
                bbox=dict(boxstyle='round,pad=0.28', facecolor=BG,
                          edgecolor=GOLD, alpha=0.95, lw=0.9),
                arrowprops=dict(arrowstyle='->', color=GOLD,
                                lw=1.2, alpha=0.9,
                                connectionstyle='arc3,rad=-0.25'),
                zorder=11)

    # ── Penrose-scale callout (where tau_grav crosses 1 s) ──
    m_penrose = (HBAR**2 / (G_NEWTON * C_LIGHT)) ** (1.0/3.0)
    k_penrose = k_of_mass(m_penrose)
    ax.plot(k_penrose, 1.0, marker='*', markersize=24, color=RED_HOT,
            markeredgecolor=WHITE, markeredgewidth=1.6, zorder=10)
    ax.annotate('Penrose-scale superposition\n'
                r'$\tau_{\rm grav} = 1\,$s at $m \approx 8\!\times\!10^{-23}\,$kg'
                '\n(experimentally testable regime)',
                xy=(k_penrose, 1.0), xytext=(k_penrose + 6, 1e-9),
                fontsize=11, color=RED_HOT, fontweight='bold',
                ha='left', va='top',
                bbox=dict(boxstyle='round,pad=0.30', facecolor=BG,
                          edgecolor=RED_HOT, alpha=0.95, lw=1.0),
                arrowprops=dict(arrowstyle='->', color=RED_HOT,
                                lw=1.4, alpha=0.9),
                zorder=11)

    # ── named objects on the tau_grav curve ──
    # Each entry: (label, mass_kg, dx_units, dy_decades, ha, va)
    # The curve sweeps from lower-left to upper-right at slope ~1.2 dec/k.
    # Below-and-RIGHT of each dot is the open lower-right wedge.  Labels
    # alternate above/below to avoid stacking.  Reduced from 7 to 5 objects
    # to keep the density readable.
    objects = [
        ('electron\n($9.1\\times10^{-31}\\,$kg)',         9.109e-31,  -8,   -2.6, 'right', 'top'),
        ('proton\n($1.7\\times10^{-27}\\,$kg)',           1.673e-27,  -8,   -2.6, 'right', 'top'),
        ('10\\,kDa protein\n($1.7\\times10^{-23}\\,$kg)', 1.66e-23,   -8,   -2.6, 'right', 'top'),
        ('virus capsid\n($10^{-18}\\,$kg, 1\\,fg)',       1e-18,      -8,   -2.6, 'right', 'top'),
        ('dust grain\n($10^{-9}\\,$kg, 1\\,$\\mu$g)',     1e-9,       +5,   +2.4, 'left',  'bottom'),
    ]
    for name, mass, dx_lab, dy_dec, ha_lab, va_lab in objects:
        k_obj = k_of_mass(mass)
        if k_obj < K_LO or k_obj > K_HI:
            continue
        tau_obj = tau_grav(k_obj)
        # Dot on the curve
        ax.plot(k_obj, tau_obj, marker='o', markersize=10, color=WHITE,
                markeredgecolor=VIOLET, markeredgewidth=1.8, zorder=9)
        x_label = k_obj + dx_lab
        if x_label < K_LO + 0.5:
            x_label = K_LO + 0.5
            ha_lab = 'left'
        if x_label > K_HI - 1.5:
            x_label = K_HI - 1.5
            ha_lab = 'right'
        y_label = tau_obj * (10.0 ** dy_dec)
        ax.annotate(name,
                    xy=(k_obj, tau_obj),
                    xytext=(x_label, y_label),
                    fontsize=10, color=WHITE,
                    ha=ha_lab, va=va_lab,
                    bbox=dict(boxstyle='round,pad=0.25', facecolor=BG,
                              edgecolor=DIM_LT, alpha=0.94, lw=0.6),
                    arrowprops=dict(arrowstyle='-', color=DIM_LT,
                                    lw=0.7, alpha=0.7,
                                    connectionstyle='arc3,rad=0.15'),
                    zorder=8)

    # (Macroscopic objects (gram-and-up) plug into the formula and give
    #  tau_grav values 14-28 decades below the Planck floor.  That point
    #  belongs in the caption, not on the plot — it would just clutter
    #  the lower-left corner.)

    # ── axes ──
    ax.set_xlim(K_LO, K_HI)
    ax.set_ylim(Y_LO, Y_HI)
    ax.set_yscale('log')

    ax.set_xlabel(r'$k$-level   (low $k$ = large mass; high $k$ = small mass)',
                  fontsize=14, color=WHITE, fontfamily='serif', labelpad=10)
    ax.set_ylabel(r'Decoherence time  $\tau_{\rm grav}$  (s, log scale)',
                  fontsize=14, color=WHITE, fontfamily='serif', labelpad=10)

    x_ticks = [1, 10, 16.25, 20, 30, 40, 44.5, 51, 57, 65, 75.4]
    x_lbl = ['1', '10', '16', '20', '30', '40', '44.5', '51', '57', '65', '75']
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_lbl, fontsize=11, color=WHITE)

    ax.tick_params(axis='both', colors=WHITE, length=5)
    for spine in ax.spines.values():
        spine.set_color(DIM)
        spine.set_alpha(0.4)

    # ── secondary x-axis: energy ──
    ax2 = ax.twiny()
    ax2.set_xlim(K_LO, K_HI)
    e_ticks = [1, 16.25, 44.5, 51, 57, 75.4]
    e_lbls = [
        r'$10^{19}\,$GeV',
        r'$10^{13}\,$GeV',
        r'$55\,$GeV',
        r'$140\,$MeV',
        r'$0.5\,$MeV',
        r'$27\,$meV',
    ]
    ax2.set_xticks(e_ticks)
    ax2.set_xticklabels(e_lbls, fontsize=10, color=DIM_LT)
    ax2.tick_params(axis='x', colors=DIM_LT, length=4)
    ax2.set_xlabel(r'$E(k)$', fontsize=12, color=DIM_LT,
                   fontfamily='serif', labelpad=8)
    for spine in ax2.spines.values():
        spine.set_color(DIM)
        spine.set_alpha(0.4)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200, facecolor=BG, bbox_inches='tight',
                pad_inches=0.3)
    plt.close()
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()

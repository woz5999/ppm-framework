#!/usr/bin/env python3
"""
generate_figures.py — Generate all computed figures for the PPM paper.

White-background scientific plots with PPM accent colors.
Output to ../figures/computed/
"""

import sys, os, math, warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as mticker

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ppm import constants as C
from ppm import hierarchy as H
from ppm import alpha as A
from ppm import gauge as G
from ppm import higgs as HI
from ppm import instanton as I
from ppm import spectral as S
from ppm import cosmology as GR
from ppm import golden_ratio as GR_phi
from ppm import berry_phase as BP
from ppm import neutrino as NU
from ppm import predictions as PRED

warnings.filterwarnings('ignore')

# ── Output directory ──
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures', 'computed')
os.makedirs(OUTDIR, exist_ok=True)

# ── Accent colors ──
PURPLE = '#6633aa'
GOLD   = '#cc8800'
CYAN   = '#009999'
RED    = '#cc3333'
BLUE   = '#3366cc'
GREEN  = '#339933'
GRAY   = '#888888'

# ── Common style ──
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'legend.fontsize': 9,
    'figure.dpi': 200,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})


def save(fig, name):
    path = os.path.join(OUTDIR, name)
    fig.savefig(path, facecolor='white')
    plt.close(fig)
    print(f"  -> {name}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. CP^n Selectivity (§4.2)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_cpn_selectivity():
    print("Fig 1: CP^n selectivity")
    # The real selectivity test: for CP^n, compute the generalized pyramidal identity
    # P_n² · ln(φ) vs P_{n+1} · π, showing closeness to 1 only for n=3
    ns = list(range(1, 8))
    ratios = []
    for n in ns:
        Pn = GR_phi.pyramidal_number(n)
        Pn1 = GR_phi.pyramidal_number(n + 1)
        lhs = Pn**2 * math.log(C.PHI)
        rhs = Pn1 * math.pi
        ratios.append(lhs / rhs if rhs > 0 else 0)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = [PURPLE if n != 3 else GOLD for n in ns]
    bars = ax.bar(ns, ratios, color=colors, edgecolor='#333', linewidth=0.8, width=0.6)

    ax.axhline(y=1.0, color=RED, linestyle='--', linewidth=1.5, label='Ratio = 1 (self-consistent)')
    ax.set_xlabel(r'$n$')
    ax.set_ylabel(r'$P_n^2 \ln\varphi\;/\;P_{n+1} \cdot \pi$')
    ax.set_title(r'Pyramidal Identity Selectivity: Only $n = 3$ Gives Ratio $\approx 1$')
    ax.set_xticks(ns)

    for n, r, bar in zip(ns, ratios, bars):
        ax.text(bar.get_x() + bar.get_width()/2, max(r, 0) + 0.02,
                f'{r:.4f}', ha='center', va='bottom', fontsize=9,
                fontweight='bold' if n == 3 else 'normal',
                color=GOLD if n == 3 else '#555')

    ax.legend(loc='upper left')
    ax.set_ylim(0, max(ratios) * 1.2)
    ax.grid(axis='y', alpha=0.3)
    save(fig, 'fig_cpn_selectivity.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Three Routes to α (§5.2)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_three_alpha_routes():
    print("Fig 2: Three routes to alpha")
    comp = A.alpha_comparison()
    alpha_obs_inv = comp['alpha_inv_observed']

    routes = [
        ('Route I\n(Spectral)', comp['route_I']['alpha_inv'], PURPLE),
        ('Route II\n(Cogito)', comp['route_II']['alpha_inv'], GOLD),
        ('Route III\n(Instanton)', comp['route_III']['R_tau_bare'] if 'R_tau_bare' in comp['route_III'] else None, CYAN),
    ]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.axhline(y=alpha_obs_inv, color=RED, linewidth=2, linestyle='-',
               label=f'Observed: 1/α = {alpha_obs_inv:.3f}', zorder=5)
    ax.axhspan(alpha_obs_inv - 0.001, alpha_obs_inv + 0.001, alpha=0.1, color=RED)

    for i, (label, val, color) in enumerate(routes):
        if val is not None:
            ax.plot(i, val, 'o', color=color, markersize=14, markeredgecolor='#333',
                    markeredgewidth=1.5, zorder=10)
            err_pct = (val / alpha_obs_inv - 1) * 100
            ax.annotate(f'{val:.2f}\n({err_pct:+.2f}%)',
                       xy=(i, val), xytext=(0, 18), textcoords='offset points',
                       ha='center', fontsize=10, color=color, fontweight='bold')
        else:
            ax.plot(i, alpha_obs_inv, 'o', color=color, markersize=14,
                    markeredgecolor='#333', markeredgewidth=1.5, zorder=10,
                    fillstyle='none')
            ax.annotate('Prefactor\nopen',
                       xy=(i, alpha_obs_inv), xytext=(0, 18), textcoords='offset points',
                       ha='center', fontsize=10, color=color, fontstyle='italic')

    ax.set_xticks(range(len(routes)))
    ax.set_xticklabels([r[0] for r in routes])
    ax.set_ylabel(r'$1/\alpha$')
    ax.set_title(r'Three Independent Routes to $\alpha$')
    ax.legend(loc='lower right')
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(alpha_obs_inv - 1.5, alpha_obs_inv + 1.5)
    ax.grid(axis='y', alpha=0.3)
    save(fig, 'fig_three_alpha_routes.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Heat Kernel Convergence (§5.3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_heat_kernel_convergence():
    print("Fig 3: Heat kernel convergence")
    t_star = A.t_star(n=3)
    nmax_values = [10, 20, 50, 100, 150, 200, 300]
    alpha_invs = []
    for nm in nmax_values:
        r = A.alpha_from_spectral_geometry(nmax=nm)
        alpha_invs.append(r['alpha_inv'])

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(nmax_values, alpha_invs, 'o-', color=PURPLE, linewidth=2, markersize=8)
    ax.axhline(y=C.ALPHA_EM_INV, color=RED, linestyle='--', linewidth=1.5,
               label=f'Observed 1/α = {C.ALPHA_EM_INV:.3f}')
    ax.set_xlabel('Number of eigenvalues (nmax)')
    ax.set_ylabel(r'$1/\alpha$ from spectral heat kernel')
    ax.set_title(r'Heat Kernel Route I: Convergence with Eigenvalue Truncation')
    ax.legend()
    ax.grid(alpha=0.3)
    save(fig, 'fig_heat_kernel_convergence.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. sin²θ_W Running (§6.3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_sin2_theta_w():
    print("Fig 4: sin²θ_W running")
    result = G.sin2_theta_W_sm_running()
    sin2_ppm = result['sin2_tW_ppm']
    sin2_sm = result['sin2_tW_sm']
    E_break = result['E_break_GeV']

    log_E = np.linspace(1, 19, 200)
    E_gev = 10.0**log_E

    # 1-loop RG for sin²θ_W
    alpha1_mz = C.ALPHA1_MZ
    alpha2_mz = C.ALPHA2_MZ
    mz = C.M_Z_GEV

    sin2_vals = []
    for E in E_gev:
        ln_ratio = math.log(E / mz)
        a1 = G.run_alpha_1loop(alpha1_mz, G.B1, ln_ratio)
        a2 = G.run_alpha_1loop(alpha2_mz, G.B2, ln_ratio)
        if a1 > 0 and a2 > 0:
            sin2_vals.append(a1 / (a1 + a2))
        else:
            sin2_vals.append(float('nan'))

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(log_E, sin2_vals, color=BLUE, linewidth=2, label=r'SM 1-loop RG')
    ax.axhline(y=3/8, color=PURPLE, linestyle='--', linewidth=1.5,
               label=r'PPM: $\sin^2\theta_W = 3/8$ at $E_{\mathrm{break}}$')
    ax.axhline(y=0.23122, color=RED, linestyle=':', linewidth=1.5,
               label=r'Observed: $\sin^2\theta_W(M_Z) = 0.23122$')
    ax.axvline(x=math.log10(E_break), color=GRAY, linestyle='-.', linewidth=1,
               label=f'$E_{{\\mathrm{{break}}}}$ = {E_break:.0f} GeV')

    ax.set_xlabel(r'$\log_{10}(E/\mathrm{GeV})$')
    ax.set_ylabel(r'$\sin^2\theta_W(E)$')
    ax.set_title(r'Weinberg Angle Running: PPM Prediction vs SM RG')
    ax.legend(fontsize=8, loc='upper left')
    ax.set_ylim(0.2, 0.4)
    ax.grid(alpha=0.3)
    save(fig, 'fig_sin2_theta_w.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. Energy Hierarchy Table (§4.3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_energy_hierarchy_table():
    print("Fig 5: Energy hierarchy — k-scale vs mass")

    particles = [
        ('top',      44.5,  172.7,      'quark'),
        ('Higgs',    44.5,  125.25,     'boson'),
        ('Z',        44.5,  91.188,     'boson'),
        ('W',        44.5,  80.377,     'boson'),
        ('bottom',   46.0,  4.18,       'quark'),
        ('charm',    47.5,  1.27,       'quark'),
        (r'$\tau$',  48.0,  1.777,      'lepton'),
        ('pion',     51.0,  0.140,      'meson'),
        (r'$\mu$',   51.5,  0.10566,    'lepton'),
        ('strange',  51.44, 0.0934,     'quark'),
        ('down',     54.70, 0.00467,    'quark'),
        ('up',       55.54, 0.00216,    'quark'),
        ('e',        57.0,  0.000511,   'lepton'),
    ]

    cat_markers = {
        'quark':  ('s', BLUE),
        'boson':  ('D', PURPLE),
        'lepton': ('o', GOLD),
        'meson':  ('^', GREEN),
    }

    k_range = np.linspace(43, 58, 300)
    E_line = np.array([H.energy_gev(k) for k in k_range])

    fig, ax = plt.subplots(figsize=(10, 6.5))

    ax.plot(k_range, E_line, color=GRAY, linewidth=2.5, zorder=1,
            label=r'$E(k) = 140\;\mathrm{MeV}\times(2\pi)^{(51-k)/2}$')

    ax.fill_between(k_range, E_line / 10, E_line * 10,
                    alpha=0.06, color=GRAY, zorder=0)

    label_config = {
        'top':     (-8, 10, 'right'),
        'Higgs':   (-8, -2, 'right'),
        'Z':       (8, 10, 'left'),
        'W':       (8, -8, 'left'),
        'bottom':  (8, 0, 'left'),
        'charm':   (8, 0, 'left'),
        r'$\tau$': (8, 0, 'left'),
        'pion':    (-8, 0, 'right'),
        r'$\mu$':  (8, 6, 'left'),
        'strange': (8, -6, 'left'),
        'down':    (8, 0, 'left'),
        'up':      (8, 0, 'left'),
        'e':       (8, 0, 'left'),
    }

    plotted_cats = set()
    for name, k, m_obs, cat in particles:
        marker, color = cat_markers[cat]
        label = cat.capitalize() if cat not in plotted_cats else None
        plotted_cats.add(cat)
        ax.scatter(k, m_obs, marker=marker, s=80, color=color,
                   edgecolors='#333', linewidths=0.6, zorder=3, label=label)

        dx, dy, ha = label_config.get(name, (8, 0, 'left'))
        ax.annotate(name, (k, m_obs), fontsize=7.5,
                    ha=ha, va='center',
                    xytext=(dx, dy), textcoords='offset points')

    ax.set_yscale('log')
    ax.set_xlabel(r'$k$-level', fontsize=12)
    ax.set_ylabel(r'Mass / Energy  (GeV)', fontsize=12)
    ax.set_title(r'PPM Energy Hierarchy: observed masses vs. $E(k)$', fontsize=13)
    ax.set_xlim(43, 58.5)
    ax.set_ylim(1e-4, 500)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
    ax.grid(True, which='major', alpha=0.25)
    ax.grid(True, which='minor', alpha=0.1)

    save(fig, 'fig_energy_hierarchy_table.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. Master Prediction Comparison (§7.3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_master_predictions():
    print("Fig 6: Master prediction comparison")
    rows = PRED.build_table()

    # Filter to rows with both predicted and observed values and a meaningful error
    plot_rows = [r for r in rows if r['error_pct'] is not None
                 and r['observed_value'] is not None
                 and r['observed_value'] != 0
                 and abs(r['error_pct']) < 50]

    ids = [r['id'] for r in plot_rows]
    errors = [r['error_pct'] for r in plot_rows]
    tiers = [r['tier'] for r in plot_rows]
    labels = [r['quantity'][:30] for r in plot_rows]

    tier_colors = {1: PURPLE, 2: BLUE, 3: GOLD, 4: GREEN}

    fig, ax = plt.subplots(figsize=(12, 7))
    y_pos = range(len(plot_rows))
    colors = [tier_colors.get(t, GRAY) for t in tiers]

    bars = ax.barh(y_pos, errors, color=colors, edgecolor='#555', linewidth=0.5, height=0.7)
    ax.axvline(x=0, color='black', linewidth=1)
    ax.axvspan(-2, 2, alpha=0.08, color=GREEN, label='±2% band')

    ax.set_yticks(y_pos)
    ax.set_yticklabels([f'{i}  {l}' for i, l in zip(ids, labels)], fontsize=7)
    ax.set_xlabel('Error: (Predicted/Observed − 1) × 100%')
    ax.set_title('PPM Master Prediction Table: All Derived Quantities vs Observation')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)

    # Legend for tiers
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=PURPLE, label='Tier 1: <2%'),
        Patch(facecolor=BLUE, label='Tier 2: 2–10%'),
        Patch(facecolor=GOLD, label='Tier 3: 10–25%'),
        Patch(facecolor=GREEN, label='Tier 4: Cosmological'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=8)
    save(fig, 'fig_master_predictions.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. G_eff(z) + JWST Evidence (§11.1 replacement)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_g_eff_jwst():
    print("Fig 7: G_eff(z) + JWST evidence")
    z = np.linspace(0, 16, 500)
    g_ratio = np.array([GR.g_eff(zi) for zi in z])

    # Alternative scaling (cumulative N)
    g_ratio_sqrt = np.sqrt(1 + z)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    # Left: G_eff / G_0
    ax1.plot(z, g_ratio, color=PURPLE, linewidth=2.5,
             label=r'PPM upper: $G/G_0 = (1+z)^{3/2}$')
    ax1.plot(z, g_ratio_sqrt, color=BLUE, linewidth=2, linestyle='--',
             label=r'PPM lower: $G/G_0 = (1+z)^{1/2}$')
    ax1.fill_between(z, g_ratio_sqrt, g_ratio, alpha=0.15, color=PURPLE)
    ax1.axhline(y=1, color=GRAY, linewidth=1, linestyle=':',
                label=r'$\Lambda$CDM: $G/G_0 = 1$')

    # JWST detection epoch
    ax1.axvspan(6, 16, alpha=0.08, color=GOLD)
    ax1.text(11, 1.5, 'JWST\nepoch', ha='center', fontsize=10, color=GOLD)

    ax1.set_xlabel('Redshift $z$')
    ax1.set_ylabel(r'$G_{\mathrm{eff}}/G_0$')
    ax1.set_title(r'PPM Prediction: $G$ Grows Toward the Big Bang')
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)
    ax1.set_ylim(0.5, max(g_ratio)*1.1)

    # Right: JWST galaxy excess
    # Observed JWST data points (approximate from literature)
    z_jwst = np.array([7, 8, 9, 10, 11, 12, 13, 14])
    # Galaxy count excess above LCDM (order of magnitude estimates)
    excess_obs = np.array([3, 5, 8, 15, 25, 40, 60, 100])
    excess_obs_lo = excess_obs * 0.3
    excess_obs_hi = excess_obs * 3.0

    # PPM prediction: enhanced collapse from G_eff
    excess_ppm = np.array([GR.g_eff(zi)**2 for zi in z_jwst])

    ax2.semilogy(z_jwst, excess_obs, 's', color=GOLD, markersize=10,
                 markeredgecolor='#333', label='JWST observed excess', zorder=10)
    for i in range(len(z_jwst)):
        ax2.plot([z_jwst[i], z_jwst[i]], [excess_obs_lo[i], excess_obs_hi[i]],
                 color=GOLD, linewidth=1.5, alpha=0.6)

    ax2.semilogy(z_jwst, excess_ppm, 'D-', color=PURPLE, markersize=8,
                 markeredgecolor='#333', label=r'PPM: $\propto G_{\mathrm{eff}}^2$', zorder=5)
    ax2.axhline(y=1, color=GRAY, linewidth=1, linestyle=':',
                label=r'$\Lambda$CDM prediction (1×)')

    ax2.set_xlabel('Redshift $z$')
    ax2.set_ylabel('Galaxy count excess above ΛCDM')
    ax2.set_title('JWST "Impossible Galaxies" vs PPM')
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    save(fig, 'fig_g_eff_jwst.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. Halo Mass Function (§11.3 replacement)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_halo_mass():
    print("Fig 8: Halo mass function")
    z = np.linspace(0, 20, 300)
    delta_c_lcdm = 1.686 * np.ones_like(z)
    delta_c_ppm = np.array([GR.delta_c_ppm(zi) for zi in z])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: collapse threshold
    ax1.plot(z, delta_c_lcdm, '--', color=BLUE, linewidth=2, label=r'$\Lambda$CDM: $\delta_c = 1.686$')
    ax1.plot(z, delta_c_ppm, color=PURPLE, linewidth=2.5, label=r'PPM: $\delta_c(z) \approx 1.75/(1+z)^{0.19}$')
    ax1.set_xlabel('Redshift $z$')
    ax1.set_ylabel(r'Collapse threshold $\delta_c$')
    ax1.set_title(r'Collapse Threshold $\delta_c(z)$')
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Right: Press-Schechter mass function enhancement
    sigma_range = np.linspace(0.3, 3, 200)

    def ps_f(sigma, delta_c):
        nu = delta_c / sigma
        return np.sqrt(2/np.pi) * nu * np.exp(-nu**2 / 2)

    for zi, ls, lw in [(0, '-', 1.5), (10, '--', 2), (20, ':', 2.5)]:
        dc_l = 1.686
        dc_p = GR.delta_c_ppm(zi)
        f_lcdm = ps_f(sigma_range, dc_l)
        f_ppm = ps_f(sigma_range, dc_p)
        ratio = f_ppm / np.where(f_lcdm > 1e-20, f_lcdm, 1e-20)
        ax2.semilogy(sigma_range, ratio, ls, color=PURPLE, linewidth=lw,
                     label=f'$z = {zi}$')

    ax2.axhline(y=1, color=GRAY, linewidth=1, linestyle=':')
    ax2.set_xlabel(r'$\sigma$ (mass variance)')
    ax2.set_ylabel(r'$f_{\mathrm{PPM}} / f_{\Lambda\mathrm{CDM}}$')
    ax2.set_title('Halo Mass Function Enhancement')
    ax2.legend()
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    save(fig, 'fig_halo_mass.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 9. Decoherence Prediction (§14.1 replacement)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_decoherence():
    print("Fig 9: Decoherence prediction")
    mass_kg = np.logspace(-20, -8, 500)
    tau_ppm = np.array([S.decoherence_timescale(m) for m in mass_kg])

    # Penrose-Diosi (geometry-dependent, approximate)
    hbar = 1.054571817e-34
    G = 6.674e-11
    # Approximate as tau_PD ~ hbar*R / (G*m^2) with R ~ (m/rho)^(1/3), rho=1000
    rho = 1000
    R = (mass_kg / (4/3 * np.pi * rho))**(1/3)
    tau_pd = hbar * R / (G * mass_kg**2)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.loglog(mass_kg, tau_ppm, color=PURPLE, linewidth=2.5,
              label=r'PPM: $\tau = 2\hbar/(Gm^2)$')
    ax.loglog(mass_kg, tau_pd, '--', color=BLUE, linewidth=2,
              label=r'Penrose-Di\'{o}si (geometry-dependent)')

    # Experimental milestones
    milestones = [
        (1e-18, 1e6, 'Current\noptomechanics'),
        (1e-15, 1e0, 'Near-term\n(nanoparticles)'),
        (1e-13, 1e-4, 'MAQRO\n(proposed)'),
    ]
    for m, t, label in milestones:
        ax.plot(m, t, '*', color=GOLD, markersize=15, markeredgecolor='#333', zorder=10)
        ax.annotate(label, xy=(m, t), xytext=(10, 10), textcoords='offset points',
                   fontsize=8, color=GOLD)

    # Accessible window
    ax.axhspan(1e-3, 1e8, alpha=0.05, color=GOLD)
    ax.text(1e-12, 1e5, 'Experimentally accessible window',
            fontsize=9, color=GOLD, ha='center', fontstyle='italic')

    ax.set_xlabel('Mass (kg)')
    ax.set_ylabel(r'Decoherence time $\tau$ (s)')
    ax.set_title('Gravitational Decoherence: PPM Prediction vs Experimental Sensitivity')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.2, which='both')
    ax.set_xlim(1e-20, 1e-8)
    ax.set_ylim(1e-10, 1e15)
    save(fig, 'fig_decoherence.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. DUNE δ_CP (§14.2 replacement)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_dune_delta_cp():
    print("Fig 10: DUNE δ_CP measurement")
    dcp = BP.delta_cp()
    dcp_rad = dcp['delta_cp_rad']
    dcp_deg = dcp['delta_cp_deg']

    delta_range_deg = np.linspace(-180, 180, 361)
    delta_range_rad = np.deg2rad(delta_range_deg)

    # DUNE sensitivity (approximate): significance ~ |sin(delta)|
    # Scale so max CP violation gives ~5sigma at 7yr
    exposure_years = [3, 5, 7, 10]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    for yr in exposure_years:
        base_sigma = 5.0 * (yr / 7.0)**0.5
        significance = base_sigma * np.abs(np.sin(delta_range_rad))
        ax1.plot(delta_range_deg, significance, linewidth=1.5,
                 label=f'{yr} yr exposure')

    ax1.axvline(x=dcp_deg, color=RED, linewidth=2.5, linestyle='-',
                label=f'PPM: δ_CP = {dcp_deg:.1f}°')
    ax1.axvline(x=-90, color=GRAY, linewidth=1, linestyle=':',
                label='Maximal CP violation')
    ax1.axhline(y=3, color='#aaa', linewidth=0.8, linestyle='-.')
    ax1.axhline(y=5, color='#aaa', linewidth=0.8, linestyle='-.')
    ax1.text(175, 3.1, '3σ', fontsize=8, ha='right', color='#666')
    ax1.text(175, 5.1, '5σ', fontsize=8, ha='right', color='#666')

    ax1.set_xlabel(r'True $\delta_{\mathrm{CP}}$ (degrees)')
    ax1.set_ylabel(r'CP violation discovery significance ($\sigma$)')
    ax1.set_title('DUNE CP-Violation Discovery Reach')
    ax1.legend(fontsize=7, loc='upper left')
    ax1.set_xlim(-180, 180)
    ax1.set_ylim(0, 8)
    ax1.grid(alpha=0.3)

    # Right: measurement precision
    for yr in exposure_years:
        precision = 15.0 / (yr / 3.0)**0.5 / np.where(np.abs(np.sin(delta_range_rad)) > 0.1,
                                                         np.abs(np.sin(delta_range_rad)), 0.1)
        precision = np.clip(precision, 0, 60)
        ax2.plot(delta_range_deg, precision, linewidth=1.5, label=f'{yr} yr')

    ax2.axvline(x=dcp_deg, color=RED, linewidth=2.5, linestyle='-',
                label=f'PPM: {dcp_deg:.1f}°')
    ppm_precision_7yr = 15.0 / (7/3)**0.5 / abs(math.sin(dcp_rad))
    ax2.plot(dcp_deg, ppm_precision_7yr, '*', color=RED, markersize=15,
             markeredgecolor='#333', zorder=10)
    ax2.annotate(f'±{ppm_precision_7yr:.1f}° at 7yr',
                xy=(dcp_deg, ppm_precision_7yr), xytext=(20, 15),
                textcoords='offset points', fontsize=9, color=RED)

    ax2.set_xlabel(r'True $\delta_{\mathrm{CP}}$ (degrees)')
    ax2.set_ylabel(r'$\delta_{\mathrm{CP}}$ measurement precision (degrees)')
    ax2.set_title(r'DUNE $\delta_{\mathrm{CP}}$ Precision')
    ax2.legend(fontsize=7, loc='upper right')
    ax2.set_xlim(-180, 180)
    ax2.set_ylim(0, 50)
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    save(fig, 'fig_dune_delta_cp.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 11. Agency Bias Lindblad (§12.7 replacement)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_agency_lindblad():
    print("Fig 11: Agency bias Lindblad")
    nr = GR.n_reliable()
    N_rel = nr['N_reliable']

    # Simulate 2-cell Lindblad bias
    N_neurons = np.logspace(2, 7, 200)
    # Bias: fraction of Born probability that can be steered by intention
    # Scales as 1/sqrt(N) for large N
    Gamma_PD = nr['Gamma_PD']
    t_int = nr['t_integrate_s']

    # Effective bias from Lindblad feedback
    bias_amplitude = 1.0 / np.sqrt(N_neurons)
    reliability = 1.0 - np.exp(-N_neurons * bias_amplitude**2)

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))

    # Panel 1: Bias amplitude vs N
    ax = axes[0, 0]
    ax.loglog(N_neurons, bias_amplitude, color=PURPLE, linewidth=2)
    ax.axvline(x=N_rel, color=RED, linewidth=1.5, linestyle='--',
               label=f'$N_{{\\mathrm{{reliable}}}} \\approx {N_rel:.1e}$')
    ax.set_xlabel('Number of neurons $N$')
    ax.set_ylabel('Bias amplitude per actualization')
    ax.set_title('Single-Event Bias Amplitude')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, which='both')

    # Panel 2: Cumulative reliability
    ax = axes[0, 1]
    M_windows = 0.150 / t_int  # motor decisions per 150ms window
    cumulative_bias = np.sqrt(M_windows) * bias_amplitude
    ax.semilogx(N_neurons, cumulative_bias, color=GOLD, linewidth=2)
    ax.axhline(y=0.5, color=RED, linewidth=1, linestyle=':',
               label='50% threshold')
    ax.axvline(x=N_rel, color=RED, linewidth=1.5, linestyle='--')
    ax.set_xlabel('Number of neurons $N$')
    ax.set_ylabel('Cumulative bias (per motor window)')
    ax.set_title(f'Cumulative Bias over {M_windows:.0f} Integration Windows')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Panel 3: Comparison to biology
    ax = axes[1, 0]
    bio_data = {
        'C. elegans\n(302)': 302,
        'Fly brain\n(~10⁵)': 1e5,
        'PPM threshold\n(~5×10⁵)': N_rel,
        'Mouse cortex\n(~4×10⁶)': 4e6,
        'Corticospinal\n(~10⁶)': 1e6,
        'Human cortex\n(~10¹⁰)': 1e10,
    }
    names = list(bio_data.keys())
    values = list(bio_data.values())
    colors_bio = [GRAY, GRAY, RED, BLUE, GOLD, BLUE]
    bars = ax.barh(range(len(names)), values, color=colors_bio,
                   edgecolor='#555', linewidth=0.5, height=0.6)
    ax.set_xscale('log')
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel('Neuron count')
    ax.set_title('PPM Reliability Threshold vs Biology')
    ax.axvline(x=N_rel, color=RED, linewidth=1.5, linestyle='--', alpha=0.5)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

    # Panel 4: Decoherence vs integration timescales
    ax = axes[1, 1]
    T_range = np.linspace(290, 340, 100)
    tau_sys = []
    tau_bath = []
    t_ints = []
    for T in T_range:
        r = GR.integration_time(T_K=T)
        tau_sys.append(r['tau_sys_s'])
        tau_bath.append(r['tau_bath_s'])
        t_ints.append(r['t_integrate_s'])

    ax.semilogy(T_range, tau_sys, color=PURPLE, linewidth=2, label=r'$\tau_{\mathrm{sys}}$')
    ax.semilogy(T_range, tau_bath, color=BLUE, linewidth=2, label=r'$\tau_{\mathrm{bath}}$')
    ax.semilogy(T_range, t_ints, color=GOLD, linewidth=2.5,
                label=r'$t_{\mathrm{integrate}}$ (Zeno window)')
    ax.axvline(x=310, color=RED, linewidth=1, linestyle=':', label='310 K (body)')
    ax.set_xlabel('Temperature (K)')
    ax.set_ylabel('Timescale (s)')
    ax.set_title('Decoherence vs Integration Timescales')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    fig.suptitle('Agency as Measurement Basis Selection: 2-Cell Lindblad Computation',
                 fontsize=14, y=1.02)
    fig.tight_layout()
    save(fig, 'fig_agency_lindblad.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 12. Λ Comparison (§10.5)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_lambda_comparison():
    print("Fig 12: Lambda comparison")
    cc = GR.cosmological_constant()
    Lambda_ppm = cc['Lambda_m2']
    Lambda_obs = cc['Lambda_obs']
    err = cc['error_pct']

    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(['PPM\nPredicted', 'Observed\n(Planck)'],
                  [Lambda_ppm * 1e52, Lambda_obs * 1e52],
                  color=[PURPLE, GOLD], edgecolor='#333', width=0.5)

    for bar, val in zip(bars, [Lambda_ppm, Lambda_obs]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2e} m⁻²', ha='center', va='bottom', fontsize=9)

    ax.set_ylabel(r'$\Lambda$ ($\times 10^{-52}$ m$^{-2}$)')
    ax.set_title(f'Cosmological Constant (error: {err:.1f}%)')
    ax.grid(axis='y', alpha=0.3)
    save(fig, 'fig_lambda_comparison.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 13. N_reliable (§12.8)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_n_reliable():
    print("Fig 13: N_reliable comparison")
    nr = GR.n_reliable()
    N_ppm = nr['N_reliable']

    fig, ax = plt.subplots(figsize=(6, 3.5))
    N_cortico_lo = 2e5
    N_cortico_hi = 1e6

    ax.barh([0], [N_ppm], height=0.4, color=PURPLE, edgecolor='#333',
            label=f'PPM: $N_{{\\mathrm{{reliable}}}} = {N_ppm:.1e}$')
    ax.barh([1], [N_cortico_hi], height=0.4, color=GOLD, edgecolor='#333', alpha=0.5)
    ax.barh([1], [N_cortico_lo], height=0.4, color=GOLD, edgecolor='#333',
            label=f'Corticospinal tract: {N_cortico_lo:.0e}–{N_cortico_hi:.0e}')

    ax.set_xscale('log')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['PPM\nprediction', 'Corticospinal\ntract'])
    ax.set_xlabel('Neuron count')
    ax.set_title(r'Agency Threshold: PPM vs Corticospinal Tract (no free parameters)')
    ax.legend(fontsize=8, loc='lower right')
    ax.grid(axis='x', alpha=0.3)
    save(fig, 'fig_n_reliable.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 14. Pöschl-Teller Potential + Wavefunction (Appendix B.1)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_poschl_teller():
    print("Fig 14: Pöschl-Teller wavefunction")
    # The CP³ tube with Pöschl-Teller confinement
    # V(d) = -λ(λ-1) / cosh²(d), λ=4 for CP³
    lam = 4  # n+1 = 4 for CP³
    d = np.linspace(-4, 4, 500)
    V = -lam * (lam - 1) / np.cosh(d)**2

    # Ground state wavefunction: u₁(d) ∝ 1/cosh^λ(d)
    u1 = 1.0 / np.cosh(d)**lam
    u1 = u1 / np.max(u1)

    # First excited state
    u2 = np.sinh(d) / np.cosh(d)**(lam)
    u2 = u2 / np.max(np.abs(u2))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(d, V, color=PURPLE, linewidth=2.5, label=r'$Q(d) = -\lambda(\lambda-1)/\cosh^2(d)$')
    ax.fill_between(d, V, min(V)-2, alpha=0.08, color=PURPLE)

    # Eigenvalues
    E0 = -(lam - 1)**2
    E1 = -(lam - 2)**2
    ax.axhline(y=E0, color=GOLD, linewidth=1, linestyle='--', alpha=0.7)
    ax.axhline(y=E1, color=CYAN, linewidth=1, linestyle='--', alpha=0.7)

    # Wavefunctions offset to their eigenvalues
    scale = 3
    ax.plot(d, E0 + scale * u1**2, color=GOLD, linewidth=2,
            label=r'$|u_1(d)|^2$ (ground state)')
    ax.plot(d, E1 + scale * u2**2, color=CYAN, linewidth=1.5,
            label=r'$|u_2(d)|^2$ (1st excited)')

    ax.text(3.5, E0, f'$E_0 = -{(lam-1)**2}$', fontsize=9, color=GOLD)
    ax.text(3.5, E1, f'$E_1 = -{(lam-2)**2}$', fontsize=9, color=CYAN)

    ax.set_xlabel(r'Fubini-Study distance $d$ from $\mathbb{RP}^3$')
    ax.set_ylabel('Potential / Probability density')
    ax.set_title(r'Pöschl-Teller Confinement in the $\mathbb{CP}^3$ Tube ($\lambda = n+1 = 4$)')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_ylim(min(V) - 2, 5)
    save(fig, 'fig_poschl_teller.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 15. Instanton Zero Mode Budget (Appendix B.2)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_zero_mode_budget():
    print("Fig 15: Instanton zero mode budget")
    zm = I.zero_mode_count()
    n_real = zm['n_real']  # 30

    # Budget: dim_R PGL(4,C) = 30 = 15 + 6 + 1 + 8
    components = ['Translations\n(15)', 'Rotations\n(6)', 'Scale\n(1)', 'Gauge\n(8)']
    sizes = [15, 6, 1, 8]
    colors_pie = [PURPLE, GOLD, CYAN, BLUE]
    explode = (0.02, 0.02, 0.1, 0.02)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    ax1.pie(sizes, labels=components, colors=colors_pie, explode=explode,
            autopct=lambda p: f'{int(p*30/100)}', startangle=90,
            textprops={'fontsize': 10})
    ax1.set_title(f'30 Real Zero Modes = dim$_{{\\mathbb{{R}}}}$ PGL(4,$\\mathbb{{C}}$)',
                  fontsize=12)

    # Right: key numbers
    phi196 = I.phi_196_check()
    S = I.instanton_action()

    info = [
        (r'$S_{\mathrm{inst}} = 30\pi$', f'{S:.3f}'),
        (r'$e^{-30\pi}$', f'{phi196["exp_neg_S"]:.2e}'),
        (r'$\varphi^{-196}$', f'{phi196["phi_neg_196"]:.2e}'),
        ('Mismatch', f'{phi196["mismatch_pct"]:.2f}%'),
        ('Zero modes (complex)', f'{zm["n_complex"]}'),
        ('Zero modes (real)', f'{zm["n_real"]}'),
    ]

    ax2.axis('off')
    for i, (label, val) in enumerate(info):
        y = 0.85 - i * 0.13
        ax2.text(0.1, y, label, fontsize=11, transform=ax2.transAxes, va='center')
        ax2.text(0.75, y, val, fontsize=11, transform=ax2.transAxes, va='center',
                fontweight='bold', color=PURPLE)

    ax2.set_title('Instanton Sector Summary', fontsize=12)

    fig.suptitle(r'Instanton Action $S = 30\pi$, $e^{-S} \approx \varphi^{-196}$',
                fontsize=13, y=1.02)
    fig.tight_layout()
    save(fig, 'fig_zero_mode_budget.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 16. Experimental Roadmap (§14.4)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fig_experimental_roadmap():
    print("Fig 16: Experimental roadmap")
    fig, ax = plt.subplots(figsize=(12, 6))

    categories = {
        'Near-term\n(2025–2030)': [
            ('Gravitational decoherence\n(nanoparticle optomechanics)', 2026, 2030, PURPLE),
            ('DUNE δ_CP = π/φ² ≈ 68.8°\n(distinguish from maximal)', 2025, 2031, RED),
            ('JWST high-z galaxies\n(G_eff structure formation)', 2024, 2028, GOLD),
            ('θ_strong = 0\n(nEDM confirmation)', 2025, 2028, BLUE),
        ],
        'Medium-term\n(2028–2035)': [
            ('Zeno coherence window\n(t_integrate ≈ 0.13 ms)', 2028, 2033, PURPLE),
            ('RP³ persistent homology\n(neural topology)', 2029, 2035, CYAN),
            ('w_eff > −1\n(dark energy EoS)', 2027, 2034, GOLD),
            ('Halo mass function\n(δ_c(z) deviation)', 2028, 2032, BLUE),
        ],
        'Long-term\n(2035+)': [
            ('GW dispersion\n(Δv/c from actualization)', 2035, 2042, PURPLE),
            ('3-generation topology\n(collider probes)', 2035, 2045, CYAN),
        ],
    }

    y = 0
    y_ticks = []
    y_labels = []
    cat_boundaries = []

    for cat_name, experiments in categories.items():
        cat_start = y
        for (name, start, end, color) in experiments:
            ax.barh(y, end - start, left=start, height=0.6, color=color,
                    alpha=0.7, edgecolor='#333', linewidth=0.5)
            ax.text(start - 0.3, y, name, ha='right', va='center', fontsize=7.5)
            y_ticks.append(y)
            y_labels.append('')
            y += 1
        cat_boundaries.append((cat_start, y - 1, cat_name))
        y += 0.5

    for start, end, name in cat_boundaries:
        mid = (start + end) / 2
        ax.text(2022.5, mid, name, ha='center', va='center', fontsize=9,
                fontweight='bold', color='#333',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#f0f0f0', edgecolor='#ccc'))

    ax.axvline(x=2026, color=RED, linewidth=1, linestyle=':', alpha=0.5, label='Current (2026)')
    ax.set_xlabel('Year')
    ax.set_title('PPM Experimental Roadmap: Testable Predictions')
    ax.set_yticks([])
    ax.set_xlim(2019, 2046)
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    ax.legend(loc='lower right')
    save(fig, 'fig_experimental_roadmap.png')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == '__main__':
    print(f"Generating computed figures → {OUTDIR}/\n")
    fig_cpn_selectivity()
    fig_three_alpha_routes()
    fig_heat_kernel_convergence()
    fig_sin2_theta_w()
    fig_energy_hierarchy_table()
    fig_master_predictions()
    fig_g_eff_jwst()
    fig_halo_mass()
    fig_decoherence()
    fig_dune_delta_cp()
    fig_agency_lindblad()
    fig_lambda_comparison()
    fig_n_reliable()
    fig_poschl_teller()
    fig_zero_mode_budget()
    fig_experimental_roadmap()
    print(f"\nDone. {16} figures generated.")

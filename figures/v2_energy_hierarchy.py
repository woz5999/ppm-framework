"""
v2_energy_hierarchy.py — PPM energy hierarchy with prediction-tier markers and full-range inset.

Three-tier visualization distinguishes what the cascade position represents:

  T1  filled, white edge:   E(k) alone gives the mass — Planck, tau, pion,
                             muon, electron. The cleanest first-principles
                             predictions, spanning 23 orders of magnitude.

  T2  filled, gold edge:    cascade rung k is framework-predicted, but the
                             full mass requires additional framework structure
                             — EWSB relations for the EW sector (top, Higgs,
                             Z, W all at k=44.5 anchor) or Kähler-radial |z|
                             corrections for the heavy quarks (bottom, charm).

  T3  hollow, color edge:   k displayed is inverse-derived from the observed
                             mass; first-principles |z| derivation is on the
                             framework's research agenda. Light quarks
                             (strange, down, up) sit on the curve by
                             construction.

Marker shape encodes physics class (square=quark, circle=lepton,
diamond=boson, triangle=meson, downtriangle=scale).

Layout: main panel zoomed to k=43-58 (particle physics range) with full
labels; inset top-left shows full k=1-58 span (Planck → electron) so the
23-orders-of-magnitude structural claim is visible.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from _style import apply_style, new_figure, save, CAT_COLORS, BG, WHITE, GRAY, GOLD
from ppm import hierarchy

apply_style()


# ── Particle data with explicit prediction tier ────────────────────────────
# The framework's predicted cascade positions are stated here directly rather
# than read from hierarchy.k_level_table(), because the table includes
# inverse-derived k for some particles (light quarks; W and Z slightly off
# their EWSB anchor) which conflate first-principles predictions with
# back-fits. Tier classification makes the distinction visible.
#
# (name, k, observed_GeV, category, tier)
PARTICLES = [
    # Tier 1 — E(k) alone gives the mass
    ('Planck',    1.00,  1.22e19,    'scale',  1),
    ('tau',      48.00,  1.777,      'lepton', 1),
    ('pion',     51.00,  0.140,      'meson',  1),
    ('muon',     51.50,  0.1057,     'lepton', 1),
    ('electron', 57.00,  0.000511,   'lepton', 1),
    # Tier 2 — cascade rung framework-predicted; mass via additional structure
    # EW sector: all four anchored at k=44.5; masses through electroweak relations.
    ('top',      44.50,  172.7,      'quark',  2),
    ('Higgs',    44.50,  125.25,     'boson',  2),
    ('Z',        44.50,   91.19,     'boson',  2),
    ('W',        44.50,   80.38,     'boson',  2),
    # Heavy quarks: integer/half-integer cascade rungs; full mass needs |z|.
    ('bottom',   46.00,   4.18,      'quark',  2),
    ('charm',    47.50,   1.27,      'quark',  2),
    # Tier 3 — k inverse-derived from observed mass; first-principles open
    ('strange',  51.44,   0.0934,    'quark',  3),
    ('down',     54.70,   0.00467,   'quark',  3),
    ('up',       55.54,   0.00216,   'quark',  3),
]

MARKERS = {'quark': 's', 'boson': 'D', 'lepton': 'o', 'meson': '^', 'scale': 'v'}


def tier_kwargs(category, tier, size=12, edge_scale=1.0):
    """Plot kwargs encoding both physics class (marker shape, color) and
    prediction tier (fill style and edge color)."""
    color = CAT_COLORS.get(category, GRAY)
    marker = MARKERS.get(category, 'o')
    base = dict(marker=marker, markersize=size, linestyle='', zorder=5)
    if tier == 1:
        # Filled, white edge — clean prediction
        base.update(markerfacecolor=color,
                    markeredgecolor=WHITE,
                    markeredgewidth=1.5 * edge_scale)
    elif tier == 2:
        # Filled with gold edge — framework-anchored, additional structure
        base.update(markerfacecolor=color,
                    markeredgecolor=GOLD,
                    markeredgewidth=2.0 * edge_scale)
    else:  # tier 3
        # Hollow with category-color edge — k inverse-derived
        base.update(markerfacecolor='none',
                    markeredgecolor=color,
                    markeredgewidth=1.6 * edge_scale)
    return base


def plot_curve(ax, k_min, k_max, n=300, lw=2, alpha=0.7, label=None):
    k_cont = np.linspace(k_min, k_max, n)
    E_cont = np.array([hierarchy.energy_gev(k) for k in k_cont])
    ax.semilogy(k_cont, E_cont, color=GRAY, linewidth=lw, alpha=alpha, label=label)


# ── Main figure ────────────────────────────────────────────────────────────
fig, ax = new_figure(width=11, height=7.5)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

plot_curve(ax, 43, 59, lw=2,
           label=r'$E(k) = 140\;\mathrm{MeV}\times(2\pi)^{(51-k)/2}$')

# Plot particles in the main range
for name, k, m, cat, tier in PARTICLES:
    if not (43 <= k <= 58):
        continue
    ax.plot(k, m, **tier_kwargs(cat, tier, size=12))
    # Label offset
    offset_x, offset_y, ha = 0.3, 1.15, 'left'
    if name in ('top', 'Higgs'):
        offset_x, ha = -0.3, 'right'
    elif name == 'Z':
        offset_x, offset_y = 0.3, 1.30
    elif name == 'W':
        offset_x, offset_y = 0.3, 0.78
    ax.text(k + offset_x, m * offset_y, name,
            fontsize=9, color=WHITE, ha=ha, va='bottom')

# ── Legend (tier + curve) ──────────────────────────────────────────────────
proxy = lambda mfc, mec, mew: dict(marker='o', color='w', markerfacecolor=mfc,
                                    markeredgecolor=mec, markeredgewidth=mew,
                                    markersize=11, linestyle='')

tier_proxies = [
    Line2D([0], [0], label='T1: predicted via $E(k)$',
           **proxy(GRAY, WHITE, 1.5)),
    Line2D([0], [0], label='T2: cascade $k$ predicted; mass via additional structure',
           **proxy(GRAY, GOLD, 2.0)),
    Line2D([0], [0], label='T3: $k$ inverse-derived (open)',
           **proxy('none', GRAY, 1.6)),
    Line2D([0], [0], color=GRAY, linewidth=2, label=r'$E(k)$ formula'),
]
ax.legend(handles=tier_proxies, fontsize=9, loc='lower left',
          framealpha=0.85, edgecolor=GRAY)

ax.set_xlabel('k-level', fontsize=13)
ax.set_ylabel('Mass / Energy (GeV)', fontsize=13)
ax.set_title('PPM Energy Hierarchy — observed masses vs. $E(k)$',
             fontsize=14, pad=15)
ax.set_xlim(43, 59)
ax.set_ylim(1e-4, 1e3)
ax.grid(True, alpha=0.2, which='both', linestyle='-')


# ── Inset: full k=1-58 span (Planck → electron, 23 orders of magnitude) ────
inset = ax.inset_axes([0.66, 0.62, 0.32, 0.34])
inset.set_facecolor(BG)
plot_curve(inset, 0.5, 58, n=400, lw=1.3)

for name, k, m, cat, tier in PARTICLES:
    inset.plot(k, m, **tier_kwargs(cat, tier, size=6, edge_scale=0.65))

# Label only the endpoints in the inset, to keep it readable
for name, k, m, cat, tier in PARTICLES:
    if name in ('Planck', 'electron'):
        offset = (1.8, 1.6) if name == 'Planck' else (1.8, 0.7)
        inset.text(k + offset[0], m * offset[1], name,
                   fontsize=7, color=WHITE, va='center', ha='left')

inset.set_xlim(0, 60)
inset.set_ylim(1e-4, 1e21)
inset.set_xlabel('k', fontsize=8, labelpad=2)
inset.set_ylabel('GeV', fontsize=8, labelpad=2)
inset.tick_params(labelsize=7, pad=2)
inset.set_title('Full range — 23 orders of magnitude',
                fontsize=8, pad=4, color=WHITE)
inset.grid(True, alpha=0.18, which='major', linestyle='-')

# Subtle frame around the inset
for spine in inset.spines.values():
    spine.set_edgecolor(GRAY)
    spine.set_linewidth(0.6)

plt.tight_layout()
save(fig, 'v2_energy_hierarchy.png')

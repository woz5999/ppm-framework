"""
v2_g_eff_jwst.py — Single-panel "anomaly factor vs ΛCDM" diagnostic.

Story line:
  - PPM predicts a closed-form gravitational enhancement
    G_eff(z)/G_0 = (1+z)^{3/2} from holographic mass screening.
  - JWST observations (Labbé+ 2023) show stellar-mass-density excess
    of factor ~20× at z≈8 and ~10³× at z≈9 above ΛCDM expectations.
  - Boylan-Kolchin 2023 reports z~10 candidates at the absolute upper
    limit of the ΛCDM halo mass function.
  - All three rise by orders of magnitude across the same redshift
    band.  The figure displays both diagnostics on a shared
    "anomaly factor vs ΛCDM" log axis.

Honesty:
  ρ_* excess and G_eff/G_0 are different physical quantities.  The
  link between them runs through SFR(G), which is not derived in PPM.
  An on-figure caveat states this explicitly so the visual rhyme
  (orders-of-magnitude tracking) is supported by structure, not
  asserted as identity.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from _style import apply_style, save, GOLD, GRAY, WHITE, CYAN, RED, BG, VIOLET
from ppm.cosmology import g_eff

apply_style()

plt.rcParams.update({
    'font.size': 15,
    'axes.titlesize': 19,
    'axes.labelsize': 17,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 13,
})

# ── Figure ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 9))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# ── PPM prediction curves ──────────────────────────────────────────────────
# Solid: closed-form geometric prediction G_eff(z)/G_0 = (1+z)^{3/2}.
# Dashed: SFR(G)-amplified expectation for the observable ρ_* excess,
#   using the standard scaling SFR ∝ G^{3/2} (faster collapse and
#   fragmentation under enhanced gravity → cumulative stellar-mass
#   excess scales as (G_eff/G_0)^{3/2} = (1+z)^{9/4}).  This is the
#   bridge from the PPM geometric prediction to the JWST observable.
z_vals = np.linspace(0, 15, 400)
g_eff_vals = np.array([g_eff(z) for z in z_vals])
sfr_amp_vals = g_eff_vals ** 1.5  # = (1+z)^{9/4}

ax.plot(z_vals, g_eff_vals, color=GOLD, linewidth=4.0,
        label=r'PPM geometric: $G_{\rm eff}(z)/G_0 = (1+z)^{3/2}$',
        zorder=4)
ax.plot(z_vals, sfr_amp_vals, color=GOLD, linewidth=3.0, linestyle='--',
        alpha=0.85,
        label=r'PPM $\to \rho_\star$ via SFR $\propto G^{3/2}$: $(1+z)^{9/4}$',
        zorder=4)
ax.fill_between(z_vals, g_eff_vals, sfr_amp_vals, alpha=0.13, color=GOLD,
                zorder=2)

# ── ΛCDM / GR baseline ─────────────────────────────────────────────────────
ax.axhline(1.0, color=GRAY, linewidth=2.2, linestyle='--', alpha=0.75,
           label=r'$\Lambda$CDM / GR baseline', zorder=3)

# ── JWST observational data (Labbé+ 2023) ──────────────────────────────────
# Cumulative stellar-mass-density excess above 10^10 M_⊙ vs ΛCDM:
#   z ≈ 8 :  factor ~20×
#   z ≈ 9 :  factor ~10^3 ×
# Asymmetric uncertainty bars approximate factor-of-3 IMF systematics.
z_lit      = np.array([8.0, 9.0])
excess_lit = np.array([20.0, 1000.0])
excess_lo  = np.array([6.0, 100.0])
excess_hi  = np.array([60.0, 3000.0])
yerr_lit   = np.array([excess_lit - excess_lo, excess_hi - excess_lit])

ax.errorbar(z_lit, excess_lit, yerr=yerr_lit,
            fmt='s', color=CYAN, markersize=15,
            markeredgecolor=WHITE, markeredgewidth=2,
            capsize=7, capthick=2.5, elinewidth=2.5,
            label='Labb\u00e9+ 2023: ' + r'$\rho_\star(>\!10^{10}\,M_\odot)$ excess vs $\Lambda$CDM',
            zorder=5)

# ── Boylan-Kolchin 2023 ΛCDM ceiling at z~10 ──────────────────────────────
# This is NOT a measured data point — it is a theoretical ceiling.  BK 2023
# argue that f_b × M_halo,max(z) (cosmic baryon fraction × the maximum halo
# mass allowed by the ΛCDM halo mass function at that redshift) bounds the
# stellar mass any galaxy could possess; the most massive JWST candidates
# at z~10 sit right at this bound.  Visualised as a thick red horizontal
# segment at z ∈ [9.4, 10.6] with hatched "no-go" region above.
z_bk_lo, z_bk_hi = 9.4, 10.6
y_bk_ceiling = 1500.0
# Hatched forbidden region above the ceiling (out to top of plot).
ax.fill_between([z_bk_lo, z_bk_hi], y_bk_ceiling, 5e3,
                color=RED, alpha=0.10, hatch='///', edgecolor=RED,
                linewidth=0, zorder=3)
# Solid red ceiling segment.
ax.plot([z_bk_lo, z_bk_hi], [y_bk_ceiling, y_bk_ceiling],
        color=RED, linewidth=4.5, solid_capstyle='butt',
        label=r'$\Lambda$CDM ceiling at $z\!\sim\!10$ (Boylan-Kolchin 2023)',
        zorder=5)
# (No inline label inside the hatched zone — the hatching + ceiling
# segment + legend entry already communicate forbidden region.)

# (Dropped the per-z ×N callouts — they read as visual noise next to a
# log-scale curve that already conveys the value clearly.)

# ── Axes ───────────────────────────────────────────────────────────────────
ax.set_xlabel('Redshift $z$', color=WHITE)
ax.set_ylabel(r'Anomaly factor vs $\Lambda$CDM (log scale)', color=WHITE)
ax.set_title(r'$G_{\rm eff}(z) = G_0(1+z)^{3/2}$ vs JWST early-galaxy excess',
             color=WHITE, pad=14)
ax.set_xlim(0, 15)
ax.set_ylim(0.5, 5e3)
ax.set_yscale('log')
ax.grid(True, alpha=0.3, linestyle=':', which='both')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(1.5)
ax.spines['left'].set_linewidth(1.5)

# ── Legend — placed lower-left so it does not occlude the data column ──────
# (which sits at z=8-10, y=20-3000, i.e. center-to-upper-right of the panel).
ax.legend(loc='lower right', framealpha=0.92, handlelength=2.5,
          bbox_to_anchor=(0.99, 0.02))

# ── Caveat textbox — small, top-left, well clear of all data ───────────────
# Says exactly what the dashed curve does: PPM gives the geometric
# G enhancement (solid); standard SFR(G) astrophysics (chapter §12.8)
# turns that into the ρ_* excess (dashed).  The data should sit near
# or above the dashed curve.  PPM does not derive the SFR(G) bridge.
ax.text(0.02, 0.97,
        ('Solid: PPM closed-form geometric prediction.\n'
         'Dashed: same prediction routed through SFR $\\propto G^{3/2}$\n'
         'to give the observable $\\rho_\\star$ excess.  PPM supplies\n'
         'the geometry; the SFR$(G)$ bridge is standard astrophysics\n'
         '(§12.8), not derived in this framework.'),
        transform=ax.transAxes, fontsize=11, color=WHITE, alpha=0.92,
        ha='left', va='top',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=BG,
                  edgecolor=GRAY, alpha=0.88))

plt.tight_layout()
save(fig, 'v2_g_eff_jwst.png')

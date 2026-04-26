"""
v2_alpha_survival_ratio.py — α as the τ-fixed FRACTION of CP³

Continuous stacked-fraction plot. Total height of every column = 1 across
the full t-axis: every column is the spectral content of CP³ partitioned
into two pieces.

  gold  band (bottom): Θ^τ(t) / Θ_{CP³}(t)        — τ-fixed fraction (RP³)
  violet band (top):   1 − Θ^τ(t) / Θ_{CP³}(t)    — projected-away fraction

At small t (UV) high-k modes dominate; the τ-fixed fraction is tiny — most
of the spectral content is asymmetric and gets stripped by the projection.
At large t (IR) only the k=0 mode survives; the τ-fixed fraction → 1.

The crossing point at t* = 1/(2(n+1)²) = 1/32 reads off directly as α:
  RP³ fraction at t* = Θ^τ(t*)/Θ_{CP³}(t*) = α ≈ 1/137.

Replaces the older Pöschl-Teller composite (alpha-geometric-origin-short-2.png)
with a parameter-free computed plot whose visual content IS the derivation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from _style import apply_style, new_figure, save, WHITE, GOLD, VIOLET, GRAY, CYAN, BG
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
from matplotlib.ticker import FixedLocator, NullLocator, FixedFormatter
from ppm import alpha as alpha_module

apply_style()

# ─── Compute fractions over t ────────────────────────────────────────────────
# Sample densely on log-t so the stacked region is smooth across many decades.
t_values = np.logspace(-3.0, 0.3, 400)   # t from 0.001 to ~2
t_star = alpha_module.t_star(n=3)        # 1/32 ≈ 0.03125

rp3_frac = []  # τ-fixed fraction = Θ^τ / Θ_CP³
for t in t_values:
    th_tau, th_cp = alpha_module._twisted_heat_traces(t, nmax=400)
    rp3_frac.append(th_tau / th_cp if th_cp > 0 else np.nan)
rp3_frac = np.array(rp3_frac)
cp3_only_frac = 1.0 - rp3_frac

# Value at t*
th_tau_star, th_cp_star = alpha_module._twisted_heat_traces(t_star, nmax=400)
alpha_at_tstar = th_tau_star / th_cp_star
alpha_inv_at_tstar = 1.0 / alpha_at_tstar
alpha_inv_obs = 137.036

# ─── Figure ──────────────────────────────────────────────────────────────────
fig, ax = new_figure(width=11, height=6.8)

# Stacked fill: gold (RP³, τ-fixed) on bottom, violet (projected-away) on top.
# Total height = 1 at every t.
ax.fill_between(t_values, 0, rp3_frac,
                color=GOLD, alpha=0.92, linewidth=0,
                label=r'$\Theta^{\tau}/\Theta_{\mathbb{CP}^{3}}$ — $\tau$-fixed fraction ($\mathbb{RP}^{3}$)')
ax.fill_between(t_values, rp3_frac, 1.0,
                color=VIOLET, alpha=0.78, linewidth=0,
                label=r'$1 - \Theta^{\tau}/\Theta_{\mathbb{CP}^{3}}$ — projected-away fraction')

# Boundary line between the bands, drawn on top for crispness
ax.plot(t_values, rp3_frac, color=WHITE, linewidth=1.4, alpha=0.55)

# Vertical line at t* and horizontal line at y = α
ax.axvline(t_star, color=WHITE, linestyle='--', linewidth=1.6, alpha=0.85)
ax.plot([t_values[0], t_star], [alpha_at_tstar, alpha_at_tstar],
        color=WHITE, linestyle='--', linewidth=1.6, alpha=0.85)

# Marker at the t* crossing
ax.scatter([t_star], [alpha_at_tstar], s=180, color=GOLD, edgecolor=WHITE,
           linewidth=2.2, zorder=8, marker='o')

# ─── Annotation: the value at t* IS α ───────────────────────────────────────
label_x = t_star * 4.2
label_y = 0.5
ax.annotate(
    '', xy=(t_star * 1.05, alpha_at_tstar + 0.015),
    xytext=(label_x * 0.96, label_y - 0.08),
    arrowprops=dict(arrowstyle='-', color=WHITE, lw=1.2, alpha=0.65),
    zorder=7,
)
ax.text(label_x, label_y,
        r'at $t^{*} = \dfrac{1}{32}$:' + '\n' +
        r'$\dfrac{\Theta^{\tau}(t^{*})}{\Theta_{\mathbb{CP}^{3}}(t^{*})} = \alpha$' +
        f'\n$= {alpha_at_tstar:.5f}$' + '\n' +
        f'$\\;\\;\\,(1/\\alpha = {alpha_inv_at_tstar:.3f})$',
        fontsize=13, color=WHITE, va='center', ha='left',
        bbox=dict(boxstyle='round,pad=0.55', facecolor='#0a0a1a',
                  edgecolor=GRAY, linewidth=1.0, alpha=0.95),
        zorder=9)

# In-band labels for the two fractions
# Move CP³ label below the inset's footprint
ax.text(0.0015, 0.32, r'$\mathbb{CP}^{3}$  (projected away)',
        color=WHITE, fontsize=12, fontweight='bold',
        ha='left', va='center', alpha=0.95)
ax.text(1.4, 0.7, r'$\mathbb{RP}^{3}$',
        color='#1a1408', fontsize=14, fontweight='bold',
        ha='right', va='center')

# ─── Axes ────────────────────────────────────────────────────────────────────
ax.set_xscale('log')
ax.set_xlabel(r'diffusion parameter $t$  (heat-kernel time on $\mathbb{CP}^{3}$)',
              fontsize=12)
ax.set_ylabel(r'fraction of spectral content',
              fontsize=12)
ax.set_title(r'$\alpha$ as the $\tau$-fixed fraction of $\mathbb{CP}^{3}$',
             fontsize=14, pad=12)
ax.set_xlim(t_values[0], t_values[-1])
ax.set_ylim(0, 1)

# Add t* to the x-axis as a labeled tick
xticks = list(ax.get_xticks())
xticks.append(t_star)
xtick_labels = [r'$10^{-3}$', r'$10^{-2}$', r'$10^{-1}$', r'$10^{0}$',
                r'$\mathbf{t^{*}{=}1/32}$']
# Filter to keep only ticks in range
filtered_ticks = [(0.001, r'$10^{-3}$'), (0.01, r'$10^{-2}$'),
                  (t_star, r'$\mathbf{t^{*}}$'),
                  (0.1, r'$10^{-1}$'), (1.0, r'$10^{0}$')]
ax.set_xticks([t for t, _ in filtered_ticks])
ax.set_xticklabels([lab for _, lab in filtered_ticks])

# Add α to the y-axis as a labeled tick
ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0, alpha_at_tstar])
ax.set_yticklabels(['0', '0.2', '0.4', '0.6', '0.8', '1', r'$\mathbf{\alpha}$'])

# Light grid only on x to keep the bands clean
ax.grid(True, which='major', axis='x', alpha=0.18, linestyle=':')
ax.grid(True, which='major', axis='y', alpha=0.10, linestyle=':')

# ─── Inset: zoom on the t* crossing at expanded y-scale ─────────────────────
# Linear axes here so the value α reads directly as a strip height.
axins = inset_axes(ax, width='32%', height='32%',
                   loc='upper left',
                   bbox_to_anchor=(0.07, -0.02, 1, 1),
                   bbox_transform=ax.transAxes,
                   borderpad=0)

# Zoom window
t_lo, t_hi = t_star * 0.4, t_star * 2.6
y_lo, y_hi = 0, 0.022

mask = (t_values >= t_lo) & (t_values <= t_hi)
t_in = t_values[mask]
rp3_in = rp3_frac[mask]

axins.fill_between(t_in, 0, rp3_in, color=GOLD, alpha=0.92, linewidth=0)
axins.fill_between(t_in, rp3_in, y_hi, color=VIOLET, alpha=0.78, linewidth=0)
axins.plot(t_in, rp3_in, color=WHITE, linewidth=1.2, alpha=0.6)

# Crossing markers and lines
axins.axvline(t_star, color=WHITE, linestyle='--', linewidth=1.2, alpha=0.85)
axins.plot([t_lo, t_star], [alpha_at_tstar, alpha_at_tstar],
           color=WHITE, linestyle='--', linewidth=1.2, alpha=0.85)
axins.scatter([t_star], [alpha_at_tstar], s=90, color=GOLD, edgecolor=WHITE,
              linewidth=1.6, zorder=8, marker='o')

axins.set_xlim(t_lo, t_hi)
axins.set_ylim(y_lo, y_hi)
axins.set_xscale('log')

# Compact ticks — only the t* tick on x; suppress all minor ticks/labels
axins.xaxis.set_major_locator(FixedLocator([t_star]))
axins.xaxis.set_major_formatter(FixedFormatter([r'$t^{*}$']))
axins.xaxis.set_minor_locator(NullLocator())
axins.tick_params(axis='x', which='major', labelsize=10)
axins.set_yticks([0, alpha_at_tstar, 0.02])
axins.set_yticklabels(['0', r'$\alpha$', '0.02'], fontsize=9)

# Subtle styling on inset axes
for spine in axins.spines.values():
    spine.set_edgecolor(GRAY)
    spine.set_linewidth(1.0)
axins.tick_params(colors=WHITE, length=3)
axins.set_facecolor('#0a0a1a')

# Connect inset to the main-plot region it magnifies
mark_inset(ax, axins, loc1=2, loc2=4, fc='none', ec=GRAY, lw=0.8, alpha=0.6)

# Legend top center, off the bands
ax.legend(fontsize=10.5, loc='upper center', framealpha=0.92,
          bbox_to_anchor=(0.5, -0.13), ncol=2)

# Footer — caption-grade math reference
fig.text(0.5, -0.05,
         r'Multiplicities: $d_k = \binom{k+3}{3}^{2} - \binom{k+2}{3}^{2}$ '
         r'(full),  $\mathrm{tr}(\tau|V_k) = \binom{k+3}{3} - \binom{k+2}{3}$ '
         r'($\tau$-fixed).  Eigenvalues $\lambda_k = k(k+3)$.',
         ha='center', va='top', fontsize=9.5, color=GRAY, style='italic')

plt.tight_layout()
save(fig, 'v2_alpha_survival_ratio.png')

print(f"t*               = {t_star:.6f}")
print(f"Θ^τ(t*)/Θ_CP³(t*) = {alpha_at_tstar:.6f}  (= α)")
print(f"1/α              = {alpha_inv_at_tstar:.4f}")
print(f"observed 1/α     = {alpha_inv_obs:.4f}")
print(f"error            = {(alpha_inv_at_tstar/alpha_inv_obs - 1)*100:+.3f}%")

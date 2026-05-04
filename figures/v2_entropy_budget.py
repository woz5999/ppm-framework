"""
Entropy budget across scales — Fig. for ch09-thermodynamics.

Shows constant entropy production ΔS ≈ 5.5 k_B per event vs
declining information yield I(k) as a function of k-level.
Crossing at k ≈ 73 marks the quantum-classical boundary (at T=310K).
QCD confinement at k ≈ 51 shown as a separate transition.

(Consciousness-window content was previously layered onto this figure
but was removed 2026-04-30: ch09 doesn't introduce or use the
consciousness window, and the band created visual clutter without
serving the chapter's purpose. A consciousness-flavored version of
this figure belongs in a later chapter where the multiple-bound
convergence story is being told.)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from ppm.consciousness import DELTA_S_PER_EVENT, K_B_JK, T_BODY_K
from ppm.hierarchy import energy_mev
from _style import apply_style, GOLD, VIOLET, CYAN, WHITE, GRAY, RED, BG

apply_style()

# --- Data ---
k_min_plot, k_max_plot = 40, 80
k_vals = np.linspace(k_min_plot, k_max_plot, 500)

delta_s_nats = DELTA_S_PER_EVENT  # ≈ 5.51 nats

def info_nats(k, T_K=T_BODY_K):
    E_mev = energy_mev(k)
    E_joules = E_mev * 1.602e-13
    k_BT = K_B_JK * T_K
    R = E_joules / k_BT
    if R <= 1.0:
        return 0.0
    return 3.0 * np.log(R)

info_vals = np.array([info_nats(k) for k in k_vals])

# Find crossing point
for i in range(len(k_vals) - 1):
    if info_vals[i] >= delta_s_nats and info_vals[i+1] < delta_s_nats:
        frac = (delta_s_nats - info_vals[i+1]) / (info_vals[i] - info_vals[i+1])
        k_cross = k_vals[i+1] - frac * (k_vals[i+1] - k_vals[i])
        break
else:
    k_cross = 73.0

# --- Plot ---
fig, ax = plt.subplots(figsize=(16, 10), facecolor=BG)
ax.set_facecolor(BG)

# ── Background texture: subtle radial glow centered on crossing ──
for r in np.linspace(2, 40, 30):
    c = plt.Circle((k_cross, delta_s_nats), r, facecolor='none',
                    edgecolor=CYAN, alpha=0.008, lw=0.8, zorder=0,
                    transform=ax.transData)
    ax.add_patch(c)

# ── Fill between curves — quantum vs classical domains ──
quantum_mask = info_vals > delta_s_nats
classical_mask = info_vals < delta_s_nats

for alpha_step in [0.03, 0.06, 0.09]:
    ax.fill_between(k_vals, delta_s_nats, info_vals,
                    where=quantum_mask, alpha=alpha_step, color=VIOLET, zorder=1)
    ax.fill_between(k_vals, info_vals, delta_s_nats,
                    where=classical_mask, alpha=alpha_step, color=GOLD, zorder=1)

# ── Main curves — with glow ──
ax.plot(k_vals, np.full_like(k_vals, delta_s_nats), color=GOLD, linewidth=8,
        alpha=0.15, zorder=2)
ax.plot(k_vals, info_vals, color=VIOLET, linewidth=8, alpha=0.15, zorder=2)

ax.plot(k_vals, np.full_like(k_vals, delta_s_nats), color=GOLD, linewidth=3.5,
        linestyle='--', label=r'Entropy production $\Delta S \approx 5.5\, k_B$',
        zorder=3)
ax.plot(k_vals, info_vals, color=VIOLET, linewidth=3.5,
        label=r'Information yield $I(k) = 3\ln R(k)$', zorder=3)

# ── Crossing point — prominent marker with glow ──
ax.plot(k_cross, delta_s_nats, 'o', color=CYAN, markersize=20, zorder=5,
        markeredgecolor=WHITE, markeredgewidth=2.5, alpha=0.3)
ax.plot(k_cross, delta_s_nats, 'o', color=CYAN, markersize=14, zorder=6,
        markeredgecolor=WHITE, markeredgewidth=2)

ax.annotate(f'$I = \\Delta S$ crossover\n$k \\approx {k_cross:.0f}$  (310 K)',
            xy=(k_cross, delta_s_nats),
            xytext=(k_cross + 4, delta_s_nats + 14),
            color=CYAN, fontsize=15, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=CYAN, lw=2.0,
                            connectionstyle='arc3,rad=-0.2'),
            ha='left', zorder=7)

# ── Consciousness band (R ≈ 1) overlay ────────────────────────────────────
# The R ≈ 1 boundary is a different criterion than the I = ΔS crossover.
# R(k) = E(k)/k_BT crosses unity at k ≈ 75; the I = ΔS information-vs-
# entropy crossover sits at k ≈ 73.  Both lie in a narrow band.  Label
# is placed below the x-axis, parallel to the particle-level labels, so
# it does not collide with the I(k) curve, the QUANTUM watermark, or the
# crossover annotation.
k_R1_lo, k_R1_hi = 73.0, 76.5
ax.axvspan(k_R1_lo, k_R1_hi, color=CYAN, alpha=0.10, zorder=0)

# ── QCD confinement marker — single line label ──
k_qcd = 51
ax.axvline(k_qcd, color=RED, alpha=0.15, linewidth=5, zorder=1)
ax.axvline(k_qcd, color=RED, alpha=0.7, linewidth=2.0, linestyle='-.',
           zorder=2)
ax.text(k_qcd + 0.5, max(info_vals) * 0.95, 'QCD confinement',
        color=RED, fontsize=16, alpha=0.9, va='top', ha='left',
        fontweight='bold')

# ── Regime labels — watermark style, placed clear of curves and arrows ──
# QUANTUM sits in the wide low-k portion of the violet region, well above
# the ΔS line and well below the (much higher) I(k) curve there.  At k=44
# the I(k) curve sits near ~75 nats while ΔS ≈ 5.5; placing the label at
# y ≈ 30 keeps it inside the shaded region without touching either curve
# or the QCD/crossover labels.
ax.text(44.5, 30.0, 'QUANTUM', color=VIOLET,
        fontsize=28, fontweight='bold', ha='center', alpha=0.40, zorder=1)
# CLASSICAL lives in the small post-crossover gold region (between I(k)
# and the ΔS line for k > k_cross).  Place horizontally near the bottom
# right so it does not collide with the crossover annotation arrow.
ax.text(78.0, 2.3, 'CLASSICAL', color=GOLD,
        fontsize=14, fontweight='bold', ha='center', alpha=0.65, zorder=1)

# ── Key k-levels along bottom — neutral color, no EWSB ──
key_levels = [
    (48, r'$\tau$'),
    (51.5, r'$\mu$'),
    (57, r'$e^-$'),
]
for k_lev, name in key_levels:
    if k_lev >= k_min_plot:
        ax.axvline(k_lev, color=GRAY, alpha=0.4, linewidth=1.0, linestyle=':',
                   zorder=1)
        ax.text(k_lev, -1.5, name, color=GRAY, fontsize=14, ha='center',
                alpha=1.0, fontweight='bold')

# R ≈ 1 band label, vertical text at the top of the band — well above the
# I(k) curve (which is below 5.5 inside the band) and below the legend.
ax.text(0.5*(k_R1_lo + k_R1_hi), 50.0,
        r'$R \approx 1$ band',
        color=CYAN, fontsize=13, ha='center', va='center',
        rotation=90, alpha=0.85, fontweight='bold', zorder=2)

# ── Axes — y=0 at bottom of plot ──
ax.set_xlabel('$k$-level (energy hierarchy)', fontsize=20, color=WHITE)
ax.set_ylabel(r'nats ($k_B$ units) per event', fontsize=20, color=WHITE)
ax.set_xlim(k_min_plot, k_max_plot)
ax.set_ylim(0, max(info_vals) * 1.05)

ax.tick_params(axis='both', labelsize=16, colors=WHITE)
ax.legend(loc='upper right', fontsize=17, framealpha=0.85,
          edgecolor=GRAY, labelcolor=WHITE)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color(WHITE)
ax.spines['left'].set_color(WHITE)
ax.spines['bottom'].set_linewidth(1.5)
ax.spines['left'].set_linewidth(1.5)

plt.tight_layout()

outdir = os.path.join(os.path.dirname(__file__), '..', '..', 'figures', 'computed')
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, 'v2_entropy_budget.png')
fig.savefig(outpath, dpi=200, facecolor=BG, bbox_inches='tight', pad_inches=0.3)
plt.close(fig)
print(f"Saved: {outpath}")
print(f"Crossing at k ≈ {k_cross:.1f}")

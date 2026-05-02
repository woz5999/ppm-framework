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

# ── PPM Colors (light-theme variant) ──
BG      = '#F2F2F6'
GOLD    = '#A8841F'
VIOLET  = '#5547A8'
CYAN    = '#1A6A75'
WHITE   = '#1A1A2E'   # text-dark; named WHITE for body-code continuity
GRAY    = '#666677'
RED     = '#B83020'
VIO_LT  = '#7868C8'   # secondary violet accent (slightly lighter than VIOLET)
GOLD_LT = '#B89638'   # secondary gold accent
CYAN_LT = '#3A8A95'   # secondary cyan accent
DIM     = '#888899'
SILVER  = '#444454'   # neutral dark gray, readable on light bg

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

ax.annotate(f'quantum-classical boundary\n$k \\approx {k_cross:.0f}$  (310 K)',
            xy=(k_cross, delta_s_nats),
            xytext=(k_cross - 10, delta_s_nats + 25),
            color=CYAN, fontsize=16, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=CYAN, lw=2.5,
                            connectionstyle='arc3,rad=0.2'),
            ha='center', zorder=7)

# ── QCD confinement marker — single line label ──
k_qcd = 51
ax.axvline(k_qcd, color=RED, alpha=0.15, linewidth=5, zorder=1)
ax.axvline(k_qcd, color=RED, alpha=0.7, linewidth=2.0, linestyle='-.',
           zorder=2)
ax.text(k_qcd + 0.5, max(info_vals) * 0.95, 'QCD confinement',
        color=RED, fontsize=16, alpha=0.9, va='top', ha='left',
        fontweight='bold')

# ── Regime labels — large watermark style ──
midpoint_q = (k_min_plot + k_cross) / 2
ax.text(midpoint_q, max(info_vals) * 0.50, 'QUANTUM', color=VIOLET,
        fontsize=32, fontweight='bold', ha='center', alpha=0.45, zorder=1)
ax.text(77.5, delta_s_nats * 1.8, 'CLASSICAL', color=GOLD,
        fontsize=22, fontweight='bold', ha='center', alpha=0.55, zorder=1,
        rotation=90)

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

# ── Axes — y=0 at bottom of plot ──
ax.set_xlabel('$k$-level (energy hierarchy)', fontsize=20, color=WHITE)
ax.set_ylabel(r'nats ($k_B$ units) per event', fontsize=20, color=WHITE)
ax.set_xlim(k_min_plot, k_max_plot)
ax.set_ylim(0, max(info_vals) * 1.05)

ax.tick_params(axis='both', labelsize=16, colors=WHITE)
ax.legend(loc='upper right', fontsize=17, framealpha=0.85,
          facecolor='#FAFAFC', edgecolor=GRAY, labelcolor=WHITE)

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

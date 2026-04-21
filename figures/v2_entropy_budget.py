"""
Entropy budget across scales — Fig. for ch09-thermodynamics.

Shows constant entropy production ΔS ≈ 5.5 k_B per event vs
declining information yield I(k) as a function of k-level.
Crossing at k ≈ 73 marks the quantum-classical boundary (at T=310K).
Consciousness window marked at k ∈ (53.8, 75.75).
QCD confinement at k ≈ 51 shown as a separate transition.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from figures._style import (apply_style, BG, GOLD, VIOLET, CYAN, WHITE, GRAY,
                            RED)

from ppm.consciousness import (DELTA_S_PER_EVENT, K_B_JK, T_BODY_K,
                                consciousness_window)
from ppm.hierarchy import energy_mev

apply_style()

# --- Data ---
k_min_plot, k_max_plot = 40, 80
k_vals = np.linspace(k_min_plot, k_max_plot, 500)

# Everything in nats (units of k_B)
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

# Consciousness window from code
cw = consciousness_window(T_K=T_BODY_K)
k_conscious_min = cw['k_min']   # ≈ 53.8 (Zeno bound)
k_conscious_max = cw['k_max']   # ≈ 75.75 (Landauer bound)

# Find crossing point (I = ΔS)
for i in range(len(k_vals) - 1):
    if info_vals[i] >= delta_s_nats and info_vals[i+1] < delta_s_nats:
        frac = (delta_s_nats - info_vals[i+1]) / (info_vals[i] - info_vals[i+1])
        k_cross = k_vals[i+1] - frac * (k_vals[i+1] - k_vals[i])
        break
else:
    k_cross = 73.0

# --- Plot ---
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# Shade consciousness window
ax.axvspan(k_conscious_min, k_conscious_max, alpha=0.10, color=CYAN, zorder=0)

# Fill between to show which dominates
quantum_mask = info_vals > delta_s_nats
classical_mask = info_vals < delta_s_nats
ax.fill_between(k_vals, delta_s_nats, info_vals,
                where=quantum_mask, alpha=0.10, color=VIOLET, zorder=1)
ax.fill_between(k_vals, info_vals, delta_s_nats,
                where=classical_mask, alpha=0.10, color=GOLD, zorder=1)

# Entropy production (constant)
ax.plot(k_vals, np.full_like(k_vals, delta_s_nats), color=GOLD, linewidth=2.5,
        linestyle='--', label=r'Entropy production $\Delta S \approx 5.5\, k_B$',
        zorder=3)

# Information yield (declining)
ax.plot(k_vals, info_vals, color=VIOLET, linewidth=2.5,
        label=r'Information yield $I(k) = 3\ln R(k)$', zorder=3)

# Crossing point
ax.plot(k_cross, delta_s_nats, 'o', color=CYAN, markersize=10, zorder=5)
ax.annotate(f'quantum-classical\nboundary ($k \\approx {k_cross:.0f}$, 310 K)',
            xy=(k_cross, delta_s_nats),
            xytext=(k_cross - 14, delta_s_nats + 20),
            color=CYAN, fontsize=9,
            arrowprops=dict(arrowstyle='->', color=CYAN, lw=1.5),
            ha='center', zorder=5)

# QCD confinement marker
k_qcd = 51
ax.axvline(k_qcd, color=RED, alpha=0.6, linewidth=1.5, linestyle='-.',
           zorder=2)
ax.text(k_qcd - 0.5, max(info_vals) * 0.92, 'QCD\nconfinement',
        color=RED, fontsize=9, alpha=0.8, va='top', ha='right')

# Consciousness window boundaries
ax.axvline(k_conscious_min, color=CYAN, alpha=0.3, linewidth=1, linestyle=':',
           zorder=2)
ax.axvline(k_conscious_max, color=CYAN, alpha=0.3, linewidth=1, linestyle=':',
           zorder=2)

# Consciousness window label — above the gold line
ax.text((k_conscious_min + k_conscious_max) / 2, delta_s_nats + 2.5,
        'consciousness window',
        color=CYAN, fontsize=9, ha='center', alpha=0.7, style='italic',
        zorder=4)

# Regime labels — quantum on left, classical smaller on right
midpoint_q = (k_min_plot + k_cross) / 2
ax.text(midpoint_q, max(info_vals) * 0.55, 'QUANTUM', color=VIOLET,
        fontsize=15, fontweight='bold', ha='center', alpha=0.35, zorder=1)
ax.text(77, delta_s_nats * 0.35, 'CLASSICAL', color=GOLD,
        fontsize=11, fontweight='bold', ha='center', alpha=0.35, zorder=1,
        rotation=90)

# Key k-levels along bottom
key_levels = [
    (44.5, 'EWSB'),
    (48, r'$\tau$'),
    (51.5, r'$\mu$'),
    (57, r'$e^-$'),
]
for k_lev, name in key_levels:
    if k_lev >= k_min_plot:
        ax.axvline(k_lev, color=GRAY, alpha=0.15, linewidth=0.7, linestyle=':',
                   zorder=1)
        ax.text(k_lev, -2.5, name, color=GRAY, fontsize=8, ha='center',
                alpha=0.7)

ax.set_xlabel('$k$-level (energy hierarchy)', fontsize=12)
ax.set_ylabel(r'nats ($k_B$ units) per event', fontsize=12)
ax.set_xlim(k_min_plot, k_max_plot)
ax.set_ylim(-4, max(info_vals) * 1.05)
ax.legend(loc='upper right', fontsize=10, framealpha=0.8)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()

# Save
outdir = os.path.join(os.path.dirname(__file__), '..', '..', 'figures', 'computed')
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, 'v2_entropy_budget.png')
fig.savefig(outpath, dpi=200)
plt.close(fig)
print(f"Saved: {outpath}")
print(f"Crossing at k ≈ {k_cross:.1f}")
print(f"Consciousness window: {k_conscious_min:.1f} – {k_conscious_max:.1f}")

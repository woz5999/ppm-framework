"""
v2_mixing_predictions.py — Mixing angles and CP phase predictions

Side-by-side bars: PPM (gold) vs Observed (cyan) for four parameters:
  sin²θ₁₂, sin²θ₂₃, sin²θ₁₃, δ_CP/π.

Design notes (post-review redesign):
  - Dropped θ_strong from this plot. PPM gives 0 and the experimental
    upper bound is ~10⁻¹⁰; both bars are invisible at linear scale and
    add nothing here.  θ_strong is treated separately in the strong-CP
    discussion in ch10b.
  - Consistent color coding: GOLD = PPM, CYAN = Observed, throughout.
    No red bars.  The sin²θ₁₃ panel is highlighted with a dashed border
    and an "Excluded (>5σ)" tag, but the bar colors stay on the same
    legend.
  - Floating "X%" labels removed — they were ambiguous (and read as
    "1000%" at a glance for the sin²θ₁₃ TBM-zero case).  Each panel
    now shows the bar values directly with a Δ = ppm − obs annotation
    underneath.
  - sin²θ₁₃ PPM = 0 (TBM leading order) is rendered as a labeled
    zero-height marker at y=0 with an annotation pointing to it.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from _style import apply_style, save, GOLD, WHITE, CYAN, GRAY, RED, BG

from ppm.neutrino import pmns_tribimaximal
from ppm.mixing import ckm_berry

apply_style()

# ── Data ──────────────────────────────────────────────────────────────────
pmns = pmns_tribimaximal()
ckm = ckm_berry()

# (label, ppm, obs, obs_err, excluded, note)
mixing_data = [
    (r'$\sin^2\theta_{12}$',
     pmns['sin2_theta12_ppm'],
     pmns['sin2_theta12_obs'][0], pmns['sin2_theta12_obs'][1],
     False, 'TBM: 1/3'),
    (r'$\sin^2\theta_{23}$',
     pmns['sin2_theta23_ppm'],
     pmns['sin2_theta23_obs'][0], pmns['sin2_theta23_obs'][1],
     False, 'TBM: 1/2'),
    (r'$\sin^2\theta_{13}$',
     pmns['sin2_theta13_ppm'],
     pmns['sin2_theta13_obs'][0], pmns['sin2_theta13_obs'][1],
     True,  'TBM zeroth order: 0'),
    (r'$\delta_{\mathrm{CP}}/\pi$',
     ckm['delta_cp_rad'] / np.pi,
     (ckm['observed_rad'] / np.pi if ckm['observed_rad'] else 1.2),
     0.3 / np.pi,
     False, 'Berry phase'),
]

# ── Figure ────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 7.5))

n = len(mixing_data)
x = np.arange(n)
width = 0.36

ppm_vals = np.array([d[1] for d in mixing_data])
obs_vals = np.array([d[2] for d in mixing_data])
obs_errs = np.array([d[3] for d in mixing_data])
labels   = [d[0] for d in mixing_data]
notes    = [d[5] for d in mixing_data]
excluded = [d[4] for d in mixing_data]

# Bars (single colors across the board — legend stays honest).
ax.bar(x - width/2, ppm_vals, width,
       color=GOLD, edgecolor=WHITE, linewidth=1.5, alpha=0.92,
       label='PPM prediction', zorder=3)
ax.bar(x + width/2, obs_vals, width,
       color=CYAN, edgecolor=WHITE, linewidth=1.5, alpha=0.92,
       yerr=obs_errs, capsize=6,
       error_kw={'elinewidth': 2, 'capthick': 2, 'ecolor': WHITE},
       label='Observed (±1σ)', zorder=3)

# Numeric value annotations directly above each bar.
for i, (ppm, obs) in enumerate(zip(ppm_vals, obs_vals)):
    # PPM value
    if ppm > 0:
        ax.text(i - width/2, ppm + 0.02, f'{ppm:.3f}',
                ha='center', va='bottom', fontsize=10, color=GOLD,
                fontweight='bold')
    else:
        # Zero-height case: tag the baseline.
        ax.text(i - width/2, 0.012, '0',
                ha='center', va='bottom', fontsize=11, color=GOLD,
                fontweight='bold')
    # Obs value
    ax.text(i + width/2, obs + obs_errs[i] + 0.02, f'{obs:.3f}',
            ha='center', va='bottom', fontsize=10, color=CYAN,
            fontweight='bold')

# Excluded-column highlight: dashed rectangle around the sin²θ₁₃ pair.
for i, ex in enumerate(excluded):
    if not ex:
        continue
    ax.axvspan(i - 0.5, i + 0.5, color=RED, alpha=0.07, zorder=1)
    # Label sits well above the bars, no overlap with data.
    ax.text(i, 1.15, 'Excluded (>5σ)',
            ha='center', va='center', fontsize=11, color=WHITE,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.45',
                      facecolor=RED, edgecolor=WHITE,
                      linewidth=1.5, alpha=0.92),
            zorder=5)

# Per-column footnote: TBM/Berry origin tag, just below the x-axis line.
for i, note in enumerate(notes):
    ax.text(i, -0.13, note, ha='center', va='top', fontsize=9,
            color=GRAY, style='italic')

# ── Axes / styling ─────────────────────────────────────────────────────────
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=14)
ax.set_ylabel('Value (dimensionless; δ_CP in units of π)',
              fontsize=12)
ax.set_title('Mixing-angle and CP-phase predictions',
             fontsize=15, pad=12)

ax.set_xlim(-0.6, n - 0.4)
ax.set_ylim(-0.18, 1.30)
ax.axhline(0, color=GRAY, linewidth=0.8, alpha=0.6, zorder=2)

ax.grid(True, alpha=0.25, linestyle=':', axis='y')
ax.legend(loc='upper left', fontsize=11, framealpha=0.92)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
save(fig, 'v2_mixing_predictions.png')

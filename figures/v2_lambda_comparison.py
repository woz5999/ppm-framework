"""
v2_lambda_comparison.py — Cosmological constant: prediction versus observation

Two-panel layout:
  Left  : log-scale bar chart showing the 68-order gap between QFT naive and
          observed; PPM prediction sits on top of observed at this resolution.
  Right : linear-scale detail panel zooming in on PPM vs Observed to show the
          actual ~1.5% numerical difference honestly.
"""

import sys
sys.path.insert(0, '../')

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
from _style import apply_style, save, GOLD, RED, GREEN, WHITE, GRAY, BG

from ppm.cosmology import cosmological_constant

apply_style()

# ─── Data ───────────────────────────────────────────────────────────────────
lam_result = cosmological_constant()
lambda_ppm = lam_result['Lambda_m2']
lambda_obs = lam_result['Lambda_obs']
error_pct  = lam_result['error_pct']

# ─── Figure: 2-panel layout (main on left, detail on right) ─────────────────
fig = plt.figure(figsize=(12, 5.5))
gs  = GridSpec(1, 2, width_ratios=[3.0, 1.0], wspace=0.30, figure=fig)
ax  = fig.add_subplot(gs[0, 0])
axd = fig.add_subplot(gs[0, 1])

# ============================================================================
# LEFT PANEL: log-scale comparison (3 bars)
# ============================================================================
scenarios = ['QFT Naive\nEstimate', 'PPM\nPrediction', 'Observed\nValue']
values    = [-120.0, np.log10(lambda_ppm), np.log10(lambda_obs)]
colors    = [RED, GOLD, GREEN]

value_strs = [
    r'$\sim 10^{-120}$',
    rf'$10^{{{values[1]:.1f}}}$',
    rf'$10^{{{values[2]:.1f}}}$',
]

x_pos = np.arange(len(scenarios))
ax.bar(
    x_pos, values, width=0.55, color=colors,
    alpha=0.92, edgecolor=WHITE, linewidth=0.8, zorder=3,
)

# Value labels above each bar
for x, v, txt, c in zip(x_pos, values, value_strs, colors):
    ax.text(
        x, 3, txt,
        ha='center', va='bottom',
        fontsize=13, color=c, weight='bold',
        zorder=4,
    )

# Vertical "68 orders of magnitude" annotation on the left
gap   = abs(values[0] - values[2])
gap_x = -0.55
ax.annotate(
    '', xy=(gap_x, values[0]), xytext=(gap_x, values[2]),
    arrowprops=dict(arrowstyle='<->', color=GRAY, lw=1.2),
    zorder=4,
)
ax.text(
    gap_x - 0.10, (values[0] + values[2]) / 2,
    f'{int(round(gap))} orders\nof magnitude',
    ha='right', va='center',
    fontsize=10, color=GRAY, style='italic',
    zorder=5,
)

# Axes
ax.set_ylabel(r'$\log_{10}(\Lambda)\ \ [\mathrm{m}^{-2}]$',
              fontsize=12, color=WHITE)
ax.set_xticks(x_pos)
ax.set_xticklabels(scenarios, fontsize=11, color=WHITE)
ax.tick_params(axis='x', length=0, pad=6)
ax.tick_params(axis='y', length=4)
ax.set_ylim(-135, 25)
ax.set_xlim(-1.4, len(scenarios) - 0.4)
ax.axhline(0, color=GRAY, lw=0.6, alpha=0.5, zorder=2)
ax.grid(True, axis='y', alpha=0.18, color=GRAY, lw=0.5, zorder=1)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)
ax.spines['left'].set_color(GRAY);   ax.spines['left'].set_linewidth(0.8)
ax.spines['bottom'].set_color(GRAY); ax.spines['bottom'].set_linewidth(0.8)
ax.set_title(
    'Log scale: full discrepancy',
    fontsize=11, color=WHITE, weight='bold', pad=8, loc='left',
)

# ============================================================================
# RIGHT PANEL: linear-scale detail
# ============================================================================
detail_labels = ['PPM', 'Observed']
detail_values = [lambda_ppm * 1e52, lambda_obs * 1e52]   # in units of 10^-52
detail_colors = [GOLD, GREEN]
detail_x      = np.arange(len(detail_labels))

axd.bar(
    detail_x, detail_values, width=0.55, color=detail_colors,
    alpha=0.92, edgecolor=WHITE, linewidth=0.8, zorder=3,
)
axd.set_xticks(detail_x)
axd.set_xticklabels(detail_labels, fontsize=11, color=WHITE)

# Numeric labels above each bar
for x, v, c in zip(detail_x, detail_values, detail_colors):
    axd.text(
        x, v + 0.003, f'{v:.3f}',
        ha='center', va='bottom',
        fontsize=11, color=c, weight='bold',
    )

# Bracket showing the 1.5% delta between the two
y_min = min(detail_values)
y_max = max(detail_values)
bracket_y = y_max + 0.025
ax_bracket_color = GOLD
axd.plot(
    [detail_x[0], detail_x[1]], [bracket_y, bracket_y],
    color=ax_bracket_color, lw=1.4, zorder=4,
)
axd.plot(
    [detail_x[0], detail_x[0]], [bracket_y, bracket_y - 0.005],
    color=ax_bracket_color, lw=1.4, zorder=4,
)
axd.plot(
    [detail_x[1], detail_x[1]], [bracket_y, bracket_y - 0.005],
    color=ax_bracket_color, lw=1.4, zorder=4,
)
axd.text(
    (detail_x[0] + detail_x[1]) / 2, bracket_y + 0.005,
    rf'$\Delta = {abs(error_pct):.1f}\%$',
    ha='center', va='bottom',
    fontsize=11, color=ax_bracket_color, weight='bold',
)

# Tighten range so the small gap is visible
ymin = min(detail_values) - 0.03
ymax = max(detail_values) + 0.06
axd.set_ylim(ymin, ymax)
axd.set_xlim(-0.6, 1.6)

axd.set_ylabel(r'$\Lambda\ \ [10^{-52}\ \mathrm{m}^{-2}]$',
               fontsize=11, color=WHITE)
axd.tick_params(axis='both', labelsize=10, colors=WHITE)
axd.grid(True, axis='y', alpha=0.18, color=GRAY, lw=0.4, zorder=1)
for spine in ('top', 'right'):
    axd.spines[spine].set_visible(False)
axd.spines['left'].set_color(GRAY);   axd.spines['left'].set_linewidth(0.8)
axd.spines['bottom'].set_color(GRAY); axd.spines['bottom'].set_linewidth(0.8)
axd.set_title(
    'Linear detail: PPM vs Observed',
    fontsize=11, color=WHITE, weight='bold', pad=8, loc='left',
)

# ─── Suptitle ───────────────────────────────────────────────────────────────
fig.suptitle(
    r'Cosmological Constant $\Lambda$: PPM Prediction vs Observation',
    fontsize=14, color=WHITE, weight='bold', y=0.99,
)

plt.tight_layout(rect=(0, 0, 1, 0.95))
save(fig, 'v2_lambda_comparison.png')

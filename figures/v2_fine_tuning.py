"""
Fine-tuning sensitivity — Fig. for ch01-problem-space.

Horizontal bar chart showing, for each fundamental constant:
  - Life-permitting range from published literature (shaded bar)
  - Observed value (vertical reference line)
  - PPM prediction (gold diamond with error bar, where applicable)

Constants: α, y_t, G, Λ (PPM-predicted), α_s (route identified, matching open).

Sensitivity ranges from:
  Tegmark et al. (2006), Barrow & Tipler (1986), Carr & Rees (1979),
  Hogan (2000), Jaffe et al. (2009), Degrassi et al. (2012).

Run: python v2_fine_tuning.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from figures._style import apply_style, BG, GOLD, VIOLET, CYAN, WHITE, GRAY, RED

apply_style()

plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 22,
    'axes.labelsize': 18,
})

# ── Colors ──
SILVER  = '#C0C0C0'
GOLD_LT = '#F0D880'
BAR_COL = '#5A7FA0'   # neutral steel-blue — no theoretical meaning

# ═══════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════

from ppm.gravity import newton_constant
from ppm.cosmology import cosmological_constant
from ppm import constants as C

G_result = newton_constant()
Lambda_result = cosmological_constant()

entries = [
    {
        'name':  r'$\alpha$',
        'sub':   'fine-structure constant',
        'obs':   1/137.036,
        'log_lo': np.log10(0.5),
        'log_hi': np.log10(2.0),
        'ppm':   1/137.036,
        'ppm_err': 0.16,
        'threat_lo': 'no stable atoms',
        'threat_hi': 'no chemistry',
    },
    {
        'name':  r'$y_t$',
        'sub':   'top Yukawa coupling',
        'obs':   C.Y_TOP_OBSERVED,
        'log_lo': np.log10(0.8),       # ~20% lower → EWSB scale shifts dramatically
        'log_hi': np.log10(1.05),      # ~5% higher → EW vacuum unstable
        'ppm':   C.Y_TOP_PPM,
        'ppm_err': abs((C.Y_TOP_PPM / C.Y_TOP_OBSERVED - 1.0) * 100),
        'threat_lo': 'EWSB disrupted',
        'threat_hi': 'vacuum unstable',
    },
    {
        'name':  r'$G$',
        'sub':   'gravitational constant',
        'obs':   6.674e-11,
        'log_lo': np.log10(0.1),
        'log_hi': np.log10(10.0),
        'ppm':   G_result['G_ppm_si'],
        'ppm_err': abs(G_result['error_pct']),
        'threat_lo': 'no stellar ignition',
        'threat_hi': 'stellar collapse',
    },
    {
        'name':  r'$\Lambda$',
        'sub':   'cosmological constant',
        'obs':   1.1e-52,
        'log_lo': np.log10(0.01),
        'log_hi': np.log10(10.0),
        'ppm':   Lambda_result['Lambda_m2'],
        'ppm_err': abs(Lambda_result['error_pct']),
        'threat_lo': 'universe recollapses',
        'threat_hi': 'no structure formation',
    },
]

# ═══════════════════════════════════════════════════════════════
# PLOT
# ═══════════════════════════════════════════════════════════════

n = len(entries)
fig, ax = plt.subplots(figsize=(16, 10), facecolor=BG)
ax.set_facecolor(BG)

# Background texture
for r in np.linspace(1, 18, 25):
    c = plt.Circle((0, n/2 * 1.4), r, facecolor='none',
                    edgecolor=VIOLET, alpha=0.005, lw=0.8, zorder=0)
    ax.add_patch(c)

bar_height = 0.55
y_spacing = 1.5
y_positions = [(n - 1 - i) * y_spacing for i in range(n)]

# Horizontal offset: shift all bars/markers right so left labels don't overlap bars
X_OFF = 0.6

for i, entry in enumerate(entries):
    y = y_positions[i]
    lo = entry['log_lo'] + X_OFF
    hi = entry['log_hi'] + X_OFF

    # ── Life-permitting range bar ──
    # Glow layers
    for pad_step in [0.08, 0.04]:
        bar_glow = FancyBboxPatch((lo - pad_step, y - bar_height/2 - pad_step),
                                   (hi - lo) + 2*pad_step, bar_height + 2*pad_step,
                                   boxstyle="round,pad=0.03",
                                   facecolor=BAR_COL, edgecolor='none',
                                   alpha=0.04, zorder=1)
        ax.add_patch(bar_glow)

    # Main bar
    bar = FancyBboxPatch((lo, y - bar_height/2), hi - lo, bar_height,
                          boxstyle="round,pad=0.02",
                          facecolor=BAR_COL, edgecolor=BAR_COL,
                          alpha=0.22, lw=0, zorder=2)
    ax.add_patch(bar)
    bar_border = FancyBboxPatch((lo, y - bar_height/2), hi - lo, bar_height,
                                 boxstyle="round,pad=0.02",
                                 facecolor='none', edgecolor=BAR_COL,
                                 alpha=0.6, lw=1.5, zorder=3)
    ax.add_patch(bar_border)

    # ── Threat labels at bar edges ──
    if entry['threat_lo']:
        ax.text(lo - 0.06, y, entry['threat_lo'],
                ha='right', va='center', fontsize=13, color=RED,
                alpha=0.75, style='italic', zorder=5)
    if entry['threat_hi']:
        ax.text(hi + 0.06, y, entry['threat_hi'],
                ha='left', va='center', fontsize=13, color=RED,
                alpha=0.75, style='italic', zorder=5)

    # ── PPM prediction marker ──
    if entry['ppm'] is not None and entry['ppm_err'] is not None:
        ppm_pos = np.log10(entry['ppm'] / entry['obs']) + X_OFF
        err_log = entry['ppm_err'] / 100.0 * 0.4343  # d(log10)/d(ln)
        err_log_vis = max(err_log, 0.018)

        # Glow
        ax.plot(ppm_pos, y, 'D', color=GOLD, markersize=18,
                alpha=0.2, zorder=6)
        # Marker + error bar
        ax.errorbar(ppm_pos, y, xerr=err_log_vis, fmt='D', color=GOLD,
                    markersize=11, markeredgecolor=WHITE, markeredgewidth=1.5,
                    capsize=6, capthick=2, elinewidth=2, ecolor=GOLD,
                    alpha=0.95, zorder=7)
        # Error label
        err_str = f'{entry["ppm_err"]:.1f}%' if entry['ppm_err'] >= 0.1 else f'{entry["ppm_err"]:.2f}%'
        ax.text(ppm_pos, y + bar_height/2 + 0.13,
                err_str,
                ha='center', va='bottom', fontsize=13, color=GOLD_LT,
                alpha=0.85, fontweight='bold', zorder=7)

    # ── Labels (left side) ──
    ax.text(-2.65, y + 0.15, entry['name'], ha='left', va='center',
            fontsize=24, color=WHITE, fontweight='bold', zorder=5)
    ax.text(-2.65, y - 0.25, entry['sub'], ha='left', va='center',
            fontsize=13, color=SILVER, alpha=0.7, zorder=5)

# ── Central reference line (observed) ──
ax.axvline(X_OFF, color=WHITE, lw=1.2, alpha=0.35, linestyle=':', zorder=1)
ax.text(X_OFF, y_positions[0] + bar_height/2 + 0.6, 'observed',
        ha='center', va='bottom', fontsize=15, color=WHITE, alpha=0.5, zorder=5)

# ── X-axis ──
xtick_positions = [X_OFF - 2, X_OFF - 1, X_OFF, X_OFF + 1, X_OFF + 2]
xtick_labels = [r'$\times 0.01$', r'$\times 0.1$',
                r'$\times 1$', r'$\times 10$', r'$\times 100$']
ax.set_xticks(xtick_positions)
ax.set_xticklabels(xtick_labels, fontsize=15, color=WHITE)
ax.set_xlabel('factor relative to observed value',
              fontsize=18, color=WHITE, labelpad=12)

# ── Y-axis ──
ax.set_yticks([])
ax.set_xlim(-2.75, 3.0)
ax.set_ylim(-1.5, y_positions[0] + 1.4)

# ── Legend (contained box, upper right) ──
leg_x0 = 1.6
leg_y0 = y_positions[0] + 0.3
leg_w = 1.3
leg_h = 1.0

leg_bg = FancyBboxPatch((leg_x0, leg_y0), leg_w, leg_h,
                          boxstyle="round,pad=0.1",
                          facecolor=BG, edgecolor=SILVER,
                          alpha=0.9, lw=1.0, zorder=8)
ax.add_patch(leg_bg)

ly1 = leg_y0 + 0.7
ly2 = leg_y0 + 0.3
lx_icon = leg_x0 + 0.2
lx_text = leg_x0 + 0.42

# PPM prediction
ax.plot(lx_icon, ly1, 'D', color=GOLD, markersize=9,
        markeredgecolor=WHITE, markeredgewidth=1.0, zorder=9)
ax.text(lx_text, ly1, 'PPM prediction', color=GOLD, fontsize=13,
        va='center', zorder=9)

# Life-permitting range
bar_leg = FancyBboxPatch((lx_icon - 0.12, ly2 - 0.1), 0.24, 0.2,
                           boxstyle="round,pad=0.02",
                           facecolor=BAR_COL, edgecolor=BAR_COL,
                           alpha=0.3, lw=1.2, zorder=9)
ax.add_patch(bar_leg)
ax.text(lx_text, ly2, 'life-permitting range', color=SILVER, fontsize=13,
        va='center', zorder=9)

# ── Spines ──
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_linewidth(1.5)

plt.tight_layout()

# ── Save ──
outdir = os.path.join(os.path.dirname(__file__), '..', '..', 'figures', 'computed')
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, 'v2_fine_tuning.png')
fig.savefig(outpath, dpi=200, facecolor=BG, bbox_inches='tight', pad_inches=0.3)
plt.close(fig)
print(f"Saved: {outpath}")

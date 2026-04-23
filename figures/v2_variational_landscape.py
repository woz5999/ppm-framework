"""
Variational landscape across scales — Fig. for ch08-variational.

Schematic showing how the F landscape reshapes at each symmetry-breaking
threshold. k on horizontal axis, stylized F(q) potential profiles drawn
at each key scale: Planck (broad minimum), Pati-Salam (bifurcation),
EWSB (Mexican hat), QCD (deep well), classical/consciousness (shallow basin).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from figures._style import apply_style, BG, GOLD, VIOLET, CYAN, WHITE, GRAY

apply_style()

# Override key sizes for figure-quality output
plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 22,
    'axes.labelsize': 20,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
})

# ── PPM accent colors ──
SILVER   = '#C0C0C0'
VIO_LT   = '#C4B8FF'
GOLD_LT  = '#F0D880'
CYAN_LT  = '#40E8E0'

# --- Scale thresholds with evenly-spaced plot positions ---
thresholds = [
    # (plot_x, real_k, name, physics)
    (10,  1,     'Planck',             'gravity'),
    (27,  16.25, 'Pati–Salam',        'gauge unification'),
    (44,  44.5,  'EWSB',              'Higgs / mass'),
    (61,  51,    'QCD',                'confinement'),
    (78,  74,    'quantum–classical\nboundary', 'thermodynamics'),
]

# --- Color gradient: violet (low k) -> cyan (mid) -> gold (high k) ---
cmap = LinearSegmentedColormap.from_list('ppm_scale',
    [(0.0, VIOLET), (0.45, CYAN), (1.0, GOLD)])

def color_at_k(real_k):
    return cmap(real_k / 80.0)

# --- Stylized potential profiles ---
def planck_potential(q):
    return 0.15 * q**6

def pati_salam_potential(q):
    return -0.55 * q**2 + 0.35 * q**4 + 0.25

def ewsb_potential(q):
    return -0.8 * q**2 + 0.4 * q**4 + 0.42

def qcd_potential(q):
    return 2.0 * q**2 - 0.6 * np.exp(-8 * q**2)

def classical_potential(q):
    return 0.08 * q**2 + 0.04 * np.cos(12 * q) + 0.02

potentials = [planck_potential, pati_salam_potential, ewsb_potential,
              qcd_potential, classical_potential]

# --- Layout ---
fig, ax = plt.subplots(figsize=(16, 10))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# ── Background texture: subtle radial glow ──
for r in np.linspace(2, 50, 30):
    c = plt.Circle((44, 1.5), r, facecolor='none',
                    edgecolor=VIOLET, alpha=0.006, lw=0.8, zorder=0)
    ax.add_patch(c)

# Configuration space range for inset profiles
q = np.linspace(-1.5, 1.5, 300)

# Inset profile dimensions
profile_width = 12.0
profile_height = 3.0
y_base = 0.0

# Draw each potential profile
for i, (px, real_k, name, physics) in enumerate(thresholds):
    pot_fn = potentials[i]
    col = color_at_k(real_k)

    q_scaled = q / 1.5 * (profile_width / 2)
    x_coords = px + q_scaled

    V = pot_fn(q)
    V = V - V.min()
    V_max = V.max() if V.max() > 0 else 1.0
    V_norm = V / V_max * profile_height + y_base

    # Glow layer under curve
    ax.fill_between(x_coords, y_base - 0.03, V_norm, color=col, alpha=0.06, zorder=1)
    # Stronger fill near baseline
    ax.fill_between(x_coords, y_base - 0.03, V_norm, color=col, alpha=0.10, zorder=1,
                    where=(V_norm < profile_height * 0.4 + y_base))

    # Glow line
    ax.plot(x_coords, V_norm, color=col, linewidth=6, alpha=0.15, zorder=2)
    # Main curve
    ax.plot(x_coords, V_norm, color=col, linewidth=3.0, zorder=3)

    # Baseline
    ax.plot([px - profile_width/2, px + profile_width/2],
            [y_base, y_base], color=col, linewidth=1.0, alpha=0.4, zorder=2)

    # Scale name above profile
    y_top = profile_height + y_base + 0.2
    ax.text(px, y_top, name, color=col, fontsize=18, fontweight='bold',
            ha='center', va='bottom', zorder=5)

    # Physics label below name
    label_offset = -0.25 if '\n' not in name else -0.55
    ax.text(px, y_top + label_offset, physics, color=col, fontsize=14,
            ha='center', va='top', alpha=0.7, style='italic', zorder=5)

    # Mark minima with dots (larger)
    V_min_idx = np.argmin(V_norm)
    if name in ['Pati–Salam', 'EWSB'] or 'boundary' in name:
        window = 10 if 'boundary' in name else 20
        min_indices = []
        for j in range(window, len(V_norm) - window):
            if V_norm[j] == min(V_norm[j-window:j+window]):
                if not min_indices or j - min_indices[-1] > window:
                    min_indices.append(j)
        ms = 6 if 'boundary' in name else 8
        for mi in min_indices:
            # Glow marker
            ax.plot(x_coords[mi], V_norm[mi], 'o', color=col, markersize=ms+6,
                    alpha=0.2, zorder=3.5)
            ax.plot(x_coords[mi], V_norm[mi], 'o', color=col, markersize=ms,
                    zorder=4, markeredgecolor=WHITE, markeredgewidth=1.0)
    else:
        ax.plot(x_coords[V_min_idx], V_norm[V_min_idx], 'o', color=col,
                markersize=10, alpha=0.2, zorder=3.5)
        ax.plot(x_coords[V_min_idx], V_norm[V_min_idx], 'o', color=col,
                markersize=7, zorder=4, markeredgecolor=WHITE, markeredgewidth=1.0)

# --- Cascade arrows between profiles ---
arrow_y = profile_height * 0.45 + y_base
for i in range(len(thresholds) - 1):
    px1 = thresholds[i][0] + profile_width / 2 + 0.3
    px2 = thresholds[i+1][0] - profile_width / 2 - 0.3
    if px2 > px1:
        ax.annotate('', xy=(px2, arrow_y), xytext=(px1, arrow_y),
                    arrowprops=dict(arrowstyle='->', color=SILVER, lw=1.8,
                                   alpha=0.4, mutation_scale=16))

# --- Axis labels ---
ax.set_xlabel('$k$-level  (energy hierarchy)', fontsize=20, labelpad=12)
ax.set_ylabel(r'$\mathcal{F}\,(q)$  (schematic)', fontsize=20, labelpad=12)

# --- Formatting ---
ax.set_xlim(-2, 92)
ax.set_ylim(-0.6, profile_height + y_base + 2.0)
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_alpha(0.3)
ax.spines['bottom'].set_linewidth(1.5)
ax.spines['left'].set_linewidth(1.5)

# k-axis ticks
ax.set_xticks([t[0] for t in thresholds])
ax.set_xticklabels([str(t[1]) for t in thresholds], fontsize=16)

# --- Annotation: same F, different landscape ---
ax.text(0.98, 0.03,
        r'Same functional $\mathcal{F}$, different constraints $\longrightarrow$ different landscapes',
        transform=ax.transAxes, fontsize=14, color=SILVER, alpha=0.5,
        ha='right', va='bottom', style='italic')

# Energy direction arrow along top
ax.annotate('', xy=(5, profile_height + y_base + 1.6),
            xytext=(85, profile_height + y_base + 1.6),
            arrowprops=dict(arrowstyle='<-', color=SILVER, lw=1.5, alpha=0.3))
ax.text(45, profile_height + y_base + 1.75, 'decreasing energy',
        color=SILVER, fontsize=13, ha='center', alpha=0.35, style='italic')

plt.tight_layout()

# --- Save ---
outdir = os.path.join(os.path.dirname(__file__), '..', '..', 'figures', 'computed')
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, 'v2_variational_landscape.png')
fig.savefig(outpath, dpi=200)
plt.close(fig)
print(f"Saved: {outpath}")

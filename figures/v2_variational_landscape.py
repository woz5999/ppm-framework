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

# --- Scale thresholds with evenly-spaced plot positions ---
# Real k-values shown as tick labels; plot positions spread for clarity
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
    """Broad single minimum — unconstrained geometry, flat-bottomed."""
    return 0.15 * q**6

def pati_salam_potential(q):
    """Bifurcation — flat direction acquires curvature, two minima."""
    return -0.55 * q**2 + 0.35 * q**4 + 0.25

def ewsb_potential(q):
    """Mexican hat cross-section — Higgs VEV in the trough."""
    return -0.8 * q**2 + 0.4 * q**4 + 0.42

def qcd_potential(q):
    """Deep narrow well — color-neutral confinement minimum."""
    return 2.0 * q**2 - 0.6 * np.exp(-8 * q**2)

def classical_potential(q):
    """Shallow thermal basin — many nearly degenerate minima."""
    return 0.08 * q**2 + 0.04 * np.cos(12 * q) + 0.02

potentials = [planck_potential, pati_salam_potential, ewsb_potential,
              qcd_potential, classical_potential]

# --- Layout ---
fig, ax = plt.subplots(figsize=(14, 6.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# Configuration space range for inset profiles
q = np.linspace(-1.5, 1.5, 300)

# Inset profile dimensions
profile_width = 12.0   # width of each profile in plot-x units
profile_height = 2.5   # normalized height
y_base = 0.0

# Draw each potential profile
for i, (px, real_k, name, physics) in enumerate(thresholds):
    pot_fn = potentials[i]
    col = color_at_k(real_k)

    # Scale q to plot coordinates centered at px
    q_scaled = q / 1.5 * (profile_width / 2)
    x_coords = px + q_scaled

    # Compute and normalize potential
    V = pot_fn(q)
    V = V - V.min()
    V_max = V.max() if V.max() > 0 else 1.0
    V_norm = V / V_max * profile_height + y_base

    # Fill under curve
    ax.fill_between(x_coords, y_base - 0.03, V_norm, color=col, alpha=0.10, zorder=1)

    # Draw the potential curve
    ax.plot(x_coords, V_norm, color=col, linewidth=2.2, zorder=3)

    # Baseline
    ax.plot([px - profile_width/2, px + profile_width/2],
            [y_base, y_base], color=col, linewidth=0.7, alpha=0.35, zorder=2)

    # Scale name above profile
    y_top = profile_height + y_base + 0.15
    ax.text(px, y_top, name, color=col, fontsize=11, fontweight='bold',
            ha='center', va='bottom', zorder=5)

    # Physics label below name
    # Adjust offset for multiline names
    label_offset = -0.20 if '\n' not in name else -0.45
    ax.text(px, y_top + label_offset, physics, color=col, fontsize=8.5,
            ha='center', va='top', alpha=0.65, style='italic', zorder=5)

    # Mark minima with dots
    V_min_idx = np.argmin(V_norm)
    if name in ['Pati–Salam', 'EWSB'] or 'boundary' in name:
        # Find all local minima
        window = 10 if 'boundary' in name else 20
        min_indices = []
        for j in range(window, len(V_norm) - window):
            if V_norm[j] == min(V_norm[j-window:j+window]):
                if not min_indices or j - min_indices[-1] > window:
                    min_indices.append(j)
        ms = 4 if 'boundary' in name else 5
        for mi in min_indices:
            ax.plot(x_coords[mi], V_norm[mi], 'o', color=col, markersize=ms,
                    zorder=4, markeredgecolor=WHITE, markeredgewidth=0.5)
    else:
        ax.plot(x_coords[V_min_idx], V_norm[V_min_idx], 'o', color=col,
                markersize=5, zorder=4, markeredgecolor=WHITE, markeredgewidth=0.5)

# --- Cascade arrows between profiles ---
arrow_y = profile_height * 0.45 + y_base
for i in range(len(thresholds) - 1):
    px1 = thresholds[i][0] + profile_width / 2 + 0.2
    px2 = thresholds[i+1][0] - profile_width / 2 - 0.2
    if px2 > px1:
        ax.annotate('', xy=(px2, arrow_y), xytext=(px1, arrow_y),
                    arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.0,
                                   alpha=0.3))

# --- Axis labels ---
ax.set_xlabel('$k$-level  (energy hierarchy)', fontsize=13, labelpad=10)
ax.set_ylabel(r'$\mathcal{F}\,(q)$  (schematic)', fontsize=13, labelpad=10)

# --- Formatting ---
ax.set_xlim(-2, 92)
ax.set_ylim(-0.6, profile_height + y_base + 1.6)
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_alpha(0.3)

# k-axis ticks at real k-values, positioned at plot positions
ax.set_xticks([t[0] for t in thresholds])
ax.set_xticklabels([str(t[1]) for t in thresholds], fontsize=10)

# --- Annotation: same F, different landscape ---
ax.text(0.98, 0.02,
        r'Same functional $\mathcal{F}$, different constraints $\longrightarrow$ different landscapes',
        transform=ax.transAxes, fontsize=9, color=GRAY, alpha=0.45,
        ha='right', va='bottom', style='italic')

# Energy direction arrow along top (low k = high energy, so arrow points LEFT)
ax.annotate('', xy=(5, profile_height + y_base + 1.3),
            xytext=(85, profile_height + y_base + 1.3),
            arrowprops=dict(arrowstyle='<-', color=GRAY, lw=1.0, alpha=0.25))
ax.text(45, profile_height + y_base + 1.4, 'decreasing energy',
        color=GRAY, fontsize=8, ha='center', alpha=0.3, style='italic')

plt.tight_layout()

# --- Save ---
outdir = os.path.join(os.path.dirname(__file__), '..', '..', 'figures', 'computed')
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, 'v2_variational_landscape.png')
fig.savefig(outpath, dpi=200)
plt.close(fig)
print(f"Saved: {outpath}")

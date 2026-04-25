"""
v2_born_mechanism.py — Pointwise conjugate pairing on the unit circle.

Companion to the closed-loop diffusion image (born-rule-closed.png).  The
diffusion image shows the 720-degree topology; this figure shows the
algebraic mechanism that topology enforces: at every angle theta, the pair
(psi(theta), psi*(theta)) is reflection-symmetric across the real axis,
so psi . psi* lands on the real line with value |psi|^2.

Run:  python v2_born_mechanism.py
Output: figures/computed/v2_born_mechanism.png
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
from figures._style import apply_style, BG, GOLD, VIOLET, CYAN, WHITE, GRAY

apply_style()

plt.rcParams.update({
    'font.size': 13,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
})

# ── Figure canvas ──
fig, ax = plt.subplots(figsize=(9, 9))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# ── Unit circle (cyan — the Z2 boundary) ──
theta_full = np.linspace(0, 2*np.pi, 400)
ax.plot(np.cos(theta_full), np.sin(theta_full),
        color=CYAN, linewidth=2.2, alpha=0.85, zorder=2)
ax.plot(np.cos(theta_full), np.sin(theta_full),
        color=CYAN, linewidth=7, alpha=0.10, zorder=1)

# ── Axes (subtle) ──
ax.axhline(0, color=WHITE, linewidth=0.8, alpha=0.35, zorder=0)
ax.axvline(0, color=WHITE, linewidth=0.8, alpha=0.35, zorder=0)

# ── Sampled angles for the conjugate pairs ──
sample_angles = np.array([np.pi/6, np.pi/3, 2*np.pi/3, 5*np.pi/6])

def draw_arrow(ax, start, end, color, lw=2.2, alpha=1.0, zorder=5,
               arrowstyle='-|>', mutation_scale=18):
    arrow = FancyArrowPatch(start, end,
                            arrowstyle=arrowstyle, mutation_scale=mutation_scale,
                            color=color, lw=lw, alpha=alpha, zorder=zorder,
                            shrinkA=0, shrinkB=0)
    ax.add_patch(arrow)

for theta in sample_angles:
    p_psi   = (np.cos(theta),  np.sin(theta))
    p_conj  = (np.cos(theta), -np.sin(theta))

    # Vertical cancellation line between psi and psi* (imaginary parts annihilate)
    ax.plot([p_psi[0], p_conj[0]], [p_psi[1], p_conj[1]],
            color=WHITE, linewidth=0.9, linestyle=':', alpha=0.45, zorder=3)

    # Gold psi arrow
    draw_arrow(ax, (0, 0), p_psi, GOLD, lw=2.4, zorder=6)
    # Violet psi* arrow
    draw_arrow(ax, (0, 0), p_conj, VIOLET, lw=2.4, zorder=6)


# ── Representative theta label on one arrow pair ──
theta_label = sample_angles[1]
ax.annotate(r'$\psi(\theta)=e^{i\theta}$',
            xy=(np.cos(theta_label), np.sin(theta_label)),
            xytext=(np.cos(theta_label) + 0.18, np.sin(theta_label) + 0.18),
            color=GOLD, fontsize=14, fontweight='bold', ha='left', va='bottom',
            zorder=8)
ax.annotate(r'$\psi^{*}(\theta)=e^{-i\theta}$',
            xy=(np.cos(theta_label), -np.sin(theta_label)),
            xytext=(np.cos(theta_label) + 0.18, -np.sin(theta_label) - 0.22),
            color=VIOLET, fontsize=14, fontweight='bold', ha='left', va='top',
            zorder=8)

# Theta arc near origin (on one sample)
arc_theta = np.linspace(0, theta_label, 60)
ax.plot(0.22*np.cos(arc_theta), 0.22*np.sin(arc_theta),
        color=GOLD, linewidth=1.4, alpha=0.7, zorder=4)
ax.text(0.30*np.cos(theta_label/2), 0.30*np.sin(theta_label/2),
        r'$\theta$', color=GOLD, fontsize=13, ha='center', va='center', zorder=8)

# ── |psi|^2 = 1 marker on the real axis ──
ax.plot(1, 0, 'o', color=GOLD, markersize=16, alpha=0.22, zorder=8)
ax.plot(1, 0, 'o', color=GOLD, markersize=10, zorder=9,
        markeredgecolor=WHITE, markeredgewidth=1.4)
ax.annotate(r'$\psi\,\psi^{*}=|\psi|^{2}=1$',
            xy=(1, 0), xytext=(1.18, 0.28),
            color=WHITE, fontsize=14, fontweight='bold',
            ha='left', va='bottom',
            arrowprops=dict(arrowstyle='-', color=WHITE, alpha=0.55, lw=1.0),
            zorder=10)
ax.text(1.18, 0.10,
        r'(every $\theta$ maps here)',
        color=WHITE, fontsize=10.5, alpha=0.7, ha='left', va='bottom',
        style='italic', zorder=10)

# ── Axis labels ──
ax.text(1.38, -0.04, r'$\mathrm{Re}$',
        color=WHITE, fontsize=13, ha='left', va='top', alpha=0.75)
ax.text(0.04, 1.38, r'$\mathrm{Im}$',
        color=WHITE, fontsize=13, ha='left', va='top', alpha=0.75)

# ── Bottom caption strip (explanation) ──
ax.text(0, -1.47,
        r'At every $\theta$, $\psi$ and $\psi^{*}$ are reflections across $\mathrm{Re}$.'
        + '\n'
        + r'Their product lands on the real axis; the $720^{\circ}$ traversal pairs every point with its conjugate.',
        color=WHITE, fontsize=12.5, ha='center', va='top',
        alpha=0.85, style='italic')

# ── Title ──
ax.set_title('Conjugate pairing: why $|\\psi|^{2}$ is real',
             color=WHITE, fontsize=16, pad=14, weight='bold')

# ── Formatting ──
ax.set_xlim(-1.55, 1.75)
ax.set_ylim(-1.75, 1.55)
ax.set_aspect('equal')
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout()

# ── Save ──
outdir = os.path.join(os.path.dirname(__file__), '..', '..', 'figures', 'computed')
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, 'v2_born_mechanism.png')
fig.savefig(outpath, dpi=200)
plt.close(fig)
print(f"Saved: {outpath}")

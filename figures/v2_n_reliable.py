"""
v2_n_reliable.py — Motor Reliability: PPM prediction vs corticospinal anatomy

Redesigned with prominent anatomy bands for specific organisms and direct
annotation on plot. Removes text boxes; makes anatomy band the visual focus.

Run: python v2_n_reliable.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, save, GOLD, WHITE, CYAN, GREEN, GRAY, BG, VIOLET
from ppm.cosmology import n_reliable

apply_style()

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

t_motor_ms = np.linspace(10, 500, 200)
t_motor_s = t_motor_ms / 1000.0

n_rel_values = []
for t in t_motor_s:
    result = n_reliable(Delta_m=1e-14, t_motor=t, T_K=310.0)
    n_rel_values.append(result['N_reliable'])

# Main PPM curve
ax.semilogy(t_motor_ms, n_rel_values, color=GOLD, linewidth=3, zorder=3,
            label=r'PPM: $N_{\rm reliable}(t_{\rm motor})$')

# Anatomy bands for different organisms with labeled lines
anatomy = [
    ('Human corticospinal', 1e6, 0.8e5, GREEN),
    ('Cat corticospinal', 1.5e5, 5e4, CYAN),
    ('Rat corticospinal', 5e4, 2e4, VIOLET),
]

for name, n_high, n_low, color in anatomy:
    # Draw the band
    ax.axhspan(n_low, n_high, alpha=0.2, color=color, zorder=1)
    # Label on the right
    ax.text(480, np.sqrt(n_high * n_low), name, fontsize=10, color=color,
            ha='right', va='center', fontweight='bold')

# Mark human typical reaction time
t_human = 150.0
result_human = n_reliable(Delta_m=1e-14, t_motor=t_human/1000.0, T_K=310.0)
ax.axvline(t_human, color=WHITE, linestyle=':', linewidth=1.5, alpha=0.5, zorder=2)
ax.scatter([t_human], [result_human['N_reliable']], s=200, color=GOLD,
           edgecolor=WHITE, linewidth=2, zorder=5, marker='*')
ax.text(t_human + 10, result_human['N_reliable'] * 1.3,
        f'Human typical\n{t_human:.0f} ms',
        fontsize=10, color=WHITE, va='bottom')

ax.set_xlabel(r'Motor response time $t_{\rm motor}$ (ms)', fontsize=13, color=WHITE)
ax.set_ylabel(r'$N_{\rm reliable}$ (fibers needed)', fontsize=13, color=WHITE)
ax.set_title('Motor Reliability: PPM prediction vs corticospinal anatomy',
             fontsize=14, color=WHITE, pad=15)
ax.set_xlim(10, 500)
ax.set_ylim(1e3, 1e8)
ax.grid(True, alpha=0.2, linestyle=':', which='both')
ax.legend(fontsize=11, loc='upper right')

plt.tight_layout()
save(fig, 'v2_n_reliable.png')

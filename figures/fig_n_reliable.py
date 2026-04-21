"""
fig_n_reliable.py — Motor reliability and corticospinal anatomy

Plots N_reliable (motor threshold) vs motor response time t_motor,
showing the PPM prediction and comparison with corticospinal tract anatomy.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, new_figure, save, GOLD, WHITE, VIOLET, CYAN, GRAY, GREEN

from ppm.cosmology import n_reliable

# Generate N_reliable as a function of motor response time
t_motor_ms = np.linspace(10, 500, 100)
t_motor_s = t_motor_ms / 1000.0

n_rel_values = []
for t in t_motor_s:
    result = n_reliable(Delta_m=1e-14, t_motor=t, T_K=310.0)
    n_rel_values.append(result['N_reliable'])

# Create figure
fig, ax = new_figure(width=10, height=6)

# Main curve
ax.semilogy(t_motor_ms, n_rel_values, color=GOLD, linewidth=3,
           label='PPM prediction: N$_{\\mathrm{reliable}}$(t$_{\\mathrm{motor}}$)')

# Mark t_motor = 150 ms (human typical)
t_typical_ms = 150.0
result_typical = n_reliable(Delta_m=1e-14, t_motor=t_typical_ms/1000.0, T_K=310.0)
ax.axvline(t_typical_ms, color=CYAN, linestyle='--', linewidth=2.5, alpha=0.8,
          label=f'Human typical: {t_typical_ms} ms')
ax.scatter([t_typical_ms], [result_typical['N_reliable']], s=200, color=GOLD,
          edgecolor=WHITE, linewidth=2.5, zorder=5, marker='*')

# Corticospinal tract anatomy band (10^5 to 10^6 fibers)
ax.axhspan(1e5, 1e6, alpha=0.15, color=GREEN, label='Corticospinal tract: 10⁵–10⁶ fibers')

# Add annotations
ax.text(t_typical_ms + 30, result_typical['N_reliable'] * 0.7,
       f"PPM: {result_typical['N_reliable']:.2e}\nfibers",
       fontsize=11, color=GOLD, fontweight='bold',
       bbox=dict(boxstyle='round,pad=0.5', facecolor='#040812', edgecolor=GOLD, alpha=0.9))

ax.text(250, 3e5, 'Anatomy band', fontsize=12, color=GREEN, fontweight='bold',
       bbox=dict(boxstyle='round,pad=0.4', facecolor='#040812', edgecolor=GREEN, alpha=0.8))

# Formatting
ax.set_xlabel('Motor response time t$_{\\mathrm{motor}}$ (ms)', fontsize=13, fontweight='bold')
ax.set_ylabel('N$_{\\mathrm{reliable}}$ (log scale)', fontsize=13, fontweight='bold')
ax.set_title('Motor reliability: PPM prediction vs corticospinal anatomy',
            fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(10, 500)
ax.set_ylim(1e4, 1e7)
ax.grid(True, alpha=0.3, linestyle=':', which='both')
ax.legend(fontsize=11, loc='upper left', framealpha=0.95)

plt.tight_layout()
save(fig, 'fig_n_reliable.png')

"""
v2_decoherence.py — Gravitational decoherence prediction (FIXED)

Plots decoherence time τ_dec = 2ℏ²/(Gm³c) across a wide range of masses.
FIXED: Reference lines now use distinct colors instead of all gray.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, save, GOLD, WHITE, VIOLET, CYAN, GRAY, RED, GREEN, BLUE

from ppm.consciousness import decoherence_time
from ppm.constants import L_PLANCK_M, G_NEWTON_SI, HBAR_SI, C_LIGHT_SI

apply_style()

# Compute timescales
PLANCK_TIME_S = np.sqrt(L_PLANCK_M**3 / (G_NEWTON_SI * (HBAR_SI / (2*np.pi))))
AGE_UNIVERSE_S = 1.38e17  # ~4.35 billion years in seconds

# Generate decoherence time curve over mass range
masses_kg = np.logspace(-30, 1, 500)  # 1e-30 to 10 kg
tau_dec = np.array([decoherence_time(m) for m in masses_kg])

# Create figure
fig, ax = plt.subplots(figsize=(11, 7))

# Main curve
ax.loglog(masses_kg, tau_dec, color=GOLD, linewidth=3,
          label=r'$\tau_{\mathrm{dec}} = \frac{2\hbar^2}{Gm^3c}$')

# Reference timescales (horizontal lines) — now with distinct colors
ax.axhline(AGE_UNIVERSE_S, color=BLUE, linestyle='--', linewidth=2, alpha=0.7,
          label=f'Age of universe: {AGE_UNIVERSE_S:.2e} s')
ax.axhline(1.0, color=GREEN, linestyle='--', linewidth=2, alpha=0.7,
          label='1 second')
ax.axhline(PLANCK_TIME_S, color=RED, linestyle='--', linewidth=2, alpha=0.7,
          label=f'Planck time: {PLANCK_TIME_S:.2e} s')

# Mark specific masses with dots and labels
particles = [
    ('Planck mass', 2.176e-8, VIOLET),
    ('Proton', 1.673e-27, CYAN),
    ('Pion', 2.4e-28, CYAN),
    ('Dust grain (1 μm)', 1e-15, RED),
]

for label, mass, color in particles:
    tau = decoherence_time(mass)
    ax.scatter([mass], [tau], s=150, color=color, edgecolor=WHITE, linewidth=2, zorder=5)
    # Position labels to avoid overlap
    if mass > 1e-10:
        ax.annotate(label, xy=(mass, tau), xytext=(10, 10), textcoords='offset points',
                   fontsize=10, color=color, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='#040812', edgecolor=color, alpha=0.8),
                   arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
    else:
        ax.annotate(label, xy=(mass, tau), xytext=(-150, -20), textcoords='offset points',
                   fontsize=10, color=color, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='#040812', edgecolor=color, alpha=0.8),
                   arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

# Shaded sensitivity regions (e.g., optomechanical experiments)
ax.axvspan(1e-30, 1e-20, alpha=0.1, color=VIOLET, label='Future QM tests')
ax.axvspan(1e-15, 1e-12, alpha=0.1, color=RED, label='Optomechanical sensitivity')

# Formatting
ax.set_xlabel('Mass (kg)', fontsize=13, fontweight='bold')
ax.set_ylabel('Decoherence time (seconds)', fontsize=13, fontweight='bold')
ax.set_title('Gravitational decoherence prediction: τ$_{\\mathrm{dec}}$ = 2ℏ²/(Gm³c)',
            fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(1e-30, 10)
ax.set_ylim(1e-50, 1e50)
ax.grid(True, alpha=0.3, linestyle=':', which='both')
ax.legend(fontsize=10, loc='upper right', framealpha=0.95)

plt.tight_layout()
save(fig, 'v2_decoherence.png')

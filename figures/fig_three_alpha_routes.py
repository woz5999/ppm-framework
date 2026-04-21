"""
fig_three_alpha_routes.py — Three independent routes to α

Displays 1/α predictions from three independent derivations:
  Route I (Spectral): 137.257
  Route II (Cogito loop): ~137.6
  Route III (Instanton): PARKED
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib.pyplot as plt
from _style import apply_style, new_figure, save, GOLD, VIOLET, GRAY, WHITE
from ppm import alpha as alpha_module

# Compute the three routes
route_I = alpha_module.alpha_from_spectral_geometry()
route_II = alpha_module.alpha_from_cogito_loop()
route_III = alpha_module.alpha_from_instanton()

alpha_obs_inv = 137.036

# Data for the plot
routes = ['Route I\n(Spectral)', 'Route II\n(Cogito)', 'Route III\n(Instanton)']
values = [route_I['alpha_inv'], route_II['alpha_inv'], None]  # Route III not applicable
colors_bar = [GOLD, VIOLET, GRAY]
statuses = [route_I['status'], route_II['status'], route_III['status']]

# Create figure
fig, ax = new_figure(width=9, height=6)

# Plot bars for valid routes
x_positions = [0, 1]
bar_values = [route_I['alpha_inv'], route_II['alpha_inv']]
bar_colors = [GOLD, VIOLET]
bars = ax.barh(x_positions, bar_values, height=0.5, color=bar_colors,
               edgecolor=WHITE, linewidth=2, alpha=0.8)

# Parked route (Route III) as dashed open bar
ax.barh([2], [alpha_obs_inv], height=0.5, color='none',
        edgecolor=GRAY, linewidth=2, linestyle='--', label='Route III (PARKED)')

# Vertical line at observed value
ax.axvline(alpha_obs_inv, color=GOLD, linestyle='--', linewidth=2.5,
          label=f'Observed: 1/α = {alpha_obs_inv:.3f}')

# Annotations with errors
for i, (val, route_name) in enumerate(zip(bar_values, ['Route I', 'Route II'])):
    error_pct = abs(val - alpha_obs_inv) / alpha_obs_inv * 100
    ax.text(val + 0.2, i, f'{val:.2f}\n({error_pct:.2f}%)',
           va='center', fontsize=10, color=WHITE, fontweight='bold')

# Route III PARKED text
ax.text(alpha_obs_inv / 2, 2, 'PARKED\n(prefactor open)',
       va='center', ha='center', fontsize=10, color=GRAY, fontweight='bold',
       style='italic')

# Formatting
ax.set_yticks([0, 1, 2])
ax.set_yticklabels(routes, fontsize=11, fontweight='bold')
ax.set_xlabel('1/α prediction', fontsize=13, fontweight='bold')
ax.set_title('Three independent routes to α', fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(130, 145)
ax.grid(True, alpha=0.3, linestyle=':', axis='x')
ax.legend(fontsize=10, loc='lower right')

plt.tight_layout()
save(fig, 'fig_three_alpha_routes.png')

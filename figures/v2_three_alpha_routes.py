"""
v2_three_alpha_routes.py — Three independent routes to α

Vertical dot plot showing 1/α values for Routes I and II,
with Route III marked as parked. Compares against observed value.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import matplotlib.pyplot as plt
from _style import apply_style, save, GOLD, VIOLET, GRAY, WHITE, CYAN, BG
from ppm import alpha as alpha_module

apply_style()

route_I = alpha_module.alpha_from_spectral_geometry()
route_II = alpha_module.alpha_from_cogito_loop()
route_III = alpha_module.alpha_from_instanton()
alpha_obs_inv = 137.036

fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# Vertical dot plot - show 1/α values as points with deviations
routes = ['Route I\n(Spectral)', 'Route II\n(Cogito)', 'Route III\n(Instanton)']
values = [route_I['alpha_inv'], route_II['alpha_inv'], None]
colors = [GOLD, VIOLET, GRAY]
statuses = [route_I['status'], route_II['status'], 'PARKED']

# Horizontal band for observed value
ax.axhline(alpha_obs_inv, color=CYAN, linewidth=2.5, linestyle='-', alpha=0.6, label=f'Observed: 1/α = {alpha_obs_inv}')
ax.axhspan(alpha_obs_inv - 0.01, alpha_obs_inv + 0.01, alpha=0.15, color=CYAN)

# Plot points for Routes I and II
for i, (val, color) in enumerate(zip(values[:2], colors[:2])):
    error_pct = abs(val - alpha_obs_inv) / alpha_obs_inv * 100
    ax.scatter([i], [val], s=300, color=color, edgecolor=WHITE, linewidth=2, zorder=5)
    ax.text(i + 0.15, val, f'{val:.2f}\n({error_pct:.2f}%)', fontsize=11, color=color,
            fontweight='bold', va='center', ha='left')

# Route III: parked (show as open marker with question mark)
ax.scatter([2], [alpha_obs_inv], s=300, color='none', edgecolor=GRAY, linewidth=2.5,
           linestyle='--', zorder=5, marker='o')
ax.text(2 + 0.15, alpha_obs_inv, 'PARKED\n(prefactor open)', fontsize=10, color=GRAY,
        style='italic', va='center', ha='left')

ax.set_xticks([0, 1, 2])
ax.set_xticklabels(routes, fontsize=11)
ax.set_ylabel('1/α', fontsize=13)
ax.set_title('Three Independent Routes to α', fontsize=14, pad=15)
ax.set_xlim(-0.5, 3.0)
ax.set_ylim(135.5, 139.0)
ax.grid(True, alpha=0.3, linestyle=':', axis='y')
ax.legend(fontsize=11, loc='upper right')

plt.tight_layout()
save(fig, 'v2_three_alpha_routes.png')

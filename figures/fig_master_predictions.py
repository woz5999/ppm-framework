"""
fig_master_predictions.py — PPM Prediction Cross-Check Table

Renders the full 37-row prediction table as a publication-quality figure.
Color-codes rows by tier and status.

Run: python fig_master_predictions.py
"""

import sys
sys.path.insert(0, '../')

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from _style import apply_style, TIER_COLORS, STATUS_COLORS, BG, WHITE, GRAY, GOLD, ORANGE

from ppm.predictions import build_table


def main():
    apply_style()

    # Get prediction table
    rows = build_table()

    # Prepare table data
    columns = ['ID', 'Quantity', 'PPM Value', 'Observed', 'Error %', 'Tier', 'Status']
    cell_text = []
    colors = []

    for row in rows:
        # Format row
        ppm_val = row['ppm_value']
        obs_val = row['observed_value']
        err = row['error_pct']

        # Format numbers intelligently
        if ppm_val is None:
            ppm_str = '—'
        elif isinstance(ppm_val, float):
            if abs(ppm_val) < 1e-10 or abs(ppm_val) > 1e6:
                ppm_str = f'{ppm_val:.2e}'
            else:
                ppm_str = f'{ppm_val:.4g}'
        else:
            ppm_str = str(ppm_val)

        if obs_val is None:
            obs_str = '—'
        elif isinstance(obs_val, float):
            if abs(obs_val) < 1e-10 or abs(obs_val) > 1e6:
                obs_str = f'{obs_val:.2e}'
            else:
                obs_str = f'{obs_val:.4g}'
        else:
            obs_str = str(obs_val)

        if err is None:
            err_str = '—'
        else:
            err_str = f'{err:+.1f}%'

        cell_text.append([
            row['id'],
            row['quantity'][:30],  # Truncate long names
            ppm_str,
            obs_str,
            err_str,
            str(row['tier']),
            row['status'][:8]  # Truncate status
        ])

        # Color coding by tier and status
        tier = row['tier']
        status = row['status']

        # Primary: tier color
        tier_color = TIER_COLORS.get(tier, GRAY)
        # Override if flagged
        if status == 'FLAGGED':
            row_color = STATUS_COLORS.get('FLAGGED', ORANGE)
        else:
            row_color = tier_color

        colors.append(row_color)

    # Create figure with table
    fig = plt.figure(figsize=(14, len(rows) * 0.4 + 2))
    ax = fig.add_subplot(111)
    ax.axis('tight')
    ax.axis('off')

    # Build table
    table = ax.table(cellText=cell_text, colLabels=columns,
                     cellLoc='center', loc='center',
                     bbox=[0, 0, 1, 1])

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.0)

    # Style header
    for i in range(len(columns)):
        cell = table[(0, i)]
        cell.set_facecolor(GOLD)
        cell.set_text_props(weight='bold', color=BG)
        cell.set_edgecolor(WHITE)
        cell.set_linewidth(1.5)

    # Style data rows by tier/status
    for i, color in enumerate(colors, start=1):
        for j in range(len(columns)):
            cell = table[(i, j)]
            cell.set_facecolor(color)
            cell.set_alpha(0.25)
            cell.set_text_props(color=WHITE, fontsize=8.5)
            cell.set_edgecolor(GRAY)
            cell.set_linewidth(0.5)

    # Add legend
    legend_items = []
    legend_labels = []

    for tier in [1, 2, 3, 4]:
        if tier in TIER_COLORS:
            legend_items.append(Rectangle((0, 0), 1, 1, fc=TIER_COLORS[tier], alpha=0.25, ec=GRAY))
            legend_labels.append(f'Tier {tier}')

    legend_items.append(Rectangle((0, 0), 1, 1, fc=STATUS_COLORS['FLAGGED'], alpha=0.25, ec=GRAY))
    legend_labels.append('FLAGGED')

    ax_legend = fig.add_axes([0.12, 0.02, 0.8, 0.05])
    ax_legend.axis('off')
    ax_legend.legend(legend_items, legend_labels, ncol=6, loc='center', fontsize=10,
                    frameon=True, fancybox=True, shadow=False,
                    framealpha=0.9, edgecolor=GRAY)

    fig.text(0.5, 0.97, 'PPM Prediction Cross-Check Table', ha='center', fontsize=14,
            weight='bold', color=WHITE)
    fig.text(0.5, 0.93, f'{len(rows)} predictions: verified, flagged, and conceptual results',
            ha='center', fontsize=10, color=GRAY, style='italic')

    fig.patch.set_facecolor(BG)

    # Save
    import os
    output_dir = 'computed'
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, 'fig_master_predictions.png')
    fig.savefig(path, facecolor=BG, edgecolor='none', dpi=200, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)
    print(f"Saved: {path}")


if __name__ == '__main__':
    main()

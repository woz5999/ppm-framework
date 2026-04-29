"""
PPM Figure Style — shared matplotlib configuration for all technical figures.

Dark background matching the document's diffusion-image palette:
  background: #040812
  gold (RP³, actualized): #D4A843
  violet (CP³, possibility): #7B68EE
  cyan (Z₂ boundary): #00CED1
  white text/axes: #E0E0E0
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# ─── Color palette ──────────────────────────────────────────────────────────
BG       = '#040812'
GOLD     = '#D4A843'
VIOLET   = '#7B68EE'
CYAN     = '#00CED1'
WHITE    = '#E0E0E0'
GRAY     = '#808080'
RED      = '#E74C3C'
GREEN    = '#2ECC71'
ORANGE   = '#F39C12'
BLUE     = '#3498DB'

# Tier colors for prediction table
TIER_COLORS = {1: GREEN, 2: GOLD, 3: ORANGE, 4: RED}
STATUS_COLORS = {'VERIFIED': GREEN, 'FLAGGED': ORANGE, 'CONCEPTUAL': GRAY,
                 'FORMULA': CYAN, 'PARKED': GRAY}

# Particle category colors
CAT_COLORS = {
    'lepton': CYAN,
    'quark': VIOLET,
    'boson': GOLD,
    'meson': ORANGE,
    'scale': GRAY,
}

# ─── RC params ──────────────────────────────────────────────────────────────
PPM_RC = {
    'figure.facecolor': BG,
    'axes.facecolor': BG,
    'axes.edgecolor': WHITE,
    'axes.labelcolor': WHITE,
    'text.color': WHITE,
    'xtick.color': WHITE,
    'ytick.color': WHITE,
    'grid.color': '#1a1a2e',
    'grid.alpha': 0.5,
    'legend.facecolor': '#0a0a1a',
    'legend.edgecolor': GRAY,
    'legend.labelcolor': WHITE,
    'font.family': 'serif',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'savefig.facecolor': BG,
    'savefig.edgecolor': BG,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
}


def apply_style():
    """Apply PPM matplotlib style globally."""
    mpl.rcParams.update(PPM_RC)


# ─── Light-theme palette (for prose-figure mode) ────────────────────────────
# Use this when a figure sits in body prose where a near-black background
# reads as a "visual black hole" against the document's white pages.

BG_LIGHT     = '#F2F2F6'
PANEL_LIGHT  = '#FAFAFC'
TEXT_DARK    = '#1A1A2E'
TEXT_MUTED   = '#4A4A5C'
GRID_LIGHT   = '#CCCCD4'

# Semantic colors darkened so they stay readable on light bg.
GOLD_DARK    = '#A8841F'
VIOLET_DARK  = '#5547A8'
CYAN_DARK    = '#1A6A75'
ORANGE_DARK  = '#D86A0A'
RED_DARK     = '#B83020'
GREEN_DARK   = '#1E8048'
BLUE_DARK    = '#1A6CB0'
GRAY_DARK    = '#666677'

PPM_LIGHT_RC = {
    'figure.facecolor': BG_LIGHT,
    'axes.facecolor':   PANEL_LIGHT,
    'axes.edgecolor':   TEXT_DARK,
    'axes.labelcolor':  TEXT_DARK,
    'text.color':       TEXT_DARK,
    'xtick.color':      TEXT_DARK,
    'ytick.color':      TEXT_DARK,
    'grid.color':       GRID_LIGHT,
    'grid.alpha':       0.6,
    'legend.facecolor': PANEL_LIGHT,
    'legend.edgecolor': GRAY_DARK,
    'legend.labelcolor': TEXT_DARK,
    'font.family':       'serif',
    'font.size':         11,
    'axes.titlesize':    13,
    'axes.labelsize':    12,
    'savefig.facecolor': BG_LIGHT,
    'savefig.edgecolor': BG_LIGHT,
    'savefig.dpi':       200,
    'savefig.bbox':      'tight',
    'savefig.pad_inches': 0.15,
}


def apply_light_style():
    """Apply PPM light-theme matplotlib style (for prose-figure mode)."""
    mpl.rcParams.update(PPM_LIGHT_RC)


def new_figure(width=8, height=5, **kwargs):
    """Create a new figure with PPM styling."""
    apply_style()
    fig, ax = plt.subplots(figsize=(width, height), **kwargs)
    return fig, ax


def new_figure_multi(nrows, ncols, width=10, height=6, **kwargs):
    """Create multi-panel figure with PPM styling."""
    apply_style()
    fig, axes = plt.subplots(nrows, ncols, figsize=(width, height), **kwargs)
    return fig, axes


def save(fig, name, output_dir='computed'):
    """Save figure to computed output directory."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, name)
    fig.savefig(path)
    plt.close(fig)
    print(f"Saved: {path}")
    return path

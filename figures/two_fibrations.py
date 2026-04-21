"""
Two Fibrations of CP³: Hopf (S¹ fibers) and Twistor (S² fibers)
Computed figure for ch03-arena.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.gridspec as gridspec

# PPM color palette
BG = '#040812'
VIOLET = '#7B68EE'
CYAN = '#00CED1'
GOLD = '#D4A843'
WHITE = '#FFFFFF'
GRAY = '#666666'

fig = plt.figure(figsize=(16, 8), facecolor=BG)
gs = gridspec.GridSpec(1, 2, wspace=0.08)

def draw_base_manifold(ax, alpha=0.15):
    """Draw a translucent sphere representing CP³ as base shape."""
    u = np.linspace(0, 2*np.pi, 60)
    v = np.linspace(0, np.pi, 40)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(x, y, z, alpha=alpha, color=VIOLET,
                    edgecolor='none', shade=True)

def setup_ax(ax, title):
    """Common axis setup."""
    ax.set_facecolor(BG)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_zlim(-1.5, 1.5)
    ax.set_axis_off()
    ax.view_init(elev=20, azim=35)
    ax.set_title(title, color=WHITE, fontsize=16, fontweight='bold',
                 pad=15, fontfamily='serif')

# ── Left panel: Hopf fibration (S¹ circles) ──
ax1 = fig.add_subplot(gs[0], projection='3d', facecolor=BG)
setup_ax(ax1, 'Hopf Fibration')
draw_base_manifold(ax1, alpha=0.08)

# Draw S¹ fibers as circles at various positions/orientations on the sphere
# Hopf circles: for different base points on S², draw the corresponding S¹ fiber
np.random.seed(42)
n_fibers = 18
t = np.linspace(0, 2*np.pi, 100)

for i in range(n_fibers):
    # Pick a point on S² (base of Hopf fibration)
    theta = np.arccos(2*np.random.random() - 1)  # uniform on sphere
    phi_base = 2*np.pi*np.random.random()

    # The Hopf fiber over (theta, phi) on S² is a great circle on S³
    # Project to 3D visualization: tilt a unit circle
    # Use the base point to determine the circle's orientation
    r = 0.85 + 0.15*np.random.random()  # slight radius variation

    # Circle in a tilted plane
    nx = np.sin(theta)*np.cos(phi_base)
    ny = np.sin(theta)*np.sin(phi_base)
    nz = np.cos(theta)

    # Build orthonormal frame perpendicular to normal (nx,ny,nz)
    if abs(nz) < 0.9:
        e1 = np.cross([nx,ny,nz], [0,0,1])
    else:
        e1 = np.cross([nx,ny,nz], [1,0,0])
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross([nx,ny,nz], e1)
    e2 = e2 / np.linalg.norm(e2)

    # Circle in this plane, centered at origin
    cx = r*(e1[0]*np.cos(t) + e2[0]*np.sin(t))
    cy = r*(e1[1]*np.cos(t) + e2[1]*np.sin(t))
    cz = r*(e1[2]*np.cos(t) + e2[2]*np.sin(t))

    alpha_val = 0.4 + 0.3*np.random.random()
    lw = 1.2 + 0.8*np.random.random()
    ax1.plot(cx, cy, cz, color=CYAN, alpha=alpha_val, linewidth=lw)

# Label
ax1.text(0, 0, -1.65, '$S^1$ fibers', color=CYAN, fontsize=13,
         ha='center', fontfamily='serif', fontstyle='italic')
ax1.text(0, 0, -1.95, 'electromagnetic gauge freedom', color=GRAY,
         fontsize=10, ha='center', fontfamily='serif')

# ── Right panel: Twistor fibration (S² spheres) ──
ax2 = fig.add_subplot(gs[1], projection='3d', facecolor=BG)
setup_ax(ax2, 'Twistor Fibration')
draw_base_manifold(ax2, alpha=0.08)

# Draw S² fibers as small spheres at various positions within the manifold
n_spheres = 25
u_s = np.linspace(0, 2*np.pi, 20)
v_s = np.linspace(0, np.pi, 15)

for i in range(n_spheres):
    # Random position inside the unit sphere
    r_pos = 0.7 * np.random.random()**(1/3)  # uniform in volume
    theta_pos = np.arccos(2*np.random.random() - 1)
    phi_pos = 2*np.pi*np.random.random()

    px = r_pos * np.sin(theta_pos) * np.cos(phi_pos)
    py = r_pos * np.sin(theta_pos) * np.sin(phi_pos)
    pz = r_pos * np.cos(theta_pos)

    # Small sphere at this position
    sr = 0.08 + 0.06*np.random.random()  # radius of little sphere
    sx = px + sr*np.outer(np.cos(u_s), np.sin(v_s))
    sy = py + sr*np.outer(np.sin(u_s), np.sin(v_s))
    sz = pz + sr*np.outer(np.ones_like(u_s), np.cos(v_s))

    alpha_val = 0.35 + 0.25*np.random.random()
    ax2.plot_surface(sx, sy, sz, alpha=alpha_val, color=GOLD,
                     edgecolor='none', shade=True)

# Label
ax2.text(0, 0, -1.65, '$S^2$ fibers', color=GOLD, fontsize=13,
         ha='center', fontfamily='serif', fontstyle='italic')
ax2.text(0, 0, -1.95, 'gravitational null geodesics', color=GRAY,
         fontsize=10, ha='center', fontfamily='serif')

# Shared bottom label
fig.text(0.5, 0.02, 'CP³', color=WHITE, fontsize=20, ha='center',
         fontfamily='serif', fontweight='bold')

plt.savefig('/sessions/eager-affectionate-franklin/mnt/ppm-latex/figures/computed/v2_two_fibrations.png',
            dpi=200, bbox_inches='tight', facecolor=BG, edgecolor='none')
plt.close()
print("Done.")

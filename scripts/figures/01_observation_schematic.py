import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from matplotlib.patches import Ellipse, Rectangle, FancyArrowPatch
from matplotlib.gridspec import GridSpec

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.style import set_pub_style, COLORS, FIG_SIZE, save_fig

set_pub_style()

# Ensure output directory exists
output_dir = os.path.join(os.path.dirname(__file__), '../../site/figures')
os.makedirs(output_dir, exist_ok=True)

# Create figure with specific layout
# Adjusted layout to reduce whitespace and balance panels
# Panel A is 76:10 aspect (7.6:1). Panel B is 1:1.
# Increased top row height ratio to ensure Panel A has enough vertical room to fill the width
# Using manual layout (constrained_layout=False) to ensure strict alignment of left edges
fig = plt.figure(figsize=(10.0, 6.0))
plt.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.10, hspace=0.3, wspace=0.25)

# Adjusted width_ratios to [1, 2.0]. This makes the left column narrower (~3.0"), 
# forcing Panel B (which needs ~3.4" height) to be WIDTH-constrained.
# This ensures it fills the left column width-wise, aligning strictly with Panel A's left edge.
gs = GridSpec(2, 2, figure=fig, height_ratios=[1, 2.2], width_ratios=[1, 2.0])

# Panel A: Full System Context (Panoramic)
ax1 = fig.add_subplot(gs[0, :])

# Theme Colors
c_obs = COLORS['observation']
c_gal = COLORS['cold'] # Dark Slate for galaxy
c_bg = COLORS['background']

# --- Generate Synthetic Image Data (Schematic) ---
# Coordinates in kpc relative to galaxy center
x_extent = 75
y_extent = 10 # Reduced height to remove whitespace
X, Y = np.meshgrid(np.linspace(-8, x_extent, 600), np.linspace(-y_extent/2, y_extent/2, 200))

# 1. Host Galaxy (Elliptical)
# Distorted/Irregular galaxy
R_gal = np.sqrt((X)**2 + (1.5*Y)**2)
I_gal = 12 * np.exp(-R_gal / 1.5)

# 2. The Wake (Linear feature)
# Narrow streak from x=0 to x=62
wake_mask = (X > 0) & (X < 62) & (np.abs(Y) < 0.8)

# Add "knots" (irregular star forming clumps)
np.random.seed(42) # Fixed seed for reproducibility
noise = np.random.normal(0, 0.1, X.shape)
# Create distinct knots
knots = np.zeros_like(X)
for i in range(15):
    kx = np.random.uniform(5, 60)
    ky = np.random.normal(0, 0.2)
    ks = np.random.uniform(0.5, 2.0) # Size
    knots += 3.0 * np.exp(-((X-kx)**2 + (Y-ky)**2)/(2*ks**2))

wake_structure = (0.5 + 0.2 * np.sin(2 * np.pi * X / 3) + noise + knots) * wake_mask
I_wake = wake_structure * np.exp(-np.abs(Y)/0.4)

# 3. The Bow Shock / Tip (Bright knot at end)
# Sharp crescent shape
dist_tip = np.sqrt((X - 62)**2 + Y**2)
crescent = (X - 62) + 0.8 * Y**2
tip_mask = (crescent > -0.5) & (crescent < 0.2) & (np.abs(Y) < 1.5)
I_tip = 8.0 * np.exp(-dist_tip / 1.5) * tip_mask + 2.0 * np.exp(-dist_tip/0.5)

# Combine Intensity
I_total = I_gal + I_wake + I_tip + np.random.normal(0, 0.05, X.shape)
# Add background noise
I_total += np.random.normal(0.1, 0.02, X.shape)

# Plot Panel A
# Inverted greyscale for "optical" look
ax1.imshow(I_total, extent=(-8, x_extent, -y_extent/2, y_extent/2), 
           origin='lower', cmap='Greys', vmin=0, vmax=6, aspect='equal')

# Annotations for Panel A
ax1.text(0, 4.0, 'Host Galaxy', ha='center', fontsize=10, fontweight='bold', color=COLORS['text_neutral'])
ax1.text(0, 2.8, '(z=0.96)', ha='center', fontsize=9, color=COLORS['text_neutral'])

ax1.text(31, 2.0, 'Linear Star-Forming Wake (62 kpc)', ha='center', fontsize=10, color=COLORS['text_neutral'], style='italic')

ax1.text(62, 4.0, 'RBH-1', ha='center', fontsize=10, fontweight='bold', color=COLORS['text_neutral'])
ax1.text(62, 2.8, '(Candidate)', ha='center', fontsize=9, color=COLORS['text_neutral'])

# Scale bar
bar_len = 10
ax1.plot([5, 5+bar_len], [-3.0, -3.0], color='black', linewidth=2.5)
ax1.text(5 + bar_len/2, -4.2, '10 kpc', ha='center', fontsize=9)

ax1.set_xlim(-8, 68)
ax1.set_ylim(-4.5, 5.5)
ax1.set_xlabel('Distance from Galaxy [kpc]')
ax1.set_ylabel('Transverse [kpc]')
ax1.set_title(r"$\bf{a)}$ Large Scale Structure (62 kpc Extent)", loc='left')
ax1.grid(False)
# Anchor to West (Left) to ensure alignment with bottom panel
ax1.set_anchor('W')

# Panel B: Zoom on RBH-1 (Schematic of Observation)
ax2 = fig.add_subplot(gs[1, 0])

# Zoom in on the tip region (x: 58-66, y: -4-4)
zoom_range_x = [59, 65]
zoom_range_y = [-3, 3]
zoom_x = np.linspace(zoom_range_x[0], zoom_range_x[1], 300)
zoom_y = np.linspace(zoom_range_y[0], zoom_range_y[1], 300)
XZ, YZ = np.meshgrid(zoom_x, zoom_y)

# Recalculate Intensity for Zoom (Higher res calculation)
# Bow shock shape
parabola = (XZ - 62) + 0.6 * YZ**2
shock_mask_z = (parabola < 0.2) & (parabola > -0.4)
I_shock_z = 6.0 * np.exp(-(parabola)**2 / 0.1) * shock_mask_z * np.exp(-np.abs(YZ)/1.2)

# Point source / Compact object
R_core = np.sqrt((XZ - 62)**2 + YZ**2)
I_point = 4.0 * np.exp(-R_core / 0.4)

I_zoom = I_shock_z + I_point + np.random.normal(0.2, 0.05, XZ.shape)

ax2.imshow(I_zoom, extent=(zoom_range_x[0], zoom_range_x[1], zoom_range_y[0], zoom_range_y[1]), 
           origin='lower', cmap='Greys', vmin=0, vmax=6, aspect='equal')

# Overlay contours to look like "data"
# Use thematic color for contours
ax2.contour(XZ, YZ, I_zoom, levels=[2, 4], colors=c_obs, linewidths=1.0, alpha=0.8)

ax2.set_xlabel('Distance [kpc]')
ax2.set_ylabel('Transverse [kpc]')
ax2.set_title(r"$\bf{b)}$ Zoom: Interaction Region", loc='left')
# Anchor to West (Left)
ax2.set_anchor('W')

# Annotations
ax2.annotate('Bow Shock', xy=(61.8, 1.2), xytext=(63.5, 2.2),
             arrowprops=dict(arrowstyle='->', color=COLORS['text_hot'], lw=1.5), 
             color=COLORS['text_hot'], fontsize=10, fontweight='bold')
ax2.annotate('Velocity Jump\n(Spectroscopic)', xy=(62, 0), xytext=(60.0, -2.5),
             arrowprops=dict(arrowstyle='->', color=COLORS['text_neutral'], lw=1.5), 
             color=COLORS['text_neutral'], fontsize=9, ha='center')

# Panel C: Velocity Slice Schematic
ax3 = fig.add_subplot(gs[1, 1])

# Schematic velocity profile
d_vals = np.linspace(-2, 4, 200) # Distance relative to shock
v_vals = np.zeros_like(d_vals)

v_shock = 650 # km/s (observed jump)

# Sigmoid profile for shock
k = 5 # steepness
v_profile = v_shock / (1 + np.exp(-k * d_vals)) 

ax3.plot(d_vals, v_profile, color=COLORS['observation'], linewidth=3)
# Error band
ax3.fill_between(d_vals, v_profile - 50, v_profile + 50, color=COLORS['observation'], alpha=0.2)

# Vertical line for shock position
ax3.axvline(0, color='black', linestyle='--', alpha=0.5, lw=1.5)
ax3.text(0.15, 600, 'Shock Front', rotation=90, fontsize=9, color='#444', va='top')

ax3.set_xlabel('Distance from Front [kpc]')
ax3.set_ylabel(r'Velocity Offset [km/s]')
ax3.set_title(r"$\bf{c)}$ Kinematic Profile", loc='left')
ax3.set_ylim(-100, 800)
ax3.set_xlim(-2, 4)
ax3.grid(True, alpha=0.3)

# Add label for "Cold Gas" vs "Discontinuity"
props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none')
ax3.text(-1, 50, 'Ambient CGM\n(Rest Frame)', ha='center', fontsize=9, color=COLORS['text_neutral'], bbox=props)
ax3.text(2.5, 700, 'Shocked Gas\n(~650 km/s)', ha='center', fontsize=9, color=COLORS['text_neutral'], bbox=props)

# Align y-labels for the left column
# Manual alignment for precision with different panel widths
# ax1 width ~ 9.0", ax2 width ~ 3.0"
# Target offset ~ 0.65"
ax1.yaxis.set_label_coords(-0.07, 0.5)
ax2.yaxis.set_label_coords(-0.21, 0.5)

# Save
save_fig(fig, 'figure_01_observation.png')

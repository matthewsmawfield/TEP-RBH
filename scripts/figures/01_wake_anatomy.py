import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os
import sys
from matplotlib.patches import FancyArrowPatch

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.style import set_pub_style, COLORS, FIG_SIZE, save_fig

set_pub_style()

# Ensure output directory exists
output_dir = os.path.join(os.path.dirname(__file__), '../../site/figures')
os.makedirs(output_dir, exist_ok=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FIG_SIZE['double_column'], constrained_layout=True)

# Colors
c_hot = COLORS['hot']
c_cold = COLORS['cold']
c_bh = COLORS['bh']
c_gas = COLORS['gas']

# --- Left: Standard Hydrodynamic Model (Hot) ---
ax1.set_title(r"$\bf{a)}$ Standard Hydrodynamic Model (Thermal)", loc='left', fontsize=11)
ax1.set_xlim(0, 10)
ax1.set_ylim(-3, 3)
ax1.axis('off')

# Background gas
ax1.axhspan(-3, 3, color=COLORS['background'], zorder=0)

# Bow Shock (Parabolic)
y_shock = np.linspace(-2.5, 2.5, 100)
x_shock = 1.0 + 0.5 * y_shock**2
ax1.plot(x_shock, y_shock, color=c_hot, lw=2, linestyle='-')

# Turbulent Wake (Randomized Streamlines behind shock)
np.random.seed(42)
for _ in range(30):
    y_start = np.random.uniform(-2, 2)
    x_start = 1.0 + 0.5 * y_start**2
    x_end = 10
    x_vals = np.linspace(x_start, x_end, 50)
    # Add turbulence
    y_vals = np.linspace(y_start, y_start * 1.5, 50) + np.random.normal(0, 0.1, 50) * (x_vals - x_start)
    ax1.plot(x_vals, y_vals, color=c_hot, alpha=0.3, lw=0.8)

# Black Hole
circle1 = plt.Circle((1.5, 0), 0.3, color=c_bh, zorder=10)
ax1.add_patch(circle1)

# Annotations
ax1.text(6, 0, r"$T \sim 10^7$ K" "\n(X-ray Emitting)", ha='center', va='center', color=COLORS['text_hot'], fontsize=9)
ax1.annotate('Bow Shock', xy=(1.5, 1.5), xytext=(3, 2.5),
             arrowprops=dict(arrowstyle='->', color='black', lw=0.8))

# --- Right: Soliton Model (Cold) ---
ax2.set_title(r"$\bf{b)}$ Temporal Soliton Model (Metric)", loc='left', fontsize=11)
ax2.set_xlim(0, 10)
ax2.set_ylim(-3, 3)
ax2.axis('off')

# Background gas
ax2.axhspan(-3, 3, color=COLORS['background'], zorder=0)

# Soliton Halo (Transparent Sphere)
halo = plt.Circle((1.5, 0), 1.2, color=c_cold, alpha=0.2, zorder=5)
ax2.add_patch(halo)
# Hard Core
core = plt.Circle((1.5, 0), 0.3, color=c_bh, zorder=10)
ax2.add_patch(core)

# Laminar Wake (Straight Streamlines)
y_lines = np.linspace(-1.0, 1.0, 7)
for y in y_lines:
    ax2.plot([1.5, 10], [y, y], color=c_cold, alpha=0.6, lw=1.5)

# Star Formation (Clumps in the wake)
for i in range(12):
    x_star = np.random.uniform(3, 9)
    y_star = np.random.uniform(-0.8, 0.8)
    ax2.scatter(x_star, y_star, marker='*', s=60, color=COLORS['star'], edgecolors='k', lw=0.3, zorder=15)

# Annotations
ax2.text(6, 1.5, "Laminar Flow\n(No Heating)", ha='center', color=COLORS['text_cold'], fontsize=9)
ax2.text(6, -1.8, "Immediate Star Formation\n(Jeans Collapse)", ha='center', color=COLORS['star'], fontsize=9)

ax2.annotate('Soliton Field', xy=(1.5, 1.2), xytext=(3, 2.5),
             arrowprops=dict(arrowstyle='->', color='black', lw=0.8))

# Save
save_fig(fig, 'figure_03_wake_anatomy.png')

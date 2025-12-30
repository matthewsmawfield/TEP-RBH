import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.style import set_pub_style, FIG_SIZE, save_fig

set_pub_style()

# Ensure output directory exists
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, '../site/figures')
os.makedirs(output_dir, exist_ok=True)

# Generate grid
N = 400
x = np.linspace(-2.5, 2.5, N)
y = np.linspace(-2.5, 2.5, N)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2)
Phi = np.arctan2(Y, X)

# --- Model 1: Standard Black Hole ---
# Photon ring at R=1
width = 0.2
I_BH = np.exp(-(R - 1.0)**2 / (2 * width**2))
# Hard shadow
mask_shadow = R < 0.6
I_BH[mask_shadow] = 0.0

# Polarization field (Spiral/Azimuthal)
Psi_BH = Phi + np.pi/2 # Azimuthal
U_BH = np.cos(Psi_BH)
V_BH = np.sin(Psi_BH)
# Mask polarization in shadow
U_BH[mask_shadow] = 0
V_BH[mask_shadow] = 0

# --- Model 2: Gravitational Soliton ---
# Photon ring at R=1 (similar to BH)
I_Sol = np.exp(-(R - 1.0)**2 / (2 * width**2))
# Luminous core (translucent) - Exponential core
I_Sol += 0.4 * np.exp(-R**2 / (2 * 0.5**2))

# Polarization field (Penetrating)
# Outside: Azimuthal
# Inside: Coherent vertical field passing through
mask_inner = R < 0.7
U_Sol = U_BH.copy()
V_Sol = V_BH.copy()

# Create a smooth transition for the vector field
# Inner field is vertical (polarized flux through center) representing field lines threading the soliton
U_inner = np.zeros_like(U_Sol)
V_inner = np.ones_like(V_Sol)

# Blend based on radius
# Sigmoid transition
transition = 1 / (1 + np.exp((R - 0.8) * 10))
U_Sol = (1 - transition) * U_BH + transition * U_inner
V_Sol = (1 - transition) * V_BH + transition * V_inner

# Normalize vectors for quiver
Norm_Sol = np.sqrt(U_Sol**2 + V_Sol**2)
mask_norm = Norm_Sol > 0
U_Sol[mask_norm] /= Norm_Sol[mask_norm]
V_Sol[mask_norm] /= Norm_Sol[mask_norm]

# Plotting
fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE['double_column'], constrained_layout=True)

# Subplot 1: Black Hole
ax1 = axes[0]
# Use 'magma' or 'inferno' for purple/dark theme consistency
cmap = 'gray'
im1 = ax1.imshow(I_BH, extent=(-2.5, 2.5, -2.5, 2.5), origin='lower', vmin=0, vmax=1.2, cmap=cmap)

# Quiver
step = 20
# Only plot vectors where intensity is significant or on the ring
mask_quiver_bh = (R[::step, ::step] > 0.6) & (R[::step, ::step] < 1.8)
Xq, Yq = X[::step, ::step], Y[::step, ::step]
Uq_BH, Vq_BH = U_BH[::step, ::step], V_BH[::step, ::step]

ax1.quiver(Xq[mask_quiver_bh], Yq[mask_quiver_bh], Uq_BH[mask_quiver_bh], Vq_BH[mask_quiver_bh], 
           color='white', alpha=0.8, scale=25, headaxislength=0, headlength=0, pivot='mid', width=0.005)

ax1.set_title(r"$\bf{a)}$ Standard Black Hole (Event Horizon)", loc='left', color='black')
ax1.text(0, 0, "No Polarized Flux", color='white', ha='center', va='center', fontsize=10, fontweight='bold', alpha=0.8)
ax1.set_xlabel(r"x ($R_s$)")
ax1.set_ylabel(r"y ($R_s$)")

# Subplot 2: Soliton
ax2 = axes[1]
im2 = ax2.imshow(I_Sol, extent=(-2.5, 2.5, -2.5, 2.5), origin='lower', vmin=0, vmax=1.2, cmap=cmap)

# Quiver for Soliton
# Plot vectors everywhere
mask_quiver_sol = (R[::step, ::step] < 1.8)
Uq_Sol, Vq_Sol = U_Sol[::step, ::step], V_Sol[::step, ::step]

ax2.quiver(Xq[mask_quiver_sol], Yq[mask_quiver_sol], Uq_Sol[mask_quiver_sol], Vq_Sol[mask_quiver_sol], 
           color='white', alpha=0.8, scale=25, headaxislength=0, headlength=0, pivot='mid', width=0.005)

ax2.set_title(r"$\bf{b)}$ Gravitational Soliton (Translucent)", loc='left', color='black')
ax2.text(0, 0, "Polarized Core", color='white', ha='center', va='center', fontsize=10, fontweight='bold', alpha=0.9)
ax2.set_xlabel(r"x ($R_s$)")
ax2.set_yticks([])

# Save
save_fig(fig, 'figure_A1_polarization.png')

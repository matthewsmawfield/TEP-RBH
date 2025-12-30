#!/usr/bin/env python3
"""
Universal Scaling Law (Figure 10)

Plots the mass-radius scaling law for solitons:
R_s = L_c * (M / M_Earth)^(1/3)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.style import set_pub_style, COLORS, FIG_SIZE, save_fig

set_pub_style()

# Constants
M_sun = 1.989e30 # kg
M_earth = 5.972e24 # kg
L_c = 4200 # km (Earth calibration)
R_S_sun = 3.0 # km

# Mass range
M_vals_Msun = np.logspace(-6, 12, 100)
M_vals_kg = M_vals_Msun * M_sun
M_vals_Mearth = M_vals_kg / M_earth

# Scaling Law
R_sol_km = L_c * (M_vals_Mearth)**(1/3)

# Schwarzschild Radius
R_sch_km = 2.95 * M_vals_Msun # 2GM/c^2 ~ 3 km per solar mass

# Plotting
fig, ax = plt.subplots(figsize=FIG_SIZE['double_column'], constrained_layout=True)

# Theme colors
c_soliton = COLORS['model_metric']
c_bh = COLORS['bh']
c_obs = COLORS['observation']

ax.loglog(M_vals_Msun, R_sol_km, color=c_soliton, linewidth=3, label=r'Soliton Radius ($R \propto M^{1/3}$)')
ax.loglog(M_vals_Msun, R_sch_km, color=c_bh, linewidth=2, linestyle='--', label=r'Schwarzschild Radius ($R_S \propto M$)')

# Points of interest
# 1. Earth
ax.plot(M_earth/M_sun, L_c, 'o', color=c_obs, markersize=8)
ax.annotate('Earth\n(GNSS Clocks)', xy=(M_earth/M_sun, L_c), xytext=(1e-4, 1e4),
            arrowprops=dict(arrowstyle='->', color='black'), fontsize=9)

# 2. RBH-1
M_rbh1 = 2.0e7 # M_sun
R_rbh1 = L_c * (M_rbh1 * M_sun / M_earth)**(1/3)
ax.plot(M_rbh1, R_rbh1, '*', color=c_obs, markersize=15, markeredgecolor='black')
ax.annotate('RBH-1\n(Crossover Point)', xy=(M_rbh1, R_rbh1), xytext=(1e4, 1e9),
            arrowprops=dict(arrowstyle='->', color='black'), fontsize=9, fontweight='bold')

# 3. Magnetar (SGR 1935+2154)
M_mag = 1.4
R_mag = L_c * (M_mag * M_sun / M_earth)**(1/3) # ~ 5e5 km ~ light cylinder
ax.plot(M_mag, R_mag, 's', color=COLORS['shock'], markersize=8)
ax.annotate('Magnetars\n(FRB Source)', xy=(M_mag, R_mag), xytext=(1e-2, 1e7),
            arrowprops=dict(arrowstyle='->', color='black'), fontsize=9)

# 4. Proton
M_proton = 1.67e-27 / M_sun # Solar masses
R_proton = L_c * (M_proton * M_sun / M_earth)**(1/3) # ~ 10^-11 km ~ Bohr radius
# ax.plot(M_proton, R_proton, 'd', color='green', markersize=8)

# Shaded regions
# Black Hole Dominated
ax.fill_between(M_vals_Msun, R_sch_km, 1e-10, where=(R_sch_km > R_sol_km), color='gray', alpha=0.3)
ax.text(1e10, 1e5, 'Black Hole\nDominated', color='black', ha='center', fontsize=12)

# Soliton Dominated
ax.fill_between(M_vals_Msun, R_sch_km, 1e-10, where=(R_sch_km < R_sol_km), color=c_soliton, alpha=0.1)
ax.text(1e-3, 1e2, 'Soliton\nDominated', color=c_soliton, ha='center', fontsize=12)

ax.set_xlabel(r'Mass $M$ [$M_{\odot}$]')
ax.set_ylabel(r'Radius $R$ [km]')
ax.set_title('Universal Scaling Law', loc='left')
ax.set_xlim(1e-6, 1e11)
ax.set_ylim(1e0, 1e12)
ax.grid(True, alpha=0.3, which='both')
ax.legend(loc='upper left', fontsize=10)

# Save
save_fig(fig, 'figure_10_scaling.png')

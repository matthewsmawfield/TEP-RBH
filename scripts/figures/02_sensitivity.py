#!/usr/bin/env python3
"""
Cooling Sensitivity Analysis (Figure 2)

Calculates the ratio of cooling time to dynamical time as a function of gas density.
Demonstrates the "Cooling Bottleneck".

t_cool = E / (n^2 Lambda)
t_dyn = w / c_s
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
k_B = 1.38e-16
m_p = 1.67e-24
mu = 0.6
Myr = 3.156e13
kpc = 3.086e21

# Parameters
T_shock = 1.4e7  # K
v_shock = 1000e5 # cm/s
w_wake = 0.7 * kpc # cm (Wake Radius, used for t_dyn = R/c_s)

# Cooling function (approximate for T ~ 10^7 K)
# Bremsstrahlung dominated
def get_cooling_rate(T):
    return 2.5e-23 # erg cm^3 s^-1 (Solar metallicity)

Lambda = get_cooling_rate(T_shock)

# Sound speed
c_s = np.sqrt(5/3 * k_B * T_shock / (mu * m_p))
t_dyn = w_wake / c_s # seconds

# Density range (log scale)
n_vals = np.logspace(-4, 1, 100) # cm^-3

# Calculate cooling time
# E = 1.5 n k T
# L = n^2 Lambda
# t_cool = E/L = 1.5 k T / (n Lambda)
t_cool_vals = (1.5 * k_B * T_shock) / (n_vals * Lambda) # seconds

# Ratio
ratio = t_cool_vals / t_dyn

# Plotting
fig, ax = plt.subplots(figsize=FIG_SIZE['double_column'], constrained_layout=True)

# Theme colors
c_thermal = COLORS['model_thermal']
c_metric = COLORS['model_metric']
c_obs = COLORS['observation']

ax.loglog(n_vals, ratio, color=c_thermal, linewidth=2.5)

# Critical line
ax.axhline(y=1.0, color='black', linestyle='--', linewidth=1.5, label='Critical Threshold ($t_{cool} = t_{dyn}$)')

# Shaded regions
ax.fill_between(n_vals, 1.0, 10000, color=c_thermal, alpha=0.1)
ax.fill_between(n_vals, 0.001, 1.0, color=c_metric, alpha=0.1)

# Annotations
ax.text(0.1, 100, 'Cooling Bottleneck\n(Gas stays hot)', color=c_thermal, ha='center', fontsize=10, fontweight='bold')
ax.text(1e-1, 0.1, 'Rapid Cooling\n(Star Formation)', color=c_metric, ha='center', fontsize=10, fontweight='bold')

# Observed density marker
n_obs = 1e-3 # Typical CGM
ratio_obs = (1.5 * k_B * T_shock) / (n_obs * Lambda) / t_dyn
ax.plot(n_obs, ratio_obs, 'o', color=c_obs, markersize=8, label='Fiducial CGM')
ax.annotate(r'Fiducial CGM\n($n \sim 10^{-3}$)', xy=(n_obs, ratio_obs), xytext=(1.5e-4, 2000),
            arrowprops=dict(arrowstyle='->', color='black'), fontsize=9)

ax.set_xlabel(r'Gas Density $n$ [cm$^{-3}$]')
ax.set_ylabel(r'Ratio $t_{cool} / t_{dyn}$')
ax.set_title('Cooling Sensitivity Analysis', loc='left')
ax.set_xlim(1e-4, 10)
ax.set_ylim(0.01, 10000)
ax.grid(True, alpha=0.3)
ax.legend(loc='lower left', fontsize=8)

# Save
save_fig(fig, 'figure_02_sensitivity.png')

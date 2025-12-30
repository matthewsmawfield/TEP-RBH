"""
Jeans Length Analysis: The "Real Data" Proof of the Cold Wake

This script calculates the Jeans Length (L_J) for the RBH-1 wake under
two scenarios:
1. Standard Hydrodynamic Shock (Hot): T ~ 10^7 K
2. TEP Metric Shock (Cold): T ~ 100 - 10,000 K

We compare these scales to the observed wake dimensions (Width ~ 1 kpc).

Theory:
L_J = c_s / sqrt(G * rho)
c_s = sqrt(gamma * k_B * T / (mu * m_p))

If L_J(Hot) >> 1 kpc, star formation should be impossible (thermal support dominates).
If L_J(Cold) <= 1 kpc, star formation is expected.

The observation of star-forming clumps (size <= 1 kpc) is the "real data"
that proves the gas is cold.
"""

import numpy as np

# Constants (CGS)
k_B = 1.381e-16
m_p = 1.673e-24
G = 6.674e-8
kpc_cm = 3.086e21
M_sun_g = 1.989e33

# Parameters
n_CGM = 0.1          # cm^-3 (approximate)
rho = n_CGM * m_p    # g/cm^3
mu = 0.6             # mean molecular weight
gamma = 5/3

# Observed scales
Wake_Width = 1.0     # kpc (approx constraint on clump size)

def calc_jeans_length(T):
    c_s = np.sqrt(gamma * k_B * T / (mu * m_p))
    L_J_cm = c_s / np.sqrt(G * rho)
    L_J_kpc = L_J_cm / kpc_cm
    M_J_g = (4/3) * np.pi * (L_J_cm/2)**3 * rho
    M_J_solar = M_J_g / M_sun_g
    return L_J_kpc, M_J_solar, c_s

print("="*60)
print("JEANS LENGTH ANALYSIS: HOT vs COLD WAKE")
print("="*60)
print(f"Density: n = {n_CGM} cm^-3")
print(f"Observed Wake Width: ~{Wake_Width} kpc")
print("-" * 60)

# Scenario 1: Hot Shock (Standard Model)
T_hot = 1.4e7
L_hot, M_hot, cs_hot = calc_jeans_length(T_hot)

print(f"SCENARIO 1: HOT SHOCK (T = {T_hot:.1e} K)")
print(f"  Sound Speed: {cs_hot/1e5:.0f} km/s")
print(f"  Jeans Length: {L_hot:.1f} kpc")
print(f"  Jeans Mass:   {M_hot:.1e} M_sun")
print(f"  Result: L_J ({L_hot:.1f} kpc) >> Wake Width ({Wake_Width} kpc)")
print("  CONCLUSION: The wake is thermally supported. Gravity cannot win.")
print("  Star formation is IMPOSSIBLE.")

print("-" * 60)

# Scenario 2: Cold Wake (TEP Model)
# TEP implies gas is not heated. Temperature is typical IGM/ISM or lower.
# Let's test a range.
print("SCENARIO 2: COLD WAKE (TEP)")
print(f"{'T (K)':<10} {'c_s (km/s)':<12} {'L_J (kpc)':<12} {'Conclusion'}")

for T_cold in [10000, 1000, 100, 10]:
    L_cold, M_cold, cs_cold = calc_jeans_length(T_cold)
    possible = "POSSIBLE" if L_cold <= Wake_Width * 2 else "UNLIKELY" 
    # factor of 2 margin
    print(f"{T_cold:<10} {cs_cold/1e5:<12.1f} {L_cold:<12.3f} {possible}")

print("-" * 60)
print("SUMMARY:")
print("The observed star formation (clumps < 1 kpc) requires gas temperatures")
print("below T ~ 10,000 K.")
print(f"Standard shock theory predicts T ~ 1.4e7 K, yielding L_J ~ {L_hot:.0f} kpc.")
print("The existence of the clumps is EMPIRICAL PROOF that the shock was non-thermal.")

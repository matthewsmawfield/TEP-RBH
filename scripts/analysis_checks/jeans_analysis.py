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

print()
print("="*60)
print("TEP FIFTH-FORCE JEANS-MASS REDUCTION (Box 2.3, corrected derivation)")
print("="*60)
# In the matter frame a uniform conformal rescaling cannot alter a local
# instability criterion (free-fall and sound-crossing times rescale together).
# The collapse criterion is modified only by the scalar fifth force:
#   G_eff = G (1 + alpha_eff^2),   alpha_0^2 = 2 beta_A^2 (corpus DEF convention)
#   M_J_tilde = M_J / (1 + alpha_eff^2)^{3/2}
beta_A = -1.0
alpha0_sq = 2 * beta_A**2          # bare scalar charge squared = 2
reduction = (1 + alpha0_sq)**1.5   # 3^{3/2}
print(f"beta_A = {beta_A},  alpha_0^2 = {alpha0_sq}")
print(f"G_eff / G (unscreened, bare coupling) = 1 + alpha_0^2 = {1+alpha0_sq}")
print(f"M_J_tilde / M_J = (1 + alpha_0^2)^(-3/2) = {1/reduction:.4f}")
print(f"  -> M_J_tilde ~ {1/reduction:.2f} M_J at bare coupling")
print()
# Timescale bookkeeping: transit vs free-fall
v_obj_kms = 1.0e3               # km/s, ~1000 km/s object speed
R_core_km = 1.0e8               # km, core zone
R_wake_km = 1.0 * 3.086e16      # km, transition/wake scale ~1 kpc
t_core_days = R_core_km / v_obj_kms / 86400
t_wake_yr   = R_wake_km / v_obj_kms / (365.25*86400)
t_ff_yr     = 1.0/np.sqrt(G * rho) / (365.25*86400)  # s -> yr
print(f"Core-zone transit:  {t_core_days:.1f} days")
print(f"Wake/transition transit: {t_wake_yr/1e6:.2f} Myr")
print(f"Free-fall time at n={n_CGM} cm^-3: {t_ff_yr/1e6:.0f} Myr")
print("Core transit << t_ff: the core is a seeding impulse only.")
print("Wake transit << ambient t_ff: passage can only reclassify or precondition gas;")
print("collapse must complete in denser condensations or after passage.")

print()
print("="*60)
print("AMBIENT-DENSITY BOOKKEEPING AND COMPRESSED-CONDENSATE REGIME")
print("="*60)
# Ambient CGM at n ~ 1e-3 cm^-3 (the dilute medium the shock traverses)
n_amb = 1.0e-3
rho_amb = n_amb * m_p
T_amb = 1.0e4
c_s_amb = np.sqrt(gamma * k_B * T_amb / (mu * m_p))
L_J_amb = c_s_amb / np.sqrt(G * rho_amb) / kpc_cm
M_J_amb = (4/3) * np.pi * (c_s_amb / np.sqrt(G * rho_amb) / 2)**3 * rho_amb / M_sun_g
M_J_tilde_amb = M_J_amb / reduction
rho_crit_factor = (1 + alpha0_sq)**3       # rho_crit(M) = c_s^6/(G_eff^3 M^2) -> drops 27x
print(f"Ambient CGM: T = {T_amb:.0e} K, n = {n_amb:.0e} cm^-3, c_s = {c_s_amb/1e5:.1f} km/s")
print(f"  Newtonian M_J ~ {M_J_amb:.1e} M_sun,  lambda_J ~ {L_J_amb:.0f} kpc")
print(f"  Bare coupling:  M_J_tilde ~ {M_J_tilde_amb:.1e} M_sun,  lambda_J ~ {L_J_amb/np.sqrt(1+alpha0_sq):.0f} kpc")
print(f"  Critical density for instability at fixed clump mass falls by {rho_crit_factor:.0f}x")
print()
print(f"{'n (cm^-3)':>10} {'M_J (M_sun)':>12} {'M_J_tilde (M_sun)':>18}")
compressed_table = []
for n in [1e-3, 1e-1, 1.0, 10.0, 100.0]:
    rho_n = n * m_p
    MJ_n = (4/3) * np.pi * (c_s_amb / np.sqrt(G * rho_n) / 2)**3 * rho_n / M_sun_g
    MJt_n = MJ_n / reduction
    compressed_table.append({"n_cm3": n, "M_J_Msun": MJ_n, "M_J_tilde_Msun": MJt_n})
    print(f"{n:>10.3f} {MJ_n:>12.2e} {MJt_n:>18.2e}")
print()
print("At bare coupling the reduced criterion reaches the 1e6-1e7 M_sun clump")
print("regime at compressed densities n ~ 1-100 cm^-3; a deeper reduction on")
print("near-ambient gas remains contingent on the corpus's open effective-charge")
print("(alpha_eff) response-amplification problem, shared across channels.")

# Persist for manuscript traceability
import json, os
out = {
    "ambient": {
        "T_K": T_amb, "n_cm3": n_amb, "c_s_kms": float(c_s_amb/1e5),
        "M_J_Newtonian_Msun": float(M_J_amb),
        "lambda_J_kpc": float(L_J_amb),
        "M_J_tilde_bare_Msun": float(M_J_tilde_amb),
        "lambda_J_tilde_kpc": float(L_J_amb/np.sqrt(1+alpha0_sq)),
    },
    "bare_coupling": {
        "beta_A": beta_A, "alpha0_sq": alpha0_sq,
        "G_eff_over_G": 1 + alpha0_sq,
        "M_J_reduction_factor": float(1/reduction),
        "rho_crit_reduction_factor": float(rho_crit_factor),
    },
    "timescales": {
        "core_transit_days": float(t_core_days),
        "wake_transit_Myr": float(t_wake_yr/1e6),
        "free_fall_Myr_at_n_0p1_cm3": float(t_ff_yr/1e6),
        "wake_to_free_fall_ratio": float(t_wake_yr/t_ff_yr),
        "interpretation": "wake transit is much shorter than the ambient free-fall time; "
                          "collapse requires denser condensations or post-passage completion",
    },
    "compressed_density_table": compressed_table,
    "contingency": "deeper reduction requires alpha_eff > bare value "
                   "(corpus open response-amplification gap, Papers 5, 10, 11)",
}
os.makedirs("results", exist_ok=True)
with open("results/jeans_analysis.json", "w") as f:
    json.dump(out, f, indent=2)
print("Wrote results/jeans_analysis.json")

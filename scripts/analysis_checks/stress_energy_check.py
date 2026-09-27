#!/usr/bin/env python3
"""
Field stress-energy bookkeeping for the RBH-1 metric shock.

Evaluates whether the transport-consistent conformal gradient required by the
observed 650 km/s position--velocity span carries enough canonical
scalar stress-energy to undercut the "strong kinematics, weak lensing"
discriminator.

The two-metric bookkeeping:

  * Kinematics respond to the matter metric g_tilde: matter feels the
    conformal gradient directly, a = c^2 grad lnA, which a Newtonian
    fit reads as an apparent enclosed mass
        M_app = c^2 grad_lnA R^2 / G.

  * The gravity metric g is sourced by the scalar's actual stress
    tensor.  On the canonical kinetic branch (the corpus's derived
    weak-field baseline; candidate non-canonical K(X) completions are
    part of the open action-closure calculation) the gradient energy
    density is u = (1/2) M_Pl^2 (grad lnA)^2.  Integrating over a
    transition shell of radius R and width w,

        E_scalar = 2 pi M_Pl^2 (grad lnA)^2 R^2 w
                 = (Delta lnA / 4) * M_app ,

    since grad_lnA * w = Delta_lnA and 2 pi G M_Pl^2 = 1/4 in units
    where M_Pl is the reduced Planck mass.  The kinematic-to-gravitating
    mass ratio is therefore

        M_app / E_scalar = 4 / Delta_lnA ~ 1.7e6 ,

    independent of the profile width: the conformal coupling amplifies
    the matter response per unit field excursion without amplifying the
    field's own gravity.  The "phantom mass" inferred kinematically is
    a Newtonian-fit parameter, not the stress-energy content of the
    configuration.

  * What strong lensing requires is surface density at the critical
    value Sigma_crit = (c^2/4 pi G) D_s / (D_l D_ls).  The scalar energy
    is distributed through the transition volume; its projected density
    Sigma = u * w is compared against Sigma_crit at the lens redshift.
    At the transport-consistent rest-entry depth, the historical ~5e12 Msun
    "gradient energy" benchmark would require a ~5.8e-6 pc transition --
    about 1.7e8 times thinner than the observed ~1 kpc discontinuity width --
    and is not the stated profile.

Outputs results/stress_energy_check.json and prints a summary table.
"""

import json
import os

# --- constants ---------------------------------------------------------------
G = 6.67430e-11            # m^3 kg^-1 s^-2
C = 299792458.0            # m/s
HBARC_GEV_M = 1.97327e-16  # GeV m
GEV4_TO_J_M3 = 1.602e-10 / (1.97327e-16 ** 3)   # J/m^3 per GeV^4
M_PL_RED_GEV = 2.435e18    # reduced Planck mass (phi convention of core)
M_SUN = 1.98847e30         # kg
KPC_M = 3.086e19
PC_M = 3.086e16

# --- stated profile ----------------------------------------------------------
V_OBS_MS = 6.5e5
DLNA = 0.5 * (V_OBS_MS / C) ** 2  # rest-entry work-integral normalization
R_KPC = 1.0                # transition radius (kpc)

# --- lensing geometry (illustrative Planck15 distances, z_l=0.96, z_s~2) ------
D_L_GPC = 1.45             # angular-diameter distance to RBH-1 (approx)
D_S_GPC = 1.70             # angular-diameter distance to a fiducial background source
D_LS_GPC = 0.95            # lens-source angular-diameter distance
SIGMA_CRIT = (C ** 2 / (4.0 * 3.14159265 * G)) \
    * (D_S_GPC / (D_L_GPC * D_LS_GPC)) / 3.086e25          # kg/m^2 (per Gpc)
SIGMA_CRIT_MSUN_PC2 = SIGMA_CRIT / M_SUN * PC_M ** 2       # Msun/pc^2

WIDTHS_KPC = [0.05, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0]


def evaluate(w_kpc):
    w_m = w_kpc * KPC_M
    grad_m1 = DLNA / w_m                          # m^-1
    grad_gev = grad_m1 * HBARC_GEV_M              # GeV
    u_gev4 = 0.5 * (M_PL_RED_GEV * grad_gev) ** 2
    u_jm3 = u_gev4 * GEV4_TO_J_M3
    u_msun_kpc3 = (u_jm3 / C ** 2) * KPC_M ** 3 / M_SUN

    v_kpc3 = 4.0 * 3.14159265 * R_KPC ** 2 * w_kpc
    e_msun = u_msun_kpc3 * v_kpc3
    sigma_msun_pc2 = u_msun_kpc3 * w_kpc / 1.0e6  # kpc^2 -> pc^2

    # apparent kinematic mass at the transition radius
    a_si = C ** 2 * grad_m1
    m_app = a_si * (R_KPC * KPC_M) ** 2 / G / M_SUN

    return {
        "w_kpc": w_kpc,
        "grad_lnA_m^-1": grad_m1,
        "u_msun_per_kpc3": u_msun_kpc3,
        "E_shell_msun": e_msun,
        "Sigma_msun_per_pc2": sigma_msun_pc2,
        "Sigma_over_Sigma_crit": sigma_msun_pc2 / SIGMA_CRIT_MSUN_PC2,
        "M_apparent_msun": m_app,
        "kinematic_to_gravitating_ratio": m_app / e_msun,
    }


def main():
    rows = [evaluate(w) for w in WIDTHS_KPC]

    # derived closed-form ratio 4 / Delta ln A
    ratio_closed = 4.0 / DLNA

    # shell width that would reproduce the often-quoted ~5e12 Msun
    # E = 2 pi M_Pl^2 (DLNA/w)^2 R^2 w  =>  w = 2 pi M_Pl^2 DLNA^2 R^2 / E
    m_pl_gev2 = M_PL_RED_GEV ** 2
    r_gev = R_KPC * KPC_M / HBARC_GEV_M            # GeV^-1
    e_target_gev = 5.0e12 * 1.116e57               # Msun -> GeV (1 Msun = 1.116e57 GeV)
    w_shell_gev = 2.0 * 3.14159265 * m_pl_gev2 * DLNA ** 2 * r_gev ** 2 / e_target_gev
    w_shell_pc = w_shell_gev * HBARC_GEV_M / PC_M

    # amplitude bookkeeping (Box 2.2 / Box 3.1): the effective coupling and
    # Newtonian-equivalent mass implied when the metric shift is read as a
    # linear response to the baryonic potential
    m_bary_msun = 2.0e7
    v_obs_ms = V_OBS_MS
    phi_n_over_c2 = G * m_bary_msun * M_SUN / (R_KPC * KPC_M * C ** 2)
    depth_req = DLNA
    alpha_eff = depth_req / phi_n_over_c2
    m_eff_equiv = depth_req * R_KPC * KPC_M * C ** 2 / G / M_SUN

    out = {
        "profile": {
            "delta_lnA": DLNA,
            "normalization": "rest-entry fiducial; multiply depth by flow-frame factor eta",
            "R_transition_kpc": R_KPC,
            "scalings_with_eta": {
                "gradient_acceleration_and_apparent_mass": "proportional to eta",
                "canonical_scalar_shell_mass_and_surface_density": "proportional to eta^2",
                "kinematic_to_scalar_mass_ratio": "proportional to eta^-1",
            },
        },
        "sigma_crit_msun_pc2": SIGMA_CRIT_MSUN_PC2,
        "rows": rows,
        "amplitude_bookkeeping": {
            "M_bary_msun": m_bary_msun,
            "v_obs_km_s": v_obs_ms / 1.0e3,
            "Phi_N_over_c2": phi_n_over_c2,
            "dynamical_depth_required": depth_req,
            "alpha_RBH_eff_linear_response": alpha_eff,
            "M_eff_newtonian_equiv_msun": m_eff_equiv,
            "note": ("Delta(v^2/2) = c^2 alpha_eff GM/(R c^2) at "
                     "the rest-entry |Delta ln A|=2.35e-6 and "
                     "Phi_N/c^2~9.6e-10 implies "
                     "alpha_eff~2.46e3, i.e. a Newtonian-equivalent enclosed "
                     "mass ~4.9e10 Msun. Under "
                     "the soliton reading this is the field configuration's "
                     "internal depth, not a response coefficient; read "
                     "linearly it is an open ~1e3 response-"
                     "normalization channel."),
        },
        "decoupling": {
            "closed_form": "M_apparent / E_scalar = 4 / Delta_lnA",
            "value": ratio_closed,
            "note": ("independent of transition width; the conformal "
                     "coupling amplifies the matter response per unit "
                     "field excursion without amplifying the field's own "
                     "gravity"),
        },
        "thin_shell_benchmark": {
            "E_claim_msun": 5.0e12,
            "implied_width_pc": w_shell_pc,
            "note": ("historical 5e12 Msun comparison retained only as a "
                     "scale diagnostic; it is incompatible with the "
                     "transport-consistent dynamical depth"),
        },
        "interpretation": (
            "At the observed ~1 kpc transition width and rest-entry "
            "normalization the canonical scalar "
            "stress-energy is ~2.9e4 Msun distributed through the "
            "transition volume, ~1.7e6x below the apparent kinematic mass. "
            "The lensing contribution is negligible -- it cannot form the "
            "compact arcsecond-scale arc a particulate ~4.9e10 Msun halo "
            "would produce. 'Strong kinematics, weak lensing' is thereby a "
            "derived quantitative asymmetry (kinematic:lensing ~ 4/Delta_lnA "
            "~ 1.7e6 : 1), not an assumption; any particulate model gives "
            "ratio 1. Evaluation is on the canonical kinetic branch -- the "
            "corpus's derived weak-field baseline; candidate non-canonical "
            "K(X) completions modify the stress-energy bookkeeping and are "
            "part of the open action-closure calculation."
        ),
    }

    os.makedirs("results", exist_ok=True)
    path = os.path.join("results", "stress_energy_check.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)

    print("=" * 78)
    print("RBH-1 FIELD STRESS-ENERGY BOOKKEEPING (canonical branch)")
    print("=" * 78)
    print(f"Delta lnA = {DLNA}, R_trans = {R_KPC} kpc")
    print(f"Sigma_crit ~ {SIGMA_CRIT_MSUN_PC2:.3e} Msun/pc^2 "
          f"(z_l=0.96, z_s~2 illustrative)")
    hdr = f"{'w[kpc]':>8} {'u[Msun/kpc3]':>14} {'E[Msun]':>12} " \
          f"{'Sig[Msun/pc2]':>14} {'Sig/SigC':>9} {'M_app[Msun]':>13} {'M_app/E':>9}"
    print(hdr)
    for r in rows:
        print(f"{r['w_kpc']:8.2f} {r['u_msun_per_kpc3']:14.3e} "
              f"{r['E_shell_msun']:12.3e} {r['Sigma_msun_per_pc2']:14.3e} "
              f"{r['Sigma_over_Sigma_crit']:9.2f} "
              f"{r['M_apparent_msun']:13.3e} "
              f"{r['kinematic_to_gravitating_ratio']:9.2e}")
    print(f"closed-form decoupling ratio 4/Delta_lnA = {ratio_closed:.3e}")
    print(f"amplitude bookkeeping: Phi_N/c^2 = {phi_n_over_c2:.2e}, "
          f"dynamical depth = {depth_req:.2e}")
    print(f"  alpha_RBH,eff (linear response) = {alpha_eff:.2e}")
    print(f"  M_eff (Newtonian equiv) = {m_eff_equiv:.2e} Msun")
    print(f"historical 5e12 Msun benchmark would imply w = {w_shell_pc:.3e} pc "
          "at the transport-consistent depth")
    print(f"saved: {path}")


if __name__ == "__main__":
    main()

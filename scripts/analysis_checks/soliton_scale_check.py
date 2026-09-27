#!/usr/bin/env python3
"""
Soliton-scale bookkeeping for the RBH-1 consistency check.

The manuscript's central geometric check is

    R_T = (3 M / 4 pi rho_T)^(1/3) ~ 7.8e7 km ~ 1.3 R_S

for M ~ 2e7 Msun at rho_T ~ 20 g/cm^3.  Three bookkeeping items are
evaluated here on the corpus's measured calibration ensemble rather
than the single nominal anchor:

  1. Product-level rho_T ensemble.  rho_T is not an independent
     parameter; it is the terrestrial GNSS decoherence scale mapped
     through rho_T = 3 M_E / (4 pi lambda_T^3).  Each analysis
     product returns a different lambda_T (Paper 1 pooled values by
     analysis center, the Paper 14 multi-GNSS product, Paper 33, and
     the held-out MGEX value of issue 6-7).  The ensemble is
     propagated through R_T/R_S and through the crossover mass
     M_x(rho_T) defined by R_T = R_S -- the mass at which the
     constant-density radius meets the horizon radius, and the
     paper's stated object-specific falsification boundary.

  2. Resolution bookkeeping.  R_T is compared against the resolved
     scale at z = 0.96 (~1 kpc per 0.1 arcsec) to quantify that the
     R_T ~ R_S comparison is a theory-internal scale coincidence at
     the crossover mass, not a match to a resolved feature.  The
     observed kinematic onset lives at R_trans ~ 0.1-1 kpc.

  3. Transition-radius parametrization.  Writing R_trans = xi * R_T,
     the observed ~1 kpc onset requires xi ~ 4e8.  Under the
     constant-density screening ansatz of Paper 6 (shear recovery
     where the enclosed mean density falls to rho_T), the phantom
     halo of Newtonian-equivalent mass M_eff ~ 4.9e10 Msun would
     transition at xi_rho = (M_eff/M)^(1/3) ~ 13.5 (~7 AU); the
     measured onset is therefore ~3e7 times the naive recovery
     radius, quantifying the shear-recovery transfer function the
     soliton profile must supply.  Equivalently, a recovery length
     ell ~ R_trans corresponds to an effective field mass
     m_eff c^2 = hbar c / ell ~ 6.4e-27 eV.

Outputs results/soliton_scale_check.json and prints a summary.
"""

import json
import os

# --- constants ---------------------------------------------------------------
G = 6.67430e-11          # m^3 kg^-1 s^-2
C = 299792458.0          # m/s
M_SUN = 1.98847e30       # kg
M_EARTH = 5.972e24       # kg
KPC_M = 3.086e19         # m
KM_M = 1.0e3
HBAR_C_EV_M = 1.97327e-7 # eV m

# --- measured inputs ---------------------------------------------------------
# lambda_T values (km): corpus GNSS decoherence lengths per analysis product.
# Paper 1 pooled coherent-band values (step_3_6_multiband_*), Paper 14
# multi-GNSS product, Paper 33, and the held-out MGEX product (issue 6-7).
LAMBDA_PRODUCTS = {
    "CODE pooled (Paper 1)": 4549.0,
    "IGS pooled (Paper 1)": 3764.0,
    "ESA pooled (Paper 1)": 3328.0,
    "Paper 33": 4200.0,
    "Paper 14 multi-GNSS": 1862.0,
    "MGEX held-out (6-7)": 1396.0,
}

M_RBH_MSUN = 2.0e7       # RBH-1 baryonic mass, van Dokkum et al. 2025
M_EFF_MSUN = 4.9115944054e10  # step-01 rest-entry normalization; scales as eta
R_TRANS_OBS_KPC = (0.1, 1.0)   # observed discontinuity scale
RESOLVED_KPC = 1.0             # ~1 kpc per 0.1 arcsec at z = 0.96


def rho_T_from_lambda(lam_km):
    """Characteristic density from the GNSS decoherence length."""
    return 3.0 * M_EARTH / (4.0 * 3.14159265 * (lam_km * KM_M) ** 3)


def r_T(m_kg, rho):
    """Temporal-topology (constant-density) radius in metres."""
    return (3.0 * m_kg / (4.0 * 3.14159265 * rho)) ** (1.0 / 3.0)


def r_S(m_kg):
    return 2.0 * G * m_kg / C ** 2


def m_cross(rho):
    """Crossover mass: R_T = R_S -> M_x = c^3 sqrt(3 / (32 pi G^3 rho))."""
    return C ** 3 * (3.0 / (32.0 * 3.14159265 * G ** 3 * rho)) ** 0.5


def main():
    m = M_RBH_MSUN * M_SUN
    rs = r_S(m)

    products = []
    for name, lam in LAMBDA_PRODUCTS.items():
        rho = rho_T_from_lambda(lam)          # kg/m^3
        rt = r_T(m, rho)                      # m
        mx = m_cross(rho)                     # kg
        products.append({
            "product": name,
            "lambda_T_km": lam,
            "rho_T_g_cm3": rho / 1.0e3,
            "R_T_km": rt / KM_M,
            "R_T_over_R_S": rt / rs,
            "M_cross_msun": mx / M_SUN,
            "soliton_passes_RT_gt_RS": bool(rt > rs),
        })

    ratios = [p["R_T_over_R_S"] for p in products]
    rhos = [p["rho_T_g_cm3"] for p in products]

    # resolution bookkeeping
    rt_nominal = r_T(m, 2.0e4)                # rho_T = 20 g/cm^3
    resolution = {
        "R_T_kpc_nominal": rt_nominal / KPC_M,
        "resolved_scale_kpc": RESOLVED_KPC,
        "R_T_over_resolved": rt_nominal / KPC_M / RESOLVED_KPC,
        "orders_below_resolution": -__import__("math").log10(
            rt_nominal / KPC_M / RESOLVED_KPC),
    }

    # transition-radius parametrization  R_trans = xi * R_T
    xi_nominal = R_TRANS_OBS_KPC[1] * KPC_M / rt_nominal
    xi_range = [R_TRANS_OBS_KPC[0] * KPC_M / rt_nominal,
                R_TRANS_OBS_KPC[1] * KPC_M / rt_nominal]
    # constant-density recovery: transition where enclosed mean density of
    # the phantom halo falls to rho_T -> R_trans,rho = (3 M_eff/4 pi rho_T)^(1/3)
    r_trans_cd = r_T(M_EFF_MSUN * M_SUN, 2.0e4)
    xi_cd = r_trans_cd / rt_nominal
    transfer_ratio = xi_nominal / xi_cd
    m_eff_ev = HBAR_C_EV_M / (R_TRANS_OBS_KPC[1] * KPC_M)

    transition = {
        "parametrization": "R_trans = xi * R_T",
        "xi_required_1kpc": xi_nominal,
        "xi_range_0p1_1kpc": xi_range,
        "constant_density_recovery": {
            "R_trans_cd_pc": r_trans_cd / 3.086e16,
            "R_trans_cd_AU": r_trans_cd / 1.496e11,
            "xi_cd": xi_cd,
            "note": ("shear recovery where enclosed mean density of the "
                     "M_eff ~ 4.9e10 Msun dynamical-equivalent halo falls to rho_T"),
        },
        "observed_over_naive_recovery": transfer_ratio,
        "m_eff_recovery_eV": m_eff_ev,
    }

    out = {
        "inputs": {
            "M_RBH_msun": M_RBH_MSUN,
            "R_S_km": rs / KM_M,
            "lambda_products_km": LAMBDA_PRODUCTS,
        },
        "product_ensemble": products,
        "ensemble_summary": {
            "rho_T_range_g_cm3": [min(rhos), max(rhos)],
            "R_T_over_R_S_range": [min(ratios), max(ratios)],
            "M_cross_range_msun": [
                min(p["M_cross_msun"] for p in products),
                max(p["M_cross_msun"] for p in products)],
            "straddles_falsification_boundary": bool(
                min(ratios) < 1.0 < max(ratios)),
        },
        "resolution": resolution,
        "transition_parametrization": transition,
        "interpretation": (
            "R_T ~ 1.3 R_S is the crossover-mass coincidence: the constant-"
            "density radius meets the horizon at M_x(rho_T) ~ 3e7 Msun for "
            "rho_T = 20 g/cm^3, and RBH-1 (2e7 Msun) sits at that single "
            "crossover point. R_T ~ 2.5e-9 kpc lies ~8.6 orders below the "
            "~1 kpc resolved scale, so the check cannot match resolved "
            "morphology; the observable onset is R_trans. Propagating the "
            "product-level calibration ensemble (rho_T ~ 15-524 g/cm^3) "
            "returns R_T/R_S in [0.44, 1.45] and M_x in [5.8e6, 3.5e7] Msun "
            "-- the ensemble straddles the paper's own falsification "
            "boundary, so the object's candidacy sits inside the anchor's "
            "systematic uncertainty rather than passing cleanly. The "
            "transition parametrization R_trans = xi R_T requires "
            "xi ~ 4e8, ~3e6x the constant-density recovery radius; this "
            "quantifies the shear-recovery transfer function that the "
            "soliton profile must supply."
        ),
    }

    os.makedirs("results", exist_ok=True)
    path = os.path.join("results", "soliton_scale_check.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)

    print("=" * 78)
    print("RBH-1 SOLITON-SCALE BOOKKEEPING")
    print("=" * 78)
    print(f"M = {M_RBH_MSUN:.1e} Msun, R_S = {rs/KM_M:.3e} km")
    hdr = f"{'product':<26} {'lam[km]':>8} {'rho_T':>8} {'R_T[km]':>10} " \
          f"{'R_T/R_S':>8} {'M_x[Msun]':>10}"
    print(hdr)
    for p in products:
        print(f"{p['product']:<26} {p['lambda_T_km']:8.0f} "
              f"{p['rho_T_g_cm3']:8.1f} {p['R_T_km']:10.3e} "
              f"{p['R_T_over_R_S']:8.2f} {p['M_cross_msun']:10.3e}")
    print(f"R_T/R_S ensemble: [{min(ratios):.2f}, {max(ratios):.2f}] "
          f"(straddles 1.0: {min(ratios) < 1.0 < max(ratios)})")
    print(f"R_T = {resolution['R_T_kpc_nominal']:.2e} kpc, "
          f"{resolution['orders_below_resolution']:.1f} orders below "
          f"the ~{RESOLVED_KPC} kpc resolved scale")
    print(f"xi = R_trans/R_T: {xi_nominal:.2e} (1 kpc onset); "
          f"constant-density recovery xi_cd = {xi_cd:.1f} "
          f"({r_trans_cd/1.496e11:.0f} AU); "
          f"required transfer ratio = {transfer_ratio:.1e}")
    print(f"recovery-length field mass m_eff c^2 = {m_eff_ev:.2e} eV")
    print(f"saved: {path}")


if __name__ == "__main__":
    main()

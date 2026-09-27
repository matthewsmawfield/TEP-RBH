#!/usr/bin/env python3
"""Audit the RBH-1 conformal transport and dynamical-depth assignments.

The published RBH-1 observables used here are the position--velocity span
(-600 to +50 km/s across approximately 1 kpc) and the independently measured
near-tip [O III] dispersion (31 +/- 4 km/s).  No synthetic observations are
generated.  The calculation compares two distinct assignments:

1. Endpoint clock shift: |Delta ln A| = ln(1 + Delta v/c).
2. Coherent matter dynamics in the rest frame of a quasi-steady profile:
   Delta(u^2/2) = c^2 |Delta ln A|, following directly from
   a_phi = -c^2 grad ln A in the weak-field matter metric.  Here u is the
   gas speed relative to the profile.  A rest-entry normalization and a
   collinear benchmark using the published 954 km/s pattern speed are both
   reported, so an unmeasured flow-frame offset is not silently set to zero.

Only the second assignment is dynamically self-consistent for gas swept
through a propagating spatial profile.  Results are written to
results/step_01_transport_consistency.json.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


C = 299_792_458.0  # m s^-1
G = 6.67430e-11  # m^3 kg^-1 s^-2
M_SUN = 1.98847e30  # kg
KPC = 3.085677581491367e19  # m
YEAR = 365.25 * 86400.0  # s

# Published measurements / adopted values stated in the manuscript.
V_BLUE_KM_S = -600.0
V_RED_KM_S = 50.0
DELTA_V = (V_RED_KM_S - V_BLUE_KM_S) * 1.0e3
V_PATTERN = 954.0e3
SIGMA_V = 31.0e3
SIGMA_V_ERR = 4.0e3
L_TRANS = 1.0 * KPC
R_TRANS = 1.0 * KPC
M_BARY = 2.0e7 * M_SUN


def branch(depth: float) -> dict[str, float]:
    """Return matter-response and canonical scalar-ledger quantities."""
    gradient = depth / L_TRANS
    acceleration = C**2 * gradient
    apparent_mass = acceleration * R_TRANS**2 / G
    scalar_shell_mass = (depth / 4.0) * apparent_mass
    surface_density = scalar_shell_mass / (4.0 * math.pi * R_TRANS**2)
    return {
        "abs_delta_ln_A": depth,
        "gradient_abs_m_inv": gradient,
        "matter_acceleration_m_s2": acceleration,
        "newtonian_equivalent_mass_msun": apparent_mass / M_SUN,
        "canonical_scalar_shell_mass_msun": scalar_shell_mass / M_SUN,
        "canonical_surface_density_msun_pc2": (
            surface_density / M_SUN * (KPC / 1000.0) ** 2
        ),
        "kinematic_to_scalar_mass_ratio": apparent_mass / scalar_shell_mass,
    }


def main() -> None:
    endpoint_depth = math.log1p(DELTA_V / C)
    dynamical_depth = 0.5 * (DELTA_V / C) ** 2
    # Collinear translating-profile benchmark: ambient gas initially at rest
    # in the host frame has u_in = V_pattern; after gaining Delta_v in the
    # pattern direction it has u_out = V_pattern - Delta_v.
    u_in_pattern = V_PATTERN
    u_out_pattern = V_PATTERN - DELTA_V
    pattern_depth = 0.5 * (u_in_pattern**2 - u_out_pattern**2) / C**2

    endpoint = branch(endpoint_depth)
    endpoint["matter_speed_from_rest_km_s"] = (
        C * math.sqrt(2.0 * endpoint_depth) / 1.0e3
    )

    dynamical = branch(dynamical_depth)
    dynamical["matter_speed_from_rest_km_s"] = (
        C * math.sqrt(2.0 * dynamical_depth) / 1.0e3
    )
    dynamical["constant_acceleration_crossing_time_myr"] = (
        2.0 * L_TRANS / DELTA_V / (1.0e6 * YEAR)
    )

    pattern = branch(pattern_depth)
    pattern["host_frame_pattern_speed_km_s"] = V_PATTERN / 1.0e3
    pattern["profile_frame_entry_speed_km_s"] = u_in_pattern / 1.0e3
    pattern["profile_frame_exit_speed_km_s"] = u_out_pattern / 1.0e3
    pattern["flow_frame_factor_eta"] = pattern_depth / dynamical_depth

    phi_bary_over_c2 = G * M_BARY / (R_TRANS * C**2)
    endpoint["linear_response_over_baryonic_potential"] = (
        endpoint_depth / phi_bary_over_c2
    )
    dynamical["linear_response_over_baryonic_potential"] = (
        dynamical_depth / phi_bary_over_c2
    )
    pattern["linear_response_over_baryonic_potential"] = (
        pattern_depth / phi_bary_over_c2
    )

    result = {
        "provenance": {
            "source": "van Dokkum et al. 2026, ApJL, arXiv:2512.04166v2",
            "position_velocity_endpoints_km_s": [V_BLUE_KM_S, V_RED_KM_S],
            "position_velocity_span_km_s": DELTA_V / 1.0e3,
            "projected_span_kpc": L_TRANS / KPC,
            "near_tip_oiii_dispersion_km_s": SIGMA_V / 1.0e3,
            "near_tip_oiii_dispersion_error_km_s": SIGMA_V_ERR / 1.0e3,
            "co_spatiality_note": (
                "The resolved velocity span and the averaged near-tip [O III] "
                "dispersion are separate observables; the dispersion is not "
                "treated as an unresolved width of the full 650 km/s span."
            ),
        },
        "matter_metric_limit": {
            "equation": "a_phi = -c^2 grad(ln A)",
            "work_integral": "Delta(u^2/2) = -c^2 Delta(ln A) in the profile frame",
            "baryonic_potential_abs_over_c2": phi_bary_over_c2,
        },
        "endpoint_clock_assignment": endpoint,
        "coherent_dynamical_assignment": dynamical,
        "collinear_pattern_frame_benchmark": pattern,
        "comparison": {
            "endpoint_to_dynamical_depth_ratio": endpoint_depth / dynamical_depth,
            "endpoint_to_pattern_benchmark_depth_ratio": endpoint_depth / pattern_depth,
            "endpoint_speed_to_observed_span_ratio": (
                endpoint["matter_speed_from_rest_km_s"] / (DELTA_V / 1.0e3)
            ),
            "canonical_scalar_energy_reduction_factor": (
                endpoint["canonical_scalar_shell_mass_msun"]
                / dynamical["canonical_scalar_shell_mass_msun"]
            ),
            "canonical_scalar_energy_reduction_factor_pattern_benchmark": (
                endpoint["canonical_scalar_shell_mass_msun"]
                / pattern["canonical_scalar_shell_mass_msun"]
            ),
            "local_dispersion_to_span_ratio": SIGMA_V / DELTA_V,
            "conditional_rms_depth_nonuniformity_limit": 2.0 * SIGMA_V / DELTA_V,
            "conditional_rms_depth_nonuniformity_limit_1sigma_range": [
                2.0 * (SIGMA_V - SIGMA_V_ERR) / DELTA_V,
                2.0 * (SIGMA_V + SIGMA_V_ERR) / DELTA_V,
            ],
            "interpretation": (
                "The endpoint assignment is incompatible with universal matter "
                "coupling because the same profile accelerates traversing gas to "
                "approximately 2e4 km/s.  Assigning the measured span to coherent "
                "matter motion instead fixes |Delta ln A| by the work integral "
                "in the profile frame. The rest-entry normalization is 2.35e-6; "
                "a collinear benchmark using the published 954 km/s pattern "
                "speed is 4.55e-6. Both are hundreds of times shallower than "
                "the endpoint assignment. "
                "The line dispersion constrains profile non-uniformity only if "
                "measured on the same flow component."
            ),
        },
    }

    output = Path(__file__).resolve().parents[2] / "results" / "step_01_transport_consistency.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("RBH-1 transport consistency audit")
    print(f"  observed resolved span: {DELTA_V / 1e3:.1f} km/s over {L_TRANS / KPC:.1f} kpc")
    print(f"  endpoint depth:         {endpoint_depth:.6e}")
    print(f"  endpoint free-fall:     {endpoint['matter_speed_from_rest_km_s']:.1f} km/s")
    print(f"  dynamical depth:        {dynamical_depth:.6e}")
    print(f"  dynamical acceleration: {dynamical['matter_acceleration_m_s2']:.6e} m/s^2")
    print(f"  dynamical response:     {dynamical['linear_response_over_baryonic_potential']:.3e}")
    print(f"  954 km/s pattern depth: {pattern_depth:.6e} (collinear benchmark)")
    print(f"  near-tip sigma/span:    {SIGMA_V / DELTA_V:.4f}")
    print(f"  wrote {output}")


if __name__ == "__main__":
    main()

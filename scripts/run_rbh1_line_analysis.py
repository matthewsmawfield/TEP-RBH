"""
Run Line-Profile Decomposition on Real RBH-1 JWST Data

This script loads the extracted [O III] spectrum and runs the full
line-profile decomposition analysis.

Author: M. Smawfield
Date: December 2025
"""

import numpy as np
import sys

# Import the analysis function
from analyze_line_profiles import analyze_line_profile

if __name__ == '__main__':
    
    # Load extracted spectrum
    data_file = '../data/rbh1_oiii_extracted.dat'
    
    print("\n" + "="*80)
    print("RBH-1 LINE-PROFILE DECOMPOSITION: REAL JWST DATA")
    print("="*80)
    print(f"\nData: {data_file}")
    print("Source: JWST NIRSpec IFU (Program 3149, PI: van Dokkum)")
    
    # Load data
    data = np.loadtxt(data_file)
    velocity = data[:, 0]
    flux = data[:, 1]
    flux_err = data[:, 2]
    
    print(f"\nSpectrum properties:")
    print(f"  Points: {len(velocity)}")
    print(f"  Velocity range: {velocity.min():.1f} to {velocity.max():.1f} km/s")
    print(f"  Mean S/N: {np.mean(flux/flux_err):.1f}")
    
    # Expected thermal width for T ~ 10^7 K
    sigma_thermal = 90.0  # km/s for O III at 10^7 K
    
    # Run analysis
    results = analyze_line_profile(
        velocity, 
        flux, 
        flux_err,
        line_name='[O III] λ5007 (RBH-1 JWST)',
        sigma2_thermal=sigma_thermal,
        output_dir='../site/figures'
    )
    
    if results:
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print("\nKey Results:")
        print(f"  Single-component σ: {results['single_component']['params'][2]:.1f} ± {results['single_component']['params_err'][2]:.1f} km/s")
        print(f"  ΔBIC: {results['model_selection']['delta_bic']:.2f}")
        print(f"  Verdict: {results['model_selection']['verdict']}")
        
        # Save results summary
        with open('../site/figures/line_profile_results.txt', 'w') as f:
            f.write("RBH-1 LINE-PROFILE DECOMPOSITION RESULTS\n")
            f.write("="*60 + "\n\n")
            f.write(f"Data: JWST NIRSpec IFU (Program 3149)\n")
            f.write(f"Line: [O III] λ5007\n")
            f.write(f"Redshift: z = 0.964\n\n")
            f.write("SINGLE-COMPONENT FIT:\n")
            f.write(f"  σ = {results['single_component']['params'][2]:.1f} ± {results['single_component']['params_err'][2]:.1f} km/s\n")
            f.write(f"  χ²/dof = {results['single_component']['chi2_red']:.3f}\n")
            f.write(f"  BIC = {results['single_component']['bic']:.2f}\n\n")
            f.write("TWO-COMPONENT FIT:\n")
            f.write(f"  σ₁ (narrow) = {results['two_component']['params'][2]:.1f} ± {results['two_component']['params_err'][2]:.1f} km/s\n")
            f.write(f"  σ₂ (broad) = {results['two_component']['params'][4]:.0f} km/s (fixed)\n")
            f.write(f"  Broad/Narrow flux = {results['two_component']['flux_ratio']:.3f}\n")
            f.write(f"  χ²/dof = {results['two_component']['chi2_red']:.3f}\n")
            f.write(f"  BIC = {results['two_component']['bic']:.2f}\n\n")
            f.write("MODEL SELECTION:\n")
            f.write(f"  ΔBIC = {results['model_selection']['delta_bic']:.2f}\n")
            f.write(f"  Interpretation: {results['model_selection']['interpretation']}\n\n")
            f.write(f"VERDICT: {results['model_selection']['verdict']}\n")
        
        print("\n✓ Results saved to: ../site/figures/line_profile_results.txt")
        print("✓ Figure saved to: ../site/figures/figure_05_decomposition.png")

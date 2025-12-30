"""
Extract [O III] λ5007 Line Profile from JWST NIRSpec Data

This script reads the downloaded JWST NIRSpec x1d FITS files and extracts
the [O III] λ5007 emission line profile for line-profile decomposition analysis.

Author: M. Smawfield
Date: December 2025
"""

import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import glob
import os

# Constants
c_kms = 299792.458  # Speed of light in km/s
z_rbh1 = 0.964  # Redshift of RBH-1
lambda_oiii_rest = 5006.843  # [O III] rest wavelength in Angstroms
lambda_oiii_obs = lambda_oiii_rest * (1 + z_rbh1)  # Observed wavelength

def extract_oiii_from_x1d(fits_file, output_file=None):
    """
    Extract [O III] line profile from NIRSpec x1d FITS file.
    
    Parameters:
    -----------
    fits_file : str
        Path to x1d FITS file
    output_file : str
        Path to save extracted spectrum (optional)
    
    Returns:
    --------
    velocity : array
        Velocity array in km/s relative to line center
    flux : array
        Flux array
    flux_err : array
        Flux uncertainty array
    """
    
    print(f"\nReading: {os.path.basename(fits_file)}")
    
    with fits.open(fits_file) as hdul:
        # Print HDU structure
        print(f"  HDUs: {len(hdul)}")
        for i, hdu in enumerate(hdul):
            print(f"    [{i}] {hdu.name}: {hdu.data.shape if hdu.data is not None else 'No data'}")
        
        # Extract spectrum from EXTRACT1D extension
        if 'EXTRACT1D' in hdul:
            data = hdul['EXTRACT1D'].data
            
            # Get wavelength, flux, and error
            wavelength = data['WAVELENGTH'][0]  # Angstroms
            flux = data['FLUX'][0]  # Flux units
            flux_err = data['FLUX_ERROR'][0]
            
            # Find [O III] line region (±1500 km/s ~ ±25 Angstroms at z=0.96)
            lambda_min = lambda_oiii_obs - 25
            lambda_max = lambda_oiii_obs + 25
            
            mask = (wavelength >= lambda_min) & (wavelength <= lambda_max)
            
            if np.sum(mask) == 0:
                print(f"  WARNING: No data in [O III] region")
                return None, None, None
            
            # Extract line region
            wave_line = wavelength[mask]
            flux_line = flux[mask]
            flux_err_line = flux_err[mask]
            
            # Convert wavelength to velocity relative to line center
            velocity = c_kms * (wave_line - lambda_oiii_obs) / lambda_oiii_obs
            
            # Check for valid data
            valid = np.isfinite(flux_line) & np.isfinite(flux_err_line) & (flux_err_line > 0)
            
            if np.sum(valid) < 10:
                print(f"  WARNING: Insufficient valid data points ({np.sum(valid)})")
                return None, None, None
            
            velocity = velocity[valid]
            flux_line = flux_line[valid]
            flux_err_line = flux_err_line[valid]
            
            # Calculate S/N
            continuum = np.median(flux_line[np.abs(velocity) > 200])
            peak_flux = np.max(flux_line)
            peak_err = flux_err_line[np.argmax(flux_line)]
            sn_peak = (peak_flux - continuum) / peak_err if peak_err > 0 else 0
            
            print(f"  Valid points: {len(velocity)}")
            print(f"  Velocity range: {velocity.min():.1f} to {velocity.max():.1f} km/s")
            print(f"  Peak S/N: {sn_peak:.1f}")
            
            # Save to file if requested
            if output_file:
                np.savetxt(output_file, 
                          np.column_stack([velocity, flux_line, flux_err_line]),
                          header='velocity (km/s), flux, flux_error\n[O III] λ5007 extracted from JWST NIRSpec',
                          fmt='%.6e')
                print(f"  Saved to: {output_file}")
            
            return velocity, flux_line, flux_err_line
        
        else:
            print(f"  ERROR: No EXTRACT1D extension found")
            return None, None, None


def find_best_spectrum(data_dir='../data/rbh1_jwst'):
    """
    Find the x1d file with the highest S/N [O III] detection.
    """
    
    print("="*80)
    print("SEARCHING FOR BEST [O III] SPECTRUM")
    print("="*80)
    
    # Find all x1d files
    x1d_files = glob.glob(f'{data_dir}/mastDownload/JWST/*/*_x1d.fits')
    
    print(f"\nFound {len(x1d_files)} x1d files")
    
    best_sn = 0
    best_file = None
    best_data = None
    
    for fits_file in x1d_files:
        velocity, flux, flux_err = extract_oiii_from_x1d(fits_file)
        
        if velocity is not None:
            # Calculate S/N
            continuum = np.median(flux[np.abs(velocity) > 200])
            peak_flux = np.max(flux)
            peak_err = flux_err[np.argmax(flux)]
            sn_peak = (peak_flux - continuum) / peak_err if peak_err > 0 else 0
            
            if sn_peak > best_sn:
                best_sn = sn_peak
                best_file = fits_file
                best_data = (velocity, flux, flux_err)
    
    if best_file:
        print("\n" + "="*80)
        print("BEST SPECTRUM IDENTIFIED")
        print("="*80)
        print(f"\nFile: {os.path.basename(best_file)}")
        print(f"Peak S/N: {best_sn:.1f}")
        
        return best_file, best_data
    else:
        print("\nERROR: No valid [O III] spectra found")
        return None, None


if __name__ == '__main__':
    
    # Find best spectrum
    best_file, best_data = find_best_spectrum()
    
    if best_file:
        velocity, flux, flux_err = best_data
        
        # Save extracted spectrum
        output_file = '../data/rbh1_oiii_extracted.dat'
        np.savetxt(output_file,
                  np.column_stack([velocity, flux, flux_err]),
                  header='velocity (km/s), flux, flux_error\n[O III] λ5007 from JWST NIRSpec (Program 3149)',
                  fmt='%.6e')
        
        print(f"\n✓ Saved extracted spectrum to: {output_file}")
        
        # Quick plot
        plt.figure(figsize=(10, 6))
        plt.errorbar(velocity, flux, yerr=flux_err, fmt='o', markersize=3, alpha=0.6)
        plt.axvline(0, color='red', linestyle='--', alpha=0.5, label='Line center')
        plt.xlabel('Velocity (km/s)')
        plt.ylabel('Flux')
        plt.title('[O III] λ5007 Line Profile (JWST NIRSpec)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig('../site/figures/rbh1_oiii_raw.png', dpi=150, bbox_inches='tight')
        print(f"✓ Saved preview plot to: ../site/figures/rbh1_oiii_raw.png")
        
        print("\n" + "="*80)
        print("EXTRACTION COMPLETE")
        print("="*80)
        print("\nNext step:")
        print("  python analyze_line_profiles.py --data ../data/rbh1_oiii_extracted.dat")
    else:
        print("\nFailed to extract [O III] spectrum")

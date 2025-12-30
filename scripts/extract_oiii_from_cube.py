"""
Extract [O III] λ5007 Line Profile from JWST NIRSpec IFU Cubes

The x1d files don't cover [O III] - need to use s3d cubes instead.

Author: M. Smawfield
Date: December 2025
"""

import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import glob
import os

# Constants
c_kms = 299792.458
z_rbh1 = 0.964
lambda_oiii_rest = 5006.843  # Angstroms
lambda_oiii_obs = lambda_oiii_rest * (1 + z_rbh1)  # ~9833 Angstroms = 0.9833 microns

def extract_oiii_from_s3d(fits_file, output_file=None):
    """Extract [O III] from NIRSpec s3d IFU cube."""
    
    print(f"\nReading: {os.path.basename(fits_file)}")
    
    with fits.open(fits_file) as hdul:
        print(f"  HDUs: {len(hdul)}")
        
        # Get the science data
        if 'SCI' in hdul:
            cube = hdul['SCI'].data  # Shape: (nwave, ny, nx)
            header = hdul['SCI'].header
            
            # Get wavelength solution
            nwave = cube.shape[0]
            crval3 = header.get('CRVAL3', None)  # Reference wavelength (microns)
            crpix3 = header.get('CRPIX3', None)  # Reference pixel
            cdelt3 = header.get('CDELT3', None)  # Wavelength step (microns)
            
            if crval3 is None or cdelt3 is None:
                print(f"  ERROR: Missing wavelength solution")
                return None, None, None
            
            # Build wavelength array (microns)
            wavelength_microns = crval3 + (np.arange(nwave) - (crpix3 - 1)) * cdelt3
            wavelength_angstroms = wavelength_microns * 10000  # Convert to Angstroms
            
            print(f"  Cube shape: {cube.shape}")
            print(f"  Wavelength range: {wavelength_angstroms.min():.1f} - {wavelength_angstroms.max():.1f} Å")
            print(f"  [O III] expected at: {lambda_oiii_obs:.1f} Å")
            
            # Check if [O III] is in range
            if lambda_oiii_obs < wavelength_angstroms.min() or lambda_oiii_obs > wavelength_angstroms.max():
                print(f"  WARNING: [O III] not in wavelength range")
                return None, None, None
            
            # Find wavelength channels near [O III] (±1500 km/s ~ ±50 Å)
            lambda_min = lambda_oiii_obs - 50
            lambda_max = lambda_oiii_obs + 50
            
            wave_mask = (wavelength_angstroms >= lambda_min) & (wavelength_angstroms <= lambda_max)
            
            if np.sum(wave_mask) == 0:
                print(f"  WARNING: No wavelength channels in [O III] region")
                return None, None, None
            
            print(f"  Found {np.sum(wave_mask)} wavelength channels near [O III]")
            
            # Extract spatial region at tip (brightest pixel in [O III] image)
            oiii_image = np.nansum(cube[wave_mask, :, :], axis=0)
            
            # Find brightest pixel
            valid_pixels = np.isfinite(oiii_image) & (oiii_image > 0)
            if not np.any(valid_pixels):
                print(f"  WARNING: No valid pixels in [O III] image")
                return None, None, None
            
            y_peak, x_peak = np.unravel_index(np.nanargmax(oiii_image), oiii_image.shape)
            print(f"  Peak at pixel: ({x_peak}, {y_peak})")
            
            # Extract spectrum at peak (sum 3x3 aperture)
            y_min, y_max = max(0, y_peak-1), min(cube.shape[1], y_peak+2)
            x_min, x_max = max(0, x_peak-1), min(cube.shape[2], x_peak+2)
            
            spectrum = np.nansum(cube[:, y_min:y_max, x_min:x_max], axis=(1, 2))
            
            # Estimate error from variance in continuum regions
            continuum_mask = (wavelength_angstroms < lambda_oiii_obs - 100) | (wavelength_angstroms > lambda_oiii_obs + 100)
            if np.sum(continuum_mask) > 10:
                continuum_std = np.nanstd(spectrum[continuum_mask])
            else:
                continuum_std = np.nanstd(spectrum) * 0.1
            
            spectrum_err = np.ones_like(spectrum) * continuum_std
            
            # Extract line region
            wave_line = wavelength_angstroms[wave_mask]
            flux_line = spectrum[wave_mask]
            flux_err_line = spectrum_err[wave_mask]
            
            # Convert to velocity
            velocity = c_kms * (wave_line - lambda_oiii_obs) / lambda_oiii_obs
            
            # Remove NaNs
            valid = np.isfinite(flux_line) & np.isfinite(flux_err_line)
            velocity = velocity[valid]
            flux_line = flux_line[valid]
            flux_err_line = flux_err_line[valid]
            
            if len(velocity) < 10:
                print(f"  WARNING: Insufficient valid points ({len(velocity)})")
                return None, None, None
            
            # Calculate S/N
            continuum = np.median(flux_line[np.abs(velocity) > 200]) if np.any(np.abs(velocity) > 200) else np.median(flux_line)
            peak_flux = np.max(flux_line)
            sn_peak = (peak_flux - continuum) / continuum_std if continuum_std > 0 else 0
            
            print(f"  Valid points: {len(velocity)}")
            print(f"  Velocity range: {velocity.min():.1f} to {velocity.max():.1f} km/s")
            print(f"  Peak S/N: {sn_peak:.1f}")
            
            if output_file:
                np.savetxt(output_file,
                          np.column_stack([velocity, flux_line, flux_err_line]),
                          header='velocity (km/s), flux, flux_error\n[O III] λ5007 from JWST NIRSpec IFU',
                          fmt='%.6e')
                print(f"  Saved to: {output_file}")
            
            return velocity, flux_line, flux_err_line
        
        else:
            print(f"  ERROR: No SCI extension found")
            return None, None, None


def find_best_cube(data_dir='../data/rbh1_jwst'):
    """Find the s3d cube with best [O III] detection."""
    
    print("="*80)
    print("SEARCHING FOR BEST [O III] SPECTRUM IN IFU CUBES")
    print("="*80)
    
    s3d_files = glob.glob(f'{data_dir}/mastDownload/JWST/*/*_s3d.fits')
    
    print(f"\nFound {len(s3d_files)} s3d files")
    
    best_sn = 0
    best_file = None
    best_data = None
    
    for fits_file in s3d_files:
        velocity, flux, flux_err = extract_oiii_from_s3d(fits_file)
        
        if velocity is not None:
            continuum = np.median(flux[np.abs(velocity) > 200]) if np.any(np.abs(velocity) > 200) else np.median(flux)
            peak_flux = np.max(flux)
            continuum_std = np.median(flux_err)
            sn_peak = (peak_flux - continuum) / continuum_std if continuum_std > 0 else 0
            
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
        print("\nERROR: No valid [O III] spectra found in cubes")
        return None, None


if __name__ == '__main__':
    best_file, best_data = find_best_cube()
    
    if best_file:
        velocity, flux, flux_err = best_data
        
        output_file = '../data/rbh1_oiii_extracted.dat'
        np.savetxt(output_file,
                  np.column_stack([velocity, flux, flux_err]),
                  header='velocity (km/s), flux, flux_error\n[O III] λ5007 from JWST NIRSpec IFU',
                  fmt='%.6e')
        
        print(f"\n✓ Saved: {output_file}")
        
        # Plot
        plt.figure(figsize=(10, 6))
        plt.errorbar(velocity, flux, yerr=flux_err, fmt='o', markersize=3, alpha=0.6)
        plt.axvline(0, color='red', linestyle='--', alpha=0.5)
        plt.xlabel('Velocity (km/s)')
        plt.ylabel('Flux')
        plt.title('[O III] λ5007 (JWST NIRSpec IFU)')
        plt.grid(True, alpha=0.3)
        plt.savefig('../site/figures/rbh1_oiii_raw.png', dpi=150, bbox_inches='tight')
        print(f"✓ Saved: ../site/figures/rbh1_oiii_raw.png")
        
        print("\n" + "="*80)
        print("READY FOR LINE-PROFILE ANALYSIS")
        print("="*80)
        print("\nRun: python analyze_line_profiles.py --data ../data/rbh1_oiii_extracted.dat")

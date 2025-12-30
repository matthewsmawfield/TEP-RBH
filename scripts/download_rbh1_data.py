"""
Download RBH-1 JWST NIRSpec Spectroscopic Data from MAST

This script downloads the JWST NIRSpec IFU observations of RBH-1 from the
Mikulski Archive for Space Telescopes (MAST).

Program: JWST-GO-3149 (PI: van Dokkum)
Observation Date: July 24, 2024

Author: M. Smawfield
Date: December 2025
"""

import os
from astroquery.mast import Observations
import warnings
warnings.filterwarnings('ignore')

def download_rbh1_jwst_data(output_dir='../data/rbh1_jwst'):
    """
    Download JWST NIRSpec IFU data for RBH-1.
    
    Parameters:
    -----------
    output_dir : str
        Directory to save downloaded data
    """
    
    print("="*80)
    print("DOWNLOADING RBH-1 JWST DATA FROM MAST")
    print("="*80)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Search for observations by program ID
    print("\n### Searching for JWST-GO-3149 observations...")
    
    try:
        # Query by proposal ID
        obs_table = Observations.query_criteria(
            proposal_id='3149',
            obs_collection='JWST'
        )
        
        print(f"\nFound {len(obs_table)} observations")
        
        if len(obs_table) == 0:
            print("\nNo observations found. Trying alternative search...")
            # Try searching by target name
            obs_table = Observations.query_criteria(
                target_name='*RBH*',
                obs_collection='JWST',
                instrument_name='NIRSPEC/IFU'
            )
            print(f"Found {len(obs_table)} observations with target name search")
        
        if len(obs_table) == 0:
            print("\nERROR: No JWST observations found for RBH-1")
            print("\nPossible reasons:")
            print("1. Data may still be in proprietary period")
            print("2. Data may not yet be publicly released")
            print("3. Program ID may be different")
            print("\nRecommendation: Contact PI (Pieter van Dokkum) directly to request data")
            return None
        
        # Display observation info
        print("\n### Observation Details:")
        for i, obs in enumerate(obs_table):
            print(f"\nObservation {i+1}:")
            print(f"  Obs ID: {obs['obs_id']}")
            print(f"  Target: {obs['target_name']}")
            print(f"  Instrument: {obs['instrument_name']}")
            print(f"  Filters: {obs['filters']}")
            print(f"  Exposure Time: {obs['t_exptime']} s")
            print(f"  Date: {obs['t_min']}")
        
        # Get data products
        print("\n### Retrieving data products...")
        data_products = Observations.get_product_list(obs_table)
        
        print(f"Found {len(data_products)} data products")
        
        # Filter for spectroscopic products
        # We want x1d (1D extracted spectra) or s3d (3D IFU cubes)
        spec_products = data_products[
            (data_products['productType'] == 'SCIENCE') &
            ((data_products['productSubGroupDescription'] == 'X1D') |
             (data_products['productSubGroupDescription'] == 'S3D'))
        ]
        
        print(f"\nFiltered to {len(spec_products)} spectroscopic products")
        
        if len(spec_products) == 0:
            print("\nNo spectroscopic products found. Showing all products:")
            print(data_products['productSubGroupDescription'].unique())
            spec_products = data_products[data_products['productType'] == 'SCIENCE']
        
        # Display products
        print("\n### Available Products:")
        for i, prod in enumerate(spec_products[:10]):  # Show first 10
            print(f"\n{i+1}. {prod['productFilename']}")
            print(f"   Type: {prod['productSubGroupDescription']}")
            print(f"   Size: {prod['size']/1e6:.1f} MB")
        
        # Download products
        print(f"\n### Downloading {len(spec_products)} products to {output_dir}...")
        print("This may take several minutes depending on file sizes...")
        
        manifest = Observations.download_products(
            spec_products,
            download_dir=output_dir
        )
        
        print(f"\n✓ Downloaded {len(manifest)} files")
        print(f"✓ Data saved to: {output_dir}")
        
        # List downloaded files
        print("\n### Downloaded Files:")
        for i, file_path in enumerate(manifest['Local Path'][:10]):
            print(f"{i+1}. {file_path}")
        
        return manifest
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Verify astroquery is installed: pip install astroquery")
        print("3. Check if data is publicly available")
        print("4. Try manual download from: https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html")
        return None


if __name__ == '__main__':
    print("\nRBH-1 JWST Data Download Script")
    print("Program: JWST-GO-3149 (PI: van Dokkum)")
    print("\nNote: This requires the 'astroquery' package.")
    print("Install with: pip install astroquery\n")
    
    # Check if astroquery is installed
    try:
        from astroquery.mast import Observations
        manifest = download_rbh1_jwst_data()
        
        if manifest is not None:
            print("\n" + "="*80)
            print("DOWNLOAD COMPLETE")
            print("="*80)
            print("\nNext steps:")
            print("1. Locate the x1d or s3d FITS files in the download directory")
            print("2. Extract the [O III] λ5007 line profile")
            print("3. Run: python analyze_line_profiles.py --data <spectrum_file>")
        else:
            print("\n" + "="*80)
            print("DOWNLOAD FAILED - DATA MAY BE PROPRIETARY")
            print("="*80)
            print("\nAlternative approach:")
            print("Contact PI directly: pieter.vandokkum@yale.edu")
            print("Request access to reduced NIRSpec IFU data for RBH-1")
            print("Specifically: 1D extracted spectrum of [O III] at the tip")
            
    except ImportError:
        print("ERROR: astroquery not installed")
        print("\nInstall with:")
        print("  pip install astroquery")
        print("\nOr use conda:")
        print("  conda install -c conda-forge astroquery")

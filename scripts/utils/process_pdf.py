#!/usr/bin/env python3
"""
Unified PDF Processing Script
Compresses PDF and embeds comprehensive metadata in one operation.

Usage:
    python process_pdf.py <input_pdf> [--quality ebook|printer|prepress|default]
    
Example:
    python process_pdf.py site/public/docs/paper.pdf --quality ebook
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse
import tempfile


def compress_pdf(input_path, output_path, quality='ebook'):
    """Compress PDF using Ghostscript."""
    quality_settings = {
        'screen': '/screen',      # 72 dpi
        'ebook': '/ebook',        # 150 dpi
        'printer': '/printer',    # 300 dpi
        'prepress': '/prepress',  # 300 dpi, color preserving
        'default': '/default'
    }
    
    if quality not in quality_settings:
        raise ValueError(f"Quality must be one of: {', '.join(quality_settings.keys())}")
    
    gs_quality = quality_settings[quality]
    
    # Get original size
    original_size = os.path.getsize(input_path)
    
    # Compress using Ghostscript
    cmd = [
        'gs',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        f'-dPDFSETTINGS={gs_quality}',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={output_path}',
        input_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        compressed_size = os.path.getsize(output_path)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        return {
            'original_mb': original_size / (1024 * 1024),
            'compressed_mb': compressed_size / (1024 * 1024),
            'reduction_pct': reduction
        }
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ghostscript compression failed: {e.stderr.decode()}")


def embed_metadata(pdf_path, metadata):
    """Embed metadata into PDF using exiftool."""
    cmd = ['exiftool']
    
    # Add all metadata fields
    for key, value in metadata.items():
        cmd.extend([f'-{key}={value}'])
    
    # Overwrite original
    cmd.extend(['-overwrite_original', pdf_path])
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Exiftool metadata embedding failed: {e.stderr.decode()}")


def verify_metadata(pdf_path, expected_fields):
    """Verify metadata was embedded correctly."""
    cmd = ['exiftool'] + [f'-{field}' for field in expected_fields] + [pdf_path]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Compress PDF and embed metadata in one operation'
    )
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument(
        '--quality',
        choices=['screen', 'ebook', 'printer', 'prepress', 'default'],
        default='ebook',
        help='Compression quality (default: ebook)'
    )
    parser.add_argument(
        '--doi',
        default='10.5281/zenodo.18059250',
        help='DOI to embed in metadata'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_pdf).resolve()
    
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    print(f"Processing: {input_path}")
    print(f"Quality: {args.quality}")
    print()
    
    # Step 1: Compress PDF
    print("Step 1: Compressing PDF...")
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        stats = compress_pdf(str(input_path), tmp_path, args.quality)
        
        # Replace original with compressed version
        os.replace(tmp_path, str(input_path))
        
        print(f"  Original:    {stats['original_mb']:.2f} MB")
        print(f"  Compressed:  {stats['compressed_mb']:.2f} MB")
        print(f"  Reduction:   {stats['reduction_pct']:.1f}%")
        print()
        
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"Error during compression: {e}")
        sys.exit(1)
    
    # Step 2: Embed metadata
    print("Step 2: Embedding metadata...")
    
    metadata = {
        'Title': 'The Soliton Wake: Identifying the Runaway Object RBH-1 as a Gravitational Soliton',
        'Author': 'Matthew Lukin Smawfield',
        'Subject': f'The runaway supermassive black hole RBH-1 (z ~ 0.96) presents a thermal paradox: JWST spectroscopy reveals a 650 km/s velocity discontinuity coexisting with cold, star-forming gas. Higher-resolution Keck/LRIS spectroscopy yields a narrow apex dispersion (sigma ~ 31 +/- 4 km/s), far below the sigma ~ 80-85 km/s expected if the emitting gas were predominantly at T ~ 10^7 K. Standard shock physics predicts post-shock temperatures T ~ 10^7 K, yielding a cooling time that exceeds the dynamical time by a factor of ~30. Yet the wake exhibits immediate star formation and extreme collimation (50:1 aspect ratio over 62 kpc). RBH-1 is explored as a candidate Temporal Topology soliton/wake interpretation: a coherent region of altered proper-time rate. Under this candidate framing, the observed velocity discontinuity is reinterpreted as a metric shock (spatial gradient in gravitational redshift) rather than bulk thermalization, and the effective Jeans mass is reduced behind the front via time dilation, enabling immediate star formation without heating. The characteristic temporal scale R_T, calibrated from terrestrial GNSS correlations (Smawfield 2025g), is applied as a consistency check rather than as proof that RBH-1 is a soliton. For RBH-1 (M ~ 2 x 10^7 M_sun), the calibration yields R_T ~ 7.8 x 10^7 km ~ 1.3 R_S, comparable to the apparent wake morphology. The amplitude of the observed kinematic discontinuity depends on screening/transition physics (via beta_eff at R_trans) and is treated as an empirical constraint rather than an independent prediction. Specific falsification criteria are outlined; decisive discrimination awaits line-profile decomposition and X-ray flux limits. DOI: {args.doi}',
        'Keywords': 'RBH-1; runaway black hole; scalar soliton; dark matter; gravitation; temporal equivalence principle; magnetars; JWST; Gaia DR3; rotation curves; Milky Way; cold shock; neutron stars; temporal topology; gravitational redshift; SPARC; GNSS; atomic clocks; metric shock',
        'Creator': 'Matthew Lukin Smawfield',
        'Producer': 'TEP-RBH Research Project',
        'Copyright': 'Creative Commons Attribution 4.0 International License (CC BY 4.0)',
        'CreationDate': '2025:12:28 00:00:00',
        'ModifyDate': '2025:12:28 00:00:00'
    }
    
    try:
        embed_metadata(str(input_path), metadata)
        print("  Metadata embedded successfully")
        print()
        
    except Exception as e:
        print(f"Error during metadata embedding: {e}")
        sys.exit(1)
    
    # Step 3: Verify
    print("Step 3: Verifying metadata...")
    verification = verify_metadata(
        str(input_path),
        ['Title', 'Author', 'Subject', 'Keywords', 'Creator', 'Copyright']
    )
    
    if verification:
        print("  ✓ Metadata verified")
        print()
        print("Verification output:")
        print(verification)
    else:
        print("  ⚠ Could not verify metadata")
    
    print()
    print(f"✓ Processing complete: {input_path}")
    print(f"  Final size: {os.path.getsize(input_path) / (1024 * 1024):.2f} MB")


if __name__ == '__main__':
    main()

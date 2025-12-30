# TEP-RBH Analysis Scripts

Analysis code for the TEP-RBH manuscript: "The Soliton Wake: Identifying the Runaway Object RBH-1 as a Gravitational Soliton"

## Directory Structure

```
scripts/
├── figures/           # Figure generation scripts (numbered sequentially)
├── eht_analysis/      # Event Horizon Telescope polarization analysis
├── analysis_checks/   # Supplementary validation scripts
├── utils/             # Shared utilities
└── archive/           # Deprecated/superseded scripts
```

## Figure Generation Scripts

Located in `scripts/figures/`:

| Script | Figure | Description |
|--------|--------|-------------|
| `01_wake_anatomy.py` | Figure 3 | Wake anatomy comparison (thermal vs metric shock) |
| `02_sensitivity.py` | Figure 2 | Cooling sensitivity analysis (cooling bottleneck) |
| `07_polarization.py` | Figure A1 | EHT polarimetry prediction |
| `09_line_width_test.py` | Figure 4 | Line width test (thermal vs metric shock) |
| `10_wake_geometry.py` | Figure 6 | Wake geometry analysis |
| `11_stellar_age.py` | Figure 7 | Stellar age gradient analysis |
| `12_line_ratios.py` | Figure 8 | Emission line ratio analysis |
| `13_energy_budget.py` | Figure 9 | Energy budget and SFE analysis |
| `14_scaling.py` | Figure 10 | Universal scaling law (RBH-1 vs others) |
| `../analyze_line_profiles.py` | Figure 5 | Line profile decomposition (synthetic) |

**Note:** Figures 7-8 (polarization/sensitivity) were removed from the manuscript and moved to archive. Scripts `07_polarization.py` and `08_sensitivity.py` remain for reference but are not part of the main figure set.

## SPARC Analysis (Reproducibility)

The SPARC galaxy analysis (`scripts/figures/05_sparc_analysis.py`) implements:

1. **Baryonic mass calculation:** $M_{\rm bar} = M_* + 1.33 M_{\rm HI}$
2. **Onset radius definition:** First radial bin where $V_{\rm obs}/V_{\rm bar} > 1.3$
3. **Bootstrap uncertainties:** 1000 resamples
4. **Threshold marginalization:** Loose (1.1), Fiducial (1.3), Strict (1.5)

### Input Data

SPARC database tables are located in `data/sparc/`:
- `Table1.mrt` - Galaxy properties
- `Table2.mrt` - Rotation curve data

### Running the Analysis

```bash
cd scripts/figures
python 05_sparc_analysis.py
```

Output: `site/figures/figure_5_sparc_enhanced.png`

## EHT Polarization Analysis

Located in `scripts/eht_analysis/`:

- `eht_complete_analysis.py` - Full polarization analysis pipeline
- `eht_polarization_complete.py` - Comprehensive polarization metrics
- `eht_proper_imaging_analysis.py` - Image reconstruction analysis
- `eht_pol_survey_2017.py` - 2017 M87* polarization survey
- `eht_pol_rml_validate_2017.py` - RML validation

## Requirements

```bash
pip install -r requirements.txt
```

Key dependencies:
- numpy
- matplotlib
- scipy
- astropy

## Citation

If you use this code, please cite:

```bibtex
@article{smawfield2025rbh1,
  author = {Smawfield, Matthew Lukin},
  title = {The Soliton Wake: Identifying the Runaway Object RBH-1 as a Gravitational Soliton},
  year = {2025},
  doi = {10.5281/zenodo.18059251}
}
```

## License

CC-BY-4.0

"""
RBH-1 Line-Profile Decomposition Analysis

This script implements the "Primary Discriminant" test between the Soliton (cold metric shock)
and Standard (thermal shock) models: rigorous line-profile decomposition to search for hidden
broad wings indicative of hot gas.

The Test:
- Single-component model: Pure cold gas (narrow Gaussian, σ ~ 30 km/s)
- Two-component model: Cold core + hot wing (narrow + broad Gaussian)
- Bayesian model selection (BIC/AIC) determines which model is preferred

If broad wings are detected → Standard thermal shock model favored
If broad wings are absent → Soliton (cold metric shock) model favored

Author: M. Smawfield
Date: December 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, minimize
from scipy.stats import chi2
import warnings
import os
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
# Also try adding current directory if running from scripts/
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from utils.style import set_pub_style, COLORS, FIG_SIZE
except ImportError:
    # If running from root, path might be different
    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'scripts')))
    from utils.style import set_pub_style, COLORS, FIG_SIZE

warnings.filterwarnings('ignore')

set_pub_style()

# --- Physical Constants ---
c_kms = 299792.458  # Speed of light in km/s
k_B = 1.380649e-23  # Boltzmann constant (J/K)
m_p = 1.6726219e-27  # Proton mass (kg)

def thermal_width(T, mass_amu=16):
    """
    Calculate thermal velocity dispersion for a given temperature.
    
    Parameters:
    -----------
    T : float
        Temperature in Kelvin
    mass_amu : float
        Atomic mass in amu (default: 16 for O III)
    
    Returns:
    --------
    sigma : float
        Velocity dispersion in km/s
    """
    m = mass_amu * m_p
    sigma_ms = np.sqrt(k_B * T / m)
    sigma_kms = sigma_ms / 1000
    return sigma_kms

# --- Model Functions ---
def gaussian(v, amplitude, v0, sigma):
    """Single Gaussian profile."""
    return amplitude * np.exp(-0.5 * ((v - v0) / sigma)**2)

def single_component(v, A1, v0, sigma1, continuum):
    """Single-component model: narrow core only."""
    return gaussian(v, A1, v0, sigma1) + continuum

def two_component(v, A1, v0, sigma1, A2, sigma2, continuum):
    """Two-component model: narrow core + broad wing."""
    return gaussian(v, A1, v0, sigma1) + gaussian(v, A2, v0, sigma2) + continuum

# --- Fitting Functions ---
def fit_single_component(velocity, flux, flux_err, initial_guess=None):
    """
    Fit single-component Gaussian model.
    
    Returns:
    --------
    params : array
        Best-fit parameters [A1, v0, sigma1, continuum]
    params_err : array
        Parameter uncertainties
    chi2_red : float
        Reduced chi-squared
    """
    if initial_guess is None:
        # Auto-generate initial guess
        continuum_guess = np.median(flux[:10])
        A1_guess = np.max(flux) - continuum_guess
        v0_guess = velocity[np.argmax(flux)]
        sigma1_guess = 30.0  # km/s
        initial_guess = [A1_guess, v0_guess, sigma1_guess, continuum_guess]
    
    try:
        params, cov = curve_fit(
            single_component, 
            velocity, 
            flux, 
            p0=initial_guess,
            sigma=flux_err,
            absolute_sigma=True,
            maxfev=10000
        )
        params_err = np.sqrt(np.diag(cov))
        
        # Calculate chi-squared
        model = single_component(velocity, *params)
        chi2_val = np.sum(((flux - model) / flux_err)**2)
        dof = len(velocity) - len(params)
        chi2_red = chi2_val / dof
        
        return params, params_err, chi2_red, chi2_val
    except:
        return None, None, np.inf, np.inf

def fit_two_component(velocity, flux, flux_err, sigma2_fixed=None, initial_guess=None):
    """
    Fit two-component Gaussian model.
    
    Parameters:
    -----------
    sigma2_fixed : float or None
        If provided, fix the broad component width to this value (km/s)
    
    Returns:
    --------
    params : array
        Best-fit parameters [A1, v0, sigma1, A2, sigma2, continuum]
    params_err : array
        Parameter uncertainties
    chi2_red : float
        Reduced chi-squared
    """
    if initial_guess is None:
        # Auto-generate initial guess
        continuum_guess = np.median(flux[:10])
        A1_guess = (np.max(flux) - continuum_guess) * 0.9
        v0_guess = velocity[np.argmax(flux)]
        sigma1_guess = 30.0  # km/s (narrow)
        A2_guess = (np.max(flux) - continuum_guess) * 0.1
        sigma2_guess = 90.0 if sigma2_fixed is None else sigma2_fixed  # km/s (broad)
        initial_guess = [A1_guess, v0_guess, sigma1_guess, A2_guess, sigma2_guess, continuum_guess]
    
    if sigma2_fixed is not None:
        # Fixed broad width version
        def two_comp_fixed(v, A1, v0, sigma1, A2, continuum):
            return two_component(v, A1, v0, sigma1, A2, sigma2_fixed, continuum)
        
        try:
            params_free, cov = curve_fit(
                two_comp_fixed,
                velocity,
                flux,
                p0=[initial_guess[0], initial_guess[1], initial_guess[2], 
                    initial_guess[3], initial_guess[5]],
                sigma=flux_err,
                absolute_sigma=True,
                maxfev=10000
            )
            # Insert fixed sigma2 back into params
            params = np.array([params_free[0], params_free[1], params_free[2], 
                              params_free[3], sigma2_fixed, params_free[4]])
            # Adjust covariance matrix
            cov_full = np.zeros((6, 6))
            indices = [0, 1, 2, 3, 5]
            for i, idx_i in enumerate(indices):
                for j, idx_j in enumerate(indices):
                    cov_full[idx_i, idx_j] = cov[i, j]
            params_err = np.sqrt(np.diag(cov_full))
            params_err[4] = 0.0  # Fixed parameter has zero uncertainty
            
            n_free_params = 5
        except:
            return None, None, np.inf, np.inf
    else:
        # Free broad width version
        try:
            params, cov = curve_fit(
                two_component,
                velocity,
                flux,
                p0=initial_guess,
                sigma=flux_err,
                absolute_sigma=True,
                maxfev=10000
            )
            params_err = np.sqrt(np.diag(cov))
            n_free_params = 6
        except:
            return None, None, np.inf, np.inf
    
    # Calculate chi-squared
    model = two_component(velocity, *params)
    chi2_val = np.sum(((flux - model) / flux_err)**2)
    dof = len(velocity) - n_free_params
    chi2_red = chi2_val / dof
    
    return params, params_err, chi2_red, chi2_val

# --- Model Selection ---
def calculate_bic(chi2, n_data, n_params):
    """Calculate Bayesian Information Criterion."""
    return chi2 + n_params * np.log(n_data)

def calculate_aic(chi2, n_params):
    """Calculate Akaike Information Criterion."""
    return chi2 + 2 * n_params

def bayes_factor(delta_bic):
    """
    Interpret BIC difference (Kass & Raftery 1995).
    
    Returns interpretation string.
    """
    if delta_bic < 0:
        return "ERROR: Complex model preferred"
    elif delta_bic < 2:
        return "Not worth more than a bare mention"
    elif delta_bic < 6:
        return "Positive evidence against complex model"
    elif delta_bic < 10:
        return "Strong evidence against complex model"
    else:
        return "Very strong evidence against complex model"

# --- Synthetic Data Generation ---
def generate_synthetic_spectrum(scenario='cold_only', S_N=50, n_points=100):
    """
    Generate synthetic [O III] line profile for testing.
    
    Parameters:
    -----------
    scenario : str
        'cold_only' - Pure narrow line (Soliton model)
        'cold_plus_hot' - Narrow core + broad wing (Thermal model)
        'hot_only' - Pure broad line (Pure thermal shock)
    S_N : float
        Signal-to-noise ratio at line peak
    n_points : int
        Number of spectral pixels
    
    Returns:
    --------
    velocity : array
        Velocity array (km/s)
    flux : array
        Flux array (arbitrary units)
    flux_err : array
        Flux uncertainty array
    true_params : dict
        True model parameters
    """
    # Velocity grid: -300 to +300 km/s
    velocity = np.linspace(-300, 300, n_points)
    
    # Continuum level
    continuum = 1.0
    
    if scenario == 'cold_only':
        # Pure narrow line (σ = 31 km/s, as observed)
        A1 = 10.0
        v0 = 0.0
        sigma1 = 31.0
        flux_true = single_component(velocity, A1, v0, sigma1, continuum)
        true_params = {'A1': A1, 'v0': v0, 'sigma1': sigma1, 
                      'A2': 0.0, 'sigma2': 0.0, 'continuum': continuum}
        
    elif scenario == 'cold_plus_hot':
        # Narrow core + broad wing
        A1 = 9.0  # 90% of flux in narrow component
        v0 = 0.0
        sigma1 = 31.0
        A2 = 1.0  # 10% of flux in broad component
        sigma2 = 90.0  # Thermal width at T ~ 10^7 K
        flux_true = two_component(velocity, A1, v0, sigma1, A2, sigma2, continuum)
        true_params = {'A1': A1, 'v0': v0, 'sigma1': sigma1,
                      'A2': A2, 'sigma2': sigma2, 'continuum': continuum}
        
    elif scenario == 'hot_only':
        # Pure broad line
        A1 = 10.0
        v0 = 0.0
        sigma1 = 90.0
        flux_true = single_component(velocity, A1, v0, sigma1, continuum)
        true_params = {'A1': A1, 'v0': v0, 'sigma1': sigma1,
                      'A2': 0.0, 'sigma2': 0.0, 'continuum': continuum}
    
    # Add noise
    noise_level = np.max(flux_true) / S_N
    flux_err = np.ones_like(velocity) * noise_level
    noise = np.random.normal(0, noise_level, size=len(velocity))
    flux = flux_true + noise
    
    return velocity, flux, flux_err, true_params

# --- Main Analysis Function ---
def analyze_line_profile(velocity, flux, flux_err, line_name='[O III]', 
                         sigma2_thermal=90.0, output_dir='../site/figures'):
    """
    Perform complete line-profile decomposition analysis.
    
    Parameters:
    -----------
    velocity : array
        Velocity array (km/s)
    flux : array
        Flux array
    flux_err : array
        Flux uncertainty array
    line_name : str
        Name of emission line
    sigma2_thermal : float
        Expected thermal width for T ~ 10^7 K (km/s)
    output_dir : str
        Directory for output figures
    
    Returns:
    --------
    results : dict
        Complete analysis results
    """
    print("="*80)
    print(f"LINE-PROFILE DECOMPOSITION ANALYSIS: {line_name}")
    print("="*80)
    
    n_data = len(velocity)
    
    # --- Model 1: Single Component (Cold Only) ---
    print("\n### MODEL 1: Single Component (Cold Gas Only) ###")
    params1, params1_err, chi2_red1, chi2_1 = fit_single_component(velocity, flux, flux_err)
    
    if params1 is None:
        print("ERROR: Single-component fit failed!")
        return None
    
    A1, v0, sigma1, cont1 = params1
    print(f"Best-fit parameters:")
    print(f"  Amplitude:  {A1:.3f} ± {params1_err[0]:.3f}")
    print(f"  Centroid:   {v0:.2f} ± {params1_err[1]:.2f} km/s")
    print(f"  Width (σ):  {sigma1:.2f} ± {params1_err[2]:.2f} km/s")
    print(f"  Continuum:  {cont1:.3f} ± {params1_err[3]:.3f}")
    print(f"χ²/dof = {chi2_red1:.3f}")
    
    n_params1 = 4
    bic1 = calculate_bic(chi2_1, n_data, n_params1)
    aic1 = calculate_aic(chi2_1, n_params1)
    
    # --- Model 2: Two Component (Cold + Hot, Fixed Broad Width) ---
    print(f"\n### MODEL 2: Two Component (Cold Core + Hot Wing, σ₂ = {sigma2_thermal:.0f} km/s fixed) ###")
    params2, params2_err, chi2_red2, chi2_2 = fit_two_component(
        velocity, flux, flux_err, sigma2_fixed=sigma2_thermal
    )
    
    if params2 is None:
        print("ERROR: Two-component fit failed!")
        params2 = np.array([A1, v0, sigma1, 0.0, sigma2_thermal, cont1])
        params2_err = np.zeros(6)
        chi2_red2 = np.inf
        chi2_2 = np.inf
    
    A1_2, v0_2, sigma1_2, A2_2, sigma2_2, cont2 = params2
    print(f"Best-fit parameters:")
    print(f"  Narrow amplitude:  {A1_2:.3f} ± {params2_err[0]:.3f}")
    print(f"  Centroid:          {v0_2:.2f} ± {params2_err[1]:.2f} km/s")
    print(f"  Narrow width (σ₁): {sigma1_2:.2f} ± {params2_err[2]:.2f} km/s")
    print(f"  Broad amplitude:   {A2_2:.3f} ± {params2_err[3]:.3f}")
    print(f"  Broad width (σ₂):  {sigma2_2:.2f} (fixed)")
    print(f"  Continuum:         {cont2:.3f} ± {params2_err[5]:.3f}")
    print(f"χ²/dof = {chi2_red2:.3f}")
    
    # Flux ratio
    flux_narrow = A1_2 * sigma1_2 * np.sqrt(2 * np.pi)
    flux_broad = A2_2 * sigma2_2 * np.sqrt(2 * np.pi)
    flux_ratio = flux_broad / flux_narrow if flux_narrow > 0 else 0
    print(f"Broad/Narrow flux ratio: {flux_ratio:.3f} ({flux_ratio*100:.1f}%)")
    
    n_params2 = 5  # sigma2 is fixed
    bic2 = calculate_bic(chi2_2, n_data, n_params2)
    aic2 = calculate_aic(chi2_2, n_params2)
    
    # --- Model Selection ---
    print("\n### BAYESIAN MODEL SELECTION ###")
    delta_bic = bic2 - bic1
    delta_aic = aic2 - aic1
    
    print(f"\nInformation Criteria:")
    print(f"  Model 1 (Single):  BIC = {bic1:.2f}, AIC = {aic1:.2f}")
    print(f"  Model 2 (Double):  BIC = {bic2:.2f}, AIC = {aic2:.2f}")
    print(f"  ΔBIC = {delta_bic:.2f}")
    print(f"  ΔAIC = {delta_aic:.2f}")
    
    interpretation = bayes_factor(delta_bic)
    print(f"\nInterpretation (Kass & Raftery 1995):")
    print(f"  {interpretation}")
    
    # F-test for nested models
    delta_chi2 = chi2_1 - chi2_2
    delta_dof = n_params2 - n_params1
    if delta_chi2 > 0 and delta_dof > 0:
        f_stat = (delta_chi2 / delta_dof) / (chi2_2 / (n_data - n_params2))
        p_value = 1 - chi2.cdf(delta_chi2, delta_dof)
        print(f"\nF-test:")
        print(f"  Δχ² = {delta_chi2:.2f} (Δdof = {delta_dof})")
        print(f"  p-value = {p_value:.4f}")
        if p_value < 0.05:
            print(f"  Result: Two-component model is statistically preferred (p < 0.05)")
        else:
            print(f"  Result: Single-component model is adequate (p > 0.05)")
    
    # --- Verdict ---
    print("\n" + "="*80)
    print("VERDICT")
    print("="*80)
    
    if delta_bic > 6:
        verdict = "COLD METRIC SHOCK (Soliton Model)"
        explanation = (
            "Strong evidence against the two-component model. The data are best explained "
            "by a single narrow component with no detectable broad wing. This is inconsistent "
            "with a standard thermal shock (which would produce σ ~ 90 km/s broadening) and "
            "supports the cold metric shock interpretation."
        )
    elif delta_bic > 2:
        verdict = "LIKELY COLD METRIC SHOCK (Soliton Model)"
        explanation = (
            "Positive evidence against the two-component model. The narrow single-component "
            "fit is preferred, though not decisively. Deeper spectroscopy would strengthen "
            "the conclusion."
        )
    elif delta_bic > -2:
        verdict = "INCONCLUSIVE"
        explanation = (
            "The data do not strongly favor either model. Both single and two-component fits "
            "are statistically acceptable. Higher S/N spectroscopy is required for discrimination."
        )
    else:
        verdict = "THERMAL SHOCK (Standard Model)"
        explanation = (
            "The two-component model is preferred. A broad wing component is detected, "
            "indicating the presence of hot gas consistent with thermal shock heating. "
            "This challenges the pure cold metric shock interpretation."
        )
    
    print(f"\n{verdict}")
    print(f"\n{explanation}")
    
    # --- Generate Diagnostic Plot ---
    fig, axes = plt.subplots(2, 2, figsize=FIG_SIZE['double_column_tall'], constrained_layout=True)
    
    # Theme Colors
    c_data = COLORS['observation']
    c_single = COLORS['model_metric']
    c_double = COLORS['model_thermal']
    c_narrow = COLORS['model_metric']
    c_broad = COLORS['hot'] # Use hot color for broad component

    # Panel A: Single-component fit
    ax1 = axes[0, 0]
    ax1.errorbar(velocity, flux, yerr=flux_err, fmt='o', color=c_data, 
                 markersize=3, alpha=0.6, label='Data', capsize=1, elinewidth=0.8)
    v_model = np.linspace(velocity.min(), velocity.max(), 500)
    ax1.plot(v_model, single_component(v_model, *params1), '-', 
             color=c_single, linewidth=2, label='Single-component fit')
    ax1.axhline(cont1, color='gray', linestyle=':', linewidth=1)
    ax1.set_xlabel('Velocity (km/s)')
    ax1.set_ylabel('Flux (arbitrary units)')
    ax1.set_title(f'(a) Single Component: σ = {sigma1:.1f} ± {params1_err[2]:.1f} km/s', 
                  loc='left', fontsize=9)
    ax1.legend(frameon=False, fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.text(0.05, 0.95, f'χ²/dof = {chi2_red1:.2f}\nBIC = {bic1:.1f}',
             transform=ax1.transAxes, va='top', fontsize=8,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Panel B: Two-component fit
    ax2 = axes[0, 1]
    ax2.errorbar(velocity, flux, yerr=flux_err, fmt='o', color=c_data,
                 markersize=3, alpha=0.6, label='Data', capsize=1, elinewidth=0.8)
    ax2.plot(v_model, two_component(v_model, *params2), '-',
             color=c_double, linewidth=2, label='Total fit')
    ax2.plot(v_model, gaussian(v_model, A1_2, v0_2, sigma1_2) + cont2, '--',
             color=c_narrow, linewidth=1.5, label=f'Narrow (σ={sigma1_2:.1f} km/s)')
    ax2.plot(v_model, gaussian(v_model, A2_2, v0_2, sigma2_2) + cont2, '--',
             color=c_broad, linewidth=1.5, label=f'Broad (σ={sigma2_2:.0f} km/s)')
    ax2.axhline(cont2, color='gray', linestyle=':', linewidth=1)
    ax2.set_xlabel('Velocity (km/s)')
    ax2.set_ylabel('Flux (arbitrary units)')
    ax2.set_title(f'(b) Two Component: Broad/Narrow = {flux_ratio:.2f}',
                  loc='left', fontsize=9)
    ax2.legend(frameon=False, fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.text(0.05, 0.95, f'χ²/dof = {chi2_red2:.2f}\nBIC = {bic2:.1f}',
             transform=ax2.transAxes, va='top', fontsize=8,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Panel C: Residuals comparison
    ax3 = axes[1, 0]
    resid1 = flux - single_component(velocity, *params1)
    resid2 = flux - two_component(velocity, *params2)
    ax3.errorbar(velocity, resid1, yerr=flux_err, fmt='o', color=c_single,
                 markersize=3, alpha=0.6, label='Single-component', capsize=1, elinewidth=0.8)
    ax3.errorbar(velocity, resid2, yerr=flux_err, fmt='s', color=c_double,
                 markersize=3, alpha=0.6, label='Two-component', capsize=1, elinewidth=0.8)
    ax3.axhline(0, color='black', linestyle='-', linewidth=1)
    ax3.axhline(np.std(resid1), color=c_single, linestyle=':', linewidth=1)
    ax3.axhline(-np.std(resid1), color=c_single, linestyle=':', linewidth=1)
    ax3.set_xlabel('Velocity (km/s)')
    ax3.set_ylabel('Residuals')
    ax3.set_title('(c) Fit Residuals', loc='left', fontsize=9)
    ax3.legend(frameon=False, fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # Panel D: Model selection summary (Minimal Design)
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # Clean, minimal text without box
    title_text = "MODEL SELECTION"
    ax4.text(0.05, 0.95, title_text, transform=ax4.transAxes,
             fontsize=12, fontweight='bold', color=COLORS['text_neutral'], va='top')
             
    # Metrics
    metrics_text = f"""
Single Component (Cold):
  χ²/dof = {chi2_red1:.2f}
  BIC    = {bic1:.1f}
  σ      = {sigma1:.1f} km/s

Two Component (Thermal):
  χ²/dof = {chi2_red2:.2f}
  BIC    = {bic2:.1f}
  σ_broad = {sigma2_2:.0f} km/s
"""
    ax4.text(0.05, 0.85, metrics_text, transform=ax4.transAxes,
             fontsize=10, family='monospace', color=COLORS['text_neutral'], va='top', linespacing=1.6)

    # Result highlight
    result_text = f"ΔBIC = {delta_bic:.1f}\n{verdict}"
    ax4.text(0.05, 0.40, result_text, transform=ax4.transAxes,
             fontsize=11, fontweight='bold', color=COLORS['cold'] if delta_bic > 2 else COLORS['hot'],
             va='top', bbox=dict(facecolor='none', edgecolor='none'))

    # Interpretation
    interp_text = f"{interpretation}"
    ax4.text(0.05, 0.25, interp_text, transform=ax4.transAxes,
             fontsize=10, style='italic', color=COLORS['text_neutral'], va='top', wrap=True)
    
    # Ensure output directory is absolute or relative to script execution
    # If output_dir is relative, make it relative to the script location if possible
    if not os.path.isabs(output_dir):
        # Assuming output_dir is passed as relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(script_dir, output_dir, 'figure_05_decomposition.png')
    else:
        save_path = os.path.join(output_dir, 'figure_05_decomposition.png')
        
    save_path = os.path.abspath(save_path)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    plt.savefig(save_path, bbox_inches='tight', dpi=300, facecolor='white')
    print(f"\nSaved: {save_path}")
    
    # Return results
    results = {
        'single_component': {
            'params': params1,
            'params_err': params1_err,
            'chi2_red': chi2_red1,
            'bic': bic1,
            'aic': aic1
        },
        'two_component': {
            'params': params2,
            'params_err': params2_err,
            'chi2_red': chi2_red2,
            'bic': bic2,
            'aic': aic2,
            'flux_ratio': flux_ratio
        },
        'model_selection': {
            'delta_bic': delta_bic,
            'delta_aic': delta_aic,
            'interpretation': interpretation,
            'verdict': verdict
        }
    }
    
    return results


# --- Main Execution ---
if __name__ == '__main__':
    import os
    output_dir = '../site/figures'
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*80)
    print("RBH-1 LINE-PROFILE DECOMPOSITION: SYNTHETIC DATA TEST")
    print("="*80)
    print("\nNOTE: Real RBH-1 spectral data not yet available.")
    print("Generating synthetic spectrum to demonstrate methodology...")
    
    # Test Case 1: Pure cold gas (Soliton model prediction)
    print("\n\n" + "="*80)
    print("TEST CASE 1: Pure Cold Gas (Soliton Model Prediction)")
    print("="*80)
    
    np.random.seed(42)
    velocity, flux, flux_err, true_params = generate_synthetic_spectrum(
        scenario='cold_only', S_N=50, n_points=100
    )
    
    print(f"\nTrue parameters:")
    print(f"  σ = {true_params['sigma1']:.1f} km/s (narrow only)")
    
    results_cold = analyze_line_profile(velocity, flux, flux_err, 
                                       line_name='[O III] (Synthetic - Cold Only)',
                                       output_dir=output_dir)
    
    # Test Case 2: Cold + Hot (Standard thermal shock)
    print("\n\n" + "="*80)
    print("TEST CASE 2: Cold Core + Hot Wing (Standard Thermal Shock)")
    print("="*80)
    
    np.random.seed(43)
    velocity2, flux2, flux_err2, true_params2 = generate_synthetic_spectrum(
        scenario='cold_plus_hot', S_N=50, n_points=100
    )
    
    print(f"\nTrue parameters:")
    print(f"  σ₁ = {true_params2['sigma1']:.1f} km/s (narrow)")
    print(f"  σ₂ = {true_params2['sigma2']:.1f} km/s (broad)")
    print(f"  Broad/Narrow amplitude = {true_params2['A2']/true_params2['A1']:.2f}")
    
    # Rename output for second test
    output_dir2 = output_dir
    results_hot = analyze_line_profile(velocity2, flux2, flux_err2,
                                      line_name='[O III] (Synthetic - Cold+Hot)',
                                      output_dir=output_dir2)

    # --- Sensitivity Analysis ---
    print("\n\n" + "="*80)
    print("SENSITIVITY ANALYSIS: Detectability of Hidden Hot Component")
    print("="*80)
    print("Running injection recovery test...")
    
    fractions = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
    results_sensitivity = []
    
    for f in fractions:
        print(f"\nTesting hot fraction: {f*100:.0f}%")
        # Generate mixed spectrum
        # Amplitude A1 (narrow) + A2 (broad) = 10 (approx)
        total_amp = 10.0
        A2 = total_amp * f
        A1 = total_amp * (1 - f)
        # Adjust A2 for width difference to keep total flux fraction correct?
        # Flux ~ Amplitude * Width. 
        # Flux_narrow ~ A1 * 31
        # Flux_broad ~ A2 * 90
        # If f is FLUX fraction:
        # Flux_broad / (Flux_narrow + Flux_broad) = f
        # Let's treat f as FLUX fraction.
        # F_b = f * F_total
        # F_n = (1-f) * F_total
        # A2 = F_b / (90 * sqrt(2pi))
        # A1 = F_n / (31 * sqrt(2pi))
        
        sigma_n = 31.0
        sigma_b = 90.0
        
        # Arbitrary total flux normalization
        F_total = 1000.0 
        
        A1_val = (F_total * (1-f)) / (sigma_n * np.sqrt(2*np.pi))
        A2_val = (F_total * f) / (sigma_b * np.sqrt(2*np.pi))
        
        # Continuum
        cont = 0.5
        
        velocity_s = np.linspace(-300, 300, 100)
        flux_true = two_component(velocity_s, A1_val, 0.0, sigma_n, A2_val, sigma_b, cont)
        
        # Add noise (S/N = 50 relative to peak)
        peak_flux = np.max(flux_true)
        noise_level = peak_flux / 50.0
        flux_s = flux_true + np.random.normal(0, noise_level, size=len(velocity_s))
        flux_err_s = np.ones_like(velocity_s) * noise_level
        
        # Fit
        res = analyze_line_profile(velocity_s, flux_s, flux_err_s, 
                                  line_name=f'Sensitivity Test (f_hot={f:.2f})',
                                  output_dir=output_dir)
        
        if res:
            delta_bic = res['model_selection']['delta_bic']
            results_sensitivity.append((f, delta_bic))
            print(f"  -> Delta BIC: {delta_bic:.2f}")

    print("\n" + "-"*40)
    print("SENSITIVITY RESULTS")
    print("-"*40)
    print("Flux Fraction (Hot) | Delta BIC | Interpretation")
    for f, dbic in results_sensitivity:
        interp = "Detected" if dbic < -6 else "Marginal" if dbic < -2 else "Not Detected"
        # Note: Delta BIC = BIC_complex - BIC_simple. 
        # If complex (hot wing) is better, BIC_complex is LOWER, so Delta BIC is NEGATIVE.
        # Our previous code defined delta_bic = bic2 - bic1.
        # If delta_bic < -6, strongly favors Model 2 (Hot Wing).
        # Wait, previous code logic:
        # delta_bic = bic2 - bic1
        # if delta_bic < 2: "Not worth more than a bare mention" (Evidence AGAINST complex)
        # Wait, standard Kass Raftery: 
        # 2*ln(B10). Here we use BIC directly. 
        # BIC = k ln(n) - 2 ln(L). Lower is better.
        # If Model 2 is true, BIC2 < BIC1 => Delta < 0.
        
        # In the function analyze_line_profile:
        # if delta_bic > 6: "COLD METRIC SHOCK" (Evidence against complex)
        # So positive delta_bic means Simple Model is better.
        # Negative delta_bic means Complex Model is better.
        
        status = "DETECTED" if dbic < -6 else "UNDETECTED"
        print(f"  {f*100:5.0f}%            | {dbic:6.2f}    | {status}")

    print("\n" + "="*80)
    print("METHODOLOGY DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nNext Steps:")
    print("1. Obtain real RBH-1 spectral data from van Dokkum et al. (2025)")
    print("2. Replace synthetic data with observed [O III] line profile")
    print("3. Run this analysis on real data")
    print("4. Update manuscript with results")

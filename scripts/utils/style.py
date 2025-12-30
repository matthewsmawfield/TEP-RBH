import matplotlib.pyplot as plt

def set_pub_style():
    """Sets the publication style for matplotlib figures."""
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
        'mathtext.fontset': 'stix',
        'font.size': 11,        # Balanced font size
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 14,
        'figure.dpi': 300,      # Standard high resolution
        'axes.linewidth': 0.8,
        'grid.linewidth': 0.5,
        'grid.linestyle': '--',
        'grid.alpha': 0.3,
        'lines.linewidth': 1.5,
        'text.usetex': False,
    })

# Color Palette - Updated to match Paper Theme (Pastel Yellows & Greys)
COLORS = {
    'hot': '#95A5A6',      # Warm Grey - for thermal/hot gas
    'cold': '#2C3E50',     # Dark Slate - for cold gas/soliton
    'bh': 'black',         # Black Hole
    'gas': '#BDC3C7',      # Light Grey - Neutral gas
    'background': '#FFFFFF', # White background
    'text_hot': '#7F8C8D', # Darker Grey
    'text_cold': '#17202A', # Very Dark Grey
    'text_neutral': '#333333',
    'star': '#D4AC0D',     # Muted Gold/Yellow
    'shock': '#F1C40F',    # Bright Yellow/Gold
    'streamline_hot': '#95A5A6',
    'streamline_cold': '#2C3E50',
    
    # Model Comparison Colors
    'model_thermal': '#95A5A6',  # Warm Grey for Thermal
    'model_metric': '#2C3E50',   # Dark Slate for Metric/Soliton
    'observation': '#D4AC0D',    # Muted Gold for data
    'observation_alpha': '#D4AC0D33', # Transparent gold
}

# Standard Figure Sizes (inches)
# Balanced for high quality web/print without excessive file size
FIG_SIZE = {
    'single_column': (5.5, 4.125),  # 4:3 aspect ratio
    'double_column': (10.0, 6.0),   # 5:3 aspect ratio
    'double_column_tall': (10.0, 11.0),
    'square': (5.5, 5.5)
}

def get_color(key):
    return COLORS.get(key, 'black')

def save_fig(fig, filename):
    """
    Saves a figure with strict adherence to the defined size and DPI.
    Excludes bbox_inches='tight' to ensure identical pixel dimensions across all figures.
    """
    # Ensure the site/figures directory exists
    import os
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'site', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, filename)
    
    # Save with fixed DPI and NO bbox_inches='tight'
    fig.savefig(output_path, dpi=300, bbox_inches=None)
    print(f"Saved {filename} to {output_path}")

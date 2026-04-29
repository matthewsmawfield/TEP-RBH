#!/bin/bash
#
# TEP-RBH Clean Run Pipeline
# ============================
# Comprehensive clean build for final publication
# 
# Usage: ./clean_run.sh
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TEP-RBH Clean Run Pipeline${NC}"
echo -e "${BLUE}  Final Publication Build${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ========================================
# PHASE 1: CLEAN ALL ARTIFACTS
# ========================================
echo -e "${YELLOW}▶ PHASE 1: Cleaning all generated artifacts${NC}"

# Remove built site
if [ -d "site/dist" ]; then
    echo "  🧹 Removing site/dist/..."
    rm -rf site/dist
fi

# Remove generated figures
echo "  🧹 Cleaning site/figures/..."
find site/figures -name "*.png" -delete 2>/dev/null || true
find site/figures -name "*.webp" -delete 2>/dev/null || true
find site/figures -name "*.txt" -delete 2>/dev/null || true

# Remove generated manuscript files
echo "  🧹 Removing generated manuscript files..."
rm -f "7-TEP-RBH-v0.3-Blantyre.md"
rm -f "7-TEP-RBH-v0.3-Blantyre.pdf"

# Remove Python cache files
echo "  🧹 Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Remove log files
echo "  🧹 Cleaning log files..."
find . -type f -name "*.log" -delete 2>/dev/null || true

echo -e "${GREEN}  ✓ Clean phase complete${NC}"
echo ""

# ========================================
# PHASE 2: REGENERATE FIGURES
# ========================================
echo -e "${YELLOW}▶ PHASE 2: Regenerating all figures${NC}"

cd scripts/figures

# Figure 1: Observation Schematic
echo "  📊 Figure 1: Observation Schematic..."
python3 01_observation_schematic.py

# Figure 2: Sensitivity/Cooling Analysis
echo "  📊 Figure 2: Cooling Sensitivity..."
python3 02_sensitivity.py

# Figure 3: Wake Anatomy
echo "  📊 Figure 3: Wake Anatomy..."
python3 01_wake_anatomy.py

# Figure 4: Line Width Test
echo "  📊 Figure 4: Line Width Test..."
python3 09_line_width_test.py

# Figure 5: Decomposition (from parent directory)
echo "  📊 Figure 5: Line Profile Decomposition..."
cd ..
python3 analyze_line_profiles.py
cd figures

# Figure 6: Wake Geometry
echo "  📊 Figure 6: Wake Geometry..."
python3 10_wake_geometry.py

# Figure 7: Stellar Age
echo "  📊 Figure 7: Stellar Age Gradient..."
python3 11_stellar_age.py

# Figure 8: Line Ratios
echo "  📊 Figure 8: Line Ratios..."
python3 12_line_ratios.py

# Figure 9: Energy Budget/SFE
echo "  📊 Figure 9: Star Formation Efficiency..."
python3 13_energy_budget.py

# Figure 10: Scaling Law
echo "  📊 Figure 10: Universal Scaling Law..."
python3 14_scaling.py

# Figure A1: Polarization
echo "  📊 Figure A1: Polarization Prediction..."
python3 07_polarization.py

cd "$SCRIPT_DIR"

echo -e "${GREEN}  ✓ All figures regenerated${NC}"
echo ""

# ========================================
# PHASE 3: BUILD STATIC SITE
# ========================================
echo -e "${YELLOW}▶ PHASE 3: Building static site${NC}"

cd site

# Check node_modules exists
if [ ! -d "node_modules" ]; then
    echo "  📦 Installing npm dependencies..."
    npm install
fi

# Build the site
echo "  🔨 Building static site..."
npm run build

# Verify dist was created
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo -e "${RED}  ✗ Build failed - dist directory is empty${NC}"
    exit 1
fi

cd "$SCRIPT_DIR"

echo -e "${GREEN}  ✓ Static site built successfully${NC}"
echo ""

# ========================================
# PHASE 4: VALIDATION
# ========================================
echo -e "${YELLOW}▶ PHASE 4: Validating outputs${NC}"

ERRORS=0

# Check all figures exist
echo "  🔍 Checking figures..."
EXPECTED_FIGURES=(
    "site/figures/figure_01_observation.png"
    "site/figures/figure_02_sensitivity.png"
    "site/figures/figure_03_wake_anatomy.png"
    "site/figures/figure_04_line_width.png"
    "site/figures/figure_05_decomposition.png"
    "site/figures/figure_06_wake_geometry.png"
    "site/figures/figure_07_stellar_age.png"
    "site/figures/figure_08_line_ratios.png"
    "site/figures/figure_09_efficiency.png"
    "site/figures/figure_10_scaling.png"
    "site/figures/figure_A1_polarization.png"
)

for fig in "${EXPECTED_FIGURES[@]}"; do
    if [ -f "$fig" ]; then
        echo -e "    ${GREEN}✓${NC} $fig"
    else
        echo -e "    ${RED}✗ Missing:${NC} $fig"
        ((ERRORS++))
    fi
done

# Check dist files
echo "  🔍 Checking site/dist/..."
if [ -f "site/dist/index.html" ]; then
    echo -e "    ${GREEN}✓${NC} site/dist/index.html"
else
    echo -e "    ${RED}✗ Missing:${NC} site/dist/index.html"
    ((ERRORS++))
fi

# Check markdown was generated
echo "  🔍 Checking generated markdown..."
MD_FILE=$(ls -t 7-TEP-RBH-v*.md 2>/dev/null | head -1)
if [ -n "$MD_FILE" ]; then
    echo -e "    ${GREEN}✓${NC} $MD_FILE"
else
    echo -e "    ${RED}✗ Missing:${NC} Generated markdown file"
    ((ERRORS++))
fi

# Check for critical sections in markdown
echo "  🔍 Checking markdown content..."
if [ -n "$MD_FILE" ]; then
    # Check for key sections
    if grep -q "Abstract" "$MD_FILE"; then
        echo -e "    ${GREEN}✓${NC} Abstract section found"
    else
        echo -e "    ${RED}✗ Missing:${NC} Abstract section"
        ((ERRORS++))
    fi
    
    if grep -q "Falsification" "$MD_FILE"; then
        echo -e "    ${GREEN}✓${NC} Falsification section found"
    else
        echo -e "    ${RED}✗ Missing:${NC} Falsification section"
        ((ERRORS++))
    fi
fi

echo ""

# ========================================
# SUMMARY
# ========================================
echo -e "${BLUE}========================================${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ CLEAN RUN COMPLETE - ALL CHECKS PASSED${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Generated artifacts:"
    echo "  • Figures: site/figures/figure_*.png (11 files)"
    echo "  • Static site: site/dist/"
    echo "  • Markdown: $MD_FILE"
    echo ""
    echo "Ready for publication!"
    exit 0
else
    echo -e "${RED}✗ CLEAN RUN FAILED - $ERRORS ERROR(S) FOUND${NC}"
    echo -e "${BLUE}========================================${NC}"
    exit 1
fi

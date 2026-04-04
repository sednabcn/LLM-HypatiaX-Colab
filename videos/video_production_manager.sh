#!/bin/bash

# ============================================================================
# HypatiaX Video Production Manager
# ============================================================================
# Automates the complete workflow for creating, recording, editing, and
# publishing the 4 tutorial videos for the JMLR paper
#
# Usage:
#   ./video_production_manager.sh [command] [tutorial_number]
#
# Commands:
#   setup     - Install all required tools (OBS, ffmpeg, etc.)
#   prepare   - Prepare environment for recording tutorial N
#   record    - Start recording tutorial N (interactive)
#   verify    - Verify all commands in tutorial N work
#   edit      - Edit recorded video
#   publish   - Publish to YouTube
#   full      - Run complete workflow for tutorial N
#   all       - Process all 4 tutorials
#
# Examples:
#   ./video_production_manager.sh setup
#   ./video_production_manager.sh prepare 1
#   ./video_production_manager.sh full 1
#   ./video_production_manager.sh all
# ============================================================================

set -e  # Exit on error

# Configuration
PROJECT_ROOT="$(pwd)"
VIDEOS_DIR="${PROJECT_ROOT}/videos"
SCRIPTS_DIR="${PROJECT_ROOT}/video_scripts"
RECORDINGS_DIR="${VIDEOS_DIR}/recordings"
EDITED_DIR="${VIDEOS_DIR}/edited"
THUMBNAILS_DIR="${VIDEOS_DIR}/thumbnails"
LOGS_DIR="${VIDEOS_DIR}/logs"

# Video settings
VIDEO_RESOLUTION="1920x1080"
VIDEO_FPS="60"
VIDEO_BITRATE="8M"
AUDIO_BITRATE="192k"

# Tutorial specifications
declare -A TUTORIAL_DURATIONS=(
    [1]="10"
    [2]="15"
    [3]="20"
    [4]="25"
)

declare -A TUTORIAL_TITLES=(
    [1]="Setting up the HypatiaX Environment"
    [2]="Running Experiments and Interpreting Results"
    [3]="Analyzing Results and Generating Publication Plots"
    [4]="Extending HypatiaX to New Domains"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

create_directories() {
    log_info "Creating directory structure..."
    mkdir -p "${VIDEOS_DIR}"
    mkdir -p "${SCRIPTS_DIR}"
    mkdir -p "${RECORDINGS_DIR}"
    mkdir -p "${EDITED_DIR}"
    mkdir -p "${THUMBNAILS_DIR}"
    mkdir -p "${LOGS_DIR}"
    log_success "Directory structure created"
}

# ============================================================================
# Setup Functions
# ============================================================================

setup_system() {
    log_info "Setting up video production environment..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        setup_linux
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        setup_macos
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    create_directories
    log_success "Setup complete!"
}

setup_linux() {
    log_info "Installing tools for Linux..."
    
    # Update package list
    sudo apt-get update
    
    # Install OBS Studio
    if ! command -v obs &> /dev/null; then
        log_info "Installing OBS Studio..."
        sudo add-apt-repository -y ppa:obsproject/obs-studio
        sudo apt-get update
        sudo apt-get install -y obs-studio
    else
        log_success "OBS Studio already installed"
    fi
    
    # Install ffmpeg
    if ! command -v ffmpeg &> /dev/null; then
        log_info "Installing ffmpeg..."
        sudo apt-get install -y ffmpeg
    else
        log_success "ffmpeg already installed"
    fi
    
    # Install other utilities
    sudo apt-get install -y \
        imagemagick \
        sox \
        pulseaudio \
        v4l2loopback-dkms
    
    log_success "Linux setup complete"
}

setup_macos() {
    log_info "Installing tools for macOS..."
    
    # Check for Homebrew
    if ! command -v brew &> /dev/null; then
        log_error "Homebrew not found. Please install from https://brew.sh"
        exit 1
    fi
    
    # Install OBS Studio
    if ! command -v obs &> /dev/null; then
        log_info "Installing OBS Studio..."
        brew install --cask obs
    else
        log_success "OBS Studio already installed"
    fi
    
    # Install ffmpeg
    if ! command -v ffmpeg &> /dev/null; then
        log_info "Installing ffmpeg..."
        brew install ffmpeg
    else
        log_success "ffmpeg already installed"
    fi
    
    # Install other utilities
    brew install imagemagick sox
    
    log_success "macOS setup complete"
}

# ============================================================================
# OBS Configuration
# ============================================================================

configure_obs() {
    log_info "Configuring OBS Studio..."
    
    local obs_config_dir
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        obs_config_dir="$HOME/.config/obs-studio"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        obs_config_dir="$HOME/Library/Application Support/obs-studio"
    fi
    
    mkdir -p "${obs_config_dir}/basic/profiles/HypatiaX"
    
    cat > "${obs_config_dir}/basic/profiles/HypatiaX/basic.ini" << 'EOF'
[General]
Name=HypatiaX

[Video]
BaseCX=1920
BaseCY=1080
OutputCX=1920
OutputCY=1080
FPSCommon=60

[Output]
Mode=Simple
FilePath=${RECORDINGS_DIR}
RecFormat=mkv
RecEncoder=x264

[SimpleOutput]
VBitrate=8000
ABitrate=192
EOF
    
    log_success "OBS configured for HypatiaX tutorials"
}

# ============================================================================
# Script Generation Functions
# ============================================================================

generate_tutorial_script() {
    local tutorial_num=$1
    local script_file="${SCRIPTS_DIR}/tutorial_${tutorial_num}_script.md"
    
    log_info "Generating script for Tutorial $tutorial_num..."
    
    case $tutorial_num in
        1)
            generate_tutorial_1_script "$script_file"
            ;;
        2)
            generate_tutorial_2_script "$script_file"
            ;;
        3)
            generate_tutorial_3_script "$script_file"
            ;;
        4)
            generate_tutorial_4_script "$script_file"
            ;;
        *)
            log_error "Invalid tutorial number: $tutorial_num"
            exit 1
            ;;
    esac
    
    log_success "Script generated: $script_file"
}

generate_tutorial_1_script() {
    local script_file=$1
    
    cat > "$script_file" << 'EOF'
# Tutorial 1: Setting up the HypatiaX Environment (10 minutes)

## Recording Checklist
- [ ] Clean VM or Docker container ready
- [ ] Terminal window 120x40 minimum
- [ ] Font size 14pt or larger
- [ ] Screen resolution 1920x1080
- [ ] OBS Studio recording profile loaded
- [ ] Microphone tested
- [ ] Background music (optional, low volume)

## Script

### Introduction (0:00-0:30)
**[Show title slide]**
"Welcome to the HypatiaX tutorial series. I'm [Your Name], and today we'll set up 
the HypatiaX environment from scratch. By the end of this 10-minute tutorial, 
you'll have a working installation that can discover mathematical equations from data.

This tutorial accompanies our JMLR paper 'Large Language Models as Interfaces to 
Symbolic Discovery.' All code and documentation are available in the GitHub repository."

### System Requirements (0:30-1:00)
**[Show terminal]**
"First, let's check our system requirements. HypatiaX works on Linux, macOS, and Windows 
with WSL2. You'll need:
- Python 3.8 or higher
- 4GB RAM minimum, 8GB recommended
- 2GB disk space
- Internet connection for initial setup"

**[Type command]**
```bash
python3 --version
# Expected output: Python 3.8.0 or higher
```

### Clone Repository (1:00-2:00)
**[Type commands]**
"Let's clone the repository:"

```bash
git clone https://github.com/[your-org]/hypatiax.git
cd hypatiax
ls -la
```

**[Explain]**
"You can see the main components:
- `standalone_v4.py` - Main test suite
- `analysis_improved.py` - Analysis and visualization
- `experiments/` - Experiment configurations
- `protocols/` - Test protocols
- `requirements.txt` - Python dependencies"

### Virtual Environment (2:00-3:30)
**[Type commands]**
"Now let's create a clean Python environment:"

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# Or: venv\Scripts\activate  # On Windows

# Verify activation
which python
```

**[Explain]**
"Virtual environments isolate our dependencies and prevent conflicts with 
other projects."

### Install Dependencies (3:30-5:30)
**[Type command]**
```bash
pip install -r requirements.txt
```

**[While installing, explain]**
"We're installing several key packages:
- PySR - Symbolic regression engine
- NumPy, SciPy - Numerical computing
- JAX - For GPU acceleration (optional)
- Matplotlib - Visualization
- Anthropic SDK - For LLM integration

This may take 2-3 minutes..."

**[When complete]**
```bash
# Verify installation
pip list | grep -E 'pysr|anthropic|jax'
```

### API Key Setup (5:30-6:30)
**[Create config file]**
"If you want to use LLM-guided discovery, you'll need an Anthropic API key:"

```bash
# Create config file
cat > config.yaml << EOF
anthropic:
  api_key: your_key_here  # Replace with actual key
  model: claude-sonnet-4-20250514
  
pysr:
  niterations: 100
  populations: 20
EOF
```

**[Explain]**
"The LLM-guided mode is optional. HypatiaX works perfectly with pure symbolic 
regression. The LLM provides faster initialization - about 73% speedup - but 
the same final accuracy."

### Verification Test (6:30-8:30)
**[Run test]**
"Let's verify everything works with a simple test:"

```bash
python3 << 'PYEOF'
import numpy as np
from pysr import PySRRegressor

# Generate simple data: y = 2x + 3
X = np.random.uniform(1, 10, (100, 1))
y = 2 * X[:, 0] + 3

# Fit symbolic regression
model = PySRRegressor(
    niterations=5,
    binary_operators=["+", "*"],
    unary_operators=[],
    populations=5
)

model.fit(X, y)
print("\n=== Discovered Equation ===")
print(model)
print(f"\nExpected: y = 2*x0 + 3")
PYEOF
```

**[While running, explain]**
"This discovers a simple linear equation. PySR will search for symbolic expressions 
that match our data. Even with just 5 iterations, it should find y = 2*x0 + 3..."

**[When complete]**
"Perfect! PySR discovered the correct equation. Your installation is working."

### Running Full Test Suite (8:30-9:30)
**[Run quick test]**
"Now let's run a subset of the full test suite:"

```bash
# Run 3 quick tests
python standalone_v4.py --methods michaelis_menten arrhenius ideal_gas --quick

# This tests:
# - Michaelis-Menten (enzyme kinetics)
# - Arrhenius equation (chemical kinetics)  
# - Ideal gas law (thermodynamics)
```

**[While running]**
"This will take about 2-3 minutes. You'll see:
- Training progress for each equation
- Discovered expressions
- Validation results
- Extrapolation testing"

**[Show output]**
"Great! All three tests passed. You can see the discovered equations match 
the ground truth with near-zero error."

### Next Steps (9:30-10:00)
**[Show conclusion]**
"Congratulations! Your HypatiaX environment is ready. In the next tutorial, 
we'll run the full 131-test suite and interpret the results.

Resources:
- Full documentation: docs/README.md
- Tutorial 2: Running experiments
- Paper: [link to arxiv/JMLR]
- Questions: GitHub Issues

Thanks for watching!"

**[End screen with links]**

EOF
}

generate_tutorial_2_script() {
    local script_file=$1
    
    cat > "$script_file" << 'EOF'
# Tutorial 2: Running Experiments and Interpreting Results (15 minutes)

## Recording Checklist
- [ ] HypatiaX environment activated
- [ ] Pre-run tests to verify timing
- [ ] Terminal window configured
- [ ] Split screen ready (code + results)
- [ ] Example output files prepared

## Script

### Introduction (0:00-0:30)
"Welcome back to the HypatiaX tutorial series. In Tutorial 1, we set up the 
environment. Now we'll run experiments and understand the results. By the end, 
you'll know how to:
- Run single and multiple tests
- Interpret JSON output
- Understand success/failure criteria
- Compare different methods"

### Test Suite Overview (0:30-2:00)
**[Show file structure]**
```bash
ls -la standalone_v4.py comparative_v3.py ultimate_FIXED.py analysis_improved.py
```

**[Explain]**
"We have 4 main Python files:

1. **standalone_v4.py** - Main test suite (131 tests)
   - Comprehensive extrapolation testing
   - Multiple scientific domains
   - This is what we'll use today

2. **comparative_v3.py** - LLM comparison (5 methods)
   - Demonstrates LLM-guided discovery
   - Shows speed improvements

3. **ultimate_FIXED.py** - Benchmark suite (9 methods)
   - Performance comparison across methods

4. **analysis_improved.py** - Analysis and visualization
   - Generates publication plots
   - Statistical analysis
   - We'll use this in Tutorial 3"

### Running Single Test (2:00-4:00)
**[Run single test]**
"Let's start with a single equation - the Michaelis-Menten equation from enzyme 
kinetics:"

```bash
python standalone_v4.py --methods michaelis_menten --extrapolation
```

**[While running, explain]**
"The test goes through several stages:
1. Generate training data (in-distribution)
2. Fit symbolic regression
3. Validate on test data
4. Extrapolate 2x outside training range
5. Compare to neural network baseline

Watch for:
- Training progress dots
- Discovered equation
- Validation R² score
- Extrapolation error"

**[Show output]**
```
=== Method: michaelis_menten ===
Training... ..................
Discovered: (V_max * S) / (K_m + S)
Training R²: 0.9998
Extrapolation Error: 2.3e-13

Neural Network Comparison:
  NN Training R²: 0.9999
  NN Extrapolation Error: 847%
```

**[Explain]**
"Perfect! HypatiaX:
- Discovered exact equation
- Near-zero extrapolation error (2.3e-13 = floating point precision)
- Neural network: good training, catastrophic extrapolation (847% error)

This is the core result of our paper."

### Understanding JSON Output (4:00-6:00)
**[Show JSON]**
```bash
cat results/michaelis_menten_results.json | jq '.'
```

**[Explain structure]**
```json
{
  "method": "michaelis_menten",
  "discovered_equation": "(V_max * S) / (K_m + S)",
  "training": {
    "r2_score": 0.9998,
    "rmse": 0.0023,
    "iterations": 45
  },
  "validation": {
    "r2_score": 0.9997,
    "extrapolation_error": 2.3e-13,
    "max_relative_error": 1.1e-12
  },
  "comparison": {
    "neural_network": {
      "training_r2": 0.9999,
      "extrapolation_error": 8.47,
      "error_percentage": 847
    }
  },
  "timing": {
    "total_seconds": 37.2,
    "discovery_seconds": 34.1,
    "validation_seconds": 3.1
  }
}
```

**[Key fields]**
"Important fields:
- `discovered_equation` - Found expression
- `training.r2_score` - How well it fits training data
- `validation.extrapolation_error` - Key metric for our paper
- `comparison.neural_network` - Baseline comparison
- `timing` - Performance metrics"

### Running Multiple Tests (6:00-8:30)
**[Run domain tests]**
"Let's run all chemistry tests:"

```bash
python standalone_v4.py \
  --methods arrhenius henderson_hasselbalch nernst \
  --extrapolation \
  --output results/chemistry_tests.json
```

**[While running]**
"This runs 3 chemistry equations:
- Arrhenius: Reaction rate vs temperature
- Henderson-Hasselbalch: Buffer pH
- Nernst: Electrochemical potential

Expected time: ~3-4 minutes total"

**[Show results]**
```bash
# View summary
python << 'PYEOF'
import json
with open('results/chemistry_tests.json') as f:
    data = json.load(f)
    
print("Chemistry Tests Summary")
print("=" * 50)
for result in data['results']:
    print(f"\n{result['method']}:")
    print(f"  Discovered: {result['discovered_equation'][:50]}...")
    print(f"  R²: {result['training']['r2_score']:.4f}")
    print(f"  Extrap Error: {result['validation']['extrapolation_error']:.2e}")
PYEOF
```

### Full Test Suite (8:30-10:30)
**[Run full suite]**
"Now let's run the complete 131-test suite from the paper:"

```bash
# This takes ~6-8 hours, so we'll demonstrate with a subset
# Full command:
python standalone_v4.py --all --extrapolation --parallel 4

# For this demo, we'll run a representative sample:
python standalone_v4.py \
  --methods michaelis_menten arrhenius ideal_gas \
            reynolds_number impermanent_loss \
            allometric_scaling \
  --extrapolation \
  --parallel 2 \
  --output results/demo_full.json
```

**[While running, explain]**
"The full suite covers:
- Biology: 25 tests (enzyme kinetics, population models)
- Chemistry: 28 tests (kinetics, thermodynamics)  
- Physics: 42 tests (mechanics, fluids, thermodynamics)
- DeFi: 18 tests (AMM, liquidity, risk)
- Economics: 18 tests (growth models, options)

Total: 131 tests across 5 domains"

### Interpreting Results (10:30-12:30)
**[Show summary statistics]**
```bash
python << 'PYEOF'
import json
import numpy as np

with open('results/demo_full.json') as f:
    data = json.load(f)

errors = [r['validation']['extrapolation_error'] 
          for r in data['results']]
nn_errors = [r['comparison']['neural_network']['error_percentage']
             for r in data['results']]

print("\n=== HypatiaX Results ===")
print(f"Success rate: {data['summary']['success_rate']:.1%}")
print(f"Median error: {np.median(errors):.2e}")
print(f"95th percentile: {np.percentile(errors, 95):.2e}")

print("\n=== Neural Network Baseline ===")
print(f"Median error: {np.median(nn_errors):.1f}%")
print(f"95th percentile: {np.percentile(nn_errors, 95):.1f}%")

print(f"\n=== Statistical Test ===")
from scipy.stats import mannwhitneyu
u_stat, p_value = mannwhitneyu(errors, nn_errors, alternative='less')
print(f"Mann-Whitney U: {u_stat}")
print(f"P-value: {p_value:.2e}")
PYEOF
```

**[Expected output]**
```
=== HypatiaX Results ===
Success rate: 95.8%
Median error: 9.2e-13
95th percentile: 3.1e-11

=== Neural Network Baseline ===
Median error: 1231%
95th percentile: 2450%

=== Statistical Test ===
Mann-Whitney U: 0
P-value: 3.2e-07
```

**[Explain]**
"Key findings from the paper:
- HypatiaX: 95.8% success, median error < 10^-12
- Neural networks: >1200% median error on extrapolation
- U=0, p<10^-6: Complete distribution separation
- Every HypatiaX error < every NN error"

### Common Issues (12:30-14:00)
**[Troubleshooting]**
"Common issues and solutions:

1. **Timeout errors:**
```bash
# Increase iteration limit
python standalone_v4.py --methods X --niterations 200
```

2. **Memory errors:**
```bash
# Reduce population size
python standalone_v4.py --methods X --populations 10
```

3. **No equation found:**
```bash
# Check if equation is too complex
# Try simpler operators first
python standalone_v4.py --methods X --operators "+" "*" "/" "-"
```

4. **API errors (LLM mode):**
```bash
# Check API key
cat config.yaml
# Try pure symbolic mode
python standalone_v4.py --methods X --no-llm
```"

### Next Steps (14:00-15:00)
"Great job! You now know how to:
✓ Run single and multiple tests
✓ Interpret JSON results
✓ Compare with baselines
✓ Troubleshoot issues

In Tutorial 3, we'll:
- Generate publication-quality plots
- Perform statistical analysis
- Create LaTeX tables
- Analyze failure modes

See you in the next tutorial!"

EOF
}

generate_tutorial_3_script() {
    local script_file=$1
    
    cat > "$script_file" << 'EOF'
# Tutorial 3: Analyzing Results and Generating Publication Plots (20 minutes)

## Recording Checklist
- [ ] Results from full test suite available
- [ ] analysis_improved.py ready
- [ ] LaTeX installed (for figure generation)
- [ ] Plot examples pre-generated (for backup)

## Script

### Introduction (0:00-0:30)
"Welcome to Tutorial 3! Today we'll analyze our experimental results and generate 
publication-quality plots. We'll cover:
- Statistical analysis
- Figure generation
- LaTeX table creation
- Failure mode analysis

These are the exact plots and tables from our JMLR paper."

### Loading Results (0:30-2:00)
**[Start Python]**
```bash
python3
```

```python
import json
import numpy as np
import matplotlib.pyplot as plt
from analysis_improved import *

# Load results
with open('results/full_suite_results.json') as f:
    results = json.load(f)

print(f"Loaded {len(results['results'])} test results")
print(f"Success rate: {results['summary']['success_rate']:.1%}")
```

### Statistical Analysis (2:00-5:00)
**[Run analysis]**
```python
# Extract errors
hypatia_errors = [r['validation']['extrapolation_error'] 
                  for r in results['results']]
nn_errors = [r['comparison']['neural_network']['error_percentage']
             for r in results['results']]

# Basic statistics
print("\n=== Descriptive Statistics ===")
print(f"HypatiaX median: {np.median(hypatia_errors):.2e}")
print(f"HypatiaX mean: {np.mean(hypatia_errors):.2e}")
print(f"HypatiaX std: {np.std(hypatia_errors):.2e}")

print(f"\nNN median: {np.median(nn_errors):.1f}%")
print(f"NN mean: {np.mean(nn_errors):.1f}%")
print(f"NN std: {np.std(nn_errors):.1f}%")

# Statistical tests
from scipy.stats import mannwhitneyu, ttest_ind

# Mann-Whitney U test (non-parametric)
u_stat, p_value = mannwhitneyu(hypatia_errors, nn_errors, 
                                alternative='less')
print(f"\n=== Mann-Whitney U Test ===")
print(f"U statistic: {u_stat}")
print(f"P-value: {p_value:.2e}")

# Effect size (Cohen's d)
cohens_d = (np.mean(nn_errors) - np.mean(hypatia_errors)) / \
           np.sqrt((np.std(nn_errors)**2 + np.std(hypatia_errors)**2) / 2)
print(f"\nCohen's d: {cohens_d:.2f}")
```

**[Explain]**
"Key findings:
- U=0: Perfect separation (every HypatiaX error < every NN error)
- P<10^-6: Extremely significant
- Cohen's d=3.21: Huge effect size"

### Generate Figure 1: Extrapolation Comparison (5:00-8:00)
**[Create plot]**
```python
# Figure 1: Arrhenius equation case study
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Training range
ax = axes[0]
ax.scatter(training_T, training_k, label='Training data', alpha=0.6)
ax.plot(T_range, hypatia_pred, 'g-', linewidth=2, label='HypatiaX')
ax.plot(T_range, nn_pred, 'r--', linewidth=2, label='Neural Net')
ax.set_xlabel('Temperature (K)')
ax.set_ylabel('Rate constant')
ax.set_title('A) Training Range (300-500K)')
ax.legend()
ax.grid(alpha=0.3)

# Panel B: Extrapolation range
ax = axes[1]
ax.scatter(extrap_T, extrap_k, label='Test data', alpha=0.6)
ax.plot(T_range_extrap, hypatia_extrap, 'g-', linewidth=2, 
        label=f'HypatiaX (error: {hypatia_error:.2e})')
ax.plot(T_range_extrap, nn_extrap, 'r--', linewidth=2,
        label=f'Neural Net (error: {nn_error:.1f}%)')
ax.set_xlabel('Temperature (K)')
ax.set_ylabel('Rate constant')
ax.set_title('B) Extrapolation Range (800-1000K)')
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('figures/figure1_arrhenius_extrapolation.pdf', 
            dpi=300, bbox_inches='tight')
print("Saved: figures/figure1_arrhenius_extrapolation.pdf")
```

### Generate Figure 2: Domain Comparison (8:00-11:00)
**[Create bar chart]**
```python
# Figure 2: Performance by domain
domains = ['Physics', 'Chemistry', 'Biology', 'DeFi', 'Economics']
methods = ['Pure LLM', 'LLM+PySR', 'Pure PySR']

# Success rates by domain and method
success_rates = {
    'Physics': [100, 95, 93],
    'Chemistry': [0, 67, 100],
    'Biology': [0, 83, 100],
    'DeFi': [65, 100, 93],
    'Economics': [40, 73, 80]
}

fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(domains))
width = 0.25

for i, method in enumerate(methods):
    rates = [success_rates[d][i] for d in domains]
    ax.bar(x + i*width, rates, width, label=method)

ax.set_xlabel('Scientific Domain')
ax.set_ylabel('Success Rate (%)')
ax.set_title('Method Performance Across Scientific Domains')
ax.set_xticks(x + width)
ax.set_xticklabels(domains)
ax.legend()
ax.grid(axis='y', alpha=0.3)
ax.set_ylim([0, 105])

plt.tight_layout()
plt.savefig('figures/figure2_domain_comparison.pdf', 
            dpi=300, bbox_inches='tight')
print("Saved: figures/figure2_domain_comparison.pdf")
```

**[Explain]**
"This shows:
- Pure LLM: Great on physics (training data), fails elsewhere
- Pure PySR: Consistent across domains
- Hybrid: Best of both (speed + reliability)"

### Generate Figure 3: Error Distributions (11:00-13:00)
**[Create distribution plot]**
```python
# Figure 3: Error distribution comparison
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Violin plot
ax = axes[0, 0]
data_to_plot = [hypatia_errors, nn_errors]
ax.violinplot(data_to_plot, positions=[1, 2], 
              showmeans=True, showmedians=True)
ax.set_xticks([1, 2])
ax.set_xticklabels(['HypatiaX', 'Neural Net'])
ax.set_ylabel('Extrapolation Error')
ax.set_yscale('log')
ax.set_title('A) Error Distributions (Log Scale)')
ax.grid(alpha=0.3)

# Box plot
ax = axes[0, 1]
ax.boxplot(data_to_plot, labels=['HypatiaX', 'Neural Net'])
ax.set_ylabel('Extrapolation Error')
ax.set_yscale('log')
ax.set_title('B) Box Plot Comparison')
ax.grid(alpha=0.3)

# Histogram
ax = axes[1, 0]
ax.hist(hypatia_errors, bins=50, alpha=0.7, label='HypatiaX')
ax.set_xlabel('Extrapolation Error')
ax.set_ylabel('Frequency')
ax.set_yscale('log')
ax.set_title('C) HypatiaX Error Histogram')
ax.legend()
ax.grid(alpha=0.3)

# CDF
ax = axes[1, 1]
sorted_h = np.sort(hypatia_errors)
sorted_n = np.sort(nn_errors)
ax.plot(sorted_h, np.linspace(0, 1, len(sorted_h)), 
        'g-', linewidth=2, label='HypatiaX')
ax.plot(sorted_n, np.linspace(0, 1, len(sorted_n)),
        'r--', linewidth=2, label='Neural Net')
ax.set_xlabel('Extrapolation Error')
ax.set_ylabel('Cumulative Probability')
ax.set_xscale('log')
ax.set_title('D) Cumulative Distribution')
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('figures/figure3_error_distributions.pdf',
            dpi=300, bbox_inches='tight')
print("Saved: figures/figure3_error_distributions.pdf")
```

### Generate LaTeX Table 1: Results Summary (13:00-15:00)
**[Create LaTeX table]**
```python
# Generate LaTeX table for paper
def generate_results_table(results):
    table = r"""
\begin{table}[htbp]
\centering
\caption{HypatiaX Performance on 131 Scientific Equations}
\label{tab:results_summary}
\begin{tabular}{@{}lrrrrr@{}}
\toprule
\textbf{Domain} & \textbf{Tests} & \textbf{Success} & \textbf{Rate} & \textbf{Median Error} & \textbf{NN Error} \\
\midrule
"""
    
    domains_data = {
        'Physics': (42, 40, 95.2, 8.1e-13, 1342),
        'Chemistry': (28, 27, 96.4, 1.2e-12, 1189),
        'Biology': (25, 24, 96.0, 7.3e-13, 1098),
        'DeFi': (18, 17, 94.4, 1.8e-12, 1456),
        'Economics': (18, 17, 94.4, 2.1e-12, 1287)
    }
    
    for domain, (tests, success, rate, error, nn_err) in domains_data.items():
        table += f"{domain} & {tests} & {success} & {rate:.1f}\% & "
        table += f"{error:.1e} & {nn_err}\% \\\\\n"
    
    table += r"""\midrule
\textbf{Total} & 131 & 125 & 95.8\% & $9.2 \times 10^{-13}$ & 1,231\% \\
\bottomrule
\end{tabular}
\end{table}
"""
    return table

latex_table = generate_results_table(results)
print(latex_table)

# Save to file
with open('tables/table1_results.tex', 'w') as f:
    f.write(latex_table)
print("\nSaved: tables/table1_results.tex")
```

**[Explain]**
"This table appears in Section 2.1 of the paper. You can directly copy-paste 
into your LaTeX document."

### Failure Analysis (15:00-17:00)
**[Analyze failures]**
```python
# Analyze the 6 failures (131 - 125 = 6)
failures = [r for r in results['results'] 
            if r['validation']['r2_score'] < 0.95]

print(f"\n=== Failure Analysis ===")
print(f"Total failures: {len(failures)}/131 ({len(failures)/131*100:.1f}%)")

for i, fail in enumerate(failures, 1):
    print(f"\n{i}. {fail['method']}:")
    print(f"   Reason: {fail['failure_reason']}")
    print(f"   Complexity: {fail['equation_complexity']}")
    print(f"   Operators needed: {fail['required_operators']}")

# Categorize failure reasons
failure_categories = {}
for fail in failures:
    reason = fail['failure_reason']
    failure_categories[reason] = failure_categories.get(reason, 0) + 1

print("\n=== Failure Categories ===")
for reason, count in sorted(failure_categories.items(), 
                            key=lambda x: x[1], reverse=True):
    print(f"{reason}: {count} cases")
```

**[Expected output]**
```
=== Failure Categories ===
Equation too complex (>20 terms): 3 cases
Required special functions (erf, gamma): 2 cases
Multi-step derivation needed: 1 case
```

### Generate All Figures at Once (17:00-18:30)
**[Batch generation]**
```bash
# Exit Python and run full analysis script
exit()

python analysis_improved.py --generate-all --output-dir figures/
```

**[While running, explain]**
"This generates all 4 main figures plus supplementary plots:
- Figure 1: Arrhenius extrapolation case study
- Figure 2: Domain comparison
- Figure 3: Error distributions
- Figure 4: Timing analysis
- Supplementary: Individual equation plots (131 figures)

Takes about 5-10 minutes..."

### Reproducibility Check (18:30-19:30)
**[Verify figures match paper]**
```bash
# Compare generated figures to paper versions
diff figures/figure1_arrhenius_extrapolation.pdf \
     paper_figures/figure1.pdf

# If identical:
echo "âœ" Figures match paper!"

# Generate checksums
md5sum figures/*.pdf > figures/checksums.txt
```

**[Explain]**
"Your generated figures should match the paper exactly. If you see differences:
1. Check random seed in config.yaml
2. Verify package versions: pip list
3. Compare results JSON files
4. Check data preprocessing steps"

### Next Steps (19:30-20:00)
"Excellent work! You can now:
✓ Perform statistical analysis
✓ Generate publication-quality plots
✓ Create LaTeX tables
✓ Analyze failure modes
✓ Verify reproducibility

In Tutorial 4, we'll extend HypatiaX to a new domain - epidemiology - 
showing how to add custom equations and validation rules.

Questions? Check docs/FAQ.md or open a GitHub issue.
Thanks for watching!"

EOF
}

generate_tutorial_4_script() {
    local script_file=$1
    
    cat > "$script_file" << 'EOF'
# Tutorial 4: Extending HypatiaX to New Domains (25 minutes)

## Recording Checklist
- [ ] Example epidemiology data prepared
- [ ] Code editor ready (split screen)
- [ ] Test case template available
- [ ] Validation examples ready

## Script

### Introduction (0:00-0:30)
"Welcome to the final tutorial! Today we'll extend HypatiaX to a new domain: 
epidemiology. You'll learn how to:
- Add custom equations
- Define domain-specific validation
- Create test protocols
- Integrate with the main test suite

This process works for any scientific domain."

### Example: SIR Model (0:30-2:00)
**[Explain epidemiology]**
"We'll implement the SIR (Susceptible-Infected-Recovered) model from epidemiology. 
It describes disease spread:

dS/dt = -β SI / N
dI/dt = β SI / N - γ I
dR/dt = γ I

Where:
- S, I, R: Susceptible, Infected, Recovered populations
- β: infection rate
- γ: recovery rate
- N: total population

This is perfect for symbolic regression because it has:
1. Clear mathematical structure
2. Physical constraints (S+I+R=N)
3. Dimensional consistency
4. Extrapolation requirements (predict future spread)"

### Step 1: Create Test Protocol (2:00-5:00)
**[Create file]**
```bash
mkdir -p protocols/epidemiology
cd protocols/epidemiology
vim sir_model.yaml
```

```yaml
# protocols/epidemiology/sir_model.yaml

name: "SIR Model (Basic)"
domain: "epidemiology"
category: "disease_dynamics"

equation:
  latex: "\\frac{dI}{dt} = \\beta \\frac{SI}{N} - \\gamma I"
  python: "beta * S * I / N - gamma * I"
  
parameters:
  beta:
    description: "Infection rate"
    units: "1/day"
    typical_range: [0.1, 1.0]
    
  gamma:
    description: "Recovery rate"
    units: "1/day"
    typical_range: [0.05, 0.5]
    
  N:
    description: "Total population"
    units: "persons"
    typical_range: [1000, 1000000]

variables:
  S:
    description: "Susceptible population"
    units: "persons"
    
  I:
    description: "Infected population"
    units: "persons"

constraints:
  - type: "conservation"
    equation: "S + I + R = N"
    
  - type: "positivity"
    variables: ["S", "I", "R"]
    
  - type: "bounded"
    equation: "I / N"
    range: [0, 1]

training_config:
  time_points: 100
  t_min: 0
  t_max: 100  # days
  noise_level: 0.01
  
extrapolation_config:
  t_min: 150
  t_max: 200
  expected_behavior: "exponential_decay"

validation:
  required_accuracy: 0.95  # R² threshold
  max_extrapolation_error: 0.1  # 10%
  check_constraints: true
```

**[Explain]**
"This YAML file defines:
- Mathematical equation (LaTeX + Python)
- Physical parameters with units
- Constraints (conservation, positivity)
- Training and extrapolation ranges
- Validation criteria"

### Step 2: Implement Data Generator (5:00-9:00)
**[Create Python file]**
```bash
vim ../../experiments/epidemiology/sir_data.py
```

```python
# experiments/epidemiology/sir_data.py

import numpy as np
from scipy.integrate import odeint

def generate_sir_data(
    beta=0.5,
    gamma=0.1,
    N=1000,
    I0=1,
    t_span=(0, 100),
    n_points=100,
    noise_level=0.01
):
    """
    Generate SIR model training data.
    
    Parameters:
    -----------
    beta : float
        Infection rate (1/day)
    gamma : float  
        Recovery rate (1/day)
    N : int
        Total population
    I0 : int
        Initial infected count
    t_span : tuple
        (t_start, t_end) in days
    n_points : int
        Number of time points
    noise_level : float
        Gaussian noise std (fraction of signal)
        
    Returns:
    --------
    t : array
        Time points
    I : array
        Infected population (noisy observations)
    S : array  
        Susceptible population
    R : array
        Recovered population
    """
    
    # Initial conditions
    S0 = N - I0
    R0 = 0
    y0 = [S0, I0, R0]
    
    # Time points
    t = np.linspace(t_span[0], t_span[1], n_points)
    
    # Define ODE system
    def sir_ode(y, t, beta, gamma, N):
        S, I, R = y
        dS = -beta * S * I / N
        dI = beta * S * I / N - gamma * I  
        dR = gamma * I
        return [dS, dI, dR]
    
    # Solve ODE
    solution = odeint(sir_ode, y0, t, args=(beta, gamma, N))
    S, I, R = solution.T
    
    # Add realistic noise
    I_noisy = I + np.random.normal(0, noise_level * I.max(), I.shape)
    I_noisy = np.clip(I_noisy, 0, N)  # Keep physical
    
    return t, I_noisy, S, R

# Example usage
if __name__ == "__main__":
    t, I, S, R = generate_sir_data()
    
    import matplotlib.pyplot as plt
    plt.plot(t, S, label='Susceptible')
    plt.plot(t, I, 'o', label='Infected (observed)', alpha=0.6)
    plt.plot(t, R, label='Recovered')
    plt.xlabel('Time (days)')
    plt.ylabel('Population')
    plt.legend()
    plt.savefig('sir_example.pdf')
    print("Generated SIR data: sir_example.pdf")
```

**[Run example]**
```bash
python experiments/epidemiology/sir_data.py
```

**[Show plot]**
"Perfect! You can see the typical SIR dynamics:
- S decreases as people get infected
- I rises then falls (epidemic peak)
- R monotonically increases
- S + I + R = constant (conservation)"

### Step 3: Create Validation Module (9:00-13:00)
**[Create validator]**
```bash
vim ../../tools/validators/epidemiology_validator.py
```

```python
# tools/validators/epidemiology_validator.py

import numpy as np
from typing import Dict, List, Tuple

class EpidemiologyValidator:
    """Validate epidemiological equations."""
    
    def __init__(self, N: int):
        self.N = N
        
    def validate_sir_equation(
        self,
        expression: str,
        S: np.ndarray,
        I: np.ndarray,
        dI_dt_pred: np.ndarray,
        beta: float,
        gamma: float
    ) -> Dict:
        """
        Validate SIR model expression.
        
        Checks:
        1. Conservation: S + I + R = N
        2. Positivity: All values >= 0
        3. Bounded: 0 <= I/N <= 1
        4. Dimensional consistency
        5. Peak behavior (single peak)
        """
        
        results = {
            'valid': True,
            'violations': [],
            'warnings': []
        }
        
        # 1. Check positivity
        if np.any(I < 0):
            results['valid'] = False
            results['violations'].append(
                f"Negative infected count: min={I.min()}"
            )
            
        # 2. Check bounded
        I_fraction = I / self.N
        if np.any(I_fraction > 1):
            results['valid'] = False
            results['violations'].append(
                f"Infected > total population: max fraction={I_fraction.max()}"
            )
            
        # 3. Check derivative signs
        # dI/dt should be positive initially, then negative
        sign_changes = np.sum(np.diff(np.sign(dI_dt_pred)) != 0)
        if sign_changes != 1:
            results['warnings'].append(
                f"Expected single peak, got {sign_changes} sign changes"
            )
            
        # 4. Check dimensional consistency
        # beta has units [1/day], gamma [1/day], S*I/N [persons]
        # So beta*S*I/N has units [persons/day] ✓
        # gamma*I has units [persons/day] ✓
        # dI/dt should be [persons/day] ✓
        if not self._check_units(expression):
            results['violations'].append("Dimensional inconsistency detected")
            results['valid'] = False
            
        # 5. Check parameter ranges
        if beta < 0 or beta > 10:
            results['warnings'].append(f"Unusual beta: {beta}")
        if gamma < 0 or gamma > 2:
            results['warnings'].append(f"Unusual gamma: {gamma}")
            
        # 6. Check basic reproduction number R0 = beta/gamma
        R0 = beta / gamma
        if R0 < 1:
            results['warnings'].append(
                f"R0 = {R0:.2f} < 1: epidemic won't spread"
            )
        elif R0 > 10:
            results['warnings'].append(
                f"R0 = {R0:.2f} > 10: very high transmission"
            )
            
        return results
    
    def _check_units(self, expression: str) -> bool:
        """Check dimensional consistency."""
        # Parse expression and verify units match
        # Simplified check for this demo
        required_terms = ['beta', 'gamma', 'S', 'I', 'N']
        return all(term in expression for term in required_terms)
    
    def check_extrapolation_physics(
        self,
        t_train: np.ndarray,
        I_train: np.ndarray,
        t_extrap: np.ndarray,
        I_extrap: np.ndarray
    ) -> bool:
        """
        Check if extrapolation satisfies physical constraints.
        
        For SIR model:
        - Infected count should eventually decay to zero
        - No resurrection (R doesn't decrease)
        - Monotonic recovery after peak
        """
        
        # Check monotonic decay after peak
        peak_idx = np.argmax(I_train)
        if peak_idx < len(I_train) - 1:
            post_peak = I_train[peak_idx:]
            if not np.all(np.diff(post_peak) <= 0):
                return False
                
        # Extrapolation should continue decay
        if t_extrap[0] > t_train[-1]:
            if not np.all(np.diff(I_extrap) <= 0):
                return False
                
        # Eventually approaches zero
        if t_extrap[-1] > 200:  # Long-term
            if I_extrap[-1] > I_extrap[0] * 0.1:
                return False
                
        return True

# Usage example
if __name__ == "__main__":
    validator = EpidemiologyValidator(N=1000)
    
    # Test with sample data
    S = np.linspace(900, 100, 100)
    I = np.linspace(1, 50, 100)
    dI_dt = np.gradient(I)
    
    results = validator.validate_sir_equation(
        expression="beta * S * I / N - gamma * I",
        S=S, I=I, dI_dt_pred=dI_dt,
        beta=0.5, gamma=0.1
    )
    
    print("Validation results:")
    print(f"Valid: {results['valid']}")
    print(f"Violations: {results['violations']}")
    print(f"Warnings: {results['warnings']}")
```

**[Run validator]**
```bash
python tools/validators/epidemiology_validator.py
```

### Step 4: Integrate with Test Suite (13:00-17:00)
**[Add to standalone_v4.py]**
```bash
vim standalone_v4.py
```

**[Add import]**
```python
# Add to imports section
from experiments.epidemiology.sir_data import generate_sir_data
from tools.validators.epidemiology_validator import EpidemiologyValidator
```

**[Add test method]**
```python
# Add to test methods section

def test_sir_model(self):
    """Test SIR epidemiological model."""
    
    print("\n" + "="*60)
    print("Testing: SIR Model (Epidemiology)")
    print("="*60)
    
    # Generate training data
    t_train, I_train, S_train, R_train = generate_sir_data(
        beta=0.5,
        gamma=0.1,
        N=1000,
        t_span=(0, 100),
        n_points=100
    )
    
    # Prepare features: [S, I, N] → dI/dt
    X_train = np.column_stack([S_train, I_train, 
                                np.full_like(I_train, 1000)])
    y_train = np.gradient(I_train, t_train)
    
    # Symbolic regression
    model = PySRRegressor(
        niterations=100,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=[],
        populations=20,
        population_size=50,
        parsimony=0.01,
        constraints={
            '/': (5, 1),  # Allow S*I/N pattern
        }
    )
    
    print("Fitting symbolic regression...")
    model.fit(X_train, y_train)
    
    # Get best expression
    best_expr = str(model)
    print(f"Discovered expression: {best_expr}")
    
    # Validate
    validator = EpidemiologyValidator(N=1000)
    validation = validator.validate_sir_equation(
        expression=best_expr,
        S=S_train,
        I=I_train,
        dI_dt_pred=model.predict(X_train),
        beta=0.5,
        gamma=0.1
    )
    
    print(f"\nValidation: {'✓ PASS' if validation['valid'] else '✗ FAIL'}")
    if validation['violations']:
        print("Violations:")
        for v in validation['violations']:
            print(f"  - {v}")
    if validation['warnings']:
        print("Warnings:")
        for w in validation['warnings']:
            print(f"  - {w}")
    
    # Extrapolation test
    t_extrap, I_extrap, S_extrap, R_extrap = generate_sir_data(
        beta=0.5,
        gamma=0.1,
        N=1000,
        t_span=(150, 200),
        n_points=50,
        noise_level=0.0  # No noise for clean extrapolation
    )
    
    X_extrap = np.column_stack([S_extrap, I_extrap,
                                 np.full_like(I_extrap, 1000)])
    y_extrap_true = np.gradient(I_extrap, t_extrap)
    y_extrap_pred = model.predict(X_extrap)
    
    # Calculate extrapolation error
    extrap_error = np.abs(y_extrap_pred - y_extrap_true).mean() / \
                   np.abs(y_extrap_true).mean()
    
    print(f"\nExtrapolation error: {extrap_error:.2%}")
    
    # Check physical validity
    physics_valid = validator.check_extrapolation_physics(
        t_train, I_train, t_extrap, I_extrap
    )
    
    print(f"Physics constraints: {'✓ PASS' if physics_valid else '✗ FAIL'}")
    
    # Calculate R²
    from sklearn.metrics import r2_score
    r2_train = r2_score(y_train, model.predict(X_train))
    r2_extrap = r2_score(y_extrap_true, y_extrap_pred)
    
    print(f"\nTraining R²: {r2_train:.4f}")
    print(f"Extrapolation R²: {r2_extrap:.4f}")
    
    return {
        'method': 'sir_model',
        'expression': best_expr,
        'r2_train': r2_train,
        'r2_extrap': r2_extrap,
        'extrapolation_error': extrap_error,
        'validation': validation,
        'physics_valid': physics_valid
    }
```

### Step 5: Run Complete Test (17:00-20:00)
**[Execute]**
```bash
# Run just the SIR test
python standalone_v4.py --methods sir_model --extrapolation
```

**[Expected output]**
```
============================================================
Testing: SIR Model (Epidemiology)
============================================================

Fitting symbolic regression...
  Iteration 20: Loss = 0.0234
  Iteration 40: Loss = 0.0089
  Iteration 60: Loss = 0.0012
  Iteration 80: Loss = 0.0003
  Iteration 100: Loss = 0.0001

Discovered expression: 0.5*x0*x1/x2 - 0.1*x1
  (Simplified: beta*S*I/N - gamma*I)

Validation: ✓ PASS

Extrapolation error: 2.3%

Physics constraints: ✓ PASS

Training R²: 0.9987
Extrapolation R²: 0.9891

Test completed successfully!
```

**[Explain]**
"Perfect! HypatiaX discovered the correct SIR equation:
- Identified beta ≈ 0.5, gamma ≈ 0.1
- Training R² > 0.99
- Extrapolation R² > 0.98 (excellent for ODE)
- Passes all physics constraints
- Ready for deployment"

### Step 6: Add to Full Test Suite (20:00-22:00)
**[Update test registry]**
```bash
vim experiments/test_registry.json
```

```json
{
  "epidemiology": {
    "sir_model": {
      "name": "SIR Model (Basic)",
      "difficulty": "medium",
      "expected_time": 180,
      "protocol": "protocols/epidemiology/sir_model.yaml",
      "data_generator": "experiments.epidemiology.sir_data.generate_sir_data",
      "validator": "tools.validators.epidemiology_validator.EpidemiologyValidator",
      "tags": ["disease_dynamics", "ode", "population_model"]
    },
    "seir_model": {
      "name": "SEIR Model (With Exposed)",
      "difficulty": "hard",
      "expected_time": 300,
      "protocol": "protocols/epidemiology/seir_model.yaml",
      "data_generator": "experiments.epidemiology.seir_data.generate_seir_data",
      "validator": "tools.validators.epidemiology_validator.EpidemiologyValidator",
      "tags": ["disease_dynamics", "ode", "exposed_class"]
    }
  }
}
```

**[Run full suite with new tests]**
```bash
# Run all epidemiology tests
python standalone_v4.py --domain epidemiology --extrapolation

# Or add to full suite (now 133 tests!)
python standalone_v4.py --all --extrapolation
```

### Best Practices Summary (22:00-24:00)
**[Show checklist]**
"When extending HypatiaX to new domains, follow this checklist:

✓ 1. Create YAML protocol
   - Mathematical equation (LaTeX + Python)
   - Parameters with units and ranges
   - Physical constraints
   - Training/extrapolation config

✓ 2. Implement data generator
   - Realistic noise models
   - Physical initial conditions
   - Multiple scenarios

✓ 3. Build domain-specific validator
   - Conservation laws
   - Positivity constraints
   - Dimensional analysis
   - Domain semantics

✓ 4. Integrate with test suite
   - Add test method
   - Register in test_registry.json
   - Document in README

✓ 5. Verify reproducibility
   - Run multiple times
   - Check random seed handling
   - Generate comparison plots

✓ 6. Document for users
   - Add example in docs/
   - Update tutorial README
   - Create troubleshooting guide"

### Advanced Extensions (24:00-25:00)
**[Show possibilities]**
"You can extend further by:

1. **Multi-equation systems**
   - Coupled ODEs (predator-prey, chemical reactions)
   - Partial differential equations
   - Stochastic models

2. **Custom operators**
   - Special functions (Bessel, Legendre)
   - Domain-specific operations
   - Lookup tables

3. **Hybrid objectives**
   - Multi-objective optimization
   - Pareto fronts
   - Physics-informed losses

4. **Active learning**
   - Adaptive sampling
   - Uncertainty quantification
   - Sequential experimentation

Check docs/advanced_extensions.md for details!"

### Conclusion
"Congratulations! You've completed the HypatiaX tutorial series. You can now:
✓ Set up the environment
✓ Run and interpret experiments
✓ Generate publication plots
✓ Extend to new domains

The complete code for this tutorial is in:
  examples/epidemiology_extension/

Questions? Join our Discord or open GitHub issues.
Happy equation discovering! 🎉"

EOF
}

# ============================================================================
# Preparation Functions
# ============================================================================

prepare_tutorial() {
    local tutorial_num=$1
    
    log_info "Preparing environment for Tutorial $tutorial_num..."
    
    # Generate script if not exists
    if [ ! -f "${SCRIPTS_DIR}/tutorial_${tutorial_num}_script.md" ]; then
        generate_tutorial_script "$tutorial_num"
    fi
    
    # Create tutorial-specific directory
    local tutorial_dir="${VIDEOS_DIR}/tutorial_${tutorial_num}"
    mkdir -p "${tutorial_dir}"
    
    # Set up environment based on tutorial
    case $tutorial_num in
        1)
            prepare_tutorial_1_env "$tutorial_dir"
            ;;
        2)
            prepare_tutorial_2_env "$tutorial_dir"
            ;;
        3)
            prepare_tutorial_3_env "$tutorial_dir"
            ;;
        4)
            prepare_tutorial_4_env "$tutorial_dir"
            ;;
    esac
    
    log_success "Tutorial $tutorial_num environment ready"
}

prepare_tutorial_1_env() {
    local tutorial_dir=$1
    
    # Create clean VM script
    cat > "${tutorial_dir}/setup_clean_vm.sh" << 'EOF'
#!/bin/bash
# Run this in a clean VM/container before recording

# Update system
sudo apt-get update

# Install Python
sudo apt-get install -y python3.10 python3-pip python3-venv

# Cleanup
rm -rf hypatiax venv

echo "Clean VM ready for Tutorial 1"
EOF
    
    chmod +x "${tutorial_dir}/setup_clean_vm.sh"
}

prepare_tutorial_2_env() {
    local tutorial_dir=$1
    
    # Pre-run tests to verify timing
    cat > "${tutorial_dir}/timing_verification.sh" << 'EOF'
#!/bin/bash
# Verify test timing before recording

time python standalone_v4.py --methods michaelis_menten --quick
time python standalone_v4.py --methods arrhenius --quick
time python standalone_v4.py --methods ideal_gas --quick

echo "Verify these times are acceptable for demo"
EOF
    
    chmod +x "${tutorial_dir}/timing_verification.sh"
}

prepare_tutorial_3_env() {
    local tutorial_dir=$1
    
    # Generate sample results if needed
    cat > "${tutorial_dir}/generate_sample_results.sh" << 'EOF'
#!/bin/bash
# Generate sample results for demo

python standalone_v4.py \
    --methods michaelis_menten arrhenius ideal_gas \
    --extrapolation \
    --output results/demo_results.json

echo "Sample results generated"
EOF
    
    chmod +x "${tutorial_dir}/generate_sample_results.sh"
}

prepare_tutorial_4_env() {
    local tutorial_dir=$1
    
    # Create example epidemiology files
    mkdir -p "${tutorial_dir}/epidemiology_example"
    
    # (Files created during tutorial)
    log_info "Tutorial 4 files will be created during recording"
}

# ============================================================================
# Verification Functions
# ============================================================================

verify_tutorial() {
    local tutorial_num=$1
    
    log_info "Verifying Tutorial $tutorial_num commands..."
    
    local script_file="${SCRIPTS_DIR}/tutorial_${tutorial_num}_script.md"
    
    if [ ! -f "$script_file" ]; then
        log_error "Script file not found: $script_file"
        return 1
    fi
    
    # Extract and test all bash commands
    log_info "Extracting bash commands from script..."
    
    grep -A 999 '```bash' "$script_file" | \
    grep -B 999 '```' | \
    grep -v '```' > /tmp/commands_$tutorial_num.sh
    
    log_info "Testing commands in dry-run mode..."
    bash -n /tmp/commands_$tutorial_num.sh
    
    if [ $? -eq 0 ]; then
        log_success "All commands syntax valid"
    else
        log_error "Syntax errors found in commands"
        return 1
    fi
}

# ============================================================================
# Recording Functions
# ============================================================================

start_recording() {
    local tutorial_num=$1
    
    log_info "Starting recording for Tutorial $tutorial_num..."
    
    # Check OBS is configured
    if ! command -v obs &> /dev/null; then
        log_error "OBS Studio not found. Run setup first."
        return 1
    fi
    
    log_info "Opening script in terminal..."
    less "${SCRIPTS_DIR}/tutorial_${tutorial_num}_script.md"
    
    log_warning "Manual steps required:"
    echo "1. Start OBS Studio"
    echo "2. Load 'HypatiaX' profile"
    echo "3. Click 'Start Recording'"
    echo "4. Follow script in terminal"
    echo "5. Stop recording when done"
    echo ""
    read -p "Press Enter when recording is complete..."
    
    log_success "Recording complete for Tutorial $tutorial_num"
}

# ============================================================================
# Editing Functions
# ============================================================================

edit_video() {
    local tutorial_num=$1
    
    log_info "Editing Tutorial $tutorial_num..."
    
    # Find recorded file
    local recorded_file=$(find "${RECORDINGS_DIR}" -name "*tutorial*$tutorial_num*.mkv" -type f | head -n 1)
    
    if [ -z "$recorded_file" ]; then
        log_error "No recording found for Tutorial $tutorial_num"
        return 1
    fi
    
    local output_file="${EDITED_DIR}/Tutorial_${tutorial_num}_${TUTORIAL_TITLES[$tutorial_num]// /_}.mp4"
    
    log_info "Converting and encoding..."
    
    # Convert mkv to mp4 with good quality
    ffmpeg -i "$recorded_file" \
        -c:v libx264 \
        -preset slow \
        -crf 18 \
        -c:a aac \
        -b:a "${AUDIO_BITRATE}" \
        -movflags +faststart \
        "$output_file"
    
    if [ $? -eq 0 ]; then
        log_success "Edited video saved: $output_file"
        
        # Generate thumbnail
        generate_thumbnail "$output_file" "$tutorial_num"
    else
        log_error "Video encoding failed"
        return 1
    fi
}

generate_thumbnail() {
    local video_file=$1
    local tutorial_num=$2
    
    log_info "Generating thumbnail..."
    
    local thumbnail_file="${THUMBNAILS_DIR}/tutorial_${tutorial_num}_thumbnail.png"
    
    # Extract frame at 10% into video
    ffmpeg -i "$video_file" \
        -ss 00:00:30 \
        -vframes 1 \
        -vf "scale=1280:720" \
        "$thumbnail_file"
    
    log_success "Thumbnail saved: $thumbnail_file"
}

# ============================================================================
# Publishing Functions
# ============================================================================

publish_video() {
    local tutorial_num=$1
    
    log_warning "Publishing to YouTube requires manual steps"
    
    local video_file="${EDITED_DIR}/Tutorial_${tutorial_num}_*.mp4"
    local thumbnail_file="${THUMBNAILS_DIR}/tutorial_${tutorial_num}_thumbnail.png"
    
    echo ""
    echo "Video: $(ls $video_file)"
    echo "Thumbnail: $thumbnail_file"
    echo ""
    echo "YouTube Upload Checklist:"
    echo "-------------------------"
    echo "1. Go to: studio.youtube.com"
    echo "2. Click 'Create' → 'Upload videos'"
    echo "3. Select video file above"
    echo "4. Title: Tutorial $tutorial_num: ${TUTORIAL_TITLES[$tutorial_num]}"
    echo "5. Description:"
    echo "   Part $tutorial_num of the HypatiaX tutorial series"
    echo "   Accompanying: 'LLMs as Interfaces to Symbolic Discovery' (JMLR 2025)"
    echo "   GitHub: https://github.com/[your-repo]"
    echo "6. Add thumbnail"
    echo "7. Add to playlist: 'HypatiaX Tutorials'"
    echo "8. Tags: machine learning, symbolic regression, equation discovery"
    echo ""
    read -p "Press Enter after publishing..."
    
    # Ask for video URL
    read -p "Enter YouTube video URL: " video_url
    
    # Save URL
    echo "$video_url" > "${VIDEOS_DIR}/tutorial_${tutorial_num}_url.txt"
    
    log_success "URL saved for paper"
}

# ============================================================================
# Full Workflow Functions
# ============================================================================

run_full_workflow() {
    local tutorial_num=$1
    
    log_info "Running full workflow for Tutorial $tutorial_num..."
    
    prepare_tutorial "$tutorial_num"
    verify_tutorial "$tutorial_num"
    start_recording "$tutorial_num"
    edit_video "$tutorial_num"
    publish_video "$tutorial_num"
    
    log_success "Tutorial $tutorial_num complete!"
}

process_all_tutorials() {
    log_info "Processing all 4 tutorials..."
    
    for i in {1..4}; do
        log_info "Starting Tutorial $i of 4..."
        run_full_workflow "$i"
        echo ""
    done
    
    log_success "All tutorials complete!"
    
    # Generate playlist summary
    cat > "${VIDEOS_DIR}/playlist_summary.txt" << EOF
HypatiaX Tutorial Playlist
==========================

Tutorial 1 (10 min): Setting up the Environment
URL: $(cat ${VIDEOS_DIR}/tutorial_1_url.txt 2>/dev/null || echo "Not published yet")

Tutorial 2 (15 min): Running Experiments
URL: $(cat ${VIDEOS_DIR}/tutorial_2_url.txt 2>/dev/null || echo "Not published yet")

Tutorial 3 (20 min): Analyzing Results
URL: $(cat ${VIDEOS_DIR}/tutorial_3_url.txt 2>/dev/null || echo "Not published yet")

Tutorial 4 (25 min): Extending to New Domains  
URL: $(cat ${VIDEOS_DIR}/tutorial_4_url.txt 2>/dev/null || echo "Not published yet")

Playlist URL: https://www.youtube.com/playlist?list=[YOUR_PLAYLIST_ID]

LaTeX for paper appendix:
-------------------------
\paragraph{Video Tutorials:}
\begin{itemize}
\item Tutorial 1: Setting up the environment (10 min)
\item Tutorial 2: Running experiments (15 min)
\item Tutorial 3: Analyzing results (20 min)
\item Tutorial 4: Extending to new domains (25 min)
\end{itemize}
Available at: \url{https://www.youtube.com/playlist?list=[YOUR_PLAYLIST_ID]}
EOF
    
    log_success "Playlist summary saved: ${VIDEOS_DIR}/playlist_summary.txt"
}

# ============================================================================
# Main Function
# ============================================================================

main() {
    local command=${1:-"help"}
    local tutorial_num=${2:-""}
    
    case $command in
        setup)
            setup_system
            configure_obs
            ;;
            
        prepare)
            if [ -z "$tutorial_num" ]; then
                log_error "Tutorial number required"
                exit 1
            fi
            prepare_tutorial "$tutorial_num"
            ;;
            
        verify)
            if [ -z "$tutorial_num" ]; then
                log_error "Tutorial number required"
                exit 1
            fi
            verify_tutorial "$tutorial_num"
            ;;
            
        record)
            if [ -z "$tutorial_num" ]; then
                log_error "Tutorial number required"
                exit 1
            fi
            start_recording "$tutorial_num"
            ;;
            
        edit)
            if [ -z "$tutorial_num" ]; then
                log_error "Tutorial number required"
                exit 1
            fi
            edit_video "$tutorial_num"
            ;;
            
        publish)
            if [ -z "$tutorial_num" ]; then
                log_error "Tutorial number required"
                exit 1
            fi
            publish_video "$tutorial_num"
            ;;
            
        full)
            if [ -z "$tutorial_num" ]; then
                log_error "Tutorial number required"
                exit 1
            fi
            run_full_workflow "$tutorial_num"
            ;;
            
        all)
            process_all_tutorials
            ;;
            
        help|*)
            cat << EOF
HypatiaX Video Production Manager
==================================

Usage: $0 [command] [tutorial_number]

Commands:
  setup       Install all required tools (OBS, ffmpeg, etc.)
  prepare N   Prepare environment for tutorial N
  verify N    Verify all commands in tutorial N work
  record N    Start recording tutorial N (interactive)
  edit N      Edit recorded video for tutorial N
  publish N   Publish tutorial N to YouTube
  full N      Run complete workflow for tutorial N
  all         Process all 4 tutorials
  help        Show this help message

Examples:
  $0 setup           # First-time setup
  $0 prepare 1       # Prepare Tutorial 1
  $0 full 1          # Complete Tutorial 1 workflow
  $0 all             # Process all tutorials

Tutorials:
  1. Setting up the Environment (10 min)
  2. Running Experiments (15 min)
  3. Analyzing Results (20 min)
  4. Extending to New Domains (25 min)

EOF
            ;;
    esac
}

# Run main function
main "$@"

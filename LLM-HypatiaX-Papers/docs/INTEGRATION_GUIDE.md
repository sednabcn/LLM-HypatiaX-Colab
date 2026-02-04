# 🚀 LLM-HypatiaX-PAPERS Integration Guide

## Overview

This repository is **specifically designed** for your LLM-HypatiaX research project. It maintains your existing code structure while adding powerful multi-paper management capabilities.

## 🎯 What Makes This Special

✅ **Perfect Structure Match**: Mirrors your `hypatiax/core/` and `hypatiax/data/` layout  
✅ **5-System Support**: Built for your LLM, NN, Hybrid, LLM-Guided, and PySR comparison  
✅ **Multi-Domain Ready**: Handles Physics, Chemistry, Biology, Math, Economics, Engineering, and DeFi  
✅ **DeFi Integration**: Special support for your finance/defi formulas  
✅ **Visualization Pipeline**: Integrated with your existing plotting scripts  
✅ **Result Merging**: Tools to combine results from all systems  

## 📦 What's Included

### 1. Repository Archive
- **LLM-HypatiaX-PAPERS-Integrated.tar.gz** - Complete repository (46 KB)

### 2. Setup Script
- **setup_hypatiax_repository.sh** - Regenerate repository if needed

### 3. Integration Tool
- **integrate_existing_data.sh** - Automatically imports your existing data

## 🏁 Quick Start (2 Options)

### Option A: Start Fresh (Minimal Setup)

```bash
# 1. Extract
tar -xzf LLM-HypatiaX-PAPERS-Integrated.tar.gz
cd LLM-HypatiaX-PAPERS

# 2. Add your key data file
cp /path/to/all_systems_merged.json shared/data/

# 3. Work on JMLR paper
cd papers/2025-JMLR

# 4. Link data
cd data && ln -s ../../../shared/data/all_systems_merged.json . && cd ..

# 5. Build
bash scripts/build.sh
```

### Option B: Full Integration (Recommended)

```bash
# 1. Extract
tar -xzf LLM-HypatiaX-PAPERS-Integrated.tar.gz
cd LLM-HypatiaX-PAPERS

# 2. Run integration (UPDATE THE PATH!)
bash tools/integrate_existing_data.sh ~/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax

# This automatically copies:
#   ✓ All your data files
#   ✓ All your Python code  
#   ✓ All your results
#   ✓ All your figures
#   ✓ All your LaTeX files

# 3. Sync data to all papers
bash tools/sync_shared_data.sh

# 4. Build first paper
cd papers/2025-JMLR
bash scripts/build.sh
```

## 📁 How Your Structure Maps

### Your Current Structure → New Repository

```
Your hypatiax/core/
├── preprocessing/      → shared/code/preprocessing/
├── training/           → shared/code/training/
├── evaluation/         → shared/code/evaluation/
├── generation/         → shared/code/generation/
│   ├── hybrid_all_domains/         → [preserved]
│   ├── hybrid_defi_llm_nn/         → [preserved]
│   └── hybrid_llm_guide_validation/→ [preserved]
├── deployment/         → shared/code/deployment/
└── base_pure_llm/      → shared/code/base_pure_llm/

Your hypatiax/data/
├── finance/
│   ├── defi/          → shared/data/finance/defi/
│   └── risk/          → shared/data/finance/risk/
└── paper1/
    ├── results/       → shared/results/
    ├── figures/       → papers/2025-JMLR/figures/
    ├── latex/         → papers/2025-JMLR/latex/
    └── visualizations/→ shared/visualizations/
```

### Result: Clean Organization

```
LLM-HypatiaX-PAPERS/
├── papers/
│   └── 2025-JMLR/          ← Your main paper
│       ├── paper/          ← LaTeX source
│       ├── figures/        ← Your figures here
│       ├── latex/          ← Your Bib/, sections_latex/
│       ├── src/            ← Analysis scripts
│       └── data/           ← Symlinks to shared
│
└── shared/
    ├── data/
    │   ├── all_systems_merged.json  ← Your master data
    │   └── finance/defi/            ← Your DeFi formulas
    ├── code/
    │   ├── preprocessing/           ← Your core modules
    │   ├── generation/              ← Your hybrid systems
    │   └── ...
    ├── results/
    │   ├── baseline_nn_pure_llm/    ← Your results
    │   ├── hybrid_pysr/all_domains/ ← Your PySR results
    │   └── ...
    └── visualizations/              ← Your plotting scripts
```

## 🔬 Your Research Structure is Preserved

The repository is designed around your **5 systems**:

### System 1: Pure LLM Baseline
- Code: `shared/code/base_pure_llm/`
- Results: `shared/results/baseline_nn_pure_llm/`

### System 2: Neural Network Baseline
- Code: `shared/code/training/baseline_neural_network*.py`
- Results: `shared/results/baseline_nn_pure_llm/`

### System 3: Hybrid LLM-NN
- Code: `shared/code/generation/hybrid_all_domains_llm_nn/`
- Results: `shared/results/hybrid_llm_nn/`

### System 4: LLM-Guided Symbolic Discovery
- Code: `shared/code/generation/hybrid_llm_guide_validation/`
- Results: `shared/results/llm_guided/`

### System 5: PySR Symbolic Regression
- Results: `shared/results/hybrid_pysr/`

## 📊 Working with Your Data

### Your Main Dataset: all_systems_merged.json

This file contains all results from your 5 systems across 30 formulas.

**Location after integration**: `shared/data/all_systems_merged.json`

**Access from papers**:
```python
import json
from pathlib import Path

# Load data
data_file = Path("data/all_systems_merged.json")  # Symlinked
with open(data_file) as f:
    data = json.load(f)

# Your data structure is preserved
for formula_id, formula_data in data.items():
    domain = formula_data['domain']
    systems_results = formula_data['systems']
    # Your analysis code here
```

### Your DeFi Data

**Location after integration**: `shared/data/finance/defi/`

Contains your specialized formulas:
- AMM (Automated Market Maker)
- Impermanent Loss
- VaR (Value at Risk)  
- Liquidation calculations
- Staking rewards

### Your Results

**Location after integration**: `shared/results/`

Organized exactly as you had them:
```
shared/results/
├── baseline_nn_pure_llm/
│   ├── comparison_analysis_all_domains/
│   └── comparison_analysis_defi/
├── comparison_results/
│   ├── all_domains/
│   └── defi/
├── hybrid_llm_nn/
├── hybrid_pysr/
│   ├── all_domains/
│   └── defi/
└── llm_guided/
```

## 🎨 Figure Generation

### Your Existing Figures

After integration, your figures are in:
- `papers/2025-JMLR/figures/`

Including:
- `figure1_arrhenius_extrapolation.pdf`
- `figure2_domain_comparison.pdf`
- `figure3_validation_breakdown.pdf`
- `figure4_real_data.pdf`
- `figure5_method_comparison.pdf`
- `figure_5systems_comparison.pdf`
- `hybrid_architecture_clean.pdf`
- And all your PNG versions

### Regenerating Figures

The repository includes a script that works with your data format:

```bash
cd papers/2025-JMLR/src

# Generate specific figure
python3 regenerate_figures.py --figure 1

# Generate all figures
python3 regenerate_figures.py --all
```

**Note**: You may need to customize `regenerate_figures.py` to exactly match your data structure. The template is already 80% there!

### Your Visualization Scripts

Your existing visualization scripts are preserved in:
- `shared/visualizations/scripts_data_vis/`

Including:
- `statistical_analysis_full.py`
- `merge_all_systems.py`
- `extract_system_data.py`
- `regenerate_figures.py`
- And more!

## 📝 Paper Workflow

### JMLR Paper (Your Main Paper)

```bash
cd papers/2025-JMLR

# 1. Verify data is linked
ls -l data/
# Should show symlinks to shared data

# 2. Merge system results (if needed)
cd src
python3 merge_all_systems.py

# 3. Run statistical analysis
python3 statistical_analysis_full.py

# 4. Generate figures
python3 regenerate_figures.py --all

# 5. Build paper
cd ..
bash scripts/build.sh

# Output: paper/jmlr_paper.pdf
```

### Paper Structure

Your JMLR paper includes:

**LaTeX Source** (`paper/`)
- `jmlr_paper.tex` - Main document with your research
- `references.bib` - Bibliography
- `Makefile` - Build automation

**Sections** (`latex/`)  
- Your existing `sections_latex/` content
- Bibliography files from `Bib/`

**Figures** (`figures/`)
- All your PDF figures
- Architecture diagrams
- Comparison plots

**Analysis** (`src/`)
- `regenerate_figures.py` - Figure generation
- `statistical_analysis_full.py` - Statistical tests
- `merge_all_systems.py` - Result merging
- `extract_system_data.py` - Data extraction

## 🛠️ Management Tools

### 1. Integration Tool

```bash
bash tools/integrate_existing_data.sh /path/to/hypatiax
```

**What it does:**
- Copies all data from `hypatiax/data/` → `shared/data/`
- Copies all code from `hypatiax/core/` → `shared/code/`
- Copies results → `shared/results/`
- Copies figures → `papers/2025-JMLR/figures/`
- Copies LaTeX files → `papers/2025-JMLR/latex/`

### 2. Data Sync

```bash
bash tools/sync_shared_data.sh
```

Creates symlinks in all papers to shared data.

### 3. Build All Papers

```bash
bash tools/build_all_papers.sh
```

Builds PDFs for all papers in the repository.

### 4. Repository Stats

```bash
bash tools/repo_stats.sh
```

Shows:
- Number of papers
- Code file counts
- Data file counts
- Build status

### 5. Create New Paper

```bash
bash tools/create_new_paper.sh "2026-ICLR" "ICLR" "2026" "New Direction"
```

Creates a new paper with the same structure.

## 💻 Using Your Existing Code

### Import Your Modules

From any paper's `src/` directory:

```python
import sys
sys.path.append('../../../shared/code')

# Now import your modules as before
from preprocessing.preparation_data import prepare_dataset
from training.baseline_neural_network import train_nn_model
from generation.experiment_protocol import run_experiment

# Your existing code works unchanged!
```

### Run Your Experiments

Your experiment protocols are preserved:

```python
# shared/code/generation/experiment_protocol.py
# shared/code/generation/experiment_protocol_defi.py
# shared/code/generation/hybrid_all_domains/experiment_protocol_all_*.py

# Use them as before
from generation.experiment_protocol_defi import run_defi_experiment
results = run_defi_experiment(config)
```

## 📈 Statistical Analysis

### Your Existing Analysis

Located in: `shared/visualizations/scripts_data_vis/statistical_analysis_full.py`

Run it from paper:
```bash
cd papers/2025-JMLR/src
python3 ../../../shared/visualizations/scripts_data_vis/statistical_analysis_full.py
```

Or create a convenience script:
```bash
cd papers/2025-JMLR/src
ln -s ../../../shared/visualizations/scripts_data_vis/statistical_analysis_full.py .
python3 statistical_analysis_full.py
```

### Generate LaTeX Tables

Your analysis generates LaTeX tables for the paper:
- Descriptive statistics
- Pairwise t-tests
- Effect sizes
- System comparisons

Tables go directly into `papers/2025-JMLR/latex/` for inclusion in the paper.

## 📊 Your Domains

The repository is organized for your 7 domains:

1. **Physics** - Mechanics, thermodynamics, electromagnetism, optics, quantum
2. **Chemistry** - Arrhenius, Nernst, Henderson-Hasselbalch
3. **Biology** - Michaelis-Menten, logistic growth, allometric scaling
4. **Mathematics** - Quadratic, Pythagorean, compound interest
5. **Economics** - Cobb-Douglas, elasticity
6. **Engineering** - Bernoulli, Hooke's law, Reynolds number
7. **Finance/DeFi** - AMM, impermanent loss, VaR, liquidation

Each domain's data flows through the same pipeline:
```
Raw Data → Preprocessing → Training → Evaluation → Results → Figures → Paper
```

## 🎓 LaTeX & Bibliography

### Your Bibliography

After integration:
- `papers/2025-JMLR/paper/references.bib` - Main bibliography
- `papers/2025-JMLR/latex/Bib/bibliography.bib` - Extended references

### Your LaTeX Sections

Your existing sections from `hypatiax/data/paper1/latex/sections_latex/`:
- Copied to `papers/2025-JMLR/latex/`
- Can be included in main paper with `\input{}`

### Build Process

```bash
cd papers/2025-JMLR/paper
make          # Full build with bibliography
make quick    # Quick rebuild
make clean    # Remove aux files
make view     # Open PDF
```

## 🔄 Typical Workflow

### Day-to-Day Research

```bash
# 1. Navigate to paper
cd LLM-HypatiaX-PAPERS/papers/2025-JMLR

# 2. Run new experiments (using your existing code)
cd ../../../shared/code/generation/hybrid_all_domains
python3 suite_hybrid_system_all_domains_v5.py

# Results saved to shared/results/

# 3. Merge new results
cd -
cd src
python3 merge_all_systems.py

# 4. Update figures
python3 regenerate_figures.py --all

# 5. Update paper text
vim ../paper/jmlr_paper.tex

# 6. Rebuild
bash ../scripts/build.sh

# 7. Review
open ../paper/jmlr_paper.pdf
```

### Preparing for Submission

```bash
cd papers/2025-JMLR

# 1. Final build
bash scripts/build.sh

# 2. Create submission package
bash scripts/create_submission.sh

# Outputs:
# - submission/YYYYMMDD_HHMMSS/ (folder)
# - submission/jmlr_submission_YYYYMMDD_HHMMSS.tar.gz (archive)
```

## 🐛 Troubleshooting

### Data Not Found

```bash
# Check symlinks
ls -l papers/2025-JMLR/data/

# Should show:
# all_systems_merged.json -> ../../../shared/data/all_systems_merged.json
# finance -> ../../../shared/data/finance

# If missing, recreate:
cd papers/2025-JMLR/data
ln -sf ../../../shared/data/all_systems_merged.json .
ln -sf ../../../shared/data/finance .
```

### Import Errors

```bash
# Check if code is in shared/
ls -R shared/code/

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/shared/code"

# Or in script:
import sys
sys.path.insert(0, '../../../shared/code')
```

### Figure Generation Fails

```bash
# Check data exists
ls -l papers/2025-JMLR/data/all_systems_merged.json

# Check script exists
ls -l papers/2025-JMLR/src/regenerate_figures.py

# Run with Python path
cd papers/2025-JMLR/src
PYTHONPATH=../../../shared/code python3 regenerate_figures.py --all
```

### LaTeX Build Errors

```bash
cd papers/2025-JMLR/paper

# Clean and rebuild
make clean
make

# Check log
less jmlr_paper.log

# Common issues:
# - Missing figures: Check ../figures/ directory
# - Missing references: Check references.bib
# - Missing jmlr2e.sty: Will auto-download or use article class
```

## 🎯 Customization

### Adjust Figure Generation

Edit `papers/2025-JMLR/src/regenerate_figures.py`:

```python
def load_data():
    """Load your specific data format"""
    # Customize this to match your JSON structure exactly
    
def figure1_extrapolation():
    """Generate Figure 1 with your exact requirements"""
    # Modify plotting to match your preferences
```

### Add New Shared Utilities

```bash
# Add new utility
vim shared/code/utils/my_new_utility.py

# Use in papers
cd papers/2025-JMLR/src
# Add to script:
import sys
sys.path.append('../../../shared/code')
from utils.my_new_utility import my_function
```

### Customize Paper Template

Edit `papers/2025-JMLR/paper/jmlr_paper.tex`:
- Update title
- Add authors
- Modify sections
- Adjust figures

## ✅ Integration Checklist

- [ ] Extract repository: `tar -xzf LLM-HypatiaX-PAPERS-Integrated.tar.gz`
- [ ] Run integration: `bash tools/integrate_existing_data.sh /path/to/hypatiax`
- [ ] Verify data copied: `ls -R shared/data/`
- [ ] Verify code copied: `ls -R shared/code/`
- [ ] Sync to papers: `bash tools/sync_shared_data.sh`
- [ ] Check symlinks: `ls -l papers/2025-JMLR/data/`
- [ ] Test figure generation: `cd papers/2025-JMLR/src && python3 regenerate_figures.py --figure 1`
- [ ] Build paper: `cd papers/2025-JMLR && bash scripts/build.sh`
- [ ] Review PDF: `papers/2025-JMLR/paper/jmlr_paper.pdf`

## 🚀 Next Steps

1. **Integrate Your Data**
   ```bash
   bash tools/integrate_existing_data.sh ~/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax
   ```

2. **Verify Integration**
   ```bash
   bash tools/repo_stats.sh
   ```

3. **Test Build**
   ```bash
   cd papers/2025-JMLR
   bash scripts/build.sh
   ```

4. **Customize**
   - Update author information
   - Adjust figure generation
   - Modify paper text
   - Add your results

## 📧 Support

For questions:
1. Check `README.md` in repository root
2. Check `docs/SETUP_SUMMARY.md`
3. Check paper-specific `papers/PAPER/README.md`

## 🎉 You're Ready!

Your LLM-HypatiaX research is now organized in a professional multi-paper repository while keeping all your existing code and data intact!

Happy publishing! 📄✨

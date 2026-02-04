# LLM-HypatiaX-PAPERS

Multi-paper research repository for LLM evaluation and analysis.

## 🎯 Overview

This repository manages multiple research papers that share common datasets and analysis code. Each paper is self-contained but can leverage shared resources.

## 📁 Structure

```
LLM-HypatiaX-PAPERS/
├── papers/              # Individual papers
│   ├── 2025-JMLR/      # JMLR paper
│   ├── 2025-NeurIPS/   # NeurIPS paper
│   ├── 2026-ICML/      # ICML paper
│   └── 2025-AAAI/      # AAAI paper
├── shared/              # Shared resources
│   ├── data/           # Common datasets
│   ├── code/           # Analysis utilities
│   └── figures/        # Reusable components
├── tools/               # Management scripts
└── docs/                # Documentation
```

## 🚀 Quick Start

### 1. Add Your Data

Place your data in the shared directory:
```bash
cp /path/to/all_systems_merged.json shared/data/
```

### 2. Work on a Paper

```bash
cd papers/2025-JMLR

# Link shared data
cd data && ln -s ../../../shared/data/all_systems_merged.json . && cd ..

# Generate figures
bash scripts/generate_figures.sh

# Build paper
bash scripts/build.sh

# Create submission
bash scripts/create_submission.sh
```

### 3. Use Management Tools

```bash
# Build all papers at once
bash tools/build_all_papers.sh

# Create a new paper
bash tools/create_new_paper.sh "2026-ICLR" "ICLR" "2026"

# Sync shared data to all papers
bash tools/sync_shared_data.sh

# Check repository statistics
bash tools/repo_stats.sh

# Analyze citations
python3 tools/check_citations.py
```

## 📄 Paper Structure

Each paper directory contains:
- `paper/` - LaTeX source + Makefile
- `figures/` - PDF figures
- `data/` - Paper-specific data (symlinks to shared/)
- `src/` - Analysis code (Python)
- `scripts/` - Build automation
- `submission/` - Submission packages
- `reviews/` - Review responses

## 🔧 Shared Resources

### Data (`shared/data/`)
- `all_systems_merged.json` - Main dataset (127 tests)
- Common benchmarks

### Code (`shared/code/`)
- `stats_utils.py` - Statistical functions
- `plot_utils.py` - Plotting utilities
- `data_loader.py` - Data loading helpers

### Usage Example

```python
import sys
sys.path.append('../../../shared/code')

from data_loader import load_shared_data
from plot_utils import save_figure

data = load_shared_data()
# Analyze and plot...
```

## 📊 Dataset

The main dataset (`all_systems_merged.json`) contains:
- 127 test cases
- Multiple system evaluations
- Comprehensive metrics

## 🛠️ Requirements

- **LaTeX**: pdflatex, bibtex
- **Python**: 3.7+, numpy, matplotlib, scipy, seaborn

Install Python dependencies:
```bash
pip install numpy matplotlib scipy seaborn
```

## 📖 Documentation

- `docs/SETUP_SUMMARY.md` - Complete setup guide
- `docs/QUICK_START_GUIDE.md` - Detailed workflows
- `docs/STRUCTURE_VISUAL.md` - Visual diagrams

## 🔄 Workflow

1. **Data Preparation**: Add datasets to `shared/data/`
2. **Analysis**: Write analysis code in `papers/*/src/`
3. **Figures**: Generate figures with `generate_figures.sh`
4. **Writing**: Edit LaTeX in `papers/*/paper/`
5. **Building**: Run `build.sh` to compile
6. **Submission**: Use `create_submission.sh` for packages

## 🎓 Best Practices

- Keep shared code in `shared/code/` for reuse
- Link (don't copy) shared data when possible
- Use consistent figure styles from `plot_utils.py`
- Document your analysis in paper README files
- Version control submission packages

## 🤝 Contributing

1. Create new papers with `tools/create_new_paper.sh`
2. Add shared utilities to `shared/code/`
3. Update documentation as needed

## 📝 License

[Your License Here]

## 👥 Authors

[Your Authors Here]

## 📧 Contact

[Your Contact Info]

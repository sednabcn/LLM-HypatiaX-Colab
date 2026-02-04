# 🚀 LLM-HypatiaX-PAPERS - Quick Start

## What You Got

✅ **Complete Multi-Paper Repository** with:
- 4 Paper directories (JMLR, NeurIPS, ICML, AAAI)
- Shared resources system
- 5 Management tools
- Full documentation
- Ready-to-use scripts

## 📦 Files Provided

1. **LLM-HypatiaX-PAPERS.tar.gz** - Complete repository archive
2. **setup_repository.sh** - Setup script (if you want to regenerate)

## 🏁 Get Started in 3 Steps

### Step 1: Extract the Archive

```bash
tar -xzf LLM-HypatiaX-PAPERS.tar.gz
cd LLM-HypatiaX-PAPERS
```

### Step 2: Add Your Data

```bash
# Copy your dataset to the shared directory
cp /path/to/all_systems_merged.json shared/data/
```

### Step 3: Choose Your Workflow

#### Option A: Work on Existing Paper (e.g., JMLR)

```bash
cd papers/2025-JMLR

# Link shared data
cd data && ln -s ../../../shared/data/all_systems_merged.json . && cd ..

# Generate figures
bash scripts/generate_figures.sh

# Build paper
bash scripts/build.sh

# View result
open paper/main.pdf  # or: evince paper/main.pdf
```

#### Option B: Create New Paper

```bash
# From repository root
bash tools/create_new_paper.sh "2026-CVPR" "CVPR" "2026"

cd papers/2026-CVPR
# Follow Option A steps above
```

## 🛠️ Essential Commands

```bash
# Build all papers at once
bash tools/build_all_papers.sh

# Sync shared data to all papers
bash tools/sync_shared_data.sh

# Check repository status
bash tools/repo_stats.sh

# Check citations across papers
python3 tools/check_citations.py

# Create submission package
cd papers/PAPER_NAME
bash scripts/create_submission.sh
```

## 📁 Repository Structure

```
LLM-HypatiaX-PAPERS/
├── papers/              # Your research papers
│   ├── 2025-JMLR/      # Each paper is independent
│   ├── 2025-NeurIPS/
│   ├── 2026-ICML/
│   └── 2025-AAAI/
├── shared/              # Common resources
│   ├── data/           # Shared datasets
│   ├── code/           # Python utilities
│   └── figures/        # Reusable components
├── tools/               # Management scripts
├── docs/                # Full documentation
└── README.md            # Main documentation
```

## 📚 Each Paper Contains

```
papers/2025-JMLR/
├── paper/               # LaTeX source
│   ├── main.tex        # Main document
│   ├── references.bib  # Bibliography
│   └── Makefile        # Build system
├── figures/             # Generated figures (PDF)
├── data/                # Paper-specific data
├── src/                 # Analysis scripts (Python)
│   ├── plot_results.py # Figure generation
│   └── analyze_data.py # Data analysis
├── scripts/             # Automation
│   ├── build.sh        # Build paper
│   ├── generate_figures.sh
│   └── create_submission.sh
├── submission/          # Submission packages
└── README.md           # Paper documentation
```

## 🎯 Common Tasks

### Generate Figures for a Paper

```bash
cd papers/2025-JMLR
bash scripts/generate_figures.sh
# Figures saved to: figures/*.pdf
```

### Edit and Rebuild Paper

```bash
cd papers/2025-JMLR

# Edit LaTeX
vim paper/main.tex

# Rebuild
bash scripts/build.sh

# Result: paper/main.pdf
```

### Use Shared Python Utilities

In your analysis scripts:

```python
import sys
sys.path.append('../../../shared/code')

from data_loader import load_shared_data
from stats_utils import compute_confidence_interval
from plot_utils import save_figure, COLORS

# Load data
data = load_shared_data()

# Analyze
mean, ci = compute_confidence_interval(data)

# Plot with consistent styling
plt.bar(x, y, color=COLORS['primary'])
save_figure(fig, '../figures/results.pdf')
```

## 📖 Documentation Files

Read these for detailed information:

1. **README.md** - Repository overview
2. **docs/SETUP_SUMMARY.md** - What's included
3. **docs/QUICK_START_GUIDE.md** - Detailed workflows
4. **docs/STRUCTURE_VISUAL.md** - Visual diagrams

## 🔧 Requirements

### For LaTeX (Paper Building)
- pdflatex
- bibtex

### For Python (Analysis & Figures)
```bash
pip install numpy matplotlib scipy seaborn
```

## 💡 Tips

### Set Up Aliases
Add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias paper-build='bash scripts/build.sh'
alias paper-figs='bash scripts/generate_figures.sh'
alias paper-all='cd ../../.. && bash tools/build_all_papers.sh'
```

### Watch for Changes
Auto-rebuild on file changes:

```bash
cd papers/2025-JMLR/paper
while inotifywait -e modify *.tex; do make; done
```

### Version Control
Initialize git repository:

```bash
cd LLM-HypatiaX-PAPERS
git init
git add .
git commit -m "Initial repository setup"
```

## 🆘 Troubleshooting

### "Data file not found" Error

```bash
# Check if symlink exists
ls -lh papers/PAPER/data/all_systems_merged.json

# Create it if missing
cd papers/PAPER/data
ln -s ../../../shared/data/all_systems_merged.json .
```

### LaTeX Build Errors

```bash
cd papers/PAPER/paper

# Clean build files
make clean

# Rebuild
make

# Check log for errors
less main.log
```

### Python Module Not Found

```bash
# Verify shared code exists
ls shared/code/*.py

# Check Python path in your script
python3 -c "import sys; print('\\n'.join(sys.path))"
```

## 🎉 What's Next?

1. ✅ Extract the archive
2. ✅ Read main README.md
3. ✅ Add your data
4. ✅ Pick a paper to work on
5. ✅ Start analyzing and writing!

## 📧 Support

For detailed workflows and advanced usage:
- Read `docs/QUICK_START_GUIDE.md`
- Check paper-specific README files
- Review example code in `shared/code/`

---

**Repository Created:** January 31, 2026  
**Version:** 1.0.0  
**Status:** ✅ Ready to Use

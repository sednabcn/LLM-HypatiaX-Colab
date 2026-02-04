# Quick Start Guide

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [Working on a Paper](#working-on-a-paper)
3. [Using Shared Resources](#using-shared-resources)
4. [Building Papers](#building-papers)
5. [Creating Submissions](#creating-submissions)
6. [Managing Multiple Papers](#managing-multiple-papers)

## Initial Setup

### 1. Add Your Dataset

```bash
# Copy your main dataset
cp /path/to/all_systems_merged.json shared/data/

# Verify it's there
ls -lh shared/data/all_systems_merged.json
```

### 2. Install Python Dependencies

```bash
pip install numpy matplotlib scipy seaborn
```

### 3. Verify LaTeX Installation

```bash
which pdflatex
which bibtex
```

## Working on a Paper

### Starting with a Paper

```bash
# Navigate to a paper
cd papers/2025-JMLR

# Check the structure
ls -la
```

### Linking Shared Data

```bash
# Go to paper's data directory
cd data

# Create symbolic link to shared data
ln -s ../../../shared/data/all_systems_merged.json .

# Verify the link
ls -lh all_systems_merged.json

# Go back to paper root
cd ..
```

### Writing Analysis Code

Edit `src/analyze_data.py`:

```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Add shared code to path
sys.path.append('../../../shared/code')
from data_loader import load_shared_data
from stats_utils import compute_confidence_interval

# Load data
data = load_shared_data()

# Your analysis here
print(f"Loaded {len(data)} records")
```

### Creating Figures

Edit `src/plot_results.py`:

```python
#!/usr/bin/env python3
import sys
sys.path.append('../../../shared/code')

from plot_utils import save_figure, COLORS
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
# Your plotting code...
save_figure(fig, '../figures/results.pdf')
```

Generate figures:
```bash
bash scripts/generate_figures.sh
```

### Writing the Paper

Edit `paper/main.tex`:
- Update title and authors
- Write sections
- Reference figures: `\includegraphics{../figures/results.pdf}`
- Add citations to `references.bib`

## Using Shared Resources

### Shared Code Structure

```
shared/code/
├── stats_utils.py     # Statistical functions
├── plot_utils.py      # Plotting utilities
└── data_loader.py     # Data loading helpers
```

### Using Shared Functions

```python
import sys
sys.path.append('../../../shared/code')

# Statistics
from stats_utils import compute_confidence_interval, cohen_d
mean, ci = compute_confidence_interval(data)

# Plotting
from plot_utils import COLORS, save_figure
plt.plot(x, y, color=COLORS['primary'])

# Data loading
from data_loader import load_shared_data
data = load_shared_data('all_systems_merged.json')
```

### Adding New Shared Functions

1. Edit appropriate file in `shared/code/`
2. All papers can immediately use the new functions
3. Document with docstrings

## Building Papers

### Build Single Paper

```bash
cd papers/2025-JMLR
bash scripts/build.sh
```

This runs:
1. `pdflatex main.tex`
2. `bibtex main`
3. `pdflatex main.tex` (twice more)

Output: `paper/main.pdf`

### Build All Papers

```bash
# From repository root
bash tools/build_all_papers.sh
```

### Cleaning Build Files

```bash
cd papers/2025-JMLR/paper
make clean      # Remove aux files
make distclean  # Remove PDF too
```

## Creating Submissions

### Generate Submission Package

```bash
cd papers/2025-JMLR
bash scripts/create_submission.sh
```

This creates:
- `submission/YYYYMMDD/` directory with:
  - PDF file
  - LaTeX sources
  - Figures
  - Compressed archive

### Manual Submission Prep

```bash
# Create directory
mkdir -p submission/custom

# Copy files
cp paper/main.pdf submission/custom/
cp paper/*.tex submission/custom/
cp paper/*.bib submission/custom/
cp -r figures submission/custom/

# Create archive
cd submission
tar -czf custom.tar.gz custom/
```

## Managing Multiple Papers

### Check Repository Status

```bash
bash tools/repo_stats.sh
```

Output shows:
- Number of papers
- Build status
- File counts

### Sync Data to All Papers

```bash
bash tools/sync_shared_data.sh
```

Creates symlinks in all paper `data/` directories.

### Create New Paper

```bash
bash tools/create_new_paper.sh "2026-ICLR" "ICLR" "2026"
```

This creates a complete paper structure at `papers/2026-ICLR/`.

### Check Citations

```bash
python3 tools/check_citations.py
```

Shows citation overlap between papers.

## Workflow Examples

### Example 1: New Paper from Scratch

```bash
# 1. Create paper
bash tools/create_new_paper.sh "2026-CVPR" "CVPR" "2026"

# 2. Link data
cd papers/2026-CVPR/data
ln -s ../../../shared/data/all_systems_merged.json .
cd ..

# 3. Write analysis
vim src/analyze_data.py
python3 src/analyze_data.py

# 4. Generate figures
bash scripts/generate_figures.sh

# 5. Write paper
vim paper/main.tex

# 6. Build
bash scripts/build.sh

# 7. Review
evince paper/main.pdf &
```

### Example 2: Update Shared Code

```bash
# 1. Edit shared function
vim shared/code/stats_utils.py

# 2. Test in one paper
cd papers/2025-JMLR
python3 src/analyze_data.py

# 3. Rebuild all papers that use it
bash ../../tools/build_all_papers.sh
```

### Example 3: Prepare Multiple Submissions

```bash
# Build all
bash tools/build_all_papers.sh

# Create all submission packages
for paper in papers/*/; do
    (cd "$paper" && bash scripts/create_submission.sh)
done

# Check results
ls -lh papers/*/submission/*.tar.gz
```

## Tips & Tricks

### Quick Commands

Add to your `.bashrc` or `.zshrc`:

```bash
alias paper-build='bash scripts/build.sh'
alias paper-figs='bash scripts/generate_figures.sh'
alias paper-sub='bash scripts/create_submission.sh'
```

### Watch for Changes

```bash
# Auto-rebuild on changes
while inotifywait -e modify paper/*.tex; do
    make -C paper
done
```

### Diff Between Papers

```bash
# Compare two papers
diff papers/2025-JMLR/paper/main.tex papers/2025-NeurIPS/paper/main.tex
```

### Backup Before Major Changes

```bash
# Create backup
tar -czf backup_$(date +%Y%m%d).tar.gz papers/
```

## Troubleshooting

### "Data file not found"

```bash
# Check symlink
ls -lh papers/PAPER/data/all_systems_merged.json

# Recreate if needed
cd papers/PAPER/data
ln -sf ../../../shared/data/all_systems_merged.json .
```

### "Module not found" in Python

```bash
# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Verify shared code exists
ls shared/code/*.py
```

### LaTeX Build Errors

```bash
# Clean and rebuild
cd papers/PAPER/paper
make clean
make

# Check log file
less main.log
```

### Missing Figures

```bash
# Regenerate figures
cd papers/PAPER
bash scripts/generate_figures.sh

# Check they exist
ls -lh figures/*.pdf
```

## Next Steps

1. Customize paper templates for your research
2. Add your specific analysis code
3. Develop shared utilities as needed
4. Set up version control (git)
5. Establish backup routine

For more information, see:
- `README.md` - Overview
- `SETUP_SUMMARY.md` - What's included
- Paper-specific README files

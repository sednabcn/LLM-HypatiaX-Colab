#!/bin/bash

################################################################################
# LLM-HypatiaX-PAPERS Repository Setup Script
# This script creates a complete multi-paper research repository
################################################################################

set -e  # Exit on any error

REPO_NAME="LLM-HypatiaX-PAPERS"
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     LLM-HypatiaX-PAPERS Repository Setup                    ║"
echo "║     Multi-Paper Research Repository Generator                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Clean up if exists
if [ -d "$REPO_NAME" ]; then
    echo -e "${YELLOW}⚠️  Removing existing repository...${NC}"
    rm -rf "$REPO_NAME"
fi

echo -e "${GREEN}📁 Creating repository structure...${NC}"
mkdir -p "$REPO_NAME"
cd "$REPO_NAME"

# Create main directories
mkdir -p papers shared/{data,code,figures} templates tools docs

echo -e "${GREEN}📄 Creating paper directories...${NC}"

# Define papers
declare -A PAPERS=(
    ["2025-JMLR"]="Journal of Machine Learning Research|2025"
    ["2025-NeurIPS"]="Neural Information Processing Systems|2025"
    ["2026-ICML"]="International Conference on Machine Learning|2026"
    ["2025-AAAI"]="Association for the Advancement of Artificial Intelligence|2025"
)

# Create each paper directory
for paper_dir in "${!PAPERS[@]}"; do
    IFS='|' read -r venue year <<< "${PAPERS[$paper_dir]}"
    
    echo -e "${BLUE}  → Creating $paper_dir ($venue)${NC}"
    
    mkdir -p "papers/$paper_dir"/{paper,figures,data,src,scripts,submission,reviews}
    
    # Create paper README
    cat > "papers/$paper_dir/README.md" << EOF
# $paper_dir Paper

**Venue:** $venue  
**Year:** $year  
**Status:** In Progress

## Overview

This paper focuses on [describe focus area].

## Directory Structure

- \`paper/\` - LaTeX source files
- \`figures/\` - All figures (PDF format)
- \`data/\` - Paper-specific data (symlinks to shared data)
- \`src/\` - Analysis code and experiments
- \`scripts/\` - Build and automation scripts
- \`submission/\` - Submission-ready packages
- \`reviews/\` - Review responses and revisions

## Quick Start

\`\`\`bash
# Build the paper
bash scripts/build.sh

# Generate all figures
bash scripts/generate_figures.sh

# Create submission package
bash scripts/create_submission.sh
\`\`\`

## Data

This paper uses the shared dataset: \`all_systems_merged.json\` (127 test cases)

To link the shared data:
\`\`\`bash
cd data
ln -s ../../../shared/data/all_systems_merged.json .
\`\`\`
EOF

    # Create main LaTeX file
    cat > "papers/$paper_dir/paper/main.tex" << 'EOF'
\documentclass[11pt]{article}

% Packages
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{cleveref}

% Title and authors
\title{Your Paper Title}
\author{
    Author One\thanks{Institution One, email@domain.com} \and
    Author Two\thanks{Institution Two, email@domain.com}
}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
Your abstract goes here. This should be a concise summary of your work, including the problem, approach, and main findings.
\end{abstract}

\section{Introduction}
\label{sec:introduction}

Your introduction goes here.

\section{Related Work}
\label{sec:related}

Discussion of related work.

\section{Methodology}
\label{sec:methodology}

Your methodology description.

\section{Experiments}
\label{sec:experiments}

Experimental setup and results.

\subsection{Dataset}

We evaluate our approach on 127 test cases from the LLM-HypatiaX benchmark.

\subsection{Results}

See \Cref{fig:results} for main results.

\begin{figure}[ht]
    \centering
    \includegraphics[width=0.8\textwidth]{../figures/results.pdf}
    \caption{Main experimental results.}
    \label{fig:results}
\end{figure}

\section{Conclusion}
\label{sec:conclusion}

Concluding remarks.

\bibliographystyle{plain}
\bibliography{references}

\end{document}
EOF

    # Create references file
    cat > "papers/$paper_dir/paper/references.bib" << 'EOF'
@article{example2024,
    title={Example Paper Title},
    author={Author, First and Author, Second},
    journal={Journal Name},
    year={2024}
}
EOF

    # Create Makefile
    cat > "papers/$paper_dir/paper/Makefile" << 'EOF'
.PHONY: all clean

MAIN = main
PDF = $(MAIN).pdf

all: $(PDF)

$(PDF): $(MAIN).tex references.bib
	pdflatex $(MAIN)
	bibtex $(MAIN)
	pdflatex $(MAIN)
	pdflatex $(MAIN)

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk *.synctex.gz

distclean: clean
	rm -f $(PDF)
EOF

    # Create build script
    cat > "papers/$paper_dir/scripts/build.sh" << 'EOF'
#!/bin/bash
set -e

echo "Building paper..."
cd ../paper
make clean
make
echo "✓ Paper built successfully!"
echo "PDF: paper/main.pdf"
EOF
    chmod +x "papers/$paper_dir/scripts/build.sh"

    # Create figure generation script
    cat > "papers/$paper_dir/scripts/generate_figures.sh" << 'EOF'
#!/bin/bash
set -e

echo "Generating figures..."
cd ../src

# Run Python scripts to generate figures
python3 plot_results.py

echo "✓ Figures generated successfully!"
EOF
    chmod +x "papers/$paper_dir/scripts/generate_figures.sh"

    # Create submission script
    cat > "papers/$paper_dir/scripts/create_submission.sh" << 'EOF'
#!/bin/bash
set -e

SUBMISSION_DIR="../submission/$(date +%Y%m%d)"
mkdir -p "$SUBMISSION_DIR"

echo "Creating submission package..."

# Copy paper
cp ../paper/main.pdf "$SUBMISSION_DIR/"
cp ../paper/*.tex "$SUBMISSION_DIR/"
cp ../paper/*.bib "$SUBMISSION_DIR/"

# Copy figures
cp -r ../figures "$SUBMISSION_DIR/"

# Create archive
cd "$SUBMISSION_DIR/.."
tar -czf "submission_$(date +%Y%m%d).tar.gz" "$(basename $SUBMISSION_DIR)"

echo "✓ Submission package created!"
echo "Location: $SUBMISSION_DIR"
EOF
    chmod +x "papers/$paper_dir/scripts/create_submission.sh"

    # Create sample Python analysis script
    cat > "papers/$paper_dir/src/plot_results.py" << 'EOF'
#!/usr/bin/env python3
"""
Generate plots for the paper
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Setup paths
DATA_DIR = Path(__file__).parent.parent / "data"
FIG_DIR = Path(__file__).parent.parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

def load_data():
    """Load the shared dataset"""
    data_file = DATA_DIR / "all_systems_merged.json"
    if data_file.exists():
        with open(data_file, 'r') as f:
            return json.load(f)
    else:
        print(f"Warning: {data_file} not found. Using sample data.")
        return generate_sample_data()

def generate_sample_data():
    """Generate sample data for demonstration"""
    return {
        'systems': ['System A', 'System B', 'System C'],
        'scores': [0.85, 0.78, 0.92],
        'tests': 127
    }

def plot_results():
    """Create main results figure"""
    data = load_data()
    
    plt.figure(figsize=(10, 6))
    
    if 'systems' in data and 'scores' in data:
        systems = data['systems']
        scores = data['scores']
        
        plt.bar(systems, scores, color=['#2E86AB', '#A23B72', '#F18F01'])
        plt.ylabel('Performance Score', fontsize=12)
        plt.xlabel('System', fontsize=12)
        plt.title('System Performance Comparison', fontsize=14, fontweight='bold')
        plt.ylim(0, 1.0)
        plt.grid(axis='y', alpha=0.3)
    else:
        # Fallback plot
        x = np.linspace(0, 10, 100)
        plt.plot(x, np.sin(x), label='Sample Data')
        plt.legend()
        plt.title('Placeholder Figure')
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'results.pdf', bbox_inches='tight', dpi=300)
    plt.close()
    print(f"✓ Saved: {FIG_DIR / 'results.pdf'}")

if __name__ == '__main__':
    print("Generating figures...")
    plot_results()
    print("Done!")
EOF
    chmod +x "papers/$paper_dir/src/plot_results.py"

    # Create analysis script
    cat > "papers/$paper_dir/src/analyze_data.py" << 'EOF'
#!/usr/bin/env python3
"""
Data analysis for the paper
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def analyze():
    """Run statistical analysis"""
    data_file = DATA_DIR / "all_systems_merged.json"
    
    if not data_file.exists():
        print(f"Data file not found: {data_file}")
        print("Please link the shared data first:")
        print(f"  cd {DATA_DIR} && ln -s ../../../shared/data/all_systems_merged.json .")
        return
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print(f"Loaded data with {len(data)} items")
    # Add your analysis here

if __name__ == '__main__':
    analyze()
EOF
    chmod +x "papers/$paper_dir/src/analyze_data.py"

done

echo -e "${GREEN}🔧 Creating shared resources...${NC}"

# Create shared Python utilities
cat > "shared/code/stats_utils.py" << 'EOF'
"""
Statistical utilities shared across papers
"""

import numpy as np
from scipy import stats

def compute_confidence_interval(data, confidence=0.95):
    """Compute confidence interval for data"""
    n = len(data)
    mean = np.mean(data)
    se = stats.sem(data)
    ci = se * stats.t.ppf((1 + confidence) / 2., n-1)
    return mean, ci

def cohen_d(group1, group2):
    """Compute Cohen's d effect size"""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

def bootstrap_ci(data, func=np.mean, n_bootstrap=10000, confidence=0.95):
    """Bootstrap confidence interval"""
    bootstrap_samples = np.random.choice(data, size=(n_bootstrap, len(data)), replace=True)
    bootstrap_stats = np.array([func(sample) for sample in bootstrap_samples])
    alpha = (1 - confidence) / 2
    return np.percentile(bootstrap_stats, [alpha*100, (1-alpha)*100])
EOF

cat > "shared/code/plot_utils.py" << 'EOF'
"""
Plotting utilities shared across papers
"""

import matplotlib.pyplot as plt
import seaborn as sns

# Set consistent style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.dpi'] = 300

# Color palette
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'neutral': '#6C757D'
}

def save_figure(fig, path, **kwargs):
    """Save figure with consistent settings"""
    fig.savefig(path, bbox_inches='tight', dpi=300, **kwargs)
    print(f"✓ Saved: {path}")

def format_axis(ax, xlabel=None, ylabel=None, title=None):
    """Apply consistent axis formatting"""
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3)
EOF

cat > "shared/code/data_loader.py" << 'EOF'
"""
Data loading utilities
"""

import json
from pathlib import Path

def load_shared_data(filename='all_systems_merged.json'):
    """Load data from shared directory"""
    # Try multiple possible paths
    possible_paths = [
        Path(__file__).parent.parent / 'data' / filename,
        Path('shared/data') / filename,
        Path('../../shared/data') / filename,
        Path('../../../shared/data') / filename,
    ]
    
    for path in possible_paths:
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
    
    raise FileNotFoundError(f"Could not find {filename} in any expected location")

def save_results(data, output_path):
    """Save analysis results"""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
EOF

# Create shared data README
cat > "shared/data/README.md" << 'EOF'
# Shared Data

This directory contains datasets used across multiple papers.

## Files

- `all_systems_merged.json` - Main dataset with 127 test cases
- `benchmarks/` - Additional benchmark datasets

## Usage

Papers can link to this data:

```bash
cd papers/YOUR_PAPER/data
ln -s ../../../shared/data/all_systems_merged.json .
```

Or copy it if modifications are needed:

```bash
cp ../../../shared/data/all_systems_merged.json .
```
EOF

echo -e "${GREEN}🛠️  Creating management tools...${NC}"

# Create tool: Build all papers
cat > "tools/build_all_papers.sh" << 'EOF'
#!/bin/bash

echo "Building all papers..."
for paper in papers/*/; do
    if [ -f "$paper/scripts/build.sh" ]; then
        echo "→ Building $(basename $paper)..."
        (cd "$paper" && bash scripts/build.sh)
    fi
done
echo "✓ All papers built!"
EOF
chmod +x "tools/build_all_papers.sh"

# Create tool: Create new paper
cat > "tools/create_new_paper.sh" << 'EOF'
#!/bin/bash

if [ $# -lt 3 ]; then
    echo "Usage: $0 <paper-id> <venue> <year>"
    echo "Example: $0 2026-ICLR ICLR 2026"
    exit 1
fi

PAPER_ID=$1
VENUE=$2
YEAR=$3

echo "Creating new paper: $PAPER_ID ($VENUE $YEAR)"

# Use template to create paper
cp -r templates/paper_template "papers/$PAPER_ID"

# Update README
sed -i "s/PAPER_ID/$PAPER_ID/g" "papers/$PAPER_ID/README.md"
sed -i "s/VENUE/$VENUE/g" "papers/$PAPER_ID/README.md"
sed -i "s/YEAR/$YEAR/g" "papers/$PAPER_ID/README.md"

echo "✓ Paper created at papers/$PAPER_ID"
EOF
chmod +x "tools/create_new_paper.sh"

# Create tool: Sync shared data
cat > "tools/sync_shared_data.sh" << 'EOF'
#!/bin/bash

echo "Syncing shared data to all papers..."
for paper in papers/*/; do
    if [ -d "$paper/data" ]; then
        echo "→ Syncing to $(basename $paper)..."
        cd "$paper/data"
        ln -sf ../../../shared/data/all_systems_merged.json . 2>/dev/null || true
        cd - > /dev/null
    fi
done
echo "✓ Data synced!"
EOF
chmod +x "tools/sync_shared_data.sh"

# Create tool: Check citations
cat > "tools/check_citations.py" << 'EOF'
#!/usr/bin/env python3
"""
Check for citation consistency across papers
"""

import re
from pathlib import Path

def extract_citations(bib_file):
    """Extract citation keys from .bib file"""
    with open(bib_file, 'r') as f:
        content = f.read()
    return set(re.findall(r'@\w+\{([^,]+),', content))

def main():
    papers_dir = Path('papers')
    all_citations = {}
    
    for paper in papers_dir.iterdir():
        if paper.is_dir():
            bib_file = paper / 'paper' / 'references.bib'
            if bib_file.exists():
                citations = extract_citations(bib_file)
                all_citations[paper.name] = citations
                print(f"{paper.name}: {len(citations)} citations")
    
    # Find common citations
    if len(all_citations) > 1:
        common = set.intersection(*all_citations.values())
        print(f"\nCommon citations across all papers: {len(common)}")
        for cite in sorted(common):
            print(f"  - {cite}")

if __name__ == '__main__':
    main()
EOF
chmod +x "tools/check_citations.py"

# Create tool: Generate statistics
cat > "tools/repo_stats.sh" << 'EOF'
#!/bin/bash

echo "Repository Statistics"
echo "===================="
echo ""
echo "Papers: $(ls -d papers/*/ 2>/dev/null | wc -l)"
echo "Shared code files: $(find shared/code -type f | wc -l)"
echo "Total LaTeX files: $(find papers -name "*.tex" | wc -l)"
echo "Total Python files: $(find . -name "*.py" | wc -l)"
echo ""
echo "Paper Status:"
for paper in papers/*/; do
    name=$(basename $paper)
    if [ -f "$paper/paper/main.pdf" ]; then
        status="✓ Built"
    else
        status="○ Not built"
    fi
    echo "  $name: $status"
done
EOF
chmod +x "tools/repo_stats.sh"

echo -e "${GREEN}📚 Creating documentation...${NC}"

# Create main README
cat > "README.md" << 'EOF'
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
EOF

# Create setup summary
cat > "docs/SETUP_SUMMARY.md" << 'EOF'
# Setup Summary

## What You Have

✅ **4 Paper Directories**
- `2025-JMLR` - Journal of Machine Learning Research
- `2025-NeurIPS` - Neural Information Processing Systems
- `2026-ICML` - International Conference on Machine Learning
- `2025-AAAI` - Association for the Advancement of Artificial Intelligence

Each paper has:
- Complete LaTeX structure
- Figure generation scripts
- Data analysis code
- Build automation
- Submission tools

✅ **Shared Resources**
- `shared/data/` - Common datasets
- `shared/code/` - Python utilities (stats, plotting, data loading)
- `shared/figures/` - Reusable components

✅ **Management Tools**
- `build_all_papers.sh` - Build all papers
- `create_new_paper.sh` - Generate new paper structure
- `sync_shared_data.sh` - Sync data to papers
- `check_citations.py` - Citation analysis
- `repo_stats.sh` - Repository statistics

## First Steps

1. **Add Your Data**
   ```bash
   cp /path/to/all_systems_merged.json shared/data/
   ```

2. **Choose a Paper to Work On**
   ```bash
   cd papers/2025-JMLR
   ```

3. **Link the Shared Data**
   ```bash
   cd data
   ln -s ../../../shared/data/all_systems_merged.json .
   cd ..
   ```

4. **Generate Sample Figures**
   ```bash
   bash scripts/generate_figures.sh
   ```

5. **Build the Paper**
   ```bash
   bash scripts/build.sh
   ```

## File Locations

- Papers: `papers/PAPER_NAME/`
- Shared data: `shared/data/`
- Shared code: `shared/code/`
- Tools: `tools/`
- Documentation: `docs/`

## Common Commands

```bash
# Build a specific paper
cd papers/2025-JMLR && bash scripts/build.sh

# Build all papers
bash tools/build_all_papers.sh

# Create new paper
bash tools/create_new_paper.sh "2026-CVPR" "CVPR" "2026"

# Check stats
bash tools/repo_stats.sh
```

## Next Steps

1. Read `QUICK_START_GUIDE.md` for detailed workflows
2. Customize paper templates for your research
3. Add your analysis code to `src/` directories
4. Generate figures and build papers
5. Create submission packages

## Support

For issues or questions, check:
- `README.md` - Main documentation
- `QUICK_START_GUIDE.md` - Detailed guide
- Paper-specific README files
EOF

# Create quick start guide
cat > "docs/QUICK_START_GUIDE.md" << 'EOF'
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
EOF

# Create structure visual
cat > "docs/STRUCTURE_VISUAL.md" << 'EOF'
# Repository Structure Visual Guide

## Directory Tree

```
LLM-HypatiaX-PAPERS/
│
├── papers/                          # 📄 Individual Research Papers
│   ├── 2025-JMLR/                  # JMLR Paper
│   │   ├── paper/                  # LaTeX source
│   │   │   ├── main.tex           # Main document
│   │   │   ├── references.bib     # Bibliography
│   │   │   └── Makefile           # Build automation
│   │   ├── figures/                # Generated figures (PDF)
│   │   │   └── results.pdf
│   │   ├── data/                   # Paper-specific data
│   │   │   └── all_systems_merged.json → ../../../shared/data/
│   │   ├── src/                    # Analysis scripts
│   │   │   ├── plot_results.py    # Figure generation
│   │   │   └── analyze_data.py    # Statistical analysis
│   │   ├── scripts/                # Automation
│   │   │   ├── build.sh           # Build paper
│   │   │   ├── generate_figures.sh # Generate all figures
│   │   │   └── create_submission.sh # Package for submission
│   │   ├── submission/             # Submission packages
│   │   │   └── 20260131/          # Dated submission
│   │   ├── reviews/                # Review responses
│   │   └── README.md              # Paper documentation
│   │
│   ├── 2025-NeurIPS/              # NeurIPS Paper (same structure)
│   ├── 2026-ICML/                  # ICML Paper (same structure)
│   └── 2025-AAAI/                  # AAAI Paper (same structure)
│
├── shared/                          # 🔧 Shared Resources
│   ├── data/                       # Common datasets
│   │   ├── all_systems_merged.json # Main dataset (127 tests)
│   │   └── README.md
│   ├── code/                       # Shared Python utilities
│   │   ├── stats_utils.py         # Statistical functions
│   │   ├── plot_utils.py          # Plotting utilities
│   │   └── data_loader.py         # Data loading helpers
│   └── figures/                    # Reusable figure components
│
├── tools/                           # 🛠️  Management Scripts
│   ├── build_all_papers.sh        # Build all papers at once
│   ├── create_new_paper.sh        # Generate new paper structure
│   ├── sync_shared_data.sh        # Sync data to all papers
│   ├── check_citations.py         # Citation consistency check
│   └── repo_stats.sh              # Repository statistics
│
├── docs/                            # 📚 Documentation
│   ├── SETUP_SUMMARY.md           # Setup overview
│   ├── QUICK_START_GUIDE.md       # Detailed workflows
│   └── STRUCTURE_VISUAL.md        # This file
│
├── templates/                       # 📋 Templates for new papers
│
└── README.md                        # Main documentation
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Shared Resources                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  shared/data/all_systems_merged.json (127 tests)    │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│          ┌────────────────┼────────────────┐                │
│          │                │                │                │
│          ▼                ▼                ▼                │
│    ┌─────────┐      ┌─────────┐     ┌─────────┐           │
│    │  JMLR   │      │ NeurIPS │     │  ICML   │           │
│    │  Paper  │      │  Paper  │     │  Paper  │           │
│    └─────────┘      └─────────┘     └─────────┘           │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│    ┌─────────┐      ┌─────────┐     ┌─────────┐           │
│    │ Figures │      │ Figures │     │ Figures │           │
│    └─────────┘      └─────────┘     └─────────┘           │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│    ┌─────────┐      ┌─────────┐     ┌─────────┐           │
│    │   PDF   │      │   PDF   │     │   PDF   │           │
│    └─────────┘      └─────────┘     └─────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Workflow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                     Paper Development Workflow                  │
└────────────────────────────────────────────────────────────────┘

1. DATA PREPARATION
   ┌─────────────────────────┐
   │ Add data to shared/data/│
   └────────────┬────────────┘
                │
                ▼
2. ANALYSIS
   ┌──────────────────────────────┐
   │ Write src/analyze_data.py    │
   │ Use shared/code utilities    │
   └────────────┬─────────────────┘
                │
                ▼
3. VISUALIZATION
   ┌──────────────────────────────┐
   │ Write src/plot_results.py    │
   │ Generate figures/            │
   └────────────┬─────────────────┘
                │
                ▼
4. WRITING
   ┌──────────────────────────────┐
   │ Edit paper/main.tex          │
   │ Add references.bib           │
   └────────────┬─────────────────┘
                │
                ▼
5. BUILD
   ┌──────────────────────────────┐
   │ bash scripts/build.sh        │
   │ → paper/main.pdf             │
   └────────────┬─────────────────┘
                │
                ▼
6. REVIEW & ITERATE
   ┌──────────────────────────────┐
   │ Review PDF                   │
   │ Make changes                 │
   │ Rebuild                      │
   └────────────┬─────────────────┘
                │
                ▼
7. SUBMISSION
   ┌──────────────────────────────┐
   │ bash scripts/                │
   │   create_submission.sh       │
   │ → submission/*.tar.gz        │
   └──────────────────────────────┘
```

## File Type Legend

```
📄 .tex     - LaTeX source files
📊 .pdf     - PDF documents and figures
🐍 .py      - Python analysis scripts
📋 .bib     - Bibliography files
⚙️  .sh      - Bash shell scripts
📝 .md      - Markdown documentation
📦 .json    - Data files
```

## Build System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Build Process                             │
└─────────────────────────────────────────────────────────────┘

   INPUT: paper/main.tex
          paper/references.bib
          figures/*.pdf
      │
      ▼
   ┌─────────────────┐
   │   pdflatex      │  First pass
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │    bibtex       │  Process citations
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │   pdflatex      │  Second pass
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │   pdflatex      │  Final pass
   └────────┬────────┘
            │
            ▼
   OUTPUT: paper/main.pdf
```

## Shared Code Usage

```
┌────────────────────────────────────────────────────────────┐
│              Using Shared Code in Papers                    │
└────────────────────────────────────────────────────────────┘

Paper Analysis Script (papers/PAPER/src/analyze_data.py):

   import sys
   sys.path.append('../../../shared/code')
              │
              │  Add shared code to Python path
              │
              ▼
   ┌──────────────────────────────────────┐
   │  from data_loader import             │
   │      load_shared_data                │
   │                                       │
   │  from stats_utils import             │
   │      compute_confidence_interval     │
   │                                       │
   │  from plot_utils import              │
   │      save_figure, COLORS             │
   └──────────────────────────────────────┘
              │
              │  Use functions in analysis
              │
              ▼
   Generate results & figures
```

## Symbolic Links

```
Papers use symbolic links to shared data:

papers/2025-JMLR/data/all_systems_merged.json
           │
           │ (symbolic link)
           │
           ▼
shared/data/all_systems_merged.json

Benefits:
✓ Single source of truth
✓ No data duplication
✓ Automatic updates
✓ Saves disk space
```

## Management Tools Overview

```
┌────────────────────────────────────────────────────────────┐
│                   Management Tools                          │
└────────────────────────────────────────────────────────────┘

build_all_papers.sh
   ↓
   For each paper in papers/:
      Run scripts/build.sh
   ↓
   All PDFs built

create_new_paper.sh
   ↓
   Input: paper-id, venue, year
   ↓
   Create directory structure
   Copy template files
   Update metadata
   ↓
   New paper ready

sync_shared_data.sh
   ↓
   For each paper in papers/:
      Create symlink to shared data
   ↓
   All papers have access to shared data

check_citations.py
   ↓
   For each paper:
      Parse references.bib
      Extract citation keys
   ↓
   Compare citations
   Show common citations
   ↓
   Citation analysis report
```

## Submission Package Structure

```
submission/20260131/
├── main.pdf              # Compiled paper
├── main.tex              # Source file
├── references.bib        # Bibliography
└── figures/              # All figures
    ├── results.pdf
    ├── comparison.pdf
    └── architecture.pdf

Compressed to:
submission_20260131.tar.gz
```

## Summary

### Key Principles

1. **Separation**: Each paper is independent
2. **Sharing**: Common resources in `shared/`
3. **Automation**: Scripts for repetitive tasks
4. **Consistency**: Templates ensure uniformity
5. **Flexibility**: Easy to add new papers

### File Counts

- Papers: 4 (expandable)
- Shared utilities: 3 Python modules
- Management tools: 5 scripts
- Documentation files: 4

### Disk Usage

- Each paper: ~500 KB (without data)
- Shared data: Variable (your dataset size)
- Total overhead: ~2-3 MB
EOF

echo -e "${GREEN}✅ Creating final touches...${NC}"

# Create .gitignore
cat > ".gitignore" << 'EOF'
# LaTeX
*.aux
*.bbl
*.blg
*.log
*.out
*.toc
*.lof
*.lot
*.fls
*.fdb_latexmk
*.synctex.gz

# Python
__pycache__/
*.py[cod]
*$py.class
.ipynb_checkpoints/

# Paper outputs (optionally track PDFs)
# papers/*/paper/*.pdf

# Build artifacts
*.tar.gz
*.zip

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/
*.swp
*.swo
*~
EOF

# Create VERSION file
cat > "VERSION" << 'EOF'
1.0.0
EOF

echo ""
echo -e "${BOLD}${GREEN}✨ Repository Created Successfully! ✨${NC}"
echo ""
echo -e "${BOLD}📦 Repository: $REPO_NAME${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}📚 What You Have:${NC}"
echo -e "   ✓ 4 Complete paper directories (JMLR, NeurIPS, ICML, AAAI)"
echo -e "   ✓ Shared resources system (data, code, figures)"
echo -e "   ✓ 5 Management tools"
echo -e "   ✓ Complete documentation suite"
echo -e "   ✓ Ready-to-use templates"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}🚀 Next Steps:${NC}"
echo ""
echo -e "   1. ${BLUE}Add your data:${NC}"
echo -e "      ${GREEN}cp /path/to/all_systems_merged.json $REPO_NAME/shared/data/${NC}"
echo ""
echo -e "   2. ${BLUE}Enter the repository:${NC}"
echo -e "      ${GREEN}cd $REPO_NAME${NC}"
echo ""
echo -e "   3. ${BLUE}Read the documentation:${NC}"
echo -e "      ${GREEN}cat README.md${NC}"
echo -e "      ${GREEN}cat docs/SETUP_SUMMARY.md${NC}"
echo ""
echo -e "   4. ${BLUE}Start working on a paper:${NC}"
echo -e "      ${GREEN}cd papers/2025-JMLR${NC}"
echo -e "      ${GREEN}bash scripts/build.sh${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}🛠️  Quick Commands:${NC}"
echo ""
echo -e "   ${BLUE}Build all papers:${NC}       ${GREEN}bash tools/build_all_papers.sh${NC}"
echo -e "   ${BLUE}Create new paper:${NC}       ${GREEN}bash tools/create_new_paper.sh \"2026-ICLR\" \"ICLR\" \"2026\"${NC}"
echo -e "   ${BLUE}Sync shared data:${NC}       ${GREEN}bash tools/sync_shared_data.sh${NC}"
echo -e "   ${BLUE}Repository stats:${NC}       ${GREEN}bash tools/repo_stats.sh${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BOLD}${GREEN}🎉 Your multi-paper research repository is ready to use!${NC}"
echo ""

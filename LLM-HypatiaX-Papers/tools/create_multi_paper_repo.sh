#!/bin/bash
# Script to create multi-paper repository structure
# Each paper gets its own directory

echo "Creating Multi-Paper Repository Structure..."
echo "============================================="
echo ""

BASE_DIR="LLM-HypatiaX-PAPERS"

# ============================================================================
# ROOT STRUCTURE
# ============================================================================

mkdir -p "$BASE_DIR"/{papers,shared/{data,figures,code,docs},tools,templates,.github/workflows}

echo "✓ Created root structure"

# ============================================================================
# SHARED RESOURCES (used across multiple papers)
# ============================================================================

cat > "$BASE_DIR/shared/README.md" << 'EOF'
# Shared Resources

Resources shared across multiple papers.

## Structure

- `data/` - Common datasets used by multiple papers
- `figures/` - Reusable figure components
- `code/` - Shared analysis code and utilities
- `docs/` - Common documentation

## Usage

Papers can reference shared resources via symlinks:
```bash
cd papers/2025-JMLR
ln -s ../../shared/data/benchmarks.json data/benchmarks.json
```
EOF

cat > "$BASE_DIR/shared/data/README.md" << 'EOF'
# Shared Data

Common datasets used across papers:

- `all_systems_merged.json` - Complete 5-system results (38 tests)
- `benchmarks/` - Standard benchmark datasets
- `expert_evaluation/` - Expert survey responses

Each paper can symlink or copy needed data.
EOF

cat > "$BASE_DIR/shared/code/README.md" << 'EOF'
# Shared Code

Reusable analysis code and utilities.

## Modules

- `statistical_analysis.py` - Common statistical functions
- `plotting_utils.py` - Shared plotting code
- `data_loaders.py` - Data loading utilities
- `metrics.py` - Evaluation metrics

## Usage

```python
import sys
sys.path.append('../../shared/code')
from statistical_analysis import run_analysis
```
EOF

# ============================================================================
# INDIVIDUAL PAPER DIRECTORIES
# ============================================================================

# Function to create a paper directory
create_paper_dir() {
    local paper_name=$1
    local paper_title=$2
    local venue=$3
    local year=$4
    
    echo "Creating paper: $paper_name..."
    
    PAPER_DIR="$BASE_DIR/papers/$paper_name"
    
    mkdir -p "$PAPER_DIR"/{paper,figures/{pdf,source},tables,data,src,scripts,submission,docs,compiled}
    
    # Paper-specific README
    cat > "$PAPER_DIR/README.md" << EOF
# $paper_title

**Venue**: $venue  
**Year**: $year  
**Status**: In preparation

## Quick Build

\`\`\`bash
cd paper
make
\`\`\`

## Contents

- \`paper/\` - LaTeX source files
- \`figures/\` - Paper-specific figures
- \`data/\` - Paper-specific data
- \`src/\` - Analysis code
- \`scripts/\` - Build automation
- \`submission/\` - Ready for submission

## Shared Resources

This paper uses shared resources from \`../../shared/\`
EOF

    # Paper Makefile
    cat > "$PAPER_DIR/paper/Makefile" << 'EOF'
PAPER = main
BIBTEX = bibliography

.PHONY: all clean view

all: $(PAPER).pdf

$(PAPER).pdf: $(PAPER).tex $(BIBTEX).bib
	pdflatex $(PAPER)
	bibtex $(PAPER)
	pdflatex $(PAPER)
	pdflatex $(PAPER)

clean:
	rm -f *.aux *.log *.out *.bbl *.blg *.toc

view: $(PAPER).pdf
	evince $(PAPER).pdf &
EOF

    # Build script
    cat > "$PAPER_DIR/scripts/build.sh" << 'EOF'
#!/bin/bash
set -e
echo "Building paper..."
cd ../paper && make
echo "✓ Paper built successfully"
EOF
    chmod +x "$PAPER_DIR/scripts/build.sh"
    
    # Data README
    cat > "$PAPER_DIR/data/README.md" << 'EOF'
# Paper-Specific Data

Data files specific to this paper.

For shared datasets, see `../../shared/data/`
EOF
}

# Create individual paper directories
create_paper_dir "2025-JMLR" \
    "HypatiaX: Hybrid Symbolic-Neural System for Scientific Equation Discovery" \
    "Journal of Machine Learning Research" \
    "2025"

create_paper_dir "2025-NeurIPS" \
    "Scaling Laws for Symbolic Regression with LLMs" \
    "NeurIPS" \
    "2025"

create_paper_dir "2026-ICML" \
    "Multi-Modal Equation Discovery" \
    "ICML" \
    "2026"

create_paper_dir "2025-AAAI" \
    "Explainable Scientific Discovery with Hybrid Systems" \
    "AAAI" \
    "2025"

# ============================================================================
# TEMPLATES (for creating new papers)
# ============================================================================

cat > "$BASE_DIR/templates/README.md" << 'EOF'
# Paper Templates

Templates for creating new papers.

## Create New Paper

```bash
bash create_new_paper.sh "Paper Title" "VENUE" "YEAR"
```

## Available Templates

- `jmlr/` - JMLR template
- `neurips/` - NeurIPS template  
- `icml/` - ICML template
- `aaai/` - AAAI template
- `arxiv/` - arXiv preprint template
EOF

mkdir -p "$BASE_DIR/templates"/{jmlr,neurips,icml,aaai,arxiv}

# ============================================================================
# TOOLS
# ============================================================================

cat > "$BASE_DIR/tools/README.md" << 'EOF'
# Tools

Utility scripts for managing the repository.

- `create_new_paper.sh` - Create a new paper directory
- `build_all_papers.sh` - Build all papers
- `sync_shared_data.sh` - Sync shared resources
- `check_citations.py` - Check citation consistency
EOF

cat > "$BASE_DIR/tools/create_new_paper.sh" << 'EOF'
#!/bin/bash
# Create a new paper directory

if [ $# -lt 3 ]; then
    echo "Usage: $0 <paper-name> <venue> <year>"
    echo "Example: $0 2026-ICLR ICLR 2026"
    exit 1
fi

PAPER_NAME=$1
VENUE=$2
YEAR=$3

echo "Creating new paper: $PAPER_NAME"
echo "Venue: $VENUE"
echo "Year: $YEAR"

# Create directory structure
mkdir -p "papers/$PAPER_NAME"/{paper,figures/{pdf,source},tables,data,src,scripts,submission,docs}

echo "✓ Paper directory created: papers/$PAPER_NAME"
echo "  Next: cd papers/$PAPER_NAME && ls"
EOF
chmod +x "$BASE_DIR/tools/create_new_paper.sh"

cat > "$BASE_DIR/tools/build_all_papers.sh" << 'EOF'
#!/bin/bash
# Build all papers in the repository

echo "Building all papers..."
echo "====================="

for paper_dir in papers/*/; do
    paper_name=$(basename "$paper_dir")
    echo ""
    echo "Building: $paper_name"
    
    if [ -f "$paper_dir/paper/Makefile" ]; then
        (cd "$paper_dir/paper" && make) || echo "  ✗ Build failed"
    else
        echo "  ⊘ No Makefile found"
    fi
done

echo ""
echo "✓ Build complete"
EOF
chmod +x "$BASE_DIR/tools/build_all_papers.sh"

# ============================================================================
# ROOT README
# ============================================================================

cat > "$BASE_DIR/README.md" << 'EOF'
# HypatiaX Papers Repository

Collection of research papers on the HypatiaX system.

[![Papers](https://img.shields.io/badge/Papers-4-blue.svg)](#papers)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📚 Papers

| Paper | Venue | Year | Status |
|-------|-------|------|--------|
| [Hybrid Symbolic-Neural System](papers/2025-JMLR/) | JMLR | 2025 | In Preparation |
| [Scaling Laws for Symbolic Regression](papers/2025-NeurIPS/) | NeurIPS | 2025 | In Preparation |
| [Multi-Modal Equation Discovery](papers/2026-ICML/) | ICML | 2026 | Planning |
| [Explainable Scientific Discovery](papers/2025-AAAI/) | AAAI | 2025 | Planning |

## 🗂️ Repository Structure

```
LLM-HypatiaX-PAPERS/
├── papers/                    # Individual paper directories
│   ├── 2025-JMLR/            # JMLR submission
│   ├── 2025-NeurIPS/         # NeurIPS submission
│   ├── 2026-ICML/            # ICML submission
│   └── 2025-AAAI/            # AAAI submission
│
├── shared/                    # Shared resources
│   ├── data/                 # Common datasets
│   ├── figures/              # Reusable figures
│   ├── code/                 # Shared analysis code
│   └── docs/                 # Common documentation
│
├── templates/                 # Paper templates
│   ├── jmlr/
│   ├── neurips/
│   └── icml/
│
└── tools/                     # Repository tools
    ├── create_new_paper.sh
    ├── build_all_papers.sh
    └── sync_shared_data.sh
```

## 🚀 Quick Start

### Build All Papers

```bash
bash tools/build_all_papers.sh
```

### Build Specific Paper

```bash
cd papers/2025-JMLR
bash scripts/build.sh
```

### Create New Paper

```bash
bash tools/create_new_paper.sh "2026-ICLR" "ICLR" "2026"
```

## 📊 Shared Data

All papers use common experimental results:
- 127 tests across 5 systems
- 100% pass rate
- Datasets in `shared/data/`

## 🔗 Related Repositories

- [HypatiaX Main Code](https://github.com/yourorg/LLM-HypatiaX-Colab)
- [Benchmarks](https://github.com/yourorg/HypatiaX-Benchmarks)
- [Documentation](https://hypatiax.readthedocs.io)

## 📝 Adding a New Paper

1. Create paper directory:
   ```bash
   bash tools/create_new_paper.sh "YEAR-VENUE" "VENUE" "YEAR"
   ```

2. Edit paper details in `papers/YEAR-VENUE/README.md`

3. Add LaTeX files in `papers/YEAR-VENUE/paper/`

4. Build:
   ```bash
   cd papers/YEAR-VENUE/paper && make
   ```

## 🤝 Contributing

Each paper directory is self-contained. See individual paper READMEs for details.

## 📧 Contact

- **Project**: HypatiaX
- **Maintainer**: [Your Name]
- **Email**: [your email]

## 📄 License

MIT License - see [LICENSE](LICENSE) file
EOF

# ============================================================================
# .gitignore
# ============================================================================

cat > "$BASE_DIR/.gitignore" << 'EOF'
# LaTeX
*.aux
*.log
*.out
*.bbl
*.blg
*.toc
*.lot
*.lof
*.synctex.gz

# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
*.egg-info/

# OS
.DS_Store
Thumbs.db

# IDEs
.vscode/
.idea/
*.swp

# Compiled outputs (keep PDFs in git)
# *.pdf  # Uncomment to ignore PDFs

# Temporary files
*~
*.bak
EOF

# ============================================================================
# LICENSE
# ============================================================================

cat > "$BASE_DIR/LICENSE" << 'EOF'
MIT License

Copyright (c) 2025 HypatiaX Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# ============================================================================
# GitHub Actions (CI/CD)
# ============================================================================

cat > "$BASE_DIR/.github/workflows/build-papers.yml" << 'EOF'
name: Build All Papers

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Install LaTeX
      run: |
        sudo apt-get update
        sudo apt-get install -y texlive-full
    
    - name: Build all papers
      run: |
        bash tools/build_all_papers.sh
    
    - name: Upload PDFs
      uses: actions/upload-artifact@v2
      with:
        name: papers
        path: papers/*/paper/*.pdf
EOF

# ============================================================================
# requirements.txt (root level)
# ============================================================================

cat > "$BASE_DIR/requirements.txt" << 'EOF'
# Python dependencies for all papers
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0
matplotlib>=3.5.0
seaborn>=0.11.0
scikit-learn>=1.0.0
EOF

# ============================================================================
# SUMMARY
# ============================================================================

echo ""
echo "============================================="
echo "✓ Multi-Paper Repository Created!"
echo "============================================="
echo ""
echo "Structure created:"
echo "  - 4 paper directories (2025-JMLR, 2025-NeurIPS, 2026-ICML, 2025-AAAI)"
echo "  - Shared resources folder"
echo "  - Templates for new papers"
echo "  - Tools for repository management"
echo ""
echo "Directory tree:"
tree -L 2 "$BASE_DIR" 2>/dev/null || find "$BASE_DIR" -maxdepth 2 -type d | sort
echo ""
echo "Next steps:"
echo "  1. cd $BASE_DIR"
echo "  2. ls papers/              # View all papers"
echo "  3. cd papers/2025-JMLR     # Work on specific paper"
echo "  4. bash ../../tools/build_all_papers.sh  # Build all"
echo ""
echo "To create a new paper:"
echo "  bash tools/create_new_paper.sh '2026-ICLR' 'ICLR' '2026'"
echo ""

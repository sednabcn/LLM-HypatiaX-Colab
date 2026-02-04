# 📚 Multi-Paper Repository Structure

## Overview

```
LLM-HypatiaX-PAPERS/                    # Root repository
│
├── 📄 papers/                          # Individual papers (each is independent)
│   │
│   ├── 2025-JMLR/                     # Paper 1: JMLR Submission
│   │   ├── paper/                     # LaTeX files
│   │   │   ├── main.tex
│   │   │   ├── bibliography.bib
│   │   │   ├── jmlr2e.sty
│   │   │   └── Makefile
│   │   ├── figures/                   # Paper-specific figures
│   │   │   ├── pdf/
│   │   │   └── source/
│   │   ├── tables/                    # LaTeX tables
│   │   ├── data/                      # Paper-specific data
│   │   ├── src/                       # Analysis code
│   │   ├── scripts/                   # Build scripts
│   │   │   └── build.sh
│   │   ├── submission/                # Submission package
│   │   ├── docs/                      # Paper documentation
│   │   ├── compiled/                  # Version history
│   │   └── README.md                  # Paper-specific README
│   │
│   ├── 2025-NeurIPS/                  # Paper 2: NeurIPS Submission
│   │   ├── paper/
│   │   ├── figures/
│   │   ├── data/
│   │   ├── src/
│   │   └── README.md
│   │
│   ├── 2026-ICML/                     # Paper 3: ICML Submission
│   │   ├── paper/
│   │   ├── figures/
│   │   ├── data/
│   │   ├── src/
│   │   └── README.md
│   │
│   └── 2025-AAAI/                     # Paper 4: AAAI Submission
│       ├── paper/
│       ├── figures/
│       ├── data/
│       ├── src/
│       └── README.md
│
├── 🔄 shared/                          # Shared across all papers
│   ├── data/                          # Common datasets
│   │   ├── all_systems_merged.json   # 38 tests, 5 systems
│   │   ├── benchmarks/
│   │   └── README.md
│   ├── figures/                       # Reusable figure components
│   │   └── common/
│   ├── code/                          # Shared utilities
│   │   ├── statistical_analysis.py
│   │   ├── plotting_utils.py
│   │   └── data_loaders.py
│   └── docs/                          # Common documentation
│       └── methodology.md
│
├── 📋 templates/                       # Templates for new papers
│   ├── jmlr/                          # JMLR template
│   ├── neurips/                       # NeurIPS template
│   ├── icml/                          # ICML template
│   ├── aaai/                          # AAAI template
│   ├── arxiv/                         # arXiv preprint
│   └── README.md
│
├── 🔧 tools/                           # Repository management
│   ├── create_new_paper.sh           # Create new paper directory
│   ├── build_all_papers.sh           # Build all papers
│   ├── sync_shared_data.sh           # Sync shared resources
│   └── check_citations.py            # Citation consistency
│
├── .github/                           # GitHub Actions CI/CD
│   └── workflows/
│       └── build-papers.yml          # Auto-build on push
│
├── requirements.txt                   # Python deps (all papers)
├── .gitignore                        # Git ignore rules
├── LICENSE                           # MIT License
└── README.md                         # Main repository README
```

---

## 📊 Papers Summary

| Directory | Paper Title | Venue | Year | Status |
|-----------|-------------|-------|------|--------|
| `2025-JMLR/` | Hybrid Symbolic-Neural System | JMLR | 2025 | In Preparation |
| `2025-NeurIPS/` | Scaling Laws for Symbolic Regression | NeurIPS | 2025 | In Preparation |
| `2026-ICML/` | Multi-Modal Equation Discovery | ICML | 2026 | Planning |
| `2025-AAAI/` | Explainable Scientific Discovery | AAAI | 2025 | Planning |

---

## 🎯 Key Design Principles

### 1. **Paper Independence**
Each paper directory is self-contained:
- Can be worked on independently
- Has its own build system
- Contains paper-specific data and code

### 2. **Shared Resources**
Common resources are centralized:
- Experimental data used by multiple papers
- Shared analysis code
- Reusable figure components

### 3. **Easy Navigation**
```bash
# Work on specific paper
cd papers/2025-JMLR

# Build specific paper
cd papers/2025-JMLR/paper && make

# Build all papers
bash tools/build_all_papers.sh
```

---

## 🚀 Common Workflows

### Create New Paper
```bash
cd LLM-HypatiaX-PAPERS
bash tools/create_new_paper.sh "2026-ICLR" "ICLR" "2026"
cd papers/2026-ICLR
```

### Build Single Paper
```bash
cd papers/2025-JMLR
bash scripts/build.sh
```

### Build All Papers
```bash
bash tools/build_all_papers.sh
```

### Use Shared Data
```bash
cd papers/2025-JMLR/data
ln -s ../../../shared/data/all_systems_merged.json .
```

---

## 📦 Each Paper Contains

```
papers/YEAR-VENUE/
├── paper/              # LaTeX source
│   ├── main.tex
│   ├── bibliography.bib
│   └── Makefile
├── figures/            # Paper figures
│   ├── pdf/           # Final PDFs
│   └── source/        # Generation scripts
├── tables/             # LaTeX tables
├── data/               # Paper-specific data
├── src/                # Analysis code
├── scripts/            # Automation
├── submission/         # Submission package
└── README.md           # Paper info
```

---

## 🔄 Shared Resources Usage

### Option 1: Symlink (recommended)
```bash
cd papers/2025-JMLR/data
ln -s ../../../shared/data/benchmarks.json .
```

### Option 2: Copy
```bash
cp ../../shared/data/benchmarks.json papers/2025-JMLR/data/
```

### Option 3: Direct import
```python
import sys
sys.path.append('../../../shared/code')
from statistical_analysis import run_analysis
```

---

## 🛠️ Repository Tools

### `tools/create_new_paper.sh`
```bash
bash tools/create_new_paper.sh "2026-ICLR" "ICLR" "2026"
```
Creates complete directory structure for new paper.

### `tools/build_all_papers.sh`
```bash
bash tools/build_all_papers.sh
```
Builds every paper in `papers/` directory.

### `tools/sync_shared_data.sh`
```bash
bash tools/sync_shared_data.sh
```
Updates shared data across all papers.

---

## 📋 Templates

Start new papers from venue-specific templates:

```bash
# Copy JMLR template
cp -r templates/jmlr/* papers/2026-JMLR/

# Copy NeurIPS template
cp -r templates/neurips/* papers/2025-NeurIPS/
```

Each template includes:
- Venue-specific LaTeX style files
- Sample paper structure
- Bibliography format
- Submission requirements

---

## 🔍 Finding Files

### All JMLR PDFs
```bash
find papers/2025-JMLR -name "*.pdf"
```

### All paper main.tex files
```bash
find papers -name "main.tex"
```

### All shared data
```bash
ls shared/data/
```

---

## 📊 Data Organization

### Shared Data (used by 2+ papers)
```
shared/data/
├── all_systems_merged.json      # Used by all papers
├── benchmarks/                   # Standard benchmarks
└── expert_evaluation/            # Survey data
```

### Paper-Specific Data
```
papers/2025-JMLR/data/
├── jmlr_specific_experiments.json
└── ablation_study.csv
```

---

## 🎓 Example: Adding a New Paper

```bash
# 1. Create paper directory
bash tools/create_new_paper.sh "2026-ICLR" "ICLR" "2026"

# 2. Navigate to paper
cd papers/2026-ICLR

# 3. Add LaTeX files
vim paper/main.tex

# 4. Link shared data
ln -s ../../shared/data/all_systems_merged.json data/

# 5. Build paper
cd paper && make

# 6. View PDF
evince main.pdf
```

---

## ✅ Checklist for Each Paper

### Setup
- [ ] Paper directory created
- [ ] README.md filled out
- [ ] Shared data linked
- [ ] LaTeX files added

### Development
- [ ] Figures generated
- [ ] Tables created
- [ ] Bibliography complete
- [ ] Paper compiles

### Submission
- [ ] All figures in PDF format
- [ ] Submission package created
- [ ] License checked
- [ ] Code/data available

---

## 🔗 Inter-Paper Dependencies

Some papers may build on others:

```
2025-JMLR (Foundation)
    ↓
2025-NeurIPS (Extensions)
    ↓
2026-ICML (Applications)
```

Track dependencies in each paper's README.

---

## 📈 Version Control

Each paper maintains its own version history:

```
papers/2025-JMLR/compiled/
├── v1.0/
│   └── main_v1.0.pdf
├── v1.1/
│   └── main_v1.1.pdf
└── final/
    └── main_final.pdf
```

---

## 🎯 Benefits of This Structure

1. ✅ **Independence** - Work on papers separately
2. ✅ **Shared Resources** - No data duplication
3. ✅ **Scalability** - Easy to add new papers
4. ✅ **Organization** - Clear hierarchy
5. ✅ **Automation** - Build scripts for all papers
6. ✅ **Templates** - Quick paper creation
7. ✅ **Version Control** - Track each paper separately

---

## 📧 Support

For questions about:
- **Repository structure**: See this document
- **Specific papers**: See paper's README.md
- **Shared resources**: See shared/README.md
- **Tools**: See tools/README.md

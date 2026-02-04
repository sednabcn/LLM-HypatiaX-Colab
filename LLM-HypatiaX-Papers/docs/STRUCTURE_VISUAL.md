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

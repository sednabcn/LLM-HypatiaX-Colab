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

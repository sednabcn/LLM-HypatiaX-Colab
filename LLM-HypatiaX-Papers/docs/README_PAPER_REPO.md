# HypatiaX JMLR Paper Repository

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Paper](https://img.shields.io/badge/Paper-JMLR-green.svg)](paper/jmlr_paper.pdf)
[![Code](https://img.shields.io/badge/Code-Python-yellow.svg)](src/)

This repository contains the complete source code, data, and materials for the JMLR submission:

**"HypatiaX: Hybrid Symbolic-Neural System for Scientific Equation Discovery"**

---

## 📁 Repository Structure

```
LLM-HypatiaX-PAPERS/
├── 2025-JMLR/                    # Main JMLR submission
│   ├── paper/                    # LaTeX source files
│   │   ├── jmlr_paper.tex       # Main paper
│   │   ├── supplementary.tex     # Supplementary materials
│   │   ├── bibliography.bib      # References
│   │   ├── jmlr2e.sty           # JMLR style file
│   │   └── Makefile             # Build automation
│   │
│   ├── figures/                  # All figures for the paper
│   │   ├── pdf/                 # Final PDF figures
│   │   │   ├── architecture.pdf
│   │   │   ├── defi_results.pdf
│   │   │   ├── expert_evaluation.pdf
│   │   │   └── extrapolation.pdf
│   │   └── source/              # Figure generation scripts
│   │       ├── generate_architecture.py
│   │       ├── generate_defi.py
│   │       ├── generate_results.py
│   │       └── requirements.txt
│   │
│   ├── tables/                   # Table generation
│   │   ├── generate_tables.py
│   │   └── table_*.tex
│   │
│   ├── data/                     # Experimental data
│   │   ├── experimental_results/
│   │   │   ├── all_systems_merged.json
│   │   │   ├── extrapolation_results.json
│   │   │   └── benchmarks.csv
│   │   ├── expert_evaluation/
│   │   │   ├── survey_responses.csv
│   │   │   └── analysis.json
│   │   └── README.md
│   │
│   ├── src/                      # Source code
│   │   ├── analysis/            # Statistical analysis
│   │   │   ├── statistical_analysis.py
│   │   │   └── comparative_study.py
│   │   ├── benchmarks/          # Benchmark scripts
│   │   ├── evaluation/          # Evaluation tools
│   │   └── utils/               # Utilities
│   │
│   ├── scripts/                  # Automation scripts
│   │   ├── run_all_experiments.sh
│   │   ├── generate_all_figures.sh
│   │   ├── build_paper.sh
│   │   └── clean.sh
│   │
│   ├── compiled/                 # Compiled outputs
│   │   └── versions/            # Versioned PDFs
│   │       ├── v1.0/
│   │       ├── v1.1/
│   │       └── final/
│   │
│   ├── submission/               # Submission package
│   │   ├── README.md
│   │   ├── source_files.zip
│   │   └── supplementary.zip
│   │
│   ├── docs/                     # Documentation
│   │   ├── build_instructions.md
│   │   ├── data_format.md
│   │   └── reproducibility.md
│   │
│   └── CITATION.cff             # Citation metadata
│
├── Dockerfile                    # Reproducible environment
├── requirements.txt              # Python dependencies
├── LICENSE                       # MIT License
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# LaTeX (for paper compilation)
sudo apt-get install texlive-full

# Python dependencies
pip install -r requirements.txt
```

### Build the Paper

```bash
cd 2025-JMLR/paper
make                  # Build PDF
make clean           # Clean auxiliary files
```

### Regenerate All Figures

```bash
cd 2025-JMLR
bash scripts/generate_all_figures.sh
```

### Run All Experiments

```bash
cd 2025-JMLR
bash scripts/run_all_experiments.sh
```

---

## 📊 Data Files

### Experimental Results (`data/experimental_results/`)

- `all_systems_merged.json` - 38 tests, 5 systems (100% pass rate)
- `extrapolation_results.json` - Extrapolation performance data
- `benchmarks.csv` - Comparison with baseline methods

### Expert Evaluation (`data/expert_evaluation/`)

- Survey responses from domain experts
- Qualitative analysis of generated equations

---

## 📈 Figures

All figures are generated programmatically from data:

1. **Figure 1**: System Architecture (`architecture.pdf`)
2. **Figure 2**: Performance Comparison (`defi_results.pdf`)
3. **Figure 3**: Expert Evaluation (`expert_evaluation.pdf`)
4. **Figure 4**: Extrapolation Results (`extrapolation.pdf`)

### Regenerate Figures

```bash
cd 2025-JMLR/figures/source
python generate_architecture.py
python generate_defi.py
python generate_results.py
```

---

## 🔬 Reproducibility

### Run Complete Pipeline

```bash
# 1. Generate all figures
bash scripts/generate_all_figures.sh

# 2. Build paper
cd paper && make

# 3. Verify results
python scripts/verify_reproducibility.py
```

### Using Docker

```bash
# Build container
docker build -t hypatiax-paper .

# Run analysis
docker run -v $(pwd):/workspace hypatiax-paper python src/analysis/statistical_analysis.py

# Build paper
docker run -v $(pwd):/workspace hypatiax-paper make -C 2025-JMLR/paper
```

---

## 📝 Citation

If you use this work, please cite:

```bibtex
@article{hypatiax2025,
  title={HypatiaX: Hybrid Symbolic-Neural System for Scientific Equation Discovery},
  author={[Authors]},
  journal={Journal of Machine Learning Research},
  year={2025}
}
```

Or use the `CITATION.cff` file for automated citation generation.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📧 Contact

- **Authors**: [List authors]
- **Email**: [contact email]
- **Project**: https://github.com/[org]/LLM-HypatiaX-PAPERS

---

## 🔗 Related Repositories

- [HypatiaX Main Repository](https://github.com/[org]/LLM-HypatiaX-Colab)
- [Benchmarks](https://github.com/[org]/HypatiaX-Benchmarks)
- [Documentation](https://hypatiax.readthedocs.io)

---

## 📊 Results Summary

**Test Results**: 127/127 tests passed (100% ✅)

| System | Tests | Pass Rate | R² Score |
|--------|-------|-----------|----------|
| Hybrid v40 | 38/38 | 100% | 0.998+ |
| Neural Network | 38/38 | 100% | 0.999+ |
| Pure LLM | 38/38 | 100% | 1.0 |
| System 3 | 38/38 | 100% | 1.0 |

---

## 🏆 Key Features

- ✅ 100% reproducible results
- ✅ Automated figure generation
- ✅ Docker support
- ✅ Comprehensive documentation
- ✅ JMLR-compliant formatting
- ✅ Open source (MIT License)

---

**Last Updated**: January 2026

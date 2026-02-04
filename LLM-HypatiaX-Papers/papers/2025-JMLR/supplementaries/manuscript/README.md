# HypatiaX: Hybrid Symbolic-Neural Framework - JMLR Manuscript

This directory contains the complete LaTeX manuscript for the HypatiaX paper submitted to JMLR (Journal of Machine Learning Research).

## Repository Structure

```
papers/2025-JMLR/latex/
├── hypatiax_manuscript.tex          # Main LaTeX manuscript
├── Bib/
│   ├── bibliography.bib             # Bibliography file with references
│   └── deduplication_bib.py         # Script to deduplicate bibliography entries
├── figures/                         # Generated figures (PDF and PNG)
│   ├── figure1_arrhenius.pdf
│   ├── figure2_domain_comparison.pdf
│   ├── figure3_validation.pdf
│   ├── figure4_extrapolation_heatmap.pdf
│   ├── figure5_method_comparison.pdf
│   ├── figure6_timing.pdf
│   └── table1_extrapolation_summary.csv
├── generate_figures.py              # Python script to generate all figures
└── *.csv                            # Source data files
```

## Compiling the Manuscript

### Prerequisites

```bash
# LaTeX distribution (TeX Live or MiKTeX)
sudo apt-get install texlive-full  # On Ubuntu/Debian

# Python packages for figure generation
pip install pandas matplotlib seaborn numpy
```

### Compilation Steps

1. **Generate figures** (if not already done):
```bash
python3 generate_figures.py
```

2. **Compile LaTeX**:
```bash
# First pass
pdflatex hypatiax_manuscript.tex

# Generate bibliography
bibtex hypatiax_manuscript

# Two more passes for cross-references
pdflatex hypatiax_manuscript.tex
pdflatex hypatiax_manuscript.tex
```

3. **Alternative**: Use the provided compile script:
```bash
chmod +x compile.sh
./compile.sh
```

## Manuscript Overview

**Title**: HypatiaX: A Hybrid Symbolic-Neural Framework for Scientific Discovery with Perfect Extrapolation

**Abstract**: This paper presents HypatiaX, a novel hybrid framework combining LLMs with symbolic regression to achieve perfect extrapolation (0.0% error) in scientific equation discovery, versus 1,231% error for pure neural networks. Evaluated across 131 tests in biology, chemistry, physics, and DeFi, HypatiaX achieves 95.8% success rate with mean discovery time of 390 seconds.

### Key Results

- **Zero extrapolation error**: 0.0% vs 1,231% for neural networks (U=0, p<10⁻⁶)
- **95.8% success rate**: Higher than Pure LLM (60%) or Pure PySR (80%)
- **4.3× speedup**: 390s vs 1,680s for pure symbolic methods
- **100% error coverage**: Multi-layer validation system

### Figures

1. **Figure 1**: Arrhenius equation extrapolation failure (neural vs HypatiaX)
2. **Figure 2**: Domain-wise performance comparison
3. **Figure 3**: Multi-layer validation breakdown (100% coverage)
4. **Figure 4**: Extrapolation error heatmap across 15 equations
5. **Figure 5**: Method comparison (success vs time trade-off)
6. **Figure 6**: Detailed timing analysis and speedup factors
7. **Figure 7**: HypatiaX 5-layer architecture (TikZ diagram in LaTeX)

### Tables

1. **Table 1**: Extrapolation error summary across all benchmarks
2. **Table 2**: Method comparison (in manuscript)
3. **Table 3**: Ablation study results (in manuscript)

## Data Files

All experimental data is provided in CSV format:

- `figure1_arrhenius_extrapolation.csv` - Arrhenius equation test data
- `figure2_domain_comparison.csv` - Performance by scientific domain
- `figure3_validation_breakdown.csv` - Validation layer statistics
- `figure4b_domain_breakdown.csv` - Detailed equation-by-equation results
- `figure5_method_comparison.csv` - Overall method comparison
- `figure_5systems_comparison.csv` - Extrapolation error data
- `figure_benchmark_comparison.csv` - Benchmark equations
- `figure_timing_comparison.csv` - Timing statistics

## Reproducing Results

To reproduce all figures from the data:

```bash
python3 generate_figures.py
```

This will:
1. Read all CSV data files
2. Generate 6 figures in both PDF and PNG format
3. Create summary table CSV
4. Save everything to the `figures/` directory

## Bibliography Management

The bibliography is managed in `Bib/bibliography.bib`. To deduplicate entries:

```bash
cd Bib
python3 deduplication_bib.py bibliography.bib
```

## LaTeX Template

This manuscript uses the JMLR template (`jmlr2e.sty`). Key commands:

- `\jmlrheading{volume}{year}{pages}{submitted}{published}{author}`
- `\ShortHeadings{short title}{short author}`
- `\firstpageno{page number}`

## Citation

If you use this work, please cite:

```bibtex
@article{hypatiax2025,
  title={HypatiaX: A Hybrid Symbolic-Neural Framework for Scientific Discovery with Perfect Extrapolation},
  author={Anonymous},
  journal={Submitted to JMLR},
  year={2025}
}
```

## Contact

For questions or issues with reproduction, please contact [to be added upon deanonymization].

## License

[To be determined upon publication]

---

**Note**: This is a submission for peer review. All author information is anonymized as per JMLR guidelines.

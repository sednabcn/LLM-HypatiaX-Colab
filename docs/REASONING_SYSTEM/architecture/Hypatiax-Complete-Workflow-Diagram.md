# HypatiaX Complete Analysis Workflow

## 🎯 Three-Phase Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 1: EXPERIMENTATION                    │
│                  (Generate Formula Discovery Results)           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
   [Baseline LLM]    [Baseline NN]        [Hybrid System]
        │                     │                     │
        ├─ baseline_pure_llm.py                    │
        ├─ baseline_pure_llm_defi.py               │
        │                     │                     │
        │              baseline_neural_network.py  │
        │              baseline_nn_defi.py         │
        │                     │                     │
        │                     │          hybrid_system_defi_domain.py
        │                     │          complete_defi_hybrid_system.py
        │                     │          complete_hybrid_system_all_domains.py
        ↓                     ↓                     ↓
    results/           results/              results/
    *llm*.json        *nn*.json            *hybrid*.json
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   PHASE 2: UNIFIED ANALYSIS                     │
│                    (Master Orchestrator)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    master_analyzer.py
                    [Auto-detects latest results]
                              │
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   TABLES     │    │   FIGURES    │    │   STATISTICS │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        ↓                   ↓                   ↓
generate_tables.py  generate_figures.py  hypatiax_hybrid_
                                         system_visualization.py
        │                   │                   │
        ↓                   ↓                   ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│• table1.csv  │    │• figure1.png │    │• plots/      │
│• table1.md   │    │• figure2.png │    │• stats.json  │
│• table1.tex  │    │• ...         │    │• tests/      │
│• (×4 tables) │    │• (×6 figures)│    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └─────────────────────┼─────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 PHASE 3: COMPREHENSIVE REPORTS                  │
│                     (All-in-One Analysis)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                 analyze_hybrid_results.py
                 [6 Plots + 4 Tables + Summary]
                              │
                              ↓
                    analysis_results/
                    ├── r2_distribution_analysis.png
                    ├── domain_performance.png
                    ├── extrapolation_analysis.png
                    ├── runtime_comparison.png
                    ├── validation_analysis.png
                    ├── decision_breakdown.png
                    ├── domain_comparison.csv
                    ├── extrapolation_comparison.csv
                    ├── decision_breakdown.csv
                    └── summary_report.txt
```

---

## 📊 Script Capabilities Matrix

| Script | Tables | Plots | Statistics | Formats | Best For |
|--------|--------|-------|------------|---------|----------|
| **master_analyzer.py** | ✅ (via modules) | ✅ (via modules) | ✅ (via modules) | ALL | **ONE-COMMAND ANALYSIS** |
| **analyze_hybrid_results.py** | ✅ (4) | ✅ (6) | Descriptive | CSV, PNG, TXT | **Post-experiment quick analysis** |
| **generate_tables.py** | ✅ (4) | ❌ | Basic | CSV, MD, LaTeX | **Academic papers** |
| **generate_figures.py** | ❌ | ✅ (6) | Descriptive | PNG | **Publications** |
| **hypatiax_hybrid_system_visualization.py** | ✅ (in JSON) | ✅ (6) | **Inferential** | PNG, JSON | **Research papers** |
| **hypatiax_visualizer.py** | ❌ | ✅ (5) | ❌ | PNG | **DeFi client reports** |

---

## 🚀 Usage Patterns

### Pattern 1: Quick Analysis (Post-Experiment)
```bash
# After running experiments
python analyze_hybrid_results.py --auto
```
**Output:** 6 plots + 4 tables + summary in `analysis_results/`

---

### Pattern 2: Publication-Ready (Academic Papers)
```bash
# Generate everything for papers
python master_analyzer.py --modules tables figures hybrid_viz

# Or individually:
python generate_tables.py          # → LaTeX tables
python generate_figures.py         # → Publication figures
python hypatiax_hybrid_system_visualization.py --all  # → Statistical tests
```
**Output:**
- `results/table*.{csv,md,tex}` - All tables in 3 formats
- `results/figure*.png` - 6 publication-quality figures
- `figures/*.png` - Statistical comparison plots
- `figures/statistical_analysis.json` - p-values, effect sizes

---

### Pattern 3: Complete Analysis (Everything)
```bash
# One command does it all
python master_analyzer.py --all --verbose
```
**Output:** Everything above + DeFi visualizations + master report

---

### Pattern 4: Specific Domain (DeFi)
```bash
# DeFi-specific client report
python hypatiax_visualizer.py
```
**Output:** 5 DeFi-focused plots in current directory

---

## 🔧 Detailed Workflow by Use Case

### 📖 **Academic Paper Preparation**

**Step 1:** Run experiments
```bash
python hybrid_system_defi_domain.py --mode full
# → results/improved_hybrid_20250124_142030.json
```

**Step 2:** Generate statistical analysis
```bash
python hypatiax_hybrid_system_visualization.py \
    --input results/improved_hybrid_*.json \
    --output-dir paper_analysis \
    --all
```
**Output:**
- Hypothesis tests (t-tests, Wilcoxon, Mann-Whitney)
- Effect sizes (Cohen's d)
- p-values and significance
- 6 comparison plots

**Step 3:** Generate tables and figures
```bash
python generate_tables.py    # LaTeX tables
python generate_figures.py   # Publication figures
```
**Output:**
- 4 tables in LaTeX format
- 6 publication-quality figures (300 DPI)

**Result:** Complete paper-ready materials! 📄

---

### 🔬 **Post-Experiment Quick Check**

**After experiments:**
```bash
python analyze_hybrid_results.py --auto
```

**What it does:**
1. Auto-detects latest results
2. Generates 6 comprehensive plots
3. Creates 4 comparison tables
4. Writes text summary report

**Output in `analysis_results/`:**
- All visualizations
- All tables
- `summary_report.txt` with recommendations

**Time:** ~2 minutes

---

### 📊 **Client Report (DeFi)**

**For DeFi clients:**
```bash
python hypatiax_visualizer.py
```

**Output:** 5 beautiful plots:
1. IL over time with fees
2. Price impact heatmap
3. Risk breakdown (bar + pie)
4. Scenario comparison (4 panels)
5. Backtest summary (6 panels)

**Customization:**
```python
from hypatiax_visualizer import HypatiaXVisualizer

viz = HypatiaXVisualizer()
viz.plot_il_over_time(your_data)
viz.plot_risk_score_breakdown(il, vol, range, days)
```

---

### 🎓 **Research Comparison Study**

**Compare 2+ architectures:**
```bash
# Run comparison
python test_real_hybrid_systems_comparison.py --mode full

# Analyze with statistics
python hypatiax_hybrid_system_visualization.py \
    --input comparison_results/comparison_*.json \
    --all
```

**Output:**
- Paired t-tests
- Wilcoxon signed-rank tests
- Effect size analysis
- Radar plots for validation layers
- Performance heatmaps

---

## 📁 Expected Directory Structure

```
hypatiax/
├── scripts/
│   ├── master_analyzer.py              ← **NEW: Master orchestrator**
│   ├── analyze_hybrid_results.py       ← **Best all-rounder**
│   ├── generate_tables.py              ← Publication tables
│   ├── generate_figures.py             ← Publication figures
│   ├── hypatiax_hybrid_system_visualization.py  ← Statistics
│   ├── hypatiax_visualizer.py          ← DeFi viz
│   ├── hybrid_system_defi_domain.py    ← Experiments
│   ├── baseline_pure_llm*.py           ← Baselines
│   └── baseline_neural_network*.py     ← Baselines
│
├── data/
│   └── results/
│       ├── *hybrid*.json               ← Experiment results
│       ├── *llm*.json
│       └── *nn*.json
│
└── analysis/                           ← **Auto-created by master**
    ├── master_report.json
    ├── tables/
    ├── figures/
    ├── hybrid_viz/
    └── analysis/
```

---

## 🎯 Decision Tree: Which Script to Use?

```
┌─ Need publication-ready materials?
│  ├─ YES → master_analyzer.py --modules tables figures hybrid_viz
│  └─ NO → Continue
│
├─ Need statistical hypothesis tests?
│  ├─ YES → hypatiax_hybrid_system_visualization.py --all
│  └─ NO → Continue
│
├─ Just finished experiment, want quick check?
│  ├─ YES → analyze_hybrid_results.py --auto
│  └─ NO → Continue
│
├─ Creating DeFi client report?
│  ├─ YES → hypatiax_visualizer.py
│  └─ NO → Continue
│
└─ Want everything automatically?
   └─ YES → master_analyzer.py --all
```

---

## 🔥 Pro Tips

### Tip 1: Always Use Master Analyzer First
```bash
# Let it detect and run everything
python master_analyzer.py --all
```
Then check `analysis/master_report.json` to see what succeeded.

### Tip 2: Chain Commands for Papers
```bash
# Complete paper pipeline
python hybrid_system_defi_domain.py --mode full && \
python master_analyzer.py --modules tables figures hybrid_viz && \
echo "✅ Paper materials ready!"
```

### Tip 3: Quick Diagnostic After Failures
```bash
# If experiment had issues
python analyze_hybrid_results.py --auto --verbose
# Check summary_report.txt for recommendations
```

### Tip 4: Compare Multiple Runs
```bash
# Generate comparison
python test_real_hybrid_systems_comparison.py

# Analyze comparison
python hypatiax_hybrid_system_visualization.py \
    --input comparison_results/comparison_*.json \
    --all

# Quick summary
python analyze_hybrid_results.py \
    --input comparison_results/comparison_*.json
```

---

## 📊 Output Formats Reference

### Tables
- **CSV** - Data analysis, Excel import
- **Markdown** - Documentation, GitHub README
- **LaTeX** - Academic papers

### Plots
- **PNG (300 DPI)** - Publications, presentations
- **JSON** - Statistical test results, metadata

### Reports
- **TXT** - Quick summaries, recommendations
- **JSON** - Programmatic access, further processing

---

## 🎓 Conclusion

**For most users:**
```bash
python master_analyzer.py --all
```

**For researchers:**
```bash
python master_analyzer.py --modules tables figures hybrid_viz
```

**For quick checks:**
```bash
python analyze_hybrid_results.py --auto
```

**Your codebase has EXCELLENT analysis capabilities** - they just need orchestration! 🚀

"""
2. Complete Workflow Diagram
A visual guide showing:

📊 Three-phase workflow (Experiment → Analyze → Report)
🎯 Script capability matrix
🚀 Usage patterns for different scenarios
🔧 Detailed workflows for academic papers, quick checks, client reports
📁 Directory structure
🎓 Decision tree for choosing the right script

Key Findings
Your codebase has EXCELLENT capabilities but needs orchestration:
StrengthGapSolution✅ Publication tables⚠️ Run separatelyMaster orchestrator✅ Statistical rigor⚠️ Distributed across scriptsUnified analysis✅ Multiple formats⚠️ No single entry pointCLI wrapper✅ Comprehensive plots⚠️ Manual coordinationAuto-detection
The master analyzer solves all these issues!
Would you like me to:

Create example output showing what each script produces?
Build a simplified quick-start guide?
Add more automation features (e.g., email reports, Slack notifications)?
"""

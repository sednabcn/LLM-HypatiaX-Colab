# Test Suite & Analysis Tools Comparison

## Overview

You have **three test suite implementations** for running symbolic regression experiments and **one analysis script** for comparing results. Here's a detailed breakdown of their purposes, features, and differences.

---

## 🔍 Quick Classification

### Test Suites (Run Experiments)
1. **standalone_real_methods_test.py** - Extrapolation-focused testing
2. **test_suite_comparative_v3.py** - Strategic LLM+PySR comparison
3. **ultimate_comparative_suite_complete_.py** - Comprehensive 9-method benchmark

### Analysis Tool (Analyze Results)
4. **comparison_analysis_improved.py** - Post-experiment LLM vs NN analysis

---

## 📋 Quick Reference Summary

| File | Type | Methods | Main Purpose | Key Output |
|------|------|---------|-------------|------------|
| **standalone_v4.py** | Test Suite | Multiple | Extrapolation testing | LaTeX tables, JSON |
| **comparative_v3.py** | Test Suite | 5 methods | LLM+PySR wins | JSON results |
| **ultimate_FIXED.py** | Test Suite | 9 methods | Comprehensive benchmark | JSON results |
| **analysis_improved.py** | **Analysis Tool** | 2 (analyzes) | **Results visualization** | **Plots, CSV, reports** |

---

## 1. **standalone_real_methods_test.py** (v4)

### Purpose
Standalone test suite that imports real methods directly with a **critical fix for extrapolation prediction issues**.

### Key Features
- ✅ **Fixed extrapolation predictions** - The main focus of v4
- Uses `TestResult._prediction_cache` to prevent cache conflicts
- Comprehensive extrapolation testing with three regimes (near/medium/far)
- Tests across multiple scientific domains (chemistry, biology, physics, DeFi)
- Built-in ground truth function registry

### Methods Tested
Not explicitly listed in the visible portion, but appears to test multiple methods with extrapolation capabilities.

### Unique Features
1. **Variable Name Sanitizer** - Handles PySR/Julia reserved names (S, N, C, D, E, I, O)
2. **Ground Truth Registry** - 15+ pre-defined scientific equations:
   - Chemistry: Arrhenius, Henderson-Hasselbalch, Rate Law
   - Biology: Allometric scaling, Michaelis-Menten, Logistic growth
   - Physics: Kinetic energy, Gravitational force, Ideal gas law
   - DeFi: Impermanent loss, Price impact, Constant product, VaR, etc.
3. **Extrapolation Testing Protocol** - Tests predictions beyond training range
4. **JMLR Paper Table Generation** - Formatted LaTeX output for research papers

### Technical Highlights
```python
# Critical fix in v4:
- Store prediction data in TestResult._prediction_cache
- Prevents cache conflicts when same wrapper runs multiple tests
- Enhanced error handling in _predict() methods
- Better filtering of inf values
```

### Usage
```bash
# Run ALL tests WITH extrapolation (FIXED!)
python standalone_real_methods_test.py --all --extrapolation

# Run specific domain with extrapolation
python standalone_real_methods_test.py --domain biology --extrapolation

# Run single test
python standalone_real_methods_test.py --test michaelis_menten --extrapolation
```

### Output
- JSON results with timestamp
- LaTeX table data for papers
- Domain-by-domain performance breakdown
- Extrapolation error metrics (near/medium/far)

---

## 2. **test_suite_comparative_v3.py** (v3)

### Purpose
Strategic comparative testing suite focused on **demonstrating when LLM-Guided PySR outperforms other methods**.

### Key Features
- Targeted strategic tests (not comprehensive)
- Uses experiment protocol for data generation
- Multiple API key search paths (robust .env loading)
- Detailed win/loss tracking for LLM+PySR

### Methods Tested (5 Methods)
1. **LLM-Guided PySR** (Hybrid approach - the focus)
2. **PySR + Validation** (Pure symbolic regression)
3. **Pure LLM Baseline** (No symbolic search)
4. **Neural Network** (Pure ML)
5. **LLM + NN Ensemble** (Hybrid ML)

### Strategic Test Categories
1. **Test 1**: Non-linear transformations (exp, log, power laws)
2. **Test 2**: Domain-specific formulas (scientific equations)
3. **Test 3**: Multi-variable interactions (product/ratio structures)
4. **Test 4**: DeFi domain (specialized financial formulas)
5. **Test 5**: Composite functions (multiple operations)

### Unique Features
1. **LLM Guidance Integration** - Gets operator suggestions before PySR search
2. **Validation Step** - LLM validates discovered formulas
3. **Domain Filtering** - Can run 'all_domains', 'defi', or specific domains
4. **Strategic Focus** - Designed to showcase LLM+PySR advantages
5. **Comprehensive .env Loading** - Checks multiple paths with detailed diagnostics

### Technical Configuration
```python
# Enhanced PySR settings for better performance
PySRRegressor(
    niterations=100,        # Increased from 40
    populations=15,         # Increased from 8
    population_size=50,     # Increased from 33
    maxsize=20,            # Increased from 15
    timeout_in_seconds=180 # Increased from 60
)
```

### Usage
```bash
# Run all tests
python test_suite_comparative_v3.py --samples 200 --verbose

# Run scientific domains only
python test_suite_comparative_v3.py --domain all_domains

# Run DeFi tests only
python test_suite_comparative_v3.py --domain defi
```

### Output
- Win/loss summary for LLM+PySR
- Detailed breakdown by test
- R² scores for each method
- JSON results with timestamp

---

## 3. **ultimate_comparative_suite_complete_.py** (FIXED)

### Purpose
The most comprehensive suite with **all bugs fixed** and **9 different methods** for thorough comparison.

### Key Features
- ✅ All bugs fixed from previous versions
- ✅ Removed duplicate Julia import
- ✅ Fixed bare exception handling
- ✅ Added error logging
- ✅ Safer exec() usage
- ✅ Better R² edge case handling
- Most comprehensive method comparison

### Methods Tested (9 Methods)
The file mentions "All 9 methods" with fixes, though the complete list isn't visible in the excerpt. Based on the structure, likely includes:
1. PySR (with Julia initialization fixes)
2. LLM code extraction (improved)
3. HybridSystem integration
4. Neural networks
5. LLM baselines
6. Ensemble methods
7-9. Additional comparative methods

### Unique Features
1. **Import Order Management** - Julia/PySR imported BEFORE PyTorch to avoid conflicts
2. **Graceful Fallbacks** - Advanced methods optional with fallback handling
3. **Safe R² Calculation** - Proper edge case handling:
   ```python
   def _safe_r2(self, y_true, y_pred):
       # Handles: invalid predictions, insufficient variance, constant values
       if not np.all(np.isfinite(y_pred)): return float("-inf")
       if ss_tot < 1e-10: return 1.0 if ss_res < 1e-10 else float("-inf")
   ```
4. **Multi-path Environment Setup** - Checks 4 different .env locations
5. **BaseMethod Class** - Standardized interface for all methods

### Technical Highlights
```python
# Availability flags for optional dependencies
PYSR_AVAILABLE = False
ADVANCED_METHODS_AVAILABLE = False
ANTHROPIC_AVAILABLE = False

# Graceful degradation if dependencies missing
```

### Usage
```bash
# Run specific domain
python ultimate_comparative_suite_complete_.py --domain chemistry

# Run single test
python ultimate_comparative_suite_complete_.py --test arrhenius

# Quiet mode
python ultimate_comparative_suite_complete_.py --domain physics --quiet
```

### Output
- Comprehensive results across all 9 methods
- Standardized MethodResult format
- JSON output with metadata
- Domain-specific breakdowns

---

## Comparison Matrix

| Feature | standalone_v4 | comparative_v3 | ultimate_FIXED |
|---------|---------------|----------------|----------------|
| **Primary Focus** | Extrapolation fixes | LLM+PySR wins | Comprehensive comparison |
| **Number of Methods** | Multiple (unspecified) | 5 methods | 9 methods |
| **Extrapolation Testing** | ✅ Yes (3 regimes) | ❌ No | Not visible |
| **Built-in Test Data** | ✅ Yes (Ground Truth Registry) | ❌ No (uses protocol) | ❌ No (uses protocol) |
| **Bug Fixes Focus** | Extrapolation caching | None specific | All bugs fixed |
| **LLM Integration** | Not visible | ✅ Yes (guidance + validation) | ✅ Yes (multiple methods) |
| **PySR Enhancements** | Not visible | ✅ Yes (better config) | ✅ Yes (Julia init fixes) |
| **LaTeX Output** | ✅ Yes (JMLR format) | ❌ No | Not visible |
| **Domain Filtering** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Error Handling** | Enhanced for predictions | Basic | Comprehensive |
| **Variable Sanitization** | ✅ Yes (PySR conflicts) | ❌ No | Not visible |
| **Graceful Degradation** | Not visible | Partial | ✅ Yes (full) |

---

## 4. **comparison_analysis_improved.py** (Analysis Tool)

### Purpose
**Post-experiment analysis tool** that compares Pure LLM vs Neural Network results across all domains. This is **NOT a test suite** - it analyzes results after experiments have been run.

### Key Features
- 📊 Comprehensive visualization (6+ plot types)
- 📈 Statistical analysis with pandas
- 🎯 Domain-specific performance breakdown
- 💾 Generates detailed reports (CSV, JSON, PNG)
- 🔍 Failure analysis and critical insights
- 📝 Automated recommendations

### What It Analyzes
- **Input**: Two JSON result files (LLM results + NN results)
- **Output**: Comparison plots, tables, and recommendations

### Analysis Components

#### 1. **Data Loading & Processing**
```python
# Flexible JSON structure handling
- Handles dict or list formats
- Extracts R², RMSE, domain, formula type
- Calculates winners for each test case
```

#### 2. **Visualizations Generated**

**Overall Comparison (`overall_comparison.png`):**
- R² distribution histograms (LLM vs NN)
- Head-to-head scatter plot
- Win rate pie chart
- Performance tier breakdown (excellent/good/poor)

**Domain Comparison (`domain_comparison.png`):**
- Mean R² by domain
- R² difference by domain
- Win counts by domain
- Count distribution

**Formula Type Comparison (`formula_type_comparison.png`):**
- Performance by formula complexity
- Advantage analysis per type

**Extrapolation Analysis (`extrapolation_analysis.png`):**
- Performance on extrapolation vs interpolation
- Error analysis

#### 3. **Statistical Reports**

**Comparison Tables:**
```
- Test-by-test comparison
- Domain statistics (mean, std, count)
- Formula type statistics
- Winner counts and percentages
```

**Critical Insights:**
- Cases where LLM dominantly outperforms (R² diff > 0.2)
- Cases where NN has advantage (R² diff < -0.1)
- Failure analysis (R² < 0.80)
- Catastrophic failures (R² < 0)

#### 4. **Automated Recommendations**

Based on actual performance metrics:
- Overall method preference (LLM vs NN vs comparable)
- Domain-specific recommendations
- Formula type recommendations
- Use case guidelines

### Unique Features

1. **Flexible File Search**
   - Auto-searches for latest result files
   - Multiple pattern matching
   - Interactive confirmation

2. **Robust Error Handling**
   ```python
   - Handles None/NaN values safely
   - Supports multiple JSON structures
   - Graceful degradation if data missing
   ```

3. **Beautiful Visualizations**
   - Seaborn styling
   - Color-coded winners
   - Professional plots with grid/labels
   - Multi-panel figures

4. **Comprehensive Metrics**
   - R² scores (mean, std, distribution)
   - RMSE analysis
   - Win/loss/tie statistics
   - Performance tiers
   - Domain & formula type breakdowns

### Usage

```bash
# With explicit files
python comparison_analysis_improved.py llm_results.json nn_results.json

# Auto-search mode
python comparison_analysis_improved.py
# (Will search for latest *llm*.json and *nn*.json files)
```

### Output Files Generated

1. **detailed_comparison.csv** - Full test-by-test comparison table
2. **summary_tables.txt** - Text-based statistics
3. **comparison_summary.json** - Machine-readable summary
4. **overall_comparison.png** - 4-panel overall comparison
5. **domain_comparison.png** - Domain-specific analysis
6. **formula_type_comparison.png** - Formula type analysis
7. **extrapolation_analysis.png** - Extrapolation performance

### Key Analysis Metrics

```python
Overall Performance:
- Mean R² (LLM vs NN)
- Standard deviation
- Win rates
- Performance tier distribution

By Domain:
- Mean R² per domain
- Win counts per domain
- R² advantage

By Formula Type:
- Performance on different formula complexities
- Method advantages per type

Failure Analysis:
- Poor performance cases (R² < 0.8)
- Catastrophic failures (R² < 0)
- Pattern identification
```

### When to Use This Tool

✅ **Use comparison_analysis_improved.py when:**
- You've already run experiments with LLM and NN methods
- You have JSON result files to compare
- You want publication-quality visualizations
- You need statistical validation of performance claims
- You want domain-specific insights
- You're writing a paper and need comparison plots

❌ **Don't use this tool when:**
- You need to RUN experiments (use test suites instead)
- You don't have result files yet
- You want to test methods other than LLM vs NN
- You need extrapolation testing (use standalone_v4)

### Integration with Test Suites

This analysis tool is designed to work with results from any test suite, but particularly:

```
1. Run experiments:
   → Use standalone_v4.py, comparative_v3.py, or ultimate_FIXED.py

2. Analyze results:
   → Use comparison_analysis_improved.py on the generated JSON files

3. Get insights:
   → Review plots, tables, and recommendations
```

### Example Workflow

```bash
# Step 1: Run LLM experiments
python test_suite_comparative_v3.py --domain all_domains
# Generates: results/strategic_tests_all_domains_*.json

# Step 2: Run NN experiments  
python ultimate_comparative_suite_complete_.py --domain all_domains
# Generates: results/nn_experiment_*.json

# Step 3: Analyze and compare
python comparison_analysis_improved.py \
    results/strategic_tests_all_domains_*.json \
    results/nn_experiment_*.json
# Generates: comparison_results/* (plots, tables, JSON)
```

---

## Comparison Matrix (Updated with Analysis Tool)

| Feature | standalone_v4 | comparative_v3 | ultimate_FIXED | analysis_tool |
|---------|---------------|----------------|----------------|---------------|
| **Type** | Test Suite | Test Suite | Test Suite | **Analysis Tool** |
| **Primary Focus** | Extrapolation fixes | LLM+PySR wins | Comprehensive comparison | **Results Analysis** |
| **Runs Experiments** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No (post-processing) |
| **Number of Methods** | Multiple | 5 methods | 9 methods | **2 methods** (LLM, NN) |
| **Generates Plots** | ❌ No | ❌ No | Not visible | ✅ Yes (6+ plots) |
| **Statistical Analysis** | Basic | Basic | Basic | ✅ Comprehensive |
| **Extrapolation Testing** | ✅ Yes (3 regimes) | ❌ No | Not visible | ✅ Analyzes it |
| **Built-in Test Data** | ✅ Yes | ❌ No | ❌ No | N/A (uses results) |
| **CSV Export** | ❌ No | ❌ No | Not visible | ✅ Yes |
| **Automated Recommendations** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Publication-Ready Plots** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Domain Breakdown** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes (visual) |
| **LaTeX Output** | ✅ Yes | ❌ No | Not visible | ❌ No |

---

## When to Use Each Tool (Updated)

### Use **standalone_real_methods_test.py** (v4) when:
- ✅ You need **extrapolation testing** beyond training data
- ✅ You want **ready-to-use ground truth functions**
- ✅ You're preparing **JMLR paper results**
- ✅ You need **variable name sanitization** for PySR
- ✅ You want to test **prediction quality at different distances**

### Use **test_suite_comparative_v3.py** when:
- ✅ You want to **demonstrate LLM+PySR advantages**
- ✅ You need **strategic test cases** showing method strengths
- ✅ You want **LLM guidance and validation** in the loop
- ✅ You're comparing **5 specific methods** (not comprehensive)
- ✅ You need **domain-specific filtering** (scientific vs DeFi)

### Use **ultimate_comparative_suite_complete_.py** when:
- ✅ You need the **most comprehensive comparison** (9 methods)
- ✅ You want **all known bugs fixed**
- ✅ You need **robust error handling** and edge cases covered
- ✅ You want **graceful fallbacks** when dependencies are missing
- ✅ You're doing a **thorough methods benchmark**

---

## Code Quality & Maturity

### standalone_v4
- **Maturity**: High (v4 indicates iteration)
- **Documentation**: Excellent (detailed comments on fixes)
- **Error Handling**: Enhanced for specific issues
- **Focus**: Specialized (extrapolation)

### comparative_v3
- **Maturity**: Medium (v3 indicates evolution)
- **Documentation**: Good (clear strategic focus)
- **Error Handling**: Basic
- **Focus**: Strategic (winning scenarios)

### ultimate_FIXED
- **Maturity**: High (explicitly "FIXED" version)
- **Documentation**: Good (bug fix changelog)
- **Error Handling**: Best (comprehensive safety)
- **Focus**: Comprehensive (all methods)

### Use **comparison_analysis_improved.py** (Analysis Tool) when:
- ✅ You have **existing result files** from LLM and NN experiments
- ✅ You need **publication-quality visualizations**
- ✅ You want **statistical validation** of performance claims
- ✅ You need **automated recommendations** based on results
- ✅ You're writing a **research paper** and need comparison plots
- ✅ You want **domain-specific** and **formula-type** breakdowns
- ✅ You need **failure analysis** and critical insights

---

## Recommendations

1. **For Research Papers**: 
   - Use **standalone_v4** for LaTeX tables and extrapolation
   - Then use **analysis_tool** for publication plots

2. **For Method Demonstrations**: 
   - Use **comparative_v3** to showcase LLM+PySR
   - Then use **analysis_tool** to visualize advantages

3. **For Comprehensive Benchmarking**: 
   - Use **ultimate_FIXED** for thorough 9-method comparison
   - Then use **analysis_tool** on LLM vs NN subsets

4. **For Production/Reliability**: 
   - Use **ultimate_FIXED** for robust error handling

5. **For Results Analysis**: 
   - Use **analysis_tool** on any existing result files

6. **Complete Workflow**:
   ```bash
   # 1. Run experiments (choose one):
   python standalone_v4.py --all --extrapolation
   python comparative_v3.py --domain all_domains
   python ultimate_FIXED.py --domain all_domains
   
   # 2. Analyze results:
   python comparison_analysis_improved.py \
       results/llm_results.json \
       results/nn_results.json
   
   # 3. Review outputs:
   - comparison_results/*.png (plots)
   - comparison_results/*.csv (data)
   - comparison_results/*.json (summary)
   ```

---

## 📊 Visual Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        YOUR WORKFLOW                             │
└─────────────────────────────────────────────────────────────────┘

STEP 1: CHOOSE YOUR TEST SUITE
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ standalone_v4    │  │ comparative_v3   │  │ ultimate_FIXED   │
│                  │  │                  │  │                  │
│ • Extrapolation  │  │ • LLM+PySR wins  │  │ • 9 methods      │
│ • LaTeX tables   │  │ • 5 methods      │  │ • Most robust    │
│ • Ground truths  │  │ • Strategic      │  │ • Bug-free       │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                      │
         └─────────────────────┼──────────────────────┘
                               ↓
                    RUN EXPERIMENTS
                    Generates JSON files
                               ↓
                    ┌─────────────────┐
                    │ Results Files:  │
                    │ • llm_*.json    │
                    │ • nn_*.json     │
                    │ • pysr_*.json   │
                    │ • hybrid_*.json │
                    └────────┬────────┘
                             ↓

STEP 2: ANALYZE RESULTS (OPTIONAL BUT RECOMMENDED)
                    ┌─────────────────────────┐
                    │ comparison_analysis.py  │
                    │                         │
                    │ Input: LLM + NN JSON    │
                    │                         │
                    │ Generates:              │
                    │ • Plots (.png)          │
                    │ • Tables (.csv)         │
                    │ • Reports (.txt)        │
                    │ • Summary (.json)       │
                    └────────┬────────────────┘
                             ↓

STEP 3: OUTPUTS
┌────────────────────────────────────────────────────────────────┐
│  FOR PAPERS:         FOR PRESENTATIONS:    FOR ANALYSIS:       │
│  • LaTeX tables      • PNG plots          • CSV data           │
│  • R² metrics        • Win/loss charts    • Statistical tests  │
│  • Extrapolation     • Domain comparisons • Failure analysis   │
└────────────────────────────────────────────────────────────────┘

TYPICAL WORKFLOWS:
═══════════════════════════════════════════════════════════════

Academic Paper:
  standalone_v4 → analysis_tool → LaTeX + Plots → Paper

Quick Benchmark:
  ultimate_FIXED → CSV export → Report

Method Showcase:
  comparative_v3 → analysis_tool → Presentation

Full Analysis:
  ultimate_FIXED → analysis_tool → Comprehensive Report
```

---

## Tool Synergy

### Optimal Combinations

**Academic Paper Workflow:**
```
standalone_v4 (extrapolation + LaTeX tables)
    ↓
analysis_tool (publication plots)
    ↓
Paper-ready results
```

**Benchmark Report:**
```
ultimate_FIXED (9 methods comprehensive)
    ↓
analysis_tool (LLM vs NN deep-dive)
    ↓
Complete performance report
```

**Method Comparison:**
```
comparative_v3 (strategic tests)
    ↓
analysis_tool (visual validation)
    ↓
Demonstration package
```

---

## Missing Information & Notes

Due to file truncation, the following details are incomplete:

### Test Suites (1-3):
1. **standalone_v4**: Complete method wrapper implementations (lines 236-1311 truncated)
2. **comparative_v3**: Complete method implementations (lines 219-824 truncated)
3. **ultimate_FIXED**: Complete method implementations (most of middle section not visible)

### Analysis Tool (4):
4. **analysis_improved.py**: Truncated visualization code (lines 206-627), but core functionality visible

To get a complete comparison of method implementations, you would need to examine the full files, particularly:
- Method wrapper classes in standalone_v4
- The 5 method implementations in comparative_v3
- All 9 method classes in ultimate_FIXED
- Full visualization code in analysis_improved.py

### Important Notes:

1. **analysis_improved.py is fundamentally different** - It's not a test suite but a post-processing analysis tool
2. **Test suites generate data** → **Analysis tool visualizes it**
3. **Complementary tools**: Test suites run experiments, analysis tool interprets results
4. **File compatibility**: Analysis tool expects specific JSON format from test suites (LLM vs NN comparison)

---

## 🎯 Decision Tree: Which Tool Should I Use?

```
START: What do you need to do?
│
├─❓ Do you need to RUN experiments?
│  │
│  YES → Continue below
│  │
│  ├─❓ Do you need extrapolation testing?
│  │  │
│  │  YES → USE: standalone_v4.py
│  │  │     ✅ Built-in ground truth functions
│  │  │     ✅ 3-regime extrapolation
│  │  │     ✅ LaTeX table output
│  │  │
│  │  NO → Continue below
│  │
│  ├─❓ How many methods do you want to test?
│  │  │
│  │  5 methods (strategic) → USE: comparative_v3.py
│  │  │                       ✅ Focus on LLM+PySR wins
│  │  │                       ✅ Strategic test cases
│  │  │                       ✅ Domain filtering
│  │  │
│  │  9 methods (comprehensive) → USE: ultimate_FIXED.py
│  │                               ✅ Most thorough
│  │                               ✅ Best error handling
│  │                               ✅ Graceful fallbacks
│  │
│  └─❓ Is this for production/high reliability?
│     │
│     YES → USE: ultimate_FIXED.py (most robust)
│     NO → USE: any test suite based on needs
│
└─❓ Do you need to ANALYZE existing results?
   │
   YES → USE: comparison_analysis_improved.py
   │     ✅ Publication-quality plots
   │     ✅ Statistical analysis
   │     ✅ Automated recommendations
   │     ✅ Domain/formula breakdowns
   │
   NO → You may need to run experiments first (see above)

QUICK ANSWERS:
═══════════════════════════════════════════════════════════════

"I need to test extrapolation"
  → standalone_v4.py --all --extrapolation

"I want to show LLM+PySR is better"
  → comparative_v3.py --domain all_domains --verbose
  → comparison_analysis_improved.py [results]

"I need the most complete benchmark"
  → ultimate_FIXED.py --domain all_domains
  → comparison_analysis_improved.py [results]

"I have result files and need plots"
  → comparison_analysis_improved.py llm_results.json nn_results.json

"I'm writing a research paper"
  → standalone_v4.py --all --extrapolation (for LaTeX tables)
  → comparison_analysis_improved.py (for plots)

"I need production-grade reliability"
  → ultimate_FIXED.py (best error handling)
```

---

## 📚 Quick Command Reference

```bash
# TEST SUITE 1: Extrapolation focus
python standalone_v4.py --all --extrapolation --samples 200

# TEST SUITE 2: Strategic LLM+PySR
python comparative_v3.py --domain all_domains --verbose

# TEST SUITE 3: Comprehensive 9-method
python ultimate_FIXED.py --domain chemistry --quiet

# ANALYSIS TOOL: Visualize results
python comparison_analysis_improved.py \
    results/llm_20240115_120000.json \
    results/nn_20240115_120000.json

# Or auto-search mode:
python comparison_analysis_improved.py
```

---

## 🎓 Summary

You have a **complete ecosystem** for symbolic regression benchmarking:

| Need | Tool | Output |
|------|------|--------|
| 🧪 **Run experiments** | Test suites (1-3) | JSON result files |
| 📊 **Analyze results** | Analysis tool (4) | Plots, tables, reports |
| 📄 **Academic paper** | standalone_v4 + analysis | LaTeX + figures |
| 🏆 **Method comparison** | comparative_v3 + analysis | Win/loss charts |
| 🔬 **Comprehensive study** | ultimate_FIXED + analysis | Full benchmark |

**Key Insight**: Test suites and analysis tool are **complementary**, not competing. Use test suites to generate data, then use the analysis tool to interpret and visualize it for maximum insight.


# Quick Start Guide: Pure LLM Formula Discovery Experiments

## Setup (One-time)

### 1. Install Dependencies
```bash
pip install anthropic numpy python-dotenv
```

### 2. Configure API Key
Create `.env` file in project root:
```bash
ANTHROPIC_API_KEY=your-key-here
```

### 3. File Structure
```
LLM-HypatiaX-PAPERS/
├── .env
└── hypatiax/core/generation/
    ├── baseline_pure_llm.py
    └── experiment_protocol.py
```

---

## Running Experiments

### Option 1: Quick Test (Recommended for first run)
**Time:** ~8 minutes | **Domains:** 2 | **Cases:** 8

```bash
cd ~/Downloads/GITHUB/LLM-HypatiaX-Colab
python hypatiax/core/generation/baseline_pure_llm.py --quick
```

**What it does:**
- Tests DeFi and Physics domains
- 4 test cases per domain
- Good for validating setup

---

### Option 2: Full Experiment
**Time:** ~20 minutes | **Domains:** 5 | **Cases:** 20

```bash
python hypatiax/core/generation/baseline_pure_llm.py --all
```

**What it does:**
- All 5 domains (DeFi, Risk, Physics, Economics, ML/Stats)
- 4 test cases per domain
- Full baseline evaluation

---

### Option 3: Specific Domains
**Time:** Variable

```bash
# Single domain
python hypatiax/core/generation/baseline_pure_llm.py --domain defi

# Multiple domains (comma-separated)
python hypatiax/core/generation/baseline_pure_llm.py --domain defi,risk,physics
```

**Available domains:**
- `defi` - Decentralized Finance
- `risk` - Risk Management
- `physics` - Classical Physics
- `economics` - Economics & Finance
- `ml_stats` - Machine Learning & Statistics

---

### Option 4: Generate Protocol Documentation
```bash
python hypatiax/core/generation/baseline_pure_llm.py --protocol
```

Creates: `docs/experiment_protocol.json`

---

## Understanding the Output

### During Execution

```
======================================================================
                     Pure LLM Baseline Evaluation                     
======================================================================

Testing 5 domains with 20 total test cases

======================================================================
                          Domain: DEFI                         
    Decentralized Finance - formulas for AMMs, lending...
======================================================================

[1/4] Impermanent loss in constant product AMM
  ⏱  Generated in 9.07s
  📝 Formula: IL = 2√r/(1+r) - 1...
  ✓ R² Score: 0.9998
  ✓ RMSE: 0.000123
```

**Symbols:**
- `⏱` Time to generate formula
- `📝` Human-readable formula
- `✓` Success
- `✗` Failure

---

### Output Files

#### 1. Results File
**Location:** `results/baseline_pure_llm_YYYYMMDD_HHMMSS.json`

```json
{
  "method": "pure_llm",
  "domain": "defi",
  "description": "Impermanent loss...",
  "formula": "IL = 2√r/(1+r) - 1",
  "latex": "IL = \\frac{2\\sqrt{r}}{1+r} - 1",
  "python_code": "def impermanent_loss(price_ratio): ...",
  "evaluation": {
    "success": true,
    "r2": 0.9998,
    "rmse": 0.000123,
    "mae": 0.000098
  },
  "generation_time": 9.07
}
```

#### 2. Experiment Report
**Location:** `results/experiment_report_YYYYMMDD_HHMMSS.json`

```json
{
  "overall": {
    "total_cases": 20,
    "successful": 18,
    "success_rate": 0.90,
    "mean_r2": 0.9542,
    "median_r2": 0.9687
  },
  "by_domain": {
    "defi": {
      "total": 4,
      "successful": 4,
      "success_rate": 1.0,
      "mean_r2": 0.9856
    }
  }
}
```

---

## Interpreting Results

### R² Score (Coefficient of Determination)

| R² Range | Interpretation | Action |
|----------|---------------|---------|
| **1.00** | Perfect fit | ✅ Excellent |
| **0.95 - 0.99** | Excellent fit | ✅ Publication quality |
| **0.90 - 0.95** | Very good fit | ✅ Good |
| **0.80 - 0.90** | Good fit | ⚠️ Acceptable |
| **< 0.80** | Poor fit | ❌ Needs investigation |

### Success Rate

| Rate | Status | Meaning |
|------|--------|---------|
| **> 85%** | Excellent | Most formulas work |
| **70% - 85%** | Good | Some challenges |
| **50% - 70%** | Fair | Significant issues |
| **< 50%** | Poor | Major problems |

---

## Common Issues & Solutions

### Issue 1: "ANTHROPIC_API_KEY environment variable not set"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify path in baseline_pure_llm.py
# Should go up 3 levels from hypatiax/core/generation/
```

### Issue 2: "No callable function found in Python code"

**Cause:** Claude didn't generate proper Python function

**Debug:**
```python
# Add verbose=True to see what was generated
metrics = baseline.test_formula_accuracy(result, X, y_true, verbose=True)
```

**Solution:** Check debug output, may need to adjust prompt

### Issue 3: "Execution error: only length-1 arrays..."

**Cause:** Function doesn't support numpy arrays

**Solution:** Already handled with fallback to element-wise evaluation

### Issue 4: Rate Limits

**Symptom:** HTTP 429 errors

**Solution:**
```python
# Increase delay in run_comprehensive_test()
time.sleep(2)  # Instead of time.sleep(1)
```

---

## Expected Performance

### By Domain (Predicted)

| Domain | Expected Success | Mean R² | Notes |
|--------|-----------------|---------|-------|
| **Physics** | 95% | 0.98 | Well-known formulas |
| **ML/Stats** | 90% | 0.96 | Common metrics |
| **Economics** | 85% | 0.92 | Some complex formulas |
| **Risk** | 80% | 0.90 | Domain-specific |
| **DeFi** | 75% | 0.88 | Most specialized |

### By Difficulty

| Difficulty | Expected Success | Mean R² |
|-----------|-----------------|---------|
| **Easy** | 95% | 0.98 |
| **Medium** | 80% | 0.92 |
| **Hard** | 60% | 0.85 |

---

## Next Steps After Running

### 1. Analyze Results
```bash
# View summary
cat results/experiment_report_*.json | jq '.overall'

# Check domain performance
cat results/experiment_report_*.json | jq '.by_domain'
```

### 2. Generate Visualizations
```python
# See figures/source/generate_results.py for plotting code
python figures/source/generate_results.py
```

### 3. Compare with Baselines
- Traditional symbolic regression (PySR)
- HypatiaX (your proposed method)
- Human expert formulas

### 4. Write Paper Section
Use results for "Baseline Comparison" section in paper

---

## Advanced Usage

### Custom Test Case

```python
from baseline_pure_llm import PureLLMBaseline
import numpy as np

baseline = PureLLMBaseline()

# Define your test
X = np.random.uniform(0, 10, 100).reshape(-1, 1)
y_true = 2 * X[:, 0] + 5

# Generate formula
result = baseline.generate_formula(
    description="Linear relationship with slope 2 and intercept 5",
    domain="mathematics",
    variable_names=["x"]
)

# Test accuracy
metrics = baseline.test_formula_accuracy(result, X, y_true)
print(f"R² Score: {metrics['r2']:.4f}")
```

### Batch Processing

```python
# Process multiple descriptions at once
descriptions = [
    "Compound annual growth rate",
    "Exponential decay",
    "Logistic growth function"
]

for desc in descriptions:
    result = baseline.generate_formula(desc, "mathematics")
    print(f"{desc}: R² = {result['evaluation']['r2']:.4f}")
```

---

## Troubleshooting Checklist

- [ ] API key is set in `.env`
- [ ] `.env` path is correct (3 levels up from script)
- [ ] All dependencies installed (`pip list | grep anthropic`)
- [ ] Internet connection working
- [ ] API key has credits remaining
- [ ] No firewall blocking api.anthropic.com

---

## Getting Help

**Error logs:**
```bash
# Run with Python error output
python baseline_pure_llm.py --all 2>&1 | tee experiment.log
```

**Debug mode:**
```python
# In baseline_pure_llm.py, set verbose=True
metrics = baseline.test_formula_accuracy(result, X, y_true, verbose=True)
```

**GitHub Issues:**
Include:
1. Error message
2. Python version (`python --version`)
3. Operating system
4. Output of `pip list | grep -E "anthropic|numpy"`

---

## Time Estimates

| Task | Time | Notes |
|------|------|-------|
| Setup | 5 min | One-time only |
| Quick test | 8 min | 2 domains, 8 cases |
| Full experiment | 20 min | 5 domains, 20 cases |
| Single domain | 4 min | 4 cases |
| Analysis | 30 min | Generate plots, interpret |
| **Total** | **~1 hour** | From setup to results |

---

## Resource Requirements

- **API Calls:** 20 (full experiment)
- **Cost:** ~$0.40 (at $0.02/call for Sonnet 4)
- **Disk Space:** < 1 MB for results
- **RAM:** < 100 MB
- **CPU:** Minimal (most time is API wait)

---

## Quick Commands Reference

```bash
# Full experiment
python baseline_pure_llm.py --all

# Quick test
python baseline_pure_llm.py --quick

# Specific domains
python baseline_pure_llm.py --domain defi,physics

# Generate docs
python baseline_pure_llm.py --protocol

# View results
cat results/experiment_report_*.json | jq

# Check status
ls -lh results/
```

---

**Ready to run?** Start with `--quick` to validate everything works!

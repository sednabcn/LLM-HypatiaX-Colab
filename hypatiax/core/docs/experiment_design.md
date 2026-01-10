# Pure LLM Formula Discovery: 5-Domain Experiment Protocol

**Version:** 1.0  
**Date:** December 2025  
**Paper:** LLM-HypatiaX JMLR 2025 Submission

---

## Executive Summary

This protocol evaluates Claude's ability to discover mathematical formulas from natural language descriptions without symbolic regression. We test across 5 diverse domains with 20 total test cases, measuring R² scores against ground truth formulas.

### Key Innovation
Pure LLM approach (no symbolic regression) for formula discovery using only natural language descriptions.

---

## 1. Experimental Domains

### Domain 1: DeFi (Decentralized Finance)
**Focus:** Blockchain financial protocols and mechanisms

| # | Test Case | Variables | Difficulty | Ground Truth |
|---|-----------|-----------|------------|--------------|
| 1 | Impermanent Loss | price_ratio | Medium | `2√r/(1+r) - 1` |
| 2 | Liquidation Price | leverage, entry_price, maint_margin | Medium | `entry*(1 - 1/L + m)` |
| 3 | AMM Invariant | token_x, token_y | Easy | `x * y` |
| 4 | Collateralization Ratio | collateral, debt | Easy | `collateral / debt` |

**Characteristics:**
- Domain-specific formulas unique to DeFi
- Mix of simple ratios and complex functions
- Real-world applications in Uniswap, Aave, etc.

---

### Domain 2: Risk Management
**Focus:** Financial risk metrics and portfolio theory

| # | Test Case | Variables | Difficulty | Ground Truth |
|---|-----------|-----------|------------|--------------|
| 1 | Value at Risk (95%) | mean, volatility | Easy | `μ - 1.645σ` |
| 2 | Sharpe Ratio | returns, rf_rate, volatility | Easy | `(r - rf) / σ` |
| 3 | Kelly Criterion | win_prob, win_loss_ratio | Medium | `(p*b - (1-p)) / b` |
| 4 | Portfolio Variance | w1, σ1, σ2, correlation | Hard | `w1²σ1² + w2²σ2² + 2w1w2σ1σ2ρ` |

**Characteristics:**
- Industry-standard risk metrics
- Tests multi-variable reasoning
- Portfolio variance is most complex (4 variables)

---

### Domain 3: Physics
**Focus:** Classical mechanics and motion

| # | Test Case | Variables | Difficulty | Ground Truth |
|---|-----------|-----------|------------|--------------|
| 1 | Kinetic Energy | mass, velocity | Easy | `0.5 * m * v²` |
| 2 | Gravitational PE | mass, height | Easy | `m * 9.81 * h` |
| 3 | Pendulum Period | length | Medium | `2π√(L/9.81)` |
| 4 | Centripetal Acceleration | velocity, radius | Easy | `v² / r` |

**Characteristics:**
- Well-established physical laws
- Tests transcendental functions (π, √)
- Universal constants (g = 9.81)

---

### Domain 4: Economics
**Focus:** Economic theory and financial mathematics

| # | Test Case | Variables | Difficulty | Ground Truth |
|---|-----------|-----------|------------|--------------|
| 1 | Continuous Compound Interest | principal, rate, time | Medium | `P * e^(rt)` |
| 2 | Present Value Annuity | payment, rate, periods | Hard | `PMT * (1 - (1+r)^(-n)) / r` |
| 3 | Price Elasticity | %Δqty, %Δprice | Easy | `%ΔQ / %ΔP` |
| 4 | Break-even Point | fixed_costs, price, var_cost | Easy | `FC / (P - VC)` |

**Characteristics:**
- Tests exponential functions
- Complex time-value-of-money calculations
- Business decision formulas

---

### Domain 5: ML & Statistics
**Focus:** Machine learning metrics and statistical measures

| # | Test Case | Variables | Difficulty | Ground Truth |
|---|-----------|-----------|------------|--------------|
| 1 | Standard Error | std_dev, sample_size | Easy | `σ / √n` |
| 2 | F1 Score | precision, recall | Easy | `2PR / (P + R)` |
| 3 | Coefficient of Variation | std_dev, mean | Easy | `(σ / μ) * 100` |
| 4 | Gini Impurity | prob_class1 | Medium | `1 - (p1² + p2²)` |

**Characteristics:**
- Common ML evaluation metrics
- Tests harmonic mean (F1)
- Statistical dispersion measures

---

## 2. Experimental Design

### 2.1 Methodology

```
For each test case:
1. Generate natural language description
2. Provide variable names to Claude
3. Claude generates: formula, LaTeX, Python code
4. Execute Python code on 100 test samples
5. Calculate R², RMSE, MAE metrics
6. Compare to ground truth
```

### 2.2 Evaluation Metrics

**Primary Metric:** R² (Coefficient of Determination)
- R² = 1.0: Perfect fit
- R² > 0.95: Excellent
- R² > 0.80: Good
- R² < 0.80: Poor

**Secondary Metrics:**
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- Success Rate (% of executable functions)

### 2.3 Sample Generation

- **Sample Size:** 100 per test case
- **Random Seed:** 42 (for reproducibility)
- **Distribution:** Uniform within realistic ranges
- **Special Cases:** Avoid division by zero, negative inputs for sqrt/log

---

## 3. Difficulty Classification

### Easy (10 cases)
- 1-2 variables
- Simple arithmetic operations
- Well-known formulas
- Examples: `x * y`, `x / y`, `x + y`

### Medium (7 cases)
- 2-3 variables
- Includes sqrt, powers, or transcendental functions
- Domain-specific knowledge
- Examples: `2√x/(1+x) - 1`, `2π√(L/g)`

### Hard (3 cases)
- 3+ variables
- Multiple operations and nested functions
- Complex mathematical relationships
- Examples: Portfolio variance, Present value annuity

---

## 4. Formula Type Classification

### Algebraic (12 cases)
Basic arithmetic: addition, subtraction, multiplication, division

### Polynomial (2 cases)
Powers and squared terms: `x²`, `x³`

### Transcendental (3 cases)
Square roots, exponentials, logarithms: `√x`, `e^x`, `ln(x)`

### Exponential (2 cases)
Exponential growth/decay: `P * e^(rt)`, `(1+r)^n`

### Mixed (1 case)
Combination of multiple types

---

## 5. Expected Outcomes

### Hypothesis 1: Domain-Specific Knowledge
**Prediction:** Claude will perform better on universal formulas (physics, statistics) than domain-specific formulas (DeFi, Kelly criterion).

**Rationale:** Training data likely contains more physics and statistics content.

### Hypothesis 2: Complexity
**Prediction:** Performance inversely correlates with difficulty:
- Easy: >90% success rate, R² > 0.95
- Medium: 70-90% success rate, R² > 0.85
- Hard: 50-70% success rate, R² > 0.70

### Hypothesis 3: Function Type
**Prediction:** Best performance on algebraic formulas, worst on exponential.

**Rationale:** Exponential formulas require precise mathematical constants (e, π).

---

## 6. Running the Experiment

### Quick Test (2 domains, ~8 minutes)
```bash
python baseline_pure_llm.py --quick
```

### Full Experiment (5 domains, ~20 minutes)
```bash
python baseline_pure_llm.py --all
```

### Specific Domain
```bash
python baseline_pure_llm.py --domain defi,physics
```

### Generate Protocol Documentation
```bash
python baseline_pure_llm.py --protocol
```

---

## 7. Output Files

### Results File
`results/baseline_pure_llm_TIMESTAMP.json`

Contains for each test case:
- Description and metadata
- Generated formula (text, LaTeX, Python)
- Evaluation metrics (R², RMSE, MAE)
- Execution time
- Error messages (if any)

### Experiment Report
`results/experiment_report_TIMESTAMP.json`

Contains:
- Overall statistics (success rate, mean R²)
- Performance by domain
- Performance by difficulty
- Performance by formula type

### Protocol Documentation
`docs/experiment_protocol.json`

Contains:
- Complete protocol specification
- All test cases with ground truth
- Metadata for each formula

---

## 8. Analysis Plan

### Quantitative Analysis
1. **Overall Performance**
   - Success rate across all domains
   - Distribution of R² scores
   - Correlation between difficulty and performance

2. **Domain Comparison**
   - Best/worst performing domains
   - Domain-specific insights

3. **Formula Type Analysis**
   - Performance by complexity
   - Error patterns

### Qualitative Analysis
1. **Error Analysis**
   - Common failure modes
   - Syntax vs semantic errors
   - Vectorization issues

2. **Formula Quality**
   - Correctness of mathematical notation
   - Variable naming conventions
   - Code quality and style

---

## 9. Baseline Comparison

This Pure LLM baseline will be compared against:

1. **HypatiaX** (proposed method)
   - LLM + Symbolic Regression
   - Expected to outperform on complex formulas

2. **Traditional Symbolic Regression**
   - PySR, GPLearn
   - No natural language understanding

3. **Human Experts**
   - Domain specialists
   - Gold standard for evaluation

---

## 10. Limitations and Considerations

### Limitations
1. **Sampling bias:** 100 samples may not cover full distribution
2. **Random seed:** Fixed seed ensures reproducibility but limits generalization
3. **Evaluation:** R² may not capture formula elegance or interpretability
4. **API rate limits:** Requires 1-second delay between requests

### Ethical Considerations
1. **Transparency:** All generated formulas are logged
2. **Reproducibility:** Fixed random seed and open source code
3. **Validation:** Ground truth formulas from authoritative sources

---

## 11. Success Criteria

**Minimum Viable Success:**
- Overall success rate > 70%
- Mean R² > 0.85 for successful cases
- At least 1 perfect (R² = 1.0) formula per domain

**Excellent Performance:**
- Overall success rate > 85%
- Mean R² > 0.95
- Success on all "easy" formulas

**Publication Quality:**
- Comprehensive analysis across all domains
- Clear insights on strengths/limitations
- Comparison with baselines

---

## 12. Timeline

| Phase | Duration | Description |
|-------|----------|-------------|
| Setup | 1 day | Protocol implementation and validation |
| Execution | 1 day | Run all experiments, collect data |
| Analysis | 2 days | Statistical analysis, visualization |
| Writing | 3 days | Paper section on baseline results |
| Review | 1 day | Verification and reproducibility check |

**Total:** ~1 week for complete baseline evaluation

---

## Appendix A: Variable Naming Conventions

- **DeFi:** `price_ratio`, `leverage`, `token_x_reserves`
- **Risk:** `returns`, `volatility`, `win_probability`
- **Physics:** `mass`, `velocity`, `length`
- **Economics:** `principal`, `rate`, `fixed_costs`
- **ML/Stats:** `precision`, `recall`, `sample_size`

Conventions:
- Snake_case for multi-word variables
- Descriptive names (avoid `x`, `y`, `z`)
- Units in name when ambiguous (`annual_rate`)

---

## Appendix B: Ground Truth Sources

- **DeFi:** Uniswap v2 whitepaper, Aave documentation
- **Risk:** "The Basics of Quantitative Risk Management" (standard textbook)
- **Physics:** Halliday & Resnick "Fundamentals of Physics"
- **Economics:** Mankiw "Principles of Economics"
- **ML/Stats:** Scikit-learn documentation, statistical textbooks

---

## Contact & Support

**Questions:** Open an issue in the GitHub repository  
**Paper:** See `paper/jmlr_paper.tex` for methodology details  
**Data:** All test data in `data/experimental_results/`

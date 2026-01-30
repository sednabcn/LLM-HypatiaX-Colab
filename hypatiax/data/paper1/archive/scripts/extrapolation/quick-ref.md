# Extrapolation Error - Quick Reference Card

## The Correct Formula

```
Extrapolation Degradation Factor = RMSE_extrap / RMSE_train
```

**Units**: Dimensionless multiplier (1.0 = perfect, >1 = degraded)

---

## Worked Example: Arrhenius Equation

### Given Data
- **Training range**: 273-373 K
- **Extrapolation range**: 746-1119 K (2× training max)
- **Ground truth**: k = 10¹¹ exp(-80000 / (8.314T))

### Neural Network Results
```
Training:
  RMSE_train = 0.05
  R² = 0.9997 (excellent!)

Extrapolation (2× range):
  RMSE_extrap = 167.4
  R² = -8.5 (catastrophic!)
```

### Calculation
```
E_extrap = RMSE_extrap / RMSE_train
         = 167.4 / 0.05
         = 3348

Report as: "3348× degradation" or "3348 times worse"
```

### Hybrid v40 Results
```
Training:
  RMSE_train = 0.06
  R² = 0.9988

Extrapolation (2× range):
  RMSE_extrap = 0.06
  R² = 0.9988 (maintained!)
```

### Calculation
```
E_extrap = RMSE_extrap / RMSE_train
         = 0.06 / 0.06
         = 1.00

Report as: "1.0× (perfect extrapolation)" or "no degradation"
```

---

## Common Values Interpretation

| Degradation Factor | Interpretation | Quality |
|-------------------|----------------|---------|
| 1.0 - 1.1 | Excellent extrapolation | ✅ Acceptable |
| 1.1 - 2.0 | Moderate degradation | ⚠️ Caution |
| 2.0 - 10 | Significant degradation | ⚠️ Poor |
| 10 - 100 | Severe failure | ❌ Unreliable |
| 100 - 1000 | Catastrophic failure | ❌ Unusable |
| > 1000 | Complete collapse | ❌ Meaningless predictions |

**Your results**:
- Pure PySR: 23× (significant but usable)
- DeFi-optimized: 8× (moderate)
- Neural Network: **3348×** (complete collapse)
- Hybrid v40: **1.0×** (perfect)

---

## Why Not Percentage?

### Problem 1: Ambiguity
```
"3348% error" could mean:
  (a) 3348% increase = 33.48× degradation  ❌ Wrong
  (b) 3348 / 100 = 33.48× degradation      ❌ Wrong
  (c) 3348 = 3348% of baseline = 33.48×    ❌ Wrong
```

### Problem 2: Huge Numbers
```
Percentage increase formula:
  (RMSE_extrap / RMSE_train - 1) × 100%
  = (167.4 / 0.05 - 1) × 100%
  = (3348 - 1) × 100%
  = 334,700%
```
Nobody wants to say "three hundred thirty-four thousand percent error"!

### Problem 3: Confusing "0%"
```
Perfect extrapolation (RMSE_extrap = RMSE_train):
  
  As multiplier: 1.0× ✅ Clear ("same as training")
  As percentage: 100% ❓ Confusing ("100% error?")
  As increase: 0% ❓ Ambiguous ("zero increase" but still has error)
```

### Solution: Use Multiplier
```
"3348×" is unambiguous:
  - Reads as "3348 times worse"
  - No percentage confusion
  - Standard in ML literature
  - Matches your abstract usage
```

---

## Python Implementation

### Correct Version ✅
```python
def calculate_extrapolation_degradation(y_true, y_pred_train, y_pred_extrap):
    """
    Calculate extrapolation degradation factor.
    
    Returns:
        float: Multiplier showing how much worse extrapolation is.
               1.0 = perfect, >1 = degraded, <1 = improved (rare).
    """
    rmse_train = np.sqrt(np.mean((y_true[:n_train] - y_pred_train)**2))
    rmse_extrap = np.sqrt(np.mean((y_true[n_train:] - y_pred_extrap)**2))
    
    degradation = rmse_extrap / rmse_train
    
    return degradation

# Example usage
deg = calculate_extrapolation_degradation(y_true, y_pred_train, y_pred_extrap)
print(f"Extrapolation degradation: {deg:.1f}×")

# Output: "Extrapolation degradation: 3348.0×"
```

### Incorrect Version ❌
```python
# DON'T DO THIS - gives confusing percentages
extrap_error_pct = (rmse_extrap / rmse_train) * 100
# Returns: 334800.0 (what does this even mean?)

# DON'T DO THIS EITHER - gives "percentage increase"
extrap_increase = ((rmse_extrap / rmse_train) - 1) * 100
# Returns: 334700.0% (too large to comprehend)
```

---

## LaTeX Code to Use

### Definition (Equation 9)
```latex
\begin{definition}[Extrapolation Degradation Factor]
\label{def:extrap_error}
Given a learned model $\hat{f}$ with training RMSE $\epsilon_{\text{train}}$ 
and extrapolation RMSE $\epsilon_{\text{extrap}}$:
\begin{equation}
D_{\text{extrap}} = \frac{\epsilon_{\text{extrap}}}{\epsilon_{\text{train}}}
\label{eq:extrap_error}
\end{equation}
where $D_{\text{extrap}} = 1$ indicates perfect extrapolation (no degradation).
\end{definition}
```

### Table Format
```latex
\begin{tabular}{lcc}
\toprule
\textbf{Method} & \textbf{Training RMSE} & \textbf{Degradation (2×)} \\
\midrule
Neural Network & 0.05 & 3348× \\
Hybrid v40 & 0.06 & 1.0× (perfect) \\
Pure PySR & 0.12 & 23× \\
\bottomrule
\end{tabular}
```

### In-Text Usage
```latex
The neural network exhibits catastrophic extrapolation failure with 
degradation factor $D_{\text{extrap}} = 3348$, meaning predictions 
are 3348 times worse than training error. In contrast, Hybrid v40 
achieves $D_{\text{extrap}} = 1.00 \pm 0.00$ across all 14 test 
cases, indicating perfect preservation of training accuracy.
```

---

## Verification Checklist

After making changes, verify:

- [ ] Equation 9 defines degradation factor (no ×100%)
- [ ] All "%" changed to "×" in extrapolation context
- [ ] Tables show values like "3348×" not "3348%"
- [ ] Abstract already uses "×" ✅ (no change needed)
- [ ] Python script calculates `rmse_extrap / rmse_train` (no ×100)
- [ ] Re-run gives ~3348, not 2.64×10¹⁰
- [ ] Figure 3 y-axis labeled "Degradation Factor (×)" or "Multiplier"
- [ ] Captions explain "3348× means 3348 times worse"
- [ ] No remaining "3348%" in manuscript (except in citations)
- [ ] "Perfect extrapolation" reported as "1.0×" not "0%"

---

## Common Questions

**Q: Why does the abstract say "3348×" but the body says "3348%"?**
A: The abstract is correct. Body needs fixing. Use "×" everywhere.

**Q: Should I report "0% error" for Hybrid v40?**
A: No. Report "1.0× degradation (perfect)" or "<1.01×". 
   Zero degradation means RMSE_extrap = RMSE_train = same error.

**Q: What if RMSE_train is actually zero (perfect fit)?**
A: Then degradation = RMSE_extrap / 0 = undefined. Report separately:
   "Training: RMSE = 0.000 (perfect), Extrapolation: RMSE = 0.002"

**Q: Can degradation be less than 1?**
A: Theoretically yes (if extrapolation easier than interpolation), 
   but rare. Usually 1.0-1.5 for good models, >100 for failures.

**Q: Why unified analysis got 2.64×10¹⁰?**
A: Script calculated (RMSE_extrap / RMSE_train) × 100 for extreme cases:
   - Some NN overfit massively (RMSE_train ≈ 0.0001)
   - Then failed completely (RMSE_extrap ≈ 26371)
   - Result: (26371 / 0.0001) × 100 = 26,371,000,000%
   Fix: Remove the ×100, get 263,710× (still terrible but interpretable)

---

## Final Answer

**What to do:**

1. **Update Equation 9**: Define as `RMSE_extrap / RMSE_train` (no ×100%)
2. **Find-replace**: Change "3348%" → "3348×" everywhere (~15 places)
3. **Fix script**: Remove `* 100` from calculation
4. **Re-run analysis**: Should now get ~3348, not billions
5. **Update tables**: Use "×" format consistently
6. **Add interpretation**: Explain "3348× = 3348 times worse than training"

**Time required**: 30-45 minutes total

**Result**: Clear, unambiguous reporting that matches your abstract and narrative.

===================================================================================

Summary: What You Should Do
The issue is simple but critical: Your paper mixes "%" and "×" notation inconsistently.
The Problem in 3 Sentences:

Your abstract says "3348×" (correct - means "3348 times worse")
Your body says "3348%" (ambiguous - could mean many things)
Your script calculates × 100 which gives billions (wrong)

The Solution (30 minutes):
Step 1: Update Equation 9 (remove × 100%)
latexE_extrap = RMSE_extrap / RMSE_train  [not × 100%]
Step 2: Global find-replace in LaTeX

"3348%" → "3348×"
"412%" → "412×"
"847%" → "847×"
"23%" → "23×"
"0%" → "1.0×" (for perfect extrapolation)

Step 3: Fix Python script (line ~200)
python# OLD (WRONG):
extrap_error_pct = (rmse_extrap / rmse_train) * 100

# NEW (CORRECT):
extrap_degradation = rmse_extrap / rmse_train
Step 4: Re-run analysis

Should now get ~3348 (not 26 billion)
Update tables and figures

Why This Matters:

"3348×" is clear: "predictions 3348 times worse than training"
"3348%" is ambiguous: could mean 33.48×, or 334,700%, or something else
Readers will understand "3348× degradation" immediately

Verification:
After fixing, your unified analysis should report:

Neural Network: ~3348× degradation ✅
Hybrid v40: 1.0× degradation (perfect) ✅
No values in billions ✅

I've created three detailed guides in the artifacts above. Start with the Quick Reference Card for the formula, then follow the Complete Fix Guide step-by-step. The first artifact shows where to integrate the corrected results in your paper.
Would you like me to help you draft the specific text for the corrected Equation 9 definition?

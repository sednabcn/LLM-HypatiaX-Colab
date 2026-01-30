# Extrapolation Error Calculation - Complete Fix Guide

## The Problem

Your paper has **three different ways** of reporting the same number:

### Version 1: Your Paper (Line ~2576, Table 9)
```
Neural Network: 3348% error at 2× training range
```

### Version 2: Your Narrative (Case Study, Line ~2875)
```
"At twice the training range (746 K), the neural network error reaches 3348×"
```

### Version 3: Unified Analysis Output
```
Neural Network: 2.637150e+10% (= 26,371,500,000%)
```

**These should all be the same number!** Let's figure out what happened.

---

## Understanding the Calculation

### Method A: Percentage Increase (WRONG for scientific papers)
```
Error = (RMSE_extrap / RMSE_train - 1) × 100%
```

**Example** (Arrhenius):
- RMSE_train = 0.05
- RMSE_extrap = 167.4
- Error = (167.4 / 0.05 - 1) × 100% = (3348 - 1) × 100% = 334,700%

**Problem**: This is "percentage increase" language (finance/business), not scientific error reporting.

---

### Method B: Ratio/Multiplier (CORRECT for your paper)
```
Error = RMSE_extrap / RMSE_train
```

**Example** (Arrhenius):
- RMSE_train = 0.05
- RMSE_extrap = 167.4
- Error = 167.4 / 0.05 = **3348×** (read as "3348 times worse")

**This matches your paper!** ✅

---

### Method C: Percentage Format (AMBIGUOUS)
```
Error = (RMSE_extrap / RMSE_train) × 100%
```

**Example** (Arrhenius):
- RMSE_train = 0.05
- RMSE_extrap = 167.4
- Error = (167.4 / 0.05) × 100% = 3348 × 100% = **334,800%**

**This is what the unified script calculated!** The 2.64×10¹⁰% suggests it did this to some extreme outliers.

---

## What Your Paper Actually Uses

Looking at your LaTeX (Definition 9, line ~2233):

```latex
\begin{definition}[Extrapolation Error]
E_{\text{extrap}} = \frac{\text{RMSE}(\hat{f}, \mathcal{D}_{\text{extrap}})}
                         {\text{RMSE}(\hat{f}, \mathcal{D}_{\text{train}})} 
                    \times 100\%
\end{definition}
```

**This is Method C** - which gives 334,800% for the Arrhenius example.

But your narrative says "3348%", which would require Method B without the ×100%.

---

## The Fix: Three Options

### Option 1: Remove ×100% (RECOMMENDED) ✅

**Change Equation 9 to:**
```latex
E_{\text{extrap}} = \frac{\text{RMSE}_{\text{extrap}}}{\text{RMSE}_{\text{train}}}
```

**Interpretation**: Report as **multiplier** (3348×, 412×, 847×)

**Update all text**:
- "3348%" → "3348× worse" or "3348-fold degradation"
- "412% error" → "412× extrapolation degradation"
- "0% error" → "1.0× (perfect extrapolation)"

**Pros**:
- Clear, unambiguous
- Standard in ML/statistics literature
- Matches your narrative usage
- Easier to understand (3348× = "3348 times worse")

**Cons**:
- Requires find-replace throughout paper (~15 instances)

---

### Option 2: Keep ×100% but Fix Interpretation

**Keep Equation 9 as-is**, but update all reported values:

- "3348%" → "334,800%" (Arrhenius case)
- "412%" → "41,200%" (GPT-4)
- "847%" → "84,700%" (some other case)
- "0%" → "100%" (perfect = baseline)

**Pros**:
- Equation matches reported values
- No equation changes needed

**Cons**:
- Huge percentages look ridiculous (334,800%!)
- "0% error" no longer makes sense (should be 100%)
- Confusing for readers

---

### Option 3: Use Relative Error (ALTERNATIVE)

**Change Equation 9 to:**
```latex
E_{\text{extrap}} = \frac{\text{RMSE}_{\text{extrap}} - \text{RMSE}_{\text{train}}}
                         {\text{RMSE}_{\text{train}}} \times 100\%
```

**Example** (Arrhenius):
- Error = (167.4 - 0.05) / 0.05 × 100% = **334,700%**

**Interpretation**: "Extrapolation RMSE is 334,700% larger than training RMSE"

**Pros**:
- Standard "percentage increase" formula
- 0% means perfect (no increase)

**Cons**:
- Still gives huge percentages
- Less intuitive than multiplier

---

## What Happened in Unified Analysis?

The script calculated:
```python
extrap_error = (RMSE_extrap / RMSE_train) * 100
```

For **extreme outliers** where RMSE_extrap is astronomical:
```
Example outlier:
RMSE_train = 0.001
RMSE_extrap = 263,715 (some catastrophic case)
Error = (263,715 / 0.001) × 100 = 26,371,500,000%
```

This is Method C applied to cases with:
- Very small training errors (overfitting)
- Huge extrapolation errors (complete failure)

---

## Recommended Action Plan

### Step 1: Choose Method B (Multiplier) ✅

**Why**: Clearest, matches your narrative, avoids huge percentages

### Step 2: Update Equation 9
```latex
\begin{definition}[Extrapolation Error]
\label{def:extrap_error}
The extrapolation degradation factor quantifies performance decay:
\begin{equation}
E_{\text{extrap}} = \frac{\text{RMSE}(\hat{f}, \mathcal{D}_{\text{extrap}})}
                         {\text{RMSE}(\hat{f}, \mathcal{D}_{\text{train}})}
\label{eq:extrap_error}
\end{equation}
\end{definition}

\textbf{Interpretation}:
\begin{itemize}
    \item $E_{\text{extrap}} = 1.0$: Perfect extrapolation (same error as training)
    \item $E_{\text{extrap}} = 3348$: Predictions 3348× worse than training
    \item $E_{\text{extrap}} > 1000$: Catastrophic failure
\end{itemize}
```

### Step 3: Global Find-Replace

**In your LaTeX file**, replace:
- `3348\%` → `3348×` or `3348-fold`
- `412\%` → `412×`
- `847\%` → `847×`
- `23\%` → `23×` (pure PySR)
- `8\%` → `8×` (DeFi-optimized)
- `0\%` → `0×` or `<1×` (Hybrid v40 - if truly zero, use "1.0×")

**Search pattern**: `(\d+)\\%(?=\s+(?:error|extrap|degradation))`

**Approximately 15-20 replacements needed**

### Step 4: Update All Tables

**Table 9** (Main extrapolation results, line ~2576):
```latex
\begin{tabular}{lccccc}
\toprule
\textbf{Method} & \textbf{Regime} & \textbf{Mean Error} & \textbf{Std Dev} & \textbf{n} & \textbf{p-value} \\
\midrule
HypatiaX v40    & Near (1.2×)   & \textbf{1.00×}  & 0.00    & 14/14 & \multirow{2}{*}{$<0.001$***} \\
Neural Network  & Near (1.2×)   & 1578×           & 1220    & 9/15  & \\
\midrule
HypatiaX v40    & Medium (2×)   & \textbf{1.00×}  & 0.00    & 14/14 & \multirow{2}{*}{$<0.001$***} \\
Neural Network  & Medium (2×)   & \textbf{3348×}  & 2995    & 7/15  & \\
\bottomrule
\end{tabular}
```

**Note**: If Hybrid truly has 0.0 RMSE_extrap (perfect fit), then Error = 0/RMSE_train = 0, which is confusing. Better to report as "1.00× (perfect)".

### Step 5: Update Abstract

**Current** (line ~40):
```latex
Neural networks similarly achieve perfect interpolation (15/15) yet exhibit 
extreme extrapolation collapse, with errors reaching $3348\times$ despite 
zero training error.
```

**This is already correct!** ✅ You used "×" in abstract, "%" in body. Fix body to match.

### Step 6: Fix Unified Analysis Script

**File**: `unified_analysis_script.py`

**Find** (around line 200-250):
```python
extrap_error_pct = (rmse_extrap / rmse_train) * 100
```

**Replace with**:
```python
extrap_degradation = rmse_extrap / rmse_train  # Multiplier, not percentage
```

**Update output**:
```python
print(f"Mean Error: {mean_error:.1f}×")  # Not "{mean_error:.1f}%"
```

### Step 7: Verify Consistency

**Run this check** on your LaTeX:
```bash
grep -n "extrap.*[0-9]\+%" jmlr_paper_rev.tex | grep -v "\\citep"
```

Should return **zero matches** after fix.

---

## Example: Arrhenius Case Study (Fixed)

**Before** (line ~2875):
```latex
At twice the training range (746 K), the neural network error reaches 3348×.
```

**After** (SAME - already correct!):
```latex
At twice the training range (746 K), the neural network error reaches 3348×.
```

**Just need to fix Equation 9 and tables to match!**

---

## What About "0% error"?

Your Hybrid v40 achieves **perfect extrapolation**. How to report?

### If literally RMSE_extrap = 0.0:
```
Error = 0.0 / 0.05 = 0× degradation
```
**Problem**: This sounds like "zero error" which is confusing.

### If RMSE_extrap ≈ RMSE_train:
```
Error = 0.05 / 0.05 = 1.0× degradation (perfect)
```
**Better**: "1.0× (no degradation)" or "<1.01× (negligible degradation)"

### Recommended phrasing:
```latex
HypatiaX v40 achieves \emph{perfect extrapolation} with degradation factor 
$E_{\text{extrap}} = 1.00 \pm 0.00$ across all 14 successful cases, 
indicating that extrapolation RMSE equals training RMSE.
```

---

## Summary Checklist

- [ ] **Update Equation 9**: Remove ×100%, define as multiplier
- [ ] **Global replace**: "%" → "×" for all extrapolation errors (~15 instances)
- [ ] **Update Table 9**: Use multiplier format (3348× not 3348%)
- [ ] **Fix unified_analysis_script.py**: Remove ×100 from calculation
- [ ] **Re-run analysis**: Verify numbers now match (should get ~3348, not 2.64×10¹⁰)
- [ ] **Update Figure 3**: Regenerate with multiplier format on y-axis
- [ ] **Add interpretation**: Explain "3348× means predictions 3348 times worse"
- [ ] **Verify abstract**: Already uses "×", keep it ✅
- [ ] **Update captions**: Change "3348% error" → "3348× degradation"
- [ ] **Proofread**: Check no remaining "%" in extrapolation context

---

## Final Recommendation

**Use Method B (Multiplier)** throughout:
- Equation 9: Remove ×100%
- All text: "3348×" not "3348%"
- Interpretation: "3348 times worse" or "3348-fold degradation"
- Tables: Show values like "3348×" in error columns

This matches your abstract, is clearest for readers, and avoids the percentage ambiguity entirely.

**Estimated time to fix**: 30-45 minutes
- Equation update: 5 min
- Find-replace: 10 min  
- Table updates: 15 min
- Script fix + re-run: 10 min
- Verification: 5 min

**Start with**: Update Equation 9, then global find-replace, then verify tables match.

# Simple 3-Step Fix for Extrapolation Error

## The Problem
Your paper says "3348%" but it should say "3348×" (3348 times worse).

---

## Step 1: Fix Equation 9 (Line ~2233)

### REPLACE THIS:
```latex
\begin{definition}[Extrapolation Error]
\label{def:extrap_error}
Given a learned model $\hat{f}$ with training RMSE $\text{RMSE}_{\text{train}}$ 
and extrapolation test set $\mathcal{D}_{\text{extrap}}$:
\begin{equation}
E_{\text{extrap}} = \frac{\text{RMSE}(\hat{f}, \mathcal{D}_{\text{extrap}})}
                         {\text{RMSE}(\hat{f}, \mathcal{D}_{\text{train}})} 
                    \times 100\%
\label{eq:extrap_error}
\end{equation}
\end{definition}
```

### WITH THIS:
```latex
\begin{definition}[Extrapolation Degradation]
\label{def:extrap_error}
Given a learned model $\hat{f}$ with training RMSE $\text{RMSE}_{\text{train}}$ 
and extrapolation test set $\mathcal{D}_{\text{extrap}}$:
\begin{equation}
E_{\text{extrap}} = \frac{\text{RMSE}(\hat{f}, \mathcal{D}_{\text{extrap}})}
                         {\text{RMSE}(\hat{f}, \mathcal{D}_{\text{train}})}
\label{eq:extrap_error}
\end{equation}
where $E_{\text{extrap}} = 1.0$ indicates perfect extrapolation.
\end{definition}

\textbf{Interpretation}:
\begin{itemize}
    \item $E_{\text{extrap}} = 1.0$: Same error as training (perfect)
    \item $E_{\text{extrap}} = 3348$: Predictions 3348× worse than training
    \item $E_{\text{extrap}} > 100$: Catastrophic failure
\end{itemize}
```

**What changed**: Removed `× 100%` and added interpretation.

---

## Step 2: Find-Replace in LaTeX

Use your text editor to replace:

| Find | Replace |
|------|---------|
| `3348\%` | `3348×` |
| `412\%` | `412×` |
| `847\%` | `847×` |
| `23\%` | `23×` |
| `8\%` | `8×` |
| `0\%` (extrapolation context only) | `1.0×` |

**About 15 replacements** total.

---

## Step 3: Fix Python Script

**File**: `unified_analysis_script.py`

**Find** (around line 200-250):
```python
extrap_error_pct = (rmse_extrap / rmse_train) * 100
```

**Replace with**:
```python
extrap_degradation = rmse_extrap / rmse_train  # Multiplier, not %
```

**Then re-run**:
```bash
python unified_analysis_script.py
```

Should now show **3348×** instead of 26 billion%.

---

## Done!

Your paper will now consistently report extrapolation as **multipliers** (3348×) 
instead of confusing percentages (3348%).

**Time**: 30 minutes  
**Impact**: Fixes major inconsistency

"""Shared statistical metrics used across analysis scripts.
 
Extracted from statistical_analysis_full.py and hybrid_system_v40.py
to eliminate duplication (audit finding §5).
"""
import numpy as np
from scipy import stats
 
def compute_r2(y_true, y_pred) -> float:
    """Coefficient of determination R²."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot != 0 else 0.0
 
def compute_rmse(y_true, y_pred) -> float:
    """Root mean squared error."""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
 
def mann_whitney(a, b) -> dict:
    """Mann-Whitney U test. Returns stat, p-value, and effect size."""
    stat, p = stats.mannwhitneyu(a, b, alternative='two-sided')
    n1, n2 = len(a), len(b)
    r = stat / (n1 * n2)  # rank-biserial correlation
    return {'statistic': float(stat), 'p_value': float(p), 'effect_size_r': float(r)}
 
def spearman(a, b) -> dict:
    """Spearman rank correlation."""
    rho, p = stats.spearmanr(a, b)
    return {'rho': float(rho), 'p_value': float(p)}

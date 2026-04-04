"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         VaR BACKTESTING ENGINE — MRM PORTFOLIO ARTEFACT 3                  ║
║         Ruperto Pedro Bonet Chaple | February 2026                          ║
║                                                                              ║
║  WHAT THIS IS:                                                               ║
║  An independent parametric VaR backtesting engine applied to real           ║
║  S&P 500 daily return data. Implements the Basel Committee traffic light     ║
║  framework (BCBS 1996) for assessing VaR model performance.                 ║
║                                                                              ║
║  WHY IT EXISTS (MRM CONTEXT):                                                ║
║  This script is Artefact 3 in the HypatiaX → Banking bridge project.        ║
║  It demonstrates SR 11-7 Element 3 (Outcomes Analysis / Backtesting)        ║
║  and SS1/23 Principle 4(c) (ongoing model performance monitoring).           ║
║                                                                              ║
║  CONNECTION TO HypatiaX:                                                     ║
║  HypatiaX Campaign 1 tested whether LLMs could recover the VaR formula:     ║
║      VaR_0.95 = -μ + σ · Φ⁻¹(0.95) = -μ + 1.645σ                          ║
║  The LLM used z = -1.645 (wrong sign), producing R² = -10.05.               ║
║  This script applies the CORRECT formula to real data and tests whether      ║
║  its predictions match actual outcomes — i.e., real backtesting.            ║
║                                                                              ║
║  REQUIREMENTS:                                                               ║
║      pip install yfinance pandas numpy scipy matplotlib                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ─── Try to import optional libraries ─────────────────────────────────────────
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — CONCEPTS (read this before looking at the code)
# ══════════════════════════════════════════════════════════════════════════════
"""
WHAT IS VaR?
    Value-at-Risk (VaR) answers: "What is the maximum loss I expect to NOT
    exceed on 95% (or 99%) of days?"

    Parametric (Normal) VaR formula:
        VaR_α = -μ + σ · Φ⁻¹(α)

    Where:
        μ     = mean daily return (estimated from recent history)
        σ     = standard deviation of daily returns
        Φ⁻¹(α)= inverse normal CDF at confidence level α
        α     = confidence level (0.95 or 0.99)

    At α = 0.95:  Φ⁻¹(0.95) = +1.645  →  VaR = -μ + 1.645σ
    At α = 0.99:  Φ⁻¹(0.99) = +2.326  →  VaR = -μ + 2.326σ

    NOTE: VaR is expressed as a POSITIVE number representing a LOSS.
    If VaR_0.95 = 1.5%, it means: "We expect to lose no more than 1.5%
    on 95% of trading days."

    THE HypatiaX LINK:
    The LLM in Campaign 1 used z = -1.645 instead of +1.645.
    This sign error means the LLM's VaR would be:
        VaR_LLM = -μ - 1.645σ  (always negative → always predicting gain)
    That is why its R² = -10.05. The formula is structurally wrong.

WHAT IS BACKTESTING?
    After we estimate VaR each day, we check: did the actual loss
    exceed our VaR estimate the next day?

    If it did → that's an "exception" (or "exceedance").

    At 95% confidence: we EXPECT exceptions on 5% of days.
    Over 250 trading days: expected exceptions = 250 × 0.05 = 12-13.

THE BASEL TRAFFIC LIGHT FRAMEWORK (SS1/23 / SR 11-7 reference):
    The Basel Committee (1996) defined a simple rule for assessing
    backtesting results over 250 trading days at 99% confidence:

    Green Zone  (0-4 exceptions):   Model is acceptable
    Amber Zone  (5-9 exceptions):   Model is under scrutiny
    Red Zone    (10+ exceptions):   Model is likely flawed → reject

    We apply this logic at both 95% and 99% confidence levels.

WHY THIS IS SR 11-7 ELEMENT 3:
    SR 11-7 defines Outcomes Analysis as: "comparing model outputs to
    corresponding actual outcomes." Backtesting is the canonical form
    of outcomes analysis for VaR models. Every major bank's MRM team
    runs exactly this test on their market risk VaR models.
"""


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — DATA
# ══════════════════════════════════════════════════════════════════════════════

def get_returns(ticker="^GSPC", start="2018-01-01", end="2024-12-31"):
    """
    Download historical price data and compute daily log returns.

    WHY LOG RETURNS?
    Log returns are additive over time and more normally distributed
    than simple returns — this is the standard assumption underlying
    parametric VaR.

    WHY S&P 500?
    It's the most widely used benchmark, freely available, and
    approximately normally distributed over short horizons (though
    fat-tailed in reality — see Section 6 on limitations).
    """
    if not YFINANCE_AVAILABLE:
        print("[INFO] yfinance not installed. Generating synthetic S&P 500-like returns.")
        print("       Install with: pip install yfinance")
        print("       Synthetic data uses realistic parameters: μ=0.04%/day, σ=1.0%/day\n")
        np.random.seed(42)
        n = 1500
        dates = pd.date_range(start=start, periods=n, freq='B')
        # Realistic S&P 500 parameters with occasional fat tails
        returns = np.random.normal(0.0004, 0.010, n)
        # Add a few crisis-like events
        crisis_days = np.random.choice(n, size=15, replace=False)
        returns[crisis_days] = np.random.normal(-0.03, 0.02, 15)
        return pd.Series(returns, index=dates, name='log_return')

    print(f"[INFO] Downloading {ticker} data from {start} to {end}...")
    data = yf.download(ticker, start=start, end=end, progress=False)
    prices = data['Close'].squeeze()
    log_returns = np.log(prices / prices.shift(1)).dropna()
    log_returns.name = 'log_return'
    print(f"[INFO] Downloaded {len(log_returns)} daily returns\n")
    return log_returns


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — VaR ESTIMATION
# ══════════════════════════════════════════════════════════════════════════════

def estimate_var(returns_window, confidence_level=0.95):
    """
    Estimate parametric VaR from a rolling window of returns.

    THIS IS THE FORMULA FROM HypatiaX CAMPAIGN 1:
        VaR_α = -μ + σ · Φ⁻¹(α)

    Parameters:
        returns_window    : array of recent daily returns (the lookback window)
        confidence_level  : α (0.95 or 0.99)

    Returns:
        VaR estimate as a positive number (representing potential loss)

    WHAT THE PARAMETERS MEAN:
        μ (mu)  : average daily return over the window
                  Positive in bull markets, negative in downturns
        σ (sigma): standard deviation of returns over the window
                  Higher in volatile markets (e.g., Covid crash: σ ≈ 3-4%)
                  Lower in calm markets (e.g., 2017: σ ≈ 0.4%)
        z       : the normal quantile — how many standard deviations
                  corresponds to our confidence level
    """
    mu = np.mean(returns_window)
    sigma = np.std(returns_window, ddof=1)  # ddof=1: sample std dev
    z = stats.norm.ppf(confidence_level)    # Φ⁻¹(α)
    # VaR = -μ + z·σ  (positive number = potential loss)
    var_estimate = -mu + z * sigma
    return var_estimate, mu, sigma


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — BACKTESTING ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def run_backtest(returns, lookback=252, confidence_95=0.95, confidence_99=0.99):
    """
    Run a rolling-window VaR backtest.

    HOW IT WORKS:
    For each day t in the test period:
        1. Take the previous `lookback` days of returns as our estimation window
        2. Estimate VaR_95 and VaR_99 using the parametric formula
        3. Observe the ACTUAL return on day t
        4. Check if the actual LOSS exceeds our VaR estimate
           → If actual_loss > VaR: record as "exception"

    WHY 252-DAY LOOKBACK?
    252 is the standard number of trading days in a year. Using 1 year
    of history to estimate today's VaR is the most common industry practice
    and is consistent with Basel Committee guidance.

    Parameters:
        returns     : full time series of daily returns
        lookback    : number of days used to estimate VaR (default: 252)

    Returns:
        DataFrame with VaR estimates, actual returns, and exception flags
    """
    results = []
    n = len(returns)

    print(f"[INFO] Running backtest: {n - lookback} test days with {lookback}-day lookback")
    print(f"[INFO] Test period: {returns.index[lookback].date()} to {returns.index[-1].date()}\n")

    for t in range(lookback, n):
        estimation_window = returns.iloc[t - lookback : t]
        actual_return = returns.iloc[t]
        actual_loss = -actual_return  # Loss = negative of return

        # Estimate VaR at both confidence levels
        var_95, mu, sigma = estimate_var(estimation_window, confidence_95)
        var_99, _, _      = estimate_var(estimation_window, confidence_99)

        # Exception: actual loss EXCEEDS VaR estimate
        exception_95 = actual_loss > var_95
        exception_99 = actual_loss > var_99

        results.append({
            'date'        : returns.index[t],
            'actual_return': actual_return,
            'actual_loss' : actual_loss,
            'var_95'      : var_95,
            'var_99'      : var_99,
            'mu'          : mu,
            'sigma'       : sigma,
            'exception_95': exception_95,
            'exception_99': exception_99,
        })

    return pd.DataFrame(results).set_index('date')


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — BASEL TRAFFIC LIGHT ASSESSMENT
# ══════════════════════════════════════════════════════════════════════════════

def traffic_light_assessment(backtest_df):
    """
    Apply the Basel Committee traffic light framework.

    SS1/23 / SR 11-7 LINK:
    This assessment is the formal "outcomes analysis" required by SR 11-7
    and the "ongoing testing" required by SS1/23 Principle 4(c).

    A bank's MRM team performs this test at least quarterly on all
    market risk VaR models. If a model enters the Amber or Red zone,
    it triggers a formal validation review and potential model restrictions.

    EXPECTED EXCEPTION RATES (what a GOOD model should produce):
        At 95%: we expect 5% exception rate → 250 days × 5% = ~12-13 exceptions/year
        At 99%: we expect 1% exception rate → 250 days × 1% = ~2-3 exceptions/year

    WHAT DEVIATIONS MEAN:
        Too FEW exceptions: model is too conservative (overestimates risk)
                           → Capital held unnecessarily; business impact
        Too MANY exceptions: model underestimates risk
                           → Insufficient capital buffer; regulatory concern
    """
    n_test = len(backtest_df)
    n_exc_95 = backtest_df['exception_95'].sum()
    n_exc_99 = backtest_df['exception_99'].sum()

    exc_rate_95 = n_exc_95 / n_test
    exc_rate_99 = n_exc_99 / n_test

    expected_95 = n_test * 0.05
    expected_99 = n_test * 0.01

    # Binomial test: Is the observed exception rate statistically
    # different from the expected rate?
    # H0: true exception rate = 1 - confidence level
    # H1: true exception rate ≠ 1 - confidence level
    p_value_95 = stats.binom_test(n_exc_95, n_test, 0.05, alternative='two-sided') \
                 if hasattr(stats, 'binom_test') else \
                 stats.binomtest(n_exc_95, n_test, 0.05).pvalue
    p_value_99 = stats.binom_test(n_exc_99, n_test, 0.01, alternative='two-sided') \
                 if hasattr(stats, 'binom_test') else \
                 stats.binomtest(n_exc_99, n_test, 0.01).pvalue

    # Traffic light zones (adapted for 95% confidence)
    # Standard Basel zones are for 99% over 250 days:
    # Green: 0-4, Amber: 5-9, Red: 10+
    # We scale proportionally for our test period
    scaling = n_test / 250
    green_threshold  = round(4  * scaling)
    amber_threshold  = round(9  * scaling)

    def traffic_light(n_exc, threshold_green, threshold_amber):
        if n_exc <= threshold_green:
            return "GREEN ✓", "Model performing as expected."
        elif n_exc <= threshold_amber:
            return "AMBER ⚠", "Model under scrutiny — investigate potential underestimation."
        else:
            return "RED ✗", "Model likely flawed — formal review required."

    tl_99, msg_99 = traffic_light(n_exc_99, green_threshold, amber_threshold)

    return {
        'n_test': n_test,
        'n_exc_95': n_exc_95, 'exc_rate_95': exc_rate_95, 'expected_95': expected_95, 'p_value_95': p_value_95,
        'n_exc_99': n_exc_99, 'exc_rate_99': exc_rate_99, 'expected_99': expected_99, 'p_value_99': p_value_99,
        'traffic_light_99': tl_99, 'traffic_light_msg': msg_99,
        'green_threshold': green_threshold, 'amber_threshold': amber_threshold,
    }


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — REPORTING
# ══════════════════════════════════════════════════════════════════════════════

def print_validation_report(results, assessment):
    """
    Print a formal validation report in SS1/23 structure.

    This is what the MRM team would produce and present to the
    Model Risk Committee after running this backtest.
    """
    sep = "═" * 70

    print(f"\n{sep}")
    print("  MODEL VALIDATION REPORT — VaR BACKTESTING")
    print("  Prepared under SS1/23 Principle 4 / SR 11-7 Element 3")
    print(f"  Validator: Ruperto P. Bonet Chaple | Date: February 2026")
    print(sep)

    print("\n1. MODEL DETAILS")
    print(f"   Model:         Parametric VaR (Normal distribution)")
    print(f"   Formula:       VaR_α = -μ + σ · Φ⁻¹(α)")
    print(f"   Data source:   S&P 500 daily log returns")
    print(f"   Test period:   {results.index[0].date()} to {results.index[-1].date()}")
    print(f"   Test days:     {assessment['n_test']}")
    print(f"   Lookback:      252 trading days (1 year)")

    print("\n2. OUTCOMES ANALYSIS — EXCEPTION COUNTS")
    print(f"   {'Confidence':15} {'Observed Exc.':15} {'Expected Exc.':15} {'Exc. Rate':12} {'p-value':10}")
    print(f"   {'-'*65}")
    print(f"   {'95%':15} {assessment['n_exc_95']:<15} {assessment['expected_95']:<15.1f} "
          f"{assessment['exc_rate_95']:.2%}{'':5} {assessment['p_value_95']:.4f}")
    print(f"   {'99%':15} {assessment['n_exc_99']:<15} {assessment['expected_99']:<15.1f} "
          f"{assessment['exc_rate_99']:.2%}{'':5} {assessment['p_value_99']:.4f}")

    print("\n   INTERPRETATION:")
    print(f"   At 95%: p = {assessment['p_value_95']:.4f}", end="")
    if assessment['p_value_95'] < 0.05:
        print("  → SIGNIFICANT: exception rate differs from expected (model may be biased)")
    else:
        print("  → NOT SIGNIFICANT: exception rate consistent with 95% VaR model")

    print(f"   At 99%: p = {assessment['p_value_99']:.4f}", end="")
    if assessment['p_value_99'] < 0.05:
        print("  → SIGNIFICANT: exception rate differs from expected")
    else:
        print("  → NOT SIGNIFICANT: exception rate consistent with 99% VaR model")

    print("\n3. BASEL TRAFFIC LIGHT ASSESSMENT (99% VaR, scaled to test period)")
    print(f"   Green zone threshold:  ≤ {assessment['green_threshold']} exceptions")
    print(f"   Amber zone threshold:  ≤ {assessment['amber_threshold']} exceptions")
    print(f"   Red zone:              > {assessment['amber_threshold']} exceptions")
    print(f"\n   Observed (99%):        {assessment['n_exc_99']} exceptions")
    print(f"\n   ┌─────────────────────────────────────────┐")
    print(f"   │  TRAFFIC LIGHT: {assessment['traffic_light_99']:20}       │")
    print(f"   │  {assessment['traffic_light_msg']:40}│")
    print(f"   └─────────────────────────────────────────┘")

    print("\n4. KEY FINDINGS")

    findings = []
    if assessment['exc_rate_95'] > 0.07:
        findings.append(("F-01", "MAJOR",
            "Exception rate at 95% exceeds 7% — model materially underestimates tail risk. "
            "Likely cause: fat-tailed return distribution not captured by normal assumption."))
    elif assessment['exc_rate_95'] < 0.03:
        findings.append(("F-01", "MINOR",
            "Exception rate at 95% below 3% — model is overly conservative. "
            "May result in excess capital allocation."))
    else:
        findings.append(("F-01", "PASS",
            f"Exception rate at 95% is {assessment['exc_rate_95']:.1%} — within acceptable range of 3-7%."))

    if assessment['p_value_99'] < 0.05:
        findings.append(("F-02", "MAJOR",
            "Binomial test significant at 99% confidence level — the observed exception "
            "rate is statistically inconsistent with a correctly specified 99% VaR model."))
    else:
        findings.append(("F-02", "PASS",
            "Binomial test not significant — exception rate statistically consistent "
            "with correct model specification."))

    findings.append(("F-03", "INFORMATIONAL",
        "Model assumes normally distributed returns. S&P 500 returns exhibit "
        "negative skewness and excess kurtosis (fat tails). A t-distribution or "
        "historical simulation VaR would likely produce more accurate tail estimates. "
        "Recommend: retest with historical simulation as challenger model."))

    for fid, severity, text in findings:
        print(f"\n   [{fid} — {severity}]")
        print(f"   {text}")

    print("\n5. DISPOSITION")
    if assessment['traffic_light_99'].startswith("GREEN"):
        disp = "APPROVED — Model performing within acceptable parameters."
        rating = "LOW"
    elif assessment['traffic_light_99'].startswith("AMBER"):
        disp = "APPROVED WITH CONDITIONS — Investigate fat-tail assumption. Retest with historical simulation."
        rating = "MEDIUM"
    else:
        disp = "REQUIRES REDEVELOPMENT — Exception rate exceeds Red zone threshold."
        rating = "HIGH"

    print(f"   Disposition:       {disp}")
    print(f"   Model Risk Rating: {rating}")
    print(f"   Next Review:       Quarterly backtesting required per SS1/23 P4(c)")

    print("\n6. KNOWN LIMITATIONS (SR 11-7: Model Limitations Documentation)")
    print("   L-1: Normal distribution assumption underestimates tail risk (fat tails)")
    print("   L-2: Constant correlation assumption breaks down in crisis periods")
    print("   L-3: Lookback window (252 days) may lag rapidly changing volatility")
    print("   L-4: Model does not capture intraday or overnight gap risk")
    print("   L-5: Single-asset model — does not capture portfolio correlation effects")

    print(f"\n{sep}")
    print("  END OF VALIDATION REPORT")
    print(sep)

    # Connection back to HypatiaX
    print("\n" + "─" * 70)
    print("  HypatiaX CONNECTION")
    print("─" * 70)
    print("  HypatiaX Campaign 1 tested LLM recovery of this formula.")
    print("  The LLM used z = -1.645 (wrong sign), giving R² = -10.05.")
    print("  This backtesting engine uses the CORRECT formula: VaR = -μ + 1.645σ")
    print("  The difference between formula RECOVERY (HypatiaX) and formula")
    print("  VALIDATION against outcomes (this script) is SR 11-7 Element 3.")
    print("  Both are necessary. Neither alone is sufficient.")
    print("─" * 70)


def plot_backtest(results, confidence_95=0.95, confidence_99=0.99):
    """
    Visualise the backtest results.
    """
    if not MATPLOTLIB_AVAILABLE:
        print("\n[INFO] matplotlib not installed. Skipping plot.")
        print("       Install with: pip install matplotlib")
        return

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle('VaR Backtesting Results — S&P 500\nSS1/23 / SR 11-7 Outcomes Analysis',
                 fontsize=13, fontweight='bold')

    # Panel 1: Returns vs VaR
    ax1 = axes[0]
    ax1.fill_between(results.index, results['actual_return'],
                     where=results['actual_return'] < 0,
                     color='lightcoral', alpha=0.4, label='Negative daily return')
    ax1.fill_between(results.index, results['actual_return'],
                     where=results['actual_return'] >= 0,
                     color='lightgreen', alpha=0.4, label='Positive daily return')
    ax1.plot(results.index, -results['var_95'], color='orange',
             linewidth=1.5, label=f'95% VaR (loss threshold)')
    ax1.plot(results.index, -results['var_99'], color='red',
             linewidth=1.5, linestyle='--', label=f'99% VaR (loss threshold)')

    # Mark exceptions at 99%
    exc_99 = results[results['exception_99']]
    ax1.scatter(exc_99.index, exc_99['actual_return'],
                color='red', zorder=5, s=30, label=f'99% VaR Exception ({len(exc_99)} days)')

    ax1.axhline(0, color='black', linewidth=0.5)
    ax1.set_ylabel('Daily Return', fontsize=11)
    ax1.set_title('Daily Returns vs. VaR Thresholds', fontsize=11)
    ax1.legend(loc='lower left', fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Panel 2: Rolling exception rate
    ax2 = axes[1]
    rolling_exc_rate = results['exception_99'].rolling(252).mean()
    ax2.plot(rolling_exc_rate.index, rolling_exc_rate * 100,
             color='navy', linewidth=2, label='Rolling 252-day exception rate (99% VaR)')
    ax2.axhline(1.0, color='green', linewidth=1.5, linestyle='--', label='Expected rate (1%)')
    ax2.axhline(2.0, color='orange', linewidth=1.5, linestyle='--', label='Amber zone boundary')
    ax2.axhline(4.0, color='red', linewidth=1.5, linestyle='--', label='Red zone boundary')
    ax2.fill_between(rolling_exc_rate.index, 0, 1, alpha=0.1, color='green')
    ax2.fill_between(rolling_exc_rate.index, 1, 2, alpha=0.1, color='orange')
    ax2.fill_between(rolling_exc_rate.index, 2, 6, alpha=0.1, color='red')
    ax2.set_ylabel('Exception Rate (%)', fontsize=11)
    ax2.set_title('Rolling 252-day Exception Rate vs. Basel Traffic Light Zones', fontsize=11)
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 6)

    plt.tight_layout()
    plt.savefig('var_backtest_results.png', dpi=150, bbox_inches='tight')
    print("\n[INFO] Chart saved: var_backtest_results.png")
    plt.show()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("═" * 70)
    print("  VaR BACKTESTING ENGINE — HypatiaX Bridge Artefact 3")
    print("  SR 11-7 Element 3: Outcomes Analysis")
    print("  SS1/23 Principle 4(c): Ongoing Model Performance Monitoring")
    print("═" * 70)

    # Step 1: Get data
    returns = get_returns(
        ticker="^GSPC",      # S&P 500 index
        start="2018-01-01",
        end="2024-12-31"
    )

    # Step 2: Run backtest
    backtest_results = run_backtest(
        returns,
        lookback=252,        # 1 year estimation window
        confidence_95=0.95,
        confidence_99=0.99
    )

    # Step 3: Traffic light assessment
    assessment = traffic_light_assessment(backtest_results)

    # Step 4: Print formal validation report
    print_validation_report(backtest_results, assessment)

    # Step 5: Plot (if matplotlib available)
    plot_backtest(backtest_results)

    # Step 6: Save results to CSV for further analysis
    backtest_results.to_csv('var_backtest_results.csv')
    print("\n[INFO] Results saved: var_backtest_results.csv")
    print("[INFO] You can open this in Excel to inspect individual exception days.")

    print("\n" + "═" * 70)
    print("  NEXT STEPS (to extend this work for MRM interviews):")
    print("  1. Run the challenger: replace parametric VaR with historical simulation")
    print("     (sort the 252-day window and take the 5th percentile loss directly)")
    print("  2. Run by sub-period: compare 2018-2019 (calm) vs 2020 (Covid crash)")
    print("  3. Add t-distribution VaR: replace stats.norm.ppf with stats.t.ppf")
    print("     with ~4-6 degrees of freedom (captures fat tails)")
    print("  4. Write up results using the Section 6 report template")
    print("═" * 70)

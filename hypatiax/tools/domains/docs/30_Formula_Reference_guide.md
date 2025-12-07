# Extended Formula Reference Guide

## 60 Total Formulas (40 Original + 20 New)

---
I've extended your formula library with 20 new sophisticated formulas (10 Risk Management + 10 DeFi), bringing the total to 60 formulas.
Key Additions:
Risk Management (10 new):

Tail Risk Metrics: CDaR, Tail Ratio, Rachev Ratio for extreme event analysis
Drawdown Sophistication: D-Ratio, RoMaD, Serenity Ratio for deeper drawdown analysis
Performance Quality: Stability Index (equity curve smoothness), M² (intuitive Sharpe)
Behavioral Finance: Prospect Ratio (combines probability and magnitude)
Recovery Metrics: Recovery Factor (profit vs worst drawdown)

DeFi (10 new):

AMM Variants: Uniswap V3 tick pricing, Constant Sum, Curve StableSwap
Advanced Lending: Aave's kinked rate model, Compound with rewards, leverage calculation
Protocol Economics: Revenue models, token dilution, Maker stability fees
Trading Tools: Multi-hop price impact, Options Greeks (Delta), perpetual basis
Tokenomics: Rebase mechanisms, cliff vesting, Bancor bonding curves, multi-asset collateral

The formulas include practical thresholds (e.g., "RoMaD > 2 is good", "Stability > 0.9 is excellent") and real-world applications. Would you like me to:

=====================================================================
Create Python implementations for these new formulas?
Add more specialized formulas (exotic options, MEV, L2-specific)?
Build a comprehensive calculator/dashboard for all 60 formulas?
==================================================================

# NEW RISK MANAGEMENT FORMULAS (10)

## Risk Management Formulas (30)

### 1. Value at Risk (VaR) 95%

**Formula:** `VaR₉₅ = μ - 1.96 × σ × √t`

**Arguments:**

- `μ` (mu): Expected return (percent)
- `σ` (sigma): Volatility/standard deviation (percent, annualized)
- `t`: Time horizon (days, typically 1-252 trading days)

**Usage:** Estimates the maximum expected loss over a given time period at 95% confidence level. For example, if VaR₉₅ = -5%, there's a 95% probability that losses won't exceed 5% over the specified period.

---

### 2. Sharpe Ratio

**Formula:** `Sharpe = (R - Rf) / σ`

**Arguments:**

- `R` (returns): Portfolio returns (percent, annualized)
- `Rf` (risk_free): Risk-free rate (percent, annualized)
- `σ` (volatility): Return volatility (percent, annualized)

**Usage:** Measures risk-adjusted return by showing excess return per unit of total risk. Higher Sharpe ratios (>1) indicate better risk-adjusted performance. Useful for comparing different investment strategies.

---

### 3. Conditional VaR (CVaR/ES) 95%

**Formula:** `CVaR₉₅ = μ - φ⁻¹ × σ × √t` where `φ⁻¹ ≈ 2.063`

**Arguments:**

- `μ` (mu): Expected return (percent)
- `σ` (sigma): Volatility (percent, annualized)
- `t`: Time horizon (days)

**Usage:** Expected Shortfall - estimates the average loss given that losses exceed the VaR threshold. More conservative than VaR as it considers tail risk beyond the confidence level.

---

### 4. Beta

**Formula:** `β = Cov(i,m) / Var(m)`

**Arguments:**

- `Cov(i,m)` (cov_im): Covariance between asset and market (percent²)
- `Var(m)` (var_m): Market variance (percent²)

**Usage:** Measures systematic risk relative to the market. β=1 means asset moves with market, β>1 indicates higher volatility than market, β<1 indicates lower volatility. Used in CAPM for asset pricing.

---

### 5. Sortino Ratio

**Formula:** `Sortino = (R - T) / σ_downside`

**Arguments:**

- `R` (returns): Portfolio returns (percent, annualized)
- `T` (target): Target or minimum acceptable return (percent)
- `σ_downside` (downside_dev): Downside deviation (percent)

**Usage:** Similar to Sharpe but only penalizes downside volatility below target return. Better for asymmetric return distributions. Preferred when upside volatility is desirable.

---

### 6. Information Ratio

**Formula:** `IR = α / TE`

**Arguments:**

- `α` (active_return): Portfolio return minus benchmark return (percent)
- `TE` (tracking_error): Standard deviation of active returns (percent)

**Usage:** Measures active management skill by showing excess return per unit of active risk. IR > 0.5 is considered good, >1.0 is excellent. Used to evaluate fund managers against benchmarks.

---

### 7. Maximum Drawdown

**Formula:** `MDD = (Trough - Peak) / Peak`

**Arguments:**

- `Peak` (peak): Peak portfolio value (currency units)
- `Trough` (trough): Trough portfolio value after peak (currency units)

**Usage:** Largest peak-to-trough decline in portfolio value. Measures worst-case loss experienced. Important for understanding downside risk and recovery requirements (30% loss needs 43% gain to recover).

---

### 8. Treynor Ratio

**Formula:** `Treynor = (R - Rf) / β`

**Arguments:**

- `R` (returns): Portfolio returns (percent, annualized)
- `Rf` (risk_free): Risk-free rate (percent, annualized)
- `β` (risk_beta): Systematic risk/beta (dimensionless)

**Usage:** Risk-adjusted return per unit of systematic risk. Useful for well-diversified portfolios where systematic risk is the main concern. Compare portfolios with similar beta values.

---

### 9. Calmar Ratio

**Formula:** `Calmar = R_annual / MDD`

**Arguments:**

- `R_annual` (annual_return): Annualized return (percent)
- `MDD` (max_drawdown): Maximum drawdown (percent, positive value)

**Usage:** Return relative to worst drawdown. Higher values indicate better performance relative to largest loss. Commonly used in hedge fund evaluation. Ratio > 3 is considered excellent.

---

### 10. Omega Ratio

**Formula:** `Ω = (Gains + ε) / (Losses + ε)` (simplified with epsilon for stability)

**Arguments:**

- `Gains` (gains): Expected gains above threshold (percent)
- `Losses` (losses): Expected losses below threshold (percent)

**Usage:** Probability-weighted ratio of gains to losses relative to a threshold. Ω > 1 means gains exceed losses. Captures all moments of return distribution, unlike Sharpe which only uses first two moments.

---

### 11. Value at Risk (VaR) 99%

**Formula:** `VaR₉₉ = μ - 2.576 × σ × √t`

**Arguments:**

- `μ` (mu): Expected return (percent)
- `σ` (sigma): Volatility (percent, annualized)
- `t`: Time horizon (days)

**Usage:** Maximum expected loss at 99% confidence level. More conservative than VaR₉₅. Used for regulatory capital requirements and extreme risk assessment. Only 1% chance of exceeding this loss.

---

### 12. Modified Sharpe Ratio

**Formula:** `Modified Sharpe = (R - Rf) / (σ × (1 + S/6))`

**Arguments:**

- `R` (returns): Portfolio returns (percent, annualized)
- `Rf` (risk_free): Risk-free rate (percent, annualized)
- `σ` (volatility): Volatility (percent, annualized)
- `S` (skewness): Return distribution skewness (dimensionless)

**Usage:** Adjusts traditional Sharpe ratio for skewness in returns. Negative skew increases denominator (penalizes), positive skew decreases it (rewards). Better for non-normal return distributions.

---

### 13. Ulcer Index

**Formula:** `UI = √(Σ(DD²) / n)`

**Arguments:**

- `DD²_sum` (dd_squared_sum): Sum of squared drawdowns (percent²)
- `n` (periods): Number of periods (dimensionless)

**Usage:** Measures depth and duration of drawdowns. Unlike standard deviation, it only considers downside volatility. Lower values indicate less stress/pain from declines. Used in Martin Ratio calculation.

---

### 14. Martin Ratio (Ulcer Performance Index)

**Formula:** `Martin = R / UI`

**Arguments:**

- `R` (returns): Portfolio returns (percent, annualized)
- `UI` (ulcer_index): Ulcer Index (percent)

**Usage:** Return per unit of downside risk as measured by Ulcer Index. Similar concept to Sharpe but uses Ulcer Index instead of standard deviation. Preferred for measuring stress-adjusted returns.

---

### 15. Kappa 3 Ratio

**Formula:** `Kappa₃ = R / LPM₃^(1/3)`

**Arguments:**

- `R` (returns): Portfolio returns (percent)
- `LPM₃` (lpm3): Lower Partial Moment of 3rd order (percent³)

**Usage:** Risk-adjusted return using 3rd order lower partial moment. Emphasizes larger losses more heavily than smaller ones. Part of Kappa family; higher orders give more weight to extreme losses.

---

### 16. Gain-Loss Ratio

**Formula:** `G/L = Average_Win / Average_Loss`

**Arguments:**

- `Average_Win` (avg_gain): Average gain per winning trade (percent)
- `Average_Loss` (avg_loss): Average loss per losing trade (percent)

**Usage:** Average size of wins versus losses. Ratio > 1 means average win exceeds average loss. Combined with win rate to evaluate trading strategy quality. Used extensively in systematic trading.

---

### 17. Upside Potential Ratio

**Formula:** `UPR = Upside_Potential / Downside_Risk`

**Arguments:**

- `Upside_Potential` (upside_potential): Expected gains above MAR (percent)
- `Downside_Risk` (downside_risk): Downside deviation below MAR (percent)

**Usage:** Measures upside potential relative to downside risk, both measured against Minimum Acceptable Return (MAR). Higher values preferred. Useful when investors have specific return targets.

---

### 18. Sterling Ratio

**Formula:** `Sterling = (R - 10%) / AvgDD`

**Arguments:**

- `R` (annual_return): Annualized return (percent)
- `AvgDD` (avg_drawdown): Average of largest drawdowns (percent)

**Usage:** Return above 10% threshold per unit of average drawdown. Originally used 10% as minimum acceptable return. Higher ratios indicate better performance relative to typical drawdown magnitude.

---

### 19. Burke Ratio

**Formula:** `Burke = Excess_Return / √(Σ DD²)`

**Arguments:**

- `Excess_Return` (excess_return): Return above risk-free rate (percent)
- `√(Σ DD²)` (sqrt_sum_dd): Square root of sum of squared drawdowns (percent)

**Usage:** Excess return per unit of drawdown magnitude. Similar to Calmar but uses multiple drawdowns rather than just maximum. Provides more comprehensive view of drawdown risk.

---

### 20. Pain Ratio

**Formula:** `Pain = R / Pain_Index`

**Arguments:**

- `R` (returns): Portfolio returns (percent)
- `Pain_Index` (pain_index): Average drawdown over evaluation period (percent)

**Usage:** Return per unit of average pain/drawdown. Pain Index measures average depth of underwater periods. Higher ratios indicate better return for experienced drawdowns. Simple but effective drawdown-adjusted metric.

## 21. Conditional Drawdown at Risk (CDaR)

**Formula:** `CDaR = E[DD | DD ≥ DaR_α]`

**Arguments:**

- `DD` (drawdowns): Historical drawdown series (percent)
- `α` (alpha): Confidence level (typically 0.95)

**Usage:** Expected drawdown given that drawdown exceeds the Drawdown at Risk threshold. More conservative than Maximum Drawdown as it considers the tail distribution of drawdowns. Used for risk budgeting in hedge funds. CDaR at 95% measures average of worst 5% drawdowns.

---

## 22. Tail Ratio

**Formula:** `Tail Ratio = |95th percentile| / |5th percentile|`

**Arguments:**

- `95th percentile`: 95th percentile of returns distribution (percent)
- `5th percentile`: 5th percentile of returns distribution (percent)

**Usage:** Measures asymmetry between right tail (gains) and left tail (losses). Ratio > 1 indicates fatter right tail (more extreme gains than losses). Used to identify positive vs negative skew. Especially useful for options strategies and tail-risk hedging.

---

## 23. M² (M-Squared / Modigliani-Modigliani)

**Formula:** `M² = Rf + Sharpe × σ_benchmark`

**Arguments:**

- `Rf` (risk_free): Risk-free rate (percent, annualized)
- `Sharpe`: Portfolio Sharpe ratio (dimensionless)
- `σ_benchmark` (benchmark_vol): Benchmark volatility (percent, annualized)

**Usage:** Risk-adjusted return expressed in percentage terms rather than ratio. Represents the return a portfolio would have earned if it had the same risk as the benchmark. M² > Benchmark return indicates outperformance. More intuitive than Sharpe for client communication.

---

## 24. Prospect Ratio (Gain-Loss Ratio with Probability)

**Formula:** `Prospect = (P_win × Avg_win²) / (P_loss × Avg_loss²)`

**Arguments:**

- `P_win` (prob_win): Probability of winning (0-1)
- `Avg_win` (avg_gain): Average gain magnitude (percent)
- `P_loss` (prob_loss): Probability of loss (0-1)
- `Avg_loss` (avg_loss): Average loss magnitude (percent)

**Usage:** Combines win rate with payoff ratio, squaring returns to emphasize magnitude. Better captures risk-reward than simple win rate. Prospect > 1 indicates favorable strategy. Based on prospect theory - investors feel losses more than equivalent gains.

---

## 25. Rachev Ratio (Tail Risk Ratio)

**Formula:** `Rachev = CVaR_α(returns) / CVaR_α(-returns)`

**Arguments:**

- `CVaR_α(returns)`: Conditional VaR of positive returns at confidence α
- `CVaR_α(-returns)`: Conditional VaR of negative returns at confidence α
- `α` (alpha): Confidence level (typically 0.95)

**Usage:** Ratio of expected tail gains to expected tail losses. Focuses on extreme outcomes rather than average returns. Rachev > 1 means extreme gains exceed extreme losses. Critical for understanding tail risk in asymmetric strategies.

---

## 26. D-Ratio (Downside Risk over Time)

**Formula:** `D-Ratio = Σ(|Underwater_i| / N) / σ_total`

**Arguments:**

- `Underwater_i`: Percentage underwater on day i (negative values)
- `N`: Total number of periods (days)
- `σ_total` (total_vol): Total return volatility (percent)

**Usage:** Measures pain of underwater periods relative to total volatility. Lower D-Ratio is better (less time spent in drawdown). Penalizes both depth and duration of drawdowns. More comprehensive than Maximum Drawdown alone.

---

## 27. Return over Maximum Drawdown (RoMaD)

**Formula:** `RoMaD = Annualized_Return / |Maximum_Drawdown|`

**Arguments:**

- `Annualized_Return`: Annual return (percent)
- `Maximum_Drawdown`: Largest peak-to-trough decline (percent, positive value)

**Usage:** Similar to Calmar but emphasizes absolute return generation. RoMaD > 2 is considered good. Used extensively in CTA and systematic trading evaluation. Higher values indicate better return generation per unit of worst-case loss.

---

## 28. Serenity Ratio

**Formula:** `Serenity = (R - Rf) / Avg(|Underwater_periods|)`

**Arguments:**

- `R` (returns): Portfolio return (percent, annualized)
- `Rf` (risk_free): Risk-free rate (percent, annualized)
- `Avg(|Underwater_periods|)`: Average depth of underwater periods (percent)

**Usage:** Excess return per unit of average underwater depth. Measures return relative to typical "pain" experienced. Lower average underwater depth is better. Serenity > 1.5 indicates strong performance. Focuses on investor experience during drawdowns.

---

## 29. Stability Index

**Formula:** `Stability = R² of equity curve regression`

**Arguments:**

- `R²`: Coefficient of determination from linear regression of cumulative returns over time

**Usage:** Measures smoothness of equity curve. R² close to 1 indicates steady growth, close to 0 indicates erratic performance. Stability > 0.9 is excellent. Used to identify consistent vs volatile strategy performance regardless of total return.

---

## 30. Recovery Factor

**Formula:** `Recovery = Net_Profit / |Maximum_Drawdown|`

**Arguments:**

- `Net_Profit`: Total profit (currency or percent)
- `Maximum_Drawdown`: Largest peak-to-trough decline (same units, positive value)

**Usage:** Total profit relative to worst drawdown. Recovery > 3 is considered good, >5 is excellent. Common in algorithmic trading evaluation. Shows how many "times over" the strategy recovered from worst loss.

---

# NEW DeFi FORMULAS (10)

## DeFi Formulas (30)

### 1. Impermanent Loss

**Formula:** `IL = 2√(price_ratio) / (price_ratio + 1) - 1`

**Arguments:**

- `price_ratio`: Ratio of current price to initial price (dimensionless)

**Usage:** Calculates loss experienced by liquidity providers due to price divergence in AMM pools. IL = 0 when price_ratio = 1 (no change). Always negative when prices change. At 2x price change, IL ≈ 5.7%. Critical for LP decision-making.

---

### 2. AMM Swap Output (Uniswap V2)

**Formula:** `Output = (Amount_in × 0.997 × Reserve_out) / (Reserve_in + Amount_in × 0.997)`

**Arguments:**

- `Amount_in`: Input token amount (normalized)
- `Reserve_in`: Input token reserve (normalized)
- `Reserve_out`: Output token reserve (normalized)

**Usage:** Calculates token output for a given input in constant product AMM (x×y=k). 0.3% fee applied (0.997 multiplier). Critical for pricing trades and calculating slippage in Uniswap-style DEXs.

---

### 3. Utilization Rate

**Formula:** `U = Borrowed / Supplied`

**Arguments:**

- `Borrowed`: Total amount borrowed from pool (tokens)
- `Supplied`: Total amount supplied to pool (tokens)

**Usage:** Measures how much of available liquidity is currently borrowed in lending protocols. U = 0.8 means 80% utilization. Drives interest rate models - higher utilization = higher rates. Key metric for lending pool health.

---

### 4. Liquidity Pool Value

**Formula:** `Value = 2 × √(Reserve₀ × Reserve₁)`

**Arguments:**

- `Reserve₀`: Reserve amount of token 0 (normalized)
- `Reserve₁`: Reserve amount of token 1 (normalized)

**Usage:** Total value locked in constant product AMM pool. Derived from constant product formula (x×y=k). Used to calculate total pool size, LP share values, and protocol TVL. Fundamental metric for DEX analytics.

---

### 5. Compound Interest Rate Model

**Formula:** `Rate = Base_Rate + Slope × Utilization`

**Arguments:**

- `Base_Rate`: Minimum interest rate at 0% utilization (decimal)
- `Utilization`: Pool utilization ratio (0-1)
- `Slope`: Rate increase per unit of utilization (decimal)

**Usage:** Linear interest rate model used in lending protocols. Rate increases linearly with utilization to incentivize supply and discourage borrowing at high utilization. Compound Finance pioneered this approach.

---

### 6. Collateral Ratio

**Formula:** `CR = Collateral_Value / Debt_Value`

**Arguments:**

- `Collateral_Value`: USD value of posted collateral
- `Debt_Value`: USD value of borrowed assets

**Usage:** Measures health of leveraged position. CR = 1.5 means 150% collateralized (50% overcollateralized). Positions liquidated when CR falls below protocol minimum. Critical for DeFi lending safety.

---

### 7. Liquidation Price

**Formula:** `P_liquidation = Entry_Price / Liquidation_Threshold`

**Arguments:**

- `Entry_Price`: Price when position opened
- `Liquidation_Threshold`: Minimum collateral ratio (e.g., 1.3 for 130%)

**Usage:** Price at which leveraged position gets liquidated. If ETH entry = $2000 and threshold = 1.5, liquidation at $1333. Essential for risk management in leveraged DeFi positions.

---

### 8. Yield Farming APY

**Formula:** `APY = (Rewards_per_Block × Blocks_per_Year) / Total_Staked`

**Arguments:**

- `Rewards_per_Block`: Token rewards per block
- `Blocks_per_Year`: Annual block count (~2,102,400 for Ethereum)
- `Total_Staked`: Total tokens staked in pool

**Usage:** Calculates annual percentage yield for liquidity mining/yield farming. Assumes constant emission rate and staked amount. Actual APY varies with participation. Critical for comparing yield opportunities.

---

### 9. Slippage

**Formula:** `Slippage = Amount_in / (Reserve + Amount_in)`

**Arguments:**

- `Amount_in`: Trade input amount
- `Reserve`: Pool reserve of input token

**Usage:** Price impact percentage from a trade in AMM. Larger trades relative to pool size have higher slippage. Slippage = 0.01 means 1% price impact. Used to estimate execution price and set slippage tolerance.

---

### 10. LP Token Share

**Formula:** `LP_Tokens = (Deposit / Total_Liquidity) × Total_Shares`

**Arguments:**

- `Deposit`: Amount being deposited
- `Total_Liquidity`: Current total pool liquidity
- `Total_Shares`: Outstanding LP token supply

**Usage:** Calculates LP tokens minted for a deposit. LP tokens represent proportional pool ownership. On withdrawal, burn LP tokens to redeem proportional pool assets plus accumulated fees.

---

### 11. Health Factor (Aave)

**Formula:** `HF = (Collateral × Liquidation_Threshold) / Debt`

**Arguments:**

- `Collateral`: Total collateral value (USD)
- `Liquidation_Threshold`: Protocol-specific threshold (0.75-0.85 typical)
- `Debt`: Total debt value (USD)

**Usage:** Aave's position health metric. HF < 1 triggers liquidation. HF = 2 means position is 2x healthy. Different collateral types have different thresholds. Critical for monitoring loan safety.

---

### 12. Perpetual Funding Rate

**Formula:** `Funding = (Mark_Price - Index_Price) / Index_Price / Interval`

**Arguments:**

- `Mark_Price`: Perpetual contract mark price
- `Index_Price`: Underlying spot index price
- `Interval`: Funding interval in hours (typically 8)

**Usage:** Periodic payment between long and short traders to keep perpetual price anchored to spot. Positive funding = longs pay shorts (perpetual trading at premium). Updated every 8 hours typically.

---

### 13. Price Impact

**Formula:** `Impact = (Trade_Size / Liquidity)^0.5`

**Arguments:**

- `Trade_Size`: Size of trade
- `Liquidity`: Available liquidity depth

**Usage:** Simplified price impact estimation using square root model. More sophisticated than linear slippage. Used to estimate execution quality before trading. Important for large trades and thin markets.

---

### 14. Staking Rewards

**Formula:** `Rewards = Staked × Rate × (Days / 365)`

**Arguments:**

- `Staked`: Amount staked
- `Rate`: Annual reward rate (APR)
- `Days`: Number of days staked

**Usage:** Simple linear staking rewards calculation. Rate = 0.12 means 12% APR. Assumes no compounding (use APY formula if compounding). Used in most PoS staking and governance token staking.

---

### 15. Linear Bonding Curve

**Formula:** `Price = Supply × Reserve_Ratio`

**Arguments:**

- `Supply`: Current token supply
- `Reserve_Ratio`: Reserve ratio parameter (0-1)

**Usage:** Simplest bonding curve where price increases linearly with supply. Reserve_Ratio determines price slope. Used in token launch mechanisms and continuous organizations. Higher supply = higher price.

---

### 16. Flash Loan Fee

**Formula:** `Fee = Loan_Amount × Fee_Rate`

**Arguments:**

- `Loan_Amount`: Amount of flash loan
- `Fee_Rate`: Protocol fee rate (typically 0.05-0.09%)

**Usage:** Fee charged for flash loan (borrow and repay in single transaction). Aave charges 0.09%, dYdX 0%. Fee must be repaid in same transaction or revert. Enables arbitrage and liquidations.

---

### 17. Linear Vesting Schedule

**Formula:** `Vested = Total × (Time_Elapsed / Vesting_Period)`

**Arguments:**

- `Total`: Total tokens to vest
- `Time_Elapsed`: Days since vesting start
- `Vesting_Period`: Total vesting duration (days)

**Usage:** Calculates linearly vested amount. Common for team tokens and VC allocations. After 6 months of 12-month vesting, 50% is vested. Prevents immediate dumping of large allocations.

---

### 18. Arbitrage Profit

**Formula:** `Profit = (Price_B - Price_A) × Trade_Size`

**Arguments:**

- `Price_A`: Price on exchange A
- `Price_B`: Price on exchange B (higher)
- `Trade_Size`: Arbitrage trade size

**Usage:** Gross profit from cross-exchange arbitrage before fees and gas. Buy low on A, sell high on B. Net profit = Gross - Fees - Gas. Arbitrageurs keep prices aligned across venues.

---

### 19. Gas Cost ROI

**Formula:** `ROI = (Profit - Gas_Cost) / Gas_Cost`

**Arguments:**

- `Profit`: Transaction profit
- `Gas_Cost`: Ethereum gas cost

**Usage:** Return on investment accounting for gas costs. ROI = 2 means profit is 2x the gas cost. Critical in MEV and arbitrage where gas costs can exceed profits. Negative ROI means unprofitable transaction.

---

### 20. Concentrated Liquidity Position (Uniswap V3)

**Formula:** `Amount₀ = L × (√P_upper - √P) / (√P × √P_upper)`

**Arguments:**

- `L` (liquidity): Position liquidity value
- `√P`: Square root of current price
- `√P_lower`: Square root of lower tick price
- `√P_upper`: Square root of upper tick price

**Usage:** Calculates token amounts in concentrated liquidity position. When price is within range, position contains both tokens. Outside range, contains only one token. Enables capital efficiency up to 4000x vs V2.

---

## Usage Categories

### Risk Management Applications

- **Portfolio Construction**: Sharpe, Sortino, Treynor ratios for strategy selection
- **Risk Budgeting**: VaR, CVaR for position sizing and limits
- **Performance Attribution**: Information Ratio, Beta for manager evaluation
- **Stress Testing**: Maximum Drawdown, Ulcer Index for worst-case analysis

### DeFi Applications

- **Liquidity Provision**: IL, Pool Value, LP Tokens for AMM participation
- **Lending/Borrowing**: Utilization Rate, Collateral Ratio, Health Factor for loan management
- **Trading**: Slippage, Price Impact, Arbitrage Profit for execution optimization
- **Yield Optimization**: APY calculations, Gas ROI for strategy evaluation

## 21. Uniswap V3 Price from Tick

**Formula:** `Price = 1.0001^tick`

**Arguments:**

- `tick`: Integer tick value in Uniswap V3 (-887272 to 887272)

**Usage:** Converts Uniswap V3 tick to actual price. Tick spacing depends on fee tier (10 for 0.05%, 60 for 0.3%, 200 for 1%). Critical for understanding concentrated liquidity positions. Each tick represents 0.01% price change (1 basis point).

---

## 22. Constant Sum AMM Output (mStable)

**Formula:** `Output = Amount_in × (1 - fee)`

**Arguments:**

- `Amount_in`: Input token amount
- `fee`: Trading fee rate (e.g., 0.003 for 0.3%)

**Usage:** Simple 1:1 swap formula used for stablecoin AMMs like mStable and Curve (when balanced). No slippage for equal-value assets. Used when tokens have very similar value (stablecoins, wrapped assets). Breaks down when prices diverge significantly.

---

## 23. Curve StableSwap Invariant

**Formula:** `D = (A × n^n × Σx_i + D^(n+1) / (n^n × Πx_i))^(1/2)` (simplified)

**Arguments:**

- `A`: Amplification coefficient (typically 50-1000)
- `n`: Number of coins in pool
- `x_i`: Reserve of coin i
- `D`: Invariant to solve for

**Usage:** Hybrid constant product + constant sum formula for stablecoins. Lower slippage than Uniswap for correlated assets. A parameter controls curve shape: high A = more like constant sum (less slippage), low A = more like constant product. Critical for stable asset swaps.

---

## 24. Aave Variable Borrow Rate

**Formula:** `Rate = R_base + (U / U_optimal) × R_slope1` when U ≤ U_optimal
`Rate = R_base + R_slope1 + ((U - U_optimal) / (1 - U_optimal)) × R_slope2` when U > U_optimal

**Arguments:**

- `U`: Utilization rate (0-1)
- `U_optimal`: Optimal utilization (typically 0.8 or 80%)
- `R_base`: Base rate (typically 0%)
- `R_slope1`: First slope (moderate increase)
- `R_slope2`: Second slope (steep increase)

**Usage:** Aave's kinked interest rate model. Rate increases moderately until optimal utilization, then sharply above it. Encourages supply when utilization is high. Prevents liquidity crisis by making borrowing expensive at high utilization.

---

## 25. Compound Borrow APY (with COMP rewards)

**Formula:** `Total_APY = Borrow_APR + (COMP_per_block × blocks_per_year × COMP_price / Total_Borrowed)`

**Arguments:**

- `Borrow_APR`: Interest rate paid on borrowing (decimal)
- `COMP_per_block`: COMP tokens distributed per block
- `blocks_per_year`: Blocks per year (~2,102,400 for Ethereum)
- `COMP_price`: Price of COMP token (USD)
- `Total_Borrowed`: Total value borrowed in pool (USD)

**Usage:** Net borrowing cost after incentive rewards. Can be negative (paid to borrow) during high incentive periods. Critical for yield farming strategies. Real cost = Borrow APR - Reward APY.

---

## 26. Leverage Ratio (DeFi Lending)

**Formula:** `Leverage = 1 / (1 - LTV)`

**Arguments:**

- `LTV`: Loan-to-Value ratio (0-1, e.g., 0.75 for 75%)

**Usage:** Maximum leverage achievable through recursive borrowing. LTV=0.75 gives 4x leverage (1/(1-0.75)=4). Shows maximum capital efficiency. Leverage > 3x is considered risky. Used in leveraged yield farming and staking strategies.

---

## 27. Protocol Revenue (Trading Fees)

**Formula:** `Revenue = Volume × Fee_Rate × Protocol_Cut`

**Arguments:**

- `Volume`: Trading volume (USD)
- `Fee_Rate`: Trading fee percentage (e.g., 0.003 for 0.3%)
- `Protocol_Cut`: Portion going to protocol (0-1, e.g., 0.167 for 1/6)

**Usage:** Calculates protocol earnings from trading fees. Used to value DEX protocols. Uniswap V3 gives 1/6 of fees to protocol (if activated). Key metric for protocol fundamental analysis and token valuation.

---

## 28. Maker DAO Stability Fee

**Formula:** `Total_Fee = Principal × e^(rate × time) - Principal`

**Arguments:**

- `Principal`: DAI debt amount
- `rate`: Annual stability fee rate (decimal, e.g., 0.05 for 5%)
- `time`: Time in years (can be fractional)

**Usage:** Continuously compounded interest on MakerDAO CDP (Collateralized Debt Position). Higher than simple interest due to continuous compounding. Stability fee controls DAI supply - higher fee = less borrowing = less DAI minted.

---

## 29. Liquidity Mining Dilution Rate

**Formula:** `Dilution = (Emissions_per_year / Total_Supply) × 100`

**Arguments:**

- `Emissions_per_year`: Annual token emissions (tokens)
- `Total_Supply`: Current total token supply (tokens)

**Usage:** Annual inflation rate from liquidity mining rewards. Dilution = 20% means supply grows 20%/year. High dilution can offset APY gains. Critical for understanding real yield vs inflationary rewards. Sustainable protocols aim for <10% dilution.

---

## 30. Impermanent Loss with Fees

**Formula:** `Net_IL = IL - (Fee_APR × time × 2√(price_ratio) / (price_ratio + 1))`

**Arguments:**

- `IL`: Impermanent loss percentage (negative)
- `Fee_APR`: Annual fee earnings (decimal)
- `time`: Time period (years)
- `price_ratio`: Current price / Initial price

**Usage:** Net impermanent loss after fee earnings. Fees can offset or exceed IL. For profitable LP: |Net_IL| < 0 (actually profit). Critical for LP decision-making. Highly traded pairs generate more fees to offset IL.

---

## 31. Automated Market Maker (AMM) Price Impact (Multi-hop)

**Formula:** `Total_Impact = 1 - Π(1 - Impact_i)` for n hops

**Arguments:**

- `Impact_i`: Price impact on hop i (decimal)
- `n`: Number of swap hops

**Usage:** Cumulative price impact across multiple pools. Two 2% impacts = 1-(0.98×0.98) = 3.96% total. Used for routing optimization. DEX aggregators minimize this by splitting across routes.

---

## 32. Options Greeks - Delta (Black-Scholes)

**Formula:** `Δ_call = N(d₁)` where `d₁ = (ln(S/K) + (r + σ²/2)T) / (σ√T)`

**Arguments:**

- `S`: Current spot price
- `K`: Strike price
- `r`: Risk-free rate (decimal)
- `σ`: Volatility (decimal, annualized)
- `T`: Time to expiration (years)
- `N()`: Cumulative standard normal distribution

**Usage:** Rate of change of option price with respect to underlying price. Delta = 0.5 means option moves $0.50 for every $1 move in underlying. Used for hedging in DeFi options protocols like Opyn, Hegic. Critical for market makers.

---

## 33. Perpetual Swap Basis

**Formula:** `Basis = (Perpetual_Price - Spot_Price) / Spot_Price × (365 / Days_to_expiry)`

**Arguments:**

- `Perpetual_Price`: Perpetual contract price
- `Spot_Price`: Spot market price
- `Days_to_expiry`: Days until settlement (typically use 1 for annualized rate)

**Usage:** Annualized premium/discount of perpetual vs spot. Positive basis = backwardation (bullish), negative = contango (bearish). Used in funding arbitrage strategies. Extreme basis indicates market imbalance.

---

## 34. Liquidity Depth (Order Book)

**Formula:** `Depth = Σ(Volume_i) for |Price_i - Mid| ≤ threshold`

**Arguments:**

- `Volume_i`: Order volume at price level i
- `Price_i`: Price at level i
- `Mid`: Mid-market price
- `threshold`: Price threshold (e.g., 1% or $100)

**Usage:** Total liquidity available within price threshold. Higher depth = less slippage for large orders. Used to assess DEX liquidity quality. Depth at 1% is common benchmark (total volume within ±1% of mid price).

---

## 35. Rebase Token Supply Adjustment

**Formula:** `New_Supply = Current_Supply × (Current_Price / Target_Price)^elasticity`

**Arguments:**

- `Current_Supply`: Current token supply
- `Current_Price`: Current market price
- `Target_Price`: Target peg price
- `elasticity`: Rebase sensitivity (typically 0.05-0.2)

**Usage:** Elastic supply adjustment for rebase tokens (Ampleforth, OHM). Supply expands when price > target, contracts when price < target. Elasticity < 1 prevents overcorrection. Used in algorithmic stablecoins and reserve currencies.

---

## 36. Flash Loan Arbitrage Net Profit

**Formula:** `Net_Profit = (Price_B - Price_A) × Amount - Fee_A - Fee_B - Gas_Cost - Flash_Fee`

**Arguments:**

- `Price_A`, `Price_B`: Prices on exchange A and B
- `Amount`: Arbitrage size
- `Fee_A`, `Fee_B`: Trading fees on both exchanges
- `Gas_Cost`: Ethereum gas cost
- `Flash_Fee`: Flash loan fee

**Usage:** True profit after all costs. Must be positive for profitable arb. Gas costs can exceed profit on small opportunities. Typical flash loan fee = 0.09% (Aave). MEV bots compete on gas to capture these opportunities.

---

## 37. Token Vesting Cliff and Linear

**Formula:** `Vested = 0` if `time < cliff`, else `min(Total × (time - cliff) / vesting_period, Total)`

**Arguments:**

- `Total`: Total tokens to vest
- `time`: Time elapsed since start
- `cliff`: Cliff period (no vesting)
- `vesting_period`: Linear vesting duration after cliff

**Usage:** Common vesting with initial lockup then linear release. 1-year cliff + 3-year vest means 0% at month 11, then linear from year 1-4. Prevents immediate selling. Standard for team/investor allocations.

---

## 38. Bonding Curve Reserve Ratio (Bancor)

**Formula:** `Price = Balance / (Supply × CW)`

**Arguments:**

- `Balance`: Reserve token balance
- `Supply`: Bonded token supply
- `CW`: Connector Weight (0-1, reserve ratio)

**Usage:** Bancor's automated market maker formula. CW=1 means constant price (stablecoin), CW=0.5 means square root curve. Lower CW = steeper price curve. Used in continuous token offerings and DAOs.

---

## 39. Collateral Coverage Ratio

**Formula:** `Coverage = (Σ Collateral_i × Liquidation_Threshold_i) / Total_Debt`

**Arguments:**

- `Collateral_i`: Value of collateral asset i
- `Liquidation_Threshold_i`: Liquidation threshold for asset i (0-1)
- `Total_Debt`: Total borrowed value

**Usage:** Multi-asset collateral health metric. Coverage > 1 is healthy, < 1 triggers liquidation. Different assets have different thresholds (ETH=0.85, stables=0.95). Used in Aave, Compound for risk assessment.

---

## 40. Yield Farming ROI (with principal)

**Formula:** `ROI = (Farming_Rewards + Fee_Income + IL) / Initial_Capital - 1`

**Arguments:**

- `Farming_Rewards`: Token rewards earned (USD value)
- `Fee_Income`: Trading fee share (USD)
- `IL`: Impermanent loss (negative value, USD)
- `Initial_Capital`: Initial investment (USD)

**Usage:** Total return including all components. Must account for IL even if not realized. Negative IL can offset positive rewards. Used to compare different farming opportunities. Break-even when ROI > risk-free rate.

---

# IMPLEMENTATION NOTES

## Risk Management Formula Categories

1. **Tail Risk**: CDaR, Tail Ratio, Rachev Ratio
2. **Drawdown Analysis**: D-Ratio, RoMaD, Serenity Ratio, Recovery Factor
3. **Performance Smoothness**: Stability Index, M²
4. **Behavioral Finance**: Prospect Ratio

## DeFi Formula Categories

1. **AMM Mechanisms**: Uniswap V3 Tick, Constant Sum, Curve StableSwap
2. **Lending Protocols**: Aave Variable Rate, Compound Rewards, Leverage Ratio
3. **Protocol Economics**: Revenue, Dilution, Maker Stability Fee
4. **Advanced Trading**: Multi-hop Impact, Options Greeks, Perpetual Basis
5. **Tokenomics**: Rebase, Vesting, Bonding Curves

## Usage Best Practices

- Combine multiple metrics for comprehensive analysis
- Consider time-varying nature of DeFi parameters
- Account for gas costs in all on-chain calculations
- Use appropriate confidence levels based on risk tolerance
- Backtest formulas with historical data before live deployment

---

**Total Formula Count: 60 (30 Risk Management + 30 DeFi)**

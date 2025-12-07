# Complete Formula Reference Guide

I've created a comprehensive reference guide that describes all 40 formulas (20 risk management + 20 DeFi) with:

Mathematical Formula: The exact equation used
Arguments: Each input parameter with its meaning and units
Usage: Practical applications, interpretation guidelines, and industry context

Key Highlights:
Risk Management Formulas cover:

Value-at-Risk measures (VaR 95%, 99%, CVaR)
Risk-adjusted return metrics (Sharpe, Sortino, Treynor, Information Ratio)
Drawdown-based metrics (Maximum Drawdown, Calmar, Sterling, Burke, Pain ratios)
Specialized metrics (Beta, Omega, Ulcer Index, Kappa ratios)

DeFi Formulas cover:

AMM mechanics (Impermanent Loss, Swap Output, Pool Value, Slippage)
Lending protocols (Utilization Rate, Interest Rates, Collateral Ratio, Health Factor)
Yield farming (APY calculation, Staking Rewards)
Advanced concepts (Funding Rates, Bonding Curves, Flash Loans, Concentrated Liquidity)

Each formula includes practical interpretation guidelines (e.g., "Sharpe > 1 is good", "HF < 1 triggers liquidation") to help users understand the results and make informed decisions.

## Risk Management Formulas (20)

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

---

## DeFi Formulas (20)

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

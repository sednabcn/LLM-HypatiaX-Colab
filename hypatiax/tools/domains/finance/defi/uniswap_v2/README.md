# HypatiaX: AI-Powered DeFi Risk Analytics 🚀

## Overview

HypatiaX is a comprehensive DeFi liquidity provider (LP) risk analysis platform that combines mathematical modeling, historical backtesting, and AI-powered insights to help users make informed decisions about providing liquidity on Automated Market Makers (AMMs) like Uniswap V2.

The platform provides deep analysis of **Impermanent Loss (IL)**, fee earnings, quality scores, and strategic recommendations across different token pairs and market conditions.

### Key Capabilities

- **Impermanent Loss Calculation**: Precise IL calculations using constant product AMM formulas
- **Historical Backtesting**: 90-day backtests comparing LP vs HODL strategies across ETH, stablecoins, and altcoins
- **Quality Score Metrics**: Daily fee earnings vs IL rate to determine optimal LP positions
- **Multi-Pair Analysis**: Comprehensive testing across volatile (ETH/USDC) and stable (USDT/USDC, DAI/USDC) pairs
- **Visual Analytics**: 4-panel dashboard showing price movements, IL progression, portfolio comparison, and daily advantages
- **Excel Export**: Full data export for custom analysis

---

## 🎯 Core Features

### 1. **Impermanent Loss Engine**

Calculate IL percentage and dollar value for any LP position:

```python
# IL Formula: 2*sqrt(price_ratio) / (price_ratio + 1) - 1
def calculate_il_percentage(current_price: float, initial_price: float) -> float:
    ratio = current_price / initial_price
    il = (2 * (ratio ** 0.5) / (ratio + 1) - 1) * 100
    return il
```

**Key Insight**: IL is **always negative or zero** - it represents a loss compared to simply holding tokens.

### 2. **Quality Score Framework**

Determines if LP fees compensate for IL losses:

```python
quality_score = daily_fees / daily_il_rate

# Interpretation:
# > 2.0  → ✅ EXCELLENT - High profit potential
# > 1.0  → ✅ GOOD - Fees cover IL daily
# 0.5-1.0 → ⚠️ MODERATE - Risky, fees ≈ IL
# < 0.5  → ❌ POOR - Avoid, IL >> fees
```

### 3. **Historical Backtesting**

90-day simulation comparing LP strategy vs HODL:

- **ETH/USDC**: Tests volatile market conditions (-42% price drop)
- **USDT/USDC**: Tests stablecoin pairs (near-zero IL)
- **DAI/USDC**: Tests low-volatility stables
- **SHIB/USDC**: Tests extreme volatility scenarios

### 4. **Breakeven Analysis**

Calculates time required for fees to offset IL:

```python
breakeven_days = abs(il_dollar) / daily_fees
```

### 5. **Fee Tier Strategy**

Volatility-based fee tier recommendations:

| Volatility Level | Price Movement | Recommended Fee Tier | Strategy |
|-----------------|----------------|---------------------|----------|
| Ultra-Low | 0-0.5% | 0.01% - 0.05% | Tight ranges, stables |
| Low | 0.5-3% | 0.05% | Concentrated liquidity |
| Medium | 3-10% | 0.30% | Standard range |
| High | 10-30% | 1.00% | Wide range + active mgmt |
| Extreme | 30%+ | Avoid or 1%+ | Generally unprofitable |

---

## 📊 Installation

### Prerequisites

```bash
Python 3.8+
pip
git
```

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/hypatiax.git
cd hypatiax

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Required Dependencies

```txt
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
requests>=2.28.0
openpyxl>=3.0.10
```

---

## 🚀 Quick Start

### Example 1: Calculate Impermanent Loss

```python
from hypatiax.tools.domains.finance.defi import UNIv2Calculator

calculator = UNIv2Calculator()

# ETH price increased 50% ($2k → $3k)
il_percent = calculator.calculate_il_percentage(
    current_price=3000,
    initial_price=2000
)

print(f"Impermanent Loss: {il_percent:.2f}%")
# Output: Impermanent Loss: -2.02%
```

### Example 2: Run Historical Backtest

```python
from hypatiax.tools.domains.finance.defi import run_complete_backtest

# Backtest ETH/USDC LP position
results, analysis = run_complete_backtest(
    days=90,
    initial_eth=10,
    initial_usdc=20000,
    daily_volume=10000000
)

# Outputs:
# - Console report with metrics
# - PNG visualization (4-panel dashboard)
# - Excel file with daily data
```

### Example 3: Calculate Quality Score

```python
from hypatiax.tools.domains.finance.defi import LPPosition, UNIv2Calculator

position = LPPosition(
    name="ETH/USDC Pool",
    initial_token_a_amount=1.0,
    initial_token_b_amount=2000,
    initial_price_b_in_a=2000,
    current_price_b_in_a=3000,
    days_elapsed=30,
    daily_volume_usd=500_000,
    pool_tvl_usd=10_000_000
)

calculator = UNIv2Calculator()
result = calculator.calculate_il_with_fees(position)

print(f"Quality Score: {result['daily_fees'] / abs(result['il_dollar'] / position.days_elapsed):.2f}")
```

---

## 📈 Backtest Results Summary

### Test Scenarios (90-Day Period)

| Pool | Price Change | IL | Fees Earned | Net Result | Quality Score | Winner |
|------|--------------|-----|-------------|------------|---------------|--------|
| **ETH/USDC** | -42.22% | -$2,472 | $1,350 | **+$738** | 0.54 | LP ✅ |
| **USDT/USDC** | -0.05% | -$0 | $2,700 | **+$2,700** | ∞ | LP ✅ |
| **DAI/USDC** | -0.07% | -$0 | $2,184 | **+$2,184** | ∞ | LP ✅ |
| **SHIB/USDC** | -39.77% | -$313 | $546 | **-$8,903** | 1.74 | HODL ❌ |

### Key Findings

1. **Stablecoin Pairs Dominate**: USDT/USDC and DAI/USDC had 100% win rates with zero IL
2. **Volatility = Risk**: ETH dropped 42% but fees barely compensated for IL
3. **Extreme Vol Loses**: SHIB/USDC lost massively despite earning fees
4. **Quality Score Rule**: Only pairs with scores >1.0 should be considered

---

## 🔬 Mathematical Formulas

### 1. Constant Product AMM

```
x * y = k  (where k is constant)
```

### 2. Swap Output (with 0.3% fee)

```
amount_out = (y * amount_in_after_fee) / (x + amount_in_after_fee)
where: amount_in_after_fee = amount_in * 0.997
```

### 3. Impermanent Loss Percentage

```
IL% = [2*√(price_ratio) / (price_ratio + 1) - 1] × 100
where: price_ratio = current_price / initial_price
```

### 4. IL in Dollars

```
IL$ = initial_position_value × (IL% / 100)
```

### 5. LP Token Minting

```
liquidity = √(reserve_x × reserve_y)
lp_tokens = liquidity - MINIMUM_LIQUIDITY (for first deposit)
```

### 6. Daily Fees Earned

```
daily_fees = (daily_volume × fee_rate) × (your_liquidity / total_pool_liquidity)
```

### 7. Quality Score

```
quality_score = daily_fees / (abs(IL$) / days_elapsed)
```

---

## 📊 Visualization Dashboard

Each backtest generates a 4-panel visualization:

### Panel 1: Price Movement & Impermanent Loss

- Blue line: ETH price over time
- Red line: IL percentage progression
- Shows correlation between volatility and IL

### Panel 2: Fees vs Impermanent Loss

- Green line: Cumulative fees earned
- Red line: IL in USD
- Green shading: Profit zone (fees > IL)

### Panel 3: LP vs HODL Portfolio Value

- Orange line: HODL portfolio value
- Purple line: LP portfolio value
- Shading shows which strategy wins daily

### Panel 4: Daily LP Advantage

- Green bars: Days LP wins
- Red bars: Days HODL wins
- Shows daily performance differential

---

## 💡 Strategic Recommendations

### For Small Capital ($20K-$100K)

❌ **Don't Expect High Returns**

- Small LP positions earn minimal fees
- Example: $20K in DAI/USDC = ~$100-400/year (0.5-2% APY)

✅ **Better Strategies**:

1. Focus on **stablecoin pairs** (zero IL risk)
2. Use **Uniswap V3 concentrated liquidity** (10-100x fee earnings)
3. Consider **yield farming** with LP tokens
4. Simply **HODL** if bullish on assets

### For Medium Capital ($100K-$500K)

⚠️ **Moderate Returns Possible**

- More capital = larger fee share
- Still need high-quality pools

✅ **Recommended Approach**:

1. **70% stablecoins** (USDC/USDT, DAI/USDC)
2. **20% blue-chip pairs** (ETH/stETH, WBTC/ETH)
3. **10% experimental** (high-fee exotic pairs)
4. Active rebalancing every 7-14 days

### For Large Capital ($500K+)

✅ **Professional LP Strategy**

- Potential APY: 5-30%
- Requires active management

**Key Components**:

1. **Concentrated liquidity** (Uniswap V3)
2. **Multiple pools** for diversification
3. **Automated rebalancing** (custom bots)
4. **Risk hedging** (IL protection protocols)

### When to Provide Liquidity

✅ **PROVIDE** when:

- Quality score > 1.0
- Stablecoin pairs
- Bull markets (trending upward)
- High trading volume pools
- Low short-term volatility

❌ **AVOID** when:

- Quality score < 0.5
- Highly volatile altcoins
- Bear markets (trending downward)
- Low liquidity pools
- Expecting large price moves

---

## 🔧 API Reference

### Core Classes

#### `LPPosition`

```python
@dataclass
class LPPosition:
    name: str
    initial_token_a_amount: float
    initial_token_b_amount: float
    initial_price_b_in_a: float
    current_price_b_in_a: float
    days_elapsed: int
    daily_volume_usd: float
    fee_rate: float = 0.003
    pool_tvl_usd: float = 1_000_000
```

#### `UNIv2Calculator`

```python
class UNIv2Calculator:
    @staticmethod
    def calculate_il_percentage(current_price, initial_price) -> float

    @staticmethod
    def calculate_il_with_fees(position: LPPosition) -> Dict
```

#### `UniswapV2Pool`

```python
class UniswapV2Pool:
    def __init__(self, reserve_x: float, reserve_y: float, fee: float = 0.003)
    def get_amount_out(self, amount_in: float) -> float
    def update_reserves(self, amount_in: float, amount_out: float)
```

### Functions

#### `run_complete_backtest()`

```python
def run_complete_backtest(
    days: int = 90,
    initial_eth: float = 10,
    initial_usdc: float = 20000,
    daily_volume: float = 5000000,
    export_excel: bool = True
) -> Tuple[pd.DataFrame, Dict]
```

**Returns**:

- DataFrame with daily results
- Dictionary with analysis metrics

#### `get_eth_historical_prices()`

```python
def get_eth_historical_prices(days: int = 90) -> List[Dict]
```

**Returns**: List of price dictionaries with timestamp, date, and price_usd

---

## 📁 Project Structure

```
hypatiax/
├── tools/
│   └── domains/
│       └── finance/
│           └── defi/
│               ├── uniswap_v2_formulas.py          # Core formulas
│               ├── uniswap_v2_backtest_analysis.py # Backtesting engine
│               ├── quality_score_calc.py           # Quality metrics
│               └── il_calculator.py                # IL calculations
├── data/
│   └── historical/                                 # Price data cache
├── outputs/
│   ├── backtest_analysis_*.png                     # Visualizations
│   └── lp_backtest_*.xlsx                          # Excel exports
├── tests/
│   └── test_calculations.py                        # Unit tests
├── requirements.txt
├── README.md
└── LICENSE
```

---

## 🧪 Example Use Cases

### Case 1: Should I provide liquidity to ETH/USDC?

```python
# Run backtest
results, analysis = run_complete_backtest(
    days=90,
    initial_eth=10,
    initial_usdc=20000,
    daily_volume=10000000
)

# Check quality score
daily_fees = analysis['summary']['total_fees_earned'] / analysis['summary']['total_days']
daily_il_rate = abs(analysis['summary']['final_il_usd']) / analysis['summary']['total_days']
quality_score = daily_fees / daily_il_rate

if quality_score > 1.0:
    print("✅ LP is profitable - fees cover IL")
else:
    print("❌ HODL is better - fees don't cover IL")
```

### Case 2: Compare Multiple Pools

```python
pools = ['ETH', 'USDT', 'DAI', 'SHIB']
results = {}

for token in pools:
    res, _ = run_complete_backtest(
        days=90,
        token_symbol=token
    )
    results[token] = res

# Find best pool by net profit
best_pool = max(results.items(), key=lambda x: x[1]['advantage_usd'].iloc[-1])
print(f"Best pool: {best_pool[0]}")
```

### Case 3: Risk Assessment

```python
analysis = analyze_results(backtest_df)

max_il = analysis['risk']['max_il_pct']
max_drawdown = analysis['risk']['max_drawdown_from_hodl']

if max_il < -5.0:
    print("⚠️ HIGH RISK: IL exceeds 5%")
if max_drawdown < -1000:
    print("⚠️ HIGH RISK: Max drawdown > $1000")
```

---

## 📚 Formula Catalog

### Impermanent Loss by Price Change

| Price Change | IL % |
|--------------|------|
| +25% | -0.6% |
| +50% | -2.0% |
| +100% | -5.7% |
| +200% | -13.4% |
| +300% | -20.0% |
| -50% | -5.7% |
| -75% | -20.0% |

### Position Value Calculation

**HODL Value**:

```
hodl_value = (initial_eth × current_eth_price) + initial_usdc
```

**LP Value** (without fees):

```
lp_value = 2 × √(initial_eth × initial_usdc × current_price)
```

**LP Value** (with fees):

```
lp_value_with_fees = lp_value + cumulative_fees
```

---

## 🎓 Key Learnings

### 1. Impermanent Loss is Always Negative

IL represents opportunity cost vs holding. The formula ensures IL ≤ 0 always.

### 2. Fees Can Compensate for IL

High trading volume generates fees that offset IL losses. Quality score measures this.

### 3. Stablecoins Are King

Near-zero price movement = near-zero IL = pure fee earnings.

### 4. Volatility = Risk

Larger price moves create exponentially larger IL. Bear markets devastate LP positions.

### 5. Small Capital = Small Returns

Without significant liquidity ($500K+), LP returns are typically <2% APY on most pairs.

### 6. Active Management Required

Passive LP positions in volatile pairs almost always underperform HODL. Rebalancing and range adjustment (v3) are critical.

---

## 🛠️ Advanced Features

### Custom Pool Analysis

```python
# Analyze custom token pair
custom_position = LPPosition(
    name="Custom Pool",
    initial_token_a_amount=100,
    initial_token_b_amount=50000,
    initial_price_b_in_a=500,
    current_price_b_in_a=750,
    days_elapsed=45,
    daily_volume_usd=1_000_000,
    pool_tvl_usd=20_000_000
)

result = calculator.calculate_il_with_fees(custom_position)
```

### Export to CSV

```python
from hypatiax.tools.domains.finance.defi import export_results_to_csv

positions = generate_test_positions()
results = [calculator.calculate_il_with_fees(p) for p in positions]
export_results_to_csv(results, "my_analysis.csv")
```

---

## 🐛 Troubleshooting

### Issue: "Failed to fetch price data"

**Solution**: Check internet connection and CoinGecko API rate limits (50 calls/min free tier)

### Issue: "Quality score = inf"

**Solution**: This is correct for stablecoin pairs where IL ≈ 0. Means excellent profitability.

### Issue: "All IL values are negative"

**Solution**: This is expected behavior. IL is always ≤ 0 by definition.

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit pull request with clear description

---

## 📧 Contact & Support

- **GitHub**: [github.com/yourusername/hypatiax](https://github.com/yourusername/hypatiax)
- **Issues**: Use GitHub Issues for bug reports
- **Documentation**: [Full docs](https://hypatiax.readthedocs.io)

---

## 🙏 Acknowledgments

- Uniswap V2 protocol documentation
- CoinGecko API for historical price data
- The Graph for on-chain data
- DeFi community for research and insights

---

## 🔮 Roadmap

- [ ] Uniswap V3 concentrated liquidity support
- [ ] Multi-chain support (Polygon, Arbitrum, BSC)
- [ ] Real-time monitoring dashboard
- [ ] Automated rebalancing recommendations
- [ ] IL protection strategy simulations
- [ ] Integration with wallet APIs
- [ ] Machine learning price prediction models
- [ ] Gas cost optimization

---

**Built with ❤️ for the DeFi community**

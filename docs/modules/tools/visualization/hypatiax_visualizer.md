# Module: `tools/visualization/hypatiax_visualizer.py`

## Description

HypatiaX Visualization Scripts
Beautiful, professional charts for DeFi analysis

**Last Modified**: 2025-11-13T10:20:21.287042

## Dependencies

- `datetime`
- `hypatiax_dataset`
- `json`
- `matplotlib.pyplot`
- `numpy`
- `seaborn`

## Classes

### `HypatiaXVisualizer`

Professional visualization suite for DeFi analytics

**Methods**:

- `__init__(self)`
- `plot_il_over_time(self, historical_data, save_path)`
  - Plot IL% progression over time with fee income
- `plot_price_impact_heatmap(self, save_path)`
  - Heatmap showing price impact vs trade size and liquidity
- `plot_risk_score_breakdown(self, il_pct, volatility, range_width, days, save_path)`
  - Bar chart showing risk score components
- `plot_scenario_comparison(self, scenarios_data, save_path)`
  - Compare multiple Uniswap scenarios side by side
- `plot_backtest_summary(self, historical_data, save_path)`
  - Comprehensive backtest visualization
- `generate_all_charts(self, historical_data)`
  - Generate complete visualization suite

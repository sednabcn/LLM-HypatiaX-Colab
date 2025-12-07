I've created extended versions of both dataset generators with 20 formulas each:
Risk Management Generator (20 formulas):
Original 8:

1. VaR 95%
2. Sharpe Ratio
3. CVaR 95%
4. Beta
5. Sortino Ratio
6. Information Ratio
7. Maximum Drawdown
8. Treynor Ratio

Added 12:
9. Calmar Ratio
10. Omega Ratio
11. VaR 99%
12. Modified Sharpe Ratio (with skewness)
13. Ulcer Index
14. Martin Ratio
15. Kappa Ratio (3rd order)
16. Gain-Loss Ratio
17. Upside Potential Ratio
18. Sterling Ratio
19. Burke Ratio
20. Pain Ratio

DeFi Generator (20 formulas):
Original 4:

1. Impermanent Loss
2. AMM Swap Output
3. Utilization Rate
4. Liquidity Pool Value

Added 16:
5. Compound Interest Rate
6. Collateral Ratio
7. Liquidation Price
8. Yield Farming APY
9. Slippage
10. LP Token Share
11. Health Factor (Aave-style)
12. Funding Rate (Perpetuals)
13. Price Impact
14. Staking Rewards
15. Bonding Curve Price
16. Flash Loan Fee
17. Vesting Schedule
18. Arbitrage Profit
19. Gas Cost ROI
20. Concentrated Liquidity Position (Uniswap V3)

Both generators maintain the same structure and error handling as the originals, with all formulas using dimensionless units where appropriate to avoid unit registry issues.Claude can make mistakes. Please double-check responses.

I've created the generate_full_dataset.py script to scale up to 150 formulas. Here are the key features:
Dataset Generation Strategy:

DeFi Domain (40 formulas):

1-3 variables per formula
Common DeFi patterns:

Square root patterns (price impact)
Inverse relationships (exchange rates)
Logarithmic (diminishing returns)
Bounded ratios (IL-like)
Geometric means
Share calculations




Risk Domain (50 formulas):

2-4 variables per formula
Risk-specific patterns:

VaR calculations (90%, 95%, 99% confidence)
Sharpe-like ratios
Portfolio variance
Coefficient of variation
Risk-adjusted returns





Key Features:

Reproducibility: Fixed random seed (42) for consistent results
Variety: Randomized complexity, sample sizes, and noise levels
Realistic data: Appropriate ranges for each domain (tokens for DeFi, standardized returns for Risk)
Error handling: Try-catch blocks to continue on failures
Progress tracking: Clear console output for each formula
Validation tracking: Counts valid vs invalid formulas
Summary statistics: Final report with validation rates

Output:

data/defi_synthetic_batch.json (40 formulas)
data/risk_synthetic_batch.json (50 formulas)
Combined with existing batches, reaches ~150 total formulas

The script uses diverse mathematical patterns to ensure the symbolic regression system is tested across various formula types and complexities.RetryClaude can make mistakes. Please double-check responses.
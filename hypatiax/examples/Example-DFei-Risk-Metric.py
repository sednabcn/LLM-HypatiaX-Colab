# Initialize system
generator = AnalyticalExpressionGenerator(api_key="your-key")

# User requirement
requirement = """
Create a novel risk metric for Uniswap V3 liquidity providers that:
1. Combines impermanent loss with fee income
2. Adjusts for concentrated liquidity range width
3. Penalizes positions during high volatility
4. Rewards positions with high trading volume
5. Outputs a score from 0 (safest) to 100 (riskiest)
"""

# Generate candidates
candidates = generator.generate_and_validate(
    requirements=requirement,
    domain="defi",
    n_candidates=5
)

# Best formula
best = candidates[0]

print("Generated Formula:")
print(best['formula_latex'])
print("\nExplanation:")
print(best['explanation'])
print("\nValidation Score:", best['score'])
print("\nPython Implementation:")
print(best['formula_python'])

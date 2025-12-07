# test_hybrid_api.py
import sys

sys.path.append("../tools")
import numpy as np
from symbolic.hybrid_system import HybridDiscoverySystem

# Test discovery
system = HybridDiscoverySystem(domain="defi")

# Generate data for "impermanent loss"
price_ratios = np.random.uniform(0.1, 10, (100, 1))
il = 2 * np.sqrt(price_ratios[:, 0]) / (price_ratios[:, 0] + 1) - 1
il += np.random.normal(0, 0.01, 100)

# Discover
result = system.discover_validate_interpret(
    X=price_ratios,
    y=il,
    variable_names=["price_ratio"],
    variable_descriptions={"price_ratio": "Current/Initial price"},
    variable_units={"price_ratio": "dimensionless"},
    description="Impermanent loss for AMM pool",
)

print(f"Discovered: {result['discovery']['expression']}")
print(f"R²: {result['discovery']['r2_score']:.4f}")
print(f"Valid: {result['validation']['valid']}")
print(f"Score: {result['validation']['total_score']:.1f}")

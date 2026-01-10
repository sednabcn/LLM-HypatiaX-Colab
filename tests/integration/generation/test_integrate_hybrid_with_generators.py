# Create: scripts/integrate_hybrid_with_generators.py

from hypatiax.core.generation.defi_queries_dataset_generator import (
    generate_defi_queries,
)
from hypatiax.core.generation.risk_queries_dataset_generator import (
    generate_risk_queries,
)
from hypatiax.symbolic.hybrid_system import HybridDiscoverySystem

# Load your 280 DeFi formulas
defi_formulas = generate_defi_queries()

# For each formula, test discovery
system = HybridDiscoverySystem(domain="defi")

for formula in defi_formulas[:10]:  # Test first 10
    # Generate synthetic data from formula
    X, y = generate_synthetic_data(formula)

    # Try to discover it back
    result = system.discover_validate_interpret(
        X=X,
        y=y,
        variable_names=formula["variables"],
        description=formula["description"],
    )

    # Compare discovered vs original
    print(f"Original: {formula['analytical_formula']}")
    print(f"Discovered: {result['expression']}")
    print(
        f"Match: {compare_formulas(formula['analytical_formula'], result['expression'])}"
    )

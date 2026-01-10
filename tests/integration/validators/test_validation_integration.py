#!/usr/bin/env python3
import numpy as np
from hypatiax.tools.validation.ensemble_validator import EnsembleValidator

# Initialize validator
validator = EnsembleValidator(domain="defi")

# Test Kelly criterion formula
print("=" * 80)
print("TESTING VALIDATION SYSTEM")
print("=" * 80)

result = validator.validate_complete(
    expression_str="min(expected_fee_apy / (2 * il_risk**2), 1.0)",
    variable_definitions={
        "expected_fee_apy": "Expected annual yield from LP fees",
        "il_risk": "Impermanent loss risk (volatility measure)",
    },
    variable_units={
        "expected_fee_apy": "dimensionless",
        "il_risk": "dimensionless",
    },
    test_data={
        "expected_fee_apy": np.array([0.15, 0.20, 0.25]),
        "il_risk": np.array([0.10, 0.15, 0.20]),
    },
)

print(f"\n✅ VALIDATION COMPLETE")
print(f"  Overall Valid: {result['valid']}")
print(f"  Total Score: {result['total_score']:.2f}")
print(f"\nLayer Scores:")
for layer, score in result["layer_scores"].items():
    print(f"  {layer}: {score:.2f}")

print(f"\nErrors: {len(result['errors'])}")
for error in result["errors"]:
    print(f"  - {error}")

print(f"\nWarnings: {len(result['warnings'])}")
for warning in result["warnings"][:3]:
    print(f"  - {warning}")

print("\n" + "=" * 80)

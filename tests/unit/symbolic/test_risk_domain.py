#!/usr/bin/env python3
"""
Test the actual validator with the risk domain formula
"""

import sys

sys.path.insert(0, "/home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab")

from hypatiax.tools.symbolic.enhanced_symbolic_validator import (
    EnhancedSymbolicValidator,
)


def test_risk_domain():
    """Test risk management-specific rules"""
    validator = EnhancedSymbolicValidator()

    formula = r"\sigma \cdot \sqrt{t}"
    print(f"Testing formula: {formula}")
    print("=" * 60)

    result = validator.validate(formula, domain="risk")

    print(f"Syntactically valid: {result['syntactically_valid']}")
    print(f"Domain valid: {result['domain_valid']}")
    print(f"Score: {result['score']}")
    print(f"Expression: {result.get('expression', 'N/A')}")

    print("\nErrors:")
    for err in result["errors"]:
        print(f"  - {err}")

    print("\nWarnings:")
    for warn in result["warnings"]:
        print(f"  - {warn}")

    print("\nInfo:")
    for info in result.get("info", []):
        print(f"  - {info}")

    print("\n" + "=" * 60)

    # Test assertions
    assert result["syntactically_valid"], "Formula should be syntactically valid"
    assert len(result["warnings"]) > 0, "Should have risk-specific warnings"

    print("✓ TEST PASSED!")
    return result


if __name__ == "__main__":
    try:
        test_risk_domain()
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Comprehensive Validation System Integration Test
Tests all validation layers with various DeFi formulas
"""

import numpy as np
from hypatiax.tools.validation.ensemble_validator import EnsembleValidator


def print_validation_report(result, test_name):
    """Print detailed validation report"""
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)

    # Overall
    status = "✅ PASS" if result["valid"] else "❌ FAIL"
    print(
        f"{status} | Score: {result['total_score']:.2f}/100 | Valid: {result['valid']}"
    )

    # Layer scores
    print("\nLayer Performance:")
    for layer, score in result["layer_scores"].items():
        if score >= 90:
            symbol = "✅"
        elif score >= 70:
            symbol = "⚠️ "
        else:
            symbol = "❌"
        print(f"  {symbol} {layer.capitalize():12s}: {score:6.2f}/100")

    # Penalties
    if result.get("penalties_applied"):
        total_penalty = result["penalties_applied"]["total_deducted"]
        if total_penalty > 0:
            print(f"\nPenalties Applied: -{total_penalty:.2f}")
            for key, val in result["penalties_applied"].items():
                if key != "total_deducted" and val > 0:
                    print(f"  • {key}: -{val:.2f}")

    # Errors
    if result["errors"]:
        print(f"\n❌ Errors ({len(result['errors'])}):")
        for err in result["errors"][:3]:
            print(f"  • {err}")
        if len(result["errors"]) > 3:
            print(f"  ... and {len(result['errors']) - 3} more")

    # Warnings
    if result["warnings"]:
        print(f"\n⚠️  Warnings ({len(result['warnings'])}):")
        for warn in result["warnings"][:3]:
            print(f"  • {warn}")
        if len(result["warnings"]) > 3:
            print(f"  ... and {len(result['warnings']) - 3} more")

    # Recommendations
    if result.get("recommendations"):
        print(f"\n💡 Top Recommendations:")
        for rec in result["recommendations"][:3]:
            print(f"  • {rec}")

    print("=" * 80)


def main():
    print("\n" + "=" * 80)
    print(" " * 20 + "HYPATIAX VALIDATION SYSTEM")
    print(" " * 15 + "Comprehensive Integration Test Suite")
    print("=" * 80)

    validator = EnsembleValidator(domain="defi")

    # ========================================================================
    # TEST 1: Kelly Criterion LP Position Sizing
    # ========================================================================
    result1 = validator.validate_complete(
        expression_str="min(expected_fee_apy / (2 * il_risk**2), 1.0)",
        variable_definitions={
            "expected_fee_apy": "Expected annual yield from LP fees",
            "il_risk": "Impermanent loss risk (volatility)",
        },
        variable_units={
            "expected_fee_apy": "dimensionless",
            "il_risk": "dimensionless",
        },
        test_data={
            "expected_fee_apy": np.array([0.15, 0.20, 0.25, 0.30]),
            "il_risk": np.array([0.10, 0.15, 0.20, 0.25]),
        },
    )
    print_validation_report(result1, "Kelly Criterion LP Position Sizing")

    # ========================================================================
    # TEST 2: AMM Constant Product (Should score high)
    # ========================================================================
    result2 = validator.validate_complete(
        expression_str="sqrt(reserve0 * reserve1)",
        variable_definitions={
            "reserve0": "Token 0 reserves in pool",
            "reserve1": "Token 1 reserves in pool",
        },
        variable_units={
            "reserve0": "USD",
            "reserve1": "USD",
        },
        test_data={
            "reserve0": np.array([100.0, 500.0, 1000.0, 5000.0]),
            "reserve1": np.array([50.0, 250.0, 500.0, 2500.0]),
        },
    )
    print_validation_report(result2, "AMM Constant Product Formula")

    # ========================================================================
    # TEST 3: Impermanent Loss Formula
    # ========================================================================
    result3 = validator.validate_complete(
        expression_str="2 * sqrt(r) / (1 + r) - 1",
        variable_definitions={
            "r": "Price ratio (P_t / P_0)",
        },
        variable_units={
            "r": "dimensionless",
        },
        test_data={
            "r": np.array([0.5, 0.8, 1.0, 1.2, 1.5, 2.0]),
        },
    )
    print_validation_report(result3, "Impermanent Loss Formula")

    # ========================================================================
    # TEST 4: Swap Output with Fee (Should detect fee constraints)
    # ========================================================================
    result4 = validator.validate_complete(
        expression_str="(amount_in * (1 - fee) * reserve_out) / (reserve_in + amount_in * (1 - fee))",
        variable_definitions={
            "amount_in": "Input token amount",
            "fee": "Pool fee (e.g., 0.003 for 0.3%)",
            "reserve_in": "Input token reserves",
            "reserve_out": "Output token reserves",
        },
        variable_units={
            "amount_in": "USD",
            "fee": "dimensionless",
            "reserve_in": "USD",
            "reserve_out": "USD",
        },
        test_data={
            "amount_in": np.array([10.0, 50.0, 100.0]),
            "fee": np.array([0.003, 0.003, 0.003]),  # 0.3% fee
            "reserve_in": np.array([1000.0, 1000.0, 1000.0]),
            "reserve_out": np.array([500.0, 500.0, 500.0]),
        },
    )
    print_validation_report(result4, "AMM Swap Output with Fee")

    # ========================================================================
    # TEST 5: Sharpe Ratio (Should detect sigma > 0 constraint)
    # ========================================================================
    result5 = validator.validate_complete(
        expression_str="(return_p - return_f) / sigma",
        variable_definitions={
            "return_p": "Portfolio return",
            "return_f": "Risk-free return",
            "sigma": "Portfolio volatility",
        },
        variable_units={
            "return_p": "dimensionless",
            "return_f": "dimensionless",
            "sigma": "dimensionless",
        },
        test_data={
            "return_p": np.array([0.15, 0.20, 0.25]),
            "return_f": np.array([0.02, 0.02, 0.02]),
            "sigma": np.array([0.10, 0.15, 0.20]),  # All positive ✓
        },
    )
    print_validation_report(result5, "Sharpe Ratio (Finance Domain)")

    # ========================================================================
    # TEST 6: Invalid Formula (Should fail validation)
    # ========================================================================
    result6 = validator.validate_complete(
        expression_str="price / quantity",
        variable_definitions={
            "price": "Asset price",
            "quantity": "Asset quantity",
        },
        variable_units={
            "price": "USD",
            "quantity": "dimensionless",
        },
        test_data={
            "price": np.array([100.0, 200.0, 300.0]),
            "quantity": np.array([0.0, 5.0, 10.0]),  # Contains zero! ❌
        },
    )
    print_validation_report(result6, "Division by Zero Test (Should Fail)")

    # ========================================================================
    # SUMMARY STATISTICS
    # ========================================================================
    stats = validator.get_statistics()

    print("\n" + "=" * 80)
    print(" " * 25 + "VALIDATION STATISTICS")
    print("=" * 80)
    print(f"Total Tests:          {stats['total_validations']}")
    print(f"Passed:               {stats['valid_count']}")
    print(f"Failed:               {stats['invalid_count']}")
    print(f"Success Rate:         {stats['success_rate'] * 100:.1f}%")
    print(f"Average Score:        {stats['average_total_score']:.2f}/100")
    print(f"Threshold:            {stats['threshold_used']:.1f}")
    print(f"\nAverage Layer Scores:")
    for layer, score in stats["average_layer_scores"].items():
        print(f"  {layer.capitalize():12s}: {score:.2f}")
    print(f"\nWeakest Layer:        {validator.get_weakest_layer()}")
    print("=" * 80)

    # ========================================================================
    # RECOMMENDATIONS
    # ========================================================================
    print("\n" + "=" * 80)
    print(" " * 25 + "SYSTEM INSIGHTS")
    print("=" * 80)

    print("\n✅ Validation System Status: OPERATIONAL")
    print("\nKey Observations:")

    weakest = validator.get_weakest_layer()
    avg_weakest = stats["average_layer_scores"][weakest]

    if avg_weakest < 85:
        print(
            f"  ⚠️  {weakest.capitalize()} layer averaging {avg_weakest:.1f} - consider tuning"
        )
    else:
        print(f"  ✅ All layers performing above threshold")

    print(f"\nValidation Thresholds:")
    print(
        f"  • Minimum Total Score:   {validator.VALIDATION_THRESHOLDS['minimum_total_score']}"
    )
    print(
        f"  • Critical Failure:      {validator.VALIDATION_THRESHOLDS['critical_failure_threshold']}"
    )
    print(
        f"  • Edge Case Penalty:     {validator.VALIDATION_THRESHOLDS['edge_case_penalty']}"
    )
    print(
        f"  • Dimensional Penalty:   {validator.VALIDATION_THRESHOLDS['dimensional_inconsistency_penalty']}"
    )

    print("\n" + "=" * 80)
    print(" " * 20 + "Integration Test Complete ✅")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

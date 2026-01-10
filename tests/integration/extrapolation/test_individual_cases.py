"""
Individual Test Case Runner for Hybrid System Debugging

This script tests each problematic case individually with detailed diagnostics.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

import numpy as np
from hypatiax.core.generation.hybrid_system_defi_domain import HybridSystemDeFiFixed
from hypatiax.core.generation.experiment_protocol_defi import DeFiExperimentProtocol


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}".center(80))
    print("=" * 80)


def test_case_detailed(case_name, domain, hybrid, protocol, num_samples=100):
    """
    Test a single case with detailed diagnostics

    Args:
        case_name: Description substring to match
        domain: Domain name (e.g., 'liquidity')
        hybrid: HybridSystemDeFiFixed instance
        protocol: DeFiExperimentProtocol instance
        num_samples: Number of samples
    """
    print_section(f"Testing: {case_name}")

    # Load test cases
    test_cases = protocol.load_test_data(domain, num_samples=num_samples)

    # Find matching case
    target_case = None
    for desc, X, y, var_names, meta in test_cases:
        if case_name.lower() in desc.lower():
            target_case = (desc, X, y, var_names, meta)
            break

    if not target_case:
        print(f"[ERROR] Case not found: {case_name}")
        print(f"\nAvailable cases in {domain}:")
        for desc, _, _, _, _ in test_cases:
            print(f"  * {desc}")
        return None

    desc, X, y, var_names, meta = target_case

    # Display test case info
    print(f"\n[INFO] Test Case Details:")
    print(f"  Description: {desc}")
    print(f"  Variables: {', '.join(var_names)}")
    print(f"  Samples: {len(X)}")
    print(f"  X shape: {X.shape}")
    print(f"  y shape: {y.shape}")
    print(f"  y range: [{y.min():.6f}, {y.max():.6f}]")

    if meta.get("extrapolation_test"):
        print(f"  [WARNING] EXTRAPOLATION TEST")

    if meta.get("ground_truth"):
        print(f"  Ground Truth: {meta['ground_truth']}")

    if meta.get("constants"):
        print(f"  Constants: {meta['constants']}")

    # Sample data points
    print(f"\n[INFO] Sample Data Points:")
    for i in range(min(3, len(X))):
        print(f"  X[{i}] = {X[i]} -> y[{i}] = {y[i]:.6f}")

    print("\n" + "-" * 80)

    # Step 1: Test formula detection
    print(f"\n[STEP 1] Formula Type Detection:")
    is_math = hybrid._is_mathematical_formula(desc, meta)
    print(f"  Is Mathematical Formula: {is_math}")

    # Step 2: Generate LLM formula
    print(f"\n[STEP 2] LLM Formula Generation:")
    llm_result = hybrid.generate_llm_formula(desc, domain, var_names, meta)

    if "error" in llm_result:
        print(f"  [ERROR] LLM Generation Failed: {llm_result['error']}")
        return None

    print(f"  Specialized Prompt Used: {llm_result.get('specialized', False)}")
    print(f"  Formula: {llm_result.get('formula', 'N/A')}")

    print(f"\n  Python Code:")
    code = llm_result.get("python_code", "N/A")
    if code != "N/A":
        for line in code.split("\n"):
            print(f"    {line}")
    else:
        print(f"    [ERROR] No code generated!")
        return None

    print(f"\n  Explanation:")
    expl = llm_result.get("explanation", "N/A")
    for line in expl.split("\n")[:3]:  # First 3 lines
        print(f"    {line}")

    # Step 3: Evaluate LLM formula
    print(f"\n[STEP 3] LLM Formula Evaluation:")
    llm_metrics = hybrid.evaluate_llm_formula(llm_result, X, y, var_names, verbose=True)

    if not llm_metrics.get("success"):
        print(f"  [ERROR] Evaluation Failed: {llm_metrics.get('error', 'Unknown')}")
        return None

    print(f"\n  LLM Metrics:")
    print(f"    R^2:  {llm_metrics['r2']:.6f}")
    print(f"    RMSE: {llm_metrics['rmse']:.6f}")
    print(f"    MAE:  {llm_metrics['mae']:.6f}")

    # Step 4: Train NN
    print(f"\n[STEP 4] Neural Network Training:")
    nn_model, nn_metrics, scaler_X, scaler_y = hybrid.train_nn(X, y, epochs=300)

    print(f"  NN Metrics:")
    print(f"    R^2:  {nn_metrics['r2']:.6f}")
    print(f"    RMSE: {nn_metrics['rmse']:.6f}")
    print(f"    MAE:  {nn_metrics['mae']:.6f}")

    # Step 5: Compare predictions
    print(f"\n[STEP 5] Prediction Comparison:")

    # Get predictions
    llm_pred = llm_metrics.get("predictions")
    nn_pred = hybrid._get_nn_predictions(nn_model, X, scaler_X, scaler_y)

    print(f"\n  Sample Predictions (First 5):")
    print(
        f"  {'Index':<6} {'True Value':<15} {'LLM Pred':<15} {'NN Pred':<15} {'LLM Error':<12} {'NN Error':<12}"
    )
    print(f"  {'-' * 6} {'-' * 15} {'-' * 15} {'-' * 15} {'-' * 12} {'-' * 12}")

    for i in range(min(5, len(y))):
        llm_err = abs(y[i] - llm_pred[i]) if llm_pred is not None else float("nan")
        nn_err = abs(y[i] - nn_pred[i])
        print(
            f"  {i:<6} {y[i]:<15.6f} {llm_pred[i]:<15.6f} {nn_pred[i]:<15.6f} {llm_err:<12.6f} {nn_err:<12.6f}"
        )

    # Step 6: Decision logic
    print(f"\n[STEP 6] Decision Logic Analysis:")

    llm_r2 = llm_metrics["r2"]
    nn_r2 = nn_metrics["r2"]

    print(f"  LLM R^2: {llm_r2:.6f}")
    print(f"  NN R^2:  {nn_r2:.6f}")
    print(f"  Difference: {abs(llm_r2 - nn_r2):.6f}")

    print(f"\n  Decision Path:")
    if is_math and llm_r2 > 0.70:
        print(f"    -> PRIORITY 1: Mathematical formula + LLM working (R^2 > 0.70)")
        print(f"    -> Decision: LLM")
    elif llm_r2 > 0.95:
        print(f"    -> PRIORITY 3: LLM excellent (R^2 > 0.95)")
        print(f"    -> Decision: LLM")
    elif llm_r2 > 0.70 and nn_r2 > 0.70:
        print(f"    -> PRIORITY 4: Both viable (R^2 > 0.70)")
        print(f"    -> Decision: ENSEMBLE")
    else:
        print(f"    -> PRIORITY 5: Fallback to NN")
        print(f"    -> Decision: NN")
        if llm_r2 < 0.70:
            print(f"    -> Reason: LLM R^2 ({llm_r2:.4f}) below threshold (0.70)")

    # Summary
    print(f"\n[SUMMARY]")
    if llm_r2 > 0.99:
        status = "[EXCELLENT]"
    elif llm_r2 > 0.95:
        status = "[GOOD]"
    elif llm_r2 > 0.80:
        status = "[ACCEPTABLE]"
    else:
        status = "[NEEDS IMPROVEMENT]"

    print(f"  Status: {status}")
    print(f"  Best Method: {'LLM' if llm_r2 > nn_r2 else 'NN'}")
    print(f"  Best R^2: {max(llm_r2, nn_r2):.6f}")

    return {
        "description": desc,
        "is_math_formula": is_math,
        "llm_r2": llm_r2,
        "nn_r2": nn_r2,
        "llm_formula": llm_result.get("formula", "N/A"),
        "success": llm_metrics["success"],
    }


def run_problematic_cases():
    """Run all problematic cases identified in the analysis"""

    print("=" * 80)
    print("INDIVIDUAL TEST CASE RUNNER - PROBLEMATIC CASES".center(80))
    print("=" * 80)

    hybrid = HybridSystemDeFiFixed()
    protocol = DeFiExperimentProtocol()

    # Define problematic cases
    test_cases = [
        {
            "name": "optimal lp position",
            "domain": "liquidity",
            "description": "Kelly Criterion - LLM returns N/A",
        },
        {
            "name": "liquidation price",
            "domain": "liquidation",
            "description": "Liquidation Long - Should use LLM but uses NN",
        },
        {
            "name": "liquidation",
            "domain": "liquidation",
            "description": "Liquidation Short - Should use LLM but uses NN",
        },
        {
            "name": "impermanent loss percentage",
            "domain": "amm",
            "description": "IL Percentage - Should use specialized prompt",
        },
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{'#' * 80}")
        print(f"TEST CASE {i}/{len(test_cases)}: {test_case['description']}".center(80))
        print(f"{'#' * 80}")

        result = test_case_detailed(
            test_case["name"], test_case["domain"], hybrid, protocol, num_samples=100
        )

        if result:
            results.append(result)

        input("\nPress Enter to continue to next test case...")

    # Final summary
    print_section("FINAL SUMMARY OF ALL PROBLEMATIC CASES")

    print(f"\nResults:")
    print(f"  Total Cases Tested: {len(results)}")
    print(f"  Successful: {sum(1 for r in results if r['success'])}/{len(results)}")

    print(f"\n  Case Performance:")
    for i, result in enumerate(results, 1):
        print(f"\n  [{i}] {result['description'][:60]}")
        print(f"      Math Formula: {result['is_math_formula']}")
        print(f"      LLM R^2: {result['llm_r2']:.6f}")
        print(f"      NN R^2:  {result['nn_r2']:.6f}")
        print(f"      Winner: {'LLM' if result['llm_r2'] > result['nn_r2'] else 'NN'}")

        if result["llm_r2"] < 0.70:
            print(f"      [WARNING] LLM underperforming!")


def run_all_cases_quick():
    """Quick test of all cases without pausing"""

    print("=" * 80)
    print("QUICK TEST - ALL CASES".center(80))
    print("=" * 80)

    hybrid = HybridSystemDeFiFixed()
    protocol = DeFiExperimentProtocol()

    domains = protocol.get_all_domains()

    all_results = []

    for domain in domains:
        print(f"\n{'=' * 80}")
        print(f"DOMAIN: {domain.upper()}".center(80))
        print(f"{'=' * 80}")

        test_cases = protocol.load_test_data(domain, num_samples=100)

        for desc, X, y, var_names, meta in test_cases:
            print(f"\n[TEST] {desc[:70]}")

            # Quick LLM test
            llm_result = hybrid.generate_llm_formula(desc, domain, var_names, meta)

            if "error" in llm_result:
                print(f"  [ERROR] LLM failed: {llm_result['error']}")
                continue

            llm_metrics = hybrid.evaluate_llm_formula(
                llm_result, X, y, var_names, verbose=False
            )

            if not llm_metrics.get("success"):
                print(f"  [ERROR] Eval failed: {llm_metrics.get('error', 'Unknown')}")
                continue

            # Quick NN test
            _, nn_metrics, _, _ = hybrid.train_nn(X, y, epochs=100)

            llm_r2 = llm_metrics["r2"]
            nn_r2 = nn_metrics["r2"]

            print(
                f"  LLM R^2: {llm_r2:.4f} | NN R^2: {nn_r2:.4f} | Winner: {'LLM' if llm_r2 > nn_r2 else 'NN'}"
            )

            if llm_r2 < 0.80:
                print(f"  [WARNING] LLM underperforming!")

            all_results.append({"desc": desc, "llm_r2": llm_r2, "nn_r2": nn_r2})

    # Summary
    print(f"\n{'=' * 80}")
    print("QUICK TEST SUMMARY".center(80))
    print(f"{'=' * 80}")

    llm_wins = sum(1 for r in all_results if r["llm_r2"] > r["nn_r2"])
    nn_wins = sum(1 for r in all_results if r["nn_r2"] > r["llm_r2"])

    print(f"\nTotal Cases: {len(all_results)}")
    print(f"LLM Wins: {llm_wins} ({100 * llm_wins / len(all_results):.1f}%)")
    print(f"NN Wins: {nn_wins} ({100 * nn_wins / len(all_results):.1f}%)")

    avg_llm = np.mean([r["llm_r2"] for r in all_results])
    avg_nn = np.mean([r["nn_r2"] for r in all_results])

    print(f"\nAverage Performance:")
    print(f"  LLM: {avg_llm:.4f}")
    print(f"  NN:  {avg_nn:.4f}")

    # Cases needing attention
    problem_cases = [r for r in all_results if r["llm_r2"] < 0.80]
    if problem_cases:
        print(f"\n[WARNING] Cases with LLM R^2 < 0.80:")
        for r in problem_cases:
            print(f"  * {r['desc'][:70]}")
            print(f"    LLM: {r['llm_r2']:.4f}, NN: {r['nn_r2']:.4f}")


def test_specific_case(description_substring, domain):
    """
    Test a specific case by description substring

    Usage:
        test_specific_case("kelly", "liquidity")
    """
    hybrid = HybridSystemDeFiFixed()
    protocol = DeFiExperimentProtocol()

    return test_case_detailed(description_substring, domain, hybrid, protocol)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Individual Test Case Runner")
    parser.add_argument(
        "--mode",
        choices=["problematic", "quick", "specific"],
        default="problematic",
        help="Test mode",
    )
    parser.add_argument(
        "--case",
        type=str,
        default=None,
        help="Case description substring (for specific mode)",
    )
    parser.add_argument(
        "--domain", type=str, default=None, help="Domain (for specific mode)"
    )

    args = parser.parse_args()

    if args.mode == "problematic":
        run_problematic_cases()

    elif args.mode == "quick":
        run_all_cases_quick()

    elif args.mode == "specific":
        if not args.case or not args.domain:
            print("Error: --case and --domain required for specific mode")
            print("Example: --mode specific --case 'kelly' --domain 'liquidity'")
            exit(1)

        test_specific_case(args.case, args.domain)

    else:
        print("Invalid mode")

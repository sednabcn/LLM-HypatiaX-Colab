"""
Diagnostic tool to inspect generated formulas and identify issues
"""

import json
import sys


def diagnose_results(results_file):
    """
    Analyze results file to identify formula generation issues
    """
    with open(results_file, "r") as f:
        results = json.load(f)

    print("=" * 80)
    print("FORMULA DIAGNOSTIC REPORT".center(80))
    print("=" * 80)

    for i, result in enumerate(results, 1):
        description = result.get("description", "Unknown")
        domain = result.get("domain", "Unknown")

        print(f"\n[{i}/{len(results)}] {description}")
        print(f"Domain: {domain}")
        print("-" * 80)

        # Formula information
        formula = result.get("formula", "N/A")
        latex = result.get("latex", "N/A")
        python_code = result.get("python_code", "N/A")

        print(f"\n📐 FORMULA: {formula}")
        print(f"\n📊 LATEX: {latex}")
        print(f"\n🐍 PYTHON CODE:")
        print(python_code)

        # Evaluation metrics
        evaluation = result.get("evaluation", {})
        if evaluation.get("success"):
            r2 = evaluation.get("r2", "N/A")
            rmse = evaluation.get("rmse", "N/A")
            mae = evaluation.get("mae", "N/A")

            print(f"\n✅ EVALUATION:")
            print(f"   R² Score: {r2}")
            print(f"   RMSE: {rmse}")
            print(f"   MAE: {mae}")

            # Identify issues
            if isinstance(r2, (int, float)):
                if r2 < 0:
                    print(f"\n❌ ISSUE: Negative R² score ({r2:.2e})")
                    print(
                        "   This indicates the model is worse than a horizontal line!"
                    )
                    print("   Possible causes:")
                    print("     - Wrong constants in formula")
                    print("     - Wrong functional form")
                    print("     - Constants treated as parameters")
                elif r2 < 0.5:
                    print(f"\n⚠️  WARNING: Low R² score ({r2:.4f})")
                    print("   Model is not fitting well")
                elif r2 > 0.99:
                    print(f"\n✨ EXCELLENT: Very high R² score ({r2:.4f})")
        else:
            error = evaluation.get("error", "Unknown error")
            print(f"\n❌ EVALUATION FAILED: {error}")

            # Debug info if available
            if "debug_code" in evaluation:
                print(f"\n🔍 DEBUG CODE:\n{evaluation['debug_code']}")
            if "debug_vars" in evaluation:
                print(f"\n🔍 VARIABLES FOUND: {evaluation['debug_vars']}")
            if "debug_signature" in evaluation:
                print(f"\n🔍 FUNCTION SIGNATURE: {evaluation['debug_signature']}")

        print("\n" + "=" * 80)

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS".center(80))
    print("=" * 80)

    successful = sum(1 for r in results if r.get("evaluation", {}).get("success"))
    total = len(results)

    print(f"\nTotal cases: {total}")
    print(f"Successful: {successful}/{total} ({100 * successful / total:.1f}%)")

    # R² statistics
    r2_scores = []
    for r in results:
        eval_dict = r.get("evaluation", {})
        if eval_dict.get("success") and "r2" in eval_dict:
            r2_scores.append(eval_dict["r2"])

    if r2_scores:
        import numpy as np

        print(f"\nR² Score Statistics:")
        print(f"   Mean:   {np.mean(r2_scores):.4e}")
        print(f"   Median: {np.median(r2_scores):.4e}")
        print(f"   Min:    {np.min(r2_scores):.4e}")
        print(f"   Max:    {np.max(r2_scores):.4e}")

        # Identify problem cases
        negative_r2 = [r for r in results if r.get("evaluation", {}).get("r2", 0) < 0]
        if negative_r2:
            print(f"\n❌ Cases with negative R²: {len(negative_r2)}")
            for r in negative_r2:
                print(
                    f"   - {r.get('description', 'Unknown')}: R²={r['evaluation']['r2']:.2e}"
                )

        good_r2 = [r for r in results if r.get("evaluation", {}).get("r2", 0) > 0.9]
        if good_r2:
            print(f"\n✅ Cases with R² > 0.9: {len(good_r2)}")
            for r in good_r2:
                print(
                    f"   - {r.get('description', 'Unknown')}: R²={r['evaluation']['r2']:.4f}"
                )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python formula_diagnostic.py <results_file.json>")
        print("\nExample:")
        print(
            "  python formula_diagnostic.py hypatiax/data/results/baseline_pure_llm_20251220_133110.json"
        )
        sys.exit(1)

    results_file = sys.argv[1]
    diagnose_results(results_file)

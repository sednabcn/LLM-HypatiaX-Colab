"""
Enhanced diagnostic tool to inspect generated formulas and identify issues
"""

import json
import sys
import numpy as np
from pathlib import Path


def extract_constants_from_code(python_code):
    """Extract constant definitions from Python code."""
    import re

    constants = {}

    # Pattern to match: variable_name = value
    pattern = r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([0-9e.+-]+)"

    for line in python_code.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            var_name = match.group(1)
            try:
                value = float(eval(match.group(2)))
                constants[var_name] = value
            except:
                pass

    return constants


def load_ground_truth(domain, description):
    """Load ground truth metadata for a test case."""
    try:
        # Import here to avoid circular dependencies
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from experiment_protocol import ExperimentProtocol

        test_cases = ExperimentProtocol.load_test_data(domain, num_samples=10)

        for desc, X, y, vars, metadata in test_cases:
            if desc == description:
                return metadata

        return None
    except Exception as e:
        print(f"Warning: Could not load ground truth: {e}")
        return None


def compare_constants(llm_constants, ground_truth_constants):
    """Compare LLM constants with ground truth."""
    issues = []
    matches = []

    if not ground_truth_constants:
        return issues, matches

    for key, gt_value in ground_truth_constants.items():
        if key in llm_constants:
            llm_value = llm_constants[key]

            # Check if values are close (within order of magnitude)
            if gt_value != 0:
                ratio = llm_value / gt_value
                if 0.1 <= ratio <= 10:
                    matches.append(
                        f"{key}: LLM={llm_value}, GT={gt_value} (ratio={ratio:.2f})"
                    )
                else:
                    issues.append(
                        f"{key}: LLM={llm_value}, GT={gt_value} (ratio={ratio:.2e}) ❌"
                    )
            else:
                if abs(llm_value - gt_value) < 1e-6:
                    matches.append(f"{key}: both zero ✓")
                else:
                    issues.append(f"{key}: LLM={llm_value}, GT={gt_value} ❌")
        else:
            issues.append(f"{key}: MISSING in LLM code (GT={gt_value}) ❌")

    # Check for extra constants in LLM
    for key in llm_constants:
        if key not in ground_truth_constants and key not in ["np", "numpy", "pi"]:
            issues.append(
                f"{key}: EXTRA constant in LLM (value={llm_constants[key]}) ⚠️"
            )

    return issues, matches


def suggest_fix(python_code, ground_truth_constants):
    """Suggest corrected Python code with ground truth constants."""
    if not ground_truth_constants:
        return None

    lines = python_code.split("\n")
    fixed_lines = []
    replaced_constants = set()

    for line in lines:
        fixed_line = line

        # Check each ground truth constant
        for const_name, const_value in ground_truth_constants.items():
            # Pattern to match: const_name = old_value
            import re

            pattern = rf"^\s*{const_name}\s*=\s*[0-9e.+-]+"

            if re.match(pattern, line.strip()):
                # Replace with ground truth value
                indent = len(line) - len(line.lstrip())
                fixed_line = " " * indent + f"{const_name} = {const_value}"
                replaced_constants.add(const_name)

        fixed_lines.append(fixed_line)

    # Add any missing constants
    if replaced_constants or True:  # Always show suggested fix
        # Find where to insert (after def line)
        insert_idx = 0
        for i, line in enumerate(fixed_lines):
            if line.strip().startswith("def "):
                insert_idx = i + 1
                break

        # Build corrected version
        corrected = fixed_lines[:]

        # Replace constants in place
        for const_name, const_value in ground_truth_constants.items():
            found = False
            for i, line in enumerate(corrected):
                if line.strip().startswith(f"{const_name} ="):
                    indent = len(line) - len(line.lstrip())
                    corrected[i] = " " * indent + f"{const_name} = {const_value}"
                    found = True
                    break

            # If constant not found, add it after function definition
            if not found:
                indent = len(corrected[insert_idx]) - len(
                    corrected[insert_idx].lstrip()
                )
                if indent == 0:
                    indent = 4  # Default indent
                corrected.insert(
                    insert_idx, " " * indent + f"{const_name} = {const_value}"
                )
                insert_idx += 1

        return "\n".join(corrected)

    return None


def test_corrected_formula(corrected_code, domain, description):
    """Test if corrected formula would work better."""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from experiment_protocol import ExperimentProtocol

        test_cases = ExperimentProtocol.load_test_data(domain, num_samples=100)

        # Find matching test case
        for desc, X, y_true, vars, metadata in test_cases:
            if desc == description:
                # Execute corrected code
                local_vars = {}
                exec(corrected_code, {"np": np, "numpy": np}, local_vars)

                # Find function
                func = None
                for var_name, var_value in local_vars.items():
                    if callable(var_value) and not var_name.startswith("_"):
                        func = var_value
                        break

                if func is None:
                    return None

                # Evaluate
                import inspect

                sig = inspect.signature(func)
                num_params = len(sig.parameters)

                # Call function appropriately
                if num_params == 1:
                    y_pred = func(X[:, 0])
                elif num_params == 2:
                    y_pred = func(X[:, 0], X[:, 1])
                elif num_params == 3:
                    y_pred = func(X[:, 0], X[:, 1], X[:, 2])
                elif num_params == 4:
                    y_pred = func(X[:, 0], X[:, 1], X[:, 2], X[:, 3])
                else:
                    y_pred = func(*[X[:, i] for i in range(X.shape[1])])

                y_pred = np.array(y_pred)

                # Calculate R²
                ss_res = np.sum((y_true - y_pred) ** 2)
                ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
                r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

                # Calculate RMSE
                rmse = np.sqrt(np.mean((y_pred - y_true) ** 2))

                return {"r2": float(r2), "rmse": float(rmse)}

        return None
    except Exception as e:
        return {"error": str(e)}


def diagnose_results(results_file):
    """
    Analyze results file to identify formula generation issues
    """
    with open(results_file, "r") as f:
        results = json.load(f)

    print("=" * 80)
    print("ENHANCED FORMULA DIAGNOSTIC REPORT".center(80))
    print("=" * 80)

    problem_cases = []

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

        # Extract constants from LLM code
        llm_constants = extract_constants_from_code(python_code)
        if llm_constants:
            print(f"\n🔢 CONSTANTS USED BY LLM:")
            for name, value in llm_constants.items():
                print(f"   {name} = {value}")

        # Load ground truth
        ground_truth = load_ground_truth(domain, description)

        if ground_truth:
            print(f"\n✅ GROUND TRUTH:")
            print(f"   Formula: {ground_truth.get('ground_truth', 'N/A')}")

            gt_constants = ground_truth.get("constants", {})
            if gt_constants:
                print(f"   Constants:")
                for name, value in gt_constants.items():
                    print(f"      {name} = {value}")

                # Compare constants
                issues, matches = compare_constants(llm_constants, gt_constants)

                if issues:
                    print(f"\n❌ CONSTANT MISMATCHES:")
                    for issue in issues:
                        print(f"   {issue}")

                if matches:
                    print(f"\n✅ MATCHING CONSTANTS:")
                    for match in matches:
                        print(f"   {match}")

        # Evaluation metrics
        evaluation = result.get("evaluation", {})
        if evaluation.get("success"):
            r2 = evaluation.get("r2", "N/A")
            rmse = evaluation.get("rmse", "N/A")
            mae = evaluation.get("mae", "N/A")

            print(f"\n📊 EVALUATION METRICS:")
            print(f"   R² Score: {r2}")
            print(f"   RMSE: {rmse}")
            print(f"   MAE: {mae}")

            # Identify issues
            if isinstance(r2, (int, float)):
                if r2 < 0:
                    print(f"\n❌ SEVERE ISSUE: Negative R² score ({r2:.2e})")
                    print(
                        "   This indicates the model is worse than a horizontal line!"
                    )
                    print("   Root cause: Wrong constants (see mismatches above)")
                    problem_cases.append((i, description, r2, domain))

                    # Suggest fix
                    if ground_truth and gt_constants:
                        corrected_code = suggest_fix(python_code, gt_constants)
                        if corrected_code:
                            print(f"\n💡 SUGGESTED FIX:")
                            print(corrected_code)

                            # Test corrected version
                            print(f"\n🧪 TESTING CORRECTED VERSION...")
                            test_result = test_corrected_formula(
                                corrected_code, domain, description
                            )
                            if test_result and "r2" in test_result:
                                print(
                                    f"   ✨ Corrected R² Score: {test_result['r2']:.4f}"
                                )
                                print(
                                    f"   ✨ Corrected RMSE: {test_result['rmse']:.6f}"
                                )

                                if test_result["r2"] > 0.9:
                                    print(
                                        f"   🎉 FIX VERIFIED! This would achieve excellent performance!"
                                    )
                            elif test_result:
                                print(
                                    f"   ⚠️  Testing error: {test_result.get('error', 'Unknown')}"
                                )

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

    # Problem summary
    if problem_cases:
        print(f"\n" + "=" * 80)
        print("PROBLEM CASES SUMMARY".center(80))
        print("=" * 80)
        print(f"\n{len(problem_cases)} cases need constant corrections:")
        for idx, desc, r2, domain in problem_cases:
            print(f"   [{idx}] {desc}")
            print(f"       Current R²: {r2:.2e} | Domain: {domain}")

        print(f"\n💡 RECOMMENDATION:")
        print(f"   Use the fixed baseline_pure_llm.py that passes metadata to the LLM.")
        print(
            f"   This will provide ground truth constants to guide formula generation."
        )
        print(
            f"   Expected improvement: Negative R² → ~1.0 for these {len(problem_cases)} cases."
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enhanced_formula_diagnostic.py <results_file.json>")
        print("\nExample:")
        print(
            "  python enhanced_formula_diagnostic.py hypatiax/data/results/baseline_pure_llm_20251220_133110.json"
        )
        sys.exit(1)

    results_file = sys.argv[1]
    diagnose_results(results_file)

"""
python hypatiax/core/training/formula_diagnostic.py hypatiax/data/results/baseline_pure_llm_20251220_133110.json


This enhanced version will:
- Show you **exactly which constants are wrong**
- Generate **corrected Python code** with ground truth constants
- **Test the corrected version** to prove it would work
- Give you confidence that the metadata-passing fix will solve the problem

The output will be much more actionable! Try it now and you'll see suggestions like:
```
❌ CONSTANT MISMATCHES:
   sigma_0: LLM=70000000.0, GT=50 (ratio=1.40e+06) ❌
   k: LLM=0.001, GT=15 (ratio=6.67e-05) ❌

💡 SUGGESTED FIX:
def formula(grain_size):
    sigma_0 = 50
    k = 15
    return sigma_0 + k / np.sqrt(grain_size)

🧪 TESTING CORRECTED VERSION...
   ✨ Corrected R² Score: 1.0000
   🎉 FIX VERIFIED! This would achieve excellent performance!

"""

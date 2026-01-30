"""
Parse baseline .txt output files and convert to JSON format
"""

import re
import json
from pathlib import Path
from datetime import datetime


def parse_test_case(text, domain):
    """Parse a single test case from text."""
    result = {
        "method": None,
        "model": None,
        "description": None,
        "domain": domain,
        "formula": None,
        "evaluation": {},
        "metadata": {},
        "timestamp": datetime.now().isoformat(),
    }

    # Extract description
    desc_match = re.search(
        r"\[(\d+)/(\d+)\]\s+(.+?)(?:\n|Variables:|Ground truth:)", text, re.DOTALL
    )
    if desc_match:
        result["description"] = desc_match.group(3).strip()

    # Extract variables
    var_match = re.search(r"Variables:\s+(.+?)(?:\n|Ground truth:)", text)
    if var_match:
        result["metadata"]["variables"] = var_match.group(1).strip()

    # Extract ground truth
    gt_match = re.search(r"Ground truth:\s+(.+?)(?:\n|Difficulty:)", text)
    if gt_match:
        result["metadata"]["ground_truth"] = gt_match.group(1).strip()

    # Extract difficulty
    diff_match = re.search(r"Difficulty:\s+(\w+)", text)
    if diff_match:
        result["metadata"]["difficulty"] = diff_match.group(1).strip()

    # Extract formula
    formula_match = re.search(r"Formula:\s+(.+?)(?:\n|✓|✅)", text, re.DOTALL)
    if formula_match:
        result["formula"] = formula_match.group(1).strip()

    # Extract R² score
    r2_patterns = [
        r"R²\s+Score:\s+([-\d.]+)",
        r"RÂ²\s+Score:\s+([-\d.]+)",
        r"R2\s+Score:\s+([-\d.]+)",
    ]
    for pattern in r2_patterns:
        r2_match = re.search(pattern, text)
        if r2_match:
            try:
                result["evaluation"]["r2"] = float(r2_match.group(1))
            except ValueError:
                result["evaluation"]["r2"] = None
            break

    # Extract RMSE
    rmse_match = re.search(r"RMSE:\s+([\d.]+)", text)
    if rmse_match:
        try:
            result["evaluation"]["rmse"] = float(rmse_match.group(1))
        except ValueError:
            result["evaluation"]["rmse"] = None

    # Extract MAE
    mae_match = re.search(r"MAE:\s+([\d.]+)", text)
    if mae_match:
        try:
            result["evaluation"]["mae"] = float(mae_match.group(1))
        except ValueError:
            result["evaluation"]["mae"] = None

    # Check for extrapolation test
    if "EXTRAPOLATION TEST" in text:
        result["metadata"]["extrapolation_test"] = True

    # Extract formula type from difficulty
    if result["metadata"].get("difficulty"):
        result["metadata"]["formula_type"] = result["metadata"]["difficulty"]

    return result


def parse_llm_txt(txt_file):
    """Parse LLM baseline text file."""
    with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    results = []
    current_domain = None

    # Find all domain sections
    domain_pattern = r"Domain:\s+([A-Z_]+)"
    domain_matches = list(re.finditer(domain_pattern, content))

    for i, match in enumerate(domain_matches):
        domain = match.group(1).lower()
        start_pos = match.end()

        # Find end of this domain section
        if i + 1 < len(domain_matches):
            end_pos = domain_matches[i + 1].start()
        else:
            end_pos = len(content)

        domain_section = content[start_pos:end_pos]

        # Split by test case number pattern
        test_cases = re.split(r"\n\[(\d+)/(\d+)\]", domain_section)

        # Process test cases (skip first element which is before first test)
        for j in range(1, len(test_cases), 3):
            if j + 2 < len(test_cases):
                test_num = test_cases[j]
                total_tests = test_cases[j + 1]
                test_content = f"[{test_num}/{total_tests}]" + test_cases[j + 2]

                test_result = parse_test_case(test_content, domain)
                test_result["method"] = "pure_llm"
                test_result["model"] = "claude-sonnet-4-20250514"

                if test_result["description"]:
                    results.append(test_result)

    return results


def parse_nn_txt(txt_file):
    """Parse NN baseline text file."""
    with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    results = []
    current_domain = None

    # Find all domain sections
    domain_pattern = r"Domain:\s+([A-Z_]+)"
    domain_matches = list(re.finditer(domain_pattern, content))

    for i, match in enumerate(domain_matches):
        domain = match.group(1).lower()
        start_pos = match.end()

        # Find end of this domain section
        if i + 1 < len(domain_matches):
            end_pos = domain_matches[i + 1].start()
        else:
            end_pos = len(content)

        domain_section = content[start_pos:end_pos]

        # Split by test case number pattern
        test_cases = re.split(r"\n\[(\d+)/(\d+)\]", domain_section)

        # Process test cases
        for j in range(1, len(test_cases), 3):
            if j + 2 < len(test_cases):
                test_num = test_cases[j]
                total_tests = test_cases[j + 1]
                test_content = f"[{test_num}/{total_tests}]" + test_cases[j + 2]

                test_result = parse_test_case(test_content, domain)
                test_result["method"] = "neural_network"
                test_result["model"] = "3-layer MLP"

                if test_result["description"]:
                    results.append(test_result)

    return results


def main():
    print("=" * 80)
    print("PARSING TEXT FILES TO JSON FORMAT")
    print("=" * 80)

    results_dir = Path("results")

    # Define which files to parse
    file_mapping = {
        "llm": {
            "defi": "baseline_neural_pure_llm_20251220_1951.txt",
            "physics": "baseline_pure_llm_202512_152604.txt",
        },
        "nn": {
            "defi": "baseline_neural_network_2251221_1033.txt",
            "physics": "baseline_neural_network_all.txt",
        },
    }

    # Parse LLM files
    print("\n🔵 Parsing LLM files...")
    all_llm = []

    for domain_type, filename in file_mapping["llm"].items():
        filepath = results_dir / filename
        if filepath.exists():
            print(f"  📄 {filename}")
            try:
                data = parse_llm_txt(filepath)
                all_llm.extend(data)
                domains = set(item.get("domain", "unknown") for item in data)
                print(f"     ✅ Extracted {len(data)} test cases")
                print(f"     Domains: {sorted(domains)}")
            except Exception as e:
                print(f"     ❌ Error: {e}")
        else:
            print(f"  ⚠️  Not found: {filename}")

    # Parse NN files
    print("\n🔴 Parsing NN files...")
    all_nn = []

    for domain_type, filename in file_mapping["nn"].items():
        filepath = results_dir / filename
        if filepath.exists():
            print(f"  📄 {filename}")
            try:
                data = parse_nn_txt(filepath)
                all_nn.extend(data)
                domains = set(item.get("domain", "unknown") for item in data)
                print(f"     ✅ Extracted {len(data)} test cases")
                print(f"     Domains: {sorted(domains)}")
            except Exception as e:
                print(f"     ❌ Error: {e}")
        else:
            print(f"  ⚠️  Not found: {filename}")

    # Save JSON files
    if all_llm:
        output_llm = results_dir / "baseline_llm_PARSED.json"
        with open(output_llm, "w") as f:
            json.dump(all_llm, f, indent=2)
        print(f"\n✅ Saved LLM: {output_llm} ({len(all_llm)} cases)")

    if all_nn:
        output_nn = results_dir / "baseline_nn_PARSED.json"
        with open(output_nn, "w") as f:
            json.dump(all_nn, f, indent=2)
        print(f"✅ Saved NN: {output_nn} ({len(all_nn)} cases)")

    if all_llm and all_nn:
        # Summary
        llm_domains = set(item["domain"] for item in all_llm)
        nn_domains = set(item["domain"] for item in all_nn)
        common = llm_domains & nn_domains

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"\n📊 Total parsed:")
        print(f"   LLM: {len(all_llm)} test cases across {len(llm_domains)} domains")
        print(f"   NN:  {len(all_nn)} test cases across {len(nn_domains)} domains")
        print(f"\n✅ Common domains: {sorted(common)}")

        print("\n" + "=" * 80)
        print("READY FOR COMPARISON")
        print("=" * 80)
        print("\nRun comparison with:")
        print(
            "  python results/comparison_analysis_improved.py results/baseline_llm_PARSED.json results/baseline_nn_PARSED.json"
        )


if __name__ == "__main__":
    main()

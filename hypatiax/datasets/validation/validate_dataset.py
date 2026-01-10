import glob
import json
import os
from collections import defaultdict
from typing import Any, Dict, List

import numpy as np


def load_dataset_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Load and validate JSON dataset file.

    Args:
        filepath: Path to JSON file

    Returns:
        List of formula results
    """
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"Warning: {filepath} does not contain a list")
                return []
            return data
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse {filepath}: {e}")
        return []
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return []


def analyze_validation_scores(result: Dict[str, Any]) -> Dict[str, float]:
    """
    Extract detailed validation scores from a result.

    Args:
        result: Single formula result dictionary

    Returns:
        Dictionary of score components
    """
    validation = result.get("validation", {})

    return {
        "total_score": validation.get("total_score", 0),
        "r2_score": validation.get("r2_score", 0),
        "symbolic_score": validation.get("symbolic_score", 0),
        "physical_score": validation.get("physical_score", 0),
        "complexity": validation.get("complexity", 0),
        "valid": validation.get("valid", False),
    }


def get_domain_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics grouped by domain.

    Args:
        results: List of all formula results

    Returns:
        Dictionary of domain-level statistics
    """
    domain_stats = defaultdict(
        lambda: {"count": 0, "valid": 0, "scores": [], "r2_scores": [], "formulas": []}
    )

    for result in results:
        domain = result.get("domain", "unknown")
        scores = analyze_validation_scores(result)

        domain_stats[domain]["count"] += 1
        if scores["valid"]:
            domain_stats[domain]["valid"] += 1
            domain_stats[domain]["scores"].append(scores["total_score"])
            domain_stats[domain]["r2_scores"].append(scores["r2_score"])

        # Store formula info
        formula_info = {
            "description": result.get("description", "N/A"),
            "equation": result.get("discovered_equation", "N/A"),
            "score": scores["total_score"],
            "valid": scores["valid"],
        }
        domain_stats[domain]["formulas"].append(formula_info)

    return dict(domain_stats)


def print_detailed_report(
    domain_stats: Dict[str, Any], total_formulas: int, valid_formulas: int
):
    """
    Print comprehensive validation report.

    Args:
        domain_stats: Statistics by domain
        total_formulas: Total number of formulas
        valid_formulas: Number of valid formulas
    """
    print(f"\n{'=' * 70}")
    print(f"{'DATASET VALIDATION REPORT':^70}")
    print(f"{'=' * 70}\n")

    # Overall Statistics
    print(f"{'OVERALL STATISTICS':^70}")
    print(f"{'-' * 70}")
    print(f"  Total formulas:        {total_formulas:>6}")
    print(f"  Valid formulas:        {valid_formulas:>6}")
    print(f"  Invalid formulas:      {total_formulas - valid_formulas:>6}")
    print(f"  Success rate:          {valid_formulas / total_formulas * 100:>5.1f}%")

    # Collect all scores for overall stats
    all_scores = []
    all_r2_scores = []
    for stats in domain_stats.values():
        all_scores.extend(stats["scores"])
        all_r2_scores.extend(stats["r2_scores"])

    if all_scores:
        print(f"\n  Score Statistics (valid formulas only):")
        print(f"    Average score:       {np.mean(all_scores):>5.1f}/100")
        print(f"    Median score:        {np.median(all_scores):>5.1f}/100")
        print(f"    Min score:           {np.min(all_scores):>5.1f}/100")
        print(f"    Max score:           {np.max(all_scores):>5.1f}/100")
        print(f"    Std deviation:       {np.std(all_scores):>5.1f}")

    if all_r2_scores:
        print(f"\n  R² Statistics:")
        print(f"    Average R²:          {np.mean(all_r2_scores):>5.3f}")
        print(f"    Median R²:           {np.median(all_r2_scores):>5.3f}")
        print(f"    Min R²:              {np.min(all_r2_scores):>5.3f}")
        print(f"    Max R²:              {np.max(all_r2_scores):>5.3f}")

    # Domain-by-Domain Breakdown
    print(f"\n{'=' * 70}")
    print(f"{'DOMAIN BREAKDOWN':^70}")
    print(f"{'=' * 70}\n")

    for domain, stats in sorted(domain_stats.items()):
        print(f"Domain: {domain.upper()}")
        print(f"{'-' * 70}")
        print(f"  Total:           {stats['count']:>4}")
        print(
            f"  Valid:           {stats['valid']:>4}/{stats['count']} "
            f"({stats['valid'] / stats['count'] * 100:.1f}%)"
        )

        if stats["scores"]:
            print(f"  Avg score:       {np.mean(stats['scores']):>5.1f}/100")
            print(f"  Avg R²:          {np.mean(stats['r2_scores']):>5.3f}")
        else:
            print(f"  Avg score:       N/A (no valid formulas)")

        # Top formulas in this domain
        valid_formulas_in_domain = [f for f in stats["formulas"] if f["valid"]]
        if valid_formulas_in_domain:
            top_formulas = sorted(
                valid_formulas_in_domain, key=lambda x: x["score"], reverse=True
            )[:3]
            print(f"\n  Top formulas:")
            for i, formula in enumerate(top_formulas, 1):
                desc = (
                    formula["description"][:50] + "..."
                    if len(formula["description"]) > 50
                    else formula["description"]
                )
                print(f"    {i}. {desc}")
                print(f"       Score: {formula['score']:.1f}/100")
                eq = (
                    formula["equation"][:60] + "..."
                    if len(formula["equation"]) > 60
                    else formula["equation"]
                )
                print(f"       Equation: {eq}")

        print()

    # Score Distribution
    print(f"{'=' * 70}")
    print(f"{'SCORE DISTRIBUTION':^70}")
    print(f"{'=' * 70}\n")

    if all_scores:
        bins = [0, 50, 70, 85, 95, 100]
        labels = [
            "Poor (0-50)",
            "Fair (50-70)",
            "Good (70-85)",
            "Very Good (85-95)",
            "Excellent (95-100)",
        ]

        for i in range(len(bins) - 1):
            count = sum(1 for s in all_scores if bins[i] <= s < bins[i + 1])
            if i == len(bins) - 2:  # Last bin includes 100
                count = sum(1 for s in all_scores if bins[i] <= s <= bins[i + 1])
            pct = count / len(all_scores) * 100 if all_scores else 0
            bar = "█" * int(pct / 2)
            print(f"  {labels[i]:20} {count:>4} ({pct:>5.1f}%) {bar}")

    print(f"\n{'=' * 70}\n")


def identify_issues(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify problematic formulas and potential issues.

    Args:
        results: List of all formula results

    Returns:
        List of issues found
    """
    issues = []

    for i, result in enumerate(results):
        validation = result.get("validation", {})

        # Check for invalid formulas
        if not validation.get("valid", False):
            issues.append(
                {
                    "type": "INVALID_FORMULA",
                    "index": i,
                    "description": result.get("description", "N/A"),
                    "reason": "Failed validation checks",
                }
            )

        # Check for low R² scores
        r2 = validation.get("r2_score", 0)
        if validation.get("valid") and r2 < 0.8:
            issues.append(
                {
                    "type": "LOW_R2",
                    "index": i,
                    "description": result.get("description", "N/A"),
                    "r2_score": r2,
                    "reason": f"R² score {r2:.3f} below 0.8 threshold",
                }
            )

        # Check for missing data
        if not result.get("discovered_equation"):
            issues.append(
                {
                    "type": "MISSING_EQUATION",
                    "index": i,
                    "description": result.get("description", "N/A"),
                    "reason": "No discovered equation found",
                }
            )

    return issues


def print_issues_report(issues: List[Dict[str, Any]]):
    """
    Print report of identified issues.

    Args:
        issues: List of issues
    """
    if not issues:
        print(f"{'✓ NO ISSUES FOUND':^70}")
        return

    print(f"{'=' * 70}")
    print(f"{'ISSUES DETECTED':^70}")
    print(f"{'=' * 70}\n")

    issue_counts = defaultdict(int)
    for issue in issues:
        issue_counts[issue["type"]] += 1

    print(f"Issue Summary:")
    for issue_type, count in sorted(issue_counts.items()):
        print(f"  {issue_type:20} {count:>4} occurrences")

    print(f"\nDetailed Issues:\n")
    for i, issue in enumerate(issues[:10], 1):  # Show first 10
        print(f"  {i}. {issue['type']}")
        print(f"     Description: {issue['description'][:60]}")
        print(f"     Reason: {issue['reason']}")
        if "r2_score" in issue:
            print(f"     R² Score: {issue['r2_score']:.3f}")
        print()

    if len(issues) > 10:
        print(f"  ... and {len(issues) - 10} more issues\n")


def export_report(
    stats: Dict[str, Any], output_file: str = "data/validation_report.json"
):
    """
    Export validation statistics to JSON file.

    Args:
        stats: Statistics dictionary
        output_file: Output file path
    """
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(stats, f, indent=2)
        print(f"Report exported to: {output_file}")
    except Exception as e:
        print(f"Error exporting report: {e}")


def validate_dataset(
    data_dir: str = "data",
    pattern: str = "*.json",
    export: bool = True,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Validate all dataset files and generate comprehensive report.

    Args:
        data_dir: Directory containing dataset files
        pattern: File pattern to match
        export: Whether to export report to JSON
        verbose: Whether to print detailed output

    Returns:
        Dictionary containing validation statistics
    """
    # Find all dataset files
    search_pattern = os.path.join(data_dir, pattern)
    all_files = glob.glob(search_pattern)

    if not all_files:
        print(f"Error: No files found matching {search_pattern}")
        print(f"\nTroubleshooting:")
        print(f"  1. Check if directory exists: {data_dir}")
        print(f"  2. Check if there are any JSON files in the directory")
        print(f"  3. Try using absolute path instead of relative path")
        print(f"  4. Current working directory: {os.getcwd()}")
        return {
            "success_rate": 0.0,
            "total_formulas": 0,
            "valid_formulas": 0,
            "error": "No files found",
        }

    if verbose:
        print(f"\nFound {len(all_files)} dataset file(s):")
        for filepath in all_files:
            print(f"  - {filepath}")

    # Load all results
    all_results = []
    file_info = {}

    for filepath in all_files:
        results = load_dataset_file(filepath)
        all_results.extend(results)
        file_info[filepath] = len(results)

    if not all_results:
        print("Error: No valid results found in dataset files")
        return {
            "success_rate": 0.0,
            "total_formulas": 0,
            "valid_formulas": 0,
            "error": "No valid results",
        }

    # Calculate statistics
    total_formulas = len(all_results)
    valid_formulas = sum(
        1 for r in all_results if r.get("validation", {}).get("valid", False)
    )

    domain_stats = get_domain_statistics(all_results)
    issues = identify_issues(all_results)

    # Print reports
    if verbose:
        print_detailed_report(domain_stats, total_formulas, valid_formulas)
        print_issues_report(issues)

    # Compile summary statistics
    all_scores = []
    for stats in domain_stats.values():
        all_scores.extend(stats["scores"])

    summary = {
        "total_formulas": total_formulas,
        "valid_formulas": valid_formulas,
        "success_rate": valid_formulas / total_formulas if total_formulas > 0 else 0,
        "avg_score": float(np.mean(all_scores)) if all_scores else 0,
        "median_score": float(np.median(all_scores)) if all_scores else 0,
        "min_score": float(np.min(all_scores)) if all_scores else 0,
        "max_score": float(np.max(all_scores)) if all_scores else 0,
        "domains": {
            domain: {
                "count": stats["count"],
                "valid": stats["valid"],
                "success_rate": (
                    stats["valid"] / stats["count"] if stats["count"] > 0 else 0
                ),
                "avg_score": float(np.mean(stats["scores"])) if stats["scores"] else 0,
            }
            for domain, stats in domain_stats.items()
        },
        "files": file_info,
        "issues_count": len(issues),
        "issue_types": dict(
            defaultdict(
                int,
                {
                    issue["type"]: sum(1 for i in issues if i["type"] == issue["type"])
                    for issue in issues
                },
            )
        ),
    }

    # Export if requested
    if export:
        export_report(summary)

    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate formula discovery datasets")
    parser.add_argument("--dir", default="data", help="Data directory")
    parser.add_argument("--pattern", default="*.json", help="File pattern")
    parser.add_argument("--no-export", action="store_true", help="Skip JSON export")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")

    args = parser.parse_args()

    stats = validate_dataset(
        data_dir=args.dir,
        pattern=args.pattern,
        export=not args.no_export,
        verbose=not args.quiet,
    )

    # Check if we got valid stats
    if "error" in stats:
        print(f"\n✗ Validation failed: {stats['error']}")
        exit(2)

    # Exit with error code if success rate is below threshold
    success_rate = stats.get("success_rate", 0)

    if success_rate < 0.8:
        print(
            f"\n⚠ Warning: Success rate {success_rate * 100:.1f}% is below 80% threshold"
        )
        exit(1)
    else:
        print(f"\n✓ Success rate {success_rate * 100:.1f}% meets quality threshold")
        exit(0)

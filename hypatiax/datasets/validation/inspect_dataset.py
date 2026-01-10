#!/usr/bin/env python3
"""
Dataset Inspector & Fixer
Diagnoses and fixes common dataset structure issues
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List


def inspect_json_file(filepath: str) -> Dict[str, Any]:
    """Inspect a single JSON file and report its structure"""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)

        report = {
            "filepath": filepath,
            "valid": True,
            "type": type(data).__name__,
            "issues": [],
            "structure": {},
        }

        # Check if it's a list
        if not isinstance(data, list):
            report["issues"].append(f"⚠️ Not a list (got {type(data).__name__})")
            if isinstance(data, dict):
                report["structure"]["keys"] = list(data.keys())
                report["structure"]["sample"] = {
                    k: type(v).__name__ for k, v in list(data.items())[:5]
                }
            return report

        # Check list length
        report["structure"]["count"] = len(data)

        if len(data) == 0:
            report["issues"].append("⚠️ Empty list")
            return report

        # Inspect first item
        first_item = data[0]
        if not isinstance(first_item, dict):
            report["issues"].append(
                f"⚠️ Items are not dicts (got {type(first_item).__name__})"
            )
            return report

        report["structure"]["keys"] = list(first_item.keys())

        # Check for required fields
        required_fields = ["description", "discovered_equation", "validation", "domain"]
        missing_fields = [f for f in required_fields if f not in first_item]

        if missing_fields:
            report["issues"].append(f"❌ Missing fields: {', '.join(missing_fields)}")

        # Check validation structure
        if "validation" in first_item:
            val = first_item["validation"]
            if isinstance(val, dict):
                report["structure"]["validation_keys"] = list(val.keys())

                val_required = ["total_score", "valid", "r2_score"]
                val_missing = [f for f in val_required if f not in val]
                if val_missing:
                    report["issues"].append(
                        f"❌ Validation missing: {', '.join(val_missing)}"
                    )
            else:
                report["issues"].append(
                    f"❌ Validation is not dict (got {type(val).__name__})"
                )

        # Sample data
        report["structure"]["sample_item"] = {
            "description": first_item.get("description", "N/A")[:50],
            "equation": first_item.get("discovered_equation", "N/A")[:50],
            "domain": first_item.get("domain", "N/A"),
            "valid": first_item.get("validation", {}).get("valid", False),
            "score": first_item.get("validation", {}).get("total_score", 0),
        }

        # Count issues across all items
        stats = {
            "missing_description": 0,
            "missing_equation": 0,
            "missing_domain": 0,
            "invalid": 0,
            "zero_r2": 0,
        }

        for item in data:
            if not item.get("description") or item.get("description") == "N/A":
                stats["missing_description"] += 1
            if (
                not item.get("discovered_equation")
                or item.get("discovered_equation") == "N/A"
            ):
                stats["missing_equation"] += 1
            if not item.get("domain") or item.get("domain") == "unknown":
                stats["missing_domain"] += 1

            val = item.get("validation", {})
            if not val.get("valid", False):
                stats["invalid"] += 1
            if val.get("r2_score", 0) == 0:
                stats["zero_r2"] += 1

        report["structure"]["stats"] = stats

        return report

    except json.JSONDecodeError as e:
        return {
            "filepath": filepath,
            "valid": False,
            "issues": [f"❌ JSON parse error: {e}"],
        }
    except FileNotFoundError:
        return {"filepath": filepath, "valid": False, "issues": [f"❌ File not found"]}
    except Exception as e:
        return {"filepath": filepath, "valid": False, "issues": [f"❌ Error: {e}"]}


def print_inspection_report(report: Dict[str, Any]):
    """Print a formatted inspection report"""
    print(f"\n{'=' * 70}")
    print(f"File: {report['filepath']}")
    print(f"{'=' * 70}")

    if not report.get("valid", False):
        print("❌ INVALID FILE")
        for issue in report.get("issues", []):
            print(f"  {issue}")
        return

    print(f"Type: {report.get('type')}")

    if report.get("issues"):
        print("\n🚨 Issues Found:")
        for issue in report["issues"]:
            print(f"  {issue}")
    else:
        print("\n✅ Structure looks good")

    structure = report.get("structure", {})

    if "count" in structure:
        print(f"\n📊 Statistics:")
        print(f"  Total items: {structure['count']}")

        if "stats" in structure:
            stats = structure["stats"]
            print(f"\n  Data Quality:")
            print(f"    Missing descriptions: {stats['missing_description']}")
            print(f"    Missing equations:    {stats['missing_equation']}")
            print(f"    Missing domains:      {stats['missing_domain']}")
            print(f"    Invalid formulas:     {stats['invalid']}")
            print(f"    Zero R² scores:       {stats['zero_r2']}")

    if "keys" in structure:
        print(f"\n  Available fields: {', '.join(structure['keys'])}")

    if "validation_keys" in structure:
        print(f"  Validation fields: {', '.join(structure['validation_keys'])}")

    if "sample_item" in structure:
        sample = structure["sample_item"]
        print(f"\n📝 Sample Item:")
        print(f"  Description: {sample['description']}")
        print(f"  Equation:    {sample['equation']}")
        print(f"  Domain:      {sample['domain']}")
        print(f"  Valid:       {sample['valid']}")
        print(f"  Score:       {sample['score']}/100")


def suggest_fixes(reports: List[Dict[str, Any]]):
    """Analyze all reports and suggest fixes"""
    print(f"\n{'=' * 70}")
    print(f"{'RECOMMENDED FIXES':^70}")
    print(f"{'=' * 70}\n")

    all_issues = []
    for report in reports:
        all_issues.extend(report.get("issues", []))

    # Categorize issues
    missing_equations = sum(
        1
        for r in reports
        if any(
            "Missing fields" in i and "discovered_equation" in i
            for i in r.get("issues", [])
        )
    )
    not_lists = sum(
        1 for r in reports if any("Not a list" in i for i in r.get("issues", []))
    )

    stats_totals = {
        "missing_description": 0,
        "missing_equation": 0,
        "missing_domain": 0,
        "invalid": 0,
        "zero_r2": 0,
        "total_items": 0,
    }

    for report in reports:
        if "structure" in report and "stats" in report["structure"]:
            stats = report["structure"]["stats"]
            for key in stats:
                if key in stats_totals:
                    stats_totals[key] += stats[key]
            if "count" in report["structure"]:
                stats_totals["total_items"] += report["structure"]["count"]

    print("🔧 Issue Summary:")
    print(f"  Files with wrong structure (not list): {not_lists}")
    print(f"  Total items across all files: {stats_totals['total_items']}")
    print(f"  Items missing equations: {stats_totals['missing_equation']}")
    print(f"  Items missing domains: {stats_totals['missing_domain']}")
    print(f"  Invalid formulas: {stats_totals['invalid']}")
    print(f"  Zero R² scores: {stats_totals['zero_r2']}")

    print("\n💡 Recommended Actions:\n")

    if not_lists > 0:
        print("1. Fix file structure:")
        print("   - Convert dict files to list format")
        print("   - Ensure each file contains: [{...}, {...}]")

    if stats_totals["missing_equation"] > stats_totals["total_items"] * 0.5:
        print("\n2. Add discovered equations:")
        print("   - Run symbolic regression to discover formulas")
        print("   - Or add ground truth equations if available")
        print("   - Format: LaTeX strings (e.g., '\\\\frac{x}{y}')")

    if stats_totals["missing_domain"] > stats_totals["total_items"] * 0.5:
        print("\n3. Assign domains:")
        print("   - Add 'domain' field to each item")
        print("   - Valid domains: 'defi', 'finance', 'esg', 'risk'")

    if stats_totals["zero_r2"] > stats_totals["total_items"] * 0.8:
        print("\n4. Run validation:")
        print("   - Validate formulas against test data")
        print("   - Calculate R² scores")
        print("   - Update validation.r2_score fields")

    print("\n📋 Example correct structure:")
    print(
        json.dumps(
            {
                "description": "Impermanent Loss Formula",
                "discovered_equation": "\\\\sqrt{x \\\\cdot y}",
                "domain": "defi",
                "validation": {
                    "total_score": 95.5,
                    "valid": True,
                    "r2_score": 0.98,
                    "symbolic_score": 90,
                    "physical_score": 100,
                },
            },
            indent=2,
        )
    )


def inspect_directory(data_dir: str, pattern: str = "*.json"):
    """Inspect all JSON files in directory"""
    import glob

    search_pattern = os.path.join(data_dir, pattern)
    files = glob.glob(search_pattern)

    if not files:
        print(f"❌ No files found matching: {search_pattern}")
        print(f"   Current directory: {os.getcwd()}")
        return

    print(f"\n🔍 Inspecting {len(files)} files in {data_dir}")

    reports = []
    for filepath in sorted(files):
        report = inspect_json_file(filepath)
        reports.append(report)
        print_inspection_report(report)

    suggest_fixes(reports)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Inspect and diagnose dataset structure issues"
    )
    parser.add_argument("--dir", required=True, help="Directory containing JSON files")
    parser.add_argument("--pattern", default="*.json", help="File pattern to match")
    parser.add_argument("--file", help="Inspect single file instead of directory")

    args = parser.parse_args()

    if args.file:
        report = inspect_json_file(args.file)
        print_inspection_report(report)
    else:
        inspect_directory(args.dir, args.pattern)

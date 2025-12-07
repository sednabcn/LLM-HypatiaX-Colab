#!/usr/bin/env python3
"""
HypatiaX Rule File Analyzer
============================
Analyzes the rule file versioning system and identifies the disconnect
between expected and actual rule file naming conventions.

This script helps solve the BLOCKER identified in the morning assessment.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


class RuleFileAnalyzer:
    """Analyzes and documents rule file structure."""

    def __init__(self, root_path: str = "./hypatiax"):
        self.root_path = Path(root_path)
        self.findings = {
            "existing_files": [],
            "expected_files": [],
            "missing_files": [],
            "version_directories": [],
            "jsonl_files": [],
        }

    def scan_rule_files(self) -> None:
        """Scan for all rule-related files."""
        print("🔍 Scanning for rule files...\n")

        # Find all .jsonl files
        for jsonl_file in self.root_path.rglob("*.jsonl"):
            self.findings["jsonl_files"].append(
                {
                    "path": str(jsonl_file.relative_to(self.root_path)),
                    "size": jsonl_file.stat().st_size,
                    "name": jsonl_file.name,
                }
            )

        # Find rules directories
        for rules_dir in self.root_path.rglob("rules"):
            if rules_dir.is_dir():
                self.findings["version_directories"].append(
                    {
                        "path": str(rules_dir.relative_to(self.root_path)),
                        "contents": [f.name for f in rules_dir.iterdir()],
                    }
                )

        # Find rules_versions directories
        for rules_ver_dir in self.root_path.rglob("rules_versions"):
            if rules_ver_dir.is_dir():
                self.findings["version_directories"].append(
                    {
                        "path": str(rules_ver_dir.relative_to(self.root_path)),
                        "contents": [f.name for f in rules_ver_dir.iterdir()],
                        "type": "version_directory",
                    }
                )

    def analyze_code_expectations(self) -> None:
        """Analyze what the code expects."""
        print("📖 Analyzing code expectations...\n")

        # Look for load_rules calls
        expected_patterns = [
            "rules_tableau_desc_version1.jsonl",
            "rules_tableau_formulas_version1.jsonl",
            "rules_tableau_version1.jsonl",
        ]

        self.findings["expected_files"] = expected_patterns

        # Look for actual ruler_*.jsonl files
        existing_patterns = [f["name"] for f in self.findings["jsonl_files"] if "ruler_" in f["name"]]

        self.findings["existing_files"] = existing_patterns

    def identify_gaps(self) -> None:
        """Identify what's missing."""
        print("🔍 Identifying gaps...\n")

        existing_names = set(f["name"] for f in self.findings["jsonl_files"])
        expected_names = set(self.findings["expected_files"])

        self.findings["missing_files"] = list(expected_names - existing_names)

    def generate_report(self) -> str:
        """Generate analysis report."""
        report = []
        report.append("=" * 70)
        report.append("HYPATIAX RULE FILE ANALYSIS REPORT")
        report.append("=" * 70)
        report.append("")

        # Existing JSONL files
        report.append("📄 EXISTING JSONL FILES:")
        report.append("-" * 70)
        for jsonl in self.findings["jsonl_files"]:
            size_kb = jsonl["size"] / 1024
            report.append(f"  ✓ {jsonl['path']}")
            report.append(f"    Size: {size_kb:.2f} KB")
        report.append("")

        # Expected files
        report.append("🎯 EXPECTED FILES (from code):")
        report.append("-" * 70)
        for expected in self.findings["expected_files"]:
            status = "❌ MISSING" if expected in self.findings["missing_files"] else "✓ FOUND"
            report.append(f"  {status} {expected}")
        report.append("")

        # Version directories
        report.append("📁 RULES DIRECTORIES:")
        report.append("-" * 70)
        for ver_dir in self.findings["version_directories"]:
            report.append(f"  📂 {ver_dir['path']}")
            for item in ver_dir["contents"]:
                report.append(f"     - {item}")
        report.append("")

        # Analysis
        report.append("🔍 ANALYSIS:")
        report.append("-" * 70)

        if self.findings["missing_files"]:
            report.append("  ⚠️  PROBLEM IDENTIFIED:")
            report.append("     The code expects versioned rule files (rules_*_version1.jsonl)")
            report.append("     but only non-versioned files (ruler_*.jsonl) exist.")
            report.append("")
            report.append("  💡 POSSIBLE SOLUTIONS:")
            report.append("     1. Rename existing ruler_*.jsonl → rules_*_version1.jsonl")
            report.append("     2. Look for a script that generates versioned rules")
            report.append("     3. Check if rules_versions/ should contain these files")
            report.append("     4. Update code to use ruler_*.jsonl naming convention")
        else:
            report.append("  ✅ All expected files found!")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)

    def suggest_fix(self) -> Dict:
        """Suggest fix options."""
        fixes = {"option_1_rename": [], "option_2_generate": None, "option_3_code_change": []}

        # Option 1: Rename files
        mapping = {
            "ruler_tableau_desc.jsonl": "rules_tableau_desc_version1.jsonl",
            "ruler_tableau_formulas.jsonl": "rules_tableau_formulas_version1.jsonl",
            "ruler_tableau.jsonl": "rules_tableau_version1.jsonl",
        }

        for old_name, new_name in mapping.items():
            old_files = [f for f in self.findings["jsonl_files"] if f["name"] == old_name]
            if old_files:
                for old_file in old_files:
                    old_path = self.root_path / old_file["path"]
                    new_path = old_path.parent / new_name
                    fixes["option_1_rename"].append(
                        {"old": str(old_path), "new": str(new_path), "command": f"mv '{old_path}' '{new_path}'"}
                    )

        # Option 2: Check for generation script
        potential_scripts = ["generate_rules.py", "create_versioned_rules.py", "prepare_rules.py"]

        for script in self.root_path.rglob("*.py"):
            if any(pattern in script.name for pattern in ["generate", "prepare", "create", "version"]):
                if fixes["option_2_generate"] is None:
                    fixes["option_2_generate"] = []
                fixes["option_2_generate"].append(str(script.relative_to(self.root_path)))

        return fixes

    def generate_fix_script(self, fixes: Dict, output_path: str = "fix_rules.sh") -> None:
        """Generate shell script to fix the issue."""
        script_lines = [
            "#!/bin/bash",
            "# Auto-generated script to fix HypatiaX rule file naming",
            "# Generated by Rule File Analyzer",
            "",
            "set -e  # Exit on error",
            "",
            "echo '🔧 Fixing HypatiaX rule file naming...'",
            "",
        ]

        if fixes["option_1_rename"]:
            script_lines.append("# Option 1: Rename existing files")
            script_lines.append("echo '📝 Renaming rule files...'")
            for rename in fixes["option_1_rename"]:
                script_lines.append(f"cp '{rename['old']}' '{rename['new']}'")
                script_lines.append(f"echo '  ✓ Created {rename['new']}'")
            script_lines.append("")

        script_lines.append("echo '✅ Rule files fixed!'")
        script_lines.append("echo ''")
        script_lines.append("echo '📋 Next steps:'")
        script_lines.append("echo '  1. Run pytest tests/ to verify'")
        script_lines.append("echo '  2. Check if tests pass now'")

        with open(output_path, "w") as f:
            f.write("\n".join(script_lines))

        # Make executable
        os.chmod(output_path, 0o755)

        print(f"\n✅ Generated fix script: {output_path}")
        print(f"   Run with: ./{output_path}")

    def run_full_analysis(self) -> None:
        """Run complete analysis."""
        self.scan_rule_files()
        self.analyze_code_expectations()
        self.identify_gaps()

        # Generate report
        report = self.generate_report()
        print(report)

        # Save report
        with open("rule_analysis_report.txt", "w") as f:
            f.write(report)
        print("\n📄 Report saved to: rule_analysis_report.txt")

        # Generate fixes
        fixes = self.suggest_fix()

        print("\n💡 SUGGESTED FIXES:")
        print("-" * 70)

        if fixes["option_1_rename"]:
            print("\nOption 1: Rename Files")
            print("  Run these commands:")
            for rename in fixes["option_1_rename"]:
                print(f"    {rename['command']}")

        if fixes["option_2_generate"]:
            print("\nOption 2: Check Generation Scripts")
            print("  Found potential scripts:")
            for script in fixes["option_2_generate"]:
                print(f"    - {script}")

        # Generate fix script
        self.generate_fix_script(fixes)

        # Save JSON
        with open("rule_analysis.json", "w") as f:
            json.dump({"findings": self.findings, "fixes": fixes}, f, indent=2)
        print("📊 Analysis data saved to: rule_analysis.json")


def main():
    print("=" * 70)
    print("HypatiaX Rule File Analyzer")
    print("Solving the Morning Assessment BLOCKER")
    print("=" * 70)
    print("")

    analyzer = RuleFileAnalyzer()
    analyzer.run_full_analysis()

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()

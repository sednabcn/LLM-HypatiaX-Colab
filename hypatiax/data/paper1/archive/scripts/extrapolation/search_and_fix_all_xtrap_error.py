#!/usr/bin/env python3
"""
COMPREHENSIVE EXTRAPOLATION ERROR FINDER AND FIXER
==================================================

This script searches your ENTIRE project for the extrapolation error
calculation bug and fixes it everywhere.

THE BUG:
    extrap_error = (rmse_extrap / rmse_train) * 100  # ❌ WRONG

    This gives percentages like 3348%, which means 33.48×
    But you want 3348× (3348 times worse)

THE FIX:
    extrap_error = (rmse_extrap / rmse_train)  # ✅ CORRECT

    This gives multipliers like 3348× (3348 times worse)

WHAT IT DOES:
1. Recursively searches ALL Python files in your project
2. Finds ALL variations of the bug (multiple variable names, patterns)
3. Shows you what it found with context
4. Backs up files before modifying
5. Applies the fix automatically
6. Verifies the fix worked

Usage:
    # Search only (safe, no changes)
    python search_and_fix_all_extrap_errors.py --search

    # Fix everything
    python search_and_fix_all_extrap_errors.py --fix

    # Fix and show detailed output
    python search_and_fix_all_extrap_errors.py --fix --verbose
"""

import re
import sys
from pathlib import Path
from datetime import datetime
import shutil
import argparse
from typing import List, Tuple, Dict


class ExtrapolationErrorSearcher:
    """Find and fix extrapolation error calculations project-wide"""

    # Multiple patterns to catch all variations
    PATTERNS = [
        # Pattern 1: Simple assignment
        (r"(\w+_?error\w*)\s*=\s*\(([^)]+)\)\s*\*\s*100", "simple_multiply"),
        # Pattern 2: Within if/ternary
        (r"(\w+_?error\w*)\s*=\s*\(([^)]+)\)\s*\*\s*100\s+if\s+", "ternary_multiply"),
        # Pattern 3: Direct calculation in context
        (r"\(\s*(\w+)\s*/\s*(\w+)\s*\)\s*\*\s*100", "inline_multiply"),
        # Pattern 4: With variable capture
        (r"=\s*\(\s*rmse_\w+\s*/\s*rmse_\w+\s*\*\s*100\s*\)", "rmse_ratio_multiply"),
    ]

    # Keywords that indicate this is extrapolation-related
    EXTRAP_KEYWORDS = [
        "extrap",
        "extrapolation",
        "rmse_train",
        "rmse_test",
        "train_error",
        "test_error",
        "degradation",
    ]

    def __init__(self, project_root: Path = None, verbose: bool = False):
        self.project_root = project_root or Path.cwd()
        self.verbose = verbose
        self.findings = []
        self.backup_dir = None

    def search_project(self, exclude_dirs: List[str] = None) -> List[Dict]:
        """Search entire project for the bug"""

        if exclude_dirs is None:
            exclude_dirs = [
                ".git",
                "__pycache__",
                "venv",
                "env",
                ".venv",
                "node_modules",
                "build",
                "dist",
            ]

        print(f"\n{'='*80}")
        print("SEARCHING FOR EXTRAPOLATION ERROR BUGS")
        print(f"{'='*80}")
        print(f"📁 Project root: {self.project_root}")
        print(f"🔍 Excluding: {', '.join(exclude_dirs)}")

        findings = []
        total_files = 0

        # Find all Python files
        for py_file in self.project_root.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in py_file.parts for excluded in exclude_dirs):
                continue

            total_files += 1
            file_findings = self._search_file(py_file)
            if file_findings:
                findings.extend(file_findings)

        print(f"\n✅ Searched {total_files} Python files")
        print(f"🔴 Found {len(findings)} potential issue(s)")

        self.findings = findings
        return findings

    def _search_file(self, file_path: Path) -> List[Dict]:
        """Search a single file for the bug"""

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Could not read {file_path}: {e}")
            return []

        findings = []
        lines = content.split("\n")

        for pattern, pattern_type in self.PATTERNS:
            for match in re.finditer(pattern, content, re.MULTILINE):
                # Get line number
                line_num = content[: match.start()].count("\n") + 1

                # Get surrounding context
                start_line = max(0, line_num - 3)
                end_line = min(len(lines), line_num + 2)
                context_lines = lines[start_line:end_line]
                context = "\n".join(context_lines)

                # Check if this is really extrapolation-related
                is_extrap = any(kw in context.lower() for kw in self.EXTRAP_KEYWORDS)

                # Check if it's in a comment (false positive)
                line_content = lines[line_num - 1]
                is_comment = line_content.strip().startswith("#")

                if is_extrap and not is_comment:
                    findings.append(
                        {
                            "file": file_path,
                            "line_num": line_num,
                            "line_content": line_content,
                            "match": match.group(0),
                            "pattern_type": pattern_type,
                            "context": context,
                            "full_content": content,
                        }
                    )

        return findings

    def print_findings(self):
        """Print all findings with context"""

        if not self.findings:
            print("\n✅ No issues found!")
            return

        print(f"\n{'='*80}")
        print(f"FOUND {len(self.findings)} ISSUE(S)")
        print(f"{'='*80}")

        for i, finding in enumerate(self.findings, 1):
            rel_path = finding["file"].relative_to(self.project_root)

            print(f"\n{i}. 📄 {rel_path}")
            print(f"   Line {finding['line_num']}: {finding['pattern_type']}")
            print(f"\n   Context:")
            for line in finding["context"].split("\n"):
                marker = (
                    "➡️ " if line.strip() == finding["line_content"].strip() else "   "
                )
                print(f"   {marker}{line}")
            print()

    def create_backup(self):
        """Create backup directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_root / "backups_extrap_fix" / timestamp
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n📦 Backup directory: {self.backup_dir}")

    def apply_fixes(self, dry_run: bool = False) -> int:
        """Apply fixes to all findings"""

        if not self.findings:
            print("\n✅ No issues to fix!")
            return 0

        if dry_run:
            print(f"\n{'='*80}")
            print("DRY RUN - SHOWING PROPOSED CHANGES")
            print(f"{'='*80}")
        else:
            print(f"\n{'='*80}")
            print("APPLYING FIXES")
            print(f"{'='*80}")
            self.create_backup()

        fixed_files = set()
        fixed_count = 0

        # Group findings by file
        by_file = {}
        for finding in self.findings:
            file_path = finding["file"]
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(finding)

        # Process each file
        for file_path, file_findings in by_file.items():
            if self._fix_file(file_path, file_findings, dry_run):
                fixed_files.add(file_path)
                fixed_count += len(file_findings)

        if not dry_run:
            print(f"\n✅ Fixed {fixed_count} issue(s) in {len(fixed_files)} file(s)")
            print(f"📦 Backups saved to: {self.backup_dir}")

        return fixed_count

    def _fix_file(self, file_path: Path, findings: List[Dict], dry_run: bool) -> bool:
        """Fix all issues in a single file"""

        rel_path = file_path.relative_to(self.project_root)

        print(f"\n📄 {rel_path}")

        # Read original content
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Sort findings by line number (reverse) to maintain positions
        findings_sorted = sorted(findings, key=lambda x: x["line_num"], reverse=True)

        # Apply fixes
        for finding in findings_sorted:
            line_num = finding["line_num"]
            line_content = finding["line_content"]

            # Create fixed version
            # Remove * 100 and add comment
            fixed_line = re.sub(r"\s*\*\s*100\s*", "", line_content)

            # Add comment if not present
            if "# Multiplier" not in fixed_line and "#" not in fixed_line:
                # Find the end of the statement
                if line_content.rstrip().endswith(":"):
                    fixed_line = fixed_line.rstrip() + "  # Multiplier, not %\n"
                else:
                    fixed_line = fixed_line.rstrip() + "  # Multiplier, not %\n"

            print(f"\n   Line {line_num}:")
            print(f"   BEFORE: {line_content.rstrip()}")
            print(f"   AFTER:  {fixed_line.rstrip()}")

            if not dry_run:
                # Replace in content
                lines = content.split("\n")
                lines[line_num - 1] = fixed_line.rstrip()
                content = "\n".join(lines)

        if dry_run:
            return False

        # Backup original
        backup_file = self.backup_dir / file_path.name
        counter = 1
        while backup_file.exists():
            backup_file = (
                self.backup_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
            )
            counter += 1

        shutil.copy2(file_path, backup_file)
        print(f"   📦 Backed up to: {backup_file.name}")

        # Write fixed content
        file_path.write_text(content, encoding="utf-8")
        print(f"   ✅ Fixed and saved")

        return True

    def verify_fixes(self) -> bool:
        """Verify that all fixes were applied correctly"""

        print(f"\n{'='*80}")
        print("VERIFYING FIXES")
        print(f"{'='*80}")

        # Re-search the project
        new_findings = self.search_project()

        if not new_findings:
            print("\n✅ All fixes verified - no issues remaining!")
            return True
        else:
            print(f"\n⚠️  Still found {len(new_findings)} issue(s)")
            print("   Some fixes may not have been applied correctly")
            return False

    def generate_report(self):
        """Generate a summary report"""

        print(f"\n{'='*80}")
        print("SUMMARY REPORT")
        print(f"{'='*80}")

        if not self.findings:
            print("\n✅ No extrapolation error bugs found in your project!")
            return

        print(f"\n📊 Statistics:")
        print(f"   Total issues found: {len(self.findings)}")

        # Count by file
        by_file = {}
        for finding in self.findings:
            file_name = finding["file"].name
            by_file[file_name] = by_file.get(file_name, 0) + 1

        print(f"   Files affected: {len(by_file)}")
        print(f"\n📁 Issues per file:")
        for file_name, count in sorted(
            by_file.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"      {file_name}: {count} issue(s)")

        print(f"\n🔧 What the fix does:")
        print(f"   BEFORE: extrap_error = (rmse_extrap / rmse_train) * 100")
        print(f"           Result: 3348% (means 33.48×) ❌")
        print(f"   AFTER:  extrap_error = (rmse_extrap / rmse_train)")
        print(f"           Result: 3348× (means 3348×) ✅")

        print(f"\n📝 Next steps:")
        print(f"   1. Review the findings above")
        print(f"   2. Run with --fix to apply changes")
        print(f"   3. Test your code to verify results")
        print(f"   4. Update LaTeX to use × instead of %")


def main():
    parser = argparse.ArgumentParser(
        description="Find and fix extrapolation error bugs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search only (safe, shows what would be fixed)
  python search_and_fix_all_extrap_errors.py --search

  # Search with verbose output
  python search_and_fix_all_extrap_errors.py --search --verbose

  # Fix all issues (creates backups first)
  python search_and_fix_all_extrap_errors.py --fix

  # Fix and verify
  python search_and_fix_all_extrap_errors.py --fix --verify

  # Specify custom project directory
  python search_and_fix_all_extrap_errors.py --fix --project /path/to/project
        """,
    )

    parser.add_argument(
        "--search",
        action="store_true",
        help="Search for issues without fixing (default if no other option)",
    )

    parser.add_argument(
        "--fix", action="store_true", help="Fix all issues found (creates backups)"
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify fixes after applying (only with --fix)",
    )

    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    parser.add_argument(
        "--project",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Default to search if nothing specified
    if not args.search and not args.fix:
        args.search = True

    # Create searcher
    searcher = ExtrapolationErrorSearcher(
        project_root=args.project, verbose=args.verbose
    )

    # Search for issues
    searcher.search_project()
    searcher.print_findings()

    # Apply fixes if requested
    if args.fix:
        fixed_count = searcher.apply_fixes(dry_run=False)

        if fixed_count > 0 and args.verify:
            searcher.verify_fixes()
    else:
        print(f"\n💡 To fix these issues, run with --fix flag")

    # Generate report
    searcher.generate_report()

    print(f"\n{'='*80}")
    print("DONE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

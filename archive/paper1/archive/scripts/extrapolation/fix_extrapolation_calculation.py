#!/usr/bin/env python3
"""
EXTRAPOLATION ERROR FIX SCRIPT
==============================

This script fixes the calculus error in your extrapolation calculations.

THE PROBLEM:
    extrap_error = (rmse_extrap / rmse_train) * 100  # WRONG - this gives %

    When rmse_extrap = 3348 * rmse_train:
        Result: 334800%  (WRONG - should be 3348×)

THE FIX:
    extrap_error = (rmse_extrap / rmse_train)  # CORRECT - this gives multiplier

    When rmse_extrap = 3348 * rmse_train:
        Result: 3348×  (CORRECT)

WHAT THIS SCRIPT DOES:
1. Finds all Python files with the error
2. Automatically fixes the calculation
3. Creates backups of original files
4. Verifies the fixes
5. Optionally re-runs tests to generate corrected output

Usage:
    python fix_extrapolation_calculation.py --dry-run  # Preview changes
    python fix_extrapolation_calculation.py --fix      # Apply fixes
    python fix_extrapolation_calculation.py --fix --rerun  # Fix and regenerate data
"""

import re
import sys
from pathlib import Path
from datetime import datetime
import shutil
import argparse
import subprocess


class ExtrapolationErrorFixer:
    """Fix extrapolation error calculations across all Python files"""

    # Pattern to match the incorrect calculation
    WRONG_PATTERN = re.compile(
        r"(\s*extrap_error(?:_\w+)?\s*=\s*\([^)]+\)\s*\*\s*100)", re.MULTILINE
    )

    # Files to check (add more as needed)
    TARGET_FILES = [
        "standalone_real_methods_test.py",
        "test_extrapolation_stress.py",
        "ultimate_comparative_suite_complte.py",
        # Add any other files that calculate extrapolation errors
    ]

    def __init__(self, project_root: Path = None):
        """Initialize fixer with project root directory"""
        self.project_root = project_root or Path.cwd()
        self.fixes_applied = []
        self.backup_dir = (
            self.project_root
            / "backups"
            / f'extrap_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        )

    def find_files_with_error(self):
        """Find all Python files that contain the error"""
        print("\n" + "=" * 80)
        print("SEARCHING FOR FILES WITH EXTRAPOLATION ERROR")
        print("=" * 80)

        files_with_error = []

        # Search in current directory and subdirectories
        for py_file in self.project_root.rglob("*.py"):
            if any(target in py_file.name for target in self.TARGET_FILES):
                try:
                    content = py_file.read_text()
                    matches = list(self.WRONG_PATTERN.finditer(content))

                    if matches:
                        files_with_error.append((py_file, matches))
                        print(
                            f"\n✓ Found {len(matches)} issue(s) in: {py_file.relative_to(self.project_root)}"
                        )

                        for i, match in enumerate(matches, 1):
                            # Get line number
                            line_num = content[: match.start()].count("\n") + 1
                            print(f"  Line {line_num}: {match.group(1).strip()}")

                except Exception as e:
                    print(f"⚠️  Could not read {py_file}: {e}")

        if not files_with_error:
            print("\n✅ No files found with the error pattern!")
            print("   (This might mean they're already fixed)")

        return files_with_error

    def preview_fix(self, file_path: Path, content: str):
        """Show what the fix would look like"""
        print(f"\n{'─'*80}")
        print(f"Preview for: {file_path.name}")
        print(f"{'─'*80}")

        lines = content.split("\n")
        matches = list(self.WRONG_PATTERN.finditer(content))

        for match in matches:
            line_num = content[: match.start()].count("\n")
            old_line = lines[line_num]

            # Create the fixed version
            new_line = re.sub(r"\s*\*\s*100\s*", "  ", old_line)
            new_line += "  # Multiplier, not percentage"

            print(f"\nLine {line_num + 1}:")
            print(f"  BEFORE: {old_line.strip()}")
            print(f"  AFTER:  {new_line.strip()}")

    def apply_fix(self, file_path: Path, dry_run: bool = True):
        """Apply the fix to a file"""

        content = file_path.read_text()
        original_content = content

        # Preview changes
        if dry_run:
            self.preview_fix(file_path, content)
            return False

        # Create backup
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backup_dir / file_path.name
        shutil.copy2(file_path, backup_path)
        print(f"📦 Backed up to: {backup_path}")

        # Apply fix - remove '* 100' and add comment
        fixed_content = content
        matches = list(self.WRONG_PATTERN.finditer(content))

        # Process matches in reverse order to maintain positions
        for match in reversed(matches):
            old_text = match.group(1)
            # Remove ' * 100' and add comment
            new_text = re.sub(r"\s*\*\s*100\s*", "", old_text)

            # Only add comment if not already present
            if "# Multiplier" not in old_text:
                new_text += "  # Multiplier, not percentage"

            fixed_content = (
                fixed_content[: match.start()] + new_text + fixed_content[match.end() :]
            )

        # Write fixed content
        file_path.write_text(fixed_content)

        changes = len(matches)
        self.fixes_applied.append(
            {"file": file_path, "changes": changes, "backup": backup_path}
        )

        print(f"✅ Fixed {changes} issue(s) in: {file_path.name}")
        return True

    def verify_fixes(self):
        """Verify that fixes were applied correctly"""
        print("\n" + "=" * 80)
        print("VERIFYING FIXES")
        print("=" * 80)

        all_good = True

        for fix in self.fixes_applied:
            file_path = fix["file"]
            content = file_path.read_text()

            # Check if the wrong pattern still exists
            if self.WRONG_PATTERN.search(content):
                print(f"❌ {file_path.name}: Still contains errors!")
                all_good = False
            else:
                # Check if the correct pattern exists
                if "extrap_error" in content and "# Multiplier" in content:
                    print(f"✅ {file_path.name}: Successfully fixed")
                else:
                    print(f"⚠️  {file_path.name}: Fixed but couldn't verify comment")

        return all_good

    def rerun_tests(self):
        """Optionally re-run tests to generate corrected data"""
        print("\n" + "=" * 80)
        print("RE-RUNNING TESTS TO GENERATE CORRECTED DATA")
        print("=" * 80)

        test_commands = [
            ["python", "standalone_real_methods_test.py", "--all", "--extrapolation"],
            # Add more test commands as needed
        ]

        for cmd in test_commands:
            script_name = cmd[1]
            script_path = self.project_root / script_name

            if not script_path.exists():
                print(f"⚠️  Skipping {script_name} (not found)")
                continue

            print(f"\n🚀 Running: {' '.join(cmd)}")
            try:
                result = subprocess.run(
                    cmd,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                )

                if result.returncode == 0:
                    print(f"✅ {script_name} completed successfully")
                else:
                    print(f"❌ {script_name} failed:")
                    print(result.stderr[:500])

            except subprocess.TimeoutExpired:
                print(f"⏰ {script_name} timed out")
            except Exception as e:
                print(f"❌ Error running {script_name}: {e}")

    def generate_report(self):
        """Generate a summary report"""
        print("\n" + "=" * 80)
        print("FIX SUMMARY REPORT")
        print("=" * 80)

        if not self.fixes_applied:
            print("\n📋 No fixes were applied (dry run or no files found)")
            return

        print(f"\n✅ Successfully fixed {len(self.fixes_applied)} file(s)")
        print(f"📦 Backups saved to: {self.backup_dir}")

        print("\nFiles modified:")
        for fix in self.fixes_applied:
            print(f"  • {fix['file'].name}: {fix['changes']} change(s)")

        print("\n📝 What changed:")
        print(
            "  BEFORE: extrap_error = (rmse_extrap / rmse_train) * 100  # 3348% = 33.48×"
        )
        print("  AFTER:  extrap_error = (rmse_extrap / rmse_train)  # 3348× = 3348×")

        print("\n🔄 Next steps:")
        print("  1. Review the changes in the modified files")
        print("  2. Run your tests to verify the output is correct")
        print("  3. Update your LaTeX paper to use × notation instead of %")
        print("  4. If something went wrong, restore from backups in:")
        print(f"     {self.backup_dir}")

    def run(self, dry_run: bool = True, rerun: bool = False):
        """Run the complete fix process"""

        # Find files
        files_with_error = self.find_files_with_error()

        if not files_with_error:
            return

        # Apply fixes
        print("\n" + "=" * 80)
        if dry_run:
            print("DRY RUN - PREVIEW MODE (No changes will be made)")
        else:
            print("APPLYING FIXES")
        print("=" * 80)

        for file_path, matches in files_with_error:
            self.apply_fix(file_path, dry_run=dry_run)

        # Verify if not dry run
        if not dry_run:
            if self.verify_fixes():
                print("\n✅ All fixes verified successfully!")
            else:
                print("\n⚠️  Some fixes could not be verified - please check manually")

        # Generate report
        self.generate_report()

        # Optionally rerun tests
        if rerun and not dry_run:
            self.rerun_tests()


def main():
    parser = argparse.ArgumentParser(
        description="Fix extrapolation error calculations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what will be changed (safe, no modifications)
  python fix_extrapolation_calculation.py --dry-run

  # Apply fixes to all files
  python fix_extrapolation_calculation.py --fix

  # Apply fixes and re-run tests to generate corrected data
  python fix_extrapolation_calculation.py --fix --rerun

  # Specify custom project directory
  python fix_extrapolation_calculation.py --fix --project-dir /path/to/project
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files (default: True)",
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Actually apply the fixes (creates backups first)",
    )

    parser.add_argument(
        "--rerun",
        action="store_true",
        help="Re-run tests after fixing to generate corrected output",
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Default to dry-run if neither --dry-run nor --fix specified
    dry_run = not args.fix

    if dry_run and not args.dry_run:
        print("\n⚠️  No --fix flag specified, running in DRY RUN mode")
        print("    Use --fix to actually apply changes\n")

    # Create fixer and run
    fixer = ExtrapolationErrorFixer(project_root=args.project_dir)
    fixer.run(dry_run=dry_run, rerun=args.rerun)

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

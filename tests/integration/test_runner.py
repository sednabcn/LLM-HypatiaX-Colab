#!/usr/bin/env python3
"""
Test Runner for HypatiaX Project
Discovers and runs all test files in the project structure
"""

import os
import sys
import subprocess
import glob
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime


class TestRunner:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.results: Dict[str, bool] = {}
        self.test_files: List[Path] = []
        
    def discover_tests(self) -> List[Path]:
        """Discover all test files in the project structure"""
        test_patterns = [
            "**/test_*.py",
            "**/*_test.py",
            "**/tests/*.py"
        ]
        
        test_files = set()
        for pattern in test_patterns:
            for file_path in self.root_dir.rglob(pattern):
                # Skip __init__.py and __pycache__
                if file_path.name != "__init__.py" and "__pycache__" not in str(file_path):
                    test_files.add(file_path)
        
        self.test_files = sorted(list(test_files))
        return self.test_files
    
    def run_test_file(self, test_file: Path) -> Tuple[bool, str]:
        """Run a single test file and return success status and output"""
        try:
            # Try running with unittest first
            result = subprocess.run(
                [sys.executable, "-m", "unittest", str(test_file)],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # If unittest fails, try running directly
            if result.returncode != 0:
                result = subprocess.run(
                    [sys.executable, str(test_file)],
                    cwd=self.root_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, "Test timed out after 30 seconds"
        except Exception as e:
            return False, f"Error running test: {str(e)}"
    
    def get_relative_path(self, path: Path) -> str:
        """Get relative path from root directory"""
        try:
            return str(path.relative_to(self.root_dir))
        except ValueError:
            return str(path)
    
    def run_all_tests(self, verbose: bool = False) -> Dict[str, bool]:
        """Run all discovered tests and return results"""
        print(f"\n{'='*70}")
        print(f"HypatiaX Test Runner")
        print(f"{'='*70}")
        print(f"Root Directory: {self.root_dir}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Discover tests
        print("Discovering tests...")
        self.discover_tests()
        print(f"Found {len(self.test_files)} test files\n")
        
        if not self.test_files:
            print("No test files found!")
            return {}
        
        # List all test files
        print("Test Files to Run:")
        print("-" * 70)
        for i, test_file in enumerate(self.test_files, 1):
            print(f"{i:3d}. {self.get_relative_path(test_file)}")
        print()
        
        # Run tests
        print(f"\n{'='*70}")
        print("Running Tests...")
        print(f"{'='*70}\n")
        
        passed = 0
        failed = 0
        
        for i, test_file in enumerate(self.test_files, 1):
            rel_path = self.get_relative_path(test_file)
            print(f"[{i}/{len(self.test_files)}] Running: {rel_path}")
            
            success, output = self.run_test_file(test_file)
            self.results[rel_path] = success
            
            if success:
                print(f"    ✓ PASSED")
                passed += 1
            else:
                print(f"    ✗ FAILED")
                failed += 1
                if verbose and output:
                    print(f"    Output: {output[:200]}...")
            print()
        
        # Print summary
        self.print_summary(passed, failed)
        
        return self.results
    
    def print_summary(self, passed: int, failed: int):
        """Print test execution summary"""
        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n{'='*70}")
        print("Test Results Summary")
        print(f"{'='*70}\n")
        
        # Passed tests
        print(f"✓ PASSED: {passed}/{total} tests")
        if passed > 0:
            print("  Successful tests:")
            for test_path, result in self.results.items():
                if result:
                    print(f"    • {test_path}")
        print()
        
        # Failed tests
        if failed > 0:
            print(f"✗ FAILED: {failed}/{total} tests")
            print("  Failed tests:")
            for test_path, result in self.results.items():
                if not result:
                    print(f"    • {test_path}")
            print()
        
        # Statistics
        print(f"{'='*70}")
        print(f"Total Tests:     {total}")
        print(f"Passed:          {passed}")
        print(f"Failed:          {failed}")
        print(f"Success Rate:    {success_rate:.1f}%")
        print(f"End Time:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Exit code
        if failed > 0:
            print("❌ Some tests failed!")
            return 1
        else:
            print("✅ All tests passed!")
            return 0


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run all tests in the HypatiaX project"
    )
    parser.add_argument(
        "-d", "--directory",
        default=".",
        help="Root directory to search for tests (default: current directory)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output for failed tests"
    )
    parser.add_argument(
        "-l", "--list-only",
        action="store_true",
        help="Only list test files without running them"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(args.directory)
    
    if args.list_only:
        # Just list tests
        print("\nDiscovering tests...")
        test_files = runner.discover_tests()
        print(f"\nFound {len(test_files)} test files:\n")
        for i, test_file in enumerate(test_files, 1):
            print(f"{i:3d}. {runner.get_relative_path(test_file)}")
        print()
        return 0
    
    # Run all tests
    results = runner.run_all_tests(verbose=args.verbose)
    
    # Return appropriate exit code
    failed_count = sum(1 for result in results.values() if not result)
    return 1 if failed_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

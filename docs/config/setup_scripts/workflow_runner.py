#!/usr/bin/env python3
"""
HypatiaX Workflow Runner
Executes all tests and scripts across directories in specified order
Generates comprehensive reports for each execution
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import traceback
from paths import paths


class WorkflowRunner:
    """Execute tests and scripts across HypatiaX project with reporting"""

    def __init__(self, base_path: str = "."):
        self.paths = paths  # Use centralized path config
        self.base_path = paths.root
        self.report_dir = self.base_path / "workflow_reports"
        self.report_dir.mkdir(exist_ok=True)

        # Execution order as specified
        self.execution_order = [
            "hypatiax/datasets",
            "hypatiax/patterns",
            "hypatiax/custom_ner",
            "hypatiax/data_spacy",
            "hypatiax/models",
            "hypatiax/core",
            "hypatiax/mappings",
            "hypatiax/scripts_",
        ]

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_path": str(self.base_path),
            "modules": {},
        }

    def find_executable_files(self, directory: Path) -> Tuple[List[Path], List[Path]]:
        """Find all test files and script files in directory"""
        tests = []
        scripts = []

        if not directory.exists():
            return tests, scripts

        for item in directory.rglob("*.py"):
            # Skip __init__.py and __pycache__
            if item.name == "__init__.py" or "__pycache__" in str(item):
                continue

            # Skip backup files
            if item.name.endswith("~"):
                continue

            # Categorize by filename pattern
            if item.name.startswith("test_") or item.name.startswith("Test_"):
                tests.append(item)
            elif item.name.startswith("script_") or "script" in item.name:
                scripts.append(item)
            elif any(
                x in item.name
                for x in ["run_time", "proc_time", "evaluate", "training"]
            ):
                scripts.append(item)

        return sorted(tests), sorted(scripts)

    def execute_file(self, filepath: Path, file_type: str) -> Dict:
        """Execute a single Python file and capture results"""
        result = {
            "file": str(filepath.relative_to(self.base_path)),
            "type": file_type,
            "status": "not_run",
            "start_time": None,
            "end_time": None,
            "duration": 0,
            "stdout": "",
            "stderr": "",
            "return_code": None,
            "error": None,
        }

        print(f"\n{'='*80}")
        print(f"Executing: {result['file']}")
        print(f"Type: {file_type}")
        print(f"{'='*80}")

        result["start_time"] = datetime.now().isoformat()
        start = time.time()

        try:
            # Execute with timeout
            proc = subprocess.run(
                [sys.executable, str(filepath)],
                cwd=filepath.parent,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            result["stdout"] = proc.stdout
            result["stderr"] = proc.stderr
            result["return_code"] = proc.returncode

            if proc.returncode == 0:
                result["status"] = "success"
                print(f"✓ SUCCESS")
            else:
                result["status"] = "failed"
                print(f"✗ FAILED (return code: {proc.returncode})")

        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["error"] = "Execution timeout (5 minutes)"
            print(f"⏱ TIMEOUT")

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
            print(f"⚠ ERROR: {e}")

        finally:
            end = time.time()
            result["end_time"] = datetime.now().isoformat()
            result["duration"] = round(end - start, 2)
            print(f"Duration: {result['duration']}s")

        return result

    def process_module(self, module_name: str) -> Dict:
        """Process all tests and scripts in a module"""
        print(f"\n{'#'*80}")
        print(f"# MODULE: {module_name.upper()}")
        print(f"{'#'*80}")

        module_path = self.base_path / module_name
        module_result = {
            "module": module_name,
            "path": str(module_path.relative_to(self.base_path)),
            "exists": module_path.exists(),
            "tests": [],
            "scripts": [],
            "summary": {
                "total_files": 0,
                "successful": 0,
                "failed": 0,
                "errors": 0,
                "timeouts": 0,
                "skipped": 0,
                "total_duration": 0,
            },
        }

        if not module_path.exists():
            print(f"⚠ Module not found: {module_path}")
            return module_result

        # Find all executable files
        tests, scripts = self.find_executable_files(module_path)

        print(f"\nFound {len(tests)} test files")
        print(f"Found {len(scripts)} script files")

        # Execute tests first
        for test_file in tests:
            result = self.execute_file(test_file, "test")
            module_result["tests"].append(result)
            self._update_summary(module_result["summary"], result)

        # Then execute scripts
        for script_file in scripts:
            result = self.execute_file(script_file, "script")
            module_result["scripts"].append(result)
            self._update_summary(module_result["summary"], result)

        return module_result

    def _update_summary(self, summary: Dict, result: Dict):
        """Update summary statistics"""
        summary["total_files"] += 1
        summary["total_duration"] += result["duration"]

        if result["status"] == "success":
            summary["successful"] += 1
        elif result["status"] == "failed":
            summary["failed"] += 1
        elif result["status"] == "error":
            summary["errors"] += 1
        elif result["status"] == "timeout":
            summary["timeouts"] += 1
        else:
            summary["skipped"] += 1

    def generate_text_report(self, module_result: Dict, filepath: Path):
        """Generate human-readable text report"""
        with open(filepath, "w") as f:
            f.write("=" * 80 + "\n")
            f.write(f"HypatiaX Workflow Report - {module_result['module'].upper()}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Timestamp: {self.results['timestamp']}\n")
            f.write(f"Module Path: {module_result['path']}\n")
            f.write(f"Module Exists: {module_result['exists']}\n\n")

            summary = module_result["summary"]
            f.write("SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Files Executed: {summary['total_files']}\n")
            f.write(f"Successful: {summary['successful']}\n")
            f.write(f"Failed: {summary['failed']}\n")
            f.write(f"Errors: {summary['errors']}\n")
            f.write(f"Timeouts: {summary['timeouts']}\n")
            f.write(f"Total Duration: {summary['total_duration']:.2f}s\n\n")

            # Test Results
            if module_result["tests"]:
                f.write("TEST RESULTS\n")
                f.write("-" * 80 + "\n")
                for test in module_result["tests"]:
                    self._write_execution_detail(f, test)

            # Script Results
            if module_result["scripts"]:
                f.write("\nSCRIPT RESULTS\n")
                f.write("-" * 80 + "\n")
                for script in module_result["scripts"]:
                    self._write_execution_detail(f, script)

    def _write_execution_detail(self, f, result: Dict):
        """Write detailed execution information"""
        status_symbol = {
            "success": "✓",
            "failed": "✗",
            "error": "⚠",
            "timeout": "⏱",
            "not_run": "○",
        }.get(result["status"], "?")

        f.write(f"\n{status_symbol} {result['file']}\n")
        f.write(f"   Status: {result['status'].upper()}\n")
        f.write(f"   Duration: {result['duration']}s\n")

        if result.get("return_code") is not None:
            f.write(f"   Return Code: {result['return_code']}\n")

        if result.get("error"):
            f.write(f"   Error: {result['error']}\n")

        if result["stdout"]:
            f.write(f"\n   STDOUT:\n")
            for line in result["stdout"].split("\n")[:50]:  # First 50 lines
                f.write(f"   {line}\n")

        if result["stderr"]:
            f.write(f"\n   STDERR:\n")
            for line in result["stderr"].split("\n")[:50]:
                f.write(f"   {line}\n")

        f.write("\n")

    def run(self):
        """Execute complete workflow"""
        print("\n" + "=" * 80)
        print("HypatiaX Workflow Runner")
        print("=" * 80)
        print(f"Base Path: {self.base_path}")
        print(f"Report Directory: {self.report_dir}")
        print(f"Execution Order: {' → '.join(self.execution_order)}")
        print("=" * 80 + "\n")

        start_time = time.time()

        # Process each module in order
        for module_name in self.execution_order:
            module_result = self.process_module(module_name)
            self.results["modules"][module_name] = module_result

            # Generate individual module reports
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # JSON report
            json_path = self.report_dir / f"{module_name}_{timestamp}.json"
            with open(json_path, "w") as f:
                json.dump(module_result, f, indent=2)

            # Text report
            txt_path = self.report_dir / f"{module_name}_{timestamp}.txt"
            self.generate_text_report(module_result, txt_path)

            print(f"\n✓ Reports saved:")
            print(f"  - {json_path}")
            print(f"  - {txt_path}")

        # Generate master summary report
        total_time = time.time() - start_time
        self.results["total_duration"] = round(total_time, 2)
        self._generate_master_report()

        print("\n" + "=" * 80)
        print("WORKFLOW COMPLETE")
        print("=" * 80)
        print(f"Total Duration: {total_time:.2f}s")
        print(f"Reports Directory: {self.report_dir}")

    def _generate_master_report(self):
        """Generate master summary report for all modules"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON master report
        json_path = self.report_dir / f"master_report_{timestamp}.json"
        with open(json_path, "w") as f:
            json.dump(self.results, f, indent=2)

        # Text master report
        txt_path = self.report_dir / f"master_report_{timestamp}.txt"
        with open(txt_path, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("HypatiaX Master Workflow Report\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Timestamp: {self.results['timestamp']}\n")
            f.write(f"Base Path: {self.results['base_path']}\n")
            f.write(f"Total Duration: {self.results['total_duration']}s\n\n")

            f.write("MODULE SUMMARIES\n")
            f.write("-" * 80 + "\n\n")

            overall = {
                "total_files": 0,
                "successful": 0,
                "failed": 0,
                "errors": 0,
                "timeouts": 0,
            }

            for module_name in self.execution_order:
                module = self.results["modules"].get(module_name, {})
                summary = module.get("summary", {})

                f.write(f"{module_name.upper()}\n")
                f.write(f"  Total Files: {summary.get('total_files', 0)}\n")
                f.write(f"  Successful: {summary.get('successful', 0)}\n")
                f.write(f"  Failed: {summary.get('failed', 0)}\n")
                f.write(f"  Errors: {summary.get('errors', 0)}\n")
                f.write(f"  Timeouts: {summary.get('timeouts', 0)}\n")
                f.write(f"  Duration: {summary.get('total_duration', 0):.2f}s\n\n")

                for key in overall:
                    overall[key] += summary.get(key, 0)

            f.write("\nOVERALL SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Files Executed: {overall['total_files']}\n")
            f.write(f"Total Successful: {overall['successful']}\n")
            f.write(f"Total Failed: {overall['failed']}\n")
            f.write(f"Total Errors: {overall['errors']}\n")
            f.write(f"Total Timeouts: {overall['timeouts']}\n")
            f.write(
                f"Success Rate: {(overall['successful']/overall['total_files']*100) if overall['total_files'] > 0 else 0:.1f}%\n"
            )

        print(f"\n✓ Master reports saved:")
        print(f"  - {json_path}")
        print(f"  - {txt_path}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="HypatiaX Workflow Runner - Execute tests and scripts with reporting"
    )
    parser.add_argument(
        "--base-path",
        default=".",
        help="Base path to HypatiaX project (default: current directory)",
    )
    parser.add_argument(
        "--modules", nargs="+", help="Specific modules to run (default: all in order)"
    )

    args = parser.parse_args()

    runner = WorkflowRunner(args.base_path)

    if args.modules:
        # Override execution order with specified modules
        runner.execution_order = args.modules

    try:
        runner.run()
    except KeyboardInterrupt:
        print("\n\n⚠ Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Workflow failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

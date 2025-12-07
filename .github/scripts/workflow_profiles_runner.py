#!/usr/bin/env python3
"""
HypatiaX Workflow Runner for GitHub Actions
Executes all tests and scripts across directories in specified order
Generates comprehensive reports for each execution

Updated to match actual HypatiaX architecture with:
- agents/ (base, coordinators, learning, memory, specialists, workflows)
- tools/ (formal, llm_providers, numerical, symbolic, transformers, validation, visualization)
- model_implementations/ (agents, llm, ner, transformers)
- tests/ (unit, integration, e2e)
"""

import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class WorkflowRunner:
    """Execute tests and scripts across HypatiaX project with reporting"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
        self.report_dir = self.base_path / "workflow_reports"
        self.report_dir.mkdir(exist_ok=True)

        # Execution order profiles for different workflows
        self.execution_profiles = {
            # NER-focused workflow (original)
            "ner": [
                "config",  # Configuration first
                "datasets",  # Data preparation
                "patterns",  # Pattern definitions
                "custom_entities",  # Custom entity definitions
                "custom_ner",  # Custom NER components
                "data_spacy",  # SpaCy data processing
                "mappings",  # Mappings and schemas
                "models",  # Base models
                "model_implementations",  # Model implementations (ner, llm, transformers, agents)
                "core",  # Core training/evaluation/deployment
                "tools",  # Tools (formal, numerical, symbolic, llm_providers, etc.)
                "agents",  # Agent systems (base, coordinators, specialists, workflows)
                "utils",  # Utilities
                "scripts_",  # Scripts
                "experiments",  # Experiments
                "tests",  # All tests (unit, integration, e2e)
            ],
            # LLM-focused workflow (optimized for language models)
            "llm": [
                "config",  # 1. Configuration first
                "datasets",  # 2. Data preparation (raw data collection)
                "utils",  # 3. Utilities (preprocessing helpers)
                "tools",  # 4. Tools (llm_providers, validation, formal, numerical)
                "mappings",  # 5. Mappings and schemas
                "models",  # 6. Base model definitions
                "model_implementations",  # 7. LLM implementations (llm/, transformers/)
                "agents",  # 8. Agent systems (coordinators, specialists for LLM orchestration)
                "core",  # 9. Training/evaluation/deployment
                "experiments",  # 10. Experiments (fine-tuning, prompt engineering)
                "scripts_",  # 11. Scripts (deployment, batch processing)
                "tests",  # 12. Tests (unit, integration, e2e)
            ],
            # Agent-focused workflow (multi-agent systems)
            "agents": [
                "config",  # 1. Configuration
                "datasets",  # 2. Data preparation
                "tools",  # 3. Tools (llm_providers, validation)
                "utils",  # 4. Utilities
                "models",  # 5. Base models
                "model_implementations",  # 6. Agent model implementations
                "agents",  # 7. Agent systems (base, coordinators, specialists, workflows)
                "core",  # 8. Core functionality
                "experiments",  # 9. Agent experiments
                "scripts_",  # 10. Scripts
                "tests",  # 11. Tests
            ],
            # Transformer-focused workflow
            "transformers": [
                "config",  # 1. Configuration
                "datasets",  # 2. Data preparation
                "utils",  # 3. Utilities
                "mappings",  # 4. Mappings
                "tools",  # 5. Tools (transformers, validation)
                "models",  # 6. Base models
                "model_implementations",  # 7. Transformer implementations
                "core",  # 8. Training/evaluation
                "experiments",  # 9. Experiments
                "scripts_",  # 10. Scripts
                "tests",  # 11. Tests
            ],
        }

        # Default to NER workflow for backward compatibility
        self.execution_order = self.execution_profiles["ner"]

        # Define which directories contain tests vs scripts
        self.test_directories = {
            "tests",  # Main test directory
        }

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_path": str(self.base_path),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "modules": {},
            "architecture_notes": {
                "agents": "Multi-agent system with coordinators, specialists, and workflows",
                "tools": "Formal, numerical, symbolic, transformers, validation, visualization",
                "model_implementations": "Implementations for agents, llm, ner, transformers",
                "tests": "Unit, integration, and end-to-end tests",
            },
        }

        # GitHub Actions specific
        self.is_github_actions = os.getenv("GITHUB_ACTIONS") == "true"

    def log(self, message: str, level: str = "info"):
        """Log with GitHub Actions annotations support"""
        print(message)

        if self.is_github_actions:
            if level == "error":
                print(f"::error::{message}")
            elif level == "warning":
                print(f"::warning::{message}")
            elif level == "notice":
                print(f"::notice::{message}")

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

            # Skip backup files and hidden files
            if item.name.endswith("~") or item.name.startswith("#") or item.name.startswith("."):
                continue

            # Skip backup_before_extension directory
            if "backup_before_extension" in str(item):
                continue

            # Categorize by filename pattern or directory
            parent_name = item.parent.name

            # Files in tests/ directory or test_ prefix
            if (
                item.name.startswith("test_")
                or item.name.startswith("Test_")
                or "tests" in str(item.parent)
                or parent_name in ["unit", "integration", "e2e"]
            ):
                tests.append(item)

            # Script files
            elif (
                item.name.startswith("script_")
                or "script" in item.name.lower()
                or parent_name in ["scripts_", "migration"]
            ):
                scripts.append(item)

            # Training, evaluation, deployment files
            elif any(
                x in item.name.lower()
                for x in ["run_", "train", "evaluate", "deploy", "workflow", "pipeline", "proc_time"]
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

        self.log(f"\n{'='*80}")
        self.log(f"Executing: {result['file']}")
        self.log(f"Type: {file_type}")
        self.log(f"{'='*80}")

        # GitHub Actions grouping
        if self.is_github_actions:
            print(f"::group::Executing {result['file']}")

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
                self.log(f"✓ SUCCESS", "notice")
            else:
                result["status"] = "failed"
                self.log(f"✗ FAILED (return code: {proc.returncode})", "warning")
                if proc.stderr:
                    stderr_preview = proc.stderr[:500]
                    self.log(f"STDERR: {stderr_preview}", "warning")

        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["error"] = "Execution timeout (5 minutes)"
            self.log(f"⏱ TIMEOUT", "warning")

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
            self.log(f"⚠ ERROR: {e}", "error")

        finally:
            end = time.time()
            result["end_time"] = datetime.now().isoformat()
            result["duration"] = round(end - start, 2)
            self.log(f"Duration: {result['duration']}s")

            if self.is_github_actions:
                print("::endgroup::")

        return result

    def process_module(self, module_name: str) -> Dict:
        """Process all tests and scripts in a module"""
        self.log(f"\n{'#'*80}")
        self.log(f"# MODULE: {module_name.upper()}")
        self.log(f"{'#'*80}")

        if self.is_github_actions:
            print(f"::group::Module: {module_name}")

        module_path = self.base_path / module_name
        module_result = {
            "module": module_name,
            "path": str(module_path.relative_to(self.base_path)) if module_path.exists() else module_name,
            "exists": module_path.exists(),
            "is_test_directory": module_name in self.test_directories,
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
            self.log(f"⚠ Module not found: {module_path}", "warning")
            if self.is_github_actions:
                print("::endgroup::")
            return module_result

        # Find all executable files
        tests, scripts = self.find_executable_files(module_path)

        self.log(f"\nFound {len(tests)} test files")
        self.log(f"Found {len(scripts)} script files")

        # For test directories, prioritize tests
        if module_name in self.test_directories:
            # Execute tests first
            for test_file in tests:
                result = self.execute_file(test_file, "test")
                module_result["tests"].append(result)
                self._update_summary(module_result["summary"], result)

            # Scripts are less common in test directories
            for script_file in scripts:
                result = self.execute_file(script_file, "script")
                module_result["scripts"].append(result)
                self._update_summary(module_result["summary"], result)
        else:
            # For other directories, execute in order found
            for test_file in tests:
                result = self.execute_file(test_file, "test")
                module_result["tests"].append(result)
                self._update_summary(module_result["summary"], result)

            for script_file in scripts:
                result = self.execute_file(script_file, "script")
                module_result["scripts"].append(result)
                self._update_summary(module_result["summary"], result)

        # Log module summary
        summary = module_result["summary"]
        self.log(f"\nModule Summary:")
        self.log(
            f"  Total: {summary['total_files']}, Success: {summary['successful']}, "
            f"Failed: {summary['failed']}, Errors: {summary['errors']}, "
            f"Timeouts: {summary['timeouts']}"
        )

        if self.is_github_actions:
            print("::endgroup::")

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
            f.write(f"Python Version: {self.results['python_version']}\n")
            f.write(f"Platform: {self.results['platform']}\n")
            f.write(f"Module Path: {module_result['path']}\n")
            f.write(f"Module Exists: {module_result['exists']}\n")
            f.write(f"Is Test Directory: {module_result['is_test_directory']}\n\n")

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
        status_symbol = {"success": "✓", "failed": "✗", "error": "⚠", "timeout": "⏱", "not_run": "○"}.get(
            result["status"], "?"
        )

        f.write(f"\n{status_symbol} {result['file']}\n")
        f.write(f"   Status: {result['status'].upper()}\n")
        f.write(f"   Duration: {result['duration']}s\n")

        if result.get("return_code") is not None:
            f.write(f"   Return Code: {result['return_code']}\n")

        if result.get("error"):
            f.write(f"   Error: {result['error']}\n")

        if result["stdout"]:
            f.write(f"\n   STDOUT (first 50 lines):\n")
            for line in result["stdout"].split("\n")[:50]:
                f.write(f"   {line}\n")

        if result["stderr"]:
            f.write(f"\n   STDERR (first 50 lines):\n")
            for line in result["stderr"].split("\n")[:50]:
                f.write(f"   {line}\n")

        f.write("\n")

    def run(self, modules: Optional[List[str]] = None):
        """Execute complete workflow"""
        self.log("\n" + "=" * 80)
        self.log("HypatiaX Workflow Runner")
        self.log("=" * 80)
        self.log(f"Base Path: {self.base_path}")
        self.log(f"Report Directory: {self.report_dir}")
        self.log(f"Python Version: {self.results['python_version']}")
        self.log(f"Platform: {self.results['platform']}")

        # Use custom modules if provided, otherwise use default order
        execution_list = modules if modules else self.execution_order
        self.log(f"Execution Order: {' → '.join(execution_list)}")
        self.log("=" * 80 + "\n")

        start_time = time.time()

        # Process each module in order
        for module_name in execution_list:
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

            self.log(f"\n✓ Reports saved:")
            self.log(f"  - {json_path}")
            self.log(f"  - {txt_path}")

        # Generate master summary report
        total_time = time.time() - start_time
        self.results["total_duration"] = round(total_time, 2)
        self._generate_master_report()

        self.log("\n" + "=" * 80)
        self.log("WORKFLOW COMPLETE")
        self.log("=" * 80)
        self.log(f"Total Duration: {total_time:.2f}s")
        self.log(f"Reports Directory: {self.report_dir}")

        # Calculate overall success
        total_files = sum(m["summary"]["total_files"] for m in self.results["modules"].values())
        failed = sum(m["summary"]["failed"] for m in self.results["modules"].values())
        errors = sum(m["summary"]["errors"] for m in self.results["modules"].values())

        if failed > 0 or errors > 0:
            self.log(f"\n⚠ Workflow completed with {failed} failures and {errors} errors", "warning")
            return 1
        else:
            self.log(f"\n✓ All {total_files} files executed successfully", "notice")
            return 0

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
            f.write(f"Python Version: {self.results['python_version']}\n")
            f.write(f"Platform: {self.results['platform']}\n")
            f.write(f"Total Duration: {self.results['total_duration']}s\n\n")

            f.write("ARCHITECTURE NOTES\n")
            f.write("-" * 80 + "\n")
            for key, note in self.results.get("architecture_notes", {}).items():
                f.write(f"{key}: {note}\n")
            f.write("\n")

            f.write("MODULE SUMMARIES\n")
            f.write("-" * 80 + "\n\n")

            overall = {"total_files": 0, "successful": 0, "failed": 0, "errors": 0, "timeouts": 0}

            for module_name, module in self.results.get("modules", {}).items():
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
            if overall["total_files"] > 0:
                f.write(f"Success Rate: {(overall['successful']/overall['total_files']*100):.1f}%\n")

        self.log(f"\n✓ Master reports saved:")
        self.log(f"  - {json_path}")
        self.log(f"  - {txt_path}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="HypatiaX Workflow Runner - Execute tests and scripts with reporting")
    parser.add_argument("--base-path", default=".", help="Base path to HypatiaX project (default: current directory)")
    parser.add_argument("--modules", nargs="+", help="Specific modules to run (space-separated)")

    args = parser.parse_args()

    runner = WorkflowRunner(args.base_path)

    try:
        exit_code = runner.run(modules=args.modules)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Workflow failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

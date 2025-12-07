#!/usr/bin/env python3
"""
HypatiaX Hybrid Workflow Runner for GitHub Actions
Combines the best of both versions with full backward compatibility

Features from Version 2 (Priority):
- Multiple execution profiles (NER, LLM, agents, transformers)
- Architecture notes and documentation
- Better file detection and filtering
- Test directory awareness
- Flexible module organization

Features from Version 1 (Preserved):
- Simple default execution order
- Clean reporting structure
- Robust error handling
"""

import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class WorkflowRunner:
    """Execute tests and scripts across HypatiaX project with comprehensive reporting"""

    def __init__(self, base_path: str = ".", profile: str = "auto"):
        self.base_path = Path(base_path).resolve()
        self.report_dir = self.base_path / "workflow_reports"
        self.report_dir.mkdir(exist_ok=True)

        # Execution order profiles for different workflows
        self.execution_profiles = {
            # NER-focused workflow (original Version 1 structure)
            "ner": [
                "config",
                "datasets",
                "patterns",
                "custom_entities",
                "custom_ner",
                "data_spacy",
                "mappings",
                "models",
                "model_implementations",
                "core",
                "tools",
                "agents",
                "utils",
                "scripts_",
                "experiments",
                "tests",
            ],
            # LLM-focused workflow (optimized for language models)
            "llm": [
                "config",
                "datasets",
                "utils",
                "tools",
                "mappings",
                "models",
                "model_implementations",
                "agents",
                "core",
                "experiments",
                "scripts_",
                "tests",
            ],
            # Agent-focused workflow (multi-agent systems)
            "agents": [
                "config",
                "datasets",
                "tools",
                "utils",
                "models",
                "model_implementations",
                "agents",
                "core",
                "experiments",
                "scripts_",
                "tests",
            ],
            # Transformer-focused workflow
            "transformers": [
                "config",
                "datasets",
                "utils",
                "mappings",
                "tools",
                "models",
                "model_implementations",
                "core",
                "experiments",
                "scripts_",
                "tests",
            ],
            # Simple/Legacy workflow (Version 1 compatibility)
            "legacy": ["datasets", "patterns", "custom_ner", "data_spacy", "models", "core", "mappings", "scripts_"],
        }

        # Auto-detect best profile or use specified
        self.profile = self._detect_profile() if profile == "auto" else profile
        self.execution_order = self.execution_profiles.get(self.profile, self.execution_profiles["ner"])

        # Define which directories contain tests vs scripts
        self.test_directories: Set[str] = {
            "tests",
            "test",
        }

        # Architecture detection and notes
        self.architecture_info = self._detect_architecture()

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_path": str(self.base_path),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "profile": self.profile,
            "detected_architecture": self.architecture_info,
            "modules": {},
        }

        # GitHub Actions specific
        self.is_github_actions = os.getenv("GITHUB_ACTIONS") == "true"

    def _detect_architecture(self) -> Dict[str, any]:
        """Detect project architecture and provide notes"""
        arch_info = {
            "type": "unknown",
            "has_agents": False,
            "has_tools": False,
            "has_model_implementations": False,
            "has_tests_dir": False,
            "notes": {},
        }

        # Check for key directories
        if (self.base_path / "agents").exists():
            arch_info["has_agents"] = True
            subdirs = [d.name for d in (self.base_path / "agents").iterdir() if d.is_dir()]
            arch_info["notes"]["agents"] = f"Multi-agent system: {', '.join(subdirs)}"

        if (self.base_path / "tools").exists():
            arch_info["has_tools"] = True
            subdirs = [d.name for d in (self.base_path / "tools").iterdir() if d.is_dir()]
            arch_info["notes"]["tools"] = f"Tool modules: {', '.join(subdirs)}"

        if (self.base_path / "model_implementations").exists():
            arch_info["has_model_implementations"] = True
            subdirs = [d.name for d in (self.base_path / "model_implementations").iterdir() if d.is_dir()]
            arch_info["notes"]["model_implementations"] = f"Implementations: {', '.join(subdirs)}"

        if (self.base_path / "tests").exists():
            arch_info["has_tests_dir"] = True
            subdirs = [d.name for d in (self.base_path / "tests").iterdir() if d.is_dir()]
            arch_info["notes"]["tests"] = f"Test structure: {', '.join(subdirs)}"

        # Determine architecture type
        if arch_info["has_agents"] and arch_info["has_tools"]:
            arch_info["type"] = "full_multi_component"
        elif arch_info["has_agents"]:
            arch_info["type"] = "agent_focused"
        elif arch_info["has_model_implementations"]:
            arch_info["type"] = "model_focused"
        elif (self.base_path / "custom_ner").exists():
            arch_info["type"] = "ner_focused"
        else:
            arch_info["type"] = "simple"

        return arch_info

    def _detect_profile(self) -> str:
        """Auto-detect the best execution profile based on project structure"""
        arch = self._detect_architecture()

        # Priority order: agents > llm > transformers > ner > legacy
        if arch["has_agents"] and arch["has_tools"]:
            if (self.base_path / "model_implementations" / "llm").exists():
                return "llm"
            return "agents"

        if (self.base_path / "model_implementations" / "transformers").exists():
            return "transformers"

        if (self.base_path / "custom_ner").exists() or (self.base_path / "data_spacy").exists():
            return "ner"

        # Check for legacy structure (Version 1)
        legacy_dirs = ["datasets", "patterns", "custom_ner", "data_spacy"]
        if all((self.base_path / d).exists() for d in legacy_dirs[:2]):
            return "legacy"

        return "ner"  # Default fallback

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
        """Find all test files and script files in directory with smart filtering"""
        tests = []
        scripts = []

        if not directory.exists():
            return tests, scripts

        # Files and patterns to exclude
        exclude_patterns = {
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
            "backup_before_extension",
            ".backup",
            "node_modules",
            "venv",
            ".venv",
        }

        for item in directory.rglob("*.py"):
            # Skip if in excluded directory
            if any(pattern in str(item) for pattern in exclude_patterns):
                continue

            # Skip __init__.py
            if item.name == "__init__.py":
                continue

            # Skip backup and hidden files
            if (
                item.name.endswith("~")
                or item.name.endswith(".bak")
                or item.name.startswith("#")
                or item.name.startswith(".")
            ):
                continue

            # Get parent directory name for context
            parent_name = item.parent.name
            rel_path = str(item.relative_to(directory))

            # Categorize files
            is_test = False
            is_script = False

            # Test file detection (high priority)
            if (
                item.name.startswith("test_")
                or item.name.startswith("Test_")
                or item.name.endswith("_test.py")
                or "tests" in rel_path
                or parent_name in ["unit", "integration", "e2e", "functional"]
            ):
                is_test = True

            # Script file detection
            elif (
                item.name.startswith("script_")
                or item.name.startswith("run_")
                or "script" in item.name.lower()
                or parent_name in ["scripts", "scripts_", "migration", "deploy"]
            ):
                is_script = True

            # Training/evaluation/workflow files
            elif any(
                keyword in item.name.lower()
                for keyword in [
                    "train",
                    "training",
                    "evaluate",
                    "evaluation",
                    "deploy",
                    "deployment",
                    "workflow",
                    "pipeline",
                    "proc_time",
                    "benchmark",
                    "experiment",
                ]
            ):
                is_script = True

            # Add to appropriate list
            if is_test:
                tests.append(item)
            elif is_script:
                scripts.append(item)
            # Else: ignore files that don't match patterns

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
        is_test_dir = module_name in self.test_directories

        module_result = {
            "module": module_name,
            "path": str(module_path.relative_to(self.base_path)) if module_path.exists() else module_name,
            "exists": module_path.exists(),
            "is_test_directory": is_test_dir,
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

        # Execute tests first (always)
        for test_file in tests:
            result = self.execute_file(test_file, "test")
            module_result["tests"].append(result)
            self._update_summary(module_result["summary"], result)

        # Then execute scripts
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
            f.write(f"Profile: {self.profile}\n")
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
        self.log("HypatiaX Hybrid Workflow Runner")
        self.log("=" * 80)
        self.log(f"Base Path: {self.base_path}")
        self.log(f"Report Directory: {self.report_dir}")
        self.log(f"Python Version: {self.results['python_version']}")
        self.log(f"Platform: {self.results['platform']}")
        self.log(f"Profile: {self.profile}")
        self.log(f"Architecture Type: {self.architecture_info['type']}")

        # Use custom modules if provided, otherwise use detected profile order
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
            f.write(f"Profile Used: {self.profile}\n")
            f.write(f"Total Duration: {self.results['total_duration']}s\n\n")

            # Architecture information
            arch = self.results.get("detected_architecture", {})
            f.write("DETECTED ARCHITECTURE\n")
            f.write("-" * 80 + "\n")
            f.write(f"Type: {arch.get('type', 'unknown')}\n")
            f.write(f"Has Agents: {arch.get('has_agents', False)}\n")
            f.write(f"Has Tools: {arch.get('has_tools', False)}\n")
            f.write(f"Has Model Implementations: {arch.get('has_model_implementations', False)}\n")
            f.write(f"Has Tests Directory: {arch.get('has_tests_dir', False)}\n\n")

            if arch.get("notes"):
                f.write("Architecture Notes:\n")
                for key, note in arch["notes"].items():
                    f.write(f"  {key}: {note}\n")
                f.write("\n")

            f.write("MODULE SUMMARIES\n")
            f.write("-" * 80 + "\n\n")

            overall = {"total_files": 0, "successful": 0, "failed": 0, "errors": 0, "timeouts": 0}

            for module_name, module in self.results.get("modules", {}).items():
                summary = module.get("summary", {})

                f.write(f"{module_name.upper()}\n")
                f.write(f"  Path: {module.get('path', 'N/A')}\n")
                f.write(f"  Exists: {module.get('exists', False)}\n")
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
                success_rate = overall["successful"] / overall["total_files"] * 100
                f.write(f"Success Rate: {success_rate:.1f}%\n")

        self.log(f"\n✓ Master reports saved:")
        self.log(f"  - {json_path}")
        self.log(f"  - {txt_path}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="HypatiaX Hybrid Workflow Runner - Execute tests and scripts with comprehensive reporting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect profile and run all modules
  python workflow_runner.py

  # Use specific profile
  python workflow_runner.py --profile llm

  # Run specific modules only
  python workflow_runner.py --modules datasets models tests

  # Combine profile with specific modules
  python workflow_runner.py --profile agents --modules agents tools tests

Available profiles: ner, llm, agents, transformers, legacy, auto
        """,
    )
    parser.add_argument("--base-path", default=".", help="Base path to HypatiaX project (default: current directory)")
    parser.add_argument("--modules", nargs="+", help="Specific modules to run (space-separated, overrides profile)")
    parser.add_argument(
        "--profile",
        default="auto",
        choices=["auto", "ner", "llm", "agents", "transformers", "legacy"],
        help="Execution profile to use (default: auto-detect)",
    )
    parser.add_argument("--list-profiles", action="store_true", help="List available profiles and exit")

    args = parser.parse_args()

    # List profiles if requested
    if args.list_profiles:
        print("\nAvailable Execution Profiles:\n")
        runner = WorkflowRunner(args.base_path, profile="auto")
        for profile_name, modules in runner.execution_profiles.items():
            print(f"{profile_name}:")
            print(f"  Modules: {' → '.join(modules)}")
            print()
        print(f"Auto-detected profile for current project: {runner.profile}")
        print(f"Architecture type: {runner.architecture_info['type']}\n")
        return 0

    # Create runner with specified profile
    runner = WorkflowRunner(args.base_path, profile=args.profile)

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

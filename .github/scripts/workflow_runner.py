#!/usr/bin/env python3
"""
HypatiaX Workflow Runner
Executes Python scripts from specified modules in order and generates reports.
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class WorkflowRunner:
    """Manages execution of workflow scripts and report generation."""
    
    def __init__(self, base_path: Path, report_dir: Path):
        self.base_path = base_path
        self.report_dir = report_dir
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # Define module execution order
        self.module_order = [
            "datasets",
            "patterns",
            "custom_ner",
            "data_spacy",
            "models",
            "core",
            "mappings",
            "scripts_"
        ]
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "base_path": str(base_path.absolute()),
            "modules": {}
        }
    
    def find_python_files(self, module_path: Path) -> List[Path]:
        """Find all Python files in a module directory."""
        if not module_path.exists():
            return []
        
        python_files = []
        for pattern in ["*.py", "**/*.py"]:
            python_files.extend(module_path.glob(pattern))
        
        # Filter out __init__.py and test files
        python_files = [
            f for f in python_files 
            if f.name != "__init__.py" 
            and not f.name.startswith("test_")
            and not f.name.startswith("_")
        ]
        
        return sorted(python_files)
    
    def execute_script(self, script_path: Path, timeout: int = 300) -> Tuple[bool, str, float]:
        """
        Execute a Python script and return success status, output, and duration.
        
        Args:
            script_path: Path to the Python script
            timeout: Maximum execution time in seconds
        
        Returns:
            Tuple of (success, output, duration)
        """
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**subprocess.os.environ, "PYTHONPATH": str(self.base_path)}
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return True, result.stdout, duration
            else:
                error_output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
                return False, error_output, duration
        
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return False, f"TIMEOUT after {timeout}s", duration
        
        except Exception as e:
            duration = time.time() - start_time
            return False, f"ERROR: {str(e)}", duration
    
    def run_module(self, module_name: str) -> Dict:
        """
        Run all scripts in a module and return results.
        
        Args:
            module_name: Name of the module directory
        
        Returns:
            Dictionary containing module execution results
        """
        module_path = self.base_path / module_name
        
        print(f"\n{'='*80}")
        print(f"MODULE: {module_name}")
        print(f"{'='*80}")
        
        if not module_path.exists():
            print(f"⚠️  Module directory not found: {module_path}")
            return {
                "path": str(module_path),
                "exists": False,
                "files": [],
                "summary": {
                    "total_files": 0,
                    "successful": 0,
                    "failed": 0,
                    "errors": 0,
                    "timeouts": 0
                }
            }
        
        python_files = self.find_python_files(module_path)
        
        if not python_files:
            print(f"ℹ️  No Python files found in {module_name}")
            return {
                "path": str(module_path),
                "exists": True,
                "files": [],
                "summary": {
                    "total_files": 0,
                    "successful": 0,
                    "failed": 0,
                    "errors": 0,
                    "timeouts": 0
                }
            }
        
        print(f"Found {len(python_files)} Python file(s)")
        
        module_results = {
            "path": str(module_path),
            "exists": True,
            "files": [],
            "summary": {
                "total_files": len(python_files),
                "successful": 0,
                "failed": 0,
                "errors": 0,
                "timeouts": 0
            }
        }
        
        for script in python_files:
            relative_path = script.relative_to(self.base_path)
            print(f"\n  Executing: {relative_path}")
            
            success, output, duration = self.execute_script(script)
            
            file_result = {
                "path": str(relative_path),
                "success": success,
                "duration": round(duration, 2),
                "output_length": len(output)
            }
            
            if success:
                print(f"    ✅ SUCCESS ({duration:.2f}s)")
                module_results["summary"]["successful"] += 1
            else:
                print(f"    ❌ FAILED ({duration:.2f}s)")
                module_results["summary"]["failed"] += 1
                
                if "TIMEOUT" in output:
                    module_results["summary"]["timeouts"] += 1
                    file_result["timeout"] = True
                elif "ERROR" in output:
                    module_results["summary"]["errors"] += 1
                    file_result["error"] = True
                
                # Store error output for debugging
                file_result["error_output"] = output[:1000]  # Truncate long outputs
            
            module_results["files"].append(file_result)
        
        return module_results
    
    def generate_reports(self):
        """Generate text and JSON reports of the workflow execution."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate JSON report
        json_path = self.report_dir / f"master_report_{timestamp}.json"
        with open(json_path, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 JSON report saved: {json_path}")
        
        # Generate text report
        txt_path = self.report_dir / f"master_report_{timestamp}.txt"
        with open(txt_path, "w") as f:
            f.write("="*80 + "\n")
            f.write("HYPATIAX WORKFLOW EXECUTION REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Timestamp: {self.results['timestamp']}\n")
            f.write(f"Python Version: {self.results['python_version']}\n")
            f.write(f"Base Path: {self.results['base_path']}\n\n")
            
            # Overall summary
            total_files = sum(m["summary"]["total_files"] for m in self.results["modules"].values())
            total_success = sum(m["summary"]["successful"] for m in self.results["modules"].values())
            total_failed = sum(m["summary"]["failed"] for m in self.results["modules"].values())
            total_errors = sum(m["summary"]["errors"] for m in self.results["modules"].values())
            total_timeouts = sum(m["summary"]["timeouts"] for m in self.results["modules"].values())
            
            f.write("OVERALL SUMMARY\n")
            f.write("-"*80 + "\n")
            f.write(f"Total Files: {total_files}\n")
            f.write(f"Successful: {total_success}\n")
            f.write(f"Failed: {total_failed}\n")
            f.write(f"Errors: {total_errors}\n")
            f.write(f"Timeouts: {total_timeouts}\n")
            
            if total_files > 0:
                success_rate = (total_success / total_files) * 100
                f.write(f"Success Rate: {success_rate:.1f}%\n")
            
            f.write("\n")
            
            # Module details
            for module_name, module_data in self.results["modules"].items():
                f.write("\n" + "="*80 + "\n")
                f.write(f"MODULE: {module_name.upper()}\n")
                f.write("="*80 + "\n")
                f.write(f"Path: {module_data['path']}\n")
                f.write(f"Exists: {module_data['exists']}\n")
                
                summary = module_data["summary"]
                f.write(f"\nSummary:\n")
                f.write(f"  Total Files: {summary['total_files']}\n")
                f.write(f"  Successful: {summary['successful']}\n")
                f.write(f"  Failed: {summary['failed']}\n")
                f.write(f"  Errors: {summary['errors']}\n")
                f.write(f"  Timeouts: {summary['timeouts']}\n")
                
                if module_data["files"]:
                    f.write(f"\nFiles:\n")
                    for file_info in module_data["files"]:
                        status = "✅" if file_info["success"] else "❌"
                        f.write(f"  {status} {file_info['path']} ({file_info['duration']}s)\n")
                        
                        if not file_info["success"] and "error_output" in file_info:
                            f.write(f"      Error: {file_info['error_output'][:200]}...\n")
        
        print(f"📄 Text report saved: {txt_path}")
    
    def run_workflow(self, modules: Optional[List[str]] = None):
 	"""
        Run the complete workflow.
        
        Args:
            modules: List of specific modules to run. If None, run all modules
        """
        if modules:
            modules_to_run = [m for m in self.module_order if m in modules]
        else:
            modules_to_run = self.module_order
        
        print("\n" + "="*80)
        print("STARTING HYPATIAX WORKFLOW")
        print("="*80)
        print(f"Python Version: {self.results['python_version']}")
        print(f"Base Path: {self.base_path}")
        print(f"Modules to execute: {', '.join(modules_to_run)}")
        
        workflow_start = time.time()
        
        for module_name in modules_to_run:
            module_results = self.run_module(module_name)
            self.results["modules"][module_name] = module_results
        
        workflow_duration = time.time() - workflow_start
        self.results["total_duration"] = round(workflow_duration, 2)
        
        print("\n" + "="*80)
        print("WORKFLOW COMPLETE")
        print("="*80)
        print(f"Total Duration: {workflow_duration:.2f}s")
        
        # Print summary
        total_files = sum(m["summary"]["total_files"] for m in self.results["modules"].values())
        total_success = sum(m["summary"]["successful"] for m in self.results["modules"].values())
        total_failed = sum(m["summary"]["failed"] for m in self.results["modules"].values())
        
        print(f"\nTotal Files Executed: {total_files}")
        print(f"Successful: {total_success}")
        print(f"Failed: {total_failed}")
        
        if total_files > 0:
            success_rate = (total_success / total_files) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        # Generate reports
        self.generate_reports()


def main():
    """Main entry point for the workflow runner."""
    parser = argparse.ArgumentParser(
        description="HypatiaX Workflow Runner - Execute Python scripts from specified modules"
    )
    
    parser.add_argument(
        "base_path",
        type=Path,
        help="Base directory containing the module folders"
    )
    
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path("reports"),
        help="Directory to save execution reports (default: ./reports)"
    )
    
    parser.add_argument(
        "--modules",
        nargs="+",
        help="Specific modules to run (default: all modules in order)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout for each script execution in seconds (default: 300)"
    )
    
    args = parser.parse_args()
    
    # Validate base path
    if not args.base_path.exists():
        print(f"❌ Error: Base path does not exist: {args.base_path}")
        sys.exit(1)
    
    if not args.base_path.is_dir():
        print(f"❌ Error: Base path is not a directory: {args.base_path}")
        sys.exit(1)
    
    # Create and run workflow
    runner = WorkflowRunner(args.base_path, args.report_dir)
    
    try:
        runner.run_workflow(modules=args.modules)
        print("\n✅ Workflow execution completed successfully!")
        sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        runner.generate_reports()
        sys.exit(130)
    
    except Exception as e:
        print(f"\n❌ Workflow failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
HypatiaX Workflow Runner for GitHub Actions
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


class WorkflowRunner:
    """Execute tests and scripts across HypatiaX project with reporting"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
        self.report_dir = self.base_path / "workflow_reports"
        self.report_dir.mkdir(exist_ok=True)
        
        # Execution order as specified
        self.execution_order = [
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
            "base_path": str(self.base_path),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "modules": {}
        }
        
        # GitHub Actions specific
        self.is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        
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
            
            # Skip backup files
            if item.name.endswith("~") or item.name.startswith("#"):
                continue
                
            # Categorize by filename pattern
            if item.name.startswith("test_") or item.name.startswith("Test_"):
                tests.append(item)
            elif item.name.startswith("script_") or "script" in item.name:
                scripts.append(item)
            elif any(x in item.name for x in ["run_time", "proc_time", "evaluate", "training"]):
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
            "error": None
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
                timeout=300  # 5 minute timeout
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
                    self.log(f"STDERR: {proc.stderr[:500]}", "warning")
                
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
            "tests": [],
            "scripts": [],
            "summary": {
                "total_files": 0,
                "successful": 0,
                "failed": 0,
                "errors": 0,
                "timeouts": 0,
                "skipped": 0,
                "total_duration": 0
            }
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
        
        # Log module summary
        summary = module_result["summary"]
        self.log(f"\nModule Summary:")
        self.log(f"  Total: {summary['total_files']}, Success: {summary['successful']}, "
                f"Failed: {summary['failed']}, Errors: {summary['errors']}, "
                f"Timeouts: {summary['timeouts']}")
        
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
        with open(filepath, 'w') as f:
            f.write("="*80 + "\n")
            f.write(f"HypatiaX Workflow Report - {module_result['module'].upper()}\n")
            f.write("="*80 + "\n\n")
            f.write(f"Timestamp: {self.results['timestamp']}\n")
            f.write(f"Python Version: {self.results['python_version']}\n")
            f.write(f"Platform: {self.results['platform']}\n")
            f.write(f"Module Path: {module_result['path']}\n")
            f.write(f"Module Exists: {module_result['exists']}\n\n")
            
            summary = module_result['summary']
            f.write("SUMMARY\n")
            f.write("-"*80 + "\n")
            f.write(f"Total Files Executed: {summary['total_files']}\n")
            f.write(f"Successful: {summary['successful']}\n")
            f.write(f"Failed: {summary['failed']}\n")
            f.write(f"Errors: {summary['errors']}\n")
            f.write(f"Timeouts: {summary['timeouts']}\n")
            f.write(f"Total Duration: {summary['total_duration']:.2f}s\n\n")
            
            # Test Results
            if module_result['tests']:
                f.write("TEST RESULTS\n")
                f.write("-"*80 + "\n")
                for test in module_result['tests']:
                    self._write_execution_detail(f, test)
            
            # Script Results
            if module_result['scripts']:
                f.write("\nSCRIPT RESULTS\n")
                f.write("-"*80 + "\n")
                for script in module_result['scripts']:
                    self._write_execution_detail(f, script)
    
    def _write_execution_detail(self, f, result: Dict):
        """Write detailed execution information"""
        status_symbol = {
            "success": "✓",
            "failed": "✗",
            "error": "⚠",
            "timeout": "⏱",
            "not_run": "○"
        }.get(result["status"], "?")
        
        f.write(f"\n{status_symbol} {result['file']}\n")
        f.write(f"   Status: {result['status'].upper()}\n")
        f.write(f"   Duration: {result['duration']}s\n")
        
        if result.get("return_code") is not None:
            f.write(f"   Return Code: {result['return_code']}\n")
        
        if result.get("error"):
            f.write(f"   Error: {result['error']}\n")
        
        if result["stdout"]:
            f.write(f"\n   STDOUT (first 50 lines):\n")
            for line in result["stdout"].split('\n')[:50]:
                f.write(f"   {line}\n")
        
        if result["stderr"]:
            f.write(f"\n   STDERR (first 50 lines):\n")
            for line in result["stderr"].split('\n')[:50]:
                f.write(f"   {line}\n")
        
        f.write("\n")
    
    def run(self):
        """Execute complete workflow"""
        self.log("\n" + "="*80)
        self.log("HypatiaX Workflow Runner")
        self.log("="*80)
        self.log(f"Base Path: {self.base_path}")
        self.log(f"Report Directory: {self.report_dir}")
        self.log(f"Python Version: {self.results['python_version']}")
        self.log(f"Platform: {self.results['platform']}")
        self.log(f"Execution Order: {' → '.join(self.execution_order)}")
        self.log("="*80 + "\n")
        
        start_time = time.time()
        
        # Process each module in order
        for module_name in self.execution_order:
            module_result = self.process_module(module_name)
            self.results["modules"][module_name] = module_result
            
            # Generate individual module reports
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # JSON report
            json_path = self.report_dir / f"{module_name}_{timestamp}.json"
            with open(json_path, 'w') as f:
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
        
        self.log("\n" + "="*80)
        self.log("WORKFLOW COMPLETE")
        self.log("="*80)
        self.log(f"Total Duration: {total_time:.2f}s")
        self.log(f"Reports Directory: {self.report_dir}")
        
        # Calculate overall success
        total_files = sum(m['summary']['total_files'] for m in self.results['modules'].values())
        failed = sum(m['summary']['failed'] for m in self.results['modules'].values())
        errors = sum(m['summary']['errors'] for m in self.results['modules'].values())
        
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
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Text master report
        txt_path = self.report_dir / f"master_report_{timestamp}.txt"
        with open(txt_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("HypatiaX Master Workflow Report\n")
            f.write("="*80 + "\n\n")
            f.write(f"Timestamp: {self.results['timestamp']}\n")
            f.write(f"Base Path: {self.results['base_path']}\n")
            f.write(f"Python Version: {self.results['python_version']}\n")
            f.write(f"Platform: {self.results['platform']}\n")
            f.write(f"Total Duration: {self.results['total_duration']}s\n\n")
            
            f.write("MODULE SUMMARIES\n")
            f.write("-"*80 + "\n\n")
            
            overall = {
                "total_files": 0,
                "successful": 0,
                "failed": 0,
                "errors": 0,
                "timeouts": 0
            }
            name: HypatiaX Test & Script Workflow

on:
  push:
    branches: [ develop, main ]
  pull_request:
    branches: [ develop, main ]
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:
    inputs:
      modules:
        description: 'Specific modules to run (space-separated, leave empty for all)'
        required: false
        default: ''
      python_version:
        description: 'Python version to use'
        required: false
        default: '3.12'
        type: choice
        options:
          - '3.11'
          - '3.12'
          - '3.13'

env:
  PYTHONUNBUFFERED: 1
  WORKFLOW_REPORTS_DIR: workflow_reports

jobs:
  setup:
    name: Setup and Validate
    runs-on: ubuntu-latest
    outputs:
      python_versions: ${{ steps.set-versions.outputs.versions }}
      modules: ${{ steps.set-modules.outputs.modules }}
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set Python versions
        id: set-versions
        run: |
          if [ -n "${{ github.event.inputs.python_version }}" ]; then
            echo "versions=[\"${{ github.event.inputs.python_version }}\"]" >> $GITHUB_OUTPUT
          else
            echo "versions=[\"3.12\", \"3.13\"]" >> $GITHUB_OUTPUT
          fi

      - name: Set modules to run
        id: set-modules
        run: |
          MODULES="${{ github.event.inputs.modules }}"
          echo "modules=${MODULES}" >> $GITHUB_OUTPUT

      - name: Validate project structure
        run: |
          echo "=== Validating HypatiaX Project Structure ==="
          required_dirs=("datasets" "patterns" "custom_ner" "data_spacy" "models" "core" "mappings" "scripts_")
          missing_dirs=()
          
          for dir in "${required_dirs[@]}"; do
            if [ -d "$dir" ]; then
              echo "✓ Found: $dir"
            else
              echo "⚠ Missing: $dir"
              missing_dirs+=("$dir")
            fi
          done
          
          if [ ${#missing_dirs[@]} -gt 0 ]; then
            echo ""
            echo "Warning: ${#missing_dirs[@]} directories missing"
          else
            echo ""
            echo "✓ All required directories present"
          fi

      - name: Check for workflow runner script
        run: |
          if [ -f ".github/scripts/workflow_runner.py" ]; then
            echo "✓ Workflow runner script found"
          elif [ -f "scripts/workflow_runner.py" ]; then
            echo "✓ Workflow runner script found in scripts/"
          elif [ -f "scripts_/workflow_runner.py" ]; then
            echo "✓ Workflow runner script found in scripts_/"
          else
            echo "⚠ Warning: workflow_runner.py not found in expected locations"
            echo "Script will need to be created or workflow will fail"
          fi

  test-workflow:
    name: Run HypatiaX Workflow - Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest
    needs: setup
    strategy:
      matrix:
        python-version: ${{ fromJson(needs.setup.outputs.python_versions) }}
      fail-fast: false
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
          cache-dependency-path: |
            requirements-py*.txt
            requirements.txt

      - name: Cache spaCy models
        uses: actions/cache@v4
        with:
          path: |
            ~/.spacy
            data_spacy/pre_trained_models
          key: ${{ runner.os }}-spacy-py${{ matrix.python-version }}-${{ hashFiles('requirements-py*.txt') }}
          restore-keys: |
            ${{ runner.os }}-spacy-py${{ matrix.python-version }}-
            ${{ runner.os }}-spacy-

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y --no-install-recommends \
            build-essential \
            python3-dev

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip setuptools wheel
          
          PYVERSION=$(python -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')")
          REQ_FILE="requirements-py${PYVERSION}.txt"
          
          echo "Python version: ${{ matrix.python-version }}"
          echo "Looking for: $REQ_FILE"
          
          if [ -f "$REQ_FILE" ]; then
            echo "Installing from $REQ_FILE"
            pip install -r "$REQ_FILE"
          elif [ -f "requirements.txt" ]; then
            echo "Falling back to requirements.txt"
            pip install -r requirements.txt
          else
            echo "Warning: No requirements file found"
          fi
          
          pip install pytest pytest-cov pytest-timeout pytest-xdist

      - name: Download spaCy models
        run: |
          echo "Downloading spaCy language models..."
          python -m spacy download en_core_web_sm || echo "Warning: Could not download en_core_web_sm"
          python -m spacy download en_core_web_md || echo "Warning: Could not download en_core_web_md"
        continue-on-error: true

      - name: Install project in editable mode
        run: |
          if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
            pip install -e .
          else
            echo "No setup.py or pyproject.toml found, skipping editable install"
          fi
        continue-on-error: true

      - name: Create necessary directories
        run: |
          mkdir -p ${{ env.WORKFLOW_REPORTS_DIR }}
          mkdir -p .github/scripts

      - name: Locate workflow runner script
        id: locate-script
        run: |
          SCRIPT_PATH=""
          
          if [ -f ".github/scripts/workflow_runner.py" ]; then
            SCRIPT_PATH=".github/scripts/workflow_runner.py"
          elif [ -f "scripts/workflow_runner.py" ]; then
            SCRIPT_PATH="scripts/workflow_runner.py"
            cp "scripts/workflow_runner.py" ".github/scripts/workflow_runner.py"
          elif [ -f "scripts_/workflow_runner.py" ]; then
            SCRIPT_PATH="scripts_/workflow_runner.py"
            cp "scripts_/workflow_runner.py" ".github/scripts/workflow_runner.py"
          else
            echo "Error: workflow_runner.py not found"
            exit 1
          fi
          
          echo "script_path=$SCRIPT_PATH" >> $GITHUB_OUTPUT
          echo "Found workflow runner at: $SCRIPT_PATH"

      - name: Run workflow tests
        id: run-workflow
        continue-on-error: true
        timeout-minutes: 45
        run: |
          cd ${{ github.workspace }}
          
          MODULES="${{ needs.setup.outputs.modules }}"
          
          if [ -n "$MODULES" ]; then
            echo "Running specific modules: $MODULES"
            python .github/scripts/workflow_runner.py --base-path . --modules $MODULES
          else
            echo "Running all modules in order"
            python .github/scripts/workflow_runner.py --base-path .
          fi
        env:
          PYTHONPATH: ${{ github.workspace }}

      - name: Check workflow execution status
        if: always()
        run: |
          if [ "${{ steps.run-workflow.outcome }}" == "failure" ]; then
            echo "::warning::Workflow execution encountered failures"
          fi

      - name: Generate workflow summary
        if: always()
        run: |
          echo "## HypatiaX Workflow Results - Python ${{ matrix.python-version }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Status**: ${{ steps.run-workflow.outcome }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          
          if [ -d "${{ env.WORKFLOW_REPORTS_DIR }}" ]; then
            latest_report=$(ls -t ${{ env.WORKFLOW_REPORTS_DIR }}/master_report_*.txt 2>/dev/null | head -1)
            
            if [ -f "$latest_report" ]; then
              echo "### Summary Report" >> $GITHUB_STEP_SUMMARY
              echo '```' >> $GITHUB_STEP_SUMMARY
              head -n 50 "$latest_report" >> $GITHUB_STEP_SUMMARY
              echo '```' >> $GITHUB_STEP_SUMMARY
            else
              echo "⚠️ No master report generated" >> $GITHUB_STEP_SUMMARY
            fi
            
            echo "" >> $GITHUB_STEP_SUMMARY
            echo "### Generated Reports" >> $GITHUB_STEP_SUMMARY
            echo '```' >> $GITHUB_STEP_SUMMARY
            ls -lh ${{ env.WORKFLOW_REPORTS_DIR }}/ 2>/dev/null || echo "No reports found"
            echo '```' >> $GITHUB_STEP_SUMMARY
          else
            echo "⚠️ Reports directory not created" >> $GITHUB_STEP_SUMMARY
          fi

      - name: Parse test results
        if: always()
        id: parse-results
        run: |
          if [ -d "${{ env.WORKFLOW_REPORTS_DIR }}" ]; then
            latest_json=$(ls -t ${{ env.WORKFLOW_REPORTS_DIR }}/master_report_*.json 2>/dev/null | head -1)
            
            if [ -f "$latest_json" ]; then
              python << 'EOFPYTHON'
          import json
          import sys
          import os
          
          try:
              latest_json = "$latest_json"
              with open(latest_json) as f:
                  data = json.load(f)
              
              total = sum(m.get('summary', {}).get('total_files', 0) for m in data.get('modules', {}).values())
              success = sum(m.get('summary', {}).get('successful', 0) for m in data.get('modules', {}).values())
              failed = sum(m.get('summary', {}).get('failed', 0) for m in data.get('modules', {}).values())
              
              with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                  f.write(f"total_files={total}\n")
                  f.write(f"successful={success}\n")
                  f.write(f"failed={failed}\n")
              
              print(f"📊 Results: {success}/{total} successful, {failed} failed")
          except Exception as e:
              print(f"Could not parse results: {e}")
              sys.exit(0)
          EOFPYTHON
            fi
          fi

      - name: Upload workflow reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: workflow-reports-py${{ matrix.python-version }}
          path: ${{ env.WORKFLOW_REPORTS_DIR }}/
          retention-days: 30
          if-no-files-found: warn

      - name: Upload test coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-reports-py${{ matrix.python-version }}
          path: |
            .coverage
            htmlcov/
            coverage.xml
          retention-days: 30
          if-no-files-found: ignore

  analyze-results:
    name: Analyze and Report Results
    runs-on: ubuntu-latest
    needs: test-workflow
    if: always()
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Download all workflow reports
        uses: actions/download-artifact@v4
        with:
          pattern: workflow-reports-*
          path: all-reports/
          merge-multiple: true

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Analyze combined results
        run: |
          python << 'EOFPYTHON'
          import json
          import glob
          from pathlib import Path
          from datetime import datetime
          
          reports_dir = Path("all-reports")
          
          if not reports_dir.exists():
              print("⚠️ No reports found")
              exit(0)
          
          all_results = {
              "total_files": 0,
              "successful": 0,
              "failed": 0,
              "errors": 0,
              "timeouts": 0,
              "by_module": {},
              "by_python_version": {}
          }
          
          report_files = list(reports_dir.glob("master_report_*.json"))
          print(f"Found {len(report_files)} report files")
          
          for report_file in report_files:
              try:
                  with open(report_file) as f:
                      data = json.load(f)
                  
                  python_version = data.get("python_version", "unknown")
                  
                  for module_name, module_data in data.get("modules", {}).items():
                      summary = module_data.get("summary", {})
                      
                      if module_name not in all_results["by_module"]:
                          all_results["by_module"][module_name] = {
                              "total_files": 0,
                              "successful": 0,
                              "failed": 0,
                              "errors": 0,
                              "timeouts": 0
                          }
                      
                      if python_version not in all_results["by_python_version"]:
                          all_results["by_python_version"][python_version] = {
                              "total_files": 0,
                              "successful": 0,
                              "failed": 0
                          }
                      
                      for key in ["total_files", "successful", "failed", "errors", "timeouts"]:
                          value = summary.get(key, 0)
                          all_results[key] += value
                          all_results["by_module"][module_name][key] += value
                          
                          if key in ["total_files", "successful", "failed"]:
                              all_results["by_python_version"][python_version][key] += value
              
              except Exception as e:
                  print(f"⚠️ Error processing {report_file}: {e}")
          
          print("\n" + "="*80)
          print("COMBINED WORKFLOW RESULTS")
          print("="*80)
          print(f"Total Files Executed: {all_results['total_files']}")
          print(f"✅ Successful: {all_results['successful']}")
          print(f"❌ Failed: {all_results['failed']}")
          print(f"⚠️ Errors: {all_results['errors']}")
          print(f"⏱️ Timeouts: {all_results['timeouts']}")
          
          if all_results['total_files'] > 0:
              success_rate = (all_results['successful'] / all_results['total_files']) * 100
              print(f"Success Rate: {success_rate:.1f}%")
          
          if all_results['by_python_version']:
              print("\n" + "-"*80)
              print("By Python Version:")
              print("-"*80)
              for version, stats in sorted(all_results['by_python_version'].items()):
                  if stats['total_files'] > 0:
                      rate = (stats['successful'] / stats['total_files']) * 100
                      print(f"\nPython {version}")
                      print(f"  Total: {stats['total_files']}, Success: {stats['successful']}, Failed: {stats['failed']} ({rate:.1f}%)")
          
          if all_results['by_module']:
              print("\n" + "-"*80)
              print("By Module:")
              print("-"*80)
              for module, stats in sorted(all_results['by_module'].items()):
                  if stats['total_files'] > 0:
                      print(f"\n{module.upper()}")
                      print(f"  Total: {stats['total_files']}, Success: {stats['successful']}, Failed: {stats['failed']}")
          
          all_results["timestamp"] = datetime.now().isoformat()
          with open("combined_results.json", "w") as f:
              json.dump(all_results, f, indent=2)
          
          print("\n" + "="*80)
          print("Results saved to combined_results.json")
          EOFPYTHON

      - name: Upload combined results
        uses: actions/upload-artifact@v4
        with:
          name: combined-workflow-results
          path: combined_results.json
          retention-days: 90

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        continue-on-error: true
        with:
          script: |
            const fs = require('fs');
            
            let comment = '## 🧪 HypatiaX Workflow Test Results\n\n';
            
            try {
              if (!fs.existsSync('combined_results.json')) {
                comment += '⚠️ No results file found\n';
                return;
              }
              
              const results = JSON.parse(fs.readFileSync('combined_results.json', 'utf8'));
              
              comment += '### Summary\n\n';
              comment += `- **Total Files**: ${results.total_files}\n`;
              comment += `- **✅ Successful**: ${results.successful}\n`;
              comment += `- **❌ Failed**: ${results.failed}\n`;
              comment += `- **⚠️ Errors**: ${results.errors}\n`;
              comment += `- **⏱️ Timeouts**: ${results.timeouts}\n`;
              
              if (results.total_files > 0) {
                const successRate = (results.successful / results.total_files * 100).toFixed(1);
                comment += `- **Success Rate**: ${successRate}%\n`;
              }
              
              if (results.by_python_version && Object.keys(results.by_python_version).length > 0) {
                comment += '\n### By Python Version\n\n';
                comment += '| Version | Total | Success | Failed | Rate |\n';
                comment += '|---------|-------|---------|--------|------|\n';
                
                for (const [version, stats] of Object.entries(results.by_python_version)) {
                  const rate = stats.total_files > 0 ? (stats.successful / stats.total_files * 100).toFixed(1) : '0.0';
                  comment += `| ${version} | ${stats.total_files} | ${stats.successful} | ${stats.failed} | ${rate}% |\n`;
                }
              }
              
              if (results.by_module && Object.keys(results.by_module).length > 0) {
                comment += '\n### By Module\n\n';
                comment += '| Module | Total | Success | Failed |\n';
                comment += '|--------|-------|---------|--------|\n';
                
                for (const [module, stats] of Object.entries(results.by_module)) {
                  comment += `| ${module} | ${stats.total_files} | ${stats.successful} | ${stats.failed} |\n`;
                }
              }
              
              comment += '\n📊 Detailed reports are available in the workflow artifacts.\n';
              
            } catch (error) {
              comment += '⚠️ Could not parse test results.\n';
              comment += `Error: ${error.message}\n`;
            }
            
            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });

  notify:
    name: Notify Results
    runs-on: ubuntu-latest
    needs: [test-workflow, analyze-results]
    if: always() && (github.event_name == 'schedule' || github.event_name == 'push')
    
    steps:
      - name: Send notification summary
        run: |
          echo "Workflow completed."
          echo "Test workflow status: ${{ needs.test-workflow.result }}"
          echo "Analysis status: ${{ needs.analyze-results.result }}"
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
            f.write("-"*80 + "\n")
            f.write(f"Total Files Executed: {overall['total_files']}\n")
            f.write(f"Total Successful: {overall['successful']}\n")
            f.write(f"Total Failed: {overall['failed']}\n")
            f.write(f"Total Errors: {overall['errors']}\n")
            f.write(f"Total Timeouts: {overall['timeouts']}\n")
            if overall['total_files'] > 0:
                f.write(f"Success Rate: {(overall['successful']/overall['total_files']*100):.1f}%\n")
        
        self.log(f"\n✓ Master reports saved:")
        self.log(f"  - {json_path}")
        self.log(f"  - {txt_path}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="HypatiaX Workflow Runner - Execute tests and scripts with reporting"
    )
    parser.add_argument(
        "--base-path",
        default=".",
        help="Base path to HypatiaX project (default: current directory)"
    )
    parser.add_argument(
        "--modules",
        nargs="+",
        help="Specific modules to run (default: all in order)"
    )
    
    args = parser.parse_args()
    
    runner = WorkflowRunner(args.base_path)
    
    if args.modules:
        # Override execution order with specified modules
        runner.execution_order = args.modules
    
    try:
        exit_code = runner.run()
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

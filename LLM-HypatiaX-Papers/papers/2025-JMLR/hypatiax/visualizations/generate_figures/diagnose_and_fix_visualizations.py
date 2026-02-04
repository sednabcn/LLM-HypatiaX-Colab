#!/usr/bin/env python3
"""
HypatiaX Visualization Diagnosis and Fix Script
===============================================

Diagnoses why visualization scripts aren't finding data and fixes the issues.

Usage:
    python diagnose_and_fix_visualizations.py [--fix]
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from datetime import datetime

class VisualizationDiagnostic:
    """Diagnoses and fixes visualization script issues"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            current = Path(__file__).resolve()
            while current.parent != current:
                if (current / "hypatiax").exists():
                    project_root = str(current)
                    break
                current = current.parent
        
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.viz_dir = self.project_root / "hypatiax" / "tools" / "visualization"
        self.results_dir = self.project_root / "hypatiax" / "data" / "results"
        self.analysis_dir = self.project_root / "hypatiax" / "data" / "analysis"
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f" {title}")
        print("="*80 + "\n")
    
    def check_script_exists(self, script_name: str) -> Tuple[bool, Path]:
        """Check if script exists and return its path"""
        script_path = self.viz_dir / script_name
        exists = script_path.exists()
        return exists, script_path
    
    def check_data_files(self) -> Dict[str, Dict]:
        """Check what data files exist"""
        self.print_header("DATA FILES INVENTORY")
        
        data_inventory = {
            "hybrid_results": [],
            "llm_results": [],
            "nn_results": [],
            "comparison_results": [],
            "other_json": [],
            "csv_files": [],
            "png_files": []
        }
        
        # Scan results directory
        if self.results_dir.exists():
            for item in self.results_dir.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(self.results_dir)
                    
                    if "hybrid" in str(item).lower() and item.suffix == ".json":
                        data_inventory["hybrid_results"].append(str(rel_path))
                    elif "llm" in str(item).lower() and item.suffix == ".json":
                        data_inventory["llm_results"].append(str(rel_path))
                    elif "nn" in str(item).lower() or "neural" in str(item).lower():
                        data_inventory["nn_results"].append(str(rel_path))
                    elif "comparison" in str(item).lower():
                        data_inventory["comparison_results"].append(str(rel_path))
                    elif item.suffix == ".json":
                        data_inventory["other_json"].append(str(rel_path))
                    elif item.suffix == ".csv":
                        data_inventory["csv_files"].append(str(rel_path))
                    elif item.suffix == ".png":
                        data_inventory["png_files"].append(str(rel_path))
        
        # Print inventory
        for category, files in data_inventory.items():
            count = len(files)
            print(f"{category.replace('_', ' ').title()}: {count} files")
            if count > 0 and count <= 5:
                for f in files:
                    print(f"  • {f}")
            elif count > 5:
                for f in files[:3]:
                    print(f"  • {f}")
                print(f"  ... and {count - 3} more")
        
        return data_inventory
    
    def analyze_master_analyzer(self) -> Dict:
        """Analyze master_analyzer.py to see what it expects"""
        self.print_header("MASTER ANALYZER ANALYSIS")
        
        master_scripts = [
            "master_analyzer.py",
            "enhanced_master_analyzer.py",
            "enhanced_master_analyzer_with_comparison_v6.py"
        ]
        
        found_script = None
        for script_name in master_scripts:
            exists, path = self.check_script_exists(script_name)
            if exists:
                found_script = path
                print(f"✓ Found: {script_name}")
                break
        
        if not found_script:
            print("✗ No master analyzer script found!")
            return {}
        
        # Read and analyze the script
        try:
            with open(found_script, 'r') as f:
                content = f.read()
            
            analysis = {
                "script": found_script.name,
                "expects_scripts": [],
                "expects_dirs": [],
                "expects_files": [],
                "issues": []
            }
            
            # Look for script references
            script_patterns = [
                "generate_tables.py",
                "generate_figures.py",
                "analyze_hybrid_results.py",
                "hypatiax_hybrid_system_visualization.py",
                "hypatiax_visualizer.py"
            ]
            
            for pattern in script_patterns:
                if pattern in content:
                    analysis["expects_scripts"].append(pattern)
            
            # Look for directory references
            dir_patterns = [
                "comparison_results",
                "hybrid_results",
                "baseline_llm",
                "baseline_nn",
                "analysis"
            ]
            
            for pattern in dir_patterns:
                if pattern in content:
                    analysis["expects_dirs"].append(pattern)
            
            # Check for path construction
            if "os.path.join" in content or "Path(" in content:
                print("  Uses path operations")
            
            if "sys.path" in content:
                print("  Modifies Python path")
            
            # Look for how it finds scripts
            if "visualization" in content:
                print("  References visualization directory")
            
            print(f"\n  Expected scripts: {len(analysis['expects_scripts'])}")
            for script in analysis["expects_scripts"]:
                exists, _ = self.check_script_exists(script)
                status = "✓" if exists else "✗"
                print(f"    {status} {script}")
            
            print(f"\n  Expected directories: {len(analysis['expects_dirs'])}")
            for dirname in analysis["expects_dirs"]:
                dir_path = self.results_dir / dirname
                exists = dir_path.exists()
                status = "✓" if exists else "✗"
                print(f"    {status} {dirname}/")
            
            return analysis
            
        except Exception as e:
            print(f"✗ Error analyzing script: {e}")
            return {}
    
    def check_individual_scripts(self) -> Dict[str, Dict]:
        """Check each visualization script for what it needs"""
        self.print_header("INDIVIDUAL SCRIPT REQUIREMENTS")
        
        scripts_to_check = [
            "generate_tables.py",
            "generate_figures.py",
            "analyze_hybrid_results.py",
            "hypatiax_hybrid_system_visualization.py",
            "hypatiax_visualizer.py"
        ]
        
        results = {}
        
        for script_name in scripts_to_check:
            exists, script_path = self.check_script_exists(script_name)
            
            if not exists:
                print(f"✗ {script_name} - NOT FOUND")
                results[script_name] = {"exists": False}
                continue
            
            print(f"\n✓ {script_name}")
            
            try:
                with open(script_path, 'r') as f:
                    content = f.read()
                
                # Look for data requirements
                requirements = {
                    "exists": True,
                    "requires_comparison": "comparison_results" in content,
                    "requires_hybrid": "hybrid" in content.lower(),
                    "requires_baseline": "baseline" in content.lower(),
                    "reads_json": ".json" in content,
                    "reads_csv": ".csv" in content,
                    "creates_png": ".png" in content or "savefig" in content,
                    "has_main": "__main__" in content,
                }
                
                for key, value in requirements.items():
                    if key != "exists" and value:
                        print(f"  • {key.replace('_', ' ').title()}")
                
                results[script_name] = requirements
                
            except Exception as e:
                print(f"  ✗ Error reading: {e}")
                results[script_name] = {"exists": True, "error": str(e)}
        
        return results
    
    def identify_issues(self, data_inventory: Dict, script_analysis: Dict) -> List[str]:
        """Identify specific issues preventing visualization"""
        self.print_header("IDENTIFIED ISSUES")
        
        issues = []
        
        # Issue 1: No comparison results
        if len(data_inventory["comparison_results"]) == 0:
            issue = "No comparison_results directory or files found"
            issues.append(issue)
            print(f"1. {issue}")
            print("   → Scripts like analyze_hybrid_results.py need this")
        
        # Issue 2: Data in wrong location
        all_json = (len(data_inventory["hybrid_results"]) + 
                   len(data_inventory["llm_results"]) + 
                   len(data_inventory["nn_results"]))
        
        if all_json > 0:
            print(f"\n2. Found {all_json} result files, but they may be in wrong location")
            print("   → Check if they're in root of results/ vs. subdirectories")
            issues.append("Data files may be in incorrect subdirectories")
        
        # Issue 3: Master analyzer path issues
        for script_name, info in script_analysis.items():
            if not info.get("exists", False):
                issue = f"{script_name} not found by master_analyzer"
                issues.append(issue)
                print(f"\n3. {issue}")
        
        # Issue 4: No output directories
        output_dirs = [
            self.analysis_dir,
            self.analysis_dir / "figures",
            self.analysis_dir / "tables",
            self.analysis_dir / "visualizations"
        ]
        
        missing_output = [d for d in output_dirs if not d.exists()]
        if missing_output:
            print(f"\n4. Missing output directories: {len(missing_output)}")
            for d in missing_output:
                print(f"   • {d.relative_to(self.project_root)}")
            issues.append("Missing output directories")
        
        return issues
    
    def generate_fixes(self, issues: List[str], data_inventory: Dict) -> List[Dict]:
        """Generate specific fixes for identified issues"""
        self.print_header("RECOMMENDED FIXES")
        
        fixes = []
        
        # Fix 1: Create missing directories
        if "Missing output directories" in issues or "No comparison_results" in str(issues):
            fix = {
                "type": "create_directories",
                "description": "Create missing directory structure",
                "dirs": [
                    "hypatiax/data/results/comparison_results",
                    "hypatiax/data/results/hybrid_results",
                    "hypatiax/data/results/baseline_llm",
                    "hypatiax/data/results/baseline_nn",
                    "hypatiax/data/analysis",
                    "hypatiax/data/analysis/figures",
                    "hypatiax/data/analysis/tables",
                    "hypatiax/data/analysis/visualizations"
                ],
                "priority": "HIGH"
            }
            fixes.append(fix)
            print("Fix 1: Create Directory Structure")
            print("  Priority: HIGH")
            print("  Action: Create all required directories")
            print("  Directories:")
            for d in fix["dirs"]:
                print(f"    • {d}")
        
        # Fix 2: Reorganize data files
        if len(data_inventory["other_json"]) > 0:
            fix = {
                "type": "reorganize_data",
                "description": "Move result files to correct subdirectories",
                "action": "Organize JSON files by type (hybrid/llm/nn)",
                "priority": "HIGH"
            }
            fixes.append(fix)
            print("\nFix 2: Reorganize Data Files")
            print("  Priority: HIGH")
            print("  Action: Sort result files into correct subdirectories")
        
        # Fix 3: Fix master_analyzer paths
        fix = {
            "type": "fix_paths",
            "description": "Update master_analyzer.py to use correct paths",
            "action": "Patch script path resolution",
            "priority": "MEDIUM"
        }
        fixes.append(fix)
        print("\nFix 3: Fix Script Paths")
        print("  Priority: MEDIUM")
        print("  Action: Update path resolution in master_analyzer.py")
        
        # Fix 4: Create stub comparison results
        if len(data_inventory["comparison_results"]) == 0:
            fix = {
                "type": "create_comparison",
                "description": "Generate comparison results from existing data",
                "action": "Create comparison JSON from hybrid/baseline results",
                "priority": "HIGH"
            }
            fixes.append(fix)
            print("\nFix 4: Generate Comparison Results")
            print("  Priority: HIGH")
            print("  Action: Synthesize comparison data from existing results")
        
        return fixes
    
    def apply_fixes(self, fixes: List[Dict], dry_run: bool = True) -> bool:
        """Apply the recommended fixes"""
        self.print_header("APPLYING FIXES")
        
        if dry_run:
            print("DRY RUN MODE - No changes will be made\n")
        
        success_count = 0
        
        for i, fix in enumerate(fixes, 1):
            print(f"\nFix {i}/{len(fixes)}: {fix['description']}")
            print(f"Priority: {fix['priority']}")
            
            if fix["type"] == "create_directories":
                if self._apply_directory_fix(fix, dry_run):
                    success_count += 1
            
            elif fix["type"] == "reorganize_data":
                if self._apply_reorganize_fix(fix, dry_run):
                    success_count += 1
            
            elif fix["type"] == "fix_paths":
                if self._apply_path_fix(fix, dry_run):
                    success_count += 1
            
            elif fix["type"] == "create_comparison":
                if self._apply_comparison_fix(fix, dry_run):
                    success_count += 1
        
        print(f"\n{'[DRY RUN] Would apply' if dry_run else 'Applied'} {success_count}/{len(fixes)} fixes")
        return success_count == len(fixes)
    
    def _apply_directory_fix(self, fix: Dict, dry_run: bool) -> bool:
        """Create missing directories"""
        try:
            for dir_path in fix["dirs"]:
                # All paths should be relative to project root
                full_path = self.project_root / dir_path
                
                if dry_run:
                    rel_path = full_path.relative_to(self.project_root)
                    print(f"  [DRY RUN] Would create: {rel_path}")
                else:
                    full_path.mkdir(parents=True, exist_ok=True)
                    # Create .gitkeep to preserve empty directories in git
                    (full_path / ".gitkeep").touch()
                    rel_path = full_path.relative_to(self.project_root)
                    print(f"  ✓ Created: {rel_path}")
            
            return True
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _apply_reorganize_fix(self, fix: Dict, dry_run: bool) -> bool:
        """Reorganize data files"""
        try:
            # Find all JSON files in root of results
            root_jsons = list(self.results_dir.glob("*.json"))
            
            if not root_jsons:
                print("  ℹ No files to reorganize")
                return True
            
            for json_file in root_jsons:
                # Determine target directory based on filename
                filename = json_file.name.lower()
                
                if "hybrid" in filename:
                    target_dir = self.results_dir / "hybrid_results"
                elif "llm" in filename or "pure_llm" in filename:
                    target_dir = self.results_dir / "baseline_llm"
                elif "nn" in filename or "neural" in filename:
                    target_dir = self.results_dir / "baseline_nn"
                else:
                    continue  # Skip files we don't recognize
                
                target_path = target_dir / json_file.name
                
                if dry_run:
                    print(f"  [DRY RUN] Would move: {json_file.name} → {target_dir.name}/")
                else:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(json_file), str(target_path))
                    print(f"  ✓ Moved: {json_file.name} → {target_dir.name}/")
            
            return True
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def _apply_path_fix(self, fix: Dict, dry_run: bool) -> bool:
        """Fix path issues in master_analyzer"""
        try:
            master_path = self.viz_dir / "master_analyzer.py"
            
            if not master_path.exists():
                print("  ℹ master_analyzer.py not found, skipping")
                return True
            
            if dry_run:
                print("  [DRY RUN] Would patch master_analyzer.py path resolution")
                return True
            
            # Create patched version
            with open(master_path, 'r') as f:
                content = f.read()
            
            # Backup
            backup_path = master_path.with_suffix('.py.bak')
            shutil.copy2(master_path, backup_path)
            print(f"  ✓ Backed up to: {backup_path.name}")
            
            # Add path fixes at the top
            path_fix = '''
# AUTOMATED PATH FIX
import sys
from pathlib import Path

# Ensure scripts can be found
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Update script paths to absolute
VIZ_DIR = SCRIPT_DIR
'''
            
            # Insert after imports
            if "import sys" not in content:
                content = path_fix + content
                
                with open(master_path, 'w') as f:
                    f.write(content)
                
                print("  ✓ Patched master_analyzer.py")
            else:
                print("  ℹ Script already has path handling")
            
            return True
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def _apply_comparison_fix(self, fix: Dict, dry_run: bool) -> bool:
        """Create comparison results from existing data"""
        try:
            # Find existing results
            hybrid_files = list(self.results_dir.rglob("*hybrid*.json"))
            llm_files = list(self.results_dir.rglob("*llm*.json"))
            nn_files = list(self.results_dir.rglob("*nn*.json"))
            
            if not (hybrid_files or llm_files or nn_files):
                print("  ℹ No existing results to create comparison from")
                return True
            
            comparison_dir = self.results_dir / "comparison_results"
            
            if dry_run:
                print(f"  [DRY RUN] Would create comparison from {len(hybrid_files)} hybrid, "
                      f"{len(llm_files)} LLM, {len(nn_files)} NN files")
                return True
            
            comparison_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a simple comparison structure
            comparison_data = {
                "timestamp": datetime.now().isoformat(),
                "hybrid_results": [str(f.relative_to(self.results_dir)) for f in hybrid_files],
                "llm_results": [str(f.relative_to(self.results_dir)) for f in llm_files],
                "nn_results": [str(f.relative_to(self.results_dir)) for f in nn_files],
                "summary": {
                    "total_experiments": len(hybrid_files) + len(llm_files) + len(nn_files),
                    "hybrid_count": len(hybrid_files),
                    "llm_count": len(llm_files),
                    "nn_count": len(nn_files)
                }
            }
            
            comparison_file = comparison_dir / f"comparison_index_{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(comparison_file, 'w') as f:
                json.dump(comparison_data, f, indent=2)
            
            print(f"  ✓ Created: {comparison_file.name}")
            return True
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def run_full_diagnosis(self, apply_fixes: bool = False) -> bool:
        """Run complete diagnosis"""
        print("\n" + "="*80)
        print(" HYPATIAX VISUALIZATION DIAGNOSTIC TOOL")
        print("="*80)
        print(f"\nProject Root: {self.project_root}")
        print(f"Viz Directory: {self.viz_dir}")
        print(f"Results Directory: {self.results_dir}")
        print(f"Analysis Directory: {self.analysis_dir}")
        
        # Step 1: Check data files
        data_inventory = self.check_data_files()
        
        # Step 2: Analyze master analyzer
        master_analysis = self.analyze_master_analyzer()
        
        # Step 3: Check individual scripts
        script_analysis = self.check_individual_scripts()
        
        # Step 4: Identify issues
        issues = self.identify_issues(data_inventory, script_analysis)
        
        # Step 5: Generate fixes
        fixes = self.generate_fixes(issues, data_inventory)
        
        # Step 6: Apply fixes if requested
        if apply_fixes:
            return self.apply_fixes(fixes, dry_run=False)
        else:
            self.apply_fixes(fixes, dry_run=True)
            
            self.print_header("TO APPLY FIXES")
            print("Run this script with --fix flag:")
            print(f"  python {Path(__file__).name} --fix")
            
            return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Diagnose and fix HypatiaX visualization issues",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--fix', action='store_true',
                       help='Apply fixes (default: diagnosis only)')
    parser.add_argument('--project-root', type=str,
                       help='Override project root directory')
    
    args = parser.parse_args()
    
    try:
        diagnostic = VisualizationDiagnostic(project_root=args.project_root)
        success = diagnostic.run_full_diagnosis(apply_fixes=args.fix)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

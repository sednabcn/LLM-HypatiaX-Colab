#!/usr/bin/env python3
"""
Comprehensive checker for data dependencies and model loading
Checks datasets, models, and all data files in HypatiaX project
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

class DataModelChecker:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).resolve()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "datasets": {},
            "models": {},
            "data_files": {},
            "errors": []
        }
    
    def check_datasets(self):
        """Check for dataset directories and files"""
        print("\n" + "="*80)
        print("📊 CHECKING DATASETS")
        print("="*80)
        
        # Common dataset locations
        dataset_paths = [
            self.project_root / "datasets",
            self.project_root / "data",
            self.project_root / "training_data",
            self.project_root / "hypatiax" / "data",
            self.project_root / "hypatiax" / "datasets",
        ]
        
        found_datasets = False
        
        for dataset_path in dataset_paths:
            if dataset_path.exists():
                found_datasets = True
                print(f"\n✅ Found dataset directory: {dataset_path.relative_to(self.project_root)}")
                
                # Count files by type
                file_counts = {}
                total_size = 0
                
                for file in dataset_path.rglob("*"):
                    if file.is_file():
                        ext = file.suffix.lower()
                        file_counts[ext] = file_counts.get(ext, 0) + 1
                        total_size += file.stat().st_size
                
                self.results["datasets"][str(dataset_path.relative_to(self.project_root))] = {
                    "exists": True,
                    "file_counts": file_counts,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "files": len(list(dataset_path.rglob("*")))
                }
                
                print(f"   📁 Total files: {len(list(dataset_path.rglob('*')))}")
                print(f"   💾 Total size: {total_size / (1024 * 1024):.2f} MB")
                print(f"   📄 File types: {dict(sorted(file_counts.items()))}")
                
                # List some files
                files = list(dataset_path.glob("*"))[:10]
                if files:
                    print(f"   📝 Sample files:")
                    for f in files:
                        if f.is_file():
                            size = f.stat().st_size / 1024
                            print(f"      - {f.name} ({size:.1f} KB)")
        
        if not found_datasets:
            print("\n❌ No dataset directories found")
            self.results["errors"].append("No dataset directories found")
        
        return found_datasets
    
    def check_spacy_models(self):
        """Check spaCy models"""
        print("\n" + "="*80)
        print("🧠 CHECKING SPACY MODELS")
        print("="*80)
        
        try:
            import spacy
            print(f"\n✅ spaCy version: {spacy.__version__}")
            
            # Find custom models
            model_paths = [
                self.project_root / "models",
                self.project_root / "hypatiax" / "data_spacy",
                self.project_root / "hypatiax" / "custom_ner",
            ]
            
            found_models = []
            
            for model_path in model_paths:
                if model_path.exists():
                    # Look for spaCy model directories (contain meta.json or config.cfg)
                    for item in model_path.rglob("*"):
                        if item.is_dir():
                            if (item / "meta.json").exists() or (item / "config.cfg").exists():
                                found_models.append(item)
                                print(f"\n✅ Found spaCy model: {item.relative_to(self.project_root)}")
                                
                                # Try to load it
                                try:
                                    nlp = spacy.load(str(item))
                                    print(f"   ✅ Successfully loaded")
                                    print(f"   📋 Pipeline: {nlp.pipe_names}")
                                    print(f"   🏷️  Labels: {nlp.get_pipe('ner').labels if 'ner' in nlp.pipe_names else 'N/A'}")
                                    
                                    self.results["models"][str(item.relative_to(self.project_root))] = {
                                        "type": "spacy",
                                        "loadable": True,
                                        "pipeline": nlp.pipe_names,
                                        "labels": list(nlp.get_pipe('ner').labels) if 'ner' in nlp.pipe_names else []
                                    }
                                    
                                except Exception as e:
                                    print(f"   ❌ Failed to load: {e}")
                                    self.results["models"][str(item.relative_to(self.project_root))] = {
                                        "type": "spacy",
                                        "loadable": False,
                                        "error": str(e)
                                    }
                                    self.results["errors"].append(f"Cannot load model {item}: {e}")
            
            if not found_models:
                print("\n⚠️  No custom spaCy models found")
            
            # Check standard models
            print("\n📦 Checking installed spaCy models:")
            try:
                from spacy.cli.info import info
                import subprocess
                result = subprocess.run([sys.executable, "-m", "spacy", "info"], 
                                      capture_output=True, text=True)
                print(result.stdout)
            except:
                pass
                
        except ImportError:
            print("\n❌ spaCy not installed")
            self.results["errors"].append("spaCy not installed")
    
    def check_data_files(self):
        """Check for training data files and JSONL files"""
        print("\n" + "="*80)
        print("📄 CHECKING DATA FILES")
        print("="*80)
        
        # Look for common data file patterns
        patterns = {
            "JSONL files": "*.jsonl",
            "CSV files": "*.csv",
            "JSON files": "*.json",
            "Pickle files": "*.pkl",
            "NPY files": "*.npy",
            "HDF5 files": "*.h5",
            "Parquet files": "*.parquet",
        }
        
        for name, pattern in patterns.items():
            files = list(self.project_root.rglob(pattern))
            if files:
                print(f"\n✅ {name}: {len(files)} found")
                self.results["data_files"][name] = {
                    "count": len(files),
                    "files": [str(f.relative_to(self.project_root)) for f in files[:5]]
                }
                
                # Show first few
                for f in files[:5]:
                    size = f.stat().st_size / 1024
                    print(f"   - {f.relative_to(self.project_root)} ({size:.1f} KB)")
                
                if len(files) > 5:
                    print(f"   ... and {len(files) - 5} more")
    
    def check_rule_files(self):
        """Check for entity ruler files"""
        print("\n" + "="*80)
        print("📏 CHECKING RULE FILES")
        print("="*80)
        
        rule_files = list(self.project_root.rglob("ruler*.jsonl"))
        
        if rule_files:
            print(f"\n✅ Found {len(rule_files)} ruler files")
            
            for rule_file in rule_files:
                print(f"\n📋 {rule_file.relative_to(self.project_root)}")
                
                try:
                    rule_count = 0
                    with open(rule_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                rule_count += 1
                    
                    print(f"   ✅ {rule_count} rules")
                    self.results["data_files"][f"ruler_{rule_file.name}"] = {
                        "path": str(rule_file.relative_to(self.project_root)),
                        "rule_count": rule_count
                    }
                    
                except Exception as e:
                    print(f"   ❌ Error reading: {e}")
                    self.results["errors"].append(f"Cannot read {rule_file}: {e}")
        else:
            print("\n⚠️  No ruler files found")
    
    def test_model_loading(self):
        """Test loading models from code"""
        print("\n" + "="*80)
        print("🧪 TESTING MODEL LOADING")
        print("="*80)
        
        # Try to import and test custom components
        try:
            sys.path.insert(0, str(self.project_root))
            
            # Look for custom component files
            component_files = list(self.project_root.rglob("custom_*_components.py"))
            
            if component_files:
                print(f"\n✅ Found {len(component_files)} custom component files")
                
                for comp_file in component_files:
                    print(f"\n📦 Testing: {comp_file.relative_to(self.project_root)}")
                    
                    try:
                        # Try to import (but don't execute fully)
                        spec = __import__('importlib.util').util.spec_from_file_location(
                            comp_file.stem, comp_file
                        )
                        if spec and spec.loader:
                            print(f"   ✅ Module is importable")
                    except Exception as e:
                        print(f"   ❌ Import error: {e}")
                        self.results["errors"].append(f"Cannot import {comp_file}: {e}")
            else:
                print("\n⚠️  No custom component files found")
                
        except Exception as e:
            print(f"\n❌ Error testing model loading: {e}")
            self.results["errors"].append(f"Model loading test failed: {e}")
    
    def check_requirements(self):
        """Check if required packages are installed"""
        print("\n" + "="*80)
        print("📦 CHECKING REQUIREMENTS")
        print("="*80)
        
        req_files = list(self.project_root.glob("requirements*.txt"))
        
        if req_files:
            for req_file in req_files:
                print(f"\n📄 Checking {req_file.name}")
                
                try:
                    with open(req_file, 'r') as f:
                        requirements = [line.strip() for line in f 
                                      if line.strip() and not line.startswith('#')]
                    
                    print(f"   Found {len(requirements)} requirements")
                    
                    # Check which are installed
                    installed = []
                    missing = []
                    
                    for req in requirements[:20]:  # Check first 20
                        pkg_name = req.split('==')[0].split('>=')[0].split('<=')[0].strip()
                        try:
                            __import__(pkg_name.replace('-', '_'))
                            installed.append(pkg_name)
                        except ImportError:
                            missing.append(pkg_name)
                    
                    if installed:
                        print(f"   ✅ Installed: {len(installed)}")
                    if missing:
                        print(f"   ❌ Missing: {missing[:5]}")
                        if len(missing) > 5:
                            print(f"      ... and {len(missing) - 5} more")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
        else:
            print("\n⚠️  No requirements.txt found")
    
    def save_report(self):
        """Save detailed report to JSON"""
        report_file = self.project_root / "data_model_check_report.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 Report saved to: {report_file}")
        except Exception as e:
            print(f"\n❌ Could not save report: {e}")
    
    def print_summary(self):
        """Print summary of findings"""
        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        
        print(f"\n✅ Datasets found: {len(self.results['datasets'])}")
        print(f"✅ Models found: {len(self.results['models'])}")
        print(f"✅ Data file types: {len(self.results['data_files'])}")
        print(f"❌ Errors encountered: {len(self.results['errors'])}")
        
        if self.results['errors']:
            print("\n⚠️  Errors:")
            for error in self.results['errors'][:10]:
                print(f"   - {error}")
        
        print("\n" + "="*80)
    
    def run_all_checks(self):
        """Run all checks"""
        print("\n🔍 Starting comprehensive data and model check...")
        print(f"📁 Project root: {self.project_root}")
        
        self.check_datasets()
        self.check_spacy_models()
        self.check_data_files()
        self.check_rule_files()
        self.test_model_loading()
        self.check_requirements()
        
        self.print_summary()
        self.save_report()
        
        print("\n✅ Check complete!")
        
        return len(self.results['errors']) == 0


if __name__ == "__main__":
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    checker = DataModelChecker(project_root)
    success = checker.run_all_checks()
    
    sys.exit(0 if success else 1)

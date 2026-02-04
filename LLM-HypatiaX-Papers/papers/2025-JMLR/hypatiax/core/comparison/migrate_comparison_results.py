#!/usr/bin/env python3
"""
Migrate Comparison Results to HypatiaX Data Structure
=====================================================

Migrates existing comparison analysis from outputs/ to hypatiax/data/results/
with proper organization and structure.

Usage:
    python migrate_comparison_results.py [--dry-run] [--preserve-original]
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import argparse


class ComparisonMigrator:
    """Migrates comparison results to HypatiaX structure"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            current = Path(__file__).resolve()
            while current.parent != current:
                if (current / "hypatiax").exists():
                    project_root = str(current)
                    break
                current = current.parent
        
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
        # Source directories
        self.source_dir = self.project_root / "outputs" / "output_results" / "comparison_llM_nn_generation"
        
        # Target directories - SEPARATED STRUCTURE
        self.target_data = self.project_root / "hypatiax" / "data"
        self.target_results = self.target_data / "results"
        self.target_comparison = self.target_data / "comparison_results"  # SEPARATE from results/
        self.target_hybrid = self.target_results / "hybrid_results"
        self.target_llm = self.target_results / "baseline_llm"
        self.target_nn = self.target_results / "baseline_nn"
        self.target_analysis = self.target_data / "analysis"
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f" {title}")
        print("="*80 + "\n")
    
    def analyze_source_structure(self) -> Dict[str, List[Path]]:
        """Analyze what we have in the source directory"""
        self.print_header("SOURCE DIRECTORY ANALYSIS")
        
        if not self.source_dir.exists():
            print(f"❌ Source directory not found: {self.source_dir}")
            return {}
        
        structure = {
            "comparison_analyses": [],
            "baseline_llm_json": [],
            "baseline_nn_json": [],
            "hybrid_json": [],
            "reports": [],
            "visualizations": [],
            "debug": [],
            "raw_data": [],
            "scripts": []
        }
        
        # Scan source directory
        for item in self.source_dir.rglob("*"):
            if not item.is_file():
                continue
            
            rel_path = item.relative_to(self.source_dir)
            
            # Categorize files
            if "comparison_analysis" in str(item):
                if item.suffix in [".json", ".csv", ".txt", ".md"]:
                    structure["comparison_analyses"].append(item)
            
            elif "baseline_llm" in item.name or "pure_llm" in item.name:
                if item.suffix == ".json":
                    structure["baseline_llm_json"].append(item)
            
            elif "baseline_nn" in item.name or "neural_network" in item.name:
                if item.suffix == ".json":
                    structure["baseline_nn_json"].append(item)
            
            elif "hybrid" in item.name:
                if item.suffix == ".json":
                    structure["hybrid_json"].append(item)
            
            elif item.suffix == ".png":
                structure["visualizations"].append(item)
            
            elif "report" in item.name and item.suffix == ".json":
                structure["reports"].append(item)
            
            elif "debug" in str(item):
                structure["debug"].append(item)
            
            elif item.suffix == ".py":
                structure["scripts"].append(item)
            
            else:
                structure["raw_data"].append(item)
        
        # Print summary
        print("Found files by category:")
        for category, files in structure.items():
            count = len(files)
            print(f"  • {category.replace('_', ' ').title()}: {count} files")
            if count > 0 and count <= 3:
                for f in files:
                    print(f"      - {f.name}")
            elif count > 3:
                for f in files[:2]:
                    print(f"      - {f.name}")
                print(f"      ... and {count - 2} more")
        
        return structure
    
    def extract_timestamp_from_filename(self, filepath: Path) -> str:
        """Extract timestamp from filename (YYYYMMDD_HHMMSS or YYYYMMDD)"""
        import re
        # Look for patterns like 20251223_124902 or 20251223
        match = re.search(r'(\d{8})(?:_(\d{6}))?', filepath.name)
        if match:
            date = match.group(1)
            time = match.group(2) if match.group(2) else "000000"
            return f"{date}_{time}"
        return "unknown"
    
    def extract_domain_from_path(self, filepath: Path) -> str:
        """Extract domain from filepath or filename"""
        path_str = str(filepath).lower()
        if "all_domains" in path_str or "all_domain" in path_str:
            return "all_domains"
        elif "defi" in path_str:
            return "defi"
        else:
            return "general"
    
    def group_files_by_timestamp(self, structure: Dict[str, List[Path]]) -> Dict[str, Dict[str, List[Path]]]:
        """Group files by timestamp to identify comparison sets"""
        self.print_header("IDENTIFYING COMPARISON SETS BY TIMESTAMP")
        
        timestamp_groups = {}
        
        # Process all result files
        all_result_files = (
            structure["baseline_llm_json"] + 
            structure["baseline_nn_json"] + 
            structure["hybrid_json"] +
            structure["reports"]
        )
        
        for filepath in all_result_files:
            timestamp = self.extract_timestamp_from_filename(filepath)
            domain = self.extract_domain_from_path(filepath)
            
            key = f"{domain}_{timestamp}"
            
            if key not in timestamp_groups:
                timestamp_groups[key] = {
                    "timestamp": timestamp,
                    "domain": domain,
                    "llm": [],
                    "nn": [],
                    "hybrid": [],
                    "reports": []
                }
            
            # Categorize
            if "baseline_llm" in filepath.name or "pure_llm" in filepath.name:
                timestamp_groups[key]["llm"].append(filepath)
            elif "baseline_nn" in filepath.name or "neural_network" in filepath.name:
                timestamp_groups[key]["nn"].append(filepath)
            elif "hybrid" in filepath.name:
                timestamp_groups[key]["hybrid"].append(filepath)
            elif "report" in filepath.name:
                timestamp_groups[key]["reports"].append(filepath)
        
        # Print comparison sets
        print(f"\nFound {len(timestamp_groups)} potential comparison sets:\n")
        
        complete_sets = []
        incomplete_sets = []
        
        for key, group in sorted(timestamp_groups.items()):
            has_llm = len(group["llm"]) > 0
            has_nn = len(group["nn"]) > 0
            has_hybrid = len(group["hybrid"]) > 0
            
            is_complete = has_llm and has_nn
            
            status = "✓ COMPLETE" if is_complete else "⚠ INCOMPLETE"
            print(f"{status} - {group['domain']} @ {group['timestamp']}")
            print(f"         LLM: {len(group['llm'])} | NN: {len(group['nn'])} | Hybrid: {len(group['hybrid'])} | Reports: {len(group['reports'])}")
            
            if has_llm:
                for f in group["llm"]:
                    print(f"           📄 {f.name}")
            if has_nn:
                for f in group["nn"]:
                    print(f"           📄 {f.name}")
            if has_hybrid:
                for f in group["hybrid"]:
                    print(f"           📄 {f.name}")
            
            print()
            
            if is_complete:
                complete_sets.append(key)
            else:
                incomplete_sets.append(key)
        
        print(f"Summary:")
        print(f"  ✓ Complete comparison sets: {len(complete_sets)}")
        print(f"  ⚠ Incomplete sets: {len(incomplete_sets)}")
        
        return timestamp_groups
    
    def create_migration_plan(self, structure: Dict[str, List[Path]], 
                             timestamp_groups: Dict[str, Dict[str, List[Path]]]) -> Dict[str, List[Tuple[Path, Path]]]:
        """Create detailed migration plan organized by comparison sets"""
        self.print_header("MIGRATION PLAN")
        
        plan = {
            "comparison_sets": [],
            "comparison_analyses": [],
            "analysis_outputs": [],
            "archived": []
        }
        
        # 1. Organize comparison sets by timestamp
        print("1. Comparison Sets (organized by timestamp)\n")
        
        for key, group in sorted(timestamp_groups.items()):
            timestamp = group["timestamp"]
            domain = group["domain"]
            
            has_llm = len(group["llm"]) > 0
            has_nn = len(group["nn"]) > 0
            is_complete = has_llm and has_nn
            
            if not is_complete:
                print(f"   ⚠ SKIPPING incomplete set: {domain} @ {timestamp}")
                continue
            
            # Create comparison directory for this timestamp
            comparison_dir = self.target_comparison / domain / timestamp
            
            print(f"   ✓ {domain} @ {timestamp}")
            
            # Add all files from this comparison set
            for llm_file in group["llm"]:
                target = comparison_dir / "baseline_llm" / llm_file.name
                plan["comparison_sets"].append((llm_file, target))
                print(f"      📄 LLM: {llm_file.name}")
            
            for nn_file in group["nn"]:
                target = comparison_dir / "baseline_nn" / nn_file.name
                plan["comparison_sets"].append((nn_file, target))
                print(f"      📄 NN:  {nn_file.name}")
            
            for hybrid_file in group["hybrid"]:
                target = comparison_dir / "hybrid" / hybrid_file.name
                plan["comparison_sets"].append((hybrid_file, target))
                print(f"      📄 Hybrid: {hybrid_file.name}")
            
            for report_file in group["reports"]:
                target = comparison_dir / "reports" / report_file.name
                plan["comparison_sets"].append((report_file, target))
                print(f"      📄 Report: {report_file.name}")
            
            # Create a comparison metadata file
            metadata = {
                "timestamp": timestamp,
                "domain": domain,
                "llm_files": [f.name for f in group["llm"]],
                "nn_files": [f.name for f in group["nn"]],
                "hybrid_files": [f.name for f in group["hybrid"]],
                "report_files": [f.name for f in group["reports"]],
                "comparison_complete": True
            }
            plan["comparison_sets"].append((
                None,  # Will create this file
                comparison_dir / "comparison_metadata.json"
            ))
            
            print()
        
        # 2. Existing comparison analyses
        print("\n2. Existing Comparison Analyses → comparison_results/analyses/")
        for src in structure["comparison_analyses"]:
            domain = self.extract_domain_from_path(src)
            target = self.target_comparison / "analyses" / domain / src.name
            
            plan["comparison_analyses"].append((src, target))
            print(f"   {src.name} → analyses/{domain}/")
        
        # 3. Visualizations
        print("\n3. Visualizations → analysis/figures/")
        for src in structure["visualizations"]:
            domain = self.extract_domain_from_path(src)
            if "comparison" in src.name:
                target = self.target_analysis / "figures" / "comparisons" / domain / src.name
            else:
                target = self.target_analysis / "figures" / domain / src.name
            
            plan["analysis_outputs"].append((src, target))
            print(f"   {src.name}")
        
        # 4. Archive
        print("\n4. Archive (debug, scripts, raw data)")
        archive_base = self.target_data / "archive" / datetime.now().strftime("%Y%m%d")
        for src in structure["debug"] + structure["scripts"] + structure["raw_data"]:
            rel_path = src.relative_to(self.source_dir)
            target = archive_base / rel_path
            plan["archived"].append((src, target))
        print(f"   {len(plan['archived'])} files → archive/{datetime.now().strftime('%Y%m%d')}/")
        
        return plan
    
    def create_migration_summary(self, plan: Dict[str, List[Tuple[Path, Path]]]) -> Dict:
        """Create summary of what will be migrated"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "source_directory": str(self.source_dir),
            "target_directory": str(self.target_comparison),
            "migration_counts": {},
            "file_mappings": {}
        }
        
        for category, mappings in plan.items():
            summary["migration_counts"][category] = len(mappings)
            summary["file_mappings"][category] = [
                {
                    "source": str(src.relative_to(self.source_dir)) if src else "auto-generated",
                    "target": str(tgt.relative_to(self.project_root))
                }
                for src, tgt in mappings
            ]
        
        return summary
    
    def execute_migration(self, plan: Dict[str, List[Tuple[Path, Path]]], 
                         dry_run: bool = True, preserve_original: bool = True) -> bool:
        """Execute the migration plan"""
        self.print_header("EXECUTING MIGRATION")
        
        if dry_run:
            print("🔍 DRY RUN MODE - No files will be moved\n")
        else:
            print("⚠️  LIVE MODE - Files will be moved\n")
        
        total_files = sum(len(mappings) for mappings in plan.values())
        migrated = 0
        errors = []
        
        for category, mappings in plan.items():
            if not mappings:
                continue
            
            print(f"\n📦 Migrating {category} ({len(mappings)} items)...")
            
            for src, tgt in mappings:
                try:
                    # Handle metadata file creation
                    if src is None:
                        if dry_run:
                            print(f"   [DRY RUN] Would create: {tgt.name}")
                        else:
                            tgt.parent.mkdir(parents=True, exist_ok=True)
                            # Metadata will be created from plan data
                            print(f"   ✓ Would create: {tgt.name}")
                        migrated += 1
                        continue
                    
                    if dry_run:
                        print(f"   [DRY RUN] Would copy: {src.name}")
                    else:
                        # Create target directory
                        tgt.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy or move
                        if preserve_original:
                            shutil.copy2(src, tgt)
                            print(f"   ✓ Copied: {src.name}")
                        else:
                            shutil.move(str(src), str(tgt))
                            print(f"   ✓ Moved: {src.name}")
                    
                    migrated += 1
                    
                except Exception as e:
                    error_msg = f"Error with {src.name if src else 'metadata'}: {str(e)}"
                    errors.append(error_msg)
                    print(f"   ❌ {error_msg}")
        
        # Summary
        print(f"\n{'='*80}")
        print(f"Migration Summary:")
        print(f"  • Total items: {total_files}")
        print(f"  • Successfully migrated: {migrated}")
        print(f"  • Errors: {len(errors)}")
        
        if dry_run:
            print(f"\n💡 To execute migration, run with --execute flag")
        else:
            print(f"\n✅ Migration complete!")
            
            if preserve_original:
                print(f"   Original files preserved in: {self.source_dir}")
            else:
                print(f"   Original files moved from: {self.source_dir}")
        
        if errors:
            print(f"\n❌ Errors encountered:")
            for error in errors[:5]:
                print(f"   • {error}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more")
        
        return len(errors) == 0
    
    def create_index_files(self, dry_run: bool = True):
        """Create index files for easier navigation"""
        self.print_header("CREATING INDEX FILES")
        
        indices = {
            "comparison_results": self.target_comparison / "INDEX.md",
            "baseline_llm": self.target_llm / "INDEX.md",
            "baseline_nn": self.target_nn / "INDEX.md",
            "hybrid_results": self.target_hybrid / "INDEX.md"
        }
        
        for category, index_path in indices.items():
            if dry_run:
                print(f"[DRY RUN] Would create: {index_path.name} in {category}")
            else:
                if not index_path.parent.exists():
                    continue
                
                content = f"""# {category.replace('_', ' ').title()}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Structure

"""
                # List subdirectories and files
                for item in sorted(index_path.parent.iterdir()):
                    if item.name == "INDEX.md":
                        continue
                    if item.is_dir():
                        content += f"### {item.name}/\n\n"
                        json_files = list(item.glob("*.json"))
                        if json_files:
                            for f in sorted(json_files)[:10]:
                                content += f"- `{f.name}`\n"
                            if len(json_files) > 10:
                                content += f"- ... and {len(json_files) - 10} more\n"
                        content += "\n"
                    elif item.suffix in [".json", ".csv", ".txt"]:
                        content += f"- `{item.name}`\n"
                
                with open(index_path, 'w') as f:
                    f.write(content)
                
                print(f"✓ Created: {index_path.relative_to(self.project_root)}")
    
    def run_migration(self, dry_run: bool = True, preserve_original: bool = True) -> bool:
        """Run complete migration process"""
        print("\n" + "="*80)
        print(" HYPATIAX COMPARISON RESULTS MIGRATION")
        print("="*80)
        print(f"\nProject Root: {self.project_root}")
        print(f"Source: {self.source_dir}")
        print(f"\nTarget Structure:")
        print(f"  • Results:     {self.target_results}")
        print(f"  • Comparisons: {self.target_comparison} (SEPARATE)")
        print(f"  • Analysis:    {self.target_analysis}")
        print(f"\nMode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
        print(f"Preserve Original: {preserve_original}")
        
        # Step 1: Analyze source
        structure = self.analyze_source_structure()
        
        if not structure or all(len(v) == 0 for v in structure.values()):
            print("\n❌ No files found to migrate!")
            return False
        
        # Step 2: Group files by timestamp to identify comparison sets
        timestamp_groups = self.group_files_by_timestamp(structure)
        
        # Step 3: Create migration plan
        plan = self.create_migration_plan(structure, timestamp_groups)
        
        # Step 3: Save migration summary
        if not dry_run:
            summary = self.create_migration_summary(plan)
            summary_path = self.target_results / f"migration_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\n📄 Migration summary saved: {summary_path.name}")
        
        # Step 4: Execute migration
        success = self.execute_migration(plan, dry_run=dry_run, preserve_original=preserve_original)
        
        # Step 5: Create index files
        if not dry_run and success:
            self.create_index_files(dry_run=False)
        
        return success


def main():
    parser = argparse.ArgumentParser(
        description="Migrate comparison results to HypatiaX structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview what will happen)
  python migrate_comparison_results.py
  
  # Execute migration (preserve originals)
  python migrate_comparison_results.py --execute
  
  # Execute migration (move files, don't preserve)
  python migrate_comparison_results.py --execute --no-preserve
  
  # Custom project root
  python migrate_comparison_results.py --project-root /path/to/project
        """
    )
    
    parser.add_argument('--execute', action='store_true',
                       help='Execute migration (default: dry run)')
    parser.add_argument('--no-preserve', action='store_true',
                       help='Move files instead of copying (default: copy)')
    parser.add_argument('--project-root', type=str,
                       help='Override project root directory')
    
    args = parser.parse_args()
    
    try:
        migrator = ComparisonMigrator(project_root=args.project_root)
        success = migrator.run_migration(
            dry_run=not args.execute,
            preserve_original=not args.no_preserve
        )
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


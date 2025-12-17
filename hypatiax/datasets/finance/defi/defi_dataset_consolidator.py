"""
DeFi Dataset Consolidator
Merge multiple timestamped datasets into a single unique dataset
"""

import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import hashlib


class DatasetConsolidator:
    """Consolidate multiple DeFi datasets into unique, deduplicated versions."""
    
    def __init__(self, base_dir: str = "data", recursive: bool = True):
        self.base_dir = Path(base_dir)
        self.recursive = recursive
        self.processed_dir = self.base_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        
        # Scan all subdirectories if recursive
        if recursive:
            self.csv_files = list(self.base_dir.rglob("*.csv"))
            self.json_files = list(self.base_dir.rglob("*.json"))
        else:
            self.csv_files = list(self.base_dir.glob("*.csv"))
            self.json_files = list(self.base_dir.glob("*.json"))
    
    def get_latest_files(self) -> Dict[str, Path]:
        """Get the most recent version of each dataset type."""
        patterns = {
            'defi_summary': 'defi_summary',
            'defi_synthetic': 'defi_synthetic',
            'il_test_cases': 'il_test_cases',
            'real_pool_snapshots': 'real_pool_snapshots',
            'uniswap_scenarios': 'uniswap_scenarios'
        }
        
        latest_files = {}
        
        # Filter CSV files by pattern
        for key, pattern in patterns.items():
            matching = [f for f in self.csv_files if pattern in f.stem and f.suffix == '.csv']
            matching = [f for f in matching if 'processed' not in str(f)]  # Exclude processed files
            
            if matching:
                # Sort by modification time, get most recent
                latest_files[key] = max(matching, key=lambda f: f.stat().st_mtime)
        
        return latest_files
    
    def create_row_hash(self, row: pd.Series) -> str:
        """Create hash for deduplication."""
        row_str = '|'.join(str(v) for v in row.values)
        return hashlib.md5(row_str.encode()).hexdigest()
    
    def deduplicate_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """Remove duplicate rows from dataframe."""
        initial_count = len(df)
        
        # Create hash for each row
        df['_row_hash'] = df.apply(self.create_row_hash, axis=1)
        
        # Remove duplicates
        df_unique = df.drop_duplicates(subset='_row_hash', keep='first')
        df_unique = df_unique.drop(columns=['_row_hash'])
        
        duplicates_removed = initial_count - len(df_unique)
        return df_unique, duplicates_removed
    
    def merge_csvs(self, csv_paths: List[Path], output_name: str) -> pd.DataFrame:
        """Merge multiple CSV files and deduplicate."""
        print(f"\nMerging {len(csv_paths)} files for {output_name}:")
        
        dfs = []
        for path in csv_paths:
            try:
                df = pd.read_csv(path)
                dfs.append(df)
                print(f"  ✓ Loaded {path.name}: {len(df)} rows")
            except Exception as e:
                print(f"  ✗ Failed to load {path.name}: {e}")
        
        if not dfs:
            return pd.DataFrame()
        
        # Concatenate all dataframes
        merged = pd.concat(dfs, ignore_index=True)
        print(f"  Total rows before deduplication: {len(merged)}")
        
        # Deduplicate
        unique_df, duplicates = self.deduplicate_dataframe(merged)
        print(f"  Removed {duplicates} duplicates")
        print(f"  Final unique rows: {len(unique_df)}")
        
        return unique_df
    
    def consolidate_formulas(self, formula_paths: List[Path] = None) -> Dict:
        """Consolidate multiple formula JSON files."""
        if formula_paths is None:
            formula_paths = [f for f in self.json_files if 'processed' not in str(f)]
        
        print(f"\nConsolidating {len(formula_paths)} formula files:")
        
        all_formulas = {}
        formula_sources = {}
        
        for path in formula_paths:
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                
                # Handle different JSON structures
                formulas = data if isinstance(data, dict) else {}
                if 'formulas' in data:
                    formulas = data['formulas']
                
                for key, value in formulas.items():
                    if key not in all_formulas:
                        all_formulas[key] = value
                        formula_sources[key] = path.name
                    # If exists, keep the one from the most recent file
                    elif 'fixed' in path.name or path.stat().st_mtime > formula_sources.get(key + '_mtime', 0):
                        all_formulas[key] = value
                        formula_sources[key] = path.name
                        formula_sources[key + '_mtime'] = path.stat().st_mtime
                
                print(f"  ✓ Loaded {path.relative_to(self.base_dir)}: {len(formulas)} formulas")
            except Exception as e:
                print(f"  ✗ Failed to load {path.name}: {e}")
        
        print(f"  Total unique formulas: {len(all_formulas)}")
        return all_formulas
    
    def create_unified_dataset(self):
        """Create unified, deduplicated datasets."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("=" * 80)
        print("DEFI DATASET CONSOLIDATION")
        print("=" * 80)
        
        # Strategy 1: Get latest version of each type
        print("\n[STRATEGY 1] Using Latest Files")
        latest = self.get_latest_files()
        
        for name, path in latest.items():
            try:
                df = pd.read_csv(path)
                unique_df, duplicates = self.deduplicate_dataframe(df)
                
                output_path = self.processed_dir / f"{name}_latest.csv"
                unique_df.to_csv(output_path, index=False)
                print(f"✓ {name}: {len(unique_df)} unique rows -> {output_path.name}")
            except Exception as e:
                print(f"✗ {name}: Failed - {e}")
        
        # Strategy 2: Merge all versions of each dataset type
        print("\n[STRATEGY 2] Merging All Versions")
        
        dataset_types = [
            'defi_summary',
            'defi_synthetic', 
            'il_test_cases',
            'real_pool_snapshots',
            'uniswap_scenarios'
        ]
        
        for dtype in dataset_types:
            matching = [f for f in self.csv_files 
                       if dtype in f.stem and f.suffix == '.csv' 
                       and 'processed' not in str(f)]
            
            if matching:
                merged_df = self.merge_csvs(matching, dtype)
                if not merged_df.empty:
                    output_path = self.processed_dir / f"{dtype}_merged_{timestamp}.csv"
                    merged_df.to_csv(output_path, index=False)
                    print(f"  ✓ Saved: {output_path.name}")
        
        # Strategy 3: Consolidate all formulas
        print("\n[STRATEGY 3] Consolidating Formulas")
        
        consolidated = self.consolidate_formulas()
        if consolidated:
            output_path = self.processed_dir / f"formulas_unified_{timestamp}.json"
            with open(output_path, 'w') as f:
                json.dump(consolidated, f, indent=2)
            print(f"  ✓ Saved: {output_path.name}")
        
        # Create master unified dataset
        print("\n[STRATEGY 4] Creating Master Unified Dataset")
        self.create_master_dataset(timestamp)
        
        print("\n" + "=" * 80)
        print("CONSOLIDATION COMPLETE")
        print(f"Output directory: {self.processed_dir}")
        print("=" * 80)
    
    def create_master_dataset(self, timestamp: str):
        """Create a single master dataset combining all data."""
        all_data = []
        
        # Load all CSV files (excluding processed ones)
        csv_files = [f for f in self.csv_files if 'processed' not in str(f)]
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                df['source_file'] = csv_file.stem
                df['source_path'] = str(csv_file.relative_to(self.base_dir))
                all_data.append(df)
            except:
                pass
        
        if all_data:
            master_df = pd.concat(all_data, ignore_index=True)
            unique_master, duplicates = self.deduplicate_dataframe(master_df)
            
            output_path = self.processed_dir / f"master_dataset_{timestamp}.csv"
            unique_master.to_csv(output_path, index=False)
            
            print(f"  Master dataset: {len(unique_master)} unique rows")
            print(f"  Removed {duplicates} duplicates")
            print(f"  Sources: {unique_master['source_path'].nunique()} files")
            print(f"  ✓ Saved: {output_path.name}")
            
            # Create summary statistics
            summary = {
                'total_rows': len(unique_master),
                'total_columns': len(unique_master.columns),
                'source_files': unique_master['source_path'].unique().tolist(),
                'created_at': timestamp,
                'column_names': list(unique_master.columns)
            }
            
            summary_path = self.processed_dir / f"master_dataset_{timestamp}_summary.json"
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
    
    def analyze_datasets(self):
        """Analyze existing datasets and show statistics."""
        print("\n" + "=" * 80)
        print("DATASET ANALYSIS")
        print("=" * 80)
        
        csv_files = [f for f in self.csv_files if 'processed' not in str(f)]
        print(f"\nFound {len(csv_files)} CSV files across all subdirectories:")
        
        stats = []
        for csv_file in sorted(csv_files):
            try:
                df = pd.read_csv(csv_file)
                stats.append({
                    'path': str(csv_file.relative_to(self.base_dir)),
                    'rows': len(df),
                    'cols': len(df.columns),
                    'modified': datetime.fromtimestamp(csv_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                })
            except:
                pass
        
        # Print statistics
        if stats:
            stats_df = pd.DataFrame(stats)
            print("\n" + stats_df.to_string(index=False))
        
        # Formula analysis
        json_files = [f for f in self.json_files if 'processed' not in str(f)]
        print(f"\n\nFound {len(json_files)} JSON files across all subdirectories")
        
        # Show recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print("\n1. Use 'latest' files for most recent data")
        print("2. Use 'merged' files for comprehensive historical data")
        print("3. Use 'master' dataset for all-in-one analysis")
        print("4. Check 'formulas_unified' for all formula definitions")
        print(f"\n✓ Recursive scanning: {self.recursive}")
        print(f"✓ Scanned directories: {len(set(f.parent for f in self.csv_files))} unique paths")


def main():
    """Main execution."""
    # Enable recursive scanning by default (set to False to scan only top-level)
    consolidator = DatasetConsolidator(base_dir="data", recursive=True)
    
    # Analyze current state
    consolidator.analyze_datasets()
    
    # Create unified datasets
    consolidator.create_unified_dataset()
    
    print("\n✓ Consolidation complete! Check the 'processed' directory.")
    print(f"✓ Scanned {len(consolidator.csv_files)} CSV files recursively")
    print(f"✓ Scanned {len(consolidator.json_files)} JSON files recursively")


if __name__ == "__main__":
    main()

#=====================================================
# USAGE
#=====================================================
    
"""
# Scan all subdirectories (default)
python dataset_consolidator.py

# Or in Python
from dataset_consolidator import DatasetConsolidator

# Recursive (scans all subdirs)
consolidator = DatasetConsolidator(base_dir="data", recursive=True)

# Non-recursive (top-level only)
consolidator = DatasetConsolidator(base_dir="data", recursive=False)
```

The output will now show files from all subdirectories:
```
Found 15 CSV files across all subdirectories:
  csv_data/defi_synthetic_20251214_131315.csv
  test_data/il_test_cases_20251214_142645.csv
  results/valid_formulas_20251216_134833.csv
  ...
"""

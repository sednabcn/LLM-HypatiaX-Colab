"""
Risk Dataset Consolidator
Merge multiple timestamped risk datasets into unique, deduplicated versions
"""

import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import hashlib


class RiskDatasetConsolidator:
    """Consolidate multiple risk datasets into unique, deduplicated versions."""
    
    def __init__(self, base_dir: str = "data", recursive: bool = True):
        self.base_dir = Path(base_dir)
        self.recursive = recursive
        self.processed_dir = self.base_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        
        # Scan all files
        if recursive:
            self.csv_files = list(self.base_dir.rglob("*.csv"))
            self.json_files = list(self.base_dir.rglob("*.json"))
        else:
            self.csv_files = list(self.base_dir.glob("*.csv"))
            self.json_files = list(self.base_dir.glob("*.json"))
        
        # Exclude processed files
        self.csv_files = [f for f in self.csv_files if 'processed' not in str(f)]
        self.json_files = [f for f in self.json_files if 'processed' not in str(f)]
    
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
    
    def get_latest_files(self) -> Dict[str, Path]:
        """Get the most recent version of each dataset type."""
        patterns = {
            'historical_prices': 'historical_prices',
            'risk_scoring_examples': 'risk_scoring_examples',
            'risk_synthetic': 'risk_synthetic',
            'risk_comprehensive': 'risk_comprehensive'
        }
        
        latest_files = {}
        
        for key, pattern in patterns.items():
            matching = [f for f in self.csv_files if pattern in f.stem and f.suffix == '.csv']
            
            if matching:
                # Sort by modification time, get most recent
                latest_files[key] = max(matching, key=lambda f: f.stat().st_mtime)
        
        return latest_files
    
    def merge_csvs(self, csv_paths: List[Path], output_name: str) -> pd.DataFrame:
        """Merge multiple CSV files and deduplicate."""
        print(f"\nMerging {len(csv_paths)} files for {output_name}:")
        
        dfs = []
        for path in csv_paths:
            try:
                df = pd.read_csv(path)
                dfs.append(df)
                print(f"  ✓ Loaded {path.name}: {len(df)} rows, {len(df.columns)} cols")
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
    
    def consolidate_json_data(self, json_paths: List[Path]) -> Dict:
        """Consolidate multiple JSON files."""
        print(f"\nConsolidating {len(json_paths)} JSON files:")
        
        all_data = {}
        
        for path in json_paths:
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                
                # Determine data type
                if isinstance(data, list):
                    data_count = len(data)
                    data_type = "list"
                elif isinstance(data, dict):
                    data_count = len(data)
                    data_type = "dict"
                else:
                    data_count = 1
                    data_type = type(data).__name__
                
                # Store with file stem as key
                all_data[path.stem] = {
                    'data': data,
                    'type': data_type,
                    'count': data_count,
                    'source': str(path.relative_to(self.base_dir)),
                    'modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                }
                
                print(f"  ✓ Loaded {path.name}: {data_type} with {data_count} items")
            except Exception as e:
                print(f"  ✗ Failed to load {path.name}: {e}")
        
        print(f"  Total JSON files consolidated: {len(all_data)}")
        return all_data
    
    def create_unified_dataset(self):
        """Create unified, deduplicated datasets."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("=" * 80)
        print("RISK DATASET CONSOLIDATION")
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
                print(f"✓ {name}: {len(unique_df)} unique rows (removed {duplicates} dupes) -> {output_path.name}")
            except Exception as e:
                print(f"✗ {name}: Failed - {e}")
        
        # Strategy 2: Merge all versions of each dataset type
        print("\n[STRATEGY 2] Merging All Versions")
        
        dataset_types = [
            'historical_prices',
            'risk_scoring_examples',
            'risk_synthetic'
        ]
        
        for dtype in dataset_types:
            matching = [f for f in self.csv_files if dtype in f.stem and f.suffix == '.csv']
            
            if matching:
                merged_df = self.merge_csvs(matching, dtype)
                if not merged_df.empty:
                    output_path = self.processed_dir / f"{dtype}_merged_{timestamp}.csv"
                    merged_df.to_csv(output_path, index=False)
                    print(f"  ✓ Saved: {output_path.name}")
        
        # Strategy 3: Consolidate all JSON data
        print("\n[STRATEGY 3] Consolidating JSON Data")
        
        if self.json_files:
            consolidated = self.consolidate_json_data(self.json_files)
            
            # Save consolidated JSON
            output_path = self.processed_dir / f"json_unified_{timestamp}.json"
            with open(output_path, 'w') as f:
                json.dump(consolidated, f, indent=2)
            print(f"  ✓ Saved unified JSON: {output_path.name}")
            
            # Create summary
            summary = {
                'total_files': len(consolidated),
                'file_types': {k: v['type'] for k, v in consolidated.items()},
                'created_at': timestamp
            }
            summary_path = self.processed_dir / f"json_summary_{timestamp}.json"
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
        
        # Strategy 4: Create master unified dataset
        print("\n[STRATEGY 4] Creating Master Unified Dataset")
        self.create_master_dataset(timestamp)
        
        print("\n" + "=" * 80)
        print("CONSOLIDATION COMPLETE")
        print(f"Output directory: {self.processed_dir}")
        print("=" * 80)
    
    def create_master_dataset(self, timestamp: str):
        """Create a single master dataset combining all CSV data."""
        all_data = []
        
        for csv_file in self.csv_files:
            try:
                df = pd.read_csv(csv_file)
                df['source_file'] = csv_file.stem
                df['source_path'] = str(csv_file.relative_to(self.base_dir))
                all_data.append(df)
            except Exception as e:
                print(f"  ✗ Failed to load {csv_file.name}: {e}")
        
        if all_data:
            master_df = pd.concat(all_data, ignore_index=True)
            unique_master, duplicates = self.deduplicate_dataframe(master_df)
            
            output_path = self.processed_dir / f"risk_master_dataset_{timestamp}.csv"
            unique_master.to_csv(output_path, index=False)
            
            print(f"  Master dataset: {len(unique_master)} unique rows")
            print(f"  Removed {duplicates} duplicates")
            print(f"  Sources: {unique_master['source_path'].nunique()} files")
            print(f"  Columns: {len(unique_master.columns)}")
            print(f"  ✓ Saved: {output_path.name}")
            
            # Create summary statistics
            summary = {
                'total_rows': len(unique_master),
                'total_columns': len(unique_master.columns),
                'duplicates_removed': duplicates,
                'source_files': unique_master['source_path'].unique().tolist(),
                'created_at': timestamp,
                'column_names': list(unique_master.columns),
                'data_types': unique_master.dtypes.astype(str).to_dict()
            }
            
            summary_path = self.processed_dir / f"risk_master_dataset_{timestamp}_summary.json"
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"  ✓ Saved summary: {summary_path.name}")
    
    def analyze_datasets(self):
        """Analyze existing datasets and show statistics."""
        print("\n" + "=" * 80)
        print("RISK DATASET ANALYSIS")
        print("=" * 80)
        
        print(f"\nFound {len(self.csv_files)} CSV files:")
        
        stats = []
        for csv_file in sorted(self.csv_files):
            try:
                df = pd.read_csv(csv_file)
                stats.append({
                    'file': csv_file.name,
                    'rows': len(df),
                    'cols': len(df.columns),
                    'size_kb': csv_file.stat().st_size // 1024,
                    'modified': datetime.fromtimestamp(csv_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                })
            except Exception as e:
                stats.append({
                    'file': csv_file.name,
                    'rows': 'ERROR',
                    'cols': 'ERROR',
                    'size_kb': csv_file.stat().st_size // 1024,
                    'modified': datetime.fromtimestamp(csv_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                })
        
        if stats:
            stats_df = pd.DataFrame(stats)
            print("\n" + stats_df.to_string(index=False))
        
        # JSON analysis
        print(f"\n\nFound {len(self.json_files)} JSON files:")
        
        json_stats = []
        for json_file in sorted(self.json_files):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    count = len(data)
                    dtype = "list"
                elif isinstance(data, dict):
                    count = len(data)
                    dtype = "dict"
                else:
                    count = 1
                    dtype = type(data).__name__
                
                json_stats.append({
                    'file': json_file.name,
                    'type': dtype,
                    'items': count,
                    'size_kb': json_file.stat().st_size // 1024,
                    'modified': datetime.fromtimestamp(json_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                })
            except:
                json_stats.append({
                    'file': json_file.name,
                    'type': 'ERROR',
                    'items': 'ERROR',
                    'size_kb': json_file.stat().st_size // 1024,
                    'modified': datetime.fromtimestamp(json_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                })
        
        if json_stats:
            json_df = pd.DataFrame(json_stats)
            print("\n" + json_df.to_string(index=False))
        
        # Show dataset type breakdown
        print("\n" + "=" * 80)
        print("DATASET TYPE BREAKDOWN")
        print("=" * 80)
        
        type_counts = {}
        for csv_file in self.csv_files:
            # Extract base type (before timestamp)
            base_name = csv_file.stem.split('_2025')[0] if '_2025' in csv_file.stem else csv_file.stem
            type_counts[base_name] = type_counts.get(base_name, 0) + 1
        
        print("\nCSV Dataset Types:")
        for dtype, count in sorted(type_counts.items()):
            print(f"  {dtype}: {count} version(s)")
        
        # Recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print("\n1. Use 'latest' files for most recent data")
        print("2. Use 'merged' files for comprehensive historical data")
        print("3. Use 'risk_master_dataset' for all-in-one analysis")
        print("4. Check 'json_unified' for all JSON data consolidated")
        print(f"\n✓ Recursive scanning: {self.recursive}")
        print(f"✓ Total CSV files found: {len(self.csv_files)}")
        print(f"✓ Total JSON files found: {len(self.json_files)}")


def main():
    """Main execution."""
    # Enable recursive scanning by default
    consolidator = RiskDatasetConsolidator(base_dir="data", recursive=True)
    
    # Analyze current state
    consolidator.analyze_datasets()
    
    # Create unified datasets
    consolidator.create_unified_dataset()
    
    print("\n✓ Consolidation complete! Check the 'data/processed' directory.")
    print(f"✓ Scanned {len(consolidator.csv_files)} CSV files")
    print(f"✓ Scanned {len(consolidator.json_files)} JSON files")


if __name__ == "__main__":
    main()

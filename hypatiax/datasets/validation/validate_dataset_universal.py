"""
Universal Dataset Validator
============================
Validates CSV and JSON datasets with comprehensive statistics and quality checks.

Supports:
- CSV files (with headers)
- JSON files (list of objects or formula results)
- Automatic format detection
- General data quality metrics
- Formula-specific validation (when applicable)
"""

import csv
import glob
import json
import os
from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple, Union

import numpy as np


class DatasetValidator:
    """Universal dataset validator for CSV and JSON files."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results = {
            "files_processed": 0,
            "total_records": 0,
            "valid_records": 0,
            "file_details": {},
            "issues": [],
            "statistics": {},
        }

    def load_csv(self, filepath: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Load and analyze CSV file."""
        try:
            records = []
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                    records.append(dict(row))

            metadata = {
                "format": "CSV",
                "headers": headers,
                "columns": len(headers) if headers else 0,
                "rows": len(records),
            }

            return records, metadata

        except Exception as e:
            self.results["issues"].append({"type": "LOAD_ERROR", "file": filepath, "error": str(e)})
            return [], {"format": "CSV", "error": str(e)}

    def load_json(self, filepath: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Load and analyze JSON file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle different JSON structures
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                # Check if it's a wrapper with results
                if "results" in data:
                    records = data["results"]
                elif "data" in data:
                    records = data["data"]
                else:
                    records = [data]  # Single record
            else:
                records = []

            metadata = {
                "format": "JSON",
                "structure": "list" if isinstance(data, list) else "object",
                "records": len(records),
            }

            return records, metadata

        except json.JSONDecodeError as e:
            self.results["issues"].append({"type": "JSON_PARSE_ERROR", "file": filepath, "error": str(e)})
            return [], {"format": "JSON", "error": str(e)}
        except Exception as e:
            self.results["issues"].append({"type": "LOAD_ERROR", "file": filepath, "error": str(e)})
            return [], {"format": "JSON", "error": str(e)}

    def detect_dataset_type(self, records: List[Dict[str, Any]]) -> str:
        """Detect if dataset is formula-based or general data."""
        if not records:
            return "empty"

        # Check first few records for formula-specific fields
        sample = records[: min(5, len(records))]
        formula_fields = {"validation", "discovered_equation", "r2_score", "domain"}

        for record in sample:
            if any(field in record for field in formula_fields):
                return "formula"

        return "general"

    def analyze_general_data(self, records: List[Dict[str, Any]], filename: str) -> Dict[str, Any]:
        """Analyze general CSV/JSON data."""
        if not records:
            return {
                "type": "general",
                "total_records": 0,
                "valid_records": 0,
                "columns": [],
                "issues": [{"type": "EMPTY_DATASET", "file": filename}],
            }

        # Get all unique column names
        all_columns = set()
        for record in records:
            all_columns.update(record.keys())

        column_stats = {}
        for col in all_columns:
            values = [record.get(col) for record in records]
            non_null = [v for v in values if v not in (None, "", "null", "NULL", "None")]

            # Detect data type
            if non_null:
                sample_val = non_null[0]
                if isinstance(sample_val, (int, float)):
                    dtype = "numeric"
                elif isinstance(sample_val, bool):
                    dtype = "boolean"
                else:
                    dtype = "string"
            else:
                dtype = "unknown"

            column_stats[col] = {
                "total": len(values),
                "non_null": len(non_null),
                "null_count": len(values) - len(non_null),
                "null_percentage": (len(values) - len(non_null)) / len(values) * 100,
                "data_type": dtype,
                "unique_values": len(set(str(v) for v in non_null)),
            }

            # Add numeric statistics if applicable
            if dtype == "numeric":
                numeric_vals = [float(v) for v in non_null if v not in ("", None)]
                if numeric_vals:
                    column_stats[col].update(
                        {
                            "min": min(numeric_vals),
                            "max": max(numeric_vals),
                            "mean": np.mean(numeric_vals),
                            "median": np.median(numeric_vals),
                            "std": np.std(numeric_vals),
                        }
                    )

        # Data quality checks
        issues = []

        # Check for high null rates
        for col, stats in column_stats.items():
            if stats["null_percentage"] > 50:
                issues.append({"type": "HIGH_NULL_RATE", "column": col, "percentage": stats["null_percentage"]})

        # Check for duplicate rows
        row_hashes = [hash(frozenset(record.items())) for record in records]
        duplicate_count = len(row_hashes) - len(set(row_hashes))
        if duplicate_count > 0:
            issues.append(
                {"type": "DUPLICATE_ROWS", "count": duplicate_count, "percentage": duplicate_count / len(records) * 100}
            )

        # Check for inconsistent columns (records with different keys)
        all_key_sets = [set(record.keys()) for record in records]
        if len(set(map(frozenset, all_key_sets))) > 1:
            issues.append({"type": "INCONSISTENT_COLUMNS", "message": "Records have different column sets"})

        return {
            "type": "general",
            "total_records": len(records),
            "valid_records": len(records) - duplicate_count,
            "columns": sorted(all_columns),
            "column_count": len(all_columns),
            "column_statistics": column_stats,
            "duplicate_rows": duplicate_count,
            "issues": issues,
        }

    def analyze_formula_data(self, records: List[Dict[str, Any]], filename: str) -> Dict[str, Any]:
        """Analyze formula discovery results."""
        domain_stats = defaultdict(lambda: {"count": 0, "valid": 0, "scores": [], "r2_scores": [], "formulas": []})

        for result in records:
            domain = result.get("domain", "unknown")
            validation = result.get("validation", {})

            domain_stats[domain]["count"] += 1

            valid = validation.get("valid", False)
            if valid:
                domain_stats[domain]["valid"] += 1
                domain_stats[domain]["scores"].append(validation.get("total_score", 0))
                domain_stats[domain]["r2_scores"].append(validation.get("r2_score", 0))

            domain_stats[domain]["formulas"].append(
                {
                    "description": result.get("description", "N/A"),
                    "equation": result.get("discovered_equation", "N/A"),
                    "valid": valid,
                }
            )

        # Calculate aggregated stats
        all_scores = []
        all_r2 = []
        valid_count = 0

        for stats in domain_stats.values():
            all_scores.extend(stats["scores"])
            all_r2.extend(stats["r2_scores"])
            valid_count += stats["valid"]

        return {
            "type": "formula",
            "total_records": len(records),
            "valid_records": valid_count,
            "success_rate": valid_count / len(records) if records else 0,
            "avg_score": np.mean(all_scores) if all_scores else 0,
            "median_score": np.median(all_scores) if all_scores else 0,
            "avg_r2": np.mean(all_r2) if all_r2 else 0,
            "domains": dict(domain_stats),
            "issues": self.identify_formula_issues(records),
        }

    def identify_formula_issues(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify issues in formula datasets."""
        issues = []

        for i, record in enumerate(records):
            validation = record.get("validation", {})

            if not validation.get("valid", False):
                issues.append({"type": "INVALID_FORMULA", "index": i, "description": record.get("description", "N/A")})

            r2 = validation.get("r2_score", 0)
            if validation.get("valid") and r2 < 0.8:
                issues.append({"type": "LOW_R2", "index": i, "r2_score": r2})

            if not record.get("discovered_equation"):
                issues.append({"type": "MISSING_EQUATION", "index": i})

        return issues

    def validate_file(self, filepath: str) -> Dict[str, Any]:
        """Validate a single file."""
        ext = os.path.splitext(filepath)[1].lower()
        filename = os.path.basename(filepath)

        # Load based on extension
        if ext == ".csv":
            records, metadata = self.load_csv(filepath)
        elif ext == ".json":
            records, metadata = self.load_json(filepath)
        else:
            return {"filename": filename, "error": f"Unsupported file type: {ext}", "supported": [".csv", ".json"]}

        if not records:
            return {"filename": filename, "metadata": metadata, "records": 0, "error": "No records loaded"}

        # Detect dataset type and analyze
        dataset_type = self.detect_dataset_type(records)

        if dataset_type == "formula":
            analysis = self.analyze_formula_data(records, filename)
        else:
            analysis = self.analyze_general_data(records, filename)

        return {"filename": filename, "metadata": metadata, **analysis}

    def validate_directory(
        self, directory: str = "data", pattern: str = "*", extensions: List[str] = [".csv", ".json"]
    ) -> Dict[str, Any]:
        """Validate all matching files in directory."""

        all_files = []
        for ext in extensions:
            search_pattern = os.path.join(directory, f"{pattern}{ext}")
            all_files.extend(glob.glob(search_pattern))

        if not all_files:
            print(f"❌ No files found in {directory} matching extensions: {extensions}")
            return {"error": "No files found", "directory": directory}

        if self.verbose:
            print(f"\n{'='*70}")
            print(f"{'UNIVERSAL DATASET VALIDATION':^70}")
            print(f"{'='*70}\n")
            print(f"Found {len(all_files)} file(s):")
            for f in all_files:
                print(f"  • {f}")
            print()

        # Process each file
        file_results = {}
        total_records = 0
        total_valid = 0

        for filepath in all_files:
            if self.verbose:
                print(f"Processing: {os.path.basename(filepath)}...")

            result = self.validate_file(filepath)
            file_results[filepath] = result

            total_records += result.get("total_records", 0)
            total_valid += result.get("valid_records", 0)

        # Generate summary report
        summary = {
            "files_processed": len(all_files),
            "total_records": total_records,
            "valid_records": total_valid,
            "success_rate": total_valid / total_records if total_records > 0 else 0,
            "file_results": file_results,
        }

        if self.verbose:
            self.print_summary_report(summary)

        return summary

    def print_summary_report(self, summary: Dict[str, Any]):
        """Print comprehensive validation report."""
        print(f"\n{'='*70}")
        print(f"{'VALIDATION SUMMARY':^70}")
        print(f"{'='*70}\n")

        print(f"Files Processed:     {summary['files_processed']}")
        print(f"Total Records:       {summary['total_records']:,}")
        print(f"Valid Records:       {summary['valid_records']:,}")
        print(f"Success Rate:        {summary['success_rate']*100:.1f}%")

        print(f"\n{'='*70}")
        print(f"{'FILE DETAILS':^70}")
        print(f"{'='*70}\n")

        for filepath, result in summary["file_results"].items():
            filename = os.path.basename(filepath)
            print(f"📄 {filename}")
            print(f"   Format:       {result.get('metadata', {}).get('format', 'Unknown')}")
            print(f"   Type:         {result.get('type', 'unknown')}")
            print(f"   Records:      {result.get('total_records', 0):,}")
            print(f"   Valid:        {result.get('valid_records', 0):,}")

            if result.get("type") == "general":
                print(f"   Columns:      {result.get('column_count', 0)}")
                if result.get("duplicate_rows", 0) > 0:
                    print(f"   ⚠️  Duplicates: {result['duplicate_rows']}")

            elif result.get("type") == "formula":
                print(f"   Avg Score:    {result.get('avg_score', 0):.1f}/100")
                print(f"   Avg R²:       {result.get('avg_r2', 0):.3f}")

            # Show issues
            issues = result.get("issues", [])
            if issues:
                issue_counts = Counter(issue["type"] for issue in issues)
                print(f"   ⚠️  Issues:    {len(issues)} total")
                for issue_type, count in issue_counts.most_common(3):
                    print(f"               - {issue_type}: {count}")
            else:
                print(f"   ✓ No issues")

            print()

        print(f"{'='*70}\n")

    def export_report(self, summary: Dict[str, Any], output_file: str):
        """Export validation report to JSON."""
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Convert numpy types to native Python types
            def convert_types(obj):
                if isinstance(obj, dict):
                    return {k: convert_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_types(item) for item in obj]
                elif isinstance(obj, (np.integer, np.floating)):
                    return obj.item()
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj

            summary_clean = convert_types(summary)

            with open(output_file, "w") as f:
                json.dump(summary_clean, f, indent=2)

            print(f"✓ Report exported to: {output_file}")
        except Exception as e:
            print(f"❌ Error exporting report: {e}")


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Universal Dataset Validator (CSV & JSON)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all CSV and JSON files in data directory
  python validate_dataset_universal.py --dir data

  # Validate only CSV files
  python validate_dataset_universal.py --dir data --ext .csv

  # Validate with specific pattern
  python validate_dataset_universal.py --dir data --pattern "perfume*"

  # Quiet mode with JSON export
  python validate_dataset_universal.py --quiet --export validation_report.json
        """,
    )

    parser.add_argument("--dir", default="data", help="Data directory (default: data)")
    parser.add_argument("--pattern", default="*", help="File pattern (default: *)")
    parser.add_argument("--ext", nargs="+", default=[".csv", ".json"], help="File extensions (default: .csv .json)")
    parser.add_argument("--export", type=str, help="Export report to JSON file")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")

    args = parser.parse_args()

    # Create validator
    validator = DatasetValidator(verbose=not args.quiet)

    # Run validation
    summary = validator.validate_directory(directory=args.dir, pattern=args.pattern, extensions=args.ext)

    # Export if requested
    if args.export:
        validator.export_report(summary, args.export)

    # Exit with appropriate code
    success_rate = summary.get("success_rate", 0)
    if success_rate < 0.8:
        print(f"\n⚠️  Warning: Success rate {success_rate*100:.1f}% below 80% threshold")
        exit(1)
    else:
        print(f"\n✓ Success rate {success_rate*100:.1f}% meets quality threshold")
        exit(0)


if __name__ == "__main__":
    main()


"""
# Validate all CSV and JSON files in data directory
python validate_dataset_universal.py --dir datasets

# Only CSV files
python validate_dataset_universal.py --dir datasets --ext .csv

# Only JSON files
python validate_dataset_universal.py --dir datasets --ext .json

# Specific pattern (e.g., perfume datasets)
python validate_dataset_universal.py --dir datasets --pattern "perfume*"

# Export full report
python validate_dataset_universal.py --export validation_report.json

# Quiet mode
python validate_dataset_universal.py --quiet
```

---

### **What It Validates:**

#### **For CSV/General Data:**
- ✓ Row count and column structure
- ✓ Missing values per column (with percentage)
- ✓ Data types (numeric, string, boolean)
- ✓ Duplicate rows
- ✓ Inconsistent column schemas
- ✓ Numeric statistics (min, max, mean, median, std)
- ✓ Unique value counts

#### **For Formula/JSON Data:**
- ✓ All above, PLUS:
- ✓ Validation scores
- ✓ R² metrics
- ✓ Domain-specific statistics
- ✓ Equation completeness
- ✓ Low R² warnings

---

### **Sample Output:**
```
======================================================================
                    UNIVERSAL DATASET VALIDATION
======================================================================

Found 2 file(s):
  • datasets/perfume_formulation_dataset_300.csv
  • datasets/clinical_laboratory_dataset_300.csv

Processing: perfume_formulation_dataset_300.csv...
Processing: clinical_laboratory_dataset_300.csv...

======================================================================
                        VALIDATION SUMMARY
======================================================================

Files Processed:     2
Total Records:       600
Valid Records:       600
Success Rate:        100.0%

======================================================================
                          FILE DETAILS
======================================================================

📄 perfume_formulation_dataset_300.csv
   Format:       CSV
   Type:         general
   Records:      300
   Valid:        300
   Columns:      2
   ✓ No issues

📄 clinical_laboratory_dataset_300.csv
   Format:       CSV
   Type:         general
   Records:      300
   Valid:        300
   Columns:      2
   ✓ No issues

======================================================================

✓ Success rate 100.0% meets quality threshold
"""

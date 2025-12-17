(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/datasets/finance/risk]
└─$ tree                                                                                                                     
.
├── data
│   ├── historical_prices_20251214_135738.csv
│   ├── historical_prices_20251214_135738.json
│   ├── historical_prices_20251214_142645.csv
│   ├── historical_prices_20251214_142645.json
│   ├── historical_prices.csv
│   ├── historical_prices.json
│   ├── __init__.py
│   ├── risk_comprehensive.json
│   ├── risk_scoring_examples_20251214_135738.csv
│   ├── risk_scoring_examples_20251214_135738.json
│   ├── risk_scoring_examples_20251214_142645.csv
│   ├── risk_scoring_examples_20251214_142645.json
│   ├── risk_synthetic_20251214_131315.csv
│   └── risk_synthetic_20251214_131315.json
└── __init__.py

2 directories, 15 files

┌──(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/datasets/finance/risk]
└─$ python risk_dataset_consolidator.py

================================================================================
RISK DATASET ANALYSIS
================================================================================

Found 6 CSV files:

                                     file  rows  cols  size_kb         modified
                    historical_prices.csv    90     6        5 2025-12-14 19:34
    historical_prices_20251214_135738.csv    90     6        5 2025-12-14 19:34
    historical_prices_20251214_142645.csv    90     6        5 2025-12-14 19:34
risk_scoring_examples_20251214_135738.csv     3     7        0 2025-12-14 19:34
risk_scoring_examples_20251214_142645.csv     3     7        0 2025-12-14 19:34
       risk_synthetic_20251214_131315.csv    50     9       10 2025-12-14 19:34


Found 7 JSON files:

                                      file type  items  size_kb         modified
                    historical_prices.json list     90       15 2025-12-14 19:34
    historical_prices_20251214_135738.json list     90       15 2025-12-14 19:34
    historical_prices_20251214_142645.json list     90       15 2025-12-14 19:34
                   risk_comprehensive.json list      8       77 2025-12-07 14:05
risk_scoring_examples_20251214_135738.json list      3        0 2025-12-14 19:34
risk_scoring_examples_20251214_142645.json list      3        0 2025-12-14 19:34
       risk_synthetic_20251214_131315.json dict      3      492 2025-12-14 19:34

================================================================================
DATASET TYPE BREAKDOWN
================================================================================

CSV Dataset Types:
  historical_prices: 3 version(s)
  risk_scoring_examples: 2 version(s)
  risk_synthetic: 1 version(s)

================================================================================
RECOMMENDATIONS
================================================================================

1. Use 'latest' files for most recent data
2. Use 'merged' files for comprehensive historical data
3. Use 'risk_master_dataset' for all-in-one analysis
4. Check 'json_unified' for all JSON data consolidated

✓ Recursive scanning: True
✓ Total CSV files found: 6
✓ Total JSON files found: 7
================================================================================
RISK DATASET CONSOLIDATION
================================================================================

[STRATEGY 1] Using Latest Files
✓ historical_prices: 90 unique rows (removed 0 dupes) -> historical_prices_latest.csv
✓ risk_scoring_examples: 3 unique rows (removed 0 dupes) -> risk_scoring_examples_latest.csv
✓ risk_synthetic: 50 unique rows (removed 0 dupes) -> risk_synthetic_latest.csv

[STRATEGY 2] Merging All Versions

Merging 3 files for historical_prices:
  ✓ Loaded historical_prices.csv: 90 rows, 6 cols
  ✓ Loaded historical_prices_20251214_135738.csv: 90 rows, 6 cols
  ✓ Loaded historical_prices_20251214_142645.csv: 90 rows, 6 cols
  Total rows before deduplication: 270
  Removed 90 duplicates
  Final unique rows: 180
  ✓ Saved: historical_prices_merged_20251216_200546.csv

Merging 2 files for risk_scoring_examples:
  ✓ Loaded risk_scoring_examples_20251214_142645.csv: 3 rows, 7 cols
  ✓ Loaded risk_scoring_examples_20251214_135738.csv: 3 rows, 7 cols
  Total rows before deduplication: 6
  Removed 3 duplicates
  Final unique rows: 3
  ✓ Saved: risk_scoring_examples_merged_20251216_200546.csv

Merging 1 files for risk_synthetic:
  ✓ Loaded risk_synthetic_20251214_131315.csv: 50 rows, 9 cols
  Total rows before deduplication: 50
  Removed 0 duplicates
  Final unique rows: 50
  ✓ Saved: risk_synthetic_merged_20251216_200546.csv

[STRATEGY 3] Consolidating JSON Data

Consolidating 7 JSON files:
  ✓ Loaded risk_comprehensive.json: list with 8 items
  ✓ Loaded historical_prices_20251214_135738.json: list with 90 items
  ✓ Loaded risk_scoring_examples_20251214_142645.json: list with 3 items
  ✓ Loaded historical_prices.json: list with 90 items
  ✓ Loaded historical_prices_20251214_142645.json: list with 90 items
  ✓ Loaded risk_synthetic_20251214_131315.json: dict with 3 items
  ✓ Loaded risk_scoring_examples_20251214_135738.json: list with 3 items
  Total JSON files consolidated: 7
  ✓ Saved unified JSON: json_unified_20251216_200546.json

[STRATEGY 4] Creating Master Unified Dataset
  Master dataset: 326 unique rows
  Removed 0 duplicates
  Sources: 6 files
  Columns: 23
  ✓ Saved: risk_master_dataset_20251216_200546.csv
  ✓ Saved summary: risk_master_dataset_20251216_200546_summary.json

================================================================================
CONSOLIDATION COMPLETE
Output directory: data/processed
================================================================================

✓ Consolidation complete! Check the 'data/processed' directory.
✓ Scanned 6 CSV files
✓ Scanned 7 JSON files


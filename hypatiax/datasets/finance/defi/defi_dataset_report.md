──(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/datasets/finance/defi]
└─$ python dataset_consolidator.py

================================================================================
DATASET ANALYSIS
================================================================================

Found 20 CSV files across all subdirectories:

                                            path  rows  cols         modified
       csv_data/defi_summary_20251126_205624.csv     4     8 2025-12-07 14:05
 csv_data/defi_summary_fixed_20251126_211441.csv     4     8 2025-12-07 14:05
     csv_data/defi_synthetic_20251214_131315.csv    40     9 2025-12-14 19:34
      csv_data/il_test_cases_20251214_135738.csv    40     8 2025-12-14 19:34
      csv_data/il_test_cases_20251214_142645.csv    40     7 2025-12-14 19:34
csv_data/real_pool_snapshots_20251214_135738.csv     1    10 2025-12-14 19:34
csv_data/real_pool_snapshots_20251214_142645.csv     1     9 2025-12-14 19:34
                  csv_data/uniswap_scenarios.csv     4     9 2025-12-14 19:34
  csv_data/uniswap_scenarios_20251214_135738.csv     5    10 2025-12-14 19:34
  csv_data/uniswap_scenarios_20251214_142645.csv     5    12 2025-12-14 19:34
                defi_summary_20251126_205624.csv     4     8 2025-12-07 14:05
          defi_summary_fixed_20251126_211441.csv     4     8 2025-12-07 14:05
              defi_synthetic_20251214_131315.csv    40     9 2025-12-14 19:34
               il_test_cases_20251214_135738.csv    40     8 2025-12-14 19:34
               il_test_cases_20251214_142645.csv    40     7 2025-12-14 19:34
         real_pool_snapshots_20251214_135738.csv     1    10 2025-12-14 19:34
         real_pool_snapshots_20251214_142645.csv     1     9 2025-12-14 19:34
                           uniswap_scenarios.csv     4     9 2025-12-14 19:34
           uniswap_scenarios_20251214_135738.csv     5    10 2025-12-14 19:34
           uniswap_scenarios_20251214_142645.csv     5    12 2025-12-14 19:34


Found 45 JSON files across all subdirectories

================================================================================
RECOMMENDATIONS
================================================================================

1. Use 'latest' files for most recent data
2. Use 'merged' files for comprehensive historical data
3. Use 'master' dataset for all-in-one analysis
4. Check 'formulas_unified' for all formula definitions

✓ Recursive scanning: True
✓ Scanned directories: 3 unique paths
================================================================================
DEFI DATASET CONSOLIDATION
================================================================================

[STRATEGY 1] Using Latest Files
✓ defi_summary: 4 unique rows -> defi_summary_latest.csv
✓ defi_synthetic: 40 unique rows -> defi_synthetic_latest.csv
✓ il_test_cases: 40 unique rows -> il_test_cases_latest.csv
✓ real_pool_snapshots: 1 unique rows -> real_pool_snapshots_latest.csv
✓ uniswap_scenarios: 5 unique rows -> uniswap_scenarios_latest.csv

[STRATEGY 2] Merging All Versions

Merging 4 files for defi_summary:
  ✓ Loaded defi_summary_fixed_20251126_211441.csv: 4 rows
  ✓ Loaded defi_summary_20251126_205624.csv: 4 rows
  ✓ Loaded defi_summary_fixed_20251126_211441.csv: 4 rows
  ✓ Loaded defi_summary_20251126_205624.csv: 4 rows
  Total rows before deduplication: 16
  Removed 8 duplicates
  Final unique rows: 8
  ✓ Saved: defi_summary_merged_20251216_194946.csv

Merging 2 files for defi_synthetic:
  ✓ Loaded defi_synthetic_20251214_131315.csv: 40 rows
  ✓ Loaded defi_synthetic_20251214_131315.csv: 40 rows
  Total rows before deduplication: 80
  Removed 40 duplicates
  Final unique rows: 40
  ✓ Saved: defi_synthetic_merged_20251216_194946.csv

Merging 4 files for il_test_cases:
  ✓ Loaded il_test_cases_20251214_142645.csv: 40 rows
  ✓ Loaded il_test_cases_20251214_135738.csv: 40 rows
  ✓ Loaded il_test_cases_20251214_142645.csv: 40 rows
  ✓ Loaded il_test_cases_20251214_135738.csv: 40 rows
  Total rows before deduplication: 160
  Removed 80 duplicates
  Final unique rows: 80
  ✓ Saved: il_test_cases_merged_20251216_194946.csv

Merging 4 files for real_pool_snapshots:
  ✓ Loaded real_pool_snapshots_20251214_142645.csv: 1 rows
  ✓ Loaded real_pool_snapshots_20251214_135738.csv: 1 rows
  ✓ Loaded real_pool_snapshots_20251214_142645.csv: 1 rows
  ✓ Loaded real_pool_snapshots_20251214_135738.csv: 1 rows
  Total rows before deduplication: 4
  Removed 2 duplicates
  Final unique rows: 2
  ✓ Saved: real_pool_snapshots_merged_20251216_194946.csv

Merging 6 files for uniswap_scenarios:
  ✓ Loaded uniswap_scenarios_20251214_135738.csv: 5 rows
  ✓ Loaded uniswap_scenarios_20251214_142645.csv: 5 rows
  ✓ Loaded uniswap_scenarios.csv: 4 rows
  ✓ Loaded uniswap_scenarios_20251214_135738.csv: 5 rows
  ✓ Loaded uniswap_scenarios_20251214_142645.csv: 5 rows
  ✓ Loaded uniswap_scenarios.csv: 4 rows
  Total rows before deduplication: 28
  Removed 18 duplicates
  Final unique rows: 10
  ✓ Saved: uniswap_scenarios_merged_20251216_194946.csv

[STRATEGY 3] Consolidating Formulas

Consolidating 45 formula files:
  ✓ Loaded il_test_cases_20251214_135738.json: 0 formulas
  ✓ Loaded real_pool_snapshots_20251214_142645.json: 0 formulas
  ✓ Loaded valid_formulas_20251216_134833.json: 0 formulas
  ✓ Loaded defi_synthetic_20251214_131315.json: 0 formulas
  ✓ Loaded real_pool_snapshots_20251214_135738.json: 0 formulas
  ✓ Loaded uniswap_scenarios_20251214_142645.json: 0 formulas
  ✓ Loaded defi_formulas_fixed_20251126_211441.json: 0 formulas
  ✓ Loaded uniswap_scenarios_20251214_135738.json: 0 formulas
  ✓ Loaded il_test_cases_20251214_142645.json: 0 formulas
  ✓ Loaded uniswap_scenarios.json: 0 formulas
  ✓ Loaded defi_formulas_20251126_205624.json: 0 formulas
  ✓ Loaded formulas/real_pool_snapshots_20251214_135738_fixed.json: 0 formulas
  ✓ Loaded formulas/uniswap_scenarios_fixed.json: 0 formulas
  ✓ Loaded formulas/real_pool_snapshots_20251214_142645_fixed.json: 0 formulas
  ✓ Loaded formulas/il_test_cases_20251214_142645_fixed.json: 0 formulas
  ✓ Loaded formulas/il_test_cases_20251214_135738.json: 0 formulas
  ✓ Loaded formulas/uniswap_scenarios_20251214_135738_fixed.json: 0 formulas
  ✓ Loaded formulas/defi_formulas_20251126_205624_fixed.json: 0 formulas
  ✓ Loaded formulas/real_pool_snapshots_20251214_142645.json: 0 formulas
  ✓ Loaded formulas/valid_formulas_20251216_134833.json: 0 formulas
  ✓ Loaded formulas/defi_synthetic_20251214_131315.json: 0 formulas
  ✓ Loaded formulas/uniswap_scenarios_20251214_142645_fixed.json: 0 formulas
  ✓ Loaded formulas/real_pool_snapshots_20251214_135738.json: 0 formulas
  ✓ Loaded formulas/uniswap_scenarios_20251214_142645.json: 0 formulas
  ✓ Loaded formulas/defi_formulas_fixed_20251126_211441.json: 0 formulas
  ✓ Loaded formulas/uniswap_scenarios_20251214_135738.json: 0 formulas
  ✓ Loaded formulas/il_test_cases_20251214_142645.json: 0 formulas
  ✓ Loaded formulas/uniswap_scenarios.json: 0 formulas
  ✓ Loaded formulas/il_test_cases_20251214_135738_fixed.json: 0 formulas
  ✓ Loaded formulas/defi_synthetic_20251214_131315_fixed.json: 0 formulas
  ✓ Loaded formulas/valid_formulas_20251216_134833_fixed.json: 0 formulas
  ✓ Loaded formulas/defi_formulas_20251126_205624.json: 0 formulas
  ✓ Loaded formulas/defi_formulas_fixed_20251126_211441_fixed.json: 0 formulas
  ✓ Loaded test_data/il_test_cases_20251214_135738.json: 0 formulas
  ✓ Loaded test_data/real_pool_snapshots_20251214_142645.json: 0 formulas
  ✓ Loaded test_data/real_pool_snapshots_20251214_135738.json: 0 formulas
  ✓ Loaded test_data/uniswap_scenarios_20251214_142645.json: 0 formulas
  ✓ Loaded test_data/uniswap_scenarios_20251214_135738.json: 0 formulas
  ✓ Loaded test_data/il_test_cases_20251214_142645.json: 0 formulas
  ✓ Loaded test_data/uniswap_scenarios.json: 0 formulas
  ✓ Loaded results/discovered_20251216_134950.json: 0 formulas
  ✓ Loaded results/valid_formulas_20251216_134833.json: 0 formulas
  ✓ Loaded results/defi_synthetic_20251214_131315.json: 0 formulas
  ✓ Loaded results/defi_formulas_fixed_20251126_211441.json: 0 formulas
  ✓ Loaded results/defi_formulas_20251126_205624.json: 0 formulas
  Total unique formulas: 0

[STRATEGY 4] Creating Master Unified Dataset
  Master dataset: 288 unique rows
  Removed 0 duplicates
  Sources: 20 files
  ✓ Saved: master_dataset_20251216_194946.csv

================================================================================
CONSOLIDATION COMPLETE
Output directory: data/processed
================================================================================

✓ Consolidation complete! Check the 'processed' directory.
✓ Scanned 37 CSV files recursively
✓ Scanned 49 JSON files recursively

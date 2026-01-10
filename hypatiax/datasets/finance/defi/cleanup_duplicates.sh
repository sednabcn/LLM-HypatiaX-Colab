#!/bin/bash
# DeFi Dataset Cleanup Script
# Removes duplicate/outdated files after consolidation
# Keep only the consolidated files in data/processed/

echo "======================================================================"
echo "DeFi Dataset Cleanup - Remove Duplicates"
echo "======================================================================"
echo ""
echo "⚠️  WARNING: This will DELETE files!"
echo "Make sure you have:"
echo "  1. Run dataset_consolidator.py successfully"
echo "  2. Verified data/processed/ contains your consolidated data"
echo "  3. Made a backup if needed"
echo ""
read -p "Continue with cleanup? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Navigate to the defi directory
cd "$(dirname "$0")"

echo ""
echo "======================================================================"
echo "STEP 1: Remove Duplicate CSV Files"
echo "======================================================================"

# These are duplicates found in both root and csv_data/
FILES_TO_REMOVE=(
    "defi_summary_20251126_205624.csv"
    "defi_summary_fixed_20251126_211441.csv"
    "defi_synthetic_20251214_131315.csv"
    "il_test_cases_20251214_135738.csv"
    "il_test_cases_20251214_142645.csv"
    "real_pool_snapshots_20251214_135738.csv"
    "real_pool_snapshots_20251214_142645.csv"
    "uniswap_scenarios.csv"
    "uniswap_scenarios_20251214_135738.csv"
    "uniswap_scenarios_20251214_142645.csv"
)

for file in "${FILES_TO_REMOVE[@]}"; do
    # Remove from root data directory
    if [ -f "data/$file" ]; then
        echo "🗑️  Removing data/$file"
        rm "data/$file"
    fi
done

echo ""
echo "======================================================================"
echo "STEP 2: Remove Old Timestamped Versions (Keep Latest Only)"
echo "======================================================================"

# Remove older timestamped versions from csv_data/
OLD_VERSIONS=(
    "csv_data/defi_summary_20251126_205624.csv"
    "csv_data/il_test_cases_20251214_135738.csv"
    "csv_data/real_pool_snapshots_20251214_135738.csv"
    "csv_data/uniswap_scenarios_20251214_135738.csv"
    "csv_data/uniswap_scenarios.csv"
)

for file in "${OLD_VERSIONS[@]}"; do
    if [ -f "data/$file" ]; then
        echo "🗑️  Removing data/$file (older version)"
        rm "data/$file"
    fi
done

echo ""
echo "======================================================================"
echo "STEP 3: Remove Backup JSON Files"
echo "======================================================================"

# Remove .backup files
find data/ -name "*.backup" -type f | while read file; do
    echo "🗑️  Removing $file"
    rm "$file"
done

echo ""
echo "======================================================================"
echo "STEP 4: Clean Up Redundant JSON Files"
echo "======================================================================"

# Remove duplicate JSON files in root (keep only in formulas/ or test_data/)
ROOT_JSON=(
    "defi_formulas_20251126_205624.json"
    "defi_formulas_fixed_20251126_211441.json"
    "defi_synthetic_20251214_131315.json"
    "il_test_cases_20251214_135738.json"
    "il_test_cases_20251214_142645.json"
    "real_pool_snapshots_20251214_135738.json"
    "real_pool_snapshots_20251214_142645.json"
    "uniswap_scenarios_20251214_135738.json"
    "uniswap_scenarios_20251214_142645.json"
    "uniswap_scenarios.json"
    "valid_formulas_20251216_134833.json"
)

for file in "${ROOT_JSON[@]}"; do
    if [ -f "data/$file" ]; then
        echo "🗑️  Removing data/$file (duplicate)"
        rm "data/$file"
    fi
done

echo ""
echo "======================================================================"
echo "STEP 5: Optional - Archive Old CSV Data"
echo "======================================================================"

read -p "Move remaining old files to archive? (yes/no): " archive_confirm

if [ "$archive_confirm" == "yes" ]; then
    mkdir -p data/archive/csv_old
    mkdir -p data/archive/json_old

    # Archive old CSV files
    find data/csv_data -name "*_2025*.csv" -type f | while read file; do
        echo "📦 Archiving $(basename $file)"
        mv "$file" data/archive/csv_old/
    done

    echo "✓ Old files archived to data/archive/"
fi

echo ""
echo "======================================================================"
echo "CLEANUP SUMMARY"
echo "======================================================================"
echo ""
echo "✓ Removed duplicate files from root directory"
echo "✓ Removed older timestamped versions"
echo "✓ Removed .backup files"
echo "✓ Cleaned up redundant JSON files"

if [ "$archive_confirm" == "yes" ]; then
    echo "✓ Archived old timestamped files"
fi

echo ""
echo "📂 Your clean, consolidated data is in: data/processed/"
echo ""
echo "Recommended files to use:"
echo "  - master_dataset_20251216_194946.csv (all data combined)"
echo "  - defi_synthetic_latest.csv"
echo "  - il_test_cases_latest.csv"
echo "  - uniswap_scenarios_latest.csv"
echo ""
echo "======================================================================"
echo "Cleanup Complete!"
echo "======================================================================"

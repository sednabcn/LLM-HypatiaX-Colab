#!/bin/bash
# Quick check script for data dependencies and models

PROJECT_ROOT="${1:-.}"
cd "$PROJECT_ROOT" || exit 1

echo "🔍 Quick Data & Model Check"
echo "=" | head -c 80
echo ""
echo "📁 Project: $(pwd)"
echo ""

# Check datasets
echo "📊 DATASETS:"
if [ -d "datasets" ] || [ -d "data" ] || [ -d "hypatiax/data" ]; then
    for dir in datasets data hypatiax/data hypatiax/datasets; do
        if [ -d "$dir" ]; then
            count=$(find "$dir" -type f 2>/dev/null | wc -l)
            size=$(du -sh "$dir" 2>/dev/null | cut -f1)
            echo "  ✅ $dir: $count files ($size)"
        fi
    done
else
    echo "  ❌ No dataset directories found"
fi

echo ""
echo "🧠 SPACY MODELS:"
# Check for spaCy model directories
found_models=0
for dir in models hypatiax/data_spacy hypatiax/custom_ner; do
    if [ -d "$dir" ]; then
        while IFS= read -r -d '' model_dir; do
            if [ -f "$model_dir/meta.json" ] || [ -f "$model_dir/config.cfg" ]; then
                echo "  ✅ Found: $model_dir"
                found_models=$((found_models + 1))
            fi
        done < <(find "$dir" -type d -print0 2>/dev/null)
    fi
done

if [ $found_models -eq 0 ]; then
    echo "  ⚠️  No custom models found"
fi

echo ""
echo "📄 DATA FILES:"
# Count different file types
jsonl_count=$(find . -name "*.jsonl" -type f 2>/dev/null | wc -l)
csv_count=$(find . -name "*.csv" -type f 2>/dev/null | wc -l)
json_count=$(find . -name "*.json" -type f 2>/dev/null | wc -l)
pkl_count=$(find . -name "*.pkl" -type f 2>/dev/null | wc -l)

echo "  JSONL files: $jsonl_count"
echo "  CSV files: $csv_count"
echo "  JSON files: $json_count"
echo "  Pickle files: $pkl_count"

echo ""
echo "📏 RULE FILES:"
ruler_count=$(find . -name "ruler*.jsonl" -type f 2>/dev/null | wc -l)
if [ $ruler_count -gt 0 ]; then
    echo "  ✅ Found $ruler_count ruler files:"
    find . -name "ruler*.jsonl" -type f 2>/dev/null | head -5 | while read -r file; do
        lines=$(wc -l < "$file" 2>/dev/null || echo "?")
        echo "     - $file ($lines rules)"
    done
else
    echo "  ⚠️  No ruler files found"
fi

echo ""
echo "📦 PYTHON ENVIRONMENT:"
if command -v python &> /dev/null; then
    python_version=$(python --version 2>&1)
    echo "  Python: $python_version"
    
    # Check key packages
    for pkg in spacy pandas numpy; do
        if python -c "import $pkg" 2>/dev/null; then
            version=$(python -c "import $pkg; print($pkg.__version__)" 2>/dev/null)
            echo "  ✅ $pkg: $version"
        else
            echo "  ❌ $pkg: not installed"
        fi
    done
else
    echo "  ❌ Python not found"
fi

echo ""
echo "=" | head -c 80
echo ""
echo "✅ Quick check complete"
echo ""
echo "💡 For detailed check, run:"
echo "   python check_data_and_models.py"

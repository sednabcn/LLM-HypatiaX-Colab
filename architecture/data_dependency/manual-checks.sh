#3. Manual Checks
# Find all datasets
find . -type d -name "dataset*" -o -name "data"

# List all data files
find . -name "*.jsonl" -o -name "*.csv" -o -name "*.pkl"

# Check spaCy models
find . -name "meta.json" -o -name "config.cfg" | grep -v node_modules

# Count rules in JSONL files
for f in $(find . -name "ruler*.jsonl"); do
    echo "$f: $(wc -l < "$f") rules"
done

# Check model directories
ls -lh hypatiax/data_spacy/queries/tableau/

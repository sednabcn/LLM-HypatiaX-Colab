# 5. Check Specific Locations
# Check your specific structure
cd ~/Downloads/LLM-HypatiaX-OLD

# Datasets
ls -R datasets/ 2>/dev/null || echo "No datasets/ directory"
ls -R data/ 2>/dev/null || echo "No data/ directory"

# Models
ls -R hypatiax/data_spacy/ 2>/dev/null || echo "No data_spacy/"
find hypatiax -name "*.spacy" -o -name "meta.json"

# Rule files
find hypatiax -name "ruler*.jsonl" -exec echo "Found: {}" \; -exec wc -l {} \;

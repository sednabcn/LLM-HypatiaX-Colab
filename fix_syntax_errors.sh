#!/bin/bash

# Fix unterminated strings in examples
files=(
  "hypatiax/examples/agent_example.py"
  "hypatiax/examples/hybrid_example.py"
  "hypatiax/examples/llm_example.py"
  "hypatiax/examples/transformer_example.py"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    # Add closing quote to unterminated print statements
    sed -i 's/print(".*Example$/&")/' "$file"
  fi
done

# Fix demo files
sed -i '1s/^/"""/' hypatiax/demo/demo_web_api.py
sed -i '1s/$/"""/' hypatiax/demo/demo_web_api.py

echo "Fixed common syntax errors. Check files manually for complex issues."

#!/bin/bash

# Fix YAML - add document start if missing
if ! head -n 1 hypatiax/config/new_config/llm_provider_config.yml | grep -q "^---"; then
    sed -i '1s/^/---\n/' hypatiax/config/new_config/llm_provider_config.yml
fi

# Fix empty JSON files
[ ! -s hypatiax/experiments/experiments_registry.json ] && echo '{}' > hypatiax/experiments/experiments_registry.json
[ ! -s frontend/package.json ] && echo '{"name": "frontend", "version": "1.0.0"}' > frontend/package.json

# Run pre-commit again
pre-commit run --all-files

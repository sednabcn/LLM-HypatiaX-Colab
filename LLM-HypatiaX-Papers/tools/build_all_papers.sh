#!/bin/bash

echo "Building all papers..."
for paper in papers/*/; do
    if [ -f "$paper/scripts/build.sh" ]; then
        echo "→ Building $(basename $paper)..."
        (cd "$paper" && bash scripts/build.sh)
    fi
done
echo "✓ All papers built!"

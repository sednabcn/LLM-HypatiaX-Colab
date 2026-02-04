#!/bin/bash

echo "Syncing shared data to all papers..."
for paper in papers/*/; do
    if [ -d "$paper/data" ]; then
        echo "→ Syncing to $(basename $paper)..."
        cd "$paper/data"
        ln -sf ../../../shared/data/all_systems_merged.json . 2>/dev/null || true
        cd - > /dev/null
    fi
done
echo "✓ Data synced!"

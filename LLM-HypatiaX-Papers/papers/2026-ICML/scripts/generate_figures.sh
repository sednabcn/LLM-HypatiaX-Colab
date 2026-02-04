#!/bin/bash
set -e

echo "Generating figures..."
cd ../src

# Run Python scripts to generate figures
python3 plot_results.py

echo "✓ Figures generated successfully!"

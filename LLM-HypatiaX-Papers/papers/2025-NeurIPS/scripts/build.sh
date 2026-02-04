#!/bin/bash
set -e

echo "Building paper..."
cd ../paper
make clean
make
echo "✓ Paper built successfully!"
echo "PDF: paper/main.pdf"

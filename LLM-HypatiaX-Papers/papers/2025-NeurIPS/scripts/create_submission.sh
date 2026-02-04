#!/bin/bash
set -e

SUBMISSION_DIR="../submission/$(date +%Y%m%d)"
mkdir -p "$SUBMISSION_DIR"

echo "Creating submission package..."

# Copy paper
cp ../paper/main.pdf "$SUBMISSION_DIR/"
cp ../paper/*.tex "$SUBMISSION_DIR/"
cp ../paper/*.bib "$SUBMISSION_DIR/"

# Copy figures
cp -r ../figures "$SUBMISSION_DIR/"

# Create archive
cd "$SUBMISSION_DIR/.."
tar -czf "submission_$(date +%Y%m%d).tar.gz" "$(basename $SUBMISSION_DIR)"

echo "✓ Submission package created!"
echo "Location: $SUBMISSION_DIR"

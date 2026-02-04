#!/bin/bash

if [ $# -lt 3 ]; then
    echo "Usage: $0 <paper-id> <venue> <year>"
    echo "Example: $0 2026-ICLR ICLR 2026"
    exit 1
fi

PAPER_ID=$1
VENUE=$2
YEAR=$3

echo "Creating new paper: $PAPER_ID ($VENUE $YEAR)"

# Use template to create paper
cp -r templates/paper_template "papers/$PAPER_ID"

# Update README
sed -i "s/PAPER_ID/$PAPER_ID/g" "papers/$PAPER_ID/README.md"
sed -i "s/VENUE/$VENUE/g" "papers/$PAPER_ID/README.md"
sed -i "s/YEAR/$YEAR/g" "papers/$PAPER_ID/README.md"

echo "✓ Paper created at papers/$PAPER_ID"

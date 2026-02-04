#!/bin/bash
# Compile HypatiaX LaTeX manuscript

set -e  # Exit on error

echo "======================================"
echo "Compiling HypatiaX JMLR Manuscript"
echo "======================================"
echo ""

# Check if figures exist
if [ ! -d "figures" ] || [ -z "$(ls -A figures/*.pdf 2>/dev/null)" ]; then
    echo "Figures not found. Generating..."
    python3 generate_figures.py
    echo ""
fi

# Clean previous compilation files
echo "Cleaning previous build files..."
rm -f *.aux *.log *.bbl *.blg *.out *.toc *.lof *.lot
echo ""

# First LaTeX pass
echo "[1/4] Running pdflatex (first pass)..."
pdflatex -interaction=nonstopmode hypatiax_manuscript.tex > /dev/null 2>&1 || {
    echo "Error in first pdflatex pass. Check hypatiax_manuscript.log"
    exit 1
}

# Run BibTeX
echo "[2/4] Running bibtex..."
bibtex hypatiax_manuscript > /dev/null 2>&1 || {
    echo "Warning: BibTeX encountered errors (this is normal if .bib file is missing)"
}

# Second LaTeX pass
echo "[3/4] Running pdflatex (second pass)..."
pdflatex -interaction=nonstopmode hypatiax_manuscript.tex > /dev/null 2>&1 || {
    echo "Error in second pdflatex pass. Check hypatiax_manuscript.log"
    exit 1
}

# Third LaTeX pass for cross-references
echo "[4/4] Running pdflatex (final pass)..."
pdflatex -interaction=nonstopmode hypatiax_manuscript.tex > /dev/null 2>&1 || {
    echo "Error in final pdflatex pass. Check hypatiax_manuscript.log"
    exit 1
}

echo ""
echo "======================================"
echo "✓ Compilation successful!"
echo "======================================"
echo ""
echo "Output: hypatiax_manuscript.pdf"
echo ""

# Display PDF info
if command -v pdfinfo &> /dev/null; then
    echo "PDF Information:"
    pdfinfo hypatiax_manuscript.pdf | grep -E "Pages|PDF version|File size"
    echo ""
fi

# Clean auxiliary files (optional)
read -p "Clean auxiliary files? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleaning auxiliary files..."
    rm -f *.aux *.log *.bbl *.blg *.out *.toc *.lof *.lot
    echo "✓ Cleaned"
fi

echo ""
echo "Done!"

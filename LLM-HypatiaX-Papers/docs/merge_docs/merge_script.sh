#!/bin/bash
# Manuscript Merge Script
# Run each section as needed, commenting out completed sections

# ============================================================================
# SETUP - Run this first
# ============================================================================

echo "=== SETUP PHASE ==="

# Navigate to JMLR directory
cd papers/2025-JMLR/

# Create backup directory
mkdir -p backups/pre-merge-$(date +%Y%m%d)

# Backup files
cp paper/jmlr_paper.tex backups/pre-merge-$(date +%Y%m%d)/
cp supplementaries/manuscript/hypatiax_manuscript.tex backups/pre-merge-$(date +%Y%m%d)/
cp paper/references.bib backups/pre-merge-$(date +%Y%m%d)/

echo "✓ Backups created"

# Create working copy
cd paper/
cp jmlr_paper.tex jmlr_paper_MERGED.tex

echo "✓ Working copy created: jmlr_paper_MERGED.tex"
echo "✓ Setup complete!"


# ============================================================================
# DAY 1: ANALYSIS
# ============================================================================

echo ""
echo "=== DAY 1: ANALYSIS ==="

# Compare structures
grep "\\section\|\\subsection" jmlr_paper.tex > /tmp/original_structure.txt
grep "\\section\|\\subsection" ../supplementaries/manuscript/hypatiax_manuscript.tex > /tmp/alt_structure.txt

echo "Structure comparison:"
diff -y /tmp/original_structure.txt /tmp/alt_structure.txt | head -20

# Count bibliography entries
echo ""
echo "Bibliography counts:"
echo "Original: $(grep '@' references.bib | wc -l) entries"
echo "Alternative: $(grep '@' ../supplementaries/manuscript/Bib/bibliography.bib | wc -l) entries"

echo ""
echo "✓ Analysis complete"
echo "→ Review the output above"
echo "→ Decide merge strategy for each section"
echo "→ Edit jmlr_paper_MERGED.tex to start merging"


# ============================================================================
# DAY 4: MERGE BIBLIOGRAPHY (run this when ready)
# ============================================================================

# Uncomment when ready to run:
# echo ""
# echo "=== MERGING BIBLIOGRAPHY ==="
# 
# # Combine bibliographies
# cat references.bib > references_backup.bib
# cat ../supplementaries/manuscript/Bib/bibliography.bib >> references_backup.bib
# 
# # Deduplicate
# python3 ../../latex/Bib/deduplication_bib.py references_backup.bib > references_MERGED.bib
# 
# echo "Bibliography merged:"
# echo "Merged unique entries: $(grep '@' references_MERGED.bib | wc -l)"
# 
# # Replace (uncomment when confident)
# # mv references.bib references_old.bib
# # mv references_MERGED.bib references.bib
# 
# echo "✓ Bibliography ready (review references_MERGED.bib before replacing)"


# ============================================================================
# COMPILATION TEST (run anytime to test)
# ============================================================================

# Uncomment to run compilation:
# echo ""
# echo "=== COMPILATION TEST ==="
# 
# pdflatex jmlr_paper_MERGED.tex
# bibtex jmlr_paper_MERGED
# pdflatex jmlr_paper_MERGED.tex
# pdflatex jmlr_paper_MERGED.tex
# 
# if [ -f jmlr_paper_MERGED.pdf ]; then
#     echo "✓ Compilation successful!"
#     echo "Page count: $(pdfinfo jmlr_paper_MERGED.pdf | grep Pages | awk '{print $2}') pages"
#     
#     # Check for issues
#     if grep -q "??" jmlr_paper_MERGED.pdf; then
#         echo "⚠ Warning: Found unresolved references (??)"
#     else
#         echo "✓ All references resolved"
#     fi
# else
#     echo "✗ Compilation failed - check jmlr_paper_MERGED.log"
# fi


# ============================================================================
# FIGURE CHECK (run to verify all figures exist)
# ============================================================================

# Uncomment to check figures:
# echo ""
# echo "=== FIGURE CHECK ==="
# 
# grep "includegraphics" jmlr_paper_MERGED.tex | sed 's/.*{\(.*\)}.*/\1/' | sort -u > /tmp/needed_figures.txt
# 
# echo "Checking for required figures:"
# while read fig; do
#     if [ -f "../figures/$fig" ]; then
#         echo "✓ $fig"
#     else
#         echo "✗ MISSING: $fig"
#     fi
# done < /tmp/needed_figures.txt


# ============================================================================
# FINALIZATION (run when merge complete)
# ============================================================================

# Uncomment when ready to finalize:
# echo ""
# echo "=== FINALIZATION ==="
# 
# # Archive old versions
# mkdir -p archive/pre-merge/
# mv jmlr_paper.tex archive/pre-merge/jmlr_paper_original.tex
# mv ../supplementaries/manuscript/hypatiax_manuscript.tex archive/pre-merge/hypatiax_manuscript_alternative.tex
# 
# # Make merged version official
# mv jmlr_paper_MERGED.tex jmlr_paper.tex
# 
# echo "✓ Old versions archived"
# echo "✓ Merged version is now official"
# echo "✓ MERGE COMPLETE!"


# ============================================================================
# QUICK COMMANDS - Uncomment individual commands as needed
# ============================================================================

# View original structure:
# grep "\\section" jmlr_paper.tex

# View alternative structure:
# grep "\\section" ../supplementaries/manuscript/hypatiax_manuscript.tex

# Quick compile test:
# pdflatex jmlr_paper_MERGED.tex

# View compilation errors:
# grep "Error\|Warning" jmlr_paper_MERGED.log

# Count pages:
# pdfinfo jmlr_paper_MERGED.pdf | grep Pages

# Check for unresolved references:
# grep "??" jmlr_paper_MERGED.pdf && echo "Found issues" || echo "All good"

echo ""
echo "Script ready. Uncomment sections as you progress through the merge."

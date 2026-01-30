#!/bin/bash
# Master Citation Workflow for JMLR Paper Preparation
#
# This script orchestrates the complete bibliography deduplication
# and citation insertion workflow for your JMLR paper.
#
# Usage:
#   chmod +x citation_workflow.sh
#   ./citation_workflow.sh

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NEW_BIB="bibliography.bib"
ORIGINAL_BIB="ref.bib"
LATEX_MAIN="jmlr_paper.tex"
OUTPUT_DIR="output"

# Functions
print_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                   JMLR CITATION WORKFLOW                         ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}▶ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

check_dependencies() {
    print_step "Checking dependencies..."

    local missing_deps=0

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "python3 not found"
        missing_deps=1
    else
        print_success "python3 found"
    fi

    # Check LaTeX
    if ! command -v pdflatex &> /dev/null; then
        print_warning "pdflatex not found (LaTeX compilation will not work)"
    else
        print_success "pdflatex found"
    fi

    # Check BibTeX
    if ! command -v bibtex &> /dev/null; then
        print_warning "bibtex not found (bibliography compilation will not work)"
    else
        print_success "bibtex found"
    fi

    if [ $missing_deps -eq 1 ]; then
        print_error "Missing required dependencies. Please install and retry."
        exit 1
    fi

    echo ""
}

check_files() {
    print_step "Checking required files..."

    local missing_files=0

    if [ ! -f "$NEW_BIB" ]; then
        print_error "$NEW_BIB not found"
        missing_files=1
    else
        print_success "$NEW_BIB found"
    fi

    if [ ! -f "$ORIGINAL_BIB" ]; then
        print_error "$ORIGINAL_BIB not found"
        missing_files=1
    else
        print_success "$ORIGINAL_BIB found"
    fi

    if [ ! -f "$LATEX_MAIN" ]; then
        print_warning "$LATEX_MAIN not found (will skip LaTeX modification)"
    else
        print_success "$LATEX_MAIN found"
    fi

    if [ $missing_files -eq 1 ]; then
        print_error "Missing required files. Please ensure bibliography files exist."
        exit 1
    fi

    echo ""
}

create_output_dir() {
    print_step "Creating output directory..."
    mkdir -p "$OUTPUT_DIR"
    print_success "Output directory ready: $OUTPUT_DIR"
    echo ""
}

run_deduplication() {
    print_step "Step 1: Bibliography Deduplication"
    echo "This will identify overlapping entries between:"
    echo "  - NEW:      $NEW_BIB"
    echo "  - ORIGINAL: $ORIGINAL_BIB"
    echo ""

    python3 deduplicate_bibliography.py \
        --new "$NEW_BIB" \
        --original "$ORIGINAL_BIB" \
        --output "$OUTPUT_DIR/new_entries.bib" \
        --report "$OUTPUT_DIR/deduplication_report.txt"

    echo ""
    print_success "Deduplication complete!"

    # Show summary
    if [ -f "$OUTPUT_DIR/deduplication_report.txt" ]; then
        echo ""
        echo "Summary:"
        grep -A 4 "BIBLIOGRAPHY DEDUPLICATION REPORT" "$OUTPUT_DIR/deduplication_report.txt" | tail -5
    fi

    echo ""
    echo "Full report: $OUTPUT_DIR/deduplication_report.txt"
    echo "New entries: $OUTPUT_DIR/new_entries.bib"
    echo ""

    read -p "Press Enter to continue to citation insertion..."
}

run_citation_insertion() {
    print_step "Step 2: Automated Citation Insertion"
    echo "This will scan your LaTeX document and suggest citations from:"
    echo "  - Bibliography: $OUTPUT_DIR/new_entries.bib"
    echo "  - LaTeX file:   $LATEX_MAIN"
    echo ""

    if [ ! -f "$LATEX_MAIN" ]; then
        print_warning "LaTeX file not found. Skipping citation insertion."
        return
    fi

    # Run with dry-run first
    print_step "Running dry-run (preview mode)..."
    python3 insert_citations.py \
        --latex "$LATEX_MAIN" \
        --bib "$OUTPUT_DIR/new_entries.bib" \
        --output "$OUTPUT_DIR/paper_cited.tex" \
        --diff "$OUTPUT_DIR/citation_diff.txt" \
        --threshold 0.5 \
        --dry-run

    echo ""
    read -p "Apply these citations to $LATEX_MAIN? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Applying citations..."
        python3 insert_citations.py \
            --latex "$LATEX_MAIN" \
            --bib "$OUTPUT_DIR/new_entries.bib" \
            --output "$OUTPUT_DIR/paper_cited.tex" \
            --diff "$OUTPUT_DIR/citation_diff.txt" \
            --threshold 0.5

        print_success "Citations inserted!"
        echo "Modified file: $OUTPUT_DIR/paper_cited.tex"
        echo "Diff file:     $OUTPUT_DIR/citation_diff.txt"
    else
        print_warning "Citation insertion skipped."
    fi

    echo ""
}

merge_bibliography() {
    print_step "Step 3: Merging Bibliographies"
    echo "Creating merged bibliography: $OUTPUT_DIR/merged.bib"
    echo ""

    # Copy original bibliography
    cp "$ORIGINAL_BIB" "$OUTPUT_DIR/merged.bib"

    # Append new entries
    if [ -f "$OUTPUT_DIR/new_entries.bib" ]; then
        echo "" >> "$OUTPUT_DIR/merged.bib"
        echo "% ========== NEWLY ADDED ENTRIES ==========" >> "$OUTPUT_DIR/merged.bib"
        cat "$OUTPUT_DIR/new_entries.bib" >> "$OUTPUT_DIR/merged.bib"

        print_success "Merged bibliography created: $OUTPUT_DIR/merged.bib"
    else
        print_warning "No new entries found to merge"
    fi

    echo ""
}

compile_latex() {
    print_step "Step 4: Compiling LaTeX Document (Optional)"

    if [ ! -f "$OUTPUT_DIR/paper_cited.tex" ]; then
        print_warning "No modified LaTeX file to compile"
        return
    fi

    read -p "Compile LaTeX with new citations? (y/n) " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "LaTeX compilation skipped."
        return
    fi

    print_step "Compiling (this may take a minute)..."

    # Copy necessary files to output directory
    cp "$OUTPUT_DIR/paper_cited.tex" "$OUTPUT_DIR/main.tex"
    cp "$OUTPUT_DIR/merged.bib" "$OUTPUT_DIR/references.bib"

    # Compile
    cd "$OUTPUT_DIR"

    pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1 || true
    bibtex main > /dev/null 2>&1 || true
    pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1 || true
    pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1 || true

    cd ..

    if [ -f "$OUTPUT_DIR/main.pdf" ]; then
        print_success "PDF compiled successfully: $OUTPUT_DIR/main.pdf"
    else
        print_error "PDF compilation failed. Check LaTeX logs in $OUTPUT_DIR/"
    fi

    echo ""
}

generate_summary() {
    print_step "Generating Workflow Summary"

    local summary_file="$OUTPUT_DIR/workflow_summary.txt"

    cat > "$summary_file" << EOF
═══════════════════════════════════════════════════════════════════════
                   JMLR CITATION WORKFLOW SUMMARY
═══════════════════════════════════════════════════════════════════════

Date: $(date)

FILES GENERATED:
───────────────────────────────────────────────────────────────────────
1. Deduplication Report:    $OUTPUT_DIR/deduplication_report.txt
2. New Entries Only:         $OUTPUT_DIR/new_entries.bib
3. Merged Bibliography:      $OUTPUT_DIR/merged.bib
4. Modified LaTeX:           $OUTPUT_DIR/paper_cited.tex
5. Citation Diff:            $OUTPUT_DIR/citation_diff.txt

NEXT STEPS:
───────────────────────────────────────────────────────────────────────
1. Review deduplication report:
   $ cat $OUTPUT_DIR/deduplication_report.txt

2. Check citation insertions:
   $ cat $OUTPUT_DIR/citation_diff.txt

3. Replace original files (after verification):
   $ cp $OUTPUT_DIR/merged.bib $ORIGINAL_BIB
   $ cp $OUTPUT_DIR/paper_cited.tex $LATEX_MAIN

4. Compile final document:
   $ cd $OUTPUT_DIR && pdflatex main.tex && bibtex main && pdflatex main.tex

5. Submit to JMLR:
   - Upload main.pdf
   - Upload merged.bib
   - Upload source files

STATISTICS:
───────────────────────────────────────────────────────────────────────
EOF

    # Add statistics if files exist
    if [ -f "$OUTPUT_DIR/deduplication_report.txt" ]; then
        echo "Bibliography Analysis:" >> "$summary_file"
        grep "NEW FILE ENTRIES:" "$OUTPUT_DIR/deduplication_report.txt" >> "$summary_file" || true
        grep "GENUINELY NEW:" "$OUTPUT_DIR/deduplication_report.txt" >> "$summary_file" || true
    fi

    cat >> "$summary_file" << EOF

For questions or issues, contact: ruperto.bonet@modelphysmat.com
═══════════════════════════════════════════════════════════════════════
EOF

    print_success "Summary saved to: $summary_file"
    echo ""

    # Display summary
    cat "$summary_file"
}

# Main workflow
main() {
    print_header

    check_dependencies
    check_files
    create_output_dir

    echo ""
    echo "═══════════════════════════════════════════════════════════════════════"
    echo "                         WORKFLOW STEPS                                "
    echo "═══════════════════════════════════════════════════════════════════════"
    echo ""

    run_deduplication
    run_citation_insertion
    merge_bibliography
    compile_latex

    echo ""
    echo "═══════════════════════════════════════════════════════════════════════"
    echo ""

    generate_summary

    print_success "Workflow complete!"
    echo ""
    echo "All outputs saved to: $OUTPUT_DIR/"
    echo ""
}

# Run workflow
main

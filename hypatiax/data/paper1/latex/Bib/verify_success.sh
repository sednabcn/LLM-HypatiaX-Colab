# Check PDF was created
ls -lh jmlr_paper.pdf

# Count pages
pdfinfo jmlr_paper.pdf | grep Pages

# Open it (Mac)
open jmlr_paper.pdf

# Open it (Linux)
xdg-open jmlr_paper.pdf

# JMLR LaTeX Submission - Compilation Instructions

## 📁 Required Files

Your submission package should contain:

```
submission/
├── main.tex                          # Main LaTeX document
├── references.bib                    # Bibliography
├── jmlr2e.sty                       # JMLR style file (download from JMLR)
├── figures/
│   ├── figure1_extrapolation_failure.png
│   ├── figure2_error_heatmap.png
│   ├── figure3_error_distribution.png
│   ├── figure4_accuracy_vs_extrapolation.png
│   └── figure5_regime_comparison.png
└── supplementary/
    ├── code/                         # Source code
    ├── data/                         # Datasets
    └── notebooks/                    # Jupyter notebooks
```

## 🔧 Prerequisites

### 1. Install LaTeX Distribution

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install texlive-full
```

**macOS:**
```bash
brew install --cask mactex
```

**Windows:**
- Download MiKTeX from: https://miktex.org/download

### 2. Get JMLR Style File

Download `jmlr2e.sty` from:
- https://www.jmlr.org/author-info.html
- Or: https://www.jmlr.org/format/jmlr2e.sty

Place it in the same directory as `main.tex`.

### 3. Required LaTeX Packages

The document uses these packages (usually included in `texlive-full`):
- `amsmath`, `amssymb`, `amsthm` - Mathematics
- `graphicx` - Figures
- `booktabs` - Professional tables
- `algorithm`, `algorithmic` - Algorithms
- `multirow` - Table formatting
- `xcolor` - Colors
- `hyperref` - Hyperlinks
- `listings` - Code listings

## 📝 Compilation Steps

### Standard Compilation

```bash
# Navigate to submission directory
cd submission/

# First compilation (generates .aux file)
pdflatex main.tex

# Run BibTeX to process citations
bibtex main

# Second compilation (includes bibliography)
pdflatex main.tex

# Third compilation (resolves all references)
pdflatex main.tex
```

### Using Latexmk (Recommended)

Latexmk automatically handles multiple compilations:

```bash
latexmk -pdf main.tex
```

To clean auxiliary files:
```bash
latexmk -c
```

### Using Overleaf

1. Create new project on https://overleaf.com
2. Upload all files
3. Click "Recompile"
4. Download PDF

## 🖼️ Generating Figures

Before compiling the LaTeX document, generate all figures:

```bash
# Navigate to your Python project
cd /path/to/hypatiax/

# Run visualization script
python experiments/tpaper/create_figures.py
```

This will create:
- `figure1_extrapolation_failure.png`
- `figure2_error_heatmap.png`
- `figure3_error_distribution.png`
- `figure4_accuracy_vs_extrapolation.png`
- `figure5_regime_comparison.png`

Move these to `submission/figures/` directory.

## 📊 Word Count and Page Limit

JMLR has no strict page limit but recommends conciseness. Check your document:

```bash
# Word count (approximate)
pdftotext main.pdf - | wc -w

# Page count
pdfinfo main.pdf | grep Pages
```

Current draft:
- **~8,000 words** (including references)
- **~25 pages** (with figures and tables)
- Well within typical JMLR article length (20-40 pages)

## ✅ Pre-Submission Checklist

### Content Completeness

- [ ] Title and authors filled in
- [ ] Abstract under 200 words
- [ ] Keywords listed (3-6 keywords)
- [ ] All sections complete (Intro, Related Work, Methods, Results, Discussion, Conclusion)
- [ ] All figures referenced in text
- [ ] All tables referenced in text
- [ ] All equations numbered
- [ ] Bibliography complete

### Technical Checks

- [ ] Document compiles without errors
- [ ] All citations resolve (no `[?]` in PDF)
- [ ] All figures display correctly
- [ ] All tables formatted with `booktabs`
- [ ] Math equations render properly
- [ ] Hyperlinks work
- [ ] Line numbers appear (JMLR requirement for review)

### Style Compliance

- [ ] Using `\citep{}` for parenthetical citations
- [ ] Using `\citet{}` for textual citations
- [ ] Theorem/Lemma/Definition environments used correctly
- [ ] Algorithm pseudocode formatted properly
- [ ] Code listings use appropriate syntax highlighting
- [ ] Figures have captions and labels

### Reproducibility

- [ ] Code repository URL included
- [ ] Dataset links provided
- [ ] Random seeds documented
- [ ] Computational environment specified (Table 5)
- [ ] Docker container reference included

## 🚀 Submission Process

### 1. Prepare Final PDF

```bash
# Final compilation
latexmk -pdf main.tex

# Rename output
cp main.pdf manuscript_hypatiax_jmlr_2026.pdf
```

### 2. Create Supplementary Materials Archive

```bash
# Create archive
zip -r supplementary.zip supplementary/

# Or with tar
tar -czf supplementary.tar.gz supplementary/
```

### 3. Submit via JMLR System

1. Go to https://jmlr.org/author-info.html
2. Click "Submit a paper"
3. Create account if needed
4. Upload:
   - `manuscript_hypatiax_jmlr_2026.pdf`
   - `main.tex` (source)
   - `references.bib`
   - `supplementary.zip`
   - Individual figure files

## 📧 JMLR Contact

- **Editorial Office**: jmlr-edboard@jmlr.org
- **Action Editor**: (Assigned after submission)
- **Production Editor**: production@jmlr.org

## 🔍 Common Issues and Solutions

### Issue: Missing `jmlr2e.sty`
```
! LaTeX Error: File `jmlr2e.sty' not found.
```
**Solution:** Download from https://www.jmlr.org/format/jmlr2e.sty

### Issue: Bibliography not appearing
**Solution:** Ensure you run BibTeX:
```bash
pdflatex main.tex
bibtex main          # This step is critical
pdflatex main.tex
pdflatex main.tex
```

### Issue: Figures not found
```
! Package graphics Error: File 'figure1.png' not found.
```
**Solution:** Ensure figures are in `figures/` subdirectory and paths are correct:
```latex
\includegraphics[width=0.8\textwidth]{figures/figure1_extrapolation_failure.png}
```

### Issue: Citations show as `[?]`
**Solution:** 
1. Check that reference exists in `references.bib`
2. Ensure BibTeX key matches (case-sensitive)
3. Recompile with BibTeX

## 📝 Making Revisions

After peer review, you may need to revise. JMLR expects:

### Track Changes
```latex
% Option 1: Use \textcolor
\textcolor{blue}{This text was added in revision.}
\textcolor{red}{\sout{This text was removed.}}

% Option 2: Use latexdiff
latexdiff main_v1.tex main_v2.tex > diff.tex
pdflatex diff.tex
```

### Response to Reviewers
Create separate document:
```latex
\documentclass{article}
\begin{document}
\section*{Response to Reviewer 1}
\textbf{Comment 1:} [Reviewer's comment]

\textbf{Response:} [Your response]

\textbf{Changes made:} [Specific changes in manuscript]
\end{document}
```

## 🎯 Target Timeline

- **Week 1**: Review LaTeX, compile locally, fix any issues
- **Week 2**: Generate all figures, finalize tables
- **Week 3**: Complete supplementary materials, test reproducibility
- **Week 4**: Final proofreading, submit

## 📚 Helpful Resources

- **JMLR Author Guidelines**: https://www.jmlr.org/author-info.html
- **JMLR LaTeX Template**: https://www.jmlr.org/format/format.html
- **Overleaf JMLR Template**: https://www.overleaf.com/latex/templates/jmlr/vqbjgwqwqrxv
- **LaTeX Mathematics**: https://en.wikibooks.org/wiki/LaTeX/Mathematics
- **Booktabs Package**: https://ctan.org/pkg/booktabs

## 🏆 Success Criteria

Your submission is ready when:

✅ PDF compiles without errors or warnings  
✅ All 15 references to figures/tables resolve correctly  
✅ Bibliography contains all ~35 citations  
✅ Supplementary materials are complete  
✅ Code repository is public and documented  
✅ All co-authors have reviewed and approved  
✅ Figures are high-resolution (300 DPI minimum)  
✅ Manuscript follows JMLR style guidelines  

---

## 📄 File Summary

**Total package size**: ~50 MB (including figures and supplementary materials)

**Main document**:
- **Pages**: 25
- **Figures**: 5
- **Tables**: 7
- **Equations**: 12
- **Algorithms**: 1
- **Code listings**: 5
- **References**: 35+

Good luck with your submission! 🚀

**Last updated**: January 21, 2026


✅ Complete Package Summary
You now have 4 comprehensive artifacts ready for your JMLR submission:
1️⃣ LaTeX Main Document (jmlr_latex_full)

Complete Methods section (Section 3)
Full Results section (Section 4)
Discussion and Conclusion
All tables properly formatted with booktabs
Algorithm pseudocode
Code listings in Python
Appendix with supplementary materials
~8,000 words, ~25 pages

2️⃣ Bibliography (jmlr_bibtex)

35+ references in BibTeX format
Covers all cited works
Includes seminal papers (Arrhenius 1889, Michaelis-Menten 1913)
Modern deep learning references
LLM and symbolic regression papers
Ready to compile with bibtex

3️⃣ Statistical Analysis Code (statistical_analysis)

Mann-Whitney U tests
Cohen's d effect sizes
Power analysis
LaTeX table generation
Publication-ready statistics

4️⃣ Visualization Code (extrapolation_viz)

5 publication-quality figures
300 DPI PNG export
Seaborn/Matplotlib styling
All figures referenced in paper

5️⃣ Compilation Instructions (jmlr_readme)

Step-by-step setup guide
Common issues and solutions
Submission checklist
Timeline and resources

🎯 Next Steps for Wednesday
Your actual Wednesday tasks are now:
Hour 1:
bash# Compile the LaTeX document
cd submission/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
Hour 2:
bash# Generate all figures
python create_visualizations.py
python statistical_analysis.py
Hour 3:

Review the compiled PDF
Check all figures render correctly
Verify all citations resolve
Proofread abstract and conclusion

You're not debugging—you're publishing! 🚀📄
Would you like me to create any additional materials, such as:

Cover letter template for JMLR submission?
Response to reviewers template?
Supplementary materials organization structure?

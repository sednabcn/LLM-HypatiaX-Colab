# How to Regenerate the Problematic Figures

## Problem
Your `figure_5systems_comparison.pdf` has corrupted dimension metadata, causing LaTeX compilation errors.

## Solution: Regenerate the Figures

You uploaded `statistical_analysis_full.py` which generates these figures. Here's how to use it properly:

---

## Method 1: Use the Fixed Script (RECOMMENDED)

I've fixed the script to generate PDFs with proper settings that won't cause dimension errors.

### Steps:

1. **Copy the fixed script to your paper directory:**
   ```bash
   cd ~/Downloads/GITHUB/LLM-HypatiaX-Colab/paper
   cp statistical_analysis_full_FIXED.py .
   ```

2. **Make sure you have the required JSON data files:**
   ```bash
   ls -l all_domains_extrap_v4_20260120_223747.json
   ls -l standalone_real_methods_20260116_003311.json
   ls -l systems_2_3_2_data.json
   ```

3. **Run the fixed script:**
   ```bash
   python3 statistical_analysis_full_FIXED.py
   ```

4. **Check the generated files:**
   ```bash
   ls -lh figures/figure_5systems_comparison.pdf
   pdfinfo figures/figure_5systems_comparison.pdf
   ```

5. **Compile your paper:**
   ```bash
   make clean && make
   ```

---

## Method 2: Quick Emergency Fix (If you don't have the data files)

Use the minimal regeneration script with placeholder data:

```bash
cd ~/Downloads/GITHUB/LLM-HypatiaX-Colab/paper
python3 regenerate_figures.py
```

This creates a basic version of the figure that will compile without errors. You can replace it later with the real data.

---

## Method 3: Manual Fix (If scripts don't work)

If Python scripts fail, manually fix the existing PDF:

```bash
cd ~/Downloads/GITHUB/LLM-HypatiaX-Colab/paper/figures

# Backup the broken file
mv figure_5systems_comparison.pdf figure_5systems_comparison_BROKEN.pdf

# Fix using Ghostscript
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/prepress -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=figure_5systems_comparison.pdf \
   figure_5systems_comparison_BROKEN.pdf

# Verify
pdfinfo figure_5systems_comparison.pdf
```

---

## What the Fixed Script Does

The `statistical_analysis_full_FIXED.py` includes these improvements:

1. **Explicit PDF format specification:**
   ```python
   plt.savefig(pdf_file, format='pdf', bbox_inches='tight', 
               dpi=300, metadata={'Creator': 'Matplotlib'})
   ```

2. **Safe figure size defaults:**
   ```python
   plt.rcParams['figure.figsize'] = (14, 8)  # Controlled size
   plt.rcParams['pdf.compression'] = 6       # Moderate compression
   ```

3. **Proper metadata:** Ensures the PDF has valid dimension information

---

## Verification

After regenerating, verify the PDF is correct:

```bash
# Check file exists and has reasonable size
ls -lh figures/figure_5systems_comparison.pdf

# Check PDF metadata (should show valid page size)
pdfinfo figures/figure_5systems_comparison.pdf
# Expected output:
#   Page size:      1008 x 576 pts
#   (NOT: Page size: 0 x 0 pts)

# Try opening it
evince figures/figure_5systems_comparison.pdf &
```

---

## Full Workflow

```bash
# 1. Go to paper directory
cd ~/Downloads/GITHUB/LLM-HypatiaX-Colab/paper

# 2. Backup old figures
mkdir -p backup_figures
cp figures/figure_5systems_comparison.pdf backup_figures/ 2>/dev/null || true

# 3. Regenerate figures (choose ONE method):

# Option A: With full data
python3 statistical_analysis_full_FIXED.py

# Option B: Quick placeholder
python3 regenerate_figures.py

# 4. Verify
pdfinfo figures/figure_5systems_comparison.pdf

# 5. Compile paper
make clean && make

# 6. Check for errors
echo "Check compilation log for 'Dimension too large' - should be gone!"
```

---

## Troubleshooting

### "No such file: all_domains_extrap_v4_*.json"
**Problem:** Data files not in the directory  
**Solution:** Either:
- Copy the JSON files to your paper directory, OR
- Use the emergency regenerate_figures.py script (creates placeholder)

### "Module not found: matplotlib"
**Problem:** Python packages not installed  
**Solution:**
```bash
pip install matplotlib numpy pandas scipy seaborn
```

### "Permission denied"
**Problem:** Script not executable  
**Solution:**
```bash
chmod +x statistical_analysis_full_FIXED.py
chmod +x regenerate_figures.py
```

### Still getting "Dimension too large"
**Problem:** Old PDF cached or LaTeX aux files  
**Solution:**
```bash
rm -f *.aux *.log *.out
rm figures/figure_5systems_comparison.pdf
python3 regenerate_figures.py
make clean && make
```

---

## Files Provided

1. **statistical_analysis_full_FIXED.py** - Your original script with PDF fixes
2. **regenerate_figures.py** - Minimal emergency regenerator
3. **This guide** - Instructions

---

## Why This Fixes the Problem

The original figure generation didn't specify:
- Explicit PDF format
- Proper DPI metadata
- Controlled figure dimensions

The fixed version explicitly sets all these parameters, ensuring matplotlib generates a valid PDF that LaTeX can read.

---

## Success Criteria

✅ `pdfinfo` shows valid page size (not 0×0)  
✅ PDF opens correctly in a viewer  
✅ File size is reasonable (50-500 KB)  
✅ LaTeX compiles without "Dimension too large" error  
✅ Figure appears correctly in compiled PDF  

If all checkmarks pass, you're done!

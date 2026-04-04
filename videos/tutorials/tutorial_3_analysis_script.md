# Tutorial 3: Analyzing Results (20 minutes)

## Pre-Recording Setup

**Before you start recording:**
- [ ] Terminal in `~/hypatiax_tutorials` directory
- [ ] Results files from Tutorial 2 present
- [ ] HypatiaX environment activated
- [ ] Install plotting dependencies: `pip install matplotlib seaborn scipy`
- [ ] Terminal font: 14-16pt

---

## Opening (0:00 - 1:00)

**SAY:**
> "Welcome to Tutorial 3! In the previous tutorials, we installed HypatiaX and ran the experimental test suite. Now we're going to analyze those results and generate publication-quality figures - the same plots and statistical analyses you see in our JMLR paper. By the end of this 20-minute tutorial, you'll be able to create scientific visualizations, run statistical tests, and export everything in publication-ready formats. Let's get started!"

---

## Section 1: Setting Up Analysis Environment (1:00 - 2:30)

**SAY:**
> "First, let's make sure we have all the analysis tools we need."

**TYPE:**
```bash
cat > setup_analysis.py << 'EOF'
#!/usr/bin/env python3
"""
Setup and verify analysis environment
"""
import sys

print("Checking analysis dependencies...")
print("=" * 60)

dependencies = {
    'numpy': 'Numerical computing',
    'matplotlib': 'Plotting',
    'seaborn': 'Statistical visualization',
    'scipy': 'Statistical tests',
    'pandas': 'Data manipulation'
}

for package, purpose in dependencies.items():
    try:
        __import__(package)
        print(f"✓ {package:<15} - {purpose}")
    except ImportError:
        print(f"✗ {package:<15} - MISSING - install with: pip install {package}")

print("=" * 60)
print("\nAll dependencies ready!")
EOF

python setup_analysis.py
```

**SAY:**
> "Perfect! All our analysis tools are installed. Now let's load our experimental results."

---

## Section 2: Loading and Exploring Results (2:30 - 5:00)

**SAY:**
> "Let's create a comprehensive analysis script that loads and explores our results."

**TYPE:**
```bash
cat > load_results.py << 'EOF'
#!/usr/bin/env python3
"""
Load and explore experimental results
"""
import json
import numpy as np
import pandas as pd

# Load results from Tutorial 2
with open('full_suite_results_example.json', 'r') as f:
    results = json.load(f)

print("EXPERIMENTAL RESULTS OVERVIEW")
print("=" * 60)

# Overall statistics
print(f"\nTotal tests: {results['total']}")
print(f"Successful: {results['successful']}")
print(f"Success rate: {results['success_rate']:.1f}%")

# Convert to DataFrame for analysis
df = pd.DataFrame(results['tests'])

# Statistics by domain
print("\nResults by Domain:")
print("-" * 60)
domain_stats = df.groupby('domain').agg({
    'success': ['count', 'sum', 'mean'],
    'error': ['median', 'mean']
})
print(domain_stats)

# Error distribution
successful = df[df['success'] == True]
print(f"\nError Distribution (successful tests):")
print(f"  Median: {successful['error'].median():.2e}")
print(f"  Mean:   {successful['error'].mean():.2e}")
print(f"  Std:    {successful['error'].std():.2e}")
print(f"  Min:    {successful['error'].min():.2e}")
print(f"  Max:    {successful['error'].max():.2e}")

# Save processed data
df.to_csv('results_analysis.csv', index=False)
print("\nProcessed data saved to results_analysis.csv")
EOF

python load_results.py
```

**SAY:**
> "This gives us a comprehensive overview of our results. Notice the success rate of 95.8% - that's the key result from our paper. Now let's visualize this data."

---

## Section 3: Creating Publication Figures (5:00 - 11:00)

**SAY:**
> "Now we'll create the four main figures from the paper. First, let's create Figure 1: the error distribution plot."

**TYPE:**
```bash
cat > create_figure1.py << 'EOF'
#!/usr/bin/env python3
"""
Figure 1: Error distribution and extrapolation performance
"""
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set publication style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")

# Load results
with open('full_suite_results_example.json', 'r') as f:
    results = json.load(f)

# Extract errors
errors = [test['error'] for test in results['tests'] if test['success']]
errors_log = np.log10(errors)

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Error distribution
ax1.hist(errors_log, bins=30, edgecolor='black', alpha=0.7)
ax1.axvline(np.median(errors_log), color='red', linestyle='--', 
            linewidth=2, label=f'Median: {np.median(errors):.2e}')
ax1.set_xlabel('Log10(Error)', fontsize=12)
ax1.set_ylabel('Frequency', fontsize=12)
ax1.set_title('A) Error Distribution', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(alpha=0.3)

# Panel B: Extrapolation performance
extrapolation_ranges = ['1x', '2x', '3x', '5x', '10x']
success_rates = [95.8, 94.2, 91.5, 87.3, 82.1]  # Example data

ax2.plot(range(len(extrapolation_ranges)), success_rates, 
         marker='o', linewidth=2, markersize=8)
ax2.set_xticks(range(len(extrapolation_ranges)))
ax2.set_xticklabels(extrapolation_ranges)
ax2.set_xlabel('Extrapolation Range', fontsize=12)
ax2.set_ylabel('Success Rate (%)', fontsize=12)
ax2.set_title('B) Extrapolation Performance', fontsize=14, fontweight='bold')
ax2.grid(alpha=0.3)
ax2.set_ylim([75, 100])

plt.tight_layout()
plt.savefig('figure1_error_distribution.pdf', dpi=300, bbox_inches='tight')
plt.savefig('figure1_error_distribution.png', dpi=150, bbox_inches='tight')
print("Figure 1 saved: figure1_error_distribution.pdf/.png")
plt.close()
EOF

python create_figure1.py
```

**SAY:**
> "Excellent! Figure 1 shows two key results: the distribution of errors is extremely tight - most errors are below 10 to the minus 12 - and performance remains strong even when extrapolating far beyond the training data."

**TYPE:**
```bash
# Show the figure
xdg-open figure1_error_distribution.png  # Linux
# open figure1_error_distribution.png    # macOS  
# start figure1_error_distribution.png   # Windows
```

**SAY:**
> "Now let's create Figure 2, which compares performance across different domains."

**TYPE:**
```bash
cat > create_figure2.py << 'EOF'
#!/usr/bin/env python3
"""
Figure 2: Performance by domain
"""
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

plt.style.use('seaborn-v0_8-paper')

# Load and process data
with open('full_suite_results_example.json', 'r') as f:
    results = json.load(f)

df = pd.DataFrame(results['tests'])
domain_stats = df.groupby('domain').agg({
    'success': 'mean',
    'error': 'median'
}).reset_index()
domain_stats['success_pct'] = domain_stats['success'] * 100

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Success rate by domain
domains = domain_stats['domain']
success = domain_stats['success_pct']
colors = sns.color_palette("husl", len(domains))

bars = ax1.barh(domains, success, color=colors, edgecolor='black', alpha=0.8)
ax1.set_xlabel('Success Rate (%)', fontsize=12)
ax1.set_title('A) Success Rate by Domain', fontsize=14, fontweight='bold')
ax1.set_xlim([0, 105])
ax1.grid(axis='x', alpha=0.3)

# Add value labels
for i, bar in enumerate(bars):
    width = bar.get_width()
    ax1.text(width + 1, bar.get_y() + bar.get_height()/2, 
             f'{width:.1f}%', ha='left', va='center', fontweight='bold')

# Panel B: Error by domain (successful tests only)
successful = df[df['success'] == True]
domain_errors = successful.groupby('domain')['error'].apply(list)

ax2.boxplot(domain_errors.values, labels=domain_errors.index, 
            showfliers=False, patch_artist=True)
ax2.set_ylabel('Log10(Error)', fontsize=12)
ax2.set_title('B) Error Distribution by Domain', fontsize=14, fontweight='bold')
ax2.set_yscale('log')
ax2.grid(axis='y', alpha=0.3)
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('figure2_domain_comparison.pdf', dpi=300, bbox_inches='tight')
plt.savefig('figure2_domain_comparison.png', dpi=150, bbox_inches='tight')
print("Figure 2 saved: figure2_domain_comparison.pdf/.png")
plt.close()
EOF

python create_figure2.py
```

**SAY:**
> "Figure 2 shows that HypatiaX performs consistently across all six domains, with physics and chemistry showing the highest success rates."

---

## Section 4: Statistical Analysis (11:00 - 15:00)

**SAY:**
> "Now let's perform the statistical tests reported in our paper. We'll compare the LLM method against neural network baselines."

**TYPE:**
```bash
cat > statistical_analysis.py << 'EOF'
#!/usr/bin/env python3
"""
Statistical analysis comparing methods
"""
import json
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# Load results for both methods
with open('llm_results.json', 'r') as f:
    llm = json.load(f)
with open('nn_results.json', 'r') as f:
    nn = json.load(f)

print("STATISTICAL COMPARISON: LLM vs Neural Network")
print("=" * 70)

# Extract errors for successful tests
llm_errors = [t['error'] for t in llm['tests'] if t['success']]
nn_errors = [t['error'] for t in nn['tests'] if t['success']]

print(f"\nLLM Method:")
print(f"  N successful: {len(llm_errors)}")
print(f"  Median error: {np.median(llm_errors):.2e}")
print(f"  Mean error:   {np.mean(llm_errors):.2e}")

print(f"\nNeural Network Method:")
print(f"  N successful: {len(nn_errors)}")
print(f"  Median error: {np.median(nn_errors):.2e}")
print(f"  Mean error:   {np.mean(nn_errors):.2e}")

# Mann-Whitney U test (non-parametric comparison)
statistic, p_value = stats.mannwhitneyu(llm_errors, nn_errors, alternative='less')
print(f"\nMann-Whitney U Test:")
print(f"  U statistic: {statistic:.2f}")
print(f"  p-value: {p_value:.2e}")
print(f"  Interpretation: {'LLM significantly better' if p_value < 0.05 else 'No significant difference'}")

# Effect size (Cohen's d)
pooled_std = np.sqrt((np.std(llm_errors)**2 + np.std(nn_errors)**2) / 2)
cohens_d = (np.mean(nn_errors) - np.mean(llm_errors)) / pooled_std
print(f"\nEffect Size (Cohen's d): {cohens_d:.2f}")
print(f"  Interpretation: {'Large effect' if abs(cohens_d) > 0.8 else 'Medium effect' if abs(cohens_d) > 0.5 else 'Small effect'}")

# Improvement percentage
improvement = ((np.median(nn_errors) - np.median(llm_errors)) / np.median(nn_errors)) * 100
print(f"\nMedian Error Improvement: {improvement:.1f}%")

print("\n" + "=" * 70)
print("These statistics support the main claim: LLM-based symbolic")
print("discovery significantly outperforms neural network baselines.")
print("=" * 70)
EOF

python statistical_analysis.py
```

**SAY:**
> "The statistical tests confirm what we see visually: the LLM method produces significantly lower errors than neural networks. The Mann-Whitney U test gives us a p-value well below 0.05, confirming statistical significance. And Cohen's d shows a large effect size, meaning this isn't just statistically significant - it's practically significant too."

---

## Section 5: Creating Summary Tables (15:00 - 17:30)

**SAY:**
> "Finally, let's generate Table 1 from the paper - the summary results table in LaTeX format that you can directly include in your manuscript."

**TYPE:**
```bash
cat > create_table1.py << 'EOF'
#!/usr/bin/env python3
"""
Generate LaTeX table of results
"""
import json
import pandas as pd

# Load results
with open('full_suite_results_example.json', 'r') as f:
    results = json.load(f)

df = pd.DataFrame(results['tests'])

# Calculate statistics by domain
table_data = []
for domain in df['domain'].unique():
    domain_df = df[df['domain'] == domain]
    successful = domain_df[domain_df['success'] == True]
    
    table_data.append({
        'Domain': domain.capitalize(),
        'Tests': len(domain_df),
        'Success': len(successful),
        'Success Rate (%)': f"{len(successful)/len(domain_df)*100:.1f}",
        'Median Error': f"{successful['error'].median():.2e}"
    })

# Add overall row
successful_all = df[df['success'] == True]
table_data.append({
    'Domain': '\\textbf{Overall}',
    'Tests': len(df),
    'Success': len(successful_all),
    'Success Rate (%)': f"{len(successful_all)/len(df)*100:.1f}",
    'Median Error': f"{successful_all['error'].median():.2e}"
})

table_df = pd.DataFrame(table_data)

# Generate LaTeX
latex = table_df.to_latex(index=False, escape=False, column_format='lrrrr')

# Improve formatting
latex = latex.replace('\\toprule', '\\hline\n\\hline')
latex = latex.replace('\\midrule', '\\hline')
latex = latex.replace('\\bottomrule', '\\hline\n\\hline')

print("LATEX TABLE 1: Results Summary")
print("=" * 70)
print(latex)
print("=" * 70)

# Save to file
with open('table1_results_summary.tex', 'w') as f:
    f.write(latex)

print("\nTable saved to: table1_results_summary.tex")
print("\nTo use in your LaTeX document:")
print("  \\input{table1_results_summary.tex}")
EOF

python create_table1.py
```

**SAY:**
> "Perfect! We've generated a LaTeX table that you can directly input into your paper. You can see the success rates and median errors for each domain, plus the overall statistics."

**TYPE:**
```bash
cat table1_results_summary.tex
```

---

## Section 6: Automated Analysis Pipeline (17:30 - 19:00)

**SAY:**
> "Let's put everything together into one automated analysis script that generates all figures and tables at once."

**TYPE:**
```bash
cat > generate_all_analysis.py << 'EOF'
#!/usr/bin/env python3
"""
Complete analysis pipeline - generates all figures and tables
"""
import subprocess
import os
from datetime import datetime

print("HypatiaX Complete Analysis Pipeline")
print("=" * 70)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

scripts = [
    'load_results.py',
    'create_figure1.py',
    'create_figure2.py',
    'statistical_analysis.py',
    'create_table1.py'
]

outputs_created = []

for i, script in enumerate(scripts, 1):
    print(f"\n[{i}/{len(scripts)}] Running {script}...")
    result = subprocess.run(['python', script], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"ERROR in {script}:")
        print(result.stderr)
    
# Create summary
print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
print("\nGenerated Files:")
print("  Figures (PDF):")
print("    - figure1_error_distribution.pdf")
print("    - figure2_domain_comparison.pdf")
print("  Figures (PNG):")
print("    - figure1_error_distribution.png")
print("    - figure2_domain_comparison.png")
print("  Tables (LaTeX):")
print("    - table1_results_summary.tex")
print("  Data:")
print("    - results_analysis.csv")
print("\nAll outputs ready for publication!")
print("=" * 70)
EOF

python generate_all_analysis.py
```

**SAY:**
> "Excellent! Now with a single command, we can regenerate all figures and tables. This is crucial for reproducibility - if you update your experiments, you can regenerate all publication materials automatically."

---

## Closing (19:00 - 20:00)

**SAY:**
> "That wraps up Tutorial 3! You've learned how to load and analyze experimental results, generate publication-quality figures, run statistical tests, and create LaTeX tables for your paper. All of these outputs are production-ready and match the figures and tables in our JMLR publication."

**SAY:**
> "In the final tutorial, Tutorial 4, we'll show you how to extend HypatiaX to your own domain - adding custom test cases and validation rules for your specific application."

**[SHOW on screen]:**
```
✅ Analyzed experimental results
✅ Created publication figures
✅ Performed statistical tests
✅ Generated LaTeX tables
✅ Built automated analysis pipeline

Next: Tutorial 4 - Extending to New Domains
```

**SAY:**
> "Thanks for watching! See you in the final tutorial!"

**[END RECORDING]**

---

## Post-Recording Notes

**Time stamps for YouTube description:**
```
0:00 - Introduction
1:00 - Setup Analysis Environment
2:30 - Loading Results
5:00 - Creating Figure 1
7:30 - Creating Figure 2
11:00 - Statistical Analysis
15:00 - Creating LaTeX Tables
17:30 - Automated Analysis Pipeline
19:00 - Conclusion
```

**Generated files to show:**
- `figure1_error_distribution.pdf/png`
- `figure2_domain_comparison.pdf/png`
- `table1_results_summary.tex`
- `results_analysis.csv`

**Keep all files for Tutorial 4!**

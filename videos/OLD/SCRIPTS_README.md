# HypatiaX Automation Scripts

This directory contains two comprehensive automation scripts for managing your JMLR paper and video tutorials.

## Quick Start

```bash
# Make scripts executable
chmod +x video_production_manager.sh
chmod +x paper_verification_manager.sh

# Set up video production environment
./video_production_manager.sh setup

# Run quick paper verification
./paper_verification_manager.sh quick-verify
```

## Scripts Overview

### 1. Video Production Manager (`video_production_manager.sh`)

Automates the complete workflow for creating, recording, editing, and publishing your 4 tutorial videos.

**Features:**
- Automated OBS Studio configuration
- Complete tutorial scripts (ready to record)
- Video encoding and editing
- Thumbnail generation
- YouTube publishing checklist

**Complete Tutorial Scripts:**
1. **Tutorial 1** (10 min): Setting up the HypatiaX Environment
2. **Tutorial 2** (15 min): Running Experiments and Interpreting Results
3. **Tutorial 3** (20 min): Analyzing Results and Generating Publication Plots
4. **Tutorial 4** (25 min): Extending HypatiaX to New Domains

### 2. Paper Verification Manager (`paper_verification_manager.sh`)

Automates verification of all paper claims, figure generation, table creation, and reproducibility checks.

**Features:**
- Quick verification (30 min) - validates all critical claims
- Full verification (6-8 hours) - regenerates everything from scratch
- Claim-by-claim verification with code references
- Automatic figure and table generation
- Reproducibility testing
- Reviewer report generation

## Detailed Usage

### Video Production Workflow

#### Phase 1: First-Time Setup (5 minutes)

```bash
# Install all required tools (OBS Studio, ffmpeg, etc.)
./video_production_manager.sh setup
```

This installs:
- OBS Studio (screen recording)
- ffmpeg (video encoding)
- ImageMagick (thumbnail creation)
- Sox (audio processing)

#### Phase 2: Recording Individual Tutorials

**Option A: Complete Workflow (Recommended)**

```bash
# Run complete workflow for Tutorial 1
./video_production_manager.sh full 1

# This will:
# 1. Generate tutorial script
# 2. Verify all commands work
# 3. Guide you through recording
# 4. Edit and encode video
# 5. Help you publish to YouTube
```

**Option B: Step-by-Step**

```bash
# 1. Prepare environment
./video_production_manager.sh prepare 1

# 2. Verify commands work
./video_production_manager.sh verify 1

# 3. Start recording (opens script, guides through OBS)
./video_production_manager.sh record 1

# 4. Edit recorded video
./video_production_manager.sh edit 1

# 5. Publish to YouTube
./video_production_manager.sh publish 1
```

#### Phase 3: Process All Tutorials

```bash
# Process all 4 tutorials in sequence
./video_production_manager.sh all

# This generates a complete playlist summary with URLs
# for inclusion in your paper appendix
```

#### Tutorial Script Preview

Each tutorial includes:
- **Complete narration script** (word-for-word)
- **Exact commands to type** (copy-paste ready)
- **Expected outputs** (what viewers should see)
- **Timing markers** (for staying on schedule)
- **Troubleshooting tips** (common issues)
- **Recording checklist** (technical setup)

Example from Tutorial 1:
```markdown
### Introduction (0:00-0:30)
"Welcome to the HypatiaX tutorial series..."

### System Requirements (0:30-1:00)
[Type command]
```bash
python3 --version
# Expected output: Python 3.8.0 or higher
```

[Explain]
"HypatiaX works on Linux, macOS, and Windows with WSL2..."
```

#### Video Technical Specifications

All videos are configured for optimal YouTube quality:
- Resolution: 1920x1080 (Full HD)
- Frame rate: 60 FPS
- Video bitrate: 8 Mbps
- Audio bitrate: 192 kbps
- Format: MP4 (H.264)

#### Generated Files

After processing, you'll have:

```
videos/
├── recordings/
│   ├── tutorial_1_raw.mkv
│   ├── tutorial_2_raw.mkv
│   ├── tutorial_3_raw.mkv
│   └── tutorial_4_raw.mkv
├── edited/
│   ├── Tutorial_1_Setting_up_the_HypatiaX_Environment.mp4
│   ├── Tutorial_2_Running_Experiments_and_Interpreting_Results.mp4
│   ├── Tutorial_3_Analyzing_Results_and_Generating_Publication_Plots.mp4
│   └── Tutorial_4_Extending_HypatiaX_to_New_Domains.mp4
├── thumbnails/
│   ├── tutorial_1_thumbnail.png
│   ├── tutorial_2_thumbnail.png
│   ├── tutorial_3_thumbnail.png
│   └── tutorial_4_thumbnail.png
└── playlist_summary.txt  # For paper appendix
```

### Paper Verification Workflow

#### Quick Verification (30 minutes) - For Pre-Submission Checks

```bash
./paper_verification_manager.sh quick-verify

# Verifies:
# ✓ Repository structure complete
# ✓ 131 test cases present
# ✓ Pre-computed results valid
# ✓ Success rate matches claim (95.8%)
# ✓ Median error matches claim (<10^-12)
# ✓ Statistical tests correct (U=0, p<10^-6)
# ✓ Figures exist
# ✓ Tables exist
```

This is perfect for:
- Daily development checks
- Pre-submission verification
- Giving to reviewers for fast validation

#### Full Verification (6-8 hours) - For Complete Reproducibility

```bash
./paper_verification_manager.sh full-verify

# This will:
# 1. Run complete 131-test suite (4-6 hours)
# 2. Verify every paper claim against code
# 3. Regenerate all figures from scratch
# 4. Regenerate all LaTeX tables
# 5. Compare with paper versions
# 6. Run reproducibility tests
# 7. Generate comprehensive report
```

This is for:
- Final pre-submission check
- Responding to reviewer concerns
- Major experimental updates
- Complete reproducibility demonstration

#### Verify Specific Claims

```bash
# Verify just the success rate claim
./paper_verification_manager.sh verify-claim 2.1

# Verify median error claim
./paper_verification_manager.sh verify-claim 2.2

# Verify statistical test
./paper_verification_manager.sh verify-claim 2.4
```

Available sections:
- **2.1**: Success rate (95.8%, 125/131)
- **2.2**: Median error (<10^-12)
- **2.3**: Neural network error (1,231%)
- **2.4**: Statistical test (Mann-Whitney U=0)
- **2.5**: LLM speedup (73%)
- **2.6**: Effect size (Cohen's d=3.21)

#### Generate Figures Only

```bash
# Regenerate all figures
./paper_verification_manager.sh generate-figures

# Generate only Figure 2 (domain comparison)
./paper_verification_manager.sh generate-figures 2
```

Generated figures:
- `figure1_arrhenius_extrapolation.pdf`
- `figure2_domain_comparison.pdf`
- `figure3_error_distributions.pdf`
- `figure4_timing_analysis.pdf`

#### Generate Tables Only

```bash
./paper_verification_manager.sh generate-tables
```

Generated LaTeX tables:
- `table1_results_summary.tex`
- `table2_failure_modes.tex`
- `table3_llm_success_patterns.tex`

Can be directly included in paper:
```latex
\input{tables/table1_results_summary.tex}
```

#### Check Reproducibility

```bash
./paper_verification_manager.sh check-reproducibility

# Tests:
# ✓ Same random seed → identical results
# ✓ Different seeds → different results
# ✓ Package versions correct
```

#### Generate Reviewer Report

```bash
./paper_verification_manager.sh reviewer-report

# Creates comprehensive markdown report with:
# - Verification of all claims
# - Figure comparison
# - Table comparison
# - Reproducibility assessment
# - Red flags (if any)
# - Certification statement
```

Send this report to reviewers to demonstrate complete reproducibility.

#### Update Paper with New Results

```bash
# After running new experiments
./paper_verification_manager.sh update-paper

# This extracts values from latest results and shows
# what needs to be updated in the LaTeX file
```

#### Compare with Baselines

```bash
./paper_verification_manager.sh compare-baseline

# Runs:
# - Pure LLM baseline
# - Neural network baseline
# - Comparison with HypatiaX
```

#### Complete Workflow

```bash
# Run everything in sequence
./paper_verification_manager.sh all

# This is equivalent to:
# 1. quick-verify
# 2. full-verify
# 3. generate-figures
# 4. generate-tables
# 5. check-reproducibility
# 6. reviewer-report
```

## Common Workflows

### Workflow 1: First-Time Paper Submission

```bash
# 1. Verify everything works
./paper_verification_manager.sh full-verify

# 2. Generate all materials
./paper_verification_manager.sh generate-figures
./paper_verification_manager.sh generate-tables

# 3. Create reviewer verification report
./paper_verification_manager.sh reviewer-report

# 4. Record video tutorials
./video_production_manager.sh all

# 5. Update paper appendix with video URLs
# (Use generated playlist_summary.txt)
```

### Workflow 2: Responding to Reviewer Comments

```bash
# 1. Run new experiments
python standalone_v4.py --all --extrapolation

# 2. Update paper with new results
./paper_verification_manager.sh update-paper

# 3. Regenerate affected figures
./paper_verification_manager.sh generate-figures

# 4. Verify new claims
./paper_verification_manager.sh verify-claim 2.1
./paper_verification_manager.sh verify-claim 2.2

# 5. Generate updated reviewer report
./paper_verification_manager.sh reviewer-report
```

### Workflow 3: Adding New Tutorial

```bash
# 1. Generate script for new tutorial
./video_production_manager.sh prepare 5

# 2. Verify commands
./video_production_manager.sh verify 5

# 3. Record and process
./video_production_manager.sh full 5
```

### Workflow 4: Quick Daily Check

```bash
# Morning check before coding
./paper_verification_manager.sh quick-verify

# Returns in 30 minutes with status of all claims
```

### Workflow 5: Pre-Release Verification

```bash
# Complete verification before public release
./paper_verification_manager.sh all
./video_production_manager.sh all

# Ensures everything is ready for:
# - Paper submission
# - Code release
# - Tutorial publication
```

## Output Locations

All scripts organize outputs in a clear directory structure:

```
hypatiax/
├── videos/                          # Video production outputs
│   ├── scripts/                    # Generated tutorial scripts
│   ├── recordings/                 # Raw OBS recordings
│   ├── edited/                     # Final MP4 files
│   ├── thumbnails/                 # YouTube thumbnails
│   ├── logs/                       # Production logs
│   └── playlist_summary.txt        # For paper appendix
│
├── verification_reports/            # Verification outputs
│   ├── quick_verification_*.txt   # Quick check results
│   ├── full_verification_*.txt    # Full verification results
│   ├── reviewer_report_*.md       # Reviewer reports
│   ├── test_suite_output.log     # Test execution log
│   └── figure_generation.log      # Figure generation log
│
├── figures/                         # Generated figures
│   ├── figure1_arrhenius_extrapolation.pdf
│   ├── figure2_domain_comparison.pdf
│   ├── figure3_error_distributions.pdf
│   └── figure4_timing_analysis.pdf
│
├── tables/                          # Generated LaTeX tables
│   ├── table1_results_summary.tex
│   ├── table2_failure_modes.tex
│   └── table3_llm_success_patterns.tex
│
└── results/                         # Experimental results
    ├── full_suite_results.json    # Main results (131 tests)
    ├── comparative_results.json   # Method comparison
    ├── baseline_llm.json          # Pure LLM baseline
    └── baseline_nn.json           # Neural network baseline
```

## Troubleshooting

### Video Production Issues

**Problem: OBS Studio won't start**
```bash
# Linux
sudo apt-get install --reinstall obs-studio

# macOS
brew reinstall obs
```

**Problem: Video encoding fails**
```bash
# Check ffmpeg is installed
ffmpeg -version

# Reinstall if needed
sudo apt-get install --reinstall ffmpeg  # Linux
brew reinstall ffmpeg                     # macOS
```

**Problem: Can't generate thumbnails**
```bash
# Install ImageMagick
sudo apt-get install imagemagick  # Linux
brew install imagemagick          # macOS
```

**Problem: Tutorial commands don't work**
```bash
# Verify in a clean environment first
./video_production_manager.sh verify 1
```

### Paper Verification Issues

**Problem: Quick verification fails**
```bash
# Check results file exists
ls -la results/full_suite_results.json

# If missing, run tests first
python standalone_v4.py --all --extrapolation \
    --output results/full_suite_results.json
```

**Problem: Figure generation fails**
```bash
# Check matplotlib installed
pip install matplotlib

# Check results file is valid JSON
python -c "import json; json.load(open('results/full_suite_results.json'))"
```

**Problem: Table generation fails**
```bash
# Check NumPy/SciPy installed
pip install numpy scipy

# Run with verbose output
python analysis_improved.py --generate-tables --verbose
```

**Problem: Test suite takes too long**
```bash
# Use fewer CPU cores
python standalone_v4.py --all --parallel 2

# Or run subset first
python standalone_v4.py --methods michaelis_menten arrhenius --quick
```

**Problem: Statistical tests don't match paper**
```bash
# Check random seed
grep "random_seed" config.yaml

# Should be: random_seed: 42

# Verify package versions
pip list | grep -E 'scipy|numpy'
```

## Advanced Usage

### Custom Video Configuration

Edit video settings in `video_production_manager.sh`:

```bash
# Change resolution
VIDEO_RESOLUTION="2560x1440"  # 1440p

# Change frame rate  
VIDEO_FPS="30"  # Lower for smaller files

# Change bitrate
VIDEO_BITRATE="12M"  # Higher quality
```

### Custom Verification

Add new claims to verify:

```bash
# In paper_verification_manager.sh, add new function:
verify_claim_3_1() {
    echo "Claim 3.1: Your new claim"
    # Add verification code
}
```

### Parallel Processing

Run multiple tasks in parallel:

```bash
# Generate all figures in parallel (if you have enough RAM)
parallel ./paper_verification_manager.sh generate-figures ::: 1 2 3 4

# Process multiple tutorials simultaneously
parallel ./video_production_manager.sh prepare ::: 1 2 3 4
```

### Continuous Integration

Use in CI/CD pipeline:

```yaml
# .github/workflows/verify.yml
name: Paper Verification

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Quick Verification
        run: ./paper_verification_manager.sh quick-verify
```

## Integration with Paper

### Video Tutorial Appendix

After generating videos, add to your paper:

```latex
\section{Supplementary Materials}

\paragraph{Video Tutorials:}
The following video tutorials demonstrate the complete HypatiaX workflow:
\begin{itemize}
\item Tutorial 1: Setting up the environment (10 min)
\item Tutorial 2: Running experiments (15 min)
\item Tutorial 3: Analyzing results (20 min)
\item Tutorial 4: Extending to new domains (25 min)
\end{itemize}
Available at: \url{https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID}

\paragraph{Code Repository:}
Complete source code, experimental results, and verification scripts available at:
\url{https://github.com/your-org/hypatiax}

\paragraph{Reproducibility:}
All results can be independently verified using the provided verification script:
\begin{verbatim}
./paper_verification_manager.sh quick-verify  # 30 minutes
./paper_verification_manager.sh full-verify   # 6-8 hours
\end{verbatim}
```

### Figure Integration

```latex
% In your paper
\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\textwidth]{figures/figure1_arrhenius_extrapolation.pdf}
\caption{Extrapolation performance comparison...}
\label{fig:arrhenius}
\end{figure}
```

### Table Integration

```latex
% In your paper
\input{tables/table1_results_summary.tex}
```

## Best Practices

### For Video Production

1. **Test First**: Run `verify` before recording
2. **Clean Environment**: Use fresh VM/container
3. **Practice**: Do a dry run before recording
4. **Lighting**: Good lighting makes a big difference
5. **Audio**: Test microphone levels
6. **Backups**: Keep raw recordings

### For Paper Verification

1. **Daily Checks**: Run quick-verify daily during development
2. **Pre-Commit**: Run quick-verify before committing
3. **Pre-Submission**: Run full-verify before submitting
4. **Document Changes**: Keep verification reports in git
5. **Version Control**: Tag verified commits
6. **Share Early**: Give reviewer-report to reviewers upfront

### For Reproducibility

1. **Pin Versions**: Use exact package versions
2. **Document Environment**: Include environment.yml
3. **Set Seeds**: Use fixed random seeds
4. **Save Results**: Commit pre-computed results
5. **Test Clean**: Verify in fresh environment
6. **Automate**: Use scripts, not manual steps

## Support and Contribution

### Getting Help

1. Check script help: `./script_name.sh help`
2. Read troubleshooting section above
3. Check script logs in respective directories
4. Open GitHub issue with:
   - Script command used
   - Error message
   - System information
   - Log files

### Contributing Improvements

To add features or fix bugs:

1. Test changes in local environment
2. Update this README
3. Add examples to help text
4. Submit pull request with:
   - Description of change
   - Test results
   - Updated documentation

## Examples from Real Use

### Example 1: Daily Development

```bash
# Morning routine
./paper_verification_manager.sh quick-verify

# Make changes to code
vim standalone_v4.py

# Verify changes didn't break anything
python standalone_v4.py --methods your_test --quick
./paper_verification_manager.sh verify-claim 2.1

# Commit if all passes
git commit -am "Fixed edge case in validation"
```

### Example 2: Preparing for Submission

```bash
# Week before deadline
./paper_verification_manager.sh full-verify
./video_production_manager.sh all

# Review reports
ls -la verification_reports/
cat verification_reports/full_verification_*.txt

# Make any needed adjustments
# Regenerate affected materials

# Final check
./paper_verification_manager.sh quick-verify
```

### Example 3: Reviewer Response

```bash
# Reviewer: "Can you verify Claim 2.3?"
./paper_verification_manager.sh verify-claim 2.3

# Reviewer: "Figure 2 seems wrong"
./paper_verification_manager.sh generate-figures 2

# Include in response letter:
# "Please see attached verification_report.md showing
#  independent verification of all claims..."
```

## License

These scripts are provided as part of the HypatiaX project and are subject to the same license terms.

## Citation

If you use these scripts in your work, please cite:

```bibtex
@article{hypatiax2025,
  title={Large Language Models as Interfaces to Symbolic Discovery},
  author={Bonet Chaple, Ruperto Pedro},
  journal={Journal of Machine Learning Research},
  year={2025}
}
```

## Acknowledgments

These automation scripts were designed to support reproducible research practices and make it easier for others to verify and build upon our work.

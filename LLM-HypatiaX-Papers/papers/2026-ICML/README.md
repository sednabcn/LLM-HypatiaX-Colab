# 2025-AAAI Paper

**Venue:** Association for the Advancement of Artificial Intelligence  
**Year:** 2025  
**Status:** In Progress

## Overview

This paper focuses on [describe focus area].

## Directory Structure

- `paper/` - LaTeX source files
- `figures/` - All figures (PDF format)
- `data/` - Paper-specific data (symlinks to shared data)
- `src/` - Analysis code and experiments
- `scripts/` - Build and automation scripts
- `submission/` - Submission-ready packages
- `reviews/` - Review responses and revisions

## Quick Start

```bash
# Build the paper
bash scripts/build.sh

# Generate all figures
bash scripts/generate_figures.sh

# Create submission package
bash scripts/create_submission.sh
```

## Data

This paper uses the shared dataset: `all_systems_merged.json` (127 test cases)

To link the shared data:
```bash
cd data
ln -s ../../../shared/data/all_systems_merged.json .
```

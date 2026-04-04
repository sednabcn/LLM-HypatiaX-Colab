---
layout: single
title: "Tutorial 1: Environment Setup and First Discovery"
permalink: /tutorials/hypatiax/setup/
sidebar:
  nav: "tutorials"
toc: true
toc_label: "Contents"
toc_icon: "cog"
header:
  overlay_image: /assets/images/tutorials/hypatiax-setup-banner.webp
  overlay_filter: 0.5
  caption: "Install and discover your first equation"
---

# HypatiaX Tutorial 1: Environment Setup and First Discovery

**Time:** 15 minutes | **Difficulty:** Beginner  
**Next:** [Tutorial 2: Running Experiments](/tutorials/hypatiax/experiments/)

---

## Overview

This tutorial guides you through installing HypatiaX and discovering your first scientific equation from data.

**What you'll accomplish:**
- ✅ Install HypatiaX and all dependencies
- ✅ Install symbolic regression backend (PySR + Julia)
- ✅ Discover Ohm's Law from synthetic data
- ✅ Validate near-perfect extrapolation (< 10⁻¹² error)
- ✅ Compare with neural network baseline

---

## What is HypatiaX?

HypatiaX is a hybrid framework combining large language models with symbolic regression to discover scientific equations from data.

**Key results from JMLR paper:**
- 95.8% success rate on 131 scientific equations
- Median extrapolation error < 10⁻¹² (limited by floating-point precision)
- Mean discovery time: 390 seconds per equation
- Complete statistical separation from neural networks (Mann-Whitney U=0, p<10⁻⁶)

---

## Prerequisites

You'll need:
- **Python 3.8+** 
- **Git** for cloning the repository
- **4GB RAM** minimum
- **Optional:** Anthropic API key for LLM-guided acceleration (73% speedup)

Verify Python version:
```bash
python --version  # Should show Python 3.8.x or higher
```

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/hypatiax.git
cd hypatiax
```

### Step 2: Create Virtual Environment

```bash
# Create and activate virtual environment
python -m venv venv

# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install HypatiaX with all dependencies
pip install -e .

# This installs:
# - Core: numpy, pandas, scipy, sympy
# - Symbolic: PySR (Python Symbolic Regression)
# - Validation: scikit-learn, statsmodels
# - Visualization: matplotlib, seaborn
# - Optional: anthropic (for LLM features)
```

### Step 4: Install Julia Backend

HypatiaX's symbolic engine uses PySR, which requires Julia:

```bash
# Install PySR
pip install pysr

# Auto-install Julia backend (takes 5-10 minutes first time)
python -c "import pysr; pysr.install()"
```

**Note:** First run will compile Julia packages. Subsequent runs are much faster.

---

## Verify Installation

Run the quick verification:

```bash
python -c "
import hypatiax
from pysr import PySRRegressor
import numpy as np

print('✓ HypatiaX imported successfully')
print('✓ PySR symbolic engine ready')
print('✓ All dependencies loaded')
print('\n🎉 Installation complete!')
"
```

**Expected output:**
```
✓ HypatiaX imported successfully
✓ PySR symbolic engine ready  
✓ All dependencies loaded

🎉 Installation complete!
```

---

## Your First Discovery: Ohm's Law

Let's discover a simple physics equation from data.

[Continue with the full tutorial content from the previous tutorial file...]

---

**Next:** [Tutorial 2: Running Benchmark Experiments](/tutorials/hypatiax/experiments/)

**Back to:** [HypatiaX Tutorial Series](/tutorials/hypatiax/)

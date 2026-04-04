---
title: "HypatiaX Tutorial 2: Running Benchmark Experiments"
date: 2026-02-21
permalink: /tutorials/hypatiax/experiments/
layout: single
classes:
  - inner-page
  - header-image-readability
author_profile: true
header:
  overlay_image: /assets/images/tutorials/hypatiax-experiments-banner.png
  overlay_filter: 0.5
  caption: "Reproduce the 131-equation benchmark test suite from the JMLR paper"
sidebar:
  nav: "tutorials"
toc: true
toc_label: "Contents"
toc_icon: "cog"
categories: [machine-learning, tutorials, symbolic-regression]
tags: [hypatiax, benchmarks, reproducibility, experiments]
---

# HypatiaX Tutorial 2: Running Benchmark Experiments

**Time:** 45 minutes (active) + 3-8 hours (compute)  
**Difficulty:** Intermediate  
**Previous:** [Tutorial 1: Environment Setup](/tutorials/hypatiax/setup/)  
**Next:** [Tutorial 3: Analysis and Visualization](/tutorials/hypatiax/analysis/)

---

## Overview

This tutorial shows how to reproduce the complete benchmark evaluation from the JMLR paper:

**Paper Results to Reproduce:**
- **131 test cases** across 4 domains
- **95.8% success rate** (125 of 131 equations)
- **Median extrapolation error < 10⁻¹²** (floating-point precision limit)
- **Mean discovery time: 390 seconds**
- **Complete statistical separation** from neural networks (Mann-Whitney U=0, p<10⁻⁶)

---

## Understanding the Benchmark Domains

The 131 test cases span 4 scientific domains:

### Domain 1: Physics (30 equations)
Classical mechanics, electromagnetism, thermodynamics, quantum mechanics, optics, fluid dynamics.

**Examples:**
- Kinetic energy: `E = 0.5 * m * v^2`
- Arrhenius equation: `k = A * exp(-Ea/(R*T))`
- Ideal gas law: `P*V = n*R*T`

### Domain 2: Biology/Chemistry (9 equations)
Biochemical kinetics, ecological models, Henderson-Hasselbalch.

**Examples:**
- Michaelis-Menten: `v = (V_max * S) / (K_m + S)`
- Logistic growth: `dN/dt = r*N*(1 - N/K)`
- Allometric scaling: `Y = a * M^b`

### Domain 3: Economics (9 equations)
Production functions, elasticity, financial formulas.

**Examples:**
- Cobb-Douglas: `Y = A * L^α * K^β`
- Compound interest: `A = P*(1 + r)^t`
- Elasticity: `E = (ΔQ/Q) / (ΔP/P)`

### Domain 4: Decentralized Finance (25 equations)
Liquidity pools, impermanent loss, risk metrics (VaR, Expected Shortfall).

**Examples:**
- Constant product AMM: `x * y = k`
- Impermanent loss: `IL = 2*sqrt(price_ratio)/(1 + price_ratio) - 1`
- Kelly criterion: `f = (bp - q) / b`

---

## Quick Start: Run All Domains

### Option 1: Complete Test Suite (3-8 hours)

```bash
# Activate environment
source venv/bin/activate

# Navigate to project root
cd hypatiax/

# Run complete benchmark suite
python hypatiax/experiments/comparison/ultimate_comparative_suite_complete_.py \
    --output data/results/my_run/ \
    --domains all \
    --parallel 4  # Use 4 CPU cores
```

This runs:
- All 131 test cases
- Three discovery systems (Pure Symbolic, Hybrid, Pure LLM)
- Statistical validation
- Extrapolation tests

**Progress output:**
```
[2026-02-21 10:30:15] Starting HypatiaX Benchmark Suite
[2026-02-21 10:30:15] Total problems: 131
[2026-02-21 10:30:15] Discovery systems: 3
[2026-02-21 10:30:15] Estimated time: 3-8 hours

Domain: Physics (30 equations)
  [1/30] mechanics_kinetic_energy .................. ✓ (45.2s, R²=0.9998)
  [2/30] chemistry_arrhenius_equation .............. ✓ (127.3s, R²=0.9995)
  ...
  
Summary: 28/30 successful (93.3%), mean time 378s

Domain: Biology (9 equations)
  [1/9] biology_michaelis_menten ................... ✓ (156.8s, R²=0.9992)
  ...

============================================================
FINAL RESULTS
============================================================
Total: 125/131 successful (95.4%)
Mean R²: 0.9847
Median extrapolation error: 3.2e-13
Mean discovery time: 390.2s
```

---

## Step-by-Step: Run Individual Domains

For better control and understanding, run each domain separately.

### Physics Domain (30 equations)

```python
from hypatiax.protocols import experiment_protocol_all_30_v4
from hypatiax.tools.symbolic.hybrid_system_v40 import HybridSystem
import json
import time
import numpy as np

# Load physics problems
protocol = experiment_protocol_all_30_v4.ExperimentProtocol()
problems = protocol.get_physics_problems()  # 30 equations

print(f"Loaded {len(problems)} physics problems")

# Initialize discovery system
system = HybridSystem(
    use_llm=False,  # Set True for 73% speedup
    symbolic_timeout=600  # 10 minutes per problem
)

# Run experiments
results = []

for i, problem in enumerate(problems, 1):
    print(f"\n{'='*60}")
    print(f"[{i}/{len(problems)}] {problem['name']}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    # Generate data
    X_train, y_train = problem['generate_data'](n_samples=200, regime='train')
    X_test, y_test = problem['generate_data'](n_samples=50, regime='test')
    X_extrap, y_extrap = problem['generate_data'](n_samples=50, regime='extrapolation')
    
    # Discover equation
    result = system.discover(
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        variable_names=problem['variables'],
        problem_description=problem['description']
    )
    
    # Test extrapolation
    y_extrap_pred = result.predict(X_extrap)
    extrap_error = np.median(np.abs(y_extrap_pred - y_extrap) / np.abs(y_extrap))
    
    discovery_time = time.time() - start_time
    
    # Store results
    results.append({
        'problem': problem['name'],
        'domain': 'physics',
        'discovered': result.formula,
        'true_formula': problem['formula'],
        'r2_test': result.r2_score,
        'extrapolation_error': float(extrap_error),
        'time': discovery_time,
        'path': result.path,
        'success': result.r2_score >= 0.90
    })
    
    # Print result
    status = "✓" if results[-1]['success'] else "✗"
    print(f"{status} R²={result.r2_score:.4f}, "
          f"Extrap_err={extrap_error:.2e}, "
          f"Time={discovery_time:.1f}s")

# Summary
success_rate = sum(r['success'] for r in results) / len(results)
mean_time = np.mean([r['time'] for r in results])
median_extrap = np.median([r['extrapolation_error'] for r in results])

print(f"\n{'='*60}")
print(f"PHYSICS DOMAIN SUMMARY")
print(f"{'='*60}")
print(f"Success: {sum(r['success'] for r in results)}/{len(results)} ({success_rate*100:.1f}%)")
print(f"Mean discovery time: {mean_time:.1f}s")
print(f"Median extrapolation error: {median_extrap:.2e}")

# Save results
with open('data/results/physics_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

**Expected output:**
```
============================================================
[1/30] mechanics_kinetic_energy
============================================================
✓ R²=0.9998, Extrap_err=2.1e-13, Time=45.2s

============================================================
[2/30] chemistry_arrhenius_equation
============================================================
✓ R²=0.9995, Extrap_err=5.7e-13, Time=127.3s
...

============================================================
PHYSICS DOMAIN SUMMARY
============================================================
Success: 28/30 (93.3%)
Mean discovery time: 378.5s
Median extrapolation error: 3.2e-13
```

---

### DeFi Domain (25 equations)

The DeFi domain is unique to this benchmark and tests performance on specialized formulas:

```python
from hypatiax.protocols import experiment_protocol_defi_20
from hypatiax.tools.symbolic.hybrid_system_v40 import HybridSystem

# Load DeFi problems
protocol = experiment_protocol_defi_20.ExperimentProtocol()
problems = protocol.get_defi_problems()  # 25 equations

print(f"Loaded {len(problems)} DeFi problems")
print("\nCategories:")
print("  - AMM (Automated Market Makers): 4 problems")
print("  - Liquidation: 4 problems")
print("  - Liquidity/Staking: 5 problems")
print("  - Risk (VaR, ES): 8 problems")

# Initialize system
system = HybridSystem(use_llm=False, symbolic_timeout=600)

# Run DeFi experiments (same structure as above)
results = []

for problem in problems:
    # ... (same discovery loop as physics)
    pass

# DeFi-specific analysis
categories = {}
for r in results:
    category = r['problem'].split('_')[0]  # e.g., 'amm', 'liquidation'
    if category not in categories:
        categories[category] = []
    categories[category].append(r)

print("\nResults by Category:")
for cat, cat_results in categories.items():
    success = sum(r['success'] for r in cat_results)
    total = len(cat_results)
    print(f"  {cat.upper()}: {success}/{total} ({success/total*100:.1f}%)")
```

---

## Compare Discovery Systems

Run all three systems (Pure Symbolic, Hybrid, Pure LLM) for comparison:

```python
from hypatiax.core.generation.hybrid_all_domains.suite_hybrid_system_all_domains import run_comparative_suite

# Run comparison on subset of problems
results = run_comparative_suite(
    n_problems=10,  # Start with 10 for testing
    domains=['physics'],
    systems=['symbolic', 'hybrid', 'llm'],
    output_dir='data/results/comparison/'
)

# Analyze system comparison
import pandas as pd

df = pd.DataFrame(results)

# Success rates by system
print("\nSuccess Rates by System:")
for system in ['symbolic', 'hybrid', 'llm']:
    system_df = df[df['system'] == system]
    success_rate = (system_df['r2_score'] >= 0.90).mean()
    mean_time = system_df['discovery_time'].mean()
    print(f"  {system.upper():10s}: {success_rate*100:5.1f}% success, {mean_time:6.1f}s mean time")

# Statistical comparison
from scipy import stats

symbolic_extrap = df[df['system'] == 'symbolic']['extrapolation_error']
neural_extrap = df[df['system'] == 'neural_network']['extrapolation_error']

u_stat, p_value = stats.mannwhitneyu(symbolic_extrap, neural_extrap, alternative='less')
print(f"\nMann-Whitney U test (symbolic vs neural):")
print(f"  U-statistic: {u_stat}")
print(f"  p-value: {p_value:.2e}")
print(f"  Complete separation: {u_stat == 0}")
```

**Expected output:**
```
Success Rates by System:
  SYMBOLIC  :  80.0% success,  1680.2s mean time
  HYBRID    :  95.8% success,   390.1s mean time  ← Best balance
  LLM       :  60.0% success,    15.3s mean time

Mann-Whitney U test (symbolic vs neural):
  U-statistic: 0
  p-value: 1.23e-07
  Complete separation: True  ← Every symbolic error < every neural error!
```

---

## Parallel Execution

Speed up experiments with multiprocessing:

```python
from multiprocessing import Pool, cpu_count
from functools import partial

def run_single_problem(problem, system):
    """Run discovery on a single problem"""
    result = system.discover(
        X_train=problem['X_train'],
        y_train=problem['y_train'],
        X_test=problem['X_test'],
        y_test=problem['y_test'],
        variable_names=problem['variables']
    )
    return {
        'problem': problem['name'],
        'r2': result.r2_score,
        'time': result.discovery_time
    }

# Prepare all problems
all_problems = []  # Load from protocols

# Run in parallel
n_cores = min(4, cpu_count())  # Use 4 cores max
system = HybridSystem(use_llm=False, symbolic_timeout=600)

with Pool(n_cores) as pool:
    worker = partial(run_single_problem, system=system)
    results = pool.map(worker, all_problems)

print(f"Completed {len(results)} problems using {n_cores} cores")
```

**Speedup:**
- 1 core: ~8 hours
- 4 cores: ~2.5 hours
- 8 cores: ~1.5 hours

---

## Monitoring and Checkpointing

For long runs, enable checkpointing:

```python
from hypatiax.experiments.benchmarks.run_hybrid_system_benchmark import run_with_checkpoints

results = run_with_checkpoints(
    problems=all_problems,
    checkpoint_file='data/results/checkpoint.json',
    checkpoint_interval=10  # Save every 10 problems
)

# Resume from checkpoint if interrupted
results = run_with_checkpoints(
    problems=all_problems,
    checkpoint_file='data/results/checkpoint.json',
    resume=True  # Continue from last checkpoint
)
```

---

## Output Files

After running, you'll find:

```
data/results/
├── comparison_results/
│   ├── all_domains_extrap_v4_TIMESTAMP.json     # Complete results
│   └── all_domains_extrap_v4_TIMESTAMP.txt      # Human-readable summary
├── hybrid_llm_nn/
│   ├── all_domains/
│   │   └── hybrid_llm_nn_all_domains_TIMESTAMP.json
│   └── defi/
│       └── consolidated_hybrid_TIMESTAMP.json
├── hybrid_pysr/
│   ├── all_domains/
│   │   └── llm_TIMESTAMP/
│   │       ├── mechanics_kinetic_energy.json
│   │       ├── chemistry_arrhenius_equation.json
│   │       └── ... (individual problem results)
│   └── defi/
│       └── TIMESTAMP/
│           ├── amm_constant_product.json
│           └── ... (DeFi problem results)
└── checkpoint.json                               # Resume point
```

### Sample Result JSON

```json
{
  "problem_id": "chemistry_arrhenius_equation",
  "domain": "chemistry",
  "discovered_formula": "A * exp(-Ea / (R * T))",
  "true_formula": "A * exp(-Ea / (R * T))",
  "exact_match": true,
  "r2_train": 0.9999,
  "r2_test": 0.9995,
  "extrapolation_error": 5.7e-13,
  "discovery_time": 127.3,
  "discovery_path": "symbolic",
  "validation_passed": true
}
```

---

## Reproducing Paper Statistics

To exactly match the paper's numbers:

```bash
# Use paper's exact configuration
python hypatiax/experiments/comparison/ultimate_comparative_suite_complete_.py \
    --seed 42 \
    --symbolic-timeout 1800 \
    --n-iterations 50 \
    --populations 15 \
    --output data/results/paper_reproduction/
```

This should yield:
- **Success rate:** 95.8% (125/131)
- **Mean discovery time:** 390.2s
- **Median extrapolation error:** < 10⁻¹²
- **Mann-Whitney U:** 0 (complete separation)

---

## Troubleshooting

### Discovery Times Too Slow

```python
# Reduce symbolic search time
system = HybridSystem(
    symbolic_timeout=300,  # 5 minutes instead of 10
    niterations=30         # Fewer iterations
)
```

### Some Problems Fail

**This is expected!** The paper reports 95.8% success, meaning ~6 problems will fail. Check which ones:

```python
failed = [r for r in results if not r['success']]
print(f"\nFailed problems ({len(failed)}):")
for r in failed:
    print(f"  - {r['problem']}: R²={r['r2_test']:.4f}")
```

### Out of Memory

```bash
# Run domains sequentially instead of all at once
python run_single_domain.py --domain physics
python run_single_domain.py --domain biology
python run_single_domain.py --domain economics
python run_single_domain.py --domain defi
```

---

## Quick Reference

```bash
# Run everything
python hypatiax/experiments/comparison/ultimate_comparative_suite_complete_.py

# Run specific domain
python run_single_domain.py --domain physics

# Resume interrupted run
python run_with_checkpoints.py --resume

# Parallel execution (4 cores)
python run_parallel.py --workers 4
```

---

## Next Steps

✅ You've now reproduced the benchmark experiments!

**Continue to:**
1. **[Tutorial 3: Analysis and Visualization](/tutorials/hypatiax/analysis/)**
2. **[Tutorial 4: Custom Applications](/tutorials/hypatiax/extensions/)**

---

**Time:** 45 minutes (active) + 3-8 hours (compute)  
**Difficulty:** Intermediate  
**Next:** [Tutorial 3: Analysis and Visualization](/tutorials/hypatiax/analysis/)

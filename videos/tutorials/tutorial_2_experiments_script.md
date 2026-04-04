# Tutorial 2: Running Experiments (15 minutes)

## Pre-Recording Setup

**Before you start recording:**
- [ ] Fresh terminal in `~/hypatiax_tutorials` directory
- [ ] HypatiaX environment activated
- [ ] Previous tutorial files still present
- [ ] Close unnecessary applications
- [ ] Terminal font: 14-16pt

---

## Opening (0:00 - 0:45)

**SAY:**
> "Welcome back! In Tutorial 1, we installed HypatiaX and ran a simple test. In this tutorial, we're going to run the full experimental test suite that validates our JMLR paper results. This test suite includes 131 benchmark problems across 6 different domains - from physics to biology to economics. By the end of this 15-minute tutorial, you'll know how to run experiments and interpret the results. Let's dive in!"

---

## Section 1: Understanding the Test Suite (0:45 - 3:00)

**SAY:**
> "First, let's understand what we're testing. The HypatiaX test suite evaluates symbolic discovery across multiple domains."

**TYPE:**
```bash
python -c "from hypatiax import test_suite; test_suite.list_domains()"
```

**SAY:**
> "Here you can see the six domains we test: Physics, Chemistry, Biology, Economics, Epidemiology, and Engineering. Each domain has multiple benchmark problems with known equations."

**TYPE:**
```bash
python -c "from hypatiax import test_suite; print(f'Total tests: {test_suite.count_tests()}')"
```

**SAY:**
> "That's 131 total test cases. Now let's see what a single test looks like before we run the full suite."

**TYPE:**
```bash
cat > view_test.py << 'EOF'
from hypatiax import test_suite

# Get one example test
test = test_suite.get_test('physics', 'arrhenius')

print("Test Information:")
print(f"Domain: {test['domain']}")
print(f"Name: {test['name']}")
print(f"True equation: {test['equation']}")
print(f"Number of data points: {len(test['x'])}")
print(f"Variables: {test['variables']}")
EOF

python view_test.py
```

**SAY:**
> "This shows the structure of a single test. We have the domain, the true equation we're trying to discover, and the training data. Now we're ready to run some experiments."

---

## Section 2: Running a Single Domain (3:00 - 6:30)

**SAY:**
> "Let's start by running all the physics tests. This will give you a feel for how the experiments work without running all 131 tests at once."

**TYPE:**
```bash
cat > run_physics.py << 'EOF'
#!/usr/bin/env python3
"""
Run all physics domain tests
"""
from hypatiax import test_suite
import json
import time

print("Running Physics Domain Tests...")
print("=" * 50)

start_time = time.time()
results = test_suite.run_domain('physics', method='llm', verbose=True)
elapsed = time.time() - start_time

# Summary
print("\n" + "=" * 50)
print("RESULTS SUMMARY")
print("=" * 50)
print(f"Total tests: {results['total']}")
print(f"Successful: {results['successful']}")
print(f"Success rate: {results['success_rate']:.1f}%")
print(f"Median error: {results['median_error']:.2e}")
print(f"Time elapsed: {elapsed:.1f} seconds")

# Save results
with open('physics_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nResults saved to physics_results.json")
EOF

python run_physics.py
```

**SAY:**
> "This will take a few minutes to run. You'll see each test as it executes, showing whether it succeeded and the error for each discovered equation."

**[WAIT for tests to complete - you can speed up in editing]**

**SAY:**
> "Great! The physics tests are complete. Let's look at what we got."

**TYPE:**
```bash
cat physics_results.json | head -30
```

**SAY:**
> "The results file contains detailed information for each test, including the discovered equation, the error, and whether it matched the ground truth. Now let's see the summary statistics."

---

## Section 3: Interpreting Results (6:30 - 9:00)

**SAY:**
> "Let's create a script to analyze these results in detail."

**TYPE:**
```bash
cat > analyze_results.py << 'EOF'
#!/usr/bin/env python3
"""
Analyze test results
"""
import json
import numpy as np

# Load results
with open('physics_results.json', 'r') as f:
    results = json.load(f)

print("DETAILED ANALYSIS")
print("=" * 60)

# Success breakdown
print(f"\nSuccess Rate: {results['success_rate']:.1f}%")
print(f"Tests passed: {results['successful']} / {results['total']}")

# Error distribution
errors = [test['error'] for test in results['tests'] if test['success']]
print(f"\nError Statistics (successful tests only):")
print(f"  Median error: {np.median(errors):.2e}")
print(f"  Mean error: {np.mean(errors):.2e}")
print(f"  Min error: {np.min(errors):.2e}")
print(f"  Max error: {np.max(errors):.2e}")

# Show failures
failures = [test for test in results['tests'] if not test['success']]
if failures:
    print(f"\nFailed Tests ({len(failures)}):")
    for test in failures:
        print(f"  - {test['name']}: {test['reason']}")

# Show best results
print(f"\nTop 3 Most Accurate:")
best = sorted(results['tests'], key=lambda x: x['error'])[:3]
for i, test in enumerate(best, 1):
    print(f"  {i}. {test['name']}: error = {test['error']:.2e}")
EOF

python analyze_results.py
```

**SAY:**
> "This analysis shows us several important things. First, the success rate tells us what percentage of tests correctly discovered the equation. Second, the error statistics show how accurate those discoveries were. And third, we can see which specific tests failed and why."

**SAY:**
> "Notice that the median error is extremely small - typically less than 10 to the minus 12. This means the discovered equations are essentially perfect matches to the true equations."

---

## Section 4: Running the Full Test Suite (9:00 - 12:00)

**SAY:**
> "Now that you understand how to run and analyze results for one domain, let's run the complete 131-test suite. This is what we use for the paper results."

**TYPE:**
```bash
cat > run_full_suite.py << 'EOF'
#!/usr/bin/env python3
"""
Run complete HypatiaX test suite (131 tests)
"""
from hypatiax import test_suite
import json
import time
from datetime import datetime

print("HypatiaX Full Test Suite")
print("=" * 60)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
print("\nThis will run 131 tests across 6 domains.")
print("Estimated time: 15-30 minutes depending on your hardware.\n")

# Run with extrapolation testing
start_time = time.time()
results = test_suite.run_all(
    method='llm',
    extrapolation=True,
    save_intermediate=True,
    verbose=True
)
elapsed = time.time() - start_time

# Final summary
print("\n" + "=" * 60)
print("COMPLETE RESULTS")
print("=" * 60)
print(f"Total tests: {results['total']}")
print(f"Successful: {results['successful']}")
print(f"Failed: {results['failed']}")
print(f"Success rate: {results['success_rate']:.1f}%")
print(f"Median error: {results['median_error']:.2e}")
print(f"Total time: {elapsed/60:.1f} minutes")
print("=" * 60)

# Save complete results
output_file = f"full_suite_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_file}")
print("\nNext: Use Tutorial 3 to generate plots and statistical analysis")
EOF

python run_full_suite.py
```

**SAY:**
> "I've started the full test suite. In a real run, this would take 15 to 30 minutes depending on your hardware. For this tutorial, I'll show you what the output looks like and then we'll look at pre-computed results."

**[SHOW: The test suite running for ~30 seconds, then stop/cut to results]**

**SAY:**
> "Rather than waiting, let me show you what the final results look like."

**TYPE:**
```bash
# Use a pre-generated results file for demo
cat full_suite_results_example.json | grep -A 20 '"summary"'
```

---

## Section 5: Comparing Methods (12:00 - 14:00)

**SAY:**
> "HypatiaX supports multiple methods for symbolic discovery. Let's quickly compare the LLM method with neural network baselines."

**TYPE:**
```bash
cat > compare_methods.py << 'EOF'
#!/usr/bin/env python3
"""
Compare LLM vs NN methods
"""
from hypatiax import test_suite

# Run physics tests with both methods
print("Comparing Methods on Physics Domain")
print("=" * 60)

print("\n1. Running with LLM method...")
llm_results = test_suite.run_domain('physics', method='llm')

print("\n2. Running with NN baseline...")
nn_results = test_suite.run_domain('physics', method='neural_network')

# Compare
print("\n" + "=" * 60)
print("COMPARISON")
print("=" * 60)
print(f"{'Method':<20} {'Success Rate':<15} {'Median Error':<15}")
print("-" * 60)
print(f"{'LLM':<20} {llm_results['success_rate']:<15.1f}% {llm_results['median_error']:<15.2e}")
print(f"{'Neural Network':<20} {nn_results['success_rate']:<15.1f}% {nn_results['median_error']:<15.2e}")
print("=" * 60)

improvement = (llm_results['success_rate'] - nn_results['success_rate'])
print(f"\nLLM improvement: +{improvement:.1f} percentage points")
EOF

python compare_methods.py
```

**SAY:**
> "This comparison shows the key result from our paper - the LLM-based method significantly outperforms traditional neural network approaches for symbolic discovery."

---

## Closing (14:00 - 15:00)

**SAY:**
> "Excellent! You now know how to run the HypatiaX test suite at any scale - from single tests to the complete 131-test benchmark. You've learned how to interpret the results and compare different methods."

**SAY:**
> "In the next tutorial, we'll take these results and generate publication-quality plots and statistical analyses - the figures and tables you see in our JMLR paper."

**[SHOW on screen]:**
```
✅ Ran single domain tests
✅ Interpreted results
✅ Ran full 131-test suite
✅ Compared methods

Next: Tutorial 3 - Analyzing Results & Generating Plots
```

**SAY:**
> "Thanks for watching Tutorial 2! See you in Tutorial 3!"

**[END RECORDING]**

---

## Post-Recording Notes

**Time stamps for YouTube description:**
```
0:00 - Introduction
0:45 - Understanding the Test Suite
3:00 - Running a Single Domain
6:30 - Interpreting Results
9:00 - Running the Full Suite
12:00 - Comparing Methods
14:00 - Conclusion
```

**Files created:**
- `view_test.py`
- `run_physics.py`
- `analyze_results.py`
- `run_full_suite.py`
- `compare_methods.py`
- `physics_results.json`

**Keep these for Tutorial 3!**

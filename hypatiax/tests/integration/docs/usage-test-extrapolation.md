I've created the test_extrapolation.py script with several enhancements:
Key features:

Comprehensive testing: Tests three different formulas:

Impermanent Loss (DeFi-specific)
Value at Risk (VaR) with 95% confidence
Quadratic function (control test)


Dual error metrics:

In-domain error: Performance within training range
Out-of-domain error: Performance in extrapolation region (2x beyond training)
Extrapolation ratio: How much worse the model performs when extrapolating


Enhanced visualization:

Clear distinction between training and extrapolation regions
Shaded extrapolation zone
Training boundary marked with vertical line
Proper legends and formatting


Robust evaluation:

Safe symbolic expression evaluation with error handling
Relative error metrics (percentage-based)
Prevents division by zero with epsilon values


Detailed reporting:

Per-test console output with metrics
Summary table comparing all tests
Average metrics across all formulas
Saved JSON results for further analysis


High-quality plots:

300 DPI resolution for publication
Tight layout for better appearance
Proper labeling and grid



What it measures:

How well symbolic regression discovers the true formula
Whether discovered formulas generalize beyond training data
Comparison of extrapolation performance across different function types

This is crucial for validating that the symbolic regression approach actually captures the underlying mathematical relationships rather than just fitting the data.
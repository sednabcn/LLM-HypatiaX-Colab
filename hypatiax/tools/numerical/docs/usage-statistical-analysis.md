I've created the comprehensive statistical_analysis.py script with the following features:
Statistical Analysis Components:

Descriptive Statistics:

Overall success rates and validation scores
Domain-specific breakdowns (DeFi vs Risk)
Score distributions (mean, median, std, min, max, quartiles)
Layer-wise score analysis (symbolic, dimensional, domain)

Hypothesis Testing:

Independent t-test: Compares DeFi vs Risk domains
Pearson correlation: Tests relationship between R² and validation scores
Complexity analysis: Compares valid vs invalid formula complexity
Includes effect sizes (Cohen's d) for practical significance

Visualizations (2 figures):

4-panel analysis plot:

Total score distribution histogram
R² score distribution histogram
Domain comparison boxplot
Complexity vs R² scatter plot

Layer scores bar chart:

Average scores for each validation layer
Clear comparison of symbolic, dimensional, and domain validation

Robust Data Handling:

Handles multiple JSON file formats
Graceful error handling for missing/malformed data
Supports different result structures

Comprehensive Output:

Console output with formatted tables
results/dataset_summary.json with all statistics and test results
results/statistical_analysis.png with multi-panel visualization
results/layer_scores.png with validation breakdown

Key Metrics Computed:

Success rates by domain
Score distributions and quartiles
Statistical significance tests
Effect sizes for practical importance
Correlation analyses

This provides a complete statistical overview of the dataset quality and characteristics, essential for validating the hybrid discovery system's performance.RetryClaude can make mistakes. Please double-check responses.

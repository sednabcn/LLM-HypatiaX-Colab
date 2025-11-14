# Module: `backup_before_extension/demo/complete-system-guide/usage_examples.py`

## Description

3. examples.py - Example Management System
Purpose: Manage training/test examples with categorization and validation
Key Classes:

Example: Single example with metadata
ExampleManager: Full example collection management
ExampleCategory: Enum for categories

Features:

✅ 15+ default examples across 5 categories
✅ Filter by category, difficulty, tags
✅ Random sampling with constraints
✅ Train/val/test splitting
✅ Generate example variations
✅ Export to JSON/CSV/spaCy format
✅ Collection statistics

Default Categories:

BASIC: Simple aggregations (sum, avg, count)
INTERMEDIATE: With grouping (by region, per product)
ADVANCED: Complex calculations (YoY growth, ratios)
EDGE_CASE: Special cases (COUNTD, MEDIAN, PERCENTILE)
TRAINING/VALIDATION/TEST: For model training

**Last Modified**: 2025-11-10T20:56:02.152130

## Dependencies

- `demo.examples`

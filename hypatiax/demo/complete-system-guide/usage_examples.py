"""
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

"""

from demo.examples import Example, ExampleCategory, ExampleManager

# Initialize manager (loads defaults)
manager = ExampleManager()

# Add custom example
new_example = Example(
    id="custom_01",
    description="calculate median order value",
    expected_formula="MEDIAN([Order Value])",
    category=ExampleCategory.INTERMEDIATE.value,
    difficulty=3,
    tags=["aggregation", "median", "statistical"],
)
manager.add_example(new_example)

# Filter examples
basic_examples = manager.filter_by_category("basic")
hard_examples = manager.filter_by_difficulty(4, 5)
sales_examples = manager.filter_by_tags(["sales"])

# Get random examples
random_sample = manager.get_random_examples(count=5, category="basic", difficulty=1)

# Split for training
train, val, test = manager.split_dataset(
    train_ratio=0.7, val_ratio=0.15, test_ratio=0.15
)

# Generate variations
base = manager.get_example("basic_sum_01")
variations = manager.generate_variations(base, count=3)

# Export
manager.save_to_file("examples.json", format="json")
manager.save_to_file("examples.csv", format="csv")
manager.export_for_training("training_data/", split=True)

# Statistics
stats = manager.get_statistics()
print(f"Total examples: {stats['total_examples']}")
print(f"Average difficulty: {stats['avg_difficulty']:.2f}")

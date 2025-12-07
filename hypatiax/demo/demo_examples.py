#!/usr/bin/env python3
"""
HypatiaX Demo Examples
Curated examples for demonstrating different capabilities

Curated example library
50+ example queries organized by category
Description, formula, and combined examples
Real-world use cases
Easy to access programmatically
"""

# Description examples - Natural language queries
DESCRIPTION_EXAMPLES = {
    "basic_calculations": [
        "calculate the sum of sales",
        "find the average profit",
        "compute the total revenue",
        "show the count of orders",
    ],
    "aggregations_with_dimensions": [
        "calculate the sum of sales by region",
        "find the average profit per category",
        "compute total revenue for each product",
        "show order count by customer segment",
    ],
    "time_based": [
        "calculate monthly sales totals",
        "find average daily profit",
        "show quarterly revenue trends",
        "compute yearly order counts",
    ],
    "complex_queries": [
        "calculate the sum of sales for each region where profit is positive",
        "find the average of top 10 products by revenue",
        "compute the percentage of total sales by category",
    ],
}

# Formula examples - Tableau calculation syntax
FORMULA_EXAMPLES = {
    "basic_aggregations": [
        "SUM([Sales])",
        "AVG([Profit])",
        "COUNT([Orders])",
        "MAX([Revenue])",
        "MIN([Cost])",
    ],
    "calculated_fields": [
        "SUM([Sales]) - SUM([Cost])",
        "AVG([Profit]) / AVG([Sales])",
        "[Sales] * [Quantity]",
        "[Revenue] - [Expenses]",
    ],
    "conditional_logic": [
        "IF [Sales] > 1000 THEN 'High' ELSE 'Low'",
        "IF [Profit] > 0 THEN [Profit] ELSE 0",
        "CASE [Region] WHEN 'East' THEN 1 WHEN 'West' THEN 2 ELSE 0 END",
    ],
    "string_operations": [
        "LEFT([Product Name], 5)",
        "UPPER([Category])",
        "CONTAINS([Description], 'sale')",
    ],
    "date_operations": [
        "YEAR([Order Date])",
        "MONTH([Ship Date])",
        "DATEDIFF('day', [Start Date], [End Date])",
    ],
}

# Combined examples - Description : Formula pairs
COMBINED_EXAMPLES = {
    "simple_mappings": [
        "calculate sum of sales : SUM([Sales])",
        "find average profit : AVG([Profit])",
        "compute total revenue : SUM([Revenue])",
        "show order count : COUNT([Orders])",
    ],
    "aggregations_with_dimensions": [
        "sum of sales by region : SUM([Sales])",
        "average profit per category : AVG([Profit])",
        "total revenue by product : SUM([Revenue])",
    ],
    "calculated_metrics": [
        "calculate profit margin : SUM([Profit]) / SUM([Sales])",
        "find sales growth rate : (SUM([Sales]) - PREVIOUS(SUM([Sales]))) / PREVIOUS(SUM([Sales]))",
        "compute average order value : SUM([Sales]) / COUNT([Orders])",
    ],
}

# Real-world use cases
USE_CASES = {
    "retail_analytics": [
        {
            "description": "Find total sales by product category",
            "formula": "SUM([Sales])",
            "context": "Retail dashboard showing category performance",
        },
        {
            "description": "Calculate profit margin percentage",
            "formula": "SUM([Profit]) / SUM([Sales])",
            "context": "Financial KPI tracking",
        },
        {
            "description": "Show top 10 customers by revenue",
            "formula": "RANK(SUM([Revenue]))",
            "context": "Customer segmentation analysis",
        },
    ],
    "sales_analytics": [
        {
            "description": "Calculate year-over-year growth",
            "formula": "(SUM([Sales]) - LOOKUP(SUM([Sales]), -1)) / LOOKUP(SUM([Sales]), -1)",
            "context": "Sales trend analysis",
        },
        {
            "description": "Find average deal size by sales rep",
            "formula": "AVG([Deal Amount])",
            "context": "Sales performance dashboard",
        },
    ],
    "financial_analytics": [
        {
            "description": "Calculate running total of revenue",
            "formula": "RUNNING_SUM(SUM([Revenue]))",
            "context": "Cumulative financial reporting",
        },
        {
            "description": "Compute return on investment",
            "formula": "(SUM([Revenue]) - SUM([Cost])) / SUM([Cost])",
            "context": "Investment analysis",
        },
    ],
}


def get_examples(category: str, subcategory: str = None) -> list:
    """
    Get examples by category and optional subcategory

    Args:
        category: 'description', 'formula', 'combined', or 'use_cases'
        subcategory: Specific subcategory within the category

    Returns:
        List of examples
    """
    categories = {
        "description": DESCRIPTION_EXAMPLES,
        "formula": FORMULA_EXAMPLES,
        "combined": COMBINED_EXAMPLES,
        "use_cases": USE_CASES,
    }

    if category not in categories:
        return []

    examples = categories[category]

    if subcategory and subcategory in examples:
        return examples[subcategory]

    # Return all examples in category if no subcategory specified
    all_examples = []
    for subcat_examples in examples.values():
        all_examples.extend(subcat_examples)

    return all_examples


def get_all_categories() -> dict:
    """Get all available categories and their subcategories"""
    return {
        "description": list(DESCRIPTION_EXAMPLES.keys()),
        "formula": list(FORMULA_EXAMPLES.keys()),
        "combined": list(COMBINED_EXAMPLES.keys()),
        "use_cases": list(USE_CASES.keys()),
    }


def print_examples_summary():
    """Print a summary of all available examples"""
    print("\n" + "=" * 70)
    print("HYPATIAX DEMO EXAMPLES CATALOG")
    print("=" * 70)

    categories = get_all_categories()

    for category, subcategories in categories.items():
        print(f"\n📁 {category.upper()}")
        for subcat in subcategories:
            examples = get_examples(category, subcat)
            print(f"  └─ {subcat}: {len(examples)} examples")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print_examples_summary()

    # Show some sample examples
    print("\n🔍 Sample Description Examples:")
    for example in get_examples("description", "basic_calculations")[:3]:
        print(f"  • {example}")

    print("\n🔍 Sample Formula Examples:")
    for example in get_examples("formula", "basic_aggregations")[:3]:
        print(f"  • {example}")

    print("\n🔍 Sample Combined Examples:")
    for example in get_examples("combined", "simple_mappings")[:3]:
        print(f"  • {example}")

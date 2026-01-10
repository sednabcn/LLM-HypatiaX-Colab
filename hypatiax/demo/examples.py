"""
HypatiaX Examples - Advanced example management and generation
Handles example datasets, validation, and benchmarking
"""

import csv
import json
import random
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ExampleCategory(Enum):
    """Categories for organizing examples"""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EDGE_CASE = "edge_case"
    TRAINING = "training"
    VALIDATION = "validation"
    TEST = "test"


@dataclass
class Example:
    """Represents a single training/test example"""

    id: str
    description: str
    expected_formula: str
    category: str = ExampleCategory.BASIC.value
    difficulty: int = 1  # 1-5 scale
    tags: List[str] = None
    notes: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Example":
        """Create from dictionary"""
        return cls(**data)


class ExampleManager:
    """Manages collections of examples for training and testing"""

    def __init__(self, examples_file: Optional[str] = None):
        """
        Initialize example manager

        Args:
            examples_file: Path to JSON file containing examples
        """
        self.examples: List[Example] = []
        self.examples_file = examples_file

        if examples_file and Path(examples_file).exists():
            self.load_from_file(examples_file)
        else:
            self._initialize_default_examples()

    def _initialize_default_examples(self):
        """Initialize with default example set"""
        default_examples = [
            # Basic aggregations
            Example(
                id="basic_sum_01",
                description="sum of sales",
                expected_formula="SUM([Sales])",
                category=ExampleCategory.BASIC.value,
                difficulty=1,
                tags=["aggregation", "sum", "sales"],
            ),
            Example(
                id="basic_avg_01",
                description="average profit",
                expected_formula="AVG([Profit])",
                category=ExampleCategory.BASIC.value,
                difficulty=1,
                tags=["aggregation", "average", "profit"],
            ),
            Example(
                id="basic_count_01",
                description="count of customers",
                expected_formula="COUNT([Customers])",
                category=ExampleCategory.BASIC.value,
                difficulty=1,
                tags=["aggregation", "count", "customers"],
            ),
            Example(
                id="basic_max_01",
                description="maximum revenue",
                expected_formula="MAX([Revenue])",
                category=ExampleCategory.BASIC.value,
                difficulty=1,
                tags=["aggregation", "max", "revenue"],
            ),
            Example(
                id="basic_min_01",
                description="minimum cost",
                expected_formula="MIN([Cost])",
                category=ExampleCategory.BASIC.value,
                difficulty=1,
                tags=["aggregation", "min", "cost"],
            ),
            # Intermediate - with grouping
            Example(
                id="inter_sum_by_01",
                description="sum of sales by region",
                expected_formula="SUM([Sales])",
                category=ExampleCategory.INTERMEDIATE.value,
                difficulty=2,
                tags=["aggregation", "sum", "groupby", "region"],
                notes="Grouping dimension implied in description",
            ),
            Example(
                id="inter_avg_per_01",
                description="average profit per product",
                expected_formula="AVG([Profit])",
                category=ExampleCategory.INTERMEDIATE.value,
                difficulty=2,
                tags=["aggregation", "average", "groupby", "product"],
            ),
            Example(
                id="inter_total_01",
                description="total revenue across all categories",
                expected_formula="SUM([Revenue])",
                category=ExampleCategory.INTERMEDIATE.value,
                difficulty=2,
                tags=["aggregation", "sum", "total", "categories"],
            ),
            # Advanced - complex queries
            Example(
                id="adv_calc_01",
                description="calculate year over year sales growth",
                expected_formula="(SUM([Sales]) - LOOKUP(SUM([Sales]), -1)) / LOOKUP(SUM([Sales]), -1)",
                category=ExampleCategory.ADVANCED.value,
                difficulty=4,
                tags=["calculation", "growth", "temporal", "lookup"],
                notes="Requires table calculation functions",
            ),
            Example(
                id="adv_ratio_01",
                description="profit margin as percentage of revenue",
                expected_formula="SUM([Profit]) / SUM([Revenue])",
                category=ExampleCategory.ADVANCED.value,
                difficulty=3,
                tags=["calculation", "ratio", "percentage"],
            ),
            Example(
                id="adv_running_01",
                description="running total of sales",
                expected_formula="RUNNING_SUM(SUM([Sales]))",
                category=ExampleCategory.ADVANCED.value,
                difficulty=3,
                tags=["calculation", "running_total", "temporal"],
            ),
            # Edge cases
            Example(
                id="edge_distinct_01",
                description="count distinct customers",
                expected_formula="COUNTD([Customers])",
                category=ExampleCategory.EDGE_CASE.value,
                difficulty=2,
                tags=["aggregation", "distinct", "count"],
                notes="Uses COUNTD instead of COUNT",
            ),
            Example(
                id="edge_median_01",
                description="median order value",
                expected_formula="MEDIAN([Order Value])",
                category=ExampleCategory.EDGE_CASE.value,
                difficulty=2,
                tags=["aggregation", "median", "statistical"],
            ),
            Example(
                id="edge_percentile_01",
                description="95th percentile of response time",
                expected_formula="PERCENTILE([Response Time], 0.95)",
                category=ExampleCategory.EDGE_CASE.value,
                difficulty=3,
                tags=["aggregation", "percentile", "statistical"],
            ),
            # Multi-word fields
            Example(
                id="multi_field_01",
                description="sum of order amount",
                expected_formula="SUM([Order Amount])",
                category=ExampleCategory.INTERMEDIATE.value,
                difficulty=2,
                tags=["aggregation", "multi_word_field"],
            ),
            Example(
                id="multi_field_02",
                description="average customer lifetime value",
                expected_formula="AVG([Customer Lifetime Value])",
                category=ExampleCategory.INTERMEDIATE.value,
                difficulty=2,
                tags=["aggregation", "multi_word_field"],
            ),
        ]

        self.examples = default_examples

    def add_example(self, example: Example) -> bool:
        """Add a new example"""
        # Check for duplicate IDs
        if any(e.id == example.id for e in self.examples):
            return False

        self.examples.append(example)
        return True

    def remove_example(self, example_id: str) -> bool:
        """Remove an example by ID"""
        original_length = len(self.examples)
        self.examples = [e for e in self.examples if e.id != example_id]
        return len(self.examples) < original_length

    def get_example(self, example_id: str) -> Optional[Example]:
        """Get a specific example by ID"""
        for example in self.examples:
            if example.id == example_id:
                return example
        return None

    def filter_by_category(self, category: str) -> List[Example]:
        """Get examples by category"""
        return [e for e in self.examples if e.category == category]

    def filter_by_difficulty(self, min_diff: int, max_diff: int) -> List[Example]:
        """Get examples by difficulty range"""
        return [e for e in self.examples if min_diff <= e.difficulty <= max_diff]

    def filter_by_tags(self, tags: List[str], match_all: bool = False) -> List[Example]:
        """
        Get examples by tags

        Args:
            tags: List of tags to match
            match_all: If True, example must have all tags; if False, any tag
        """
        if match_all:
            return [e for e in self.examples if all(tag in e.tags for tag in tags)]
        else:
            return [e for e in self.examples if any(tag in e.tags for tag in tags)]

    def get_random_examples(
        self,
        count: int,
        category: Optional[str] = None,
        difficulty: Optional[int] = None,
    ) -> List[Example]:
        """Get random examples with optional filtering"""
        filtered = self.examples

        if category:
            filtered = [e for e in filtered if e.category == category]

        if difficulty is not None:
            filtered = [e for e in filtered if e.difficulty == difficulty]

        return random.sample(filtered, min(count, len(filtered)))

    def split_dataset(
        self,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        shuffle: bool = True,
    ) -> Tuple[List[Example], List[Example], List[Example]]:
        """
        Split examples into train/validation/test sets

        Args:
            train_ratio: Proportion for training
            val_ratio: Proportion for validation
            test_ratio: Proportion for testing
            shuffle: Whether to shuffle before splitting

        Returns:
            Tuple of (train, validation, test) example lists
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001

        examples = self.examples.copy()
        if shuffle:
            random.shuffle(examples)

        total = len(examples)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)

        train = examples[:train_end]
        val = examples[train_end:val_end]
        test = examples[val_end:]

        return train, val, test

    def generate_variations(self, example: Example, count: int = 3) -> List[Example]:
        """
        Generate variations of an example

        Creates similar examples with different wording
        """
        variations = []

        # Templates for generating variations
        operation_synonyms = {
            "sum": ["total", "sum", "add up", "aggregate"],
            "average": ["average", "avg", "mean"],
            "count": ["count", "number of", "total count"],
            "max": ["maximum", "max", "highest", "largest"],
            "min": ["minimum", "min", "lowest", "smallest"],
        }

        # Extract operation from description
        desc_lower = example.description.lower()
        base_operation = None

        for op, synonyms in operation_synonyms.items():
            if any(syn in desc_lower for syn in synonyms):
                base_operation = op
                break

        if not base_operation:
            return []

        # Generate variations
        for i in range(count):
            synonym = random.choice(operation_synonyms[base_operation])
            new_desc = example.description

            for syn in operation_synonyms[base_operation]:
                if syn in desc_lower:
                    new_desc = new_desc.replace(syn, synonym)
                    break

            variations.append(
                Example(
                    id=f"{example.id}_var_{i + 1}",
                    description=new_desc,
                    expected_formula=example.expected_formula,
                    category=example.category,
                    difficulty=example.difficulty,
                    tags=example.tags + ["variation"],
                    notes=f"Variation of {example.id}",
                )
            )

        return variations

    def save_to_file(self, filepath: str, format: str = "json"):
        """
        Save examples to file

        Args:
            filepath: Output file path
            format: File format ('json', 'csv')
        """
        if format == "json":
            with open(filepath, "w") as f:
                data = [e.to_dict() for e in self.examples]
                json.dump(data, f, indent=2)

        elif format == "csv":
            with open(filepath, "w", newline="") as f:
                if not self.examples:
                    return

                fieldnames = self.examples[0].to_dict().keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for example in self.examples:
                    row = example.to_dict()
                    row["tags"] = ",".join(row["tags"])  # Convert list to string
                    writer.writerow(row)

    def load_from_file(self, filepath: str):
        """Load examples from file"""
        path = Path(filepath)

        if path.suffix == ".json":
            with open(filepath, "r") as f:
                data = json.load(f)
                self.examples = [Example.from_dict(item) for item in data]

        elif path.suffix == ".csv":
            with open(filepath, "r") as f:
                reader = csv.DictReader(f)
                self.examples = []

                for row in reader:
                    # Convert tags back to list
                    if "tags" in row and isinstance(row["tags"], str):
                        row["tags"] = row["tags"].split(",")
                    self.examples.append(Example.from_dict(row))

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the example collection"""
        if not self.examples:
            return {}

        stats = {
            "total_examples": len(self.examples),
            "by_category": {},
            "by_difficulty": {},
            "avg_difficulty": sum(e.difficulty for e in self.examples)
            / len(self.examples),
            "unique_tags": set(),
        }

        # Count by category
        for example in self.examples:
            stats["by_category"][example.category] = (
                stats["by_category"].get(example.category, 0) + 1
            )

            stats["by_difficulty"][example.difficulty] = (
                stats["by_difficulty"].get(example.difficulty, 0) + 1
            )

            stats["unique_tags"].update(example.tags)

        stats["unique_tags"] = len(stats["unique_tags"])

        return stats

    def export_for_training(self, output_dir: str, split: bool = True):
        """
        Export examples in format suitable for spaCy training

        Args:
            output_dir: Directory to save training files
            split: Whether to split into train/val/test
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if split:
            train, val, test = self.split_dataset()

            for name, dataset in [("train", train), ("val", val), ("test", test)]:
                data = {
                    "examples": [
                        {
                            "text": e.description,
                            "formula": e.expected_formula,
                            "meta": {
                                "category": e.category,
                                "difficulty": e.difficulty,
                                "tags": e.tags,
                            },
                        }
                        for e in dataset
                    ]
                }

                with open(output_path / f"{name}.json", "w") as f:
                    json.dump(data, f, indent=2)
        else:
            data = {
                "examples": [
                    {
                        "text": e.description,
                        "formula": e.expected_formula,
                        "meta": {
                            "category": e.category,
                            "difficulty": e.difficulty,
                            "tags": e.tags,
                        },
                    }
                    for e in self.examples
                ]
            }

            with open(output_path / "examples.json", "w") as f:
                json.dump(data, f, indent=2)

    def __len__(self) -> int:
        """Get number of examples"""
        return len(self.examples)

    def __iter__(self):
        """Iterate over examples"""
        return iter(self.examples)


# Example usage
if __name__ == "__main__":
    # Initialize manager
    manager = ExampleManager()

    print("HypatiaX Example Manager")
    print("=" * 50)

    # Show statistics
    stats = manager.get_statistics()
    print(f"\nTotal examples: {stats['total_examples']}")
    print(f"Average difficulty: {stats['avg_difficulty']:.2f}")
    print(f"Unique tags: {stats['unique_tags']}")

    print("\nExamples by category:")
    for category, count in stats["by_category"].items():
        print(f"  {category}: {count}")

    print("\nExamples by difficulty:")
    for diff, count in sorted(stats["by_difficulty"].items()):
        print(f"  Level {diff}: {count}")

    # Get some random examples
    print("\n" + "=" * 50)
    print("Random Basic Examples:")
    random_examples = manager.get_random_examples(3, category="basic")
    for ex in random_examples:
        print(f"\n  Description: {ex.description}")
        print(f"  Formula: {ex.expected_formula}")
        print(f"  Tags: {', '.join(ex.tags)}")

    # Generate variations
    print("\n" + "=" * 50)
    print("Example Variations:")
    base_example = manager.get_example("basic_sum_01")
    if base_example:
        variations = manager.generate_variations(base_example, count=3)
        for var in variations:
            print(f"\n  {var.description} → {var.expected_formula}")

    # Export examples
    print("\n" + "=" * 50)
    output_dir = "demo/example_exports"
    manager.save_to_file(f"{output_dir}/all_examples.json", format="json")
    manager.save_to_file(f"{output_dir}/all_examples.csv", format="csv")
    print(f"Examples exported to {output_dir}/")

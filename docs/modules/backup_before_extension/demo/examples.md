# Module: `backup_before_extension/demo/examples.py`

## Description

HypatiaX Examples - Advanced example management and generation
Handles example datasets, validation, and benchmarking

**Last Modified**: 2025-11-10T20:42:53.440191

## Dependencies

- `csv`
- `dataclasses`
- `enum`
- `json`
- `pathlib`
- `random`
- `typing`

## Constants

- `BASIC`
- `INTERMEDIATE`
- `ADVANCED`
- `EDGE_CASE`
- `TRAINING`
- `VALIDATION`
- `TEST`

## Classes

### `ExampleCategory`

**Inherits from**: `Enum`

Categories for organizing examples

### `Example`

Represents a single training/test example

**Decorators**: `dataclass`

**Methods**:

- `__post_init__(self)`
- `to_dict(self) -> Dict[<ast.Tuple object at 0x7fa6f85eced0>]`
  - Convert to dictionary
- `from_dict(cls, data: Dict[<ast.Tuple object at 0x7fa6f85ed050>]) -> <ast.Constant object at 0x7fa6f889a810>`
  - Create from dictionary

### `ExampleManager`

Manages collections of examples for training and testing

**Methods**:

- `__init__(self, examples_file: Optional[str])`
  - Initialize example manager
- `_initialize_default_examples(self)`
  - Initialize with default example set
- `add_example(self, example: Example) -> bool`
  - Add a new example
- `remove_example(self, example_id: str) -> bool`
  - Remove an example by ID
- `get_example(self, example_id: str) -> Optional[Example]`
  - Get a specific example by ID
- `filter_by_category(self, category: str) -> List[Example]`
  - Get examples by category
- `filter_by_difficulty(self, min_diff: int, max_diff: int) -> List[Example]`
  - Get examples by difficulty range
- `filter_by_tags(self, tags: List[str], match_all: bool) -> List[Example]`
  - Get examples by tags
- `get_random_examples(self, count: int, category: Optional[str], difficulty: Optional[int]) -> List[Example]`
  - Get random examples with optional filtering
- `split_dataset(self, train_ratio: float, val_ratio: float, test_ratio: float, shuffle: bool) -> Tuple[<ast.Tuple object at 0x7fa6f8514d50>]`
  - Split examples into train/validation/test sets
- `generate_variations(self, example: Example, count: int) -> List[Example]`
  - Generate variations of an example
- `save_to_file(self, filepath: str, format: str)`
  - Save examples to file
- `load_from_file(self, filepath: str)`
  - Load examples from file
- `get_statistics(self) -> Dict[<ast.Tuple object at 0x7fa6f8681690>]`
  - Get statistics about the example collection
- `export_for_training(self, output_dir: str, split: bool)`
  - Export examples in format suitable for spaCy training
- `__len__(self) -> int`
  - Get number of examples
- `__iter__(self)`
  - Iterate over examples

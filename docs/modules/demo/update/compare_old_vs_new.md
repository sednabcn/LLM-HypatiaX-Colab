# Module: `demo/update/compare_old_vs_new.py`

## Description

Comparison Demo: Old Sequential Pipeline vs Modern LLM (2025)
============================================================
Shows side-by-side comparison to demonstrate why LLMs are better.

Usage:
    python compare_old_vs_new.py

**Last Modified**: 2025-11-11T16:13:32.737642

## Dependencies

- `dataclasses`
- `modern_llm_mapper`
- `os`
- `random`
- `sys`
- `time`
- `typing`

## Constants

- `HAS_MODERN`
- `HAS_MODERN`

## Classes

### `OldSequentialPipeline`

Simulates the old 2018-style NER → Mapping → Generation pipeline
This is what you were building with training_spacy.py

**Methods**:

- `__init__(self)`
- `extract_entities(self, text: str) -> Dict`
  - Step 1: NER - Extract entities (70% accuracy)
- `map_to_formula_type(self, entities: Dict) -> str`
  - Step 2: Mapping - Map entities to formula type (80% accuracy)
- `generate_formula(self, formula_type: str) -> str`
  - Step 3: Generation - Generate formula from type (90% accuracy)
- `map_single(self, text: str) -> Dict`
  - Full pipeline execution

### `ComparisonResult`

Results from comparing both approaches

**Decorators**: `dataclass`

**Methods**:

- `print_comparison(self)`
  - Pretty print comparison

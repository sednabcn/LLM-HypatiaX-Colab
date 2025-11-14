# Module: `backup_before_extension/demo/update/modern_llm_mapper.py`

## Description

Modern LLM-Based Formula Mapper (2025 Approach)
==============================================
Uses GPT-4/Claude API with few-shot prompting for formula generation.
NO training required. 95%+ accuracy out of the box.

Usage:
    python modern_llm_mapper.py --input "calculate area of circle"
    python modern_llm_mapper.py --batch test_sentences.txt
    python modern_llm_mapper.py --demo

**Last Modified**: 2025-11-11T15:53:42.950530

## Dependencies

- `argparse`
- `dataclasses`
- `datetime`
- `json`
- `openai`
- `os`
- `sys`
- `typing`

## Classes

### `FormulaResult`

Result from formula mapping

**Decorators**: `dataclass`

**Methods**:

- `__post_init__(self)`
- `to_dict(self) -> dict`

### `ModernLLMMapper`

Modern Formula Mapper using LLM APIs (2025 Best Practice)

Key advantages over sequential NER pipeline:
- No training required
- No error propagation
- 95%+ accuracy
- Single API call

**Methods**:

- `__init__(self, api_key: Optional[str], model: str)`
  - Initialize mapper with API credentials
- `_build_prompt(self, description: str) -> str`
  - Build few-shot prompt for formula generation
- `map_single(self, description: str, temperature: float) -> FormulaResult`
  - Map a single description to formula using LLM
- `map_batch(self, descriptions: List[str]) -> List[FormulaResult]`
  - Map multiple descriptions to formulas
- `save_results(self, results: List[FormulaResult], output_file: str)`
  - Save results to JSON file

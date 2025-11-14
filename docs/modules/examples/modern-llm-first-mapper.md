# Module: `examples/modern-llm-first-mapper.py`

## Description

Modern LLM-First Formula Mapping (2025 Trends)
Primary: Few-shot prompting with GPT-4/Claude
Fallback: Fine-tuned smaller models for cost/latency

**Last Modified**: 2025-11-13T21:24:29.763839

## Dependencies

- `anthropic`
- `dataclasses`
- `openai`
- `os`
- `typing`

## Classes

### `ModernMapperConfig`

Configuration aligned with 2025 best practices

**Decorators**: `dataclass`

### `ModernFormulaMapper`

2025-Aligned Formula Mapper
Prioritizes: LLM API calls > Fine-tuned models > Rule-based fallback

**Methods**:

- `__init__(self, config: ModernMapperConfig)`
- `build_prompt(self, description: str) -> str`
  - Build optimized prompt for 2025 LLMs
- `map_with_llm(self, description: str) -> Dict`
  - Primary method: Use LLM API (2025 best practice)
- `map_with_fallback(self, description: str) -> Dict`
  - Fallback: Simple pattern matching (when API unavailable)
- `map(self, description: str) -> str`
  - Main entry point - uses LLM-first approach
- `batch_map(self, descriptions: List[str]) -> List[Dict]`
  - Batch processing with intelligent routing

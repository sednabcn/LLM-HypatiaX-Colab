# Module: `mappings/llm_mapping_.py`

**Last Modified**: 2025-11-13T10:54:31.529936

## Dependencies

- `pathlib`
- `sys`
- `tools.llm_providers.anthropic_provider`
- `tools.validation.symbolic_validator`

## Classes

### `LLMMapper`

LLM-based formula generation and mapping

Integrates with existing HypatiaX:
    - Uses NER results as input context
    - Validates with symbolic validator
    - Returns compatible format

Usage:
    mapper = LLMMapper(api_key="your-key")
    result = mapper.map("Calculate impermanent loss for ETH/USDC")

**Methods**:

- `__init__(self, api_key: str)`
- `map(self, query: str, domain: str, ner_entities: dict) -> dict`
  - Map natural language query to formula
- `_enhance_with_ner(self, query: str, ner_entities: dict) -> str`
  - Enhance query with NER context
- `_calculate_overall_score(self, formula: dict, validation: dict) -> float`
  - Calculate combined score

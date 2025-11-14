# Module: `mappings/hybrid_mapping.py`

## Description

Hybrid mapping combining all methods

**Last Modified**: 2025-11-12T16:47:36.498831

## Dependencies

- `typing`

## Classes

### `HybridMapper`

Ensemble mapper using multiple strategies

**Methods**:

- `__init__(self, ner_mapper, transformer_mapper, llm_mapper, agent_mapper)`
- `map(self, query: str, use_ner: bool, use_transformer: bool, use_llm: bool, use_agents: bool) -> Dict[<ast.Tuple object at 0x7fa6f86f6cd0>]`
  - Map using multiple strategies and combine results
- `_select_best(self, methods: Dict) -> Optional[str]`
  - Select best expression from multiple methods

# Module: `mappings/transformer_mapping.py`

## Description

Transformer-based expression mapping

**Last Modified**: 2025-11-12T16:47:36.498831

## Dependencies

- `typing`

## Classes

### `TransformerMapper`

Map queries using transformer models

**Methods**:

- `__init__(self, model_path: str)`
- `map(self, query: str) -> Dict[<ast.Tuple object at 0x7fa6f86f6390>]`
  - Map query to expression using transformer

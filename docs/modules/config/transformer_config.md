# Module: `config/transformer_config.py`

## Description

Transformer model configurations

**Last Modified**: 2025-11-12T16:47:36.486831

## Dependencies

- `typing`

## Constants

- `BERT_MODEL`
- `T5_MODEL`
- `LEARNING_RATE`
- `BATCH_SIZE`
- `NUM_EPOCHS`
- `MAX_LENGTH`
- `TRANSFORMER_MODEL_DIR`
- `TRANSFORMER_DATA_DIR`

## Classes

### `TransformerConfig`

Configuration for BERT/T5 models

**Methods**:

- `get_config(cls, model_type: str) -> Dict[<ast.Tuple object at 0x7fa6f88dd410>]`
  - Get configuration for specific model type

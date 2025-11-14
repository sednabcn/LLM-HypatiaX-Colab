# Module: `core/preprocessing/transformer_prep.py`

## Description

Transformer data preprocessing

**Last Modified**: 2025-11-12T16:47:36.490831

## Dependencies

- `json`
- `transformers`
- `typing`

## Classes

### `TransformerPreprocessor`

Preprocess data for transformer models

**Methods**:

- `__init__(self, model_name: str)`
- `prepare_seq2seq_data(self, input_texts: List[str], target_texts: List[str], max_length: int) -> Dict[<ast.Tuple object at 0x7fa6f863c0d0>]`
  - Prepare data for sequence-to-sequence task
- `save_prepared_data(self, data: Dict, output_path: str)`
  - Save prepared data to file

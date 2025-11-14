# Module: `core/training/training_tranformer_.py`

## Description

Transformer-based Training for Formula Mapping
Uses BERT/T5 models via Hugging Face Transformers

**Last Modified**: 2025-11-07T15:14:05.660389

## Dependencies

- `dataclasses`
- `json`
- `matplotlib.pyplot`
- `numpy`
- `pandas`
- `pathlib`
- `torch`
- `torch.utils.data`
- `transformers`
- `typing`

## Classes

### `TransformerConfig`

Configuration for transformer training

**Decorators**: `dataclass`

### `FormulaMappingDataset`

**Inherits from**: `Dataset`

Dataset for seq2seq formula mapping

**Methods**:

- `__init__(self, data: List[Dict], tokenizer, max_length: int)`
- `__len__(self)`
- `__getitem__(self, idx)`

### `TransformerTrainer`

Train transformer models for formula mapping

**Methods**:

- `__init__(self, config: TransformerConfig)`
- `load_data(self, train_path: str, val_path: str) -> Tuple[<ast.Tuple object at 0x7fa6f854da90>]`
  - Load training and validation data
- `prepare_model(self)`
  - Initialize tokenizer and model
- `train(self, train_data: List[Dict], val_data: List[Dict])`
  - Train the model
- `plot_history(self, save_path: str)`
  - Plot training history
- `predict(self, descriptions: List[str]) -> List[str]`
  - Generate formulas for descriptions

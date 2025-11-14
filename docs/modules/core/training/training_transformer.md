# Module: `core/training/training_transformer.py`

## Description

Transformer model training

**Last Modified**: 2025-11-12T16:47:36.490831

## Dependencies

- `torch`
- `transformers`
- `typing`

## Classes

### `TransformerTrainer`

Train transformer models for expression mapping

**Methods**:

- `__init__(self, model_name: str, output_dir: str)`
- `initialize_model(self)`
  - Initialize model for training
- `train(self, train_dataset, eval_dataset, num_epochs: int, learning_rate: float, batch_size: int)`
  - Train the transformer model
- `save_model(self, path: str)`
  - Save trained model

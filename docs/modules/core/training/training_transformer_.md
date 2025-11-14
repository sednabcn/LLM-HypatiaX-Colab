# Module: `core/training/training_transformer_.py`

## Description

Modern Transformer Training (2025 Best Practices)
Uses: LoRA fine-tuning on modern open-source models
Replaces: Full fine-tuning of outdated models like T5-small

**Last Modified**: 2025-11-11T12:03:09.229228

## Dependencies

- `dataclasses`
- `datasets`
- `json`
- `os`
- `peft`
- `torch`
- `transformers`
- `typing`
- `wandb`

## Classes

### `TrainingConfig`

Modern training configuration for 2025

**Decorators**: `dataclass`

**Methods**:

- `__post_init__(self)`

### `ModernFormulaTrainer`

2025 Approach: Fine-tune modern LLMs with LoRA
- Uses parameter-efficient methods (saves 99% memory)
- Instruction-tuned format
- Quantization-aware training

**Methods**:

- `__init__(self, config: TrainingConfig)`
- `prepare_training_data(self, data_path: str) -> Dataset`
  - Convert data to instruction format (2025 standard)
- `load_model(self)`
  - Load model with 8-bit quantization (QLoRA)
- `train(self, train_dataset: Dataset, val_dataset: Optional[Dataset])`
  - Modern training with best practices
- `inference(self, description: str) -> str`
  - Run inference with the fine-tuned model

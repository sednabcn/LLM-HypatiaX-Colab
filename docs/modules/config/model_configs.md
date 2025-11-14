# Module: `config/model_configs.py`

## Description

Model and Training Configuration

Centralized configurations for model training, data processing, and evaluation.

**Last Modified**: 2025-11-09T18:28:21.343197

## Dependencies

- `dataclasses`
- `typing`

## Classes

### `TrainingConfig`

Configuration for model training.

Usage:
    config = TrainingConfig(niter=50, batchsize=16)
    config_dict = config.to_dict()

**Decorators**: `dataclass`

**Methods**:

- `to_dict(self) -> Dict[<ast.Tuple object at 0x7fa6f88dddd0>]`
  - Convert to dictionary
- `update(self) -> <ast.Constant object at 0x7fa6f88dc750>`
  - Update configuration with new values
- `quick_train(cls) -> <ast.Constant object at 0x7fa6f88a2a90>`
  - Quick training config (for testing)
- `production(cls) -> <ast.Constant object at 0x7fa6f88a3990>`
  - Production training config (best quality)

### `DataConfig`

Configuration for data processing.

Usage:
    config = DataConfig.for_descriptions()
    config.update(test_size=0.3)

**Decorators**: `dataclass`

**Methods**:

- `to_dict(self) -> Dict[<ast.Tuple object at 0x7fa6f88a2810>]`
  - Convert to dictionary
- `update(self) -> <ast.Constant object at 0x7fa6f88c84d0>`
  - Update configuration
- `for_descriptions(cls) -> <ast.Constant object at 0x7fa6f88c8c50>`
  - Config for description data
- `for_formulas(cls) -> <ast.Constant object at 0x7fa6f88cb510>`
  - Config for formula data
- `for_combined(cls) -> <ast.Constant object at 0x7fa6f8550650>`
  - Config for combined data

### `ModelConfig`

Complete model configuration combining training and data configs.

Usage:
    config = ModelConfig.training_desc()
    print(config.training.niter)
    print(config.data.filename)

**Decorators**: `dataclass`

**Methods**:

- `to_dict(self) -> Dict[<ast.Tuple object at 0x7fa6f8550550>]`
  - Convert entire config to dictionary
- `training_desc(cls, niter: int, batchsize: int, sizefile: str) -> <ast.Constant object at 0x7fa6f8553290>`
  - Config for training description NER model.
- `training_formulas(cls, niter: int, batchsize: int, sizefile: str) -> <ast.Constant object at 0x7fa6f8538350>`
  - Config for training formula NER model
- `training_combined(cls, niter: int, batchsize: int, sizefile: str) -> <ast.Constant object at 0x7fa6f853a010>`
  - Config for training combined model
- `quick_test(cls) -> <ast.Constant object at 0x7fa6f866f850>`
  - Quick config for testing (fast training)

### `EvaluationConfig`

Configuration for model evaluation

**Decorators**: `dataclass`

**Methods**:

- `to_dict(self) -> Dict[<ast.Tuple object at 0x7fa6f88af350>]`

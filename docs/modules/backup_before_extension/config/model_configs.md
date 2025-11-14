# Module: `backup_before_extension/config/model_configs.py`

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

- `to_dict(self) -> Dict[<ast.Tuple object at 0x7fa6f8666910>]`
  - Convert to dictionary
- `update(self) -> <ast.Constant object at 0x7fa6f8664d90>`
  - Update configuration with new values
- `quick_train(cls) -> <ast.Constant object at 0x7fa6f851c950>`
  - Quick training config (for testing)
- `production(cls) -> <ast.Constant object at 0x7fa6f851cf10>`
  - Production training config (best quality)

### `DataConfig`

Configuration for data processing.

Usage:
    config = DataConfig.for_descriptions()
    config.update(test_size=0.3)

**Decorators**: `dataclass`

**Methods**:

- `to_dict(self) -> Dict[<ast.Tuple object at 0x7fa6f85bcc50>]`
  - Convert to dictionary
- `update(self) -> <ast.Constant object at 0x7fa6f85bc750>`
  - Update configuration
- `for_descriptions(cls) -> <ast.Constant object at 0x7fa6f85db310>`
  - Config for description data
- `for_formulas(cls) -> <ast.Constant object at 0x7fa6f85d8ad0>`
  - Config for formula data
- `for_combined(cls) -> <ast.Constant object at 0x7fa6f85d9190>`
  - Config for combined data

### `ModelConfig`

Complete model configuration combining training and data configs.

Usage:
    config = ModelConfig.training_desc()
    print(config.training.niter)
    print(config.data.filename)

**Decorators**: `dataclass`

**Methods**:

- `to_dict(self) -> Dict[<ast.Tuple object at 0x7fa6f85db5d0>]`
  - Convert entire config to dictionary
- `training_desc(cls, niter: int, batchsize: int, sizefile: str) -> <ast.Constant object at 0x7fa6f8622d10>`
  - Config for training description NER model.
- `training_formulas(cls, niter: int, batchsize: int, sizefile: str) -> <ast.Constant object at 0x7fa6f8622150>`
  - Config for training formula NER model
- `training_combined(cls, niter: int, batchsize: int, sizefile: str) -> <ast.Constant object at 0x7fa6f88af510>`
  - Config for training combined model
- `quick_test(cls) -> <ast.Constant object at 0x7fa6f856ea90>`
  - Quick config for testing (fast training)

### `EvaluationConfig`

Configuration for model evaluation

**Decorators**: `dataclass`

**Methods**:

- `to_dict(self) -> Dict[<ast.Tuple object at 0x7fa6f859fb90>]`

# Module: `config/base.py`

## Description

Base Configuration Class

Central configuration management for HypatiaX.

**Last Modified**: 2025-11-09T18:25:24.274355

## Dependencies

- `constants`
- `dataclasses`
- `json`
- `model_configs`
- `os`
- `pathlib`
- `paths`
- `typing`

## Classes

### `Config`

Main configuration class that ties together all config components.

Usage:
    config = Config()
    config.print_all()
    config.save_to_file('config.json')

**Methods**:

- `__init__(self)`
- `_detect_environment(self) -> str`
  - Detect execution environment
- `print_all(self)`
  - Print all configuration settings
- `save_to_file(self, filepath: str)`
  - Save configuration to JSON file
- `get(self, key: str, default: Any) -> Any`
  - Get configuration value by key

### `BaseDataConfig`

Base configuration for data processing

**Decorators**: `dataclass`

**Methods**:

- `to_dict(self) -> Dict[<ast.Tuple object at 0x7fa6f88d99d0>]`
  - Convert to dictionary
- `update(self)`
  - Update configuration

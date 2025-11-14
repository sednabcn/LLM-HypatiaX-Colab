# Module: `config/paths.py`

## Description

Path Configuration Management

Handles all path-related configurations with environment detection.

**Last Modified**: 2025-11-09T18:26:16.953414

## Dependencies

- `logging`
- `os`
- `pathlib`
- `typing`

## Classes

### `PathConfig`

Centralized path management for HypatiaX.

Automatically detects project root and sets up all necessary paths.
Supports multiple environments (local, Colab, GitHub Actions, etc.)

Usage:
    from hypatiax.config import paths
    
    # Access paths
    datasets_dir = paths.datasets
    output_file = paths.get_output_path('models', 'my_model')

**Methods**:

- `__init__(self, project_name: str)`
- `_detect_environment(self) -> str`
  - Detect the current execution environment
- `_find_project_root(self) -> Path`
  - Find project root directory
- `get_output_path(self) -> Path`
  - Get path within outputs directory.
- `get_dataset_path(self, domain: str, sub_domain: str, action: str, filename: Optional[str]) -> Path`
  - Get dataset path with standard structure.
- `get_model_path(self, domain: str, sub_domain: str, model_name: Optional[str]) -> Path`
  - Get model path within data_spacy directory.
- `get_rules_path(self, domain: str, sub_domain: str, filename: Optional[str]) -> Path`
  - Get path to custom rules files
- `validate_path(self, path: Union[<ast.Tuple object at 0x7fa6f86f0c10>]) -> bool`
  - Check if path exists and is accessible
- `ensure_directory(self) -> Path`
  - Create directory if it doesn't exist
- `print_paths(self)`
  - Print all configured paths
- `to_dict(self) -> dict`
  - Convert paths to dictionary

# Module: `config/config.py`

## Description

Universal configuration for HypatiaX project.
Works in: Local development, GitHub Actions, Docker, Cloud environments.

**Last Modified**: 2025-11-13T16:02:18.158746

## Dependencies

- `hypatiax`
- `logging`
- `os`
- `pathlib`
- `sys`
- `tempfile`
- `typing`

## Classes

### `PathConfig`

Universal path configuration for HypatiaX.

Priority for finding project root:
1. HYPATIAX_ROOT environment variable (explicit override)
2. GITHUB_WORKSPACE (GitHub Actions)
3. Docker standard paths (/app, /workspace, /code)
4. Detect from current file location (development)
5. Detect from installed package location (production)
6. Current working directory (fallback)

Environment detection:
- Local development: Uses project structure
- GitHub Actions: Uses GITHUB_WORKSPACE
- Docker: Uses /app or custom mount point
- Cloud: Uses environment variables

**Methods**:

- `__init__(self, custom_root: Optional[Path])`
  - Initialize path configuration.
- `_detect_environment() -> str`
  - Detect the current execution environment.
- `_find_project_root(self) -> Path`
  - Find the project root directory with multi-environment support.
- `_setup_paths(self)`
  - Setup all standard paths based on project structure.
- `_validate_environment(self)`
  - Validate that the environment is properly configured.
- `root(self) -> Path`
  - Project root directory.
- `hypatiax(self) -> Path`
  - HypatiaX package directory.
- `datasets(self) -> Path`
  - Datasets directory.
- `data_spacy(self) -> Path`
  - Spacy data directory.
- `outputs(self) -> Path`
  - Output directory (environment-aware).
- `tests(self) -> Path`
  - Tests directory.
- `agents(self) -> Path`
  - Agents directory.
- `core(self) -> Path`
  - Core directory.
- `models(self) -> Path`
  - Models directory.
- `tools(self) -> Path`
  - Tools directory.
- `utils(self) -> Path`
  - Utils directory.
- `custom_entities(self) -> Path`
  - Custom entities directory.
- `custom_ner(self) -> Path`
  - Custom NER directory.
- `config_dir(self) -> Path`
  - Config directory.
- `patterns(self) -> Path`
  - Patterns directory.
- `mappings(self) -> Path`
  - Mappings directory.
- `examples(self) -> Path`
  - Examples directory.
- `experiments(self) -> Path`
  - Experiments directory.
- `docs(self) -> Path`
  - Documentation directory.
- `demo(self) -> Path`
  - Demo directory.
- `get_dataset_path(self) -> Path`
  - Get path within datasets directory.
- `get_spacy_path(self) -> Path`
  - Get path within spacy data directory.
- `get_output_path(self) -> Path`
  - Get path within outputs directory.
- `get_test_path(self) -> Path`
  - Get path within tests directory.
- `get_agent_path(self) -> Path`
  - Get path within agents directory.
- `get_model_path(self) -> Path`
  - Get path within models directory.
- `get_tool_path(self) -> Path`
  - Get path within tools directory.
- `exists(self, path_type: str) -> bool`
  - Check if a standard path exists.
- `ensure_output_dirs(self) -> Dict[<ast.Tuple object at 0x7fa6f88dbf50>]`
  - Ensure multiple output subdirectories exist.
- `list_available_paths(self) -> List[str]`
  - List all available path properties.
- `to_dict(self) -> Dict[<ast.Tuple object at 0x7fa6f853bb50>]`
  - Export configuration as dictionary.
- `print_config(self)`
  - Print complete configuration for debugging.
- `__repr__(self) -> str`

# Module: `backup_before_extension/utils/path_manager.py`

**Last Modified**: 2025-11-06T12:30:05.293475

## Dependencies

- `logging`
- `os`
- `pathlib`
- `sys`
- `typing`

## Classes

### `PathManager`

Universal path manager for local, GitHub, and cloud environments

**Methods**:

- `__init__(self, project_name: str)`
- `_detect_environment(self) -> str`
  - Detect the current execution environment
- `_get_project_root(self) -> Path`
  - Get project root based on environment
- `get_path(self) -> Optional[Path]`
  - Build path from project root
- `walk_directory(self) -> List[Tuple[<ast.Tuple object at 0x7fa6f85167d0>]]`
  - Walk directory with error handling
- `list_files(self) -> List[Path]`
  - List all files in directory
- `ensure_directory(self) -> Optional[Path]`
  - Create directory if it doesn't exist
- `validate_path(self) -> bool`
  - Check if path exists and is accessible

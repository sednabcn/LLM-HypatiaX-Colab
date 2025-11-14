# Module: `auto_migrate.py`

## Description

Smart Auto-Migrate System with Automatic Backup
================================================
Keeps ALL older versions with timestamps
Automatic backup before/after file operations
Auto-restore on validation failure

Features:
- Tracks all file/directory changes
- Creates timestamped backups automatically
- Validates content (JSONL, JSON, NER models)
- Auto-restores from last good backup if broken
- Decorator & context manager for automatic protection
- Version history with rollback capability

**Last Modified**: 2025-11-12T18:10:27.519347

## Dependencies

- `contextlib`
- `datetime`
- `functools`
- `hashlib`
- `importlib`
- `json`
- `pathlib`
- `shutil`
- `sys`
- `typing`

## Classes

### `AutoMigrate`

Smart auto-migration with version control.

**Methods**:

- `__init__(self, backup_root: Optional[Path])`
- `_load_state(self) -> Dict`
- `_save_state(self)`
- `_resolve_path(self, filename: str, style: str, package: str, modules: str, domains: str, sub_domains: str, folder: str) -> Optional[Path]`
  - Resolve filename to actual path.
- `_get_hash(self, path: Path) -> Optional[str]`
  - Calculate hash of file or directory.
- `_validate(self, path: Path, style: str) -> tuple`
  - Validate file/directory based on style.
- `_create_backup(self, path: Path, backup_subdir: str, reason: str) -> Optional[Path]`
  - Create timestamped backup - KEEPS ALL OLD VERSIONS.
- `execute(self, action: str, filename: str, style: str, package: str, modules: str, domains: str, sub_domains: str, folder: str, backup_subdir: Optional[str], backup_index: int, force: bool) -> Dict`
  - Execute an action on a file/directory.
- `_migrate(self, obj_path: Path, style: str, backup_subdir: str, force: bool) -> Dict`
  - Migrate: detect changes, create backups, auto-restore if broken.
- `_list_backups(self, obj_path: Path) -> Dict`
  - List ALL backups for an object.
- `_restore(self, obj_path: Path, backup_index: int) -> Dict`
  - Restore from any backup version.

### `AutoBackup`

Decorator and context manager for automatic backups.

**Methods**:

- `__init__(self, migrator: Optional[AutoMigrate])`
- `before_use(self, filename: str, style: str)`
  - Decorator: Create backup BEFORE using a file.
- `after_use(self, filename: str, style: str)`
  - Decorator: Create backup AFTER using a file.
- `protect(self, filename: str, style: str, when: str)`
  - Context manager: Create backup before/after/both.

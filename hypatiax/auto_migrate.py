#!/usr/bin/env python3
"""
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
"""

import hashlib
import json
import shutil
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from importlib import resources
from pathlib import Path
from typing import Any, Callable, Dict, Optional


class AutoMigrate:
    """Smart auto-migration with version control."""

    def __init__(self, backup_root: Optional[Path] = None):
        if backup_root is None:
            current = Path(__file__).parent
            while current.name != "hypatiax" and current.parent != current:
                current = current.parent
            self.backup_root = current / ".versions"
        else:
            self.backup_root = Path(backup_root)

        self.backup_root.mkdir(exist_ok=True)
        self.state_file = self.backup_root / "state.json"
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if self.state_file.exists():
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {"tracked": {}}

    def _save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def _resolve_path(
        self,
        filename: str,
        style: str,
        package: str,
        modules: str,
        domains: str,
        sub_domains: str,
        folder: str,
    ) -> Optional[Path]:
        """
        Resolve filename to actual path.

        Args:
            filename: "ruler_tableau_desc.jsonl", "ner_tableau_desc", etc.
            style: "rules", "ner", "entity", "models", "csv", etc.
            package: "hypatiax"
            modules: "custom_ner", "data_spacy", "datasets"
            domains: "queries"
            sub_domains: "tableau"
            folder: "rules", "training_spacy", "testing_spacy", etc.
        """
        path_domains = f"{package}.{modules}.{domains}.{sub_domains}"

        try:
            if style in ["ner", "models"]:
                # Directories in path_domains
                resolved = resources.files(path_domains).joinpath(filename)
            else:
                # Files in folder
                path_dir = f"{path_domains}.{folder}"
                resolved = resources.files(path_dir).joinpath(filename)

            return Path(str(resolved))
        except Exception as e:
            print(f"⚠️  Could not resolve path: {e}")
            return None

    def _get_hash(self, path: Path) -> Optional[str]:
        """Calculate hash of file or directory."""
        if not path.exists():
            return None

        if path.is_file():
            hash_md5 = hashlib.md5()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()

        elif path.is_dir():
            hash_md5 = hashlib.md5()
            for file_path in sorted(path.rglob("*")):
                if file_path.is_file():
                    hash_md5.update(str(file_path.relative_to(path)).encode())
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
            return hash_md5.hexdigest()

        return None

    def _validate(self, path: Path, style: str) -> tuple:
        """
        Validate file/directory based on style.

        Returns:
            (is_valid: bool, reason: str)
        """
        if not path.exists():
            return False, "missing"

        if path.is_file():
            # JSONL validation (rules)
            if style == "rules" or path.suffix == ".jsonl":
                try:
                    with open(path, "r") as f:
                        for line in f:
                            if line.strip():
                                json.loads(line)
                    return True, "ok"
                except json.JSONDecodeError as e:
                    return False, f"invalid_jsonl: {e}"
                except Exception as e:
                    return False, f"error: {e}"

            # JSON validation
            elif path.suffix == ".json":
                try:
                    with open(path, "r") as f:
                        json.load(f)
                    return True, "ok"
                except json.JSONDecodeError as e:
                    return False, f"invalid_json: {e}"

            # Other files just check existence
            else:
                return True, "ok"

        elif path.is_dir():
            # NER/Models must have meta.json and config.cfg
            if style in ["ner", "models"]:
                required = ["meta.json", "config.cfg"]
                for req in required:
                    if not (path / req).exists():
                        return False, f"missing_{req}"

            return True, "ok"

        return True, "ok"

    def _create_backup(
        self, path: Path, backup_subdir: str, reason: str = "auto"
    ) -> Optional[Path]:
        """
        Create timestamped backup - KEEPS ALL OLD VERSIONS.

        Example backup structure:
            .versions/
                custom_ner/queries/tableau/rules/
                    ruler_tableau_desc_initial_20241112_143022.jsonl
                    ruler_tableau_desc_changed_20241112_150133.jsonl
                    ruler_tableau_desc_changed_20241112_151044.jsonl
                    ruler_tableau_desc_forced_20241112_152155.jsonl
        """
        if not path.exists():
            return None

        # Create backup directory
        backup_dir = self.backup_root / backup_subdir
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if path.is_file():
            backup_name = f"{path.stem}_{reason}_{timestamp}{path.suffix}"
        else:
            backup_name = f"{path.name}_{reason}_{timestamp}"

        backup_path = backup_dir / backup_name

        try:
            if path.is_file():
                shutil.copy2(path, backup_path)
            else:
                shutil.copytree(path, backup_path)

            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None

    def execute(
        self,
        action: str,
        filename: str,
        style: str,
        package: str = "hypatiax",
        modules: str = "custom_ner",
        domains: str = "queries",
        sub_domains: str = "tableau",
        folder: str = "rules",
        backup_subdir: Optional[str] = None,
        backup_index: int = -1,
        force: bool = False,
    ) -> Dict:
        """
        Execute an action on a file/directory.

        Args:
            action: "migrate", "list", "restore"
            filename: File/directory name
            style: "rules", "ner", "entity", "models", "csv", etc.
            package: Package name (default: "hypatiax")
            modules: Module (e.g., "custom_ner", "data_spacy", "datasets")
            domains: Domain (default: "queries")
            sub_domains: Sub-domain (default: "tableau")
            folder: Folder within sub_domains (e.g., "rules", "training_spacy")
            backup_subdir: Where to save backups (default: auto-generated)
            backup_index: For restore action, which backup to use
            force: Force backup even if unchanged

        Returns:
            Dictionary with results

        Example:
            # Migrate rules file
            execute("migrate", "ruler_tableau_desc.jsonl", "rules",
                    modules="custom_ner", folder="rules")

            # Migrate NER model
            execute("migrate", "ner_tableau_desc", "ner",
                    modules="data_spacy", folder="")

            # List backups
            execute("list", "ruler_tableau_desc.jsonl", "rules")

            # Restore
            execute("restore", "ruler_tableau_desc.jsonl", "rules", backup_index=0)
        """

        # Resolve path
        obj_path = self._resolve_path(
            filename, style, package, modules, domains, sub_domains, folder
        )

        if obj_path is None:
            return {"status": "error", "message": "Could not resolve path"}

        # Auto-generate backup_subdir if not provided
        if backup_subdir is None:
            backup_subdir = f"{modules}/{domains}/{sub_domains}/{folder}"

        # Execute action
        if action == "migrate":
            return self._migrate(obj_path, style, backup_subdir, force)

        elif action == "list":
            return self._list_backups(obj_path)

        elif action == "restore":
            return self._restore(obj_path, backup_index)

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def _migrate(
        self, obj_path: Path, style: str, backup_subdir: str, force: bool
    ) -> Dict:
        """
        Migrate: detect changes, create backups, auto-restore if broken.
        KEEPS ALL OLD VERSIONS with timestamps.
        """

        print(f"\n🔍 Migrating: {obj_path.name}")
        print(f"   Style: {style}")

        # Validate
        is_valid, reason = self._validate(obj_path, style)

        if not is_valid:
            print(f"   ⚠️  INVALID: {reason}")

            # Try auto-restore from last good backup
            obj_key = str(obj_path)
            if obj_key in self.state["tracked"]:
                backups = self.state["tracked"][obj_key].get("backups", [])
                if backups:
                    latest = backups[-1]
                    backup_path = Path(latest["path"])

                    if backup_path.exists():
                        print(f"   🔄 Auto-restoring from: {backup_path.name}")

                        try:
                            if backup_path.is_file():
                                shutil.copy2(backup_path, obj_path)
                            else:
                                if obj_path.exists():
                                    shutil.rmtree(obj_path)
                                shutil.copytree(backup_path, obj_path)

                            print(f"   ✅ Restored")
                            return {"status": "restored", "reason": reason}
                        except Exception as e:
                            print(f"   ❌ Restore failed: {e}")
                            return {"status": "broken", "reason": reason}

            return {"status": "broken", "reason": reason}

        # Get current hash
        current_hash = self._get_hash(obj_path)
        obj_key = str(obj_path)

        # Check if tracked
        if obj_key not in self.state["tracked"]:
            # NEW - create initial backup
            print(f"   🆕 New object")

            backup_path = self._create_backup(obj_path, backup_subdir, "initial")

            if backup_path:
                print(f"   📦 Backup: {backup_path.name}")

            self.state["tracked"][obj_key] = {
                "hash": current_hash,
                "style": style,
                "backup_subdir": backup_subdir,
                "last_check": datetime.now().isoformat(),
                "backups": [
                    {
                        "path": str(backup_path),
                        "timestamp": datetime.now().isoformat(),
                        "reason": "initial",
                        "hash": current_hash,
                    }
                ],
            }

            self._save_state()
            return {
                "status": "new",
                "backup": str(backup_path) if backup_path else None,
            }

        # EXISTING - check changes
        old_hash = self.state["tracked"][obj_key]["hash"]

        if current_hash != old_hash or force:
            reason = "forced" if force else "changed"
            print(f"   🔄 {reason.capitalize()}")

            # Create new backup (keeps old ones too!)
            backup_path = self._create_backup(obj_path, backup_subdir, reason)

            if backup_path:
                print(f"   📦 Backup: {backup_path.name}")

            self.state["tracked"][obj_key]["hash"] = current_hash
            self.state["tracked"][obj_key]["last_check"] = datetime.now().isoformat()
            self.state["tracked"][obj_key]["backups"].append(
                {
                    "path": str(backup_path),
                    "timestamp": datetime.now().isoformat(),
                    "reason": reason,
                    "hash": current_hash,
                }
            )

            self._save_state()
            return {
                "status": reason,
                "backup": str(backup_path) if backup_path else None,
            }

        else:
            print(f"   ✓ No changes")
            return {"status": "unchanged"}

    def _list_backups(self, obj_path: Path) -> Dict:
        """List ALL backups for an object."""
        obj_key = str(obj_path)

        print(f"\n📦 Backups for: {obj_path.name}")
        print("-" * 60)

        if obj_key not in self.state["tracked"]:
            print("   No backups found")
            return {"status": "none", "backups": []}

        backups = self.state["tracked"][obj_key].get("backups", [])

        if not backups:
            print("   No backups found")
            return {"status": "none", "backups": []}

        for i, backup in enumerate(backups):
            backup_name = Path(backup["path"]).name
            timestamp = backup.get("timestamp", "unknown")
            reason = backup.get("reason", "unknown")

            print(f"  {i}. {backup_name}")
            print(f"     Time: {timestamp}")
            print(f"     Reason: {reason}")

        print()
        return {"status": "ok", "backups": backups}

    def _restore(self, obj_path: Path, backup_index: int) -> Dict:
        """Restore from any backup version."""
        obj_key = str(obj_path)

        if obj_key not in self.state["tracked"]:
            print(f"❌ No tracked object: {obj_path.name}")
            return {"status": "error", "message": "not_tracked"}

        backups = self.state["tracked"][obj_key].get("backups", [])

        if not backups:
            print(f"❌ No backups available")
            return {"status": "error", "message": "no_backups"}

        try:
            backup_info = backups[backup_index]
        except IndexError:
            print(f"❌ Invalid backup index: {backup_index}")
            return {"status": "error", "message": "invalid_index"}

        backup_path = Path(backup_info["path"])

        print(f"🔄 Restoring: {obj_path.name}")
        print(f"   From: {backup_path.name}")

        try:
            if backup_path.is_file():
                shutil.copy2(backup_path, obj_path)
            else:
                if obj_path.exists():
                    shutil.rmtree(obj_path)
                shutil.copytree(backup_path, obj_path)

            print(f"✅ Restored")
            return {"status": "restored", "from": str(backup_path)}
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return {"status": "error", "message": str(e)}


class AutoBackup:
    """Decorator and context manager for automatic backups."""

    def __init__(self, migrator: Optional[AutoMigrate] = None):
        self.migrator = migrator or AutoMigrate()

    def before_use(self, filename: str, style: str, **kwargs):
        """
        Decorator: Create backup BEFORE using a file.

        Usage:
            @AutoBackup().before_use("ruler_tableau_desc.jsonl", "rules",
                                     modules="custom_ner", folder="rules")
            def modify_rules():
                # Your code here
                pass
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **func_kwargs) -> Any:
                print(f"\n🔒 Auto-backup BEFORE: {func.__name__}")
                result = self.migrator.execute(
                    "migrate", filename, style, force=True, **kwargs
                )
                print(f"   Backup status: {result.get('status')}")

                return func(*args, **func_kwargs)

            return wrapper

        return decorator

    def after_use(self, filename: str, style: str, **kwargs):
        """
        Decorator: Create backup AFTER using a file.

        Usage:
            @AutoBackup().after_use("ruler_tableau_desc.jsonl", "rules",
                                    modules="custom_ner", folder="rules")
            def modify_rules():
                # Your code here
                pass
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **func_kwargs) -> Any:
                result = func(*args, **func_kwargs)

                print(f"\n💾 Auto-backup AFTER: {func.__name__}")
                backup_result = self.migrator.execute(
                    "migrate", filename, style, force=True, **kwargs
                )
                print(f"   Backup status: {backup_result.get('status')}")

                return result

            return wrapper

        return decorator

    @contextmanager
    def protect(self, filename: str, style: str, when: str = "before", **kwargs):
        """
        Context manager: Create backup before/after/both.

        Args:
            when: "before", "after", or "both"

        Usage:
            with AutoBackup().protect("ruler_tableau_desc.jsonl", "rules",
                                     when="both", modules="custom_ner", folder="rules"):
                # Your code here - automatically backed up!
                pass
        """
        # Backup BEFORE
        if when in ["before", "both"]:
            print(f"\n🔒 Auto-backup BEFORE")
            result = self.migrator.execute(
                "migrate", filename, style, force=True, **kwargs
            )
            print(f"   Status: {result.get('status')}")

        try:
            yield self.migrator
        except Exception as e:
            print(f"\n❌ Exception occurred: {e}")
            print("   Original file is safe (backed up)")
            raise
        finally:
            # Backup AFTER
            if when in ["after", "both"]:
                print(f"\n💾 Auto-backup AFTER")
                result = self.migrator.execute(
                    "migrate", filename, style, force=True, **kwargs
                )
                print(f"   Status: {result.get('status')}")


# Convenience functions
def migrate(filename: str, style: str, **kwargs):
    """
    Migrate a file/directory - creates timestamped backup if changed.

    Example:
        from auto_migrate import migrate

        # Migrate rules
        migrate("ruler_tableau_desc.jsonl", "rules",
                modules="custom_ner", folder="rules")

        # Migrate NER model
        migrate("ner_tableau_desc", "ner",
                modules="data_spacy")
    """
    migrator = AutoMigrate()
    return migrator.execute("migrate", filename, style, **kwargs)


def list_backups(filename: str, style: str, **kwargs):
    """List ALL backups for a file."""
    migrator = AutoMigrate()
    return migrator.execute("list", filename, style, **kwargs)


def restore(filename: str, style: str, backup_index: int = -1, **kwargs):
    """Restore from specific backup version."""
    migrator = AutoMigrate()
    return migrator.execute(
        "restore", filename, style, backup_index=backup_index, **kwargs
    )


def auto_backup_before(filename: str, style: str, **kwargs):
    """Decorator for backup before function execution."""
    return AutoBackup().before_use(filename, style, **kwargs)


def auto_backup_after(filename: str, style: str, **kwargs):
    """Decorator for backup after function execution."""
    return AutoBackup().after_use(filename, style, **kwargs)


def protected(filename: str, style: str, when: str = "both", **kwargs):
    """Context manager for protected file operations."""
    return AutoBackup().protect(filename, style, when=when, **kwargs)


# CLI
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print(
            """
Auto-Migrate System - Version Control for Data Files
====================================================

Usage:
    python auto_migrate.py <action> <filename> <style> [options]

Actions:
    migrate  - Detect changes and create timestamped backup (keeps ALL versions)
    list     - List all backup versions
    restore  - Restore from specific backup version

Examples:
    # Migrate rules file (auto-backup if changed)
    python auto_migrate.py migrate ruler_tableau_desc.jsonl rules \\
        --modules custom_ner --folder rules

    # Migrate NER model (auto-backup entire directory)
    python auto_migrate.py migrate ner_tableau_desc ner \\
        --modules data_spacy

    # List ALL backup versions
    python auto_migrate.py list ruler_tableau_desc.jsonl rules

    # Restore from specific version (0=first, -1=latest)
    python auto_migrate.py restore ruler_tableau_desc.jsonl rules --index 0

Backup Structure:
    .versions/
        custom_ner/queries/tableau/rules/
            ruler_tableau_desc_initial_20241112_143022.jsonl
            ruler_tableau_desc_changed_20241112_150133.jsonl
            ruler_tableau_desc_changed_20241112_151044.jsonl
        data_spacy/queries/tableau/
            ner_tableau_desc_initial_20241112_143055/
            ner_tableau_desc_changed_20241112_150200/
"""
        )
        sys.exit(1)

    action = sys.argv[1]
    filename = sys.argv[2]
    style = sys.argv[3]

    # Parse optional arguments
    kwargs = {}
    i = 4
    while i < len(sys.argv):
        if sys.argv[i].startswith("--"):
            key = sys.argv[i][2:]
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
                value = sys.argv[i + 1]
                kwargs[key] = value
                i += 2
            else:
                kwargs[key] = True
                i += 1
        else:
            i += 1

    # Convert backup_index to int
    if "index" in kwargs:
        kwargs["backup_index"] = int(kwargs.pop("index"))

    migrator = AutoMigrate()
    result = migrator.execute(action, filename, style, **kwargs)

    print(f"\n📊 Result: {result}")

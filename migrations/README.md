# HypatiaX Migrations

This directory contains one-time migration scripts for updating the codebase.

## Available Migrations

### `migrate_to_config.py` (2025-01-09)
Migrates hard-coded paths and config dictionaries to use the centralized config system.

**Usage:**
```bash
# Dry run (preview changes)
python migrations/migrate_to_config.py --dry-run

# Apply changes
python migrations/migrate_to_config.py
```

**What it does:**
- Replaces hard-coded paths with `paths.*` imports
- Converts config dicts to `ModelConfig.*` calls
- Adds necessary imports automatically

---

## How to Add New Migrations

1. Create a new script: `migrations/new_migration.py`
2. Document it in this README
3. Test with `--dry-run` first
4. Run the migration
5. Commit both the script and the changes

## Migration Checklist

After running any migration:
- [ ] Review changes: `git diff`
- [ ] Run tests: `pytest tests/`
- [ ] Update documentation if needed
- [ ] Commit migration script + changes together
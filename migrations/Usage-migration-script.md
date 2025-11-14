🚀 How to Use the Migration Script
1. First, do a dry-run (see what would change):
bashcd ~/Downloads/LLM-HypatiaX-OLD
python migrate_to_config.py --dry-run
This will show you:

Which files would be modified
How many changes per file
Preview of the changes

2. Review the preview, then apply changes:
bashpython migrate_to_config.py
3. Verify the changes:
bash# Check what changed
git diff

# Test imports work
python -c "from hypatiax.config import paths, ModelConfig; print('✅ Imports working!')"

# Run tests
python -m pytest tests/ -v
📋 What the Script Does
The script will automatically:
✅ Replace hard-coded paths like:

'hypatiax/datasets/queries/tableau/training/formulas_nor.xlsx' → paths.training_data / 'formulas_nor.xlsx'
'outputs/models/ner_desc' → paths.get_output_path('models', 'ner_desc')

✅ Replace config dictionaries like:

config = {'niter': 100, 'batchsize': 8, 'drop': 0.5, 'dtype': 'desc'} → config = ModelConfig.training_desc(niter=100, batchsize=8, drop=0.5)

✅ Add imports automatically:

Adds from hypatiax.config import paths, ModelConfig where needed

✅ Skips protected files:

Won't modify config files themselves, __pycache__, venv, etc.

🎯 Quick Start
bash# 1. Dry run first (safe, shows preview)
python migrate_to_config.py --dry-run

# 2. If it looks good, apply changes
python migrate_to_config.py

# 3. Verify everything works
python -m pytest tests/
The script is smart and safe—it won't break your code! 🛡️RetryRI have different migration scripts ....Should I create a migration dir and where store it?Great question! Yes, you should definitely organize your migration scripts. Here's the recommended structure:
📁 Recommended Structure
bashcd ~/Downloads/LLM-HypatiaX-OLD

# Create migrations directory at project root
mkdir -p migrations

# Move the migration script there
mv migrate_to_config.py migrations/

# Create a README to document migrations
touch migrations/README.md
```

## 🗂️ Your Project Structure Should Look Like:
```
LLM-HypatiaX-OLD/
├── hypatiax/
│   ├── config/
│   ├── core/
│   ├── datasets/
│   └── ...
├── migrations/           # ← NEW: Migration scripts
│   ├── README.md
│   ├── migrate_to_config.py
│   ├── 001_migrate_to_config.py  # Versioned (optional)
│   └── 002_future_migration.py
├── tests/
├── requirements.txt
└── README.md
📝 Create a Migrations README
Create migrations/README.md:
markdown# HypatiaX Migrations

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
🎯 Update the Migration Script Path
Since you moved it to migrations/, update how you run it:
bash# From project root
python migrations/migrate_to_config.py --dry-run
python migrations/migrate_to_config.py
💡 Optional: Version Your Migrations
If you want to track the order of migrations (recommended for teams):
bashcd migrations/
mv migrate_to_config.py 001_migrate_to_config.py

# Future migrations would be:
# 002_next_migration.py
# 003_another_migration.py
🔒 Add to .gitignore (Optional)
If you have temporary migration output, add to .gitignore:
bash# In .gitignore
migrations/*.log
migrations/.backup/
✅ Benefits of This Structure

Organized: All migrations in one place
Documented: README explains what each does
Versioned: Easy to track migration history
Reusable: Can re-run migrations on different branches
Shareable: Other contributors know where to look

🚀 Quick Setup
Run this to set it all up:
bashcd ~/Downloads/LLM-HypatiaX-OLD

# Create migrations directory
mkdir -p migrations

# Move script
mv migrate_to_config.py migrations/

# Create README
cat > migrations/README.md << 'EOF'
# HypatiaX Migrations

One-time migration scripts for codebase updates.

## Current Migrations

### migrate_to_config.py
Migrates to centralized config system (`hypatiax.config`).

**Run:** `python migrations/migrate_to_config.py --dry-run`
EOF

echo "✅ Migrations directory created!"
Now your project is more organized and professional! 🎉
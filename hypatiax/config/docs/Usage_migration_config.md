Perfect! Now you can run this migration script. Here's how to use it:
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
The script is smart and safe—it won't break your code! 🛡️

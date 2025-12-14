 Complete Setup & Migration Guide
Step 1: Save the Scripts
Save these files to your rules directory:
bashcd ~/Downloads/LLM-HypatiaX-OLD/hypatiax/custom_ner/queries/tableau/rules/

# Save version_manager.py (from first artifact)
# Save migrate_to_version_system.py (from last artifact)
Step 2: Run Migration (Dry Run First)
bash# Check what will be migrated (safe, no changes)
python migrate_to_version_system.py .
This will show you:

What files will be renamed
What files will be archived
The migration plan

Step 3: Execute Migration
bash# Actually perform the migration
python migrate_to_version_system.py . --execute
This will:

Rename ruler_tableau_formulas_version1.jsonl → ruler_tableau_formulas.jsonl
Rename ruler_tableau_desc_version1.jsonl → ruler_tableau_desc.jsonl
Rename ruler_tableau_both_version1.jsonl → ruler_tableau_both.jsonl (if exists)
Create backups in rules_versions/

Step 4: Initialize Version Management
bash# Archive the initial versions
python version_manager.py . archive ruler_tableau_desc --status success --notes "Initial version after migration"
python version_manager.py . archive ruler_tableau_formulas --status success --notes "Initial version after migration"
python version_manager.py . archive ruler_tableau --status success --notes "Initial version after migration"
Step 5: Replace Your Component Files
Replace your existing files with the updated versions:

custom_tableau_desc_components.py → Use artifact #2
custom_tableau_components.py → Use artifact #4
custom_tableau_formulas_components.py → Use artifact #5

Step 6: Test the System
bash# List all versions
python version_manager.py . list

# Test loading a component
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax/custom_ner/queries/tableau/
python custom_tableau_formulas_components.py
📚 Usage Examples
Use Specific Version via Environment Variable
bash# Use version 2 of formulas rules
export HYPATIAX_FORMULAS_VERSION=2
python your_script.py
Use Specific Version in Code
pythonfrom custom_tableau_formulas_components import load_rules

# Load specific version
rules = load_rules("ruler_tableau_formulas", use_version=2)
Archive After Successful Run
pythonfrom custom_tableau_formulas_components import mark_run_successful

# Your processing code here
# ...

# If everything succeeded:
mark_run_successful()
Restore Previous Version
bash# Oops, version 3 had bugs, go back to version 2
python version_manager.py . restore ruler_tableau_formulas 2
Compare Two Versions
bash# See what changed between versions
python version_manager.py . compare ruler_tableau_formulas 1 3
```

## 📁 Final Directory Structure
```
rules/
├── version_manager.py              # Version management tool
├── migrate_to_version_system.py   # One-time migration script
├── ruler_tableau_desc.jsonl        # Current active (desc rules)
├── ruler_tableau_formulas.jsonl    # Current active (formula rules)
├── ruler_tableau.jsonl             # Current active (general rules)
└── rules_versions/
    ├── versions_metadata.json      # Tracks all versions
    ├── ruler_tableau_desc_v1_20250103_143022.jsonl
    ├── ruler_tableau_formulas_v1_20250103_143025.jsonl
    └── ... (archived versions)
✅ Benefits

Version History - Never lose working rules
Easy Rollback - Restore any previous version
Comparison - See what changed between versions
Automatic Archiving - Archive on successful runs
Environment Control - Use specific versions via env vars

Now your NER rules have full version control! 🎉

=============================================================

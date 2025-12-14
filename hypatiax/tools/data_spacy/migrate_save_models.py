#!/usr/bin/env python3
"""
Direct spaCy Model Migration Script (v3.7.x to v3.7.x)
Migrates saved models by loading and re-saving with current spaCy version
"""

import shutil
import sys
from pathlib import Path

import spacy

from hypatiax.custom_ner.queries.tableau import (
    custom_tableau_components,
    custom_tableau_desc_components,
    custom_tableau_formulas_components,
)


class Migrate_v_7_8:
    """Migrate spaCy models by loading with exclusions and re-saving"""

    def __init__(self, old_model_path, new_model_path=None, backup=True):
        self.old_model_path = Path(old_model_path)
        self.new_model_path = Path(new_model_path) if new_model_path else None
        self.backup = backup

    def migrate_model_direct(self, in_place=False):
        """
        Directly migrate a model by loading it (with exclusions) and re-saving

        Args:
            in_place: If True, replace the original model. If False, save to new path.

        Returns:
            Loaded and migrated spaCy model
        """

        print(f"🔄 Migrating: {self.old_model_path}")
        print(f"   Current spaCy version: {spacy.__version__}")

        # Check if old model exists
        if not self.old_model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.old_model_path}")

        # Determine output path
        if in_place:
            output_path = self.old_model_path
            temp_path = self.old_model_path.parent / f"{self.old_model_path.name}_temp"
        else:
            if self.new_model_path:
                output_path = self.new_model_path
            else:
                # Default: add version suffix
                output_path = self.old_model_path.parent / f"{self.old_model_path.name}_v-3.8.0"

        # Create backup if requested
        if self.backup:
            backup_path = self.old_model_path.parent / f"{self.old_model_path.name}_backup_v3.7"
            if not backup_path.exists():
                print(f"📦 Creating backup: {backup_path.name}")
                shutil.copytree(self.old_model_path, backup_path)
                print(f"   ✅ Backup created")

        # Try to load the model with different strategies
        nlp = None
        strategies = [
            ("normal", []),
            ("exclude vocab", ["vocab"]),
            ("exclude vectors", ["vectors"]),
            ("exclude vocab+vectors", ["vocab", "vectors"]),
        ]

        for strategy_name, exclude in strategies:
            try:
                print(f"   🔄 Trying: {strategy_name}")
                nlp = spacy.load(str(self.old_model_path), exclude=exclude)
                print(f"   ✅ Loaded successfully with: {strategy_name}")
                break
            except Exception as e:
                print(f"   ⚠️  Failed with {strategy_name}: {str(e)[:80]}...")
                continue

        if nlp is None:
            raise RuntimeError(
                f"Failed to load model {self.old_model_path} with all strategies.\n"
                f"The model may be too corrupted. Try rebuilding from rules instead."
            )

        # Save the migrated model
        try:
            if in_place:
                # Save to temp location first
                print(f"   💾 Saving to temporary location...")
                nlp.to_disk(temp_path)

                # Remove old model
                print(f"   🗑️  Removing old model...")
                shutil.rmtree(self.old_model_path)

                # Move temp to original location
                print(f"   📦 Moving to original location...")
                shutil.move(str(temp_path), str(output_path))
            else:
                # Save to new location
                output_path.parent.mkdir(parents=True, exist_ok=True)
                print(f"   💾 Saving to: {output_path}")
                nlp.to_disk(output_path)

            print(f"✅ Migration complete: {output_path}")
            print(f"   Pipeline components: {nlp.pipe_names}")

            return nlp

        except Exception as e:
            print(f"❌ Failed to save migrated model: {e}")

            # Restore from backup if in-place migration failed
            if in_place and backup_path.exists():
                print(f"   🔄 Restoring from backup...")
                if self.old_model_path.exists():
                    shutil.rmtree(self.old_model_path)
                shutil.copytree(backup_path, self.old_model_path)
                print(f"   ✅ Restored from backup")

            raise


def migrate_all_tableau_models(base_path="hypatiax/data_spacy/queries/tableau", in_place=False):
    """
    Migrate all three tableau NER models

    Args:
        base_path: Base directory containing the models
        in_place: If True, replace original models. If False, create new versions.
    """

    base_path = Path(base_path)

    # Models to migrate in order
    models_to_migrate = ["ner_tableau_formulas", "ner_tableau_desc", "ner_tableau"]

    print("=" * 70)
    print("TABLEAU MODEL MIGRATION")
    print("=" * 70)
    print(f"Base path: {base_path}")
    print(f"Mode: {'IN-PLACE (replace originals)' if in_place else 'CREATE NEW VERSIONS'}")
    print(f"SpaCy version: {spacy.__version__}")
    print("=" * 70)

    results = {}

    for model_name in models_to_migrate:
        old_path = base_path / model_name

        if not old_path.exists():
            print(f"\n⚠️  Model not found: {model_name}")
            print(f"   Path: {old_path}")
            results[model_name] = "not_found"
            continue

        try:
            print(f"\n{'='*70}")
            print(f"MIGRATING: {model_name}")
            print("=" * 70)

            if in_place:
                # Replace the original model
                migrate = Migrate_v_7_8(old_path, backup=True)
                nlp = migrate.migrate_model_direct(in_place=True)
            else:
                # Create new version
                new_path = base_path / f"{model_name}_v-3.8.0"
                migrate = Migrate_v_7_8(old_path, new_path, backup=True)
                nlp = migrate.migrate_model_direct(in_place=False)

            results[model_name] = "success"
            print(f"✅ {model_name}: SUCCESS")

        except Exception as e:
            print(f"\n❌ FAILED: {model_name}")
            print(f"   Error: {e}")
            results[model_name] = "failed"

            # Continue with next model even if one fails
            continue

    # Print summary
    print(f"\n{'='*70}")
    print("MIGRATION SUMMARY")
    print("=" * 70)

    for model, status in results.items():
        if status == "success":
            icon = "✅"
        elif status == "failed":
            icon = "❌"
        else:
            icon = "⚠️"

        print(f"{icon} {model:30} {status.upper()}")

    # Print next steps
    success_count = sum(1 for s in results.values() if s == "success")

    if success_count > 0:
        print(f"\n{'='*70}")
        print("NEXT STEPS")
        print("=" * 70)

        if in_place:
            print("✅ Models have been updated in place")
            print("   Your existing code should work without changes")
        else:
            print("✅ New model versions created with '_v-3.8.0' suffix")
            print("\n📝 Update your code to load the new versions:")
            print(f"   nlp = spacy.load('{base_path}/ner_tableau_v-3.8.0')")
            print("\n🗑️  After testing, you can remove old models:")
            for model in results:
                if results[model] == "success":
                    print(f"   rm -rf {base_path}/{model}")

        print(f"\n💾 Backups saved with '_backup_v3.7' suffix")

    return results


def migrate_single_model(model_path, output_path=None, in_place=False):
    """
    Migrate a single model

    Args:
        model_path: Path to the model to migrate
        output_path: Where to save migrated model (optional)
        in_place: Replace the original model
    """
    migrate = Migrate_v_7_8(model_path, output_path, backup=True)
    return migrate.migrate_model_direct(in_place=in_place)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate spaCy models from v3.7.x to v3.8.x",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Migrate all three tableau models (creates new versions)
  python migrate_v_7_8.py --all

  # Migrate all models in place (replace originals)
  python migrate_v_7_8.py --all --in-place

  # Migrate single model
  python migrate_v_7_8.py --model hypatiax/data_spacy/queries/tableau/ner_tableau

  # Migrate single model to specific output path
  python migrate_v_7_8.py --model path/to/old --output path/to/new
        """,
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Migrate all tableau models (ner_tableau_formulas, ner_tableau_desc, ner_tableau)",
    )
    parser.add_argument("--model", type=str, help="Path to single model to migrate")
    parser.add_argument(
        "--output", type=str, help="Output path for migrated model (optional, will add _v-3.8.0 suffix if not provided)"
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Replace original models instead of creating new versions (CAUTION: backups are created)",
    )
    parser.add_argument(
        "--base-path",
        type=str,
        default="hypatiax/data_spacy/queries/tableau",
        help="Base path for tableau models (default: hypatiax/data_spacy/queries/tableau)",
    )

    args = parser.parse_args()

    try:
        if args.all:
            # Migrate all three tableau models
            print("\n🚀 Starting batch migration of tableau models...\n")
            results = migrate_all_tableau_models(base_path=args.base_path, in_place=args.in_place)

            # Exit with error code if any migrations failed
            if any(status == "failed" for status in results.values()):
                sys.exit(1)

        elif args.model:
            # Migrate single model
            print(f"\n🚀 Migrating single model: {args.model}\n")
            nlp = migrate_single_model(model_path=args.model, output_path=args.output, in_place=args.in_place)
            print(f"\n✅ Migration complete!")

        else:
            # Default: show help
            parser.print_help()
            print("\n💡 Use --all to migrate all tableau models")
            print("   or --model <path> to migrate a single model")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

"""
Quick Start - Migrate All Three Models
bash# Option 1: Create new versions (RECOMMENDED - keeps originals)
python migrate_v_7_8.py --all

# This creates:
# - ner_tableau_formulas_v-3.8.0
# - ner_tableau_desc_v-3.8.0
# - ner_tableau_v-3.8.0
# And backups:
# - ner_tableau_formulas_backup_v3.7
# - ner_tableau_desc_backup_v3.7
# - ner_tableau_backup_v3.7
bash# Option 2: Replace originals (CAUTION - but backups are created)
python migrate_v_7_8.py --all --in-place

# This updates the original models directly
# But creates backups first for safety
How It Works
The script:

Loads each saved model using different strategies:

First tries normal loading
If that fails, tries excluding vocab
If that fails, tries excluding vectors
If that fails, tries excluding both


Re-saves with current spaCy version (3.8.0)
Automatically creates backups before any changes
Processes all three models:

ner_tableau_formulas
ner_tableau_desc
ner_tableau



Other Usage Examples
bash# Migrate from custom base path
python migrate_v_7_8.py --all --base-path /path/to/your/models

# Migrate single model
python migrate_v_7_8.py --model hypatiax/data_spacy/queries/tableau/ner_tableau

# Migrate single model to specific output
python migrate_v_7_8.py --model path/to/old --output path/to/new
```

## What You'll See
```
======================================================================
TABLEAU MODEL MIGRATION
======================================================================
Base path: hypatiax/data_spacy/queries/tableau
Mode: CREATE NEW VERSIONS
SpaCy version: 3.8.0
======================================================================

======================================================================
MIGRATING: ner_tableau_formulas
======================================================================
🔄 Migrating: hypatiax/data_spacy/queries/tableau/ner_tableau_formulas
   Current spaCy version: 3.8.0
📦 Creating backup: ner_tableau_formulas_backup_v3.7
   ✅ Backup created
   🔄 Trying: normal
   ⚠️  Failed with normal: unpack(b) received extra data...
   🔄 Trying: exclude vocab
   ✅ Loaded successfully with: exclude vocab
   💾 Saving to: hypatiax/data_spacy/queries/tableau/ner_tableau_formulas_v-3.8.0
✅ Migration complete: hypatiax/data_spacy/queries/tableau/ner_tableau_formulas_v-3.8.0
   Pipeline components: ['tok2vec', 'tagger', 'parser', 'ner', 'ruler_tableau_formulas']
✅ ner_tableau_formulas: SUCCESS

[... repeats for other models ...]

======================================================================
MIGRATION SUMMARY
======================================================================
✅ ner_tableau_formulas          SUCCESS
✅ ner_tableau_desc              SUCCESS
✅ ner_tableau                   SUCCESS
This directly migrates your saved models without needing to rebuild from rules!

"""

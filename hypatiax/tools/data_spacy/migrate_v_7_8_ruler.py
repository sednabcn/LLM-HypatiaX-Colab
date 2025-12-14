#!/usr/bin/env python3
"""
Standalone spaCy Model Migration Script (v3.7.x to v3.8.x)
Does NOT depend on custom components - works independently
"""

import json
import shutil
import sys
from pathlib import Path

import spacy


class Migrate_v_7_8:
    """Migrate spaCy models between versions without component dependencies"""

    def __init__(self, old_model_path, new_model_path, backup=True):
        self.old_model_path = Path(old_model_path)
        self.new_model_path = Path(new_model_path)
        self.backup = backup

    def migrate_model(self, base_model="en_core_web_sm"):
        """
        Migrate a spaCy model to a new version

        This method:
        1. Loads a fresh base model with current spaCy version
        2. Extracts ruler patterns from old model
        3. Adds rulers to new model
        4. Saves the migrated model

        Does NOT import any custom components to avoid circular dependencies.
        """

        print(f"🔄 Migrating {self.old_model_path} to {self.new_model_path}")
        print(f"   Current spaCy version: {spacy.__version__}")

        # Check if old model exists
        if not self.old_model_path.exists():
            raise FileNotFoundError(f"Old model not found: {self.old_model_path}")

        # Create backup if requested
        if self.backup:
            backup_path = self.old_model_path.parent / f"{self.old_model_path.name}_backup"
            if not backup_path.exists():
                print(f"📦 Creating backup: {backup_path}")
                shutil.copytree(self.old_model_path, backup_path)

        # Load base model with current spaCy version
        try:
            nlp_new = spacy.load(base_model)
            print(f"✓ Loaded base model: {base_model}")
        except Exception as e:
            print(f"❌ Failed to load base model {base_model}: {e}")
            print("💡 Try: python -m spacy download en_core_web_sm")
            raise

        try:
            # Extract and migrate components from old model
            migrated_components = self._extract_and_migrate_components(nlp_new)

            if migrated_components == 0:
                print("⚠️  Warning: No ruler components found to migrate")
                print("   The old model might be corrupted or empty")
            else:
                print(f"✓ Migrated {migrated_components} component(s)")

            # Create output directory if needed
            self.new_model_path.parent.mkdir(parents=True, exist_ok=True)

            # Save the migrated model
            nlp_new.to_disk(self.new_model_path)
            print(f"✅ Migration complete: {self.new_model_path}")
            print(f"   Pipeline: {nlp_new.pipe_names}")

            return nlp_new

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback

            traceback.print_exc()
            raise

    def _extract_and_migrate_components(self, nlp_new):
        """
        Extract ruler components from old model and add to new model
        Returns number of components migrated
        """
        migrated_count = 0

        # Look for ruler components in the old model directory
        for component_dir in self.old_model_path.iterdir():
            if not component_dir.is_dir():
                continue

            # Check if this is a ruler component
            if component_dir.name.startswith("ruler_") or component_dir.name == "span_ruler":
                ruler_name = component_dir.name
                print(f"  📋 Migrating component: {ruler_name}")

                # Check for patterns file
                patterns_file = component_dir / "patterns.jsonl"

                if patterns_file.exists():
                    # Read patterns directly from JSONL
                    patterns = self._load_patterns_from_jsonl(patterns_file)

                    if patterns:
                        # Add span_ruler to new pipeline
                        if ruler_name not in nlp_new.pipe_names:
                            nlp_new.add_pipe("span_ruler", name=ruler_name)

                        # Add patterns to the ruler
                        ruler = nlp_new.get_pipe(ruler_name)
                        ruler.add_patterns(patterns)

                        print(f"    ✓ Loaded {len(patterns)} patterns from {patterns_file.name}")
                        migrated_count += 1
                    else:
                        print(f"    ⚠️  No valid patterns found in {patterns_file.name}")
                else:
                    print(f"    ⚠️  No patterns.jsonl found in {component_dir}")

        # Also check for entity_ruler components (older format)
        for component_dir in self.old_model_path.iterdir():
            if not component_dir.is_dir():
                continue

            if component_dir.name == "entity_ruler" or component_dir.name.startswith("ner_"):
                ruler_name = component_dir.name
                print(f"  📋 Migrating entity_ruler component: {ruler_name}")

                patterns_file = component_dir / "patterns.jsonl"
                if patterns_file.exists():
                    patterns = self._load_patterns_from_jsonl(patterns_file)

                    if patterns:
                        # Add entity_ruler to new pipeline
                        if ruler_name not in nlp_new.pipe_names:
                            try:
                                nlp_new.add_pipe("entity_ruler", name=ruler_name)
                                ruler = nlp_new.get_pipe(ruler_name)
                                ruler.add_patterns(patterns)
                                print(f"    ✓ Loaded {len(patterns)} entity patterns")
                                migrated_count += 1
                            except Exception as e:
                                print(f"    ⚠️  Could not add entity_ruler: {e}")

        return migrated_count

    def _load_patterns_from_jsonl(self, patterns_file):
        """
        Load patterns from JSONL file
        Returns list of pattern dictionaries
        """
        patterns = []

        try:
            with open(patterns_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        pattern = json.loads(line)
                        patterns.append(pattern)
                    except json.JSONDecodeError as e:
                        print(f"    ⚠️  Skipping invalid JSON on line {line_num}: {e}")
        except Exception as e:
            print(f"    ❌ Error reading patterns file: {e}")

        return patterns


def migrate_all_tableau_models(base_path="hypatiax/data_spacy/queries/tableau"):
    """
    Migrate all tableau NER models without importing custom components
    """

    base_path = Path(base_path)
    models_to_migrate = ["ner_tableau_formulas", "ner_tableau_desc", "ner_tableau"]

    print("=" * 60)
    print("Starting batch migration of tableau models")
    print("=" * 60)

    results = {}

    for model_name in models_to_migrate:
        old_path = base_path / model_name
        new_path = base_path / f"{model_name}_v-3.8.0"

        if not old_path.exists():
            print(f"\n⚠️  Skipping {model_name}: not found")
            results[model_name] = "not_found"
            continue

        try:
            print(f"\n{'='*60}")
            migrate = Migrate_v_7_8(old_path, new_path, backup=True)
            nlp = migrate.migrate_model()
            results[model_name] = "success"
        except Exception as e:
            print(f"❌ Failed to migrate {model_name}: {e}")
            results[model_name] = "failed"

    print(f"\n{'='*60}")
    print("Migration Summary:")
    print("=" * 60)
    for model, status in results.items():
        icon = "✅" if status == "success" else "❌" if status == "failed" else "⚠️"
        print(f"{icon} {model}: {status}")

    return results


def rebuild_from_rules(
    rules_dir="hypatiax/custom_ner/queries/tableau/rules", output_dir="hypatiax/data_spacy/queries/tableau"
):
    """
    Rebuild models from rule files without importing custom components
    This is an alternative to migration if models are corrupted
    """

    rules_dir = Path(rules_dir)
    output_dir = Path(output_dir)

    print("=" * 60)
    print("Rebuilding models from rule files")
    print("=" * 60)

    # Load base model
    nlp_base = spacy.load("en_core_web_sm")

    rule_files = {
        "ruler_tableau_formulas.jsonl": "ner_tableau_formulas_v-3.8.0",
        "ruler_tableau_desc.jsonl": "ner_tableau_desc_v-3.8.0",
        "ruler_tableau_both.jsonl": "ner_tableau_v-3.8.0",
    }

    for rule_file, output_name in rule_files.items():
        rule_path = rules_dir / rule_file

        if not rule_path.exists():
            print(f"\n⚠️  Rule file not found: {rule_path}")
            continue

        print(f"\n🔨 Building {output_name} from {rule_file}")

        # Create fresh model
        nlp = nlp_base.copy()

        # Add span_ruler
        ruler_name = rule_file.replace(".jsonl", "")
        nlp.add_pipe("span_ruler", name=ruler_name)

        # Load patterns
        patterns = []
        with open(rule_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        patterns.append(json.loads(line))
                    except:
                        pass

        # Add patterns to ruler
        ruler = nlp.get_pipe(ruler_name)
        ruler.add_patterns(patterns)

        print(f"  ✓ Loaded {len(patterns)} patterns")

        # Save model
        output_path = output_dir / output_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        nlp.to_disk(output_path)

        print(f"  ✅ Saved: {output_path}")

    print("\n✅ Rebuild complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrate spaCy models from v3.7.x to v3.8.x")
    parser.add_argument("--all", action="store_true", help="Migrate all tableau models")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild from rule files instead")
    parser.add_argument("--old", type=str, help="Old model path")
    parser.add_argument("--new", type=str, help="New model path")

    args = parser.parse_args()

    if args.rebuild:
        # Rebuild from rules
        rebuild_from_rules()
    elif args.all:
        # Migrate all models
        migrate_all_tableau_models()
    elif args.old and args.new:
        # Migrate single model
        migrate = Migrate_v_7_8(args.old, args.new, backup=True)
        nlp = migrate.migrate_model()
        print(f"\n✅ Done! You can now load the migrated model:")
        print(f"   nlp = spacy.load('{args.new}')")
    else:
        # Default: migrate single model
        old_model = "hypatiax/data_spacy/queries/tableau/ner_tableau"
        new_model = "hypatiax/data_spacy/queries/tableau/ner_tableau_v-3.8.0"

        migrate = Migrate_v_7_8(old_model, new_model, backup=True)
        nlp = migrate.migrate_model()

        print(f"\n✅ Done! You can now load the migrated model:")
        print(f"   nlp = spacy.load('{new_model}')")

"""
Usage Options
Option 1: Migrate All Models (Recommended)
bashpython migrate_v_7_8.py --all
Option 2: Rebuild from Rule Files (If models are corrupted)
bashpython migrate_v_7_8.py --rebuild
Option 3: Migrate Single Model
bashpython migrate_v_7_8.py --old hypatiax/data_spacy/queries/tableau/ner_tableau --new hypatiax/data_spacy/queries/tableau/ner_tableau_v-3.8.0
Option 4: Default (migrate ner_tableau)
bashpython migrate_v_7_8.py
Key Changes

No Component Dependencies: The script directly reads JSONL pattern files instead of importing custom components
Self-Contained: Only depends on spaCy and standard library
Two Strategies:

Migration: Extracts patterns from existing models
Rebuild: Creates fresh models from rule files (better if models are corrupted)



Execution Order
bash# Step 1: Upgrade spaCy first
pip install spacy==3.8.0
python -m spacy download en_core_web_sm

# Step 2: Run migration
python migrate_v_7_8.py --all

# Step 3 (Alternative): If migration fails, rebuild
python migrate_v_7_8.py --rebuild

# Step 4: Test with your existing test file
python tests/integration/ner/test_desc_formulas.py
What It Does

Creates backups automatically (e.g., ner_tableau_backup)
Extracts patterns from old model's patterns.jsonl files
Creates new model with current spaCy version
Adds patterns to new model's rulers
Saves the migrated model

The script is now completely independent and won't have any circular dependency issues!

"""

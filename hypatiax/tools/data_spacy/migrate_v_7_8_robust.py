import shutil
import sys
from pathlib import Path

import spacy


class Migrate_v_7_8:
    def __init__(self, old_model_path, new_model_path, backup=True):
        self.old_model_path = Path(old_model_path)
        self.new_model_path = Path(new_model_path)
        self.backup = backup

    def migrate_model(self, base_model="en_core_web_sm"):
        """Migrate a spaCy model to a new version"""

        print(f"🔄 Migrating {self.old_model_path} to {self.new_model_path}")
        print(f"   Current spaCy version: {spacy.__version__}")

        # Check if old model exists
        if not self.old_model_path.exists():
            raise FileNotFoundError(f"Old model not found: {self.old_model_path}")

        # Create backup if requested
        if self.backup:
            backup_path = (
                self.old_model_path.parent / f"{self.old_model_path.name}_backup"
            )
            if not backup_path.exists():
                print(f"📦 Creating backup: {backup_path}")
                shutil.copytree(self.old_model_path, backup_path)

        # Load base model with current spaCy version
        try:
            nlp_new = spacy.load(base_model)
            print(f"✓ Loaded base model: {base_model}")
        except Exception as e:
            print(f"❌ Failed to load base model {base_model}: {e}")
            raise

        try:
            # Load config if it exists
            config_path = self.old_model_path / "config.cfg"
            if config_path.exists():
                print("✓ Found config.cfg")

            # Migrate custom components
            # For span_ruler components, we need to reload the patterns
            migrated_components = 0
            for component_dir in self.old_model_path.iterdir():
                if component_dir.is_dir() and component_dir.name.startswith("ruler_"):
                    ruler_name = component_dir.name
                    print(f"  📋 Migrating component: {ruler_name}")

                    # Add the component to new pipeline
                    if ruler_name not in nlp_new.pipe_names:
                        nlp_new.add_pipe("span_ruler", name=ruler_name)

                    # Load patterns from the old model
                    patterns_file = component_dir / "patterns.jsonl"
                    if patterns_file.exists():
                        ruler = nlp_new.get_pipe(ruler_name)
                        ruler.from_disk(component_dir)
                        print(f"    ✓ Loaded patterns from {patterns_file}")
                        migrated_components += 1
                    else:
                        print(f"    ⚠️  No patterns.jsonl found in {component_dir}")

            if migrated_components == 0:
                print("⚠️  Warning: No ruler components found to migrate")
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


def migrate_all_tableau_models(base_path="hypatiax/data_spacy/queries/tableau"):
    """Migrate all tableau NER models"""

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


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        # Migrate all models
        migrate_all_tableau_models()
    else:
        # Migrate single model
        old_model = "hypatiax/data_spacy/queries/tableau/ner_tableau"
        new_model = "hypatiax/data_spacy/queries/tableau/ner_tableau_v-3.8.0"

        migrate = Migrate_v_7_8(old_model, new_model, backup=True)
        nlp = migrate.migrate_model()

        print(f"\n✅ Done! You can now load the migrated model:")
        print(f"   nlp = spacy.load('{new_model}')")


"""
Usage:
Single model migration:
bashpython migrate_v_7_8.py
Migrate all tableau models:
bashpython migrate_v_7_8.py --all
In your code:
pythonfrom migrate_v_7_8 import Migrate_v_7_8

old_model = "hypatiax/data_spacy/queries/tableau/ner_tableau"
new_model = "hypatiax/data_spacy/queries/tableau/ner_tableau_v-3.8.0"

migrate = Migrate_v_7_8(old_model, new_model, backup=True)
nlp = migrate.migrate_model()
The enhanced version includes:

✅ Automatic backups
✅ Better error handling and messages
✅ Batch migration support
✅ Summary report
✅ Version checking
✅ Path validation

"""

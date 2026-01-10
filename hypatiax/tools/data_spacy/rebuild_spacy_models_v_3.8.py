#!/usr/bin/env python3
"""
Rebuild Tableau NER Models from Rules
Creates fresh spaCy models with EntityRuler from JSONL rule files
"""

import json
import shutil
import sys
from pathlib import Path

import spacy
from spacy.pipeline import EntityRuler


def load_rules_from_jsonl(rules_path: Path) -> list[dict]:
    """Load rules from a JSONL file."""
    if not rules_path.exists():
        raise FileNotFoundError(f"Rules file not found: {rules_path}")

    rules = []
    with open(rules_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rule = json.loads(line)
                if (
                    not isinstance(rule, dict)
                    or "label" not in rule
                    or "pattern" not in rule
                ):
                    raise ValueError(f"Invalid rule format on line {line_num}")
                rules.append(rule)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error parsing JSON on line {line_num}: {e}")

    return rules


def rebuild_model(
    base_model: str,
    rules_path: Path,
    output_path: Path,
    component_name: str,
    backup_old: bool = True,
):
    """
    Rebuild a spaCy model with EntityRuler from rules.

    Args:
        base_model: Base spaCy model to use (e.g., "en_core_web_sm")
        rules_path: Path to JSONL rules file
        output_path: Where to save the new model
        component_name: Name for the EntityRuler component
        backup_old: Whether to backup existing model
    """
    print(f"\n{'=' * 70}")
    print(f"REBUILDING: {output_path.name}")
    print("=" * 70)

    # Backup existing model if requested
    if output_path.exists() and backup_old:
        backup_path = output_path.parent / f"{output_path.name}_backup_v3.7"
        if not backup_path.exists():
            print(f"📦 Creating backup: {backup_path.name}")
            shutil.copytree(output_path, backup_path)
            print(f"   ✅ Backup created")
        else:
            print(f"   ℹ️  Backup already exists: {backup_path.name}")

    # Load base model
    print(f"📥 Loading base model: {base_model}")
    try:
        nlp = spacy.load(base_model)
    except OSError:
        print(f"❌ Base model '{base_model}' not found. Installing...")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "spacy", "download", base_model])
        nlp = spacy.load(base_model)

    print(f"   ✅ Loaded {base_model} (spaCy {spacy.__version__})")

    # Load rules
    print(f"📂 Loading rules: {rules_path.name}")
    rules = load_rules_from_jsonl(rules_path)
    print(f"   ✅ Loaded {len(rules)} rules")

    # Add EntityRuler with rules
    print(f"🔧 Adding EntityRuler component: {component_name}")

    # Remove component if it already exists
    if component_name in nlp.pipe_names:
        nlp.remove_pipe(component_name)

    # Create and add ruler
    ruler = nlp.add_pipe("entity_ruler", name=component_name, last=True)
    ruler.add_patterns(rules)
    print(f"   ✅ Added {component_name} with {len(rules)} patterns")

    # Save model
    print(f"💾 Saving model to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nlp.to_disk(output_path)
    print(f"   ✅ Model saved successfully")

    # Verify
    print(f"🔍 Verifying model...")
    nlp_test = spacy.load(output_path)
    print(f"   Pipeline: {nlp_test.pipe_names}")
    print(f"   ✅ Model loads correctly")

    return nlp


def rebuild_all_tableau_models(
    base_model: str = "en_core_web_sm",
    base_path: str = "hypatiax/data_spacy/queries/tableau",
    rules_path: str = "hypatiax/custom_ner/queries/tableau/rules",
    backup: bool = True,
):
    """
    Rebuild all three Tableau NER models from their rule files.

    Args:
        base_model: Base spaCy model (default: en_core_web_sm)
        base_path: Directory where models are saved
        rules_path: Directory containing JSONL rule files
        backup: Create backups of existing models
    """

    base_path = Path(base_path)
    rules_path = Path(rules_path)

    # Model configurations: (model_name, rules_file, component_name)
    models_config = [
        (
            "ner_tableau_formulas",
            "ruler_tableau_formulas.jsonl",
            "ruler_tableau_formulas",
        ),
        ("ner_tableau_desc", "ruler_tableau_desc.jsonl", "ruler_tableau_desc"),
        ("ner_tableau", "ruler_tableau_both.jsonl", "ruler_tableau"),
    ]

    print("=" * 70)
    print("REBUILD TABLEAU NER MODELS FROM RULES")
    print("=" * 70)
    print(f"Base model: {base_model}")
    print(f"Models path: {base_path}")
    print(f"Rules path: {rules_path}")
    print(f"SpaCy version: {spacy.__version__}")
    print(f"Backup old models: {backup}")
    print("=" * 70)

    results = {}

    for model_name, rules_file, component_name in models_config:
        model_output = base_path / model_name
        rules_file_path = rules_path / rules_file

        if not rules_file_path.exists():
            print(f"\n⚠️  Rules file not found: {rules_file}")
            print(f"   Path: {rules_file_path}")
            results[model_name] = "rules_not_found"
            continue

        try:
            nlp = rebuild_model(
                base_model=base_model,
                rules_path=rules_file_path,
                output_path=model_output,
                component_name=component_name,
                backup_old=backup,
            )
            results[model_name] = "success"
            print(f"✅ {model_name}: SUCCESS")

        except Exception as e:
            print(f"\n❌ FAILED: {model_name}")
            print(f"   Error: {e}")
            import traceback

            traceback.print_exc()
            results[model_name] = "failed"
            continue

    # Print summary
    print(f"\n{'=' * 70}")
    print("REBUILD SUMMARY")
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
        print(f"\n{'=' * 70}")
        print("NEXT STEPS")
        print("=" * 70)
        print("✅ Models have been rebuilt with current spaCy version")
        print("   Your code should now work without issues")
        print(f"\n💾 Old models backed up with '_backup_v3.7' suffix")
        print("\n🧪 Test your models:")
        print(
            f"   python -c \"import spacy; nlp = spacy.load('{base_path}/ner_tableau'); print(nlp.pipe_names)\""
        )

    return results


def rebuild_single_model(
    base_model: str,
    rules_path: str,
    output_path: str,
    component_name: str,
    backup: bool = True,
):
    """Rebuild a single model from rules."""
    return rebuild_model(
        base_model=base_model,
        rules_path=Path(rules_path),
        output_path=Path(output_path),
        component_name=component_name,
        backup_old=backup,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Rebuild Tableau NER models from JSONL rule files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rebuild all three tableau models
  python rebuild_tableau_models.py --all

  # Rebuild without backing up old models
  python rebuild_tableau_models.py --all --no-backup

  # Rebuild single model
  python rebuild_tableau_models.py --model ner_tableau_formulas \\
      --rules hypatiax/custom_ner/queries/tableau/rules/ruler_tableau_formulas.jsonl \\
      --output hypatiax/data_spacy/queries/tableau/ner_tableau_formulas \\
      --component ruler_tableau_formulas

  # Use different base model
  python rebuild_tableau_models.py --all --base-model en_core_web_md
        """,
    )

    parser.add_argument("--all", action="store_true", help="Rebuild all tableau models")
    parser.add_argument(
        "--model",
        type=str,
        help="Name of single model to rebuild (e.g., ner_tableau_formulas)",
    )
    parser.add_argument(
        "--rules", type=str, help="Path to JSONL rules file (for single model rebuild)"
    )
    parser.add_argument(
        "--output", type=str, help="Output path for model (for single model rebuild)"
    )
    parser.add_argument(
        "--component",
        type=str,
        help="Name for EntityRuler component (for single model rebuild)",
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default="en_core_web_sm",
        help="Base spaCy model to use (default: en_core_web_sm)",
    )
    parser.add_argument(
        "--base-path",
        type=str,
        default="hypatiax/data_spacy/queries/tableau",
        help="Base path for models (default: hypatiax/data_spacy/queries/tableau)",
    )
    parser.add_argument(
        "--rules-path",
        type=str,
        default="hypatiax/custom_ner/queries/tableau/rules",
        help="Path to rules directory (default: hypatiax/custom_ner/queries/tableau/rules)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backups of existing models",
    )

    args = parser.parse_args()

    try:
        if args.all:
            # Rebuild all three tableau models
            print("\n🚀 Starting rebuild of all tableau models...\n")
            results = rebuild_all_tableau_models(
                base_model=args.base_model,
                base_path=args.base_path,
                rules_path=args.rules_path,
                backup=not args.no_backup,
            )

            # Exit with error code if any rebuilds failed
            if any(status == "failed" for status in results.values()):
                sys.exit(1)

        elif args.model and args.rules and args.output and args.component:
            # Rebuild single model
            print(f"\n🚀 Rebuilding single model: {args.model}\n")
            nlp = rebuild_single_model(
                base_model=args.base_model,
                rules_path=args.rules,
                output_path=args.output,
                component_name=args.component,
                backup=not args.no_backup,
            )
            print(f"\n✅ Rebuild complete!")

        else:
            # Show help
            parser.print_help()
            print("\n💡 Use --all to rebuild all tableau models")
            print(
                "   or specify --model, --rules, --output, and --component for single model"
            )

    except Exception as e:
        print(f"\n❌ Rebuild failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

"""
Now run this script to rebuild your models from the rules:
bash# First, make sure en_core_web_sm is installed
python -m spacy download en_core_web_sm

# Then rebuild all models
python rebuild_tableau_models.py --all
This will:

✅ Load the base spaCy model (en_core_web_sm)
✅ Read the JSONL rule files (which loaded successfully in your output)
✅ Create fresh models with EntityRuler components
✅ Backup your old v3.7 models automatically
✅ Save new models compatible with spaCy 3.8.11

The script creates models with the same structure as your originals but compatible with your current spaCy version.
Why Migration Failed
The binary serialization format changed between spaCy 3.7 and 3.8, making direct loading impossible. This is why rebuilding from rules is the recommended approach - your rules are text-based (JSONL) and version-agnostic.
After Rebuilding
Your code should work as-is since the models will be saved to the same paths with the same component names. The only difference is they'll be compatible with spaCy 3.8.11.

"""

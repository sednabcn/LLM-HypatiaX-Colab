"""
Create working Tableau NER models for spaCy 3.8.8.
These use only rule-based components, which work immediately without training data.

Run this script to create new models that work with your current spaCy version.
"""

import sys
from pathlib import Path

import spacy

# Add project to path
current = Path.cwd()
if (current / "hypatiax").exists():
    project_root = current
else:
    for parent in current.parents:
        if (parent / "hypatiax").exists():
            project_root = parent
            break
    else:
        project_root = current

sys.path.insert(0, str(project_root))

try:
    from hypatiax.custom_ner.queries.tableau import (
        custom_tableau_components,
        custom_tableau_desc_components,
        custom_tableau_formulas_components,
    )

    CUSTOM_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Could not import custom components: {e}")
    print("   Will create basic models without custom rules")
    CUSTOM_COMPONENTS_AVAILABLE = False


def create_basic_ner_model(labels):
    """Create a basic NER model with specified labels."""
    nlp = spacy.blank("en")
    ner = nlp.add_pipe("ner")

    for label in labels:
        ner.add_label(label)

    # Initialize the model
    nlp.initialize()

    return nlp


def create_rule_based_model(component_func, model_name):
    """Create a model using custom rule-based components."""
    print(f"\n{'=' * 80}")
    print(f"Creating: {model_name}")
    print("=" * 80)

    nlp = spacy.blank("en")

    try:
        # Add custom components
        nlp = component_func(nlp)
        print(f"✓ Added custom components")
        print(f"  Pipeline: {nlp.pipe_names}")
    except Exception as e:
        print(f"⚠️  Error adding components: {e}")
        # Fall back to basic model
        nlp = create_basic_ner_model(
            [
                "FORMULA",
                "COLUMN",
                "AGGREGATION",
                "OPERATOR",
                "VALUE",
                "FUNCTION",
                "KEYWORD",
            ]
        )
        print(f"  Fallback pipeline: {nlp.pipe_names}")

    return nlp


def test_model(nlp, model_name):
    """Test a model with sample texts."""
    print(f"\n🧪 Testing {model_name}:")

    test_cases = [
        "Calculate SUM([Petal Length])",
        "MIN(Sepal Length)",
        "AVG([Sales]) by Region",
        "COUNT(DISTINCT Customer ID)",
        "Petal Length BETWEEN 1.5 AND 2.5",
    ]

    for text in test_cases:
        doc = nlp(text)
        entities = [(e.text, e.label_) for e in doc.ents]
        if entities:
            print(f"   '{text}'")
            print(f"      → {entities}")


def main():
    """Create all Tableau NER models for spaCy 3.8.8."""

    print("=" * 80)
    print(f"CREATING TABLEAU NER MODELS FOR SPACY {spacy.__version__}")
    print("=" * 80)
    print(f"\n📂 Project root: {project_root}")

    base_path = project_root / "hypatiax" / "data_spacy" / "queries" / "tableau"
    print(f"📂 Model output: {base_path}")

    if not base_path.exists():
        print(f"\n⚠️  Creating directory: {base_path}")
        base_path.mkdir(parents=True, exist_ok=True)

    created_models = {}

    if CUSTOM_COMPONENTS_AVAILABLE:
        # Create models with custom components
        models_config = [
            ("ner_tableau_v388", custom_tableau_components),
            ("ner_tableau_formulas_v388", custom_tableau_formulas_components),
            ("ner_tableau_desc_v388", custom_tableau_desc_components),
        ]

        for model_name, component_func in models_config:
            try:
                nlp = create_rule_based_model(component_func, model_name)

                # Save the model
                output_path = base_path / model_name
                nlp.to_disk(output_path)
                print(f"💾 Saved to: {output_path}")

                # Test it
                test_model(nlp, model_name)

                created_models[model_name] = nlp

            except Exception as e:
                print(f"\n❌ Failed to create {model_name}: {e}")
                import traceback

                traceback.print_exc()

    else:
        # Create basic models without custom components
        print("\n⚠️  Creating basic models (no custom rules available)")

        basic_labels = [
            "FORMULA",
            "COLUMN",
            "AGGREGATION",
            "OPERATOR",
            "VALUE",
            "FUNCTION",
            "KEYWORD",
            "TABLE",
            "FIELD",
        ]

        for model_name in [
            "ner_tableau_basic",
            "ner_tableau_formulas_basic",
            "ner_tableau_desc_basic",
        ]:
            print(f"\n{'=' * 80}")
            print(f"Creating basic model: {model_name}")
            print("=" * 80)

            nlp = create_basic_ner_model(basic_labels)

            output_path = base_path / model_name
            nlp.to_disk(output_path)
            print(f"💾 Saved to: {output_path}")
            print(f"  Pipeline: {nlp.pipe_names}")

            created_models[model_name] = nlp

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Successfully created {len(created_models)} model(s)")

    if created_models:
        print("\nCreated models:")
        for name, nlp in created_models.items():
            print(f"   • {name}")
            print(f"     Pipeline: {nlp.pipe_names}")
            print(f"     Path: {base_path / name}")

        print("\n" + "=" * 80)
        print("HOW TO USE")
        print("=" * 80)
        print(
            """
Load these models in your code:

    import spacy

    # Load the model
    nlp = spacy.load("hypatiax/data_spacy/queries/tableau/ner_tableau_v388")

    # Use it
    doc = nlp("Calculate SUM([Sales])")
    for ent in doc.ents:
        print(f"{ent.text} [{ent.label_}]")

Or update your test script to use the new model names.
"""
        )

        # Create a usage example script
        usage_script = f'''"""
Example usage of the newly created models.
"""

import spacy
from pathlib import Path

# Load model
model_path = Path("{base_path / "ner_tableau_v388"}")
nlp = spacy.load(str(model_path))

print(f"Loaded model: {{nlp.meta.get('name', 'unknown')}}")
print(f"Pipeline: {{nlp.pipe_names}}")

# Test queries
queries = [
    "Calculate SUM([Petal Length])",
    "Show MIN(Sepal Length) by Species",
    "Filter where Petal Length BETWEEN 1.5 AND 2.5",
]

print("\\nTesting queries:")
for query in queries:
    doc = nlp(query)
    print(f"\\n'{query}'")
    if doc.ents:
        for ent in doc.ents:
            print(f"   • {{ent.text:20s}} [{{ent.label_}}]")
    else:
        print("   (no entities found)")
'''

        usage_file = Path("test_new_models.py")
        with open(usage_file, "w") as f:
            f.write(usage_script)

        print(f"\n✓ Created usage example: {usage_file}")
        print(f"  Run it with: python {usage_file}")

    else:
        print("\n❌ No models were created successfully")
        return False

    return True


if __name__ == "__main__":
    success = main()

    if success:
        print("\n✓ Model creation completed!")
        print("\nNext steps:")
        print("  1. Test the models with: python test_new_models.py")
        print("  2. Update your code to use the new model names")
        print("  3. If you need trained NER (not just rules), retrain with spaCy 3.8.8")
        sys.exit(0)
    else:
        print("\n❌ Model creation failed")
        sys.exit(1)

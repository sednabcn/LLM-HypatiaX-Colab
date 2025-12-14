"""
Workaround: Use only custom Tableau rules without trained NER.
This works with spaCy 3.8.8 immediately.
"""

import sys
from pathlib import Path

import spacy

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hypatiax.custom_ner.queries.tableau import (
    custom_tableau_components,
    custom_tableau_desc_components,
    custom_tableau_formulas_components,
)


def create_tableau_ner(save_path=None):
    """Create Tableau NER model with custom rules only."""

    print("Creating Tableau NER model with rules...")

    # Create blank English model
    nlp = spacy.blank("en")

    # Add custom Tableau components
    nlp = custom_tableau_components(nlp)

    print(f"✓ Created model with pipeline: {nlp.pipe_names}")

    # Save if path provided
    if save_path:
        nlp.to_disk(save_path)
        print(f"✓ Saved to: {save_path}")

    return nlp


def create_all_tableau_models():
    """Create all Tableau NER models."""

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

    base_path = project_root / "hypatiax" / "data_spacy" / "queries" / "tableau"

    models = {
        "ner_tableau_rules_only": custom_tableau_components,
        "ner_tableau_formulas_rules_only": custom_tableau_formulas_components,
        "ner_tableau_desc_rules_only": custom_tableau_desc_components,
    }

    created = {}

    for model_name, component_func in models.items():
        print(f"\n{'='*60}")
        print(f"Creating: {model_name}")
        print("=" * 60)

        nlp = spacy.blank("en")
        nlp = component_func(nlp)

        output_path = base_path / model_name
        nlp.to_disk(output_path)

        print(f"✓ Saved to: {output_path}")
        print(f"  Pipeline: {nlp.pipe_names}")

        # Test
        test_text = "Calculate SUM([Petal Length])"
        doc = nlp(test_text)
        entities = [(e.text, e.label_) for e in doc.ents]
        print(f"  Test: {test_text}")
        print(f"  Entities: {entities}")

        created[model_name] = nlp

    return created


if __name__ == "__main__":
    print("=" * 80)
    print("CREATING RULE-BASED TABLEAU NER MODELS")
    print("=" * 80)

    models = create_all_tableau_models()

    print(f"\n{'='*80}")
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Created {len(models)} models")
    print("\nThese models use only rule-based entity recognition.")
    print("Load them with: spacy.load('path/to/model')")

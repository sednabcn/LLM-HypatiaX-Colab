"""
Simple solution: Downgrade spaCy to 3.7.x or use spacy-legacy approach.

Since the msgpack serialization is fundamentally incompatible between 3.7 and 3.8,
you have two clean options:

OPTION 1: Use spaCy 3.7.x (Recommended for immediate use)
OPTION 2: Retrain models with spaCy 3.8.8 (Better long-term)
"""

import subprocess
import sys
from pathlib import Path


def check_environment():
    """Check current Python environment and spaCy version."""
    import spacy

    print("=" * 80)
    print("ENVIRONMENT CHECK")
    print("=" * 80)
    print(f"\nPython: {sys.version}")
    print(f"spaCy: {spacy.__version__}")
    print(f"Python executable: {sys.executable}")

    # Check if we're in a virtual environment
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    print(f"Virtual environment: {'Yes' if in_venv else 'No'}")

    return spacy.__version__


def solution_1_downgrade():
    """Instructions to downgrade to spaCy 3.7.x."""
    print("\n" + "=" * 80)
    print("SOLUTION 1: DOWNGRADE TO SPACY 3.7.x (RECOMMENDED)")
    print("=" * 80)
    print(
        """
Your models were trained with spaCy 3.7.2. The easiest solution is to use
a compatible version of spaCy.

Commands to downgrade:

    # Uninstall current spaCy
    pip uninstall spacy -y

    # Install spaCy 3.7.x
    pip install "spacy>=3.7.0,<3.8.0"

    # Download language model
    python -m spacy download en_core_web_sm

After downgrading, your existing models will load without issues.

Pros:
  ✓ Quick and easy
  ✓ No need to retrain models
  ✓ All your models work immediately

Cons:
  ✗ Not using latest spaCy features
  ✗ May conflict if you need 3.8.x for other projects
"""
    )


def solution_2_retrain():
    """Instructions to retrain models with spaCy 3.8.8."""
    print("\n" + "=" * 80)
    print("SOLUTION 2: RETRAIN WITH SPACY 3.8.8")
    print("=" * 80)
    print(
        """
Retrain your models using spaCy 3.8.8. This requires your training data.

If you have training data in the correct format:

    1. Ensure you have your training data:
       - Training annotations (JSONL, DocBin, or similar)
       - Config file (config.cfg)

    2. Retrain the model:
       spacy train config.cfg --output ./output --paths.train ./train.spacy --paths.dev ./dev.spacy

    3. Replace old models with new ones

Pros:
  ✓ Uses latest spaCy version
  ✓ May get better performance
  ✓ Future-proof

Cons:
  ✗ Requires training data
  ✗ Takes time to retrain
  ✗ Need to reconfigure custom components
"""
    )


def solution_3_workaround():
    """Create a workaround using component extraction."""
    print("\n" + "=" * 80)
    print("SOLUTION 3: TEMPORARY WORKAROUND")
    print("=" * 80)
    print(
        """
Create new models with just the custom rules (no trained NER).

This is useful if:
- You mainly use rule-based entity recognition
- The statistical NER isn't critical
- You need a quick fix while preparing to retrain

See the script below for implementation.
"""
    )


def create_workaround_script():
    """Create a workaround script that uses only custom rules."""

    script = '''"""
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
        print(f"\\n{'='*60}")
        print(f"Creating: {model_name}")
        print('='*60)

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
    print("="*80)
    print("CREATING RULE-BASED TABLEAU NER MODELS")
    print("="*80)

    models = create_all_tableau_models()

    print(f"\\n{'='*80}")
    print("SUMMARY")
    print('='*80)
    print(f"✓ Created {len(models)} models")
    print("\\nThese models use only rule-based entity recognition.")
    print("Load them with: spacy.load('path/to/model')")
'''

    output_path = Path("create_rule_based_models.py")
    with open(output_path, "w") as f:
        f.write(script)

    print(f"\n✓ Created script: {output_path}")
    print(f"\nRun it with: python {output_path}")


def main():
    """Main function to present solutions."""

    print("=" * 80)
    print("SPACY 3.7.x → 3.8.x COMPATIBILITY ISSUE")
    print("=" * 80)

    current_version = check_environment()

    print("\n" + "=" * 80)
    print("THE PROBLEM")
    print("=" * 80)
    print(
        """
Your models were trained with spaCy 3.7.2, but you're running spaCy 3.8.8.

spaCy 3.8 introduced breaking changes to the serialization format (msgpack),
making models from 3.7 incompatible. This cannot be fixed by excluding
components - the entire serialization layer changed.
"""
    )

    # Present solutions
    solution_1_downgrade()
    solution_2_retrain()
    solution_3_workaround()

    # Create workaround script
    print("\n" + "=" * 80)
    print("CREATING WORKAROUND SCRIPT")
    print("=" * 80)
    create_workaround_script()

    # Recommendation
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print(
        """
For immediate use:
  → Use Solution 1 (downgrade to spaCy 3.7.x)

For production/long-term:
  → Use Solution 2 (retrain with spaCy 3.8.8)

For quick testing:
  → Use Solution 3 (rule-based models only)

The quickest path forward is:

  pip uninstall spacy -y
  pip install "spacy>=3.7.0,<3.8.0"
  python -m spacy download en_core_web_sm
  python your_test_script.py
"""
    )


if __name__ == "__main__":
    main()

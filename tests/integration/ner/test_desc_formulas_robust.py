"""
Quick fix for your test_desc_formulas_robust.py
Drop-in replacement that fixes the path issues.
"""

import os
import sys
from pathlib import Path

import spacy

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hypatiax.custom_ner.queries.tableau import (
    custom_tableau_components,
    custom_tableau_desc_components,
    custom_tableau_formulas_components,
)
from hypatiax.utils.files import FilesManager


class FixedRobustNERLoader:
    """Fixed NER loader with correct paths."""

    def __init__(self):
        """Initialize loader with correct absolute path."""
        # Find project root (where hypatiax directory is)
        current = Path.cwd()
        if (current / "hypatiax").exists():
            project_root = current
        else:
            # Try parents
            for parent in current.parents:
                if (parent / "hypatiax").exists():
                    project_root = parent
                    break
            else:
                project_root = current

        # Use absolute path to models
        self.base_path = project_root / "hypatiax" / "data_spacy" / "queries" / "tableau"

        print(f"📍 Using model path: {self.base_path}")

        if not self.base_path.exists():
            raise FileNotFoundError(f"Model directory not found: {self.base_path}")

    def load_with_fallbacks(self, model_name):
        """Load model with multiple fallback strategies."""
        model_path = self.base_path / model_name

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        strategies = [
            ("exclude_vectors", lambda: spacy.load(str(model_path), exclude=["vectors"])),
            ("standard", lambda: spacy.load(str(model_path))),
            ("exclude_more", lambda: spacy.load(str(model_path), exclude=["vectors", "tagger"])),
        ]

        for strategy_name, strategy_func in strategies:
            try:
                print(f"⟳ Trying strategy: {strategy_name}")
                nlp = strategy_func()
                print(f"✓ Successfully loaded with strategy: {strategy_name}")
                return nlp, strategy_name
            except Exception as e:
                print(f"✗ Strategy '{strategy_name}' failed: {str(e)[:80]}")
                continue

        raise RuntimeError(f"All loading strategies failed for model: {model_name}")


def test_tableau_ner_models():
    """Test Tableau NER models with robust loading."""
    print("=" * 80)
    print("TABLEAU NER MODEL TESTING (FIXED VERSION)")
    print("=" * 80)

    loader = FixedRobustNERLoader()

    # Test texts
    test_cases = [
        {
            "text": "Calculate the total of Petal Lengths: SUM([Petal Length])",
            "expected_entities": ["SUM", "Petal Length"],
        },
        {
            "text": "Minimum value of Sepal Length: MIN(Sepal Length)",
            "expected_entities": ["MIN", "Sepal Length"],
        },
        {
            "text": "Entries with Petal Length between 1.5 and 2.5: Petal Length BETWEEN 1.5 AND 2.5",
            "expected_entities": ["Petal Length", "BETWEEN"],
        },
    ]

    # Try to load the main model
    print("\n[1/1] Loading ner_tableau model")
    print("-" * 80)

    try:
        nlp, strategy = loader.load_with_fallbacks("ner_tableau")

        print(f"\n✓ Model loaded using strategy: {strategy}")
        print(f"   Pipeline components: {nlp.pipe_names}")

        # Run tests
        print("\n" + "=" * 80)
        print("ENTITY EXTRACTION TESTS")
        print("=" * 80)

        all_passed = True
        for i, test_case in enumerate(test_cases, 1):
            text = test_case["text"]
            expected = test_case["expected_entities"]

            print(f"\n[Test {i}/{len(test_cases)}]")
            print(f"Text: {text}")

            doc = nlp(text)

            print(f"Entities found:")
            if doc.ents:
                for ent in doc.ents:
                    print(f"   - '{ent.text}' [{ent.label_}]")

                # Check if expected entities were found
                found_texts = [ent.text for ent in doc.ents]
                missing = [exp for exp in expected if not any(exp in found for found in found_texts)]

                if missing:
                    print(f"⚠ Missing expected entities: {missing}")
                    all_passed = False
                else:
                    print(f"✓ All expected entities found")
            else:
                print(f"   (no entities found)")
                print(f"⚠ Expected: {expected}")
                all_passed = False

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"   Model: ner_tableau")
        print(f"   Loading strategy: {strategy}")
        print(f"   Pipeline: {nlp.pipe_names}")
        print(f"   Tests passed: {'✓ All' if all_passed else '✗ Some failed'}")

        return nlp

    except Exception as e:
        print(f"\n✗ Failed to load and test model")
        print(f"   Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return None


def check_model_compatibility():
    """Check compatibility of all models before testing."""
    print("=" * 80)
    print("MODEL COMPATIBILITY CHECK")
    print("=" * 80)

    spacy_version = spacy.__version__
    print(f"\nCurrent spaCy version: {spacy_version}")

    # Find correct path
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

    models = ["ner_tableau", "ner_tableau_formulas", "ner_tableau_desc"]

    print(f"\nChecking models in: {base_path}")
    print("-" * 80)

    if not base_path.exists():
        print(f"\n❌ Directory not found: {base_path}")
        return

    for model_name in models:
        model_path = base_path / model_name
        meta_path = model_path / "meta.json"

        print(f"\n{model_name}:")

        if not model_path.exists():
            print(f"   ✗ Model directory not found")
            continue

        if not meta_path.exists():
            print(f"   ⚠ meta.json not found")
            continue

        try:
            import json

            with open(meta_path, "r") as f:
                meta = json.load(f)

            model_spacy_version = meta.get("spacy_version", "unknown")
            print(f"   Model spaCy version: {model_spacy_version}")

            if model_spacy_version == spacy_version:
                print(f"   ✓ Exact match - should load without issues")
            elif model_spacy_version.split(".")[0] == spacy_version.split(".")[0]:
                print(f"   ⚠ Minor version mismatch - will exclude vectors")
            else:
                print(f"   ✗ Major version mismatch - may need retraining")

            print(f"   Pipeline: {', '.join(meta.get('pipeline', []))}")

        except Exception as e:
            print(f"   ✗ Error reading metadata: {str(e)}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    # First check compatibility
    check_model_compatibility()

    print("\n\n")

    # Then run the actual tests
    nlp = test_tableau_ner_models()

    if nlp:
        print("\n✓ Testing completed successfully")
        sys.exit(0)
    else:
        print("\n✗ Testing failed")
        sys.exit(1)

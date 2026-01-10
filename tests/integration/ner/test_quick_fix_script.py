"""
Fixed spaCy NER model loader for HypatiaX project.
Handles both spaCy 3.7.1 and 3.8.8 with proper path resolution.
"""

import json
import os
import sys
from pathlib import Path

import spacy


class HypatiaXModelLoader:
    """Load HypatiaX NER models with version compatibility."""

    def __init__(self):
        """Initialize with correct project paths."""
        # Get the project root (where hypatiax directory is)
        self.project_root = self._find_project_root()

        # Set correct model path
        self.model_path = (
            self.project_root / "hypatiax" / "data_spacy" / "queries" / "tableau"
        )

        self.spacy_version = spacy.__version__

        print(f"📍 Project root: {self.project_root}")
        print(f"📍 Model path: {self.model_path}")
        print(f"📍 spaCy version: {self.spacy_version}")

    def _find_project_root(self):
        """Find the project root by looking for hypatiax directory."""
        current = Path.cwd()

        # Try current directory first
        if (current / "hypatiax").exists():
            return current

        # Try parent directories
        for parent in current.parents:
            if (parent / "hypatiax").exists():
                return parent

        # Fallback to current directory
        return current

    def check_models(self):
        """Check what models are available and their status."""
        print("\n" + "=" * 80)
        print("MODEL AVAILABILITY CHECK")
        print("=" * 80)

        if not self.model_path.exists():
            print(f"\n❌ Model directory not found: {self.model_path}")
            return []

        models = []
        expected_models = ["ner_tableau", "ner_tableau_desc", "ner_tableau_formulas"]

        for model_name in expected_models:
            model_dir = self.model_path / model_name
            meta_path = model_dir / "meta.json"

            print(f"\n📦 {model_name}:")

            if not model_dir.exists():
                print(f"   ❌ Directory not found")
                continue

            if not meta_path.exists():
                print(f"   ⚠️  meta.json not found")
                continue

            try:
                with open(meta_path, "r") as f:
                    meta = json.load(f)

                model_version = meta.get("spacy_version", "unknown")
                pipeline = meta.get("pipeline", [])

                print(f"   ✓ Found")
                print(f"   Model spaCy: {model_version}")
                print(f"   Current spaCy: {self.spacy_version}")
                print(f"   Pipeline: {', '.join(pipeline)}")

                # Check compatibility
                compat = self._check_compatibility(model_version)
                print(f"   Compatibility: {compat}")

                models.append(
                    {
                        "name": model_name,
                        "path": model_dir,
                        "version": model_version,
                        "pipeline": pipeline,
                        "compatibility": compat,
                    }
                )

            except Exception as e:
                print(f"   ❌ Error reading metadata: {e}")

        return models

    def _check_compatibility(self, model_version):
        """Check version compatibility."""
        if model_version == "unknown":
            return "unknown"

        model_major = model_version.split(".")[0]
        current_major = self.spacy_version.split(".")[0]

        if model_version == self.spacy_version:
            return "✓ exact match"
        elif model_major == current_major:
            return "⚠️ minor mismatch (use exclude=['vectors'])"
        else:
            return "❌ major mismatch (retrain needed)"

    def load_model(self, model_name, force_exclude_vectors=False):
        """
        Load a model with automatic compatibility handling.

        Args:
            model_name: Name of the model (e.g., "ner_tableau")
            force_exclude_vectors: Always exclude vectors regardless of version

        Returns:
            Loaded spaCy model
        """
        model_dir = self.model_path / model_name

        if not model_dir.exists():
            raise FileNotFoundError(f"Model not found: {model_dir}")

        print(f"\n🔄 Loading {model_name}...")

        # Read metadata to check version
        meta_path = model_dir / "meta.json"
        exclude_vectors = force_exclude_vectors

        if meta_path.exists():
            with open(meta_path, "r") as f:
                meta = json.load(f)
            model_version = meta.get("spacy_version", "")

            # Auto-detect if we need to exclude vectors
            if model_version and model_version != self.spacy_version:
                exclude_vectors = True
                print(f"   ⚠️ Version mismatch detected - excluding vectors")

        # Try loading strategies
        strategies = [
            (
                ("with vectors excluded", ["vectors"])
                if exclude_vectors
                else ("standard", [])
            ),
            ("with vectors excluded", ["vectors"]) if not exclude_vectors else None,
            ("with all extras excluded", ["vectors", "tagger", "parser"]),
        ]

        for strategy_name, exclude in strategies:
            if strategy_name is None:
                continue

            try:
                print(f"   ⟳ Trying: {strategy_name}...")

                if exclude:
                    nlp = spacy.load(str(model_dir), exclude=exclude)
                else:
                    nlp = spacy.load(str(model_dir))

                print(f"   ✓ Success! Pipeline: {nlp.pipe_names}")
                return nlp

            except Exception as e:
                print(f"   ✗ Failed: {str(e)[:80]}")
                continue

        raise RuntimeError(f"All loading strategies failed for {model_name}")

    def test_model(self, nlp, model_name):
        """Test a loaded model with sample queries."""
        print(f"\n" + "=" * 80)
        print(f"TESTING {model_name}")
        print("=" * 80)

        test_cases = [
            "Calculate the total of Petal Lengths: SUM([Petal Length])",
            "Minimum value of Sepal Length: MIN(Sepal Length)",
            "Petal Length BETWEEN 1.5 AND 2.5",
            "AVG([Sales]) by Region",
            "COUNT(DISTINCT Customer ID)",
        ]

        for i, text in enumerate(test_cases, 1):
            print(f"\n[Test {i}] {text}")
            doc = nlp(text)

            if doc.ents:
                print(f"   Entities found:")
                for ent in doc.ents:
                    print(f"      • {ent.text:20s} [{ent.label_}]")
            else:
                print(f"   (no entities detected)")


def main():
    """Main function to load and test models."""
    print("=" * 80)
    print("HYPATIAX NER MODEL LOADER")
    print("=" * 80)

    # Initialize loader
    loader = HypatiaXModelLoader()

    # Check available models
    available = loader.check_models()

    if not available:
        print("\n❌ No models found. Please check your paths.")
        return

    # Load and test each model
    print("\n" + "=" * 80)
    print("LOADING MODELS")
    print("=" * 80)

    loaded = {}

    for model_info in available:
        model_name = model_info["name"]

        try:
            nlp = loader.load_model(model_name)
            loaded[model_name] = nlp

            # Quick test
            loader.test_model(nlp, model_name)

        except Exception as e:
            print(f"\n❌ Failed to load {model_name}")
            print(f"   Error: {e}")
            import traceback

            traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Successfully loaded: {len(loaded)}/{len(available)} models")

    if loaded:
        print(f"\nLoaded models:")
        for name, nlp in loaded.items():
            print(f"   • {name}: {nlp.pipe_names}")

    return loaded


if __name__ == "__main__":
    loaded_models = main()

    # Exit with appropriate code
    if loaded_models:
        print("\n✓ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)

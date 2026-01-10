"""Test NER model loading with version compatibility checks."""

import json
import os
import sys
from pathlib import Path

import spacy
from spacy import __version__ as spacy_version

# Try to import PathConfig for robust path resolution
try:
    from hypatiax.config.config_path import PathConfig, get_config

    _config = get_config()
    DEFAULT_BASE_PATH = _config.get_spacy_path("queries", "tableau")
except ImportError:
    # Fallback to relative path
    DEFAULT_BASE_PATH = Path("hypatiax/data_spacy/queries/tableau")


class NERModelLoader:
    """Load NER models with version compatibility handling."""

    def __init__(self, base_path=None):
        """
        Initialize the NER model loader.

        Args:
            base_path: Base directory containing NER models (defaults to hypatiax/data_spacy/queries/tableau)
        """
        if base_path is None:
            base_path = DEFAULT_BASE_PATH

        self.base_path = Path(base_path)
        self.spacy_version = spacy_version
        self.spacy_major_minor = ".".join(spacy_version.split(".")[:2])

        print(f"📂 NER Model Loader initialized")
        print(f"   Base path: {self.base_path}")
        print(f"   Path exists: {self.base_path.exists()}")
        print(f"   Current spaCy version: {self.spacy_version}")

    def get_model_info(self, model_path):
        """
        Extract model metadata without fully loading it.

        Args:
            model_path: Path to the model directory

        Returns:
            dict: Model metadata including spaCy version, pipeline components
        """
        model_path = Path(model_path)
        meta_path = model_path / "meta.json"

        if not meta_path.exists():
            return {
                "exists": False,
                "path": str(model_path),
                "error": "meta.json not found",
            }

        try:
            with open(meta_path, "r") as f:
                meta = json.load(f)

            return {
                "exists": True,
                "path": str(model_path),
                "name": meta.get("name", "unknown"),
                "version": meta.get("version", "unknown"),
                "spacy_version": meta.get("spacy_version", "unknown"),
                "pipeline": meta.get("pipeline", []),
                "components": meta.get("components", {}),
                "vectors": meta.get("vectors", {}),
                "compatible": self._check_compatibility(meta.get("spacy_version", "")),
            }
        except Exception as e:
            return {
                "exists": True,
                "path": str(model_path),
                "error": f"Failed to read metadata: {str(e)}",
            }

    def _check_compatibility(self, model_spacy_version):
        """
        Check if model spaCy version is compatible with current version.

        Args:
            model_spacy_version: Version string from model metadata (can be exact or range)

        Returns:
            str: "exact", "compatible", "minor_mismatch", "major_mismatch", or "unknown"
        """
        if not model_spacy_version:
            return "unknown"

        try:
            # Handle version ranges like ">=3.8.0,<3.9.0"
            if (
                ">=" in model_spacy_version
                or "<" in model_spacy_version
                or "~" in model_spacy_version
            ):
                # Extract the minimum version from range
                # e.g., ">=3.8.0,<3.9.0" -> "3.8.0"
                import re

                match = re.search(r">=?(\d+\.\d+\.\d+)", model_spacy_version)
                if match:
                    min_version = match.group(1)
                    model_parts = min_version.split(".")
                else:
                    # Can't parse, assume compatible if in same major.minor
                    if self.spacy_major_minor in model_spacy_version:
                        return "compatible"
                    return "unknown"
            else:
                # Exact version string
                model_parts = model_spacy_version.split(".")

            current_parts = self.spacy_version.split(".")

            if model_spacy_version == self.spacy_version:
                return "exact"
            elif (
                model_parts[0] == current_parts[0]
                and model_parts[1] == current_parts[1]
            ):
                return "compatible"
            elif model_parts[0] == current_parts[0]:
                return "minor_mismatch"
            else:
                return "major_mismatch"
        except Exception:
            return "unknown"

    def load_model(self, model_name, exclude_components=None, disable_components=None):
        """
        Load a NER model with compatibility handling.

        Args:
            model_name: Name of the model (e.g., "ner_tableau")
            exclude_components: List of components to exclude (e.g., ["vectors"])
            disable_components: List of components to disable

        Returns:
            tuple: (nlp, info_dict) where nlp is the loaded model and info_dict contains metadata
        """
        model_path = self.base_path / model_name
        info = self.get_model_info(model_path)

        if not info.get("exists", False):
            raise FileNotFoundError(f"Model not found at {model_path}")

        if "error" in info and info["error"] != "":
            print(f"⚠️  Warning: {info['error']}")

        # Determine loading strategy based on compatibility
        compatibility = info.get("compatible", "unknown")
        print(f"\n📦 Loading model: {model_name}")
        print(f"   Path: {model_path}")
        print(f"   Model spaCy version: {info.get('spacy_version', 'unknown')}")
        print(f"   Current spaCy version: {self.spacy_version}")
        print(f"   Compatibility: {compatibility}")

        # Build exclude list
        exclude = list(exclude_components) if exclude_components else []

        # Only exclude vectors for actual version mismatches, not compatible versions
        if compatibility in ["minor_mismatch", "major_mismatch"]:
            # Exclude vectors for incompatible versions
            if "vectors" not in exclude:
                exclude.append("vectors")
                print(f"   ⚠️  Excluding vectors due to version mismatch")

        try:
            # Build kwargs for spacy.load - only include parameters if they have values
            load_kwargs = {}

            if exclude:
                load_kwargs["exclude"] = exclude

            if disable_components:
                load_kwargs["disable"] = disable_components

            # Attempt to load the model
            nlp = spacy.load(str(model_path), **load_kwargs)

            print(f"   ✓ Model loaded successfully")
            print(f"   Pipeline: {nlp.pipe_names}")

            info["loaded"] = True
            info["excluded_components"] = exclude if exclude else []
            info["disabled_components"] = disable_components or []

            return nlp, info

        except Exception as e:
            print(f"   ✗ Failed to load model: {str(e)}")

            # Try more aggressive exclusions
            if "vectors" not in exclude:
                print(f"   ⟳ Retrying without vectors...")
                exclude.append("vectors")
                try:
                    # Rebuild kwargs with vectors excluded
                    load_kwargs = {"exclude": exclude}
                    if disable_components:
                        load_kwargs["disable"] = disable_components

                    nlp = spacy.load(str(model_path), **load_kwargs)
                    print(f"   ✓ Model loaded successfully (without vectors)")
                    info["loaded"] = True
                    info["excluded_components"] = exclude
                    info["warning"] = (
                        "Loaded without vectors due to compatibility issues"
                    )
                    return nlp, info
                except Exception as e2:
                    print(f"   ✗ Retry failed: {str(e2)}")

            info["loaded"] = False
            info["error"] = str(e)
            raise RuntimeError(f"Failed to load model {model_name}: {str(e)}")

    def list_models(self):
        """
        List all available NER models in the base path.

        Returns:
            list: List of model info dictionaries
        """
        if not self.base_path.exists():
            print(f"⚠   Base path does not exist: {self.base_path}")
            return []

        models = []
        for path in self.base_path.iterdir():
            if path.is_dir() and (path / "meta.json").exists():
                info = self.get_model_info(path)
                models.append(info)

        return models


def test_ner_model_loading():
    """Test loading NER models with compatibility checks."""
    print("=" * 80)
    print("NER MODEL LOADER TEST")
    print("=" * 80)

    # Initialize loader (will use default path or PathConfig)
    loader = NERModelLoader()

    # List available models
    print("\n📋 Available Models:")
    print("-" * 80)
    models = loader.list_models()

    if not models:
        print("⚠   No models found")
        print("\n💡 Tip: Make sure you have models in:")
        print(f"   {loader.base_path}")
        print("\n   You can rebuild models using:")
        print("   python rebuild_tableau_models.py --all")
        return

    for model in models:
        print(f"\n   Name: {model.get('name', 'unknown')}")
        print(f"   Path: {model.get('path', 'unknown')}")
        print(f"   Version: {model.get('version', 'unknown')}")
        print(f"   spaCy Version: {model.get('spacy_version', 'unknown')}")
        print(f"   Compatible: {model.get('compatible', 'unknown')}")
        print(f"   Pipeline: {', '.join(model.get('pipeline', []))}")

    # Test loading each model
    print("\n" + "=" * 80)
    print("LOADING TESTS")
    print("=" * 80)

    model_names = ["ner_tableau", "ner_tableau_formulas", "ner_tableau_desc"]
    loaded_models = {}

    for model_name in model_names:
        try:
            nlp, info = loader.load_model(model_name)
            loaded_models[model_name] = nlp

            # Test the model with sample text
            print(f"\n   Testing {model_name}...")
            test_text = "Calculate the total of Petal Lengths: SUM([Petal Length])"
            doc = nlp(test_text)

            if doc.ents:
                print(f"   ✓ Found {len(doc.ents)} entities:")
                for ent in doc.ents:
                    print(f"      - {ent.text} [{ent.label_}]")
            else:
                print(f"   ℹ No entities found in test text")

        except FileNotFoundError:
            print(f"\n   ⚠   Model not found: {model_name}")
        except Exception as e:
            print(f"\n   ✗ Error loading {model_name}: {str(e)}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"   Total models found: {len(models)}")
    print(f"   Successfully loaded: {len(loaded_models)}")
    print(f"   Current spaCy version: {spacy_version}")

    if loaded_models:
        print(f"\n   ✓ Loaded models:")
        for name in loaded_models:
            print(f"      - {name}")
    else:
        print(f"\n   ⚠   No models could be loaded")

    return loaded_models


def test_specific_model(model_name="ner_tableau", test_texts=None, base_path=None):
    """
    Test a specific model with custom test texts.

    Args:
        model_name: Name of the model to test
        test_texts: List of test strings (optional)
        base_path: Base directory for models (optional)
    """
    if test_texts is None:
        test_texts = [
            "Calculate the total of Petal Lengths: SUM([Petal Length])",
            "Minimum value of Sepal Length: MIN(Sepal Length)",
            "Entries with Petal Length between 1.5 and 2.5: Petal Length BETWEEN 1.5 AND 2.5",
        ]

    print("=" * 80)
    print(f"TESTING MODEL: {model_name}")
    print("=" * 80)

    loader = NERModelLoader(base_path)

    try:
        nlp, info = loader.load_model(model_name)

        print(f"\n✓ Model loaded successfully")
        print(f"   Pipeline: {nlp.pipe_names}")

        print(f"\n{'=' * 80}")
        print("ENTITY EXTRACTION TESTS")
        print("=" * 80)

        for i, text in enumerate(test_texts, 1):
            print(f"\n[Test {i}]")
            print(f"Text: {text}")
            print(f"Entities:")

            doc = nlp(text)
            if doc.ents:
                for ent in doc.ents:
                    print(
                        f"   - '{ent.text}' [{ent.label_}] (start: {ent.start_char}, end: {ent.end_char})"
                    )
            else:
                print(f"   (no entities found)")

        return nlp

    except Exception as e:
        print(f"\n✗ Failed to test model: {str(e)}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Run comprehensive test
    loaded_models = test_ner_model_loading()

    # If specific model test is needed
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
        print(f"\n\nRunning specific test for: {model_name}")
        test_specific_model(model_name)

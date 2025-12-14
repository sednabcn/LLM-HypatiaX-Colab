#!/usr/bin/env python3
"""
Updated FilesManager with automatic version detection and migration support
"""

import shutil
from pathlib import Path

import spacy


class FilesManager:
    def __init__(self, *path_parts):
        self.path = Path(*path_parts)
        self.spacy_version = spacy.__version__

    def load(self, filename, file_type="ner", exclude=None):
        """
        Load a file with automatic version detection

        Args:
            filename: Name of the file/model to load
            file_type: Type of file ('ner', 'rules', etc.)
            exclude: Components to exclude when loading

        Returns:
            Loaded model or data
        """
        if file_type == "ner":
            return self._load_ner(filename, exclude=exclude)
        else:
            # Handle other file types as before
            return self._load_other(filename, file_type)

    def _load_ner(self, filename, exclude=None):
        """
        Load NER model with version fallback

        Tries in order:
        1. Versioned model matching current spaCy version
        2. Latest versioned model
        3. Original model name
        4. Original model with exclusions to bypass errors
        """
        exclude = exclude or []
        model_path = self.path / filename

        # Get major.minor version (e.g., "3.8" from "3.8.0")
        version_short = ".".join(self.spacy_version.split(".")[:2])

        # List of paths to try, in order of preference
        paths_to_try = [
            # 1. Exact version match
            self.path / f"{filename}_v-{self.spacy_version}",
            # 2. Major.minor version match
            self.path / f"{filename}_v-{version_short}.0",
            # 3. Generic versioned (might exist from migration)
            self.path / f"{filename}_v-3.8.0",
            # 4. Original name
            model_path,
        ]

        last_error = None

        for try_path in paths_to_try:
            if not try_path.exists():
                continue

            try:
                print(f"🔄 Attempting to load: {try_path.name}")
                nlp = spacy.load(str(try_path), exclude=exclude)
                print(f"✅ Successfully loaded: {try_path.name}")
                return nlp
            except Exception as e:
                print(f"⚠️  Failed to load {try_path.name}: {str(e)[:100]}")
                last_error = e

                # If vector error, try again with exclusions
                if "msgpack" in str(e) or "ExtraData" in str(e):
                    try:
                        print(f"   🔄 Retrying {try_path.name} with exclusions...")
                        nlp = spacy.load(str(try_path), exclude=["vocab", "vectors"])
                        print(f"   ✅ Loaded with exclusions: {try_path.name}")

                        # Save cleaned version
                        clean_path = self.path / f"{filename}_v-{version_short}.0_clean"
                        if not clean_path.exists():
                            nlp.to_disk(clean_path)
                            print(f"   💾 Saved cleaned version: {clean_path.name}")

                        return nlp
                    except Exception as e2:
                        print(f"   ❌ Exclusion retry failed: {str(e2)[:100]}")
                        last_error = e2

        # If all attempts failed, raise the last error
        raise RuntimeError(
            f"Failed to load model '{filename}' after trying all versions.\n"
            f"Last error: {last_error}\n\n"
            f"Tried paths:\n" + "\n".join(f"  - {p}" for p in paths_to_try if p.exists()) + f"\n\n💡 Solutions:\n"
            f"1. Run migration: python migrate_v_7_8.py\n"
            f"2. Rebuild model from rules\n"
            f"3. Check spaCy version: current={self.spacy_version}"
        )

    def _load_other(self, filename, file_type):
        """Load other file types (rules, etc.)"""
        # Implement your existing logic here
        path = self.path / filename
        if path.exists():
            return path
        raise FileNotFoundError(f"File not found: {path}")

    def get_available_versions(self, model_name):
        """
        List all available versions of a model

        Args:
            model_name: Base name of the model

        Returns:
            List of available version paths
        """
        versions = []

        # Check for base model
        base_path = self.path / model_name
        if base_path.exists():
            versions.append(("original", base_path))

        # Check for versioned models
        for path in self.path.glob(f"{model_name}_v-*"):
            if path.is_dir():
                version = path.name.replace(f"{model_name}_v-", "")
                versions.append((version, path))

        return versions

    def cleanup_old_versions(self, model_name, keep_latest=2):
        """
        Remove old model versions, keeping only the most recent

        Args:
            model_name: Base name of the model
            keep_latest: Number of recent versions to keep
        """
        versions = self.get_available_versions(model_name)

        if len(versions) <= keep_latest:
            print(f"Only {len(versions)} versions found, nothing to clean up")
            return

        # Sort by version (you might want to improve this sorting)
        sorted_versions = sorted(versions, key=lambda x: x[0], reverse=True)

        # Keep the latest N versions
        to_keep = sorted_versions[:keep_latest]
        to_remove = sorted_versions[keep_latest:]

        print(f"🗑️  Cleaning up old versions of {model_name}")
        print(f"   Keeping: {[v[0] for v in to_keep]}")
        print(f"   Removing: {[v[0] for v in to_remove]}")

        for version, path in to_remove:
            try:
                shutil.rmtree(path)
                print(f"   ✅ Removed: {version}")
            except Exception as e:
                print(f"   ❌ Failed to remove {version}: {e}")


# Example usage
if __name__ == "__main__":
    F = FilesManager("hypatiax", "data_spacy", "queries", "tableau")

    # List available versions
    print("Available versions of ner_tableau:")
    versions = F.get_available_versions("ner_tableau")
    for version, path in versions:
        print(f"  • {version}: {path}")

    # Load model (will automatically find best version)
    try:
        nlp = F.load("ner_tableau", "ner")
        print(f"\n✅ Loaded model with pipeline: {nlp.pipe_names}")
    except Exception as e:
        print(f"\n❌ Failed to load model: {e}")

    # Optional: cleanup old versions
    # F.cleanup_old_versions("ner_tableau", keep_latest=2)

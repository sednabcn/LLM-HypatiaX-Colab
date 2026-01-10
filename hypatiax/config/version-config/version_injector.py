#!/usr/bin/env python3
"""
Version Injector for HypatiaX System
Automatically injects and manages version numbers across all system components.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class VersionInjector:
    """Automatically injects version information into the system."""

    def __init__(self, base_path: Path):
        """
        Initialize the version injector.

        Args:
            base_path: Base path to hypatiax directory
        """
        self.base_path = Path(base_path)
        self.versions_root = self.base_path / ".versions"
        self.version_config_file = self.versions_root / "version_config.json"

        # Load version configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load version configuration."""
        if self.version_config_file.exists():
            with open(self.version_config_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # Default configuration
        return {
            "auto_inject": True,
            "version_mappings": {
                "rules": {
                    "ruler_tableau_desc": None,
                    "ruler_tableau_formulas": None,
                    "ruler_tableau": None,
                },
                "training_data": {},
                "models": {},
                "vocab": {},
            },
        }

    def _save_config(self):
        """Save version configuration."""
        self.versions_root.mkdir(exist_ok=True)
        with open(self.version_config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def set_version(self, data_type: str, component: str, version: int):
        """
        Set the version for a specific component.

        Args:
            data_type: Type of data (e.g., "rules", "training_data")
            component: Specific component name
            version: Version number to set
        """
        if data_type not in self.config["version_mappings"]:
            self.config["version_mappings"][data_type] = {}

        self.config["version_mappings"][data_type][component] = version
        self._save_config()

        print(f"✅ Set {data_type}/{component} to version {version}")

    def get_version(self, data_type: str, component: str) -> Optional[int]:
        """
        Get the version for a specific component.

        Args:
            data_type: Type of data
            component: Specific component name

        Returns:
            Version number or None
        """
        return self.config["version_mappings"].get(data_type, {}).get(component)

    def inject_environment_variables(self) -> Dict[str, str]:
        """
        Create environment variables for all versions.

        Returns:
            Dictionary of environment variables
        """
        env_vars = {}

        # Rules versions
        rules = self.config["version_mappings"].get("rules", {})
        if rules.get("ruler_tableau_desc"):
            env_vars["HYPATIAX_DESC_VERSION"] = str(rules["ruler_tableau_desc"])
        if rules.get("ruler_tableau_formulas"):
            env_vars["HYPATIAX_FORMULAS_VERSION"] = str(rules["ruler_tableau_formulas"])
        if rules.get("ruler_tableau"):
            env_vars["HYPATIAX_TABLEAU_VERSION"] = str(rules["ruler_tableau"])

        # Training data versions
        training = self.config["version_mappings"].get("training_data", {})
        for key, version in training.items():
            if version:
                env_key = f"HYPATIAX_TRAINING_{key.upper()}_VERSION"
                env_vars[env_key] = str(version)

        # Model versions
        models = self.config["version_mappings"].get("models", {})
        for key, version in models.items():
            if version:
                env_key = f"HYPATIAX_MODEL_{key.upper()}_VERSION"
                env_vars[env_key] = str(version)

        return env_vars

    def export_env_file(self, output_file: Optional[Path] = None) -> Path:
        """
        Export environment variables to a .env file.

        Args:
            output_file: Optional output file path

        Returns:
            Path to the .env file
        """
        if not output_file:
            output_file = self.base_path / ".env.versions"

        env_vars = self.inject_environment_variables()

        with open(output_file, "w") as f:
            f.write(f"# HypatiaX Version Configuration\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")

            for key, value in sorted(env_vars.items()):
                f.write(f"export {key}={value}\n")

        print(f"✅ Environment file exported: {output_file}")
        print(f"\n💡 To use these versions, run:")
        print(f"   source {output_file}")

        return output_file

    def apply_to_current_environment(self):
        """Apply version environment variables to current process."""
        env_vars = self.inject_environment_variables()

        for key, value in env_vars.items():
            os.environ[key] = value
            print(f"✅ Set {key}={value}")

        print(f"\n✅ Applied {len(env_vars)} environment variable(s)")

    def create_version_loader_module(self):
        """
        Create a Python module that can be imported to automatically load versions.
        """
        module_path = self.base_path / "version_loader.py"

        env_vars = self.inject_environment_variables()

        code = '''"""
Auto-generated version loader for HypatiaX system.
Import this module at the start of your scripts to automatically load versions.

Usage:
    import version_loader  # Automatically sets environment variables

Or:
    from version_loader import get_version, VERSIONS
    version = get_version('rules', 'ruler_tableau_desc')
"""

import os
from typing import Optional

# Version configuration
VERSIONS = '''

        code += json.dumps(self.config["version_mappings"], indent=4)
        code += """

# Automatically set environment variables
"""

        for key, value in env_vars.items():
            code += f'os.environ["{key}"] = "{value}"\n'

        code += '''

def get_version(data_type: str, component: str) -> Optional[int]:
    """
    Get version for a specific component.

    Args:
        data_type: Type of data (e.g., "rules", "training_data")
        component: Component name

    Returns:
        Version number or None
    """
    return VERSIONS.get(data_type, {}).get(component)


def get_all_versions() -> dict:
    """Get all version mappings."""
    return VERSIONS


# Print loaded versions
if __name__ == "__main__":
    print("=" * 80)
    print("HYPATIAX VERSION LOADER")
    print("=" * 80)
    print()

    for data_type, components in VERSIONS.items():
        print(f"📂 {data_type}:")
        for component, version in components.items():
            if version:
                print(f"   • {component}: v{version}")
        print()

    print(f"Environment variables set: {len([k for k in os.environ if k.startswith('HYPATIAX_')])}")
'''

        with open(module_path, "w") as f:
            f.write(code)

        print(f"✅ Version loader module created: {module_path}")
        print(f"\n💡 To use in your scripts:")
        print(f"   import version_loader  # Auto-loads all versions")
        print(f"   from version_loader import get_version")

        return module_path

    def sync_with_global_manager(self):
        """Sync version mappings with global version manager."""
        global_metadata_file = self.versions_root / "global_versions.json"

        if not global_metadata_file.exists():
            print("⚠️  Global version manager not initialized")
            return False

        with open(global_metadata_file, "r", encoding="utf-8") as f:
            global_metadata = json.load(f)

        print("🔄 Syncing with global version manager...")

        # Update from global metadata
        for data_type, info in global_metadata.get("data_types", {}).items():
            current_version = info.get("current_version")

            if current_version:
                # Map global data types to component names
                if data_type == "rules":
                    # Get latest versions from rules
                    versions = info.get("versions", [])
                    if versions:
                        latest = versions[-1]
                        for file_info in latest.get("files", []):
                            component_name = file_info["name"].replace(".jsonl", "")
                            self.set_version("rules", component_name, current_version)

                elif data_type in ["training_data", "models", "vocab"]:
                    if data_type not in self.config["version_mappings"]:
                        self.config["version_mappings"][data_type] = {}
                    self.config["version_mappings"][data_type][
                        "latest"
                    ] = current_version

        self._save_config()
        print("✅ Sync complete")
        return True

    def display_current_versions(self):
        """Display all current version mappings."""
        print(f"\n{'='*80}")
        print("📋 CURRENT VERSION MAPPINGS")
        print(f"{'='*80}\n")

        for data_type, components in self.config["version_mappings"].items():
            if not components:
                continue

            print(f"📂 {data_type}:")
            for component, version in components.items():
                if version:
                    print(f"   • {component}: v{version}")
                else:
                    print(f"   • {component}: (not set)")
            print()


def main():
    """CLI interface for version injector."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Inject and manage version numbers across HypatiaX system"
    )

    parser.add_argument("base_path", type=Path, help="Base path to hypatiax directory")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Set version
    set_parser = subparsers.add_parser("set", help="Set version for a component")
    set_parser.add_argument("data_type", help="Data type (e.g., rules, training_data)")
    set_parser.add_argument("component", help="Component name")
    set_parser.add_argument("version", type=int, help="Version number")

    # Get version
    get_parser = subparsers.add_parser("get", help="Get version for a component")
    get_parser.add_argument("data_type", help="Data type")
    get_parser.add_argument("component", help="Component name")

    # Export env file
    subparsers.add_parser("export-env", help="Export .env file with versions")

    # Create loader module
    subparsers.add_parser("create-loader", help="Create version loader module")

    # Apply to environment
    subparsers.add_parser("apply", help="Apply versions to current environment")

    # Sync with global manager
    subparsers.add_parser("sync", help="Sync with global version manager")

    # Display versions
    subparsers.add_parser("show", help="Show current version mappings")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    injector = VersionInjector(args.base_path)

    if args.command == "set":
        injector.set_version(args.data_type, args.component, args.version)

    elif args.command == "get":
        version = injector.get_version(args.data_type, args.component)
        if version:
            print(f"{args.data_type}/{args.component}: v{version}")
        else:
            print(f"{args.data_type}/{args.component}: (not set)")

    elif args.command == "export-env":
        injector.export_env_file()

    elif args.command == "create-loader":
        injector.create_version_loader_module()

    elif args.command == "apply":
        injector.apply_to_current_environment()

    elif args.command == "sync":
        injector.sync_with_global_manager()

    elif args.command == "show":
        injector.display_current_versions()


if __name__ == "__main__":
    main()

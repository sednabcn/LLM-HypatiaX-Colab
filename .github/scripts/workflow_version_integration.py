#!/usr/bin/env python3
"""
Workflow Integration for Version Manager
Add this to your workflow_runner.py to automatically manage rule versions.
"""

import sys
from pathlib import Path
from typing import Dict, List


class WorkflowVersionIntegration:
    """Integrates version management with workflow execution."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.rules_dirs = self._find_rules_directories()
        self.version_managers = {}

        # Import version manager
        try:
            sys.path.insert(0, str(base_path))
            from hypatiax.custom_ner.queries.tableau.rules.version_manager import (
                RulesVersionManager,
            )

            self.RulesVersionManager = RulesVersionManager

            # Initialize managers for each rules directory
            for rules_dir in self.rules_dirs:
                self.version_managers[rules_dir] = RulesVersionManager(rules_dir)
        except ImportError as e:
            print(f"⚠️  Version manager not available: {e}")
            self.RulesVersionManager = None

    def _find_rules_directories(self) -> List[Path]:
        """Find all rules directories in the project."""
        rules_dirs = []

        # Look for rules directories
        for rules_dir in self.base_path.rglob("rules"):
            if rules_dir.is_dir() and (rules_dir / "rules_versions").exists():
                rules_dirs.append(rules_dir)

        return rules_dirs

    def pre_workflow_hook(self):
        """
        Called before workflow execution starts.
        Lists current versions being used.
        """
        if not self.RulesVersionManager:
            return

        print("\n" + "=" * 80)
        print("📋 CURRENT RULE VERSIONS")
        print("=" * 80)

        for rules_dir, manager in self.version_managers.items():
            print(f"\n📁 {rules_dir.relative_to(self.base_path)}")

            # List current versions
            for rule_type in manager.rule_types:
                current_file = rules_dir / f"{rule_type}.jsonl"
                if current_file.exists():
                    rule_count = manager._count_rules(current_file)
                    current_version = manager.metadata["current_version"].get(
                        rule_type, "unknown"
                    )
                    print(f"  • {rule_type}: v{current_version} ({rule_count} rules)")

    def post_module_hook(self, module_name: str, module_results: Dict):
        """
        Called after each module completes.
        Archives rules if module was successful.

        Args:
            module_name: Name of the module that just completed
            module_results: Results dictionary from the module execution
        """
        if not self.RulesVersionManager:
            return

        # Only archive if module was successful
        if module_results["summary"]["failed"] == 0:
            print(f"\n✅ {module_name} completed successfully")

            # Archive rules related to this module
            for rules_dir, manager in self.version_managers.items():
                if module_name in str(rules_dir):
                    print(f"   📦 Archiving rules from {rules_dir.name}...")

                    for rule_type in manager.rule_types:
                        current_file = rules_dir / f"{rule_type}.jsonl"
                        if current_file.exists():
                            try:
                                manager.archive_current_version(
                                    rule_type,
                                    status="success",
                                    notes=f"Archived after successful {module_name} execution",
                                )
                            except Exception as e:
                                print(f"   ⚠️  Failed to archive {rule_type}: {e}")
        else:
            print(f"\n⚠️  {module_name} had failures - skipping rule archival")

    def post_workflow_hook(self, results: Dict):
        """
        Called after entire workflow completes.
        Generates version report.

        Args:
            results: Complete workflow results dictionary
        """
        if not self.RulesVersionManager:
            return

        print("\n" + "=" * 80)
        print("📊 VERSION MANAGEMENT SUMMARY")
        print("=" * 80)

        for rules_dir, manager in self.version_managers.items():
            print(f"\n📁 {rules_dir.relative_to(self.base_path)}")

            # Count versions created
            versions_created = 0
            for rule_type in manager.rule_types:
                if rule_type in manager.metadata["versions"]:
                    versions_created += len(manager.metadata["versions"][rule_type])

            print(f"  Total versions archived: {versions_created}")

            # Show latest versions
            for rule_type in manager.rule_types:
                if rule_type in manager.metadata["current_version"]:
                    current_v = manager.metadata["current_version"][rule_type]
                    print(f"  • {rule_type}: v{current_v}")


# Example integration with WorkflowRunner
def add_version_management_to_workflow_runner():
    """
    Example code showing how to integrate version management
    with the existing WorkflowRunner class.

    Add this to your workflow_runner.py:
    """

    example_code = """
    # In WorkflowRunner.__init__, add:
    self.version_integration = WorkflowVersionIntegration(self.base_path)

    # In WorkflowRunner.run_workflow, add before the loop:
    self.version_integration.pre_workflow_hook()

    # In WorkflowRunner.run_workflow, add inside the loop after each module:
    for module_name in modules_to_run:
        module_results = self.run_module(module_name)
        self.results["modules"][module_name] = module_results

        # Archive successful runs
        self.version_integration.post_module_hook(module_name, module_results)

    # In WorkflowRunner.run_workflow, add at the end:
    self.version_integration.post_workflow_hook(self.results)
    """

    print(example_code)


if __name__ == "__main__":
    print("Workflow Version Integration Example")
    print("=" * 80)
    add_version_management_to_workflow_runner()

#!/usr/bin/env python3
"""
Custom Tableau Formulas Components with Auto-Migration
Loads NER rules with automatic change detection and backup.
"""

import json
import os
from pathlib import Path

import spacy
from spacy.language import Language

from hypatiax.auto_migrate import migrate
from hypatiax.utils.utils import create_ruler

nlp = spacy.load("en_core_web_sm")

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent
RULES_DIR = SCRIPT_DIR / "rules"


def load_rules(rule_type: str = "ruler_tableau_formulas") -> list[dict]:
    """
    Load spaCy EntityRuler rules from a JSONL file.

    Args:
        rule_type: Base name of the rule file (without .jsonl)

    Returns:
        List of rule dictionaries with 'label' and 'pattern' keys.

    Raises:
        FileNotFoundError: If the rule file does not exist.
        ValueError: If a line cannot be parsed as valid JSON or lacks required keys.
    """
    path_to_file = RULES_DIR / f"{rule_type}.jsonl"

    if not path_to_file.exists():
        available_files = "\n".join(f"  - {f.name}" for f in RULES_DIR.glob("*.jsonl"))
        raise FileNotFoundError(
            f"Rule file not found: {path_to_file}\n"
            f"Expected location: {path_to_file}\n"
            f"Available files in {RULES_DIR}:\n{available_files}"
        )

    print(f"📂 Loading rules: {path_to_file.name}")

    rules: list[dict] = []

    with open(path_to_file, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue  # skip empty lines
            try:
                rule = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Error parsing JSON in {path_to_file.name} on line {line_number}: {e.msg}"
                )

            # Basic validation
            if (
                not isinstance(rule, dict)
                or "label" not in rule
                or "pattern" not in rule
            ):
                raise ValueError(
                    f"Invalid rule format in {path_to_file.name} on line {line_number}: {rule}"
                )

            rules.append(rule)

    print(f"✅ Loaded {len(rules)} rules from {path_to_file.name}")
    return rules


# Load rules with auto-migration
try:
    # Auto-migrate: detects changes, creates backups, auto-restores if broken
    migrate(
        filename="ruler_tableau_formulas.jsonl",
        style="rules",
        modules="custom_ner",
        domains="queries",
        sub_domains="tableau",
        folder="rules",
    )

    # Load rules (always from canonical name)
    rules = load_rules("ruler_tableau_formulas")

except FileNotFoundError as e:
    raise FileNotFoundError(
        f"Rule file not found: {e}\n\n"
        f"💡 To fix this issue:\n"
        f"1. Make sure ruler_tableau_formulas.jsonl exists in: {RULES_DIR}\n"
        f"2. Check the file has valid JSONL format\n"
    )


@Language.component("custom_tableau_formulas_ruler")
def custom_tableau_formulas_ruler_component(doc):
    """Custom spaCy pipeline component for Tableau formula entity recognition."""
    custom_tableau_formulas_ruler = create_ruler(rules=rules)
    return custom_tableau_formulas_ruler(doc)


# Register ruler_arg component
@Language.component("ruler_arg")
def ruler_arg_component(doc):
    """Custom component for argument entity recognition."""
    # Load rules for ruler_arg
    rules_path = Path(__file__).parent / "rules" / "ruler_arg.jsonl"

    if rules_path.exists():
        rules = []
        with open(rules_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rules.append(json.loads(line))
        ruler = create_ruler(rules=rules)
        return ruler(doc)
    return doc


@Language.component("ruler_sort_command")
def ruler_sort_command_component(doc):
    """Custom component to handle sort commands in Tableau queries."""
    for sent in doc.sents:
        text = sent.text.lower()
        if "sort by" in text:
            # Extract the criteria immediately following "sort by"
            try:
                criteria_start = text.index("sort by") + len("sort by")
                criteria = text[criteria_start:].strip()
                # Custom logic to handle "sort by <criteria>"
                # You could add entity annotations or custom attributes here
                # Example: doc._.sort_criteria = criteria
            except (ValueError, IndexError):
                pass
        elif "sort" in text:
            # Custom logic to handle generic "sort"
            # You could mark this sentence as containing a sort command
            pass
    return doc


if __name__ == "__main__":
    # Test the component
    print("\n" + "=" * 80)
    print("TESTING CUSTOM TABLEAU FORMULAS RULER COMPONENT")
    print("=" * 80 + "\n")

    # Add components to pipeline if not already present
    if "custom_tableau_formulas_ruler" not in nlp.pipe_names:
        nlp.add_pipe("custom_tableau_formulas_ruler", last=True)
        print("✅ Added 'custom_tableau_formulas_ruler' to pipeline")

    if "ruler_sort_command" not in nlp.pipe_names:
        nlp.add_pipe("ruler_sort_command", last=True)
        print("✅ Added 'ruler_sort_command' to pipeline")

    print(f"\n📊 Current pipeline: {nlp.pipe_names}\n")
    print("-" * 80)

    # Test with sample texts focused on Tableau formulas
    test_texts = [
        "Create a calculated field using SUM([Sales]) and AVG([Profit])",
        "Use IF [Sales] > 1000 THEN 'High' ELSE 'Low' END",
        "Calculate the running total with WINDOW_SUM(SUM([Sales]))",
        "Apply DATEPART('month', [Order Date]) to extract month",
        "Sort by sales descending",
        "Filter where CONTAINS([Product Name], 'Chair')",
        "Create a level of detail expression: {FIXED [Region] : SUM([Sales])}",
        "Use LOOKUP(SUM([Sales]), -1) for previous period comparison",
        "Calculate year over year growth with ZN(SUM([Sales])) / ZN(SUM([Sales Previous Year])) - 1",
    ]

    print("\n🧪 Testing with sample Tableau formula queries:\n")

    for i, test_text in enumerate(test_texts, 1):
        print(f"Test {i}: {test_text}")

        try:
            doc = nlp(test_text)

            if doc.ents:
                print("   Entities found:")
                for ent in doc.ents:
                    print(f"     • {ent.text:40} -> {ent.label_}")
            else:
                print("     (No entities detected)")
        except Exception as e:
            print(f"     ❌ Error processing: {e}")

        print()

    print("-" * 80)
    print("\n✅ Component test complete!")
    print("\n💡 Backups are automatically managed in .versions/ directory")
    print(
        "   • To list backups: python -m hypatiax.auto_migrate list ruler_tableau_formulas.jsonl rules"
    )
    print(
        "   • To restore: python -m hypatiax.auto_migrate restore ruler_tableau_formulas.jsonl rules --index 0"
    )

#!/usr/bin/env python3
"""
Custom Tableau Components with Auto-Migration
Loads NER rules with automatic change detection and backup for combined tableau rules.
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


def load_rules(rule_type: str = "ruler_tableau_both") -> list:
    """
    Load rules from a JSONL file.

    Args:
        rule_type: Base name of the rule file (without .jsonl)

    Returns:
        List of rule dictionaries
    """
    path_to_file = RULES_DIR / f"{rule_type}.jsonl"

    if not path_to_file.exists():
        raise FileNotFoundError(
            f"Rule file not found: {path_to_file}\n"
            f"Expected location: {path_to_file}\n"
            f"Available files in {RULES_DIR}:\n"
            + "\n".join(f"  - {f.name}" for f in RULES_DIR.glob("*.jsonl"))
        )

    print(f"📂 Loading rules: {path_to_file.name}")

    # Load rules from file
    rules = []
    with open(path_to_file, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                # Strip whitespace to ignore empty lines
                if line.strip():
                    rules.append(json.loads(line))
            except json.JSONDecodeError as e:
                # Provide a more informative error message
                raise ValueError(
                    f"Error parsing JSON in {path_to_file.name} "
                    f"on line {line_number}: {e.msg}"
                )

    print(f"✅ Loaded {len(rules)} rules from {path_to_file.name}")
    return rules


# Load rules with auto-migration
try:
    # Auto-migrate: detects changes, creates backups, auto-restores if broken
    migrate(
        filename="ruler_tableau_both.jsonl",
        style="rules",
        modules="custom_ner",
        domains="queries",
        sub_domains="tableau",
        folder="rules",
    )

    # Load rules (always from canonical name)
    rules = load_rules("ruler_tableau_both")

except FileNotFoundError as e:
    raise FileNotFoundError(
        f"Rule file not found: {e}\n\n"
        f"💡 To fix this issue:\n"
        f"1. Make sure ruler_tableau_both.jsonl exists in: {RULES_DIR}\n"
        f"2. Check the file has valid JSONL format\n"
    )


@Language.component("custom_tableau_ruler")
def custom_tableau_ruler_component(doc):
    """Custom spaCy pipeline component for Tableau entity recognition (combined rules)."""
    custom_tableau_ruler = create_ruler(rules=rules)
    return custom_tableau_ruler(doc)


@Language.component("ruler_sort_command")
def ruler_sort_command_component(doc):
    """Custom component to handle sort commands in Tableau queries."""
    for sent in doc.sents:
        text = sent.text.lower()
        if "sort by" in text:
            # Extract the criteria immediately following "sort by"
            criteria_start = text.index("sort by") + len("sort by")
            criteria = text[criteria_start:].strip()
            # Custom logic to handle "sort by <criteria>"
            # Could add entity or custom attribute here
            pass
        elif "sort" in text:
            # Custom logic to handle generic "sort"
            pass
    return doc


if __name__ == "__main__":
    # Test the component
    print("\n" + "=" * 80)
    print("Testing custom_tableau_ruler component")
    print("=" * 80 + "\n")

    # Add component to pipeline
    if "custom_tableau_ruler" not in nlp.pipe_names:
        nlp.add_pipe("custom_tableau_ruler", last=True)

    if "ruler_sort_command" not in nlp.pipe_names:
        nlp.add_pipe("ruler_sort_command", last=True)

    # Test with sample text
    test_texts = [
        "Create a calculated field using SUM([Sales]) and AVG([Profit])",
        "Sort by sales descending",
        "Filter the data and show top 10 customers",
    ]

    for test_text in test_texts:
        doc = nlp(test_text)
        print(f"Text: {test_text}")

        if doc.ents:
            print("Entities found:")
            for ent in doc.ents:
                print(f"  {ent.text:30} -> {ent.label_}")
        else:
            print("  (No entities detected)")
        print()

    print("✅ Component test complete")
    print("\n💡 Backups are automatically managed in .versions/ directory")
    print(
        "   • To list backups: python -m hypatiax.auto_migrate list ruler_tableau_both.jsonl rules"
    )
    print(
        "   • To restore: python -m hypatiax.auto_migrate restore ruler_tableau_both.jsonl rules --index 0"
    )

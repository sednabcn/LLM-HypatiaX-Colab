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


@Language.component("ruler_arg")
def ruler_arg_component(doc):
    ruler_arg = create_ruler(rules=rules)
    return ruler_arg(doc)


@Language.component("ruler_argn")
def ruler_argn_component(doc):
    ruler_argn = create_ruler(rules=rules)
    return ruler_argn(doc)


@Language.component("ruler_num")
def ruler_num_component(doc):
    ruler_num = create_ruler(rules=rules)
    return ruler_num(doc)


@Language.component("ruler_numm")
def ruler_numm_component(doc):
    ruler_numm = create_ruler(rules=rules)
    return ruler_numm(doc)


@Language.component("ruler_advv")
def ruler_advv_component(doc):
    ruler_advv = create_ruler(rules=rules)
    return ruler_advv(doc)


@Language.component("ruler_oper")
def ruler_oper_component(doc):
    ruler_oper = create_ruler(rules=rules)
    return ruler_oper(doc)


@Language.component("ruler_adpp")
def ruler_adpp_component(doc):
    ruler_adpp = create_ruler(rules=rules)
    return ruler_adpp(doc)


@Language.component("ruler_nounn")
def ruler_nounn_component(doc):
    ruler_nounn = create_ruler(rules=rules)
    return ruler_nounn(doc)


@Language.component("ruler_adjj")
def ruler_adjj_component(doc):
    ruler_adjj = create_ruler(rules=rules)
    return ruler_adjj(doc)


@Language.component("ruler_intj")
def ruler_intj_component(doc):
    ruler_intj = create_ruler(rules=rules)
    return ruler_intj(doc)


@Language.component("ruler_verb")
def ruler_verb_component(doc):
    ruler_verb = create_ruler(rules=rules)
    return ruler_verb(doc)


@Language.component("ruler_adv")
def ruler_adv_component(doc):
    ruler_adv = create_ruler(rules=rules)
    return ruler_adv(doc)


@Language.component("ruler_pron")
def ruler_pron_component(doc):
    ruler_pron = create_ruler(rules=rules)
    return ruler_pron(doc)


@Language.component("ruler_adp")
def ruler_adp_component(doc):
    ruler_adp = create_ruler(rules=rules)
    return ruler_adp(doc)


@Language.component("ruler_noun")
def ruler_noun_component(doc):
    ruler_noun = create_ruler(rules=rules)
    return ruler_noun(doc)


@Language.component("ruler_adj")
def ruler_adj_component(doc):
    ruler_adj = create_ruler(rules=rules)
    return ruler_adj(doc)


@Language.component("ruler_propn")
def ruler_propn_component(doc):
    ruler_propn = create_ruler(rules=rules)
    return ruler_propn(doc)


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

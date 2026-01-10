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


# Register ALL components to use the same rule set


@Language.component("custom_tableau_formulas_ruler")
def custom_tableau_formulas_ruler_component(doc):
    """Custom spaCy pipeline component for Tableau formula entity recognition."""
    custom_tableau_formulas_ruler = create_ruler(rules=rules)
    return custom_tableau_formulas_ruler(doc)


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
    return doc


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TESTING COMPONENTS")
    print("=" * 80 + "\n")

    # Test with fresh pipeline
    test_nlp = spacy.load("en_core_web_sm")

    # Add ruler BEFORE ner
    test_nlp.add_pipe("ruler_oper", before="ner")

    print(f"📊 Pipeline: {test_nlp.pipe_names}\n")

    test_texts = ["SUM ( Sepal Width )", "COUNT ( * )", "AVG ( Petal Length )"]

    for text in test_texts:
        print(f"Input: {text}")
        doc = test_nlp(text)

        if doc.ents:
            for ent in doc.ents:
                print(f"  {ent.text:30} -> {ent.label_}")
        else:
            print("  (No entities detected)")
        print()

    print("=" * 80)
    print("✅ Component test complete!")

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
        "SUM ( Sepal Width )",
        "COUNT ( * )",
        "AVG ( Petal Length )"
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

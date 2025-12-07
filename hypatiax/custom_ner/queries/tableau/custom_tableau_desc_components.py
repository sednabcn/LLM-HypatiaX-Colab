import json
import os
from pathlib import Path

import spacy
from spacy.language import Language

from hypatiax.auto_migrate import migrate
from hypatiax.utils.utils import create_ruler

nlp = spacy.load("en_core_web_sm")

script_dir = Path(__file__).parent
rules_dir = script_dir / "rules"


def load_rules():
    """Load rules from the canonical JSONL file."""
    script_dir = Path(__file__).parent
    path_to_file = script_dir / "rules" / "ruler_tableau_desc.jsonl"

    if not path_to_file.exists():
        raise FileNotFoundError(f"Rule file not found: {path_to_file}")

    print(f"📂 Loading rules: {path_to_file}")

    rules = []
    with open(path_to_file, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                # Strip whitespace to ignore empty lines
                if line.strip():
                    rules.append(json.loads(line))
            except json.JSONDecodeError as e:
                # Provide a more informative error message
                raise ValueError(f"Error parsing JSON on line {line_number}: {e.msg}")
    return rules


"""Loading the rules from file with auto-migration"""
rules = None
try:
    # Auto-migrate: detects changes, creates backups, auto-restores if broken
    migrate(
        filename="ruler_tableau_desc.jsonl",
        style="rules",
        modules="custom_ner",
        domains="queries",
        sub_domains="tableau",
        folder="rules",
    )

    # Load rules (always from canonical name)
    rules = load_rules()
    print(f"✅ Loaded {len(rules)} rules successfully")

except FileNotFoundError as e:
    raise FileNotFoundError(f"Failed to load rules: {e}")
except Exception as e:
    raise RuntimeError(f"Error loading rules: {e}")

# Register ALL components to use the same rule set


@Language.component("custom_tableau_desc_ruler")
def custom_tableau_desc_ruler_component(doc):
    custom_tableau_desc_ruler = create_ruler(rules=rules)
    return custom_tableau_desc_ruler(doc)


@Language.component("ruler_arg")
def ruler_arg_component(doc):
    ruler_arg = create_ruler(rules=rules)
    return ruler_arg(doc)


@Language.component("ruler_argn")
def ruler_argn_component(doc):
    ruler_argn = create_ruler(rules=rules)
    return ruler_argn(doc)


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


@Language.component("ruler_num")
def ruler_num_component(doc):
    ruler_num = create_ruler(rules=rules)
    return ruler_num(doc)


@Language.component("ruler_sort_command")
def ruler_sort_command_component(doc):
    return doc

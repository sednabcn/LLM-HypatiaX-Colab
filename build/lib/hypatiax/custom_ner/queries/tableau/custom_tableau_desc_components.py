import os
import json
import spacy
from spacy.tokens import Doc
from spacy.language import Language
from spacy.pipeline import EntityRuler
from importlib import resources
from hypatiax.utils.utils import create_ruler

nlp = spacy.load("en_core_web_sm")

def load_rules(version):
    # Dynamically construct the path based on provided parameters
    path_to_file = resources.files('hypatiax.custom_ner.queries.tableau.rules').joinpath(f'rules_tableau_desc_{version}.jsonl')

    """Load rules from a JSONL file, with improved error handling."""
    rules = []
    with open(path_to_file, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            try:
                # Strip whitespace to ignore empty lines
                if line.strip():
                    rules.append(json.loads(line))
            except json.JSONDecodeError as e:
                # Provide a more informative error message
                raise ValueError(f"Error parsing JSON on line {line_number}: {e.msg}")
    return rules
"""Loading the rules from file"""     
try:
    rules = load_rules("version1")
    #print(rules)
except FileNotFoundError:
    raise FileNotFoundError(f"Rule file not found")

@Language.component("custom_tableau_desc_ruler")
def custom_tableau_desc_ruler_component(doc):
        custom_tableau_desc_ruler=create_ruler(rules=rules)
        return custom_tableau_desc_ruler(doc)

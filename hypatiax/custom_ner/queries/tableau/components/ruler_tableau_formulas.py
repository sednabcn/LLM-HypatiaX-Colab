import json
import os
from importlib import resources

import spacy
from spacy.language import Language
from spacy.pipeline import EntityRuler
from spacy.tokens import Doc

from hypatiax.utils.files_local import load
from hypatiax.utils.utils import create_ruler

nlp = spacy.load("en_core_web_sm")


@Language.component("custom_tableau_formulas_ruler")
def custom_tableau_formulas_ruler_component(
    doc,
    nlp=nlp,
    name="custom_tableau_formulas_ruler",
    sub_domain="tableau",
    type="formulas",
    path_to_file=None,
):
    if path_to_file is None:
        # Dynamically construct the path based on provided parameters
        path_to_file = resources.files(
            "hypatiax.custom_ner.queries.tableau.rules"
        ).joinpath(f"ruler_{sub_domain}_{type}.jsonl")

    try:
        rules = load(path=path_to_file, style="rules")
    except FileNotFoundError:
        raise FileNotFoundError(f"Rule file not found: {path_to_file}")
    custom_tableau_formulas_ruler = create_ruler(rules=rules)
    return custom_tableau_formulas_ruler(doc)


@Language.component("ruler_sort_command")
def ruler_sort_command_component(doc):
    for sent in doc.sents:
        text = sent.text.lower()
        if "sort by" in text:
            # Extract the criteria immediately following "sort by"
            criteria_start = text.index("sort by") + len("sort by")
            criteria = text[criteria_start:].strip()
            # Custom logic to handle "sort by <criteria>"
            # print(f"Handling 'sort by {criteria}' command")
        elif "sort" in text:
            pass
        # Custom logic to handle "sort"
        # print("Handling 'sort' command")
        return doc


def setup_nlp_pipeline():
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("custom_tableau_formulas_ruler", before="ner")
    nlp.add_pipe("ruler_sort_command", before="ner")
    # List of custom labels used in your EntityRuler or custom component
    custom_labels = ["ARG", "ARGN", "OPER"]

    # Register each custom label in the nlp object's vocab
    for label in custom_labels:
        nlp.vocab.strings.add(label)
    ner_path = resources.files("hypatiax.data_spacy.queries.tableau").joinpath(
        "ner_tableau_formulas"
    )
    nlp.to_disk(ner_path)
    return nlp


# =========================================
nlp = setup_nlp_pipeline()
# ========================================
print(nlp.pipe_names)
# =========================================

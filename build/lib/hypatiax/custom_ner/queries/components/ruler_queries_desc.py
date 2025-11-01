import os
import json
import spacy
from spacy.tokens import Doc
from spacy.language import Language
from spacy.pipeline import EntityRuler
from importlib import resources
from hypatiax.utils.files_local import load
from hypatiax.utils.utils import create_ruler

nlp = spacy.load("en_core_web_sm")

@Language.component("custom_queries_desc_ruler")
def custom_queries_desc_ruler_component(doc,nlp=nlp, name='custom_queries_desc_ruler', rules_version="version1", domain="queries", type="desc", path_to_file=None):
    if path_to_file is None:
        # Dynamically construct the path based on provided parameters
        path_to_file =resources.files('hypatiax.custom_ner.queries.rules').joinpath(f'rules_{domain}_{type}_{rules_version}.jsonl')
    
    try:
        rules = load(path=path_to_file,style="rules")
    except FileNotFoundError:
        raise FileNotFoundError(f"Rule file not found: {path_to_file}")
    custom_queries_desc_ruler=create_ruler(rules=rules)
    return custom_queries_desc_ruler(doc)

def setup_nlp_pipeline():
    nlp=spacy.load("en_core_web_sm")
    nlp.add_pipe("custom_queries_desc_ruler",before="ner")
    ner_path = resources.files('hypatiax.data_spacy.queries').joinpath("ner_queries_desc")
    nlp.to_disk(ner_path)
    return nlp


#=========================================
nlp =setup_nlp_pipeline()
#========================================
print(nlp.pipe_names)
#=========================================


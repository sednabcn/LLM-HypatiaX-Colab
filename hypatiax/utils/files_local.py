#/usr/bin/python3
import os
import pandas as pd
import json
import spacy
from importlib import resources
from hypatiax.utils.utils import upload_spacy_training_data,upload_spacy_training_data_from_json
from hypatiax.custom_ner.queries.tableau import custom_tableau_desc_components, custom_tableau_formulas_components

def load(filename=None, path=None, style=None):
    """
    Load files like datasets, ner, entities, models, rules
    style:
    1) datasets
    2) ner
    3) entities
    4) models
    5) rules
    """

    if filename is None or not isinstance(filename, str):
        raise ValueError("Filename must be a non-empty string.")

    if style not in [None, 'datasets', 'ner', 'entities', 'models', 'rules']:
        raise ValueError("Invalid style specified. Must be one of ['datasets', 'ner', 'entities', 'models', 'rules'] or None.")

    try:
        if filename.endswith('.csv'):
            return pd.read_csv(filename)
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filename, index_col=0)
            if len(df.columns) != 2:
                df.reset_index(inplace=True)
            return df
        elif filename.endswith('.txt'):
            with open(filename, 'r') as file:
                return file.read()
        elif style == "ner":
            model_path = os.path.abspath(filename)
            return spacy.load(model_path)
        elif filename.endswith('.spacy') and style == "entity":
            ner_entity = "ner_" + filename.split('_')[1]
            ner_entity = os.path.join(os.path.abspath('..'), ner_entity)
            nlp = spacy.load(ner_entity)
            return upload_spacy_training_data(os.path.abspath('.'), filename.rsplit(".", 1)[0], nlp)
        elif filename.endswith(".json") and style == "entity":
            return upload_spacy_training_data_from_json(os.path.abspath('.'), filename.rsplit(".", 1)[0])
        elif style == "models":
            return spacy.load(os.path.abspath(filename))
        elif style == "rules":
            rules_path = path if path else filename
            rules = []
            with open(rules_path, 'r', encoding='utf-8') as file:
                for line_number, line in enumerate(file, start=1):
                    if line.strip():
                        rules.append(json.loads(line))
            return rules
        else:
            raise ValueError("Unsupported file type or operation.")
    except Exception as e:
        raise IOError(f"Failed to load file '{filename}' due to an error: {str(e)}")


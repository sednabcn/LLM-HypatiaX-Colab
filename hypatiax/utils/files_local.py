# /usr/bin/python3
import json
import os
from importlib import resources

import pandas as pd
import spacy

from hypatiax.auto_migrate import migrate
from hypatiax.utils.utils import upload_spacy_training_data, upload_spacy_training_data_from_json


def load(filename=None, path=None, style=None, auto_migrate=True):
    """
    Load files like datasets, ner, entities, models, rules

    Args:
        filename: Name of file to load
        path: Optional path override
        style: Type of file ('datasets', 'ner', 'entity', 'models', 'rules')
        auto_migrate: If True, automatically backup and validate (default: True)

    Style options:
        1) datasets
        2) ner
        3) entity
        4) models
        5) rules
    """

    if filename is None or not isinstance(filename, str):
        raise ValueError("Filename must be a non-empty string.")

    if style not in [None, "datasets", "ner", "entity", "models", "rules"]:
        raise ValueError(
            "Invalid style specified. Must be one of ['datasets', 'ner', 'entity', 'models', 'rules'] or None."
        )

    # ============================================
    # AUTO-MIGRATE BLOCK - Backup and validation
    # ============================================
    if auto_migrate and style in ["ner", "entity", "models", "rules"]:
        try:
            from hypatiax.auto_migrate import migrate

            # Determine file path for migration
            file_to_migrate = path if path else filename

            # Determine modules and folder based on style

            if style == "rules":
                modules = "custom_ner"
                folder = "rules"
            elif style == "ner" or style == "models":
                modules = "data_spacy"
                folder = ""
            elif style == "entity":
                # Determine if training or testing
                if "Train" in filename:
                    modules = "datasets"
                    folder = "training_spacy"
                elif "Test" in filename:
                    modules = "datasets"
                    folder = "testing_spacy"
                else:
                    modules = "datasets"
                    folder = "training_spacy"
            else:
                modules = "custom_ner"
                folder = "rules"

            # Execute migration (detects changes, creates backups, auto-restores if broken)
            migrate(
                filename=filename, style=style, modules=modules, domains="queries", sub_domains="tableau", folder=folder
            )

        except ImportError:
            # auto_migrate.py not available, continue without migration
            pass
        except Exception as e:
            # Migration failed, log but continue
            print(f"⚠️  Migration warning: {e}")

    try:
        if filename.endswith(".csv"):
            return pd.read_csv(filename)
        elif filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(filename, index_col=0)
            if len(df.columns) != 2:
                df.reset_index(inplace=True)
            return df
        elif filename.endswith(".txt"):
            with open(filename, "r") as file:
                return file.read()
        elif style == "ner":
            from hypatiax.custom_ner.queries.tableau import (
                custom_tableau_desc_components,
                custom_tableau_formulas_components,
            )

            model_path = os.path.abspath(filename)
            return spacy.load(model_path)
        elif filename.endswith(".spacy") and style == "entity":
            base_filename = os.path.basename(filename)
            ner_entity = "ner_" + base_filename.split("_")[1]
            ner_entity = os.path.join(os.path.abspath(".."), ner_entity)
            nlp = spacy.load(ner_entity)

            return upload_spacy_training_data(os.path.abspath("."), filename.rsplit(".", 1)[0], nlp)
        elif filename.endswith(".json") and style == "entity":
            return upload_spacy_training_data_from_json(os.path.abspath("."), filename.rsplit(".", 1)[0])
        elif style == "models":
            from hypatiax.custom_ner.queries.tableau import (
                custom_tableau_desc_components,
                custom_tableau_formulas_components,
            )

            return spacy.load(os.path.abspath(filename))
        elif style == "rules":
            from hypatiax.custom_ner.queries.tableau import (
                custom_tableau_desc_components,
                custom_tableau_formulas_components,
            )

            rules_path = path if path else filename
            rules = []
            with open(rules_path, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    if line.strip():
                        rules.append(json.loads(line))
            return rules
        else:
            raise ValueError("Unsupported file type or operation.")
    except Exception as e:
        raise IOError(f"Failed to load file '{filename}' due to an error: {str(e)}")

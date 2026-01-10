import json
import os
from importlib import resources
from pathlib import Path

import pandas as pd
import spacy

from hypatiax.auto_migrate import migrate
from hypatiax.utils.utils import (
    upload_spacy_training_data,
    upload_spacy_training_data_from_json,
)


class FilesManager:
    def __init__(self, modules, domains, sub_domains, actions, package="hypatiax"):
        self.package = package
        self.path_domains = f"{self.package}.{modules}.{domains}.{sub_domains}"
        self.domains = domains
        self.sub_domains = sub_domains
        self.path_dir = f"{self.path_domains}.{actions}"
        self.modules = modules
        self.actions = actions

    def load(self, filename="default", style=None):

        migrate(
            filename,
            style,
            package=self.package,
            modules=self.modules,
            domains=self.domains,
            sub_domains=self.sub_domains,
            folder=self.actions,
        )

        if filename.endswith(".csv"):
            return self._load_csv(filename)
        elif filename.endswith((".xls", ".xlsx")):
            return self._load_excel(filename)
        elif filename.endswith(".txt"):
            return self._load_text(filename)
        elif style == "ner":
            return self._load_ner(filename)
        elif filename.endswith(".spacy") and style == "entity":
            return self._load_entity(filename)
        elif filename.endswith(".json") and style == "entity":
            return self._load_entity_json(filename)
        elif style == "rules":
            return self._load_rules(filename)
        elif style == "models":
            return self._load_models(filename)
        else:
            raise ValueError(
                f"Unsupported file type or operation for filename: {filename}"
            )

    def _load_csv(self, filename):
        with resources.open_text(self.path_dir, filename) as file:
            try:
                return pd.read_csv(file)
            except FileNotFoundError:
                raise FileNotFoundError("File not found or wrong format")

    def _load_excel(self, filename):
        with resources.open_binary(self.path_dir, filename) as file:
            df = pd.read_excel(file, index_col=0)
            if len(df.columns) == 1:
                df.reset_index(inplace=True)
            return df

    def _load_text(self, filename):
        with resources.open_text(f"{self.path_dir}.data", filename) as file:
            return file.read()

    def _load_ner(self, filename):
        from hypatiax.custom_ner.queries.tableau import (
            custom_tableau_components,
            custom_tableau_desc_components,
            custom_tableau_formulas_components,
        )

        model_path = resources.files(self.path_domains).joinpath(filename)
        return spacy.load(str(model_path))

    def _load_entity(self, filename):
        from hypatiax.custom_ner.queries.tableau import (
            custom_tableau_components,
            custom_tableau_desc_components,
            custom_tableau_formulas_components,
        )

        filename_, ext = filename.split(".")
        ner_entity = "ner_" + filename.split("_")[1]
        ner_path = resources.files(self.path_domains).joinpath(str(ner_entity))
        nlp = spacy.load(ner_path)
        with resources.files(self.path_dir) as model_path:
            return upload_spacy_training_data(str(model_path), filename_, nlp)

    def _load_entity_json(self, filename):
        filename_, ext = filename.split(".")
        model_path = Path(self.path_dir.replace(".", "/"))
        return upload_spacy_training_data_from_json(str(model_path), filename_)

    def _load_rules(self, filename):
        if filename.endswith(".jsonl"):
            rules_path = Path(self.path_dir.replace(".", "/")) / filename
        else:
            raise ValueError("Invalid file type for rules")
        rules = []
        with open(str(rules_path), "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if line.strip():
                    rules.append(json.loads(line))
        return rules

    def _load_models(self, filename):
        model_path = Path(self.path_dir.replace(".", "/")) / filename
        return spacy.load(str(model_path))

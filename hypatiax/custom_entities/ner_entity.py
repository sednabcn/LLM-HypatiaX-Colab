import os

import pandas as pd
import spacy

from hypatiax.custom_ner.queries.tableau import (
    custom_tableau_components,
    custom_tableau_desc_components,
    custom_tableau_formulas_components,
)
from hypatiax.utils.utils import set_entity


class Custom_ner_entities:

    def __init__(self, data, path_ner_entity, column_name):
        self.data = data
        self.path_ner_entity = path_ner_entity
        self.column_name = column_name

    def get_entity(self):
        return set_entity(self.data, self.column_name, self.path_ner_entity)

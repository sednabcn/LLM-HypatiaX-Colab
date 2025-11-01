import os
import spacy
import pandas as pd
import logging
from importlib import resources
from hypatiax.patterns.queries.generation import Generation_custom_queries_patterns
from spacy import load as spacy_load
import argparse  # Import argparse library

# Setup basic logging
logging.basicConfig(level=logging.INFO)

# Initialize the spaCy model
nlp = spacy_load("en_core_web_sm")

def patterns_rules(data, ind, type):
    # Define stopwords for descriptions and formulas
    stopwords_desc = ['\\', 'Iri', 'Se', 'C', 'Sepal', 'ica', 'Length', "'s", '.', "'", 's', 'a', '(', ')', 'Petal', 'Distinct', "Width", ',', "'", "[", "]"]
    stopwords_formulas = ['\\', 'Iri', 'Se', 'C', 'Sepal', 'ica', 'Length', "'s", '.', "'", 's', 'a', '(', ')', 'Petal', 'Distinct', 'distinct', "Width", ',', 'BY', 'by', 'from', "[", "]"]
    
    if ind == "B":
        chosen_stopwords = list(set(stopwords_desc + stopwords_formulas))
    elif ind == "F":
        chosen_stopwords = stopwords_formulas
    elif ind == "S":
        chosen_stopwords = stopwords_desc
    else:
        logging.error(f"Invalid indicator '{ind}'. Must be 'S', 'F', or 'B'.")
        return None

    generator = Generation_custom_queries_patterns(data, chosen_stopwords)
    return generator.create_ruler_queries(nlp, type)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate query patterns.')
    parser.add_argument('type', help='Type of patterns to generate (desc, formulas, both)')
    args = parser.parse_args()

    try:
        path_data = resources.files('hypatiax.datasets.queries.training').joinpath('formulas.xlsx')
        if path_data.exists():
            result = patterns_rules(path_data, "B", args.type)
        else:
            logging.error(f"Data file {path_data} does not exist.")
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)

import os
import spacy
from hypatiax.custom_ner.queries.tableau import custom_tableau_desc_components,custom_tableau_formulas_components, custom_tableau_components

from hypatiax.utils.files import FilesManager
F=FilesManager('data_spacy','queries','tableau','')
# Load ner_desc English tokenizer, tagger, parser and NER
nlp=F.load('ner_tableau_desc','ner')
#nlp = spacy.load("en_core_web_sm")
# Test
text="Sum of Sepal Length. Average Sepal Width across all entries . Count the number of records in the dataset"
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)

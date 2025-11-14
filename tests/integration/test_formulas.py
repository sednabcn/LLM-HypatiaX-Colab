#/usr/bin/python3
import spacy
import os
from hypatiax.custom_ner.queries.tableau import custom_tableau_desc_components,custom_tableau_formulas_components, custom_tableau_components
from hypatiax.utils.files import FilesManager
F=FilesManager('data_spacy','queries','tableau','')

# Load English tokenizer, tagger, parser and NER

nlp=F.load('ner_tableau_formulas','ner')

# Test
text="SUM ( Sepal Length ) AVG ( Sepal Length )"
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)


# Test
text=" SORT ( [ Species ] , DESC ) "
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)

# Test
text=" SORT ( [ Species ] , DESC ) INDEX ( ) < = 3 SORT BY [ Petal Length ] ASC"
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)

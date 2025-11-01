#/usr/bin/python3
import spacy
import os
from hypatiax.custom_ner.queries.tableau import custom_tableau_desc_components,custom_tableau_formulas_components, custom_tableau_components
from hypatiax.utils.files import FilesManager
from hypatiax.utils.utils import get_ner_desc_formulas
# Load ner_desc English tokenizer, tagger, parser and NER
F=FilesManager('data_spacy','queries','tableau','')
try:
    nlp=F.load('ner_tableau','ner')
except:
    nlp_formulas=F.load('ner_tableau_formulas','ner')
    nlp_desc=F.load('ner_tableau_desc','ner')
    nlp=get_ner_desc_formulas(nlp_formulas,nlp_desc,'ruler_arg')
    nlp.to_disk("../hypatiax/data_spacy/queries/tableau/ner_tableau")

print("=============================================")
print(nlp.pipe_names)
print("=============================================")

#Test
text="Calculate the total of Petal Lengths :  SUM ( [ Petal Length ] )"
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)

print("=============================================")
#Test
text="Minimum value of Sepal Length : MIN ( Sepal Length ) "
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)
print("=============================================")

#Test
text="Entries with Petal Length between 1.5 and 2.5 : Petal Length BETWEEN 1.5 AND 2.5"
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)
print("=============================================")

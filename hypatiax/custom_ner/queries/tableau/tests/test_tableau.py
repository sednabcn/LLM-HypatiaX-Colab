import os
# Set the environment variable
os.environ['SAVE_TO_DISK'] = 'False'
import spacy
from importlib import resources
from spacy.pipeline import EntityRuler
from spacy.language import Language
from hypatiax.custom_ner.queries.tableau import custom_tableau_components

# Load the spaCy model

#nlp = spacy.load("en_core_web_sm")
  
ner_path=resources.files('hypatiax.data_spacy.queries.tableau').joinpath("ner_tableau")

nlp=spacy.load(ner_path)

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

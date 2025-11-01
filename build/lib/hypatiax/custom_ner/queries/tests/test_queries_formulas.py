import spacy
from importlib import resources
from spacy.pipeline import EntityRuler
from spacy.language import Language
from hypatiax.custom_ner.queries import custom_queries_formulas_components 

# Load the spaCy model

#nlp = spacy.load("en_core_web_sm")
  
ner_path=resources.files('hypatiax.data_spacy.queries').joinpath("ner_queries_formulas")

nlp=spacy.load(ner_path)

print("=============================================")
print(nlp.pipe_names)
print("=============================================")


# Test
text="SUM ( Sepal Length ) AVG ( Sepal Length ) "
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)


# Test
text=" SORT [ Species ] , DESC  "
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


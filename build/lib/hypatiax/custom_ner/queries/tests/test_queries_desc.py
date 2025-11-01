import spacy
from hypatiax.custom_ner.queries import custom_queries_desc_components 
from importlib import resources

# Load the spaCy model
  
ner_path=resources.files('hypatiax.data_spacy.queries').joinpath("ner_queries_desc")

nlp=spacy.load(ner_path)

print("=============================================")
print(nlp.pipe_names)
print("=============================================")

# Test
text="Sum of Sepal Length. Average Sepal Width across all entries . Count the number of records in the dataset"
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)
print("=============================================")

#Test
text="Calculate the total of Petal Lengths"
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)

print("=============================================")
#Test
text="Minimum value of Sepal Length"
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)
print("=============================================")

#Test
text="Entries with Petal Length between 1.5 and 2.5"
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)
print("=============================================")



from hypatiax.utils.files import FilesManager
# Record the start time

F=FilesManager("data_spacy","queries","tableau",'')
#Test
try:
    nlp=F.load("ner_tableau_desc","ner")
    print("File ner_tableau_desc loaded successfully")
except:
    import spacy
    nlp=spacy.load("ner_tableau_desc")
    nlp.pipe_line("ner_tableau_desc",before="ner")
    print("File ner_desc not found ")


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

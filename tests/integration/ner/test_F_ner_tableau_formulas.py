from hypatiax.utils.files import FilesManager

# Record the start time

F = FilesManager("data_spacy", "queries", "tableau", "")
# Test
try:
    nlp = F.load(filename="ner_tableau_formulas", style="ner")
    print("File ner_tableau_formulas loaded successfully")
except:
    import spacy

    nlp = spacy.load("ner_tableau_formulas")
    nlp.add_pipe("ner_formulas", before="ner")
    print("File ner_formulas not found ")

print("=============================================")
print(nlp.pipe_names)
print("=============================================")


# Test
text = "SUM ( Sepal Length ) AVG ( Sepal Length )"
print(text)
doc = nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)


# Test
text = " SORT ( [ Species ] , DESC ) "
print(text)
doc = nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)

# Test
text = " SORT ( [ Species ] , DESC ) INDEX ( ) < = 3 SORT BY [ Petal Length ] ASC"
print(text)
doc = nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)

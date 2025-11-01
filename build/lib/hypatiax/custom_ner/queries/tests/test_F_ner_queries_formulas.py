from hypatiax.utils.files import FilesManager
# Record the start time

F=FilesManager("data_spacy","queries",'')
#Test
try:
    nlp=F.load(filename="ner_queries_formulas",style="ner")
    print("File ner_queries_formulas loaded successfully")
except:
    import spacy
    nlp=spacy.load("ner_queries_formulas")
    nlp.add_pipe("ner_formulas",before="ner")
    print("File ner_formulas not found ")

print("=============================================")
print(nlp.pipe_names)
print("=============================================")


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

from hypatiax.utils.files_local import load
#Test
try:
    nlp=load("ner_tableau_desc","ner")
    print("File ner_tableau_desc loaded successfully")
except:
    print("File ner_tableau_desc not found ")
# Test
text="Sum of Sepal Length. Average Sepal Width across all entries . Count the number of records in the dataset"
print(text)
try:
    doc=nlp(text)
    for ent in doc.ents:
        print(ent.text, ent.label_)
    print("Test passed successfully")
except:
     print("Wrong Test for ner_desc") 

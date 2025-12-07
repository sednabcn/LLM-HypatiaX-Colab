from hypatiax.utils.files_local import load

# Test
try:
    nlp = load("ner_tableau_formulas", "ner")
    print("File ner_tableau_formulas loaded successfully")
except:
    print("File ner_tableau_formulas not found ")
# Test
text = "SUM ( Sepal Length )"
print("Test:", text)
try:
    ent_ = {}
    doc = nlp(text)
    for ent in doc.ents:
        ent_[ent.text] = ent.label_
        print(ent.text, ent.label_)
    print("Test passed succesfully")
except:
    print("Wrong Test for ner_desc")
# Test
text2 = "SUM(Sepal Length)"
print("Test:", text2)
try:
    doc2 = nlp(text2)
    if doc2.ents == ():
        print("Error: Text must be normalized ")
    else:
        for ent in doc2.ents:
            if ent != None:
                print(ent.text, ent.label_)
                if ent_[ent.text] != ent.label_:
                    print("Error: Text must be normalized ")
                    break
                else:
                    print(f"{ent.text} has equal labels in both texts")
            else:
                print("Error: Text must be normalized ")
                break

except:
    print("Wrong Test for ner_formulas with not normalized text")

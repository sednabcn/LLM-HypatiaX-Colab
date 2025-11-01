from hypatiax.utils.files_local import load
from hypatiax.utils.files import FilesManager
from hypatiax.utils.utils import evaluate_the_model_in_batches,make_predictions
from importlib import resources

model_path=resources.files('hypatiax.models.queries.trained_models').joinpath('Description_Tableau_data') 

#Requirement
F=FilesManager('datasets','queries','testing')
dff=F.load("formulas_test_nor.xlsx")
print(dff.head(5))
F=FilesManager('datasets','queries','testing_spacy')
Test_formulas_data=F.load("Test_formulas_data.json",'entity')
for item in Test_formulas_data:
    print(item)

#Test 
nlp=load("Formulas_Tableau_data",'models')
ner = nlp.get_pipe("ner")

# List all labels the NER has been trained on
labels = ner.labels
print(labels)
# Evaluation the model on Test descritptions file: Test_desc_data in sPacy format
scores=evaluate_the_model_in_batches(nlp,Test_formulas_data)
print("+++++++++++++++++++++++++++++++++++++++++++++++++")
print("scores=",scores)
print("+++++++++++++++++++++++++++++++++++++++++++++++++")
# text
text=dff[dff.columns[1]][3]
print(text)
make_predictions(model_path,text)
text=dff[dff.columns[1]][0]
print(text)
make_predictions(model_path,text)

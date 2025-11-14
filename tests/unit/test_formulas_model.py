import spacy
from hypatiax.utils.files_local import load
from hypatiax.utils.files import FilesManager
from hypatiax.utils.utils import evaluate_the_model_in_batches,make_predictions
from importlib import resources
from hypatiax.custom_ner.queries.tableau import custom_tableau_formulas_components


niter=400
drop=0.5
batchsize=8
model_path=resources.files('hypatiax.models.queries.tableau.trained_models').\
    joinpath(f"Formulas_sm_tableau_{niter}_{drop}_{batchsize}_data")) 
#Requirement
F=FilesManager('datasets','queries','tableau','testing')
dff=F.load("formulas_test_nor.xlsx")
print(dff.head(5))
F=FilesManager('datasets','queries','tableau','testing_spacy')
Test_formulas_data=F.load("Test_tableau_formulas_sm_data.json",'entity')
for item in Test_formulas_data:
    print(item)

#Test
M=FilesManager('models','queries','tableau','trained_models')
nlp=M.load(f"Formulas_sm_tableau_{niter}_{drop}_{batchsize}_data",'models')
#nlp=spacy.load("Formulas_sm Tableau_data")
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

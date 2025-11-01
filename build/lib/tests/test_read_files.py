
from hypatiax.utils.files import load
from hypatiax.utils.utils import evaluate_the_model_in_batches,evaluate_the_model, make_predictions
"""
import unittest
from hypatiax.core import some_module
from importlib import resources

class TestDataAccess(unittest.TestCase):
    def test_data_loading(self):
        # Load test data
        with resources.open_text('hypatiax.datasets', 'datafile.csv') as file:
            data = file.read()
        # Assume some_module can process this data
        result = some_module.process_data(data)
        self.assertEqual(result, expected_result)
"""

#Test 1
#df=load("formulas.xlsx")
#print(df.head(10))
"""
#Test 2
df=load("tableau_data.csv")
print(df.head(10))
"""
#Test 3
#dff=load("formulas_test_nor.xlsx")
#print(dff.head(5))

#Test 4
nlp=load("ner_desc","ner")
# Test
text="Sum of Sepal Length. Average Sepal Width across all entries . Count the number of records in the dataset"
print(text)
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)

#Test 5
nlp=load("ner_formulas","ner")
# Test
text ='SUM ( Sepal Length )'
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)

#Test 6
nlp=load("ner_desc_formulas","ner")
text='Sum of Sepal Length . SUM ( Sepal Length )'
doc=nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)
    
#Test 6
#Test_desc_data=load("Test_desc_data.json",'entity')
"""
for item in Test_desc_data:
    print(item)
"""    
#Test 7
#nlp=load("Description_Tableau_data",'models')
#ner = nlp.get_pipe("ner")
"""
# List all labels the NER has been trained on
labels = ner.labels
print(labels)
from importlib import resources
model_path=resources.files('hypatiax.data_spacy').joinpath('Description_Tableau_data') 
scores=evaluate_the_model_in_batches(nlp,Test_desc_data)
print("+++++++++++++++++++++++++++++++++++++++++++++++++")
print("scores=",scores)
print("+++++++++++++++++++++++++++++++++++++++++++++++++")
# text
make_predictions(model_path,dff[dff.columns[0]][3])

make_predictions(model_path,dff[dff.columns[0]][0])

#Test 8
nlp=load("Combined_multi_task_data_400.0.5.8",'models')
ner = nlp.get_pipe("ner")

# List all labels the NER has been trained on
labels = ner.labels
print(labels)
from importlib import resources
model_path=resources.files('hypatiax.data_spacy').joinpath('Combined_multi_task_data_400.0.5.8')

scores=evaluate_the_model_in_batches(nlp,Test_desc_data)
print("+++++++++++++++++++++++++++++++++++++++++++++++++")
print("scores=",scores)
print("+++++++++++++++++++++++++++++++++++++++++++++++++")
# text
make_predictions(model_path,dff[dff.columns[0]][3])

make_predictions(model_path,dff[dff.columns[0]][0])
"""



import os 
import spacy
import pandas as pd
from hypatiax.custom_ner.queries.tableau import custom_tableau_desc_components,custom_tableau_formulas_components, custom_tableau_components
from hypatiax.custom_entities.ner_entity import Custom_ner_entities
from hypatiax.utils.utils import save_spacy_training_data, save_spacy_training_data_to_json
from hypatiax.utils.files import FilesManager
from importlib import resources
# save (optional)
option=0 # no save
# Load ner_desc English tokenizer, tagger, parser and NER
F=FilesManager('datasets','queries','tableau','training')
data = F.load('formulas_nor.xlsx')
G=FilesManager('datasets','tableau','testing')
data_t = G.load('formulas_test_nor.xlsx')
name_col='Description'

path_ner=resources.path('hypatiax.data_spacy.queries.tableau','ner_desc') 
# Train
ent_desc, Train_desc_data=Custom_ner_entities(data,path_ner,name_col).get_entity()
# Test
ent_test_desc, Test_desc_data=Custom_ner_entities(data_t,path_ner,name_col).get_entity()

# Train
print(ent_desc)

for item in Train_desc_data:
     print(item)

# Test
print(ent_test_desc)

for item in Test_desc_data:
    print(item)

# save to disk
path='~/Downloads/GEN_AI/PROJECTS/TABLEAU_FORMULAS/FORMULAS/hypatiax/hypatiax/data_spacy/queries/tableau'
path_tr=os.path.join(path,'training_spacy')
path_te=os.path.join(path,'testing_spacy')
path_vo=os.path.join(path,'vocab')

path_='~/Downloads/GEN_AI/PROJECTS/TABLEAU_FORMULAS/FORMULAS/hypatiax/hypatiax/datasets/queries/tableau'
path_tr_=os.path.join(path_,'training_spacy')
path_te_=os.path.join(path_,'testing_spacy')

if option !=0:
     path_ner=resources.path('hypatiax.data_spacy.queries.tableau','ner_desc')  
     #Train
     save_spacy_training_data(path_tr,Train_desc_data,"Train_tableau_desc_sm_data",path_ner)
     #Test
     save_spacy_training_data(path_te,Test_desc_data,"Test_tableau_desc_sm_data",path_ner)

     #Train
     save_spacy_training_data_to_json(path_tr_,Train_desc_data,"Train_tableau_desc_sm_data")
     save_spacy_training_data_to_json(path_vo,ent_desc,"vocab_tableau_desc_Description_sm")
     #Test
     save_spacy_training_data_to_json(path_te_,Test_desc_data,"Test_tableau_desc_sm_data")


#/usr/bin/python3
import spacy
import os
from hypatiax.custom_ner.queries.tableau import custom_tableau_desc_components,custom_tableau_formulas_components, custom_tableau_components
from hypatiax.custom_entities.ner_entity import Custom_ner_entities
from hypatiax.utils.utils import save_spacy_training_data, save_spacy_training_data_to_json
from hypatiax.utils.files import load
from importlib import resources

option=0 # save to disk
# Load English tokenizer, tagger, parser and NER

data = load('formulas_nor.xlsx')
data_t = load('formulas_test_nor.xlsx')
name_col='Formula'

path_formulas=resources.files('hypatiax.data_spacy.queries.tableau').joinpath('ner_formulas')
# Train
ent_formulas, Train_formulas_data=Custom_ner_entities(data,path_formulas,name_col).get_entity()
 
# Test
ent_test_formulas, Test_formulas_data=Custom_ner_entities(data_t,path_formulas,name_col).get_entity()

#Train
print(ent_formulas)

for item in Training_formulas_data:
     print(item)

# Test
print(ent_test_formulas)

for item in Test_formulas_data:
    print(item)

# save to disk
path='~/Downloads/GEN_AI/PROJECTS/TABLEAU_FORMULAS/FORMULAS/hypatiax/hypatiax/data_spacy/queries/tableau'
path_tr=os.path.join(path,'training_spacy')
path_te=os.path.join(path,'testing_spacy')
path_vo=os.path.join(path,'vocab')

path_='~/Downloads/GEN_AI/PROJECTS/TABLEAU_FORMULAS/FORMULAS/hypatiax/hypatiax/datasets/queries/tableau'
path_tr_=os.path.join(path_,'training_spacy')
path_te_=os.path.join(path_,'testing_spacy')

if option!=0:
          path_formulas=resources.path('hypatiax.data_spacy.queries.tableau','ner_formulas')
          #Train
          save_spacy_training_data(path_tr,Train_formulas_data,"Train_tableau_formulas_sm_data",path_formulas)
          #Test
          save_spacy_training_data(path_te,Test_formulas_data,"Test_tableau_formulas_sm_data",path_formulas)

          #Train
          save_spacy_training_data_to_json(path_tr_,Train_formulas_data,"Train_tableau_formulas_sm_data")
          save_spacy_training_data_to_json(path_vo,ent_formulas,"vocab_tableau_formulas_Formula_sm")
          #Test
          save_spacy_training_data_to_json(path_te_,Test_formulas_data,"Test_tableau_formulas_sm_data")
          

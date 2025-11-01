import os
import pandas as pd
import matplotlib.pyplot as plt
import nltk
import re
import spacy
from nltk.tokenize import word_tokenize, sent_tokenize,wordpunct_tokenize

from spacy import displacy
from spacy.matcher import matcher
from spacy.tokens import span
from spacy.language import Language
from spacy.pipeline import EntityRuler
from hypatiax.utils.utils import normalize_formula, preproc_ent,tok_formulas,get_pos_,get_patterns, get_formatted_patterns


#nltk.download('punkt')

# Load English tokenizer, tagger, parser and NER
nlp = spacy.load("en_core_web_sm")


class Generation_custom_tableau_patterns:
       def __init__(self, path_data,stopwords,train=True):
           self.data=path_data
           self.stopwords=stopwords
           self.train=train
           
           self.out_d,self.out_f= preproc_ent(self.data,self.stopwords)

           # Initialize patterns
           self.patterns_tableau_desc = self.gen_patterns_tableau_desc()
           self.patterns_tableau_formulas = self.gen_patterns_tableau_formulas()
           self.rules_tableau_desc=self.get_rules_tableau_desc()
           self.rules_tableau_formulas=self.get_rules_tableau_formulas()
           
       def gen_patterns_tableau_desc(self):
              
              
              p_d=get_patterns(self.out_d,"vocab",nlp)
              
              patterns_tableau_desc=[]
       
              # patterns to description
              p_d['CONJ']=p_d['CCONJ']+ p_d['SCONJ']
              p_d.pop('SCONJ',None)
              p_d.pop('CCONJ',None)
              p_d['VERB']=p_d['VERB'] + p_d['AUX']
              p_d.pop('AUX',None)
              p_d['PRON']=p_d['PRON'] + p_d['DET']
              p_d.pop('DET',None)
              p_d['NOUN']=[x for x in p_d['X'] if x != p_d['X'][1]]+p_d['NOUN'] +['dataset']
              p_d['ADJ']=[p_d['X'][1]]+[x for x in p_d['ADJ'] if x !='dataset' ]
              p_d['PROPN']=['Sepal Length','Sepal Width', 'Petal Length', 'Petal Width']+p_d['PROPN']
              p_d.pop('X',None)
              patterns_tableau_desc=[{key:value} for (key,value) in p_d.items() if value!=None]
              return patterns_tableau_desc

       def gen_patterns_tableau_formulas(self):
              p_t=get_patterns(self.out_f,"vocab",nlp)
              self.patterns_tableau_formulas=[]
              p_t['ARG']=['[Sepal Length]','[Sepal Width]','[Petal Length]','[Petal Width]', '[Species]']
              p_t['ARGN']=['Sepal Length','Sepal Width','Petal Length','Petal Width', 'Species']
              p_t['NOUN'] =['month', 'TODAY', 'color','YEAR','versicolor','setosa','year','virginica']
              p_t['STOPWORDS']=['[Sepal','Sepal','[Petal','Width]','Width','Petal','Length]',"'Se'",':','"virginica",'"setosa",'','{',')','*',"'Setosa'","'month', ",'4.0 AND','"setosa" AND','ica',"Iri",'!= 3.0','"versicolor" AND',"Species STARTS WITH 'Se'","Length",'"Iri"' ]
              p_t['NUM']=[ff  for ff in p_t['NUM'] if ff !='TOP']+['1.5','2.5','4.5','3.0','3','2.0','5.0']
              p_t['ADP']+=['to','AND','>=','<','!=','<=','=','>']
              p_t['ADV']=[ff for ff in p_t["ADV"] if ff!="SORT"] + ['highest to lowest','ASC','DESC','NULL','LEFT']
              p_t['ADJ']=[ff for ff in p_t['ADJ'] if  ff!='SORTED']
              ptt=p_t['ARG']+p_t['NOUN']+p_t['NUM'] + p_t['STOPWORDS'] + p_t['ARGN'] + p_t['ADV'] + p_t['ADP']+p_t['ADJ']
              p_t['OPER']=['STARTS WITH']
              p_t['OPER']+=tok_formulas(self.data,ptt)
              p_t['OPER'][p_t['OPER'].index('LISTED')]='LISTED FROM'
              p_t['OPER']+=['TOP BY']
              p_t['OPER']+=['IF CONTAINS','BY']
              p_t['NOUN']=[ff for ff in p_t['NOUN'] if ff not in p_t['OPER']]
              p_t.pop('STOPWORDS',None)
              p_t.pop('X',None)
              p_t.pop('AUX',None)
              p_t.pop('CCONJ',None)
              p_t.pop('INTJ',None)
              p_t.pop('PROPN',None)
              p_t.pop('PART',None)
              p_t.pop('PRON',None)
              p_t.pop('SCONJ',None)
              p_t.pop('VERB',None)
              p_t.pop('SCONJ',None)
              p_t.pop('PROPN',None)
              p_t.pop('PART',None)
              p_t.pop('PUNCT',None)
              # patterns to formulas
              patterns_tableau_formulas=[{key:value} for (key,value) in p_t.items() if value!=None]
              return patterns_tableau_formulas

       def  get_rules_tableau_desc(self):
                     return get_formatted_patterns(*self.patterns_tableau_desc)

       def  get_rules_tableau_formulas(self):
                     return get_formatted_patterns(*self.patterns_tableau_formulas)
       def create_ruler_tableau(self, nlp, type):
              from importlib import resources
              from spacy.pipeline import EntityRuler

              # Initialize the EntityRuler
              ruler = EntityRuler(nlp)

              # Define file paths based on type
              file_paths = {
                     'desc': 'ruler_tableau_desc.jsonl',
                     'formulas': 'ruler_tableau_formulas.jsonl',
                     'both': 'ruler_tableau.jsonl'
              }
              
              # Check and add patterns based on type
              if type == 'desc' or type == 'both':
                     ruler.add_patterns(self.rules_tableau_desc)
              if type == 'formulas' or type == 'both':
                     ruler.add_patterns(self.rules_tableau_formulas)
                            
              # Save the ruler to a file
              path_to_file = resources.files('hypatiax.custom_ner.queries.tableau.rules').joinpath(file_paths[type])
              ruler.to_disk(path_to_file)
                            
              return f"Ruler patterns saved successfully to {path_to_file}"
   

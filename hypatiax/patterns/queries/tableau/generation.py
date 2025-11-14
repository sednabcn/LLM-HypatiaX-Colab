import os
import pandas as pd
import matplotlib.pyplot as plt
import nltk
import re
import spacy
from nltk.tokenize import word_tokenize, sent_tokenize,wordpunct_tokenize

from spacy import displacy
from spacy.matcher import Matcher
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
              
              p_d = get_patterns(self.out_d, "vocab", nlp)
    
              patterns_tableau_desc = []

              # patterns to description - use .get() with default empty list
              p_d['CONJ'] = p_d.get('CCONJ', []) + p_d.get('SCONJ', [])
              p_d.pop('SCONJ', None)
              p_d.pop('CCONJ', None)
    
              p_d['VERB'] = p_d.get('VERB', []) + p_d.get('AUX', [])
              p_d.pop('AUX', None)
    
              p_d['PRON'] = p_d.get('PRON', []) + p_d.get('DET', [])
              p_d.pop('DET', None)
    
              # Safely handle 'X' key
              x_values = p_d.get('X', [])
              if x_values:
                     p_d['NOUN'] = [x for x in x_values if len(x_values) > 1 and x != x_values[1]] + p_d.get('NOUN', []) + ['dataset']
                     p_d['ADJ'] = [x_values[1]] + [x for x in p_d.get('ADJ', []) if x != 'dataset']
              else:
                     p_d['NOUN'] = p_d.get('NOUN', []) + ['dataset']
                     p_d['ADJ'] = [x for x in p_d.get('ADJ', []) if x != 'dataset']
    
              p_d['PROPN'] = ['Sepal Length', 'Sepal Width', 'Petal Length', 'Petal Width'] + p_d.get('PROPN', [])
              p_d.pop('X', None)
    
              patterns_tableau_desc = [{key: value} for (key, value) in p_d.items() if value]
              return patterns_tableau_desc

       def gen_patterns_tableau_formulas(self):
              
              p_t = get_patterns(self.out_f, "vocab", nlp)
              self.patterns_tableau_formulas = []
    
              p_t['ARG'] = ['[Sepal Length]', '[Sepal Width]', '[Petal Length]', '[Petal Width]', '[Species]']
              p_t['ARGN'] = ['Sepal Length', 'Sepal Width', 'Petal Length', 'Petal Width', 'Species']
              p_t['NOUN'] = ['month', 'TODAY', 'color', 'YEAR', 'versicolor', 'setosa', 'year', 'virginica']
              p_t['STOPWORDS'] = ['[Sepal', 'Sepal', '[Petal', 'Width]', 'Width', 'Petal', 'Length]', "'Se'", ':', 
                        '"virginica",', '"setosa",', '', '{', ')', '*', "'Setosa'", "'month', ", '4.0 AND',
                        '"setosa" AND', 'ica', "Iri", '!= 3.0', '"versicolor" AND', "Species STARTS WITH 'Se'",
                        "Length", '"Iri"']
    
              # Safely handle NUM
              num_values = p_t.get('NUM', [])
              p_t['NUM'] = [ff for ff in num_values if ff != 'TOP'] + ['1.5', '2.5', '4.5', '3.0', '3', '2.0', '5.0']
    
              # Safely handle ADP
              p_t['ADP'] = p_t.get('ADP', []) + ['to', 'AND', '>=', '<', '!=', '<=', '=', '>']
    
              # Safely handle ADV
              adv_values = p_t.get('ADV', [])
              p_t['ADV'] = [ff for ff in adv_values if ff != "SORT"] + ['highest to lowest', 'ASC', 'DESC', 'NULL', 'LEFT']
    
              # Safely handle ADJ
              adj_values = p_t.get('ADJ', [])
              p_t['ADJ'] = [ff for ff in adj_values if ff != 'SORTED']
    
              # Build ptt list
              ptt = (p_t.get('ARG', []) + p_t.get('NOUN', []) + p_t.get('NUM', []) + 
                     p_t.get('STOPWORDS', []) + p_t.get('ARGN', []) + p_t.get('ADV', []) + 
                     p_t.get('ADP', []) + p_t.get('ADJ', []))
    
              p_t['OPER'] = ['STARTS WITH']
              p_t['OPER'] += tok_formulas(self.data, ptt)
    
              # Safely handle list operations
              if 'LISTED' in p_t['OPER']:
                     p_t['OPER'][p_t['OPER'].index('LISTED')] = 'LISTED FROM'
    
              p_t['OPER'] += ['TOP BY']
              p_t['OPER'] += ['IF CONTAINS', 'BY']
    
              # Filter NOUN
              p_t['NOUN'] = [ff for ff in p_t.get('NOUN', []) if ff not in p_t.get('OPER', [])]
    
              # Remove unwanted keys
              keys_to_remove = ['STOPWORDS', 'X', 'AUX', 'CCONJ', 'INTJ', 'PROPN', 
                      'PART', 'PRON', 'SCONJ', 'VERB', 'PUNCT']
              for key in keys_to_remove:
                     p_t.pop(key, None)
    
              # patterns to formulas
              patterns_tableau_formulas = [{key: value} for (key, value) in p_t.items() if value]
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
                     'both': 'ruler_tableau_both.jsonl'
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
   

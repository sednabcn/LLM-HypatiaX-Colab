import os
import pandas as pd
from hypatiax.patterns.queries.tableau.generation import Generation_custom_tableau_patterns

stopwords=[]

def patterns_rules(data,ind):
        stopwords_desc= ['\\','Iri','Se','C','Sepal','ica','Length',"'s",'.',"'", 's', 'a','(',')','Petal','Distinct',"Width",',',"'","[","]"]
        stopwords_formulas=['\\','Iri','Se','C','Sepal','ica','Length',"'s",'.',"'", 's', 'a','(',')','Petal','Distinct','distinct',"Width",',','BY','by','from',"[","]"]
        stopwords=[stopwords_desc,stopwords_formulas]
        if ind=="S":
            return Generation_custom_tableau_patterns(data,stopwords).rules_tableau_desc
        elif ind=="F":
            return Generation_custom_tableau_patterns(data,stopwords).rules_tableau_formulas
        else:
            pass
  
if __name__=='__main__':
      import os  
      from importlib import resources
      path_data=resources.files('hypatiax.datasets.queries.tableau.training').joinpath('formulas.xlsx')
      
      for ind in ["S","F"]:
           print(patterns_rules(path_data,ind))
           print("============================")


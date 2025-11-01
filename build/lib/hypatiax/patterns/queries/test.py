import os
import pandas as pd
from hypatiax.patterns.queries.generation import Generation_custom_queries_patterns

stopwords=[]

def patterns_gen(data,ind):
            stopwords_desc= ['\\','Iri','Se','C','Sepal','ica','Length',"'s",'.',"'", 's', 'a','(',')','Petal','Distinct',"Width",',',"'","[","]"]
            stopwords_formulas=['\\','Iri','Se','C','Sepal','ica','Length',"'s",'.',"'", 's', 'a','(',')','Petal','Distinct','distinct',"Width",',','BY','by','from',"[","]"]
            stopwords=[stopwords_desc,stopwords_formulas]
            if ind=="S":
                return Generation_custom_queries_patterns(data,stopwords).patterns_queries_desc
            elif ind=="F": 
                return Generation_custom_queries_patterns(data,stopwords).patterns_queries_formulas
            else:
                pass
    

if __name__=='__main__':
      from importlib import resources
      path_data=resources.files('hypatiax.datasets.queries.training').joinpath('formulas.xlsx')
      for ind in ["S","F"]:
           print(patterns_gen(path_data,ind))
 


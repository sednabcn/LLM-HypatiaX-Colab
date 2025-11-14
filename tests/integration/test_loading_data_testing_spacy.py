import os
from importlib import resources
from hypatiax.utils.files_local import load
import pandas as pd
#Test1:

dir_path=resources.files('hypatiax.datasets.queries.tableau').joinpath('testing_spacy')

if os.path.exists(dir_path):
    n=1
    for root,dirs,files in os.walk(dir_path):   
        for filename in files:
              if filename.lower().endswith('.json') or \
              filename.lower().endswith('.spacy'):
                 full_path = os.path.join(root, filename)
                 df = load(full_path,style='entity')
                 if df is not None:
                    for item in df:
                        print(item)
                    print("=================================")
                    print(f"Test{n} passed")
                    print("=================================")
                    n +=1
                 else:
                    print(f"Test{n} failed to load data.")
                    n += 1
else:
    print("Directory not found")


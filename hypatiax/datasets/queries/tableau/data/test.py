import os
from importlib import resources

import pandas as pd

from hypatiax.utils.files_local import load

#Test1:



dir_path=resources.files('hypatiax.datasets.queries.tableau').joinpath('data')

if os.path.exists(dir_path):
    n=1
    for root,dirs,files in os.walk(dir_path):
        for filename in files:
              if filename.lower().endswith('.csv') or \
              filename.lower().endswith('.xlsx') \
              or filename.lower().endswith('.xls'):
                 full_path = os.path.join(root, filename)
                 df = load(full_path)
                 if df is not None:
                    print(df.head(5))
                    print("=================================")
                    print(f"Test{n} passed")
                    print("=================================")
                 else:
                    print(f"Test{n} failed to load data.")
              n += 1
        else:
    print("Directory not found")

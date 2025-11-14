import pandas as pd
import os
from hypatiax.utils.path_manager import PathManager

# Initialize once
pm = PathManager("LLM-HypatiaX-OLD")

# Walk your directory
results = pm.walk_directory("hypatiax", "datasets", "queries", "tableau", "testing")

n=1
for root, dirs, files in results:
  for filename in files:
      if filename.endswith('.xlsx'):
          full_path = os.path.join(root, filename)
          df=pd.read_excel(full_path,index_col=0)
          df=df.rename(columns={"Formula (Tableau)":"Formulas"})
          print(df.columns)
          df.to_excel(filename)
          dg=pd.read_excel(filename,index_col=0)
          print(dg.head(3))
          print("n=",n,"file=",filename)
          n+=1

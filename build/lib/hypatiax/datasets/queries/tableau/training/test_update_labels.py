import pandas as pd
import os
n=1
for root,dirs,files in os.walk('.'):
  for filename in files:
      if filename.endswith('.xlsx'):
          df=pd.read_excel(filename,index_col=0)
          df=df.rename(columns={"Formula (Tableau)":"Formulas"})
          print(df.columns)
          df.to_excel(filename)
          dg=pd.read_excel(filename,index_col=0)
          print(dg.head(3))
          print("n=",n,"file=",filename)
          print(dg.columns)
          n+=1

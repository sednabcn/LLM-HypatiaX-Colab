# Use the MASTER dataset for comprehensive analysis
import pandas as pd

df = pd.read_csv('data/processed/master_dataset_20251216_194946.csv')

print(df.shape)
print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"Source files: {df['source_path'].unique()}")

# Or use individual merged files for specific analysis
il_cases = pd.read_csv('data/processed/il_test_cases_merged_20251216_194946.csv')
uniswap = pd.read_csv('data/processed/uniswap_scenarios_merged_20251216_194946.csv')


## 📁 Your Unique Dataset Location:
# ```
# data/processed/master_dataset_20251216_194946.csv  ← Use this one!

import pandas as pd
from hypatiax.utils.files_local import load

def combined_process(path_data, path_out, option=None):
    """
    Combined process of Description and Formulas.

    Args:
        path_data (str): Path to the input data file.
        path_out (str): Path where the output file should be saved.
        option (None, optional): Additional options if any.

    Returns:
        pd.DataFrame: DataFrame with an additional column 'both' combining the first two columns.
    """
    filename, ext = path_data.split('/')[-1].split('.')
    data = load(path_data)
    nrows,ncols=data.shape
    if isinstance(data, pd.DataFrame) and len(data.columns) == 2:
        # Combine the two columns with a colon in between
        data['Combined'] = data[data.columns[0]] + ' : ' + data[data.columns[1]]
        assert data.shape==(nrows,ncols+1),"Data does not have the expected shape."
    # Saving data to disk in the appropriate format
    if ext in ['xls', 'xlsx']:
        output_path = f'{path_out}/{filename}_combined.xlsx'
        data.to_excel(output_path)
    elif ext == 'csv':
        output_path = f'{path_out}/{filename}_combined.csv'
        data.to_csv(output_path)
    
    # The function currently does not move the file, just saves it to a new location
    return data




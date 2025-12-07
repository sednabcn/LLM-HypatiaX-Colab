from pathlib import Path

import pandas as pd

from hypatiax.utils.files import FilesManager


class CombinedData:
    def __init__(self, modules, domain, sub_domains, actions, dataset_type=None):
        self.modules = modules
        self.domain = domain
        self.sub_domains = sub_domains
        self.actions = actions
        self.dataset_type = dataset_type

    def combined_process(self, filename, path_out, option=None):
        """
        Combined process of Description and Formulas.

        Args:
            filename (str): Name of the input data file.
            path_out (str): Path where the output file should be saved.
            option (None, optional): Additional options if any.

        Returns:
            pd.DataFrame: DataFrame with an additional column 'both' combining the first two columns.
        """
        filename_, ext = filename.split(".")
        F = FilesManager(self.modules, self.domain, self.sub_domains, self.actions)
        data = F.load(filename)
        nrows, ncols = data.shape

        if isinstance(data, pd.DataFrame) and len(data.columns) == 2:
            # Combine the two columns with a colon in between
            data["Combined"] = data[data.columns[0]] + " : " + data[data.columns[1]]
            assert data.shape == (nrows, ncols + 1), "Data does not have the expected shape."

        # Saving data to disk in the appropriate format
        output_path = Path(path_out) / f"{filename_}_combined.{ext}"
        if ext in ["xls", "xlsx"]:
            data.to_excel(output_path)
        elif ext == "csv":
            data.to_csv(output_path)

        return data


if __name__ == "__main__":
    from importlib import resources

    # Assuming 'datasets.queries.training' is a valid Python package
    Cd = CombinedData("datasets", "queries", "tableau", "training")
    file_path = resources.files("hypatiax.datasets.queries.tableau.training").joinpath("")
    # output_path = Path.cwd()  # Adjust the output directory as needed
    Cd.combined_process("formulas.xlsx", file_path)

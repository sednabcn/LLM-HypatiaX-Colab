import os

import pandas as pd

from hypatiax.utils.utils import dataset_normalized


# data in excel format !!Be careful
def get_normalization(path_data, name_col):
    return dataset_normalized(path_data, name_col)


if __name__ == "__main__":
    from importlib import resources

    # training test
    path_to_file = resources.files(
        "hypatiax.datasets.queries.tableau.training"
    ).joinpath("formulas.xlsx")
    df = get_normalization(path_to_file, "Formulas")
    df.to_excel(path_to_file)
    # testing test
    path_to_test_file = resources.files(
        "hypatiax.datasets.queries.tableau.testing"
    ).joinpath("formulas_test.xlsx")
    dg = get_normalization(path_to_test_file, "Formulas")
    dg.to_excel(path_to_test_file)

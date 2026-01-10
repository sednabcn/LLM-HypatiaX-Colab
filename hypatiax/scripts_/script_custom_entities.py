import logging
import os
from importlib import resources

import pandas as pd

from hypatiax.custom_entities.ner_entity import Custom_ner_entities
from hypatiax.utils.utils import (
    save_data_to_json,
    save_spacy_training_data,
    save_spacy_training_data_to_json,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_ner_entity(path_data, path_entity_name, column_name):
    try:
        data = pd.read_excel(path_data, index_col=0)
        return Custom_ner_entities(data, path_entity_name, column_name).get_entity()
    except Exception as e:
        logging.error(f"Failed to get NER entity from {path_data} with error: {e}")
        return None, None


def process_ner_data(
    domain,
    sub_domain,
    dataset_file_dir,
    dataset_file,
    ner_type,
    column_name,
    data_spacy_dir,
    size_data_spacy_file,
):
    try:

        # Resolving the file paths for input data based on datasets
        dataset_path = resources.files(
            f"hypatiax.datasets.{domain}.{sub_domain}.{dataset_file_dir}"
        ).joinpath(f"{dataset_file}.xlsx")

        # Resolving the file paths for entity models based on data_spacy
        entity_path = resources.files(
            f"hypatiax.data_spacy.{domain}.{sub_domain}"
        ).joinpath(f"ner_{domain}_{ner_type}")
        if ner_type == "both":
            entity_path = resources.files(
                f"hypatiax.data_spacy.{domain}.{sub_domain}"
            ).joinpath(f"ner_{domain}")

        print(f"Processing NER type {ner_type} for file {dataset_file}")
        entities, train_data = get_ner_entity(dataset_path, entity_path, column_name)

        for item in train_data:
            print(item)

        # spacy_dir_paths
        if data_spacy_dir == "training_spacy":
            file_cap = "Train"
        elif data_spacy_dir == "testing_spacy":
            file_cap = "Test"
        else:
            pass

        # output files
        file_output = f"{file_cap}_{sub_domain}_{ner_type}_{size_data_spacy_file}_data"
        vocab_output = (
            f"vocab_{sub_domain}_{ner_type}_{column_name}_{size_data_spacy_file}"
        )

        # save to data_spacy/queries/training_spacy(or testing_spacy) dir
        spacy_dir_path = resources.files(
            f"hypatiax.data_spacy.{domain}.{sub_domain}.{data_spacy_dir}"
        )

        print(f"Saving {file_output} to {spacy_dir_path}")
        save_spacy_training_data(spacy_dir_path, train_data, file_output, entity_path)

        # save to data_spacy/queries/vocab
        spacy_dir_path_vocab = resources.files(
            f"hypatiax.data_spacy.{domain}.{sub_domain}.vocab"
        )
        vocab_output_path = os.path.join(spacy_dir_path_vocab, vocab_output)

        print(f"Saving {vocab_output} to {spacy_dir_path_vocab}")
        save_data_to_json(vocab_output_path, entities)

        # save to datasets/queries/training(or testing) dir
        dataset_spacy_dir_path = resources.files(
            f"hypatiax.datasets.{domain}.{sub_domain}.{data_spacy_dir}"
        )

        print(f"Saving {file_output} to {dataset_spacy_dir_path}")
        save_spacy_training_data_to_json(
            dataset_spacy_dir_path, train_data, file_output
        )

    except Exception as e:
        logging.error(f"Failed to get NER entity from {path_data} with error: {e}")
    return None, None


def main(domain, sub_domain):
    try:

        # Process data for different types and files
        process_ner_data(
            domain,
            sub_domain,
            "training",
            "formulas_nor_combined",
            "desc",
            "Description",
            "training_spacy",
            "sm",
        )
        print("Passed 1")
        process_ner_data(
            domain,
            sub_domain,
            "testing",
            "formulas_test_nor_combined",
            "desc",
            "Description",
            "testing_spacy",
            "sm",
        )
        print("Passed 2")

        process_ner_data(
            domain,
            sub_domain,
            "training",
            "gformulas_nor_combined",
            "desc",
            "Description",
            "training_spacy",
            "bsm",
        )
        print("Passed 3")

        process_ner_data(
            domain,
            sub_domain,
            "training",
            "formulas_nor_combined",
            "formulas",
            "Formulas",
            "training_spacy",
            "sm",
        )
        print("Passed 4")
        process_ner_data(
            domain,
            sub_domain,
            "testing",
            "formulas_test_nor_combined",
            "formulas",
            "Formulas",
            "testing_spacy",
            "sm",
        )
        print("Passed 5")
        process_ner_data(
            domain,
            sub_domain,
            "training",
            "gformulas_nor_combined",
            "formulas",
            "Formulas",
            "training_spacy",
            "bsm",
        )
        print("Passed 6")

        process_ner_data(
            domain,
            sub_domain,
            "training",
            "formulas_nor_combined",
            "both",
            "Combined",
            "training_spacy",
            "dsm",
        )
        print("Passed 7")
        process_ner_data(
            domain,
            sub_domain,
            "testing",
            "formulas_test_nor_combined",
            "both",
            "Combined",
            "testing_spacy",
            "sm",
        )
        print("Passed 8")
        process_ner_data(
            domain,
            sub_domain,
            "training",
            "gformulas_nor_combined",
            "both",
            "Combined",
            "training_spacy",
            "bdsm",
        )
    except Exception as e:
        logging.error(f"Main execution failed: {e}")
        print("End")


if __name__ == "__main__":
    domain = "queries"  # Set your domain
    sub_domain = "tableau"
    main(domain, sub_domain)

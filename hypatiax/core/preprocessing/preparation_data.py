import numpy as np
from importlib import resources
from sklearn.model_selection import train_test_split
from hypatiax.utils.files import FilesManager
from hypatiax.custom_entities.ner_entity import Custom_ner_entities
from hypatiax.utils.data_utils import save_spacy_training_data_to_json  # Add this import

def split_data(data, test_size, val_data, val_ratio):
    """
    Helper function to split data into training, validation, and testing sets.
    """
    X_train, X_test = train_test_split(data, test_size=test_size)
    if val_data:
        X_train, X_val = train_test_split(X_train, test_size=val_ratio)
        return X_train, X_val, X_test
    return X_train, None, X_test

def preparation_data(modules, domain, sub_domain, actions, filename, dtype, sizefile='sm', 
                    test_size=0.2, task_type='single', ner_entity=None, 
                    dataset_normalized=None, val_data=False, option=None):
    """
    Main entry point for data preparation.
    
    Parameters:
        modules (str): Module name.
        domain (str): Domain name.
        sub_domain (str): Sub-domain name.
        actions (str): Specific action.
        filename (str): Filename to load.
        dtype (str): Data type (desc, formulas, combined).
        sizefile (str): File size ('sm' or 'bg').
        test_size (float): Fraction for test set.
        task_type (str): 'single' or 'multitask'.
        ner_entity (str): NER entity type.
        dataset_normalized: Dataset normalization flag.
        val_data (bool): Whether to create validation set.
        option (str): Data handling option ('None', 'split', 'build').
    
    Returns:
        Data splits (X_train, X_val, X_test) or (X_train, X_test).
    """
    if task_type == 'single':        
        return prepare_unlabeled_data_single(
            modules, domain, sub_domain, actions, filename, dtype, 
            sizefile, test_size, ner_entity, dataset_normalized, val_data, option
        )
    elif task_type == 'multitask':
        return prepare_unlabeled_data_multitask(
            modules, domain, sub_domain, actions, filename, dtype, 
            sizefile, test_size, ner_entity, dataset_normalized, val_data, option
        )
    else:
        raise ValueError(f"Invalid task_type: {task_type}. Must be 'single' or 'multitask'.")

def prepare_unlabeled_data_multitask(modules, domain, sub_domain, actions, filename, dtype, 
                                     sizefile='sm', test_size=0.2, ner_entity=None, 
                                     dataset_normalized=None, val_data=False, option=None):
    """
    Prepare data for multitask learning scenarios.
    
    Parameters:
        modules (str): Module name.
        domain (str): Domain name.
        sub_domain (str): Sub-domain name.
        actions (str): Specific action.
        filename (str): Filename to load for 'build' option.
        dtype (str): Type of NER entity (desc, formulas, combined).
        sizefile (str): 'sm' or 'bg'.
        test_size (float): Fraction of data to be used as test set.
        ner_entity (str): Spacy entity like ner_desc, ner_formulas, ner_both.
        dataset_normalized: Dataset normalization flag.
        val_data (bool): Indicates if validation data should be prepared.
        option (str): Option to manage data ('None', 'split', 'build').
    
    Returns:
        Tuple of datasets depending on `val_data` parameter.
    """
    Tr = FilesManager(modules, domain, sub_domain, 'training_spacy')
    T = FilesManager(modules, domain, sub_domain, 'testing_spacy')
    V = FilesManager(modules, domain, sub_domain, 'validation_spacy')

    if option == 'None':
        # Load predefined datasets
        X_train = [
            Tr.load(f'Train_{sub_domain}_desc_{sizefile}_data.json', style='entity'),
            Tr.load(f'Train_{sub_domain}_formulas_{sizefile}_data.json', style='entity')
        ]
        X_test = T.load(f'Test_{sub_domain}_both_{sizefile}_data.json', style='entity')

        if val_data:
            X_val = [
                V.load(f'Val_{sub_domain}_desc_{sizefile}_data.json', style='entity'),
                V.load(f'Val_{sub_domain}_formulas_{sizefile}_data.json', style='entity')
            ]
            return X_train, X_val, X_test

        return X_train, None, X_test

    elif option in ["split", "build"]:
        if option == "split":
            data_desc = Tr.load(f'Train_{sub_domain}_desc_{sizefile}_data.json', style='entity')
            data_formulas = Tr.load(f'Train_{sub_domain}_formulas_{sizefile}_data.json', style='entity')
        elif option == "build":
            F = FilesManager(modules, domain, sub_domain, actions)
            try:
                data = F.load(filename)
                entity_path = f"{modules}/{domain}/{sub_domain}/ner_{sub_domain}_desc"
                _, data_desc = Custom_ner_entities(data, entity_path, 'Description').get_entity()
                entity_path = f"{modules}/{domain}/{sub_domain}/ner_{sub_domain}_formulas"
                _, data_formulas = Custom_ner_entities(data, entity_path, 'Formulas').get_entity()
                if 'Combined' in data.columns:
                    entity_path = f"{modules}/{domain}/{sub_domain}/ner_{sub_domain}"
                    _, data_combined = Custom_ner_entities(data, entity_path, 'Combined').get_entity()
                    # Use combined data for formulas if available
                    data_formulas = data_combined
            except FileNotFoundError as e:
                print(f"Filename not found: {e}")
                return None, None, None
            except Exception as e:
                print(f"Error loading data: {e}")
                return None, None, None

        # Split data
        val_ratio = 0.5 * test_size
        X_train_0, X_val_0, X_test_0 = split_data(data_desc, test_size, val_data, val_ratio)
        X_train_1, X_val_1, X_test_1 = split_data(data_formulas, test_size, val_data, val_ratio)

        X_train = [X_train_0, X_train_1]
        X_test = [X_test_0, X_test_1]
        
        if val_data:
            X_val = [X_val_0, X_val_1]
            
            # Output files
            file_output = f'Valid_{sub_domain}_{sizefile}_data.json'
            # Save to datasets/queries/tableau/validation_spacy dir
            json_dir_path = resources.files(f'hypatiax.datasets.{domain}.{sub_domain}.validation_spacy')
            print(f"Saving {file_output} to {json_dir_path}")
            save_spacy_training_data_to_json(json_dir_path, X_val, file_output)

            return X_train, X_val, X_test

        return X_train, None, X_test

    else:
        raise ValueError(f"Invalid option: {option}. Must be 'None', 'split', or 'build'.")


def prepare_unlabeled_data_single(modules, domain, sub_domain, actions, filename, dtype, 
                                  sizefile='sm', test_size=0.2, ner_entity=None, 
                                  dataset_normalized=None, val_data=False, option=None):
    """
    Prepare data for single-task learning.
    
    Parameters:
        modules (str): Module name.
        domain (str): Domain name.
        sub_domain (str): Sub-domain name.
        actions (str): Specific action.
        filename (str): Filename to load for 'build' option.
        dtype (str): Data type (desc, formulas, combined).
        sizefile (str): 'sm' or 'bg'.
        test_size (float): Fraction of data to be used as test set.
        ner_entity (str): Spacy entity like ner_desc, ner_formulas, ner_both.
        dataset_normalized: Dataset normalization flag.
        val_data (bool): Indicates if validation data should be prepared.
        option (str): Option to manage data ('None', 'split', 'build').
    
    Returns:
        Data splits depending on `val_data` parameter.
    """
    F = FilesManager(modules, domain, sub_domain, actions)
    Tr = FilesManager(modules, domain, sub_domain, 'training_spacy')
    T = FilesManager(modules, domain, sub_domain, 'testing_spacy')
    V = FilesManager(modules, domain, sub_domain, 'validation_spacy')
    
    if option == 'None':
        # Load predefined datasets
        X_train = Tr.load(f'Train_{sub_domain}_{dtype}_{sizefile}_data.json', style='entity')
        X_test = T.load(f'Test_{sub_domain}_{dtype}_{sizefile}_data.json', style='entity')
        if val_data:
            X_val = V.load(f'Val_{sub_domain}_{dtype}_{sizefile}_data.json', style='entity')
            return X_train, X_val, X_test
        return X_train, None, X_test
    
    elif option == "split":
        # Load data for splitting
        data = Tr.load(f'Train_{sub_domain}_{dtype}_{sizefile}_data.json', style='entity')
        X = data
        X_train, X_test = train_test_split(X, test_size=test_size)
        if val_data:
            X_train, X_val = train_test_split(X_train, test_size=0.5 * test_size)
            return X_train, X_val, X_test
        return X_train, None, X_test
    
    elif option == "build":
        # Load and potentially transform/build features for the data
        try:
            data = F.load(filename)
            # Assume entity_path and Custom_ner_entities can be correctly set up
            entity_path = f"{modules}/{domain}/{sub_domain}/ner_{sub_domain}"
            _, data_ = Custom_ner_entities(data, entity_path, 'Combined').get_entity()

            # Add any specific transformations or feature engineering steps here
            print("Building features...")
            
        except FileNotFoundError as e:
            print(f"Filename not found: {e}")
            return None, None, None
        except Exception as e:
            print(f"Error loading data: {e}")
            return None, None, None
            
        X = data_
        X_train, X_test = train_test_split(X, test_size=test_size)
        if val_data:
            X_train, X_val = train_test_split(X_train, test_size=0.5 * test_size)
            # Output files
            file_output = f'Valid_{sub_domain}_{sizefile}_data.json'
            # Save to datasets/queries/tableau/validation_spacy dir
            json_dir_path = resources.files(f'hypatiax.datasets.{domain}.{sub_domain}.validation_spacy')
            print(f"Saving {file_output} to {json_dir_path}")
            save_spacy_training_data_to_json(json_dir_path, X_val, file_output)
            
            return X_train, X_val, X_test
        return X_train, None, X_test

    else:
        raise ValueError(f"Invalid option: {option}. Must be 'None', 'split', or 'build'.")

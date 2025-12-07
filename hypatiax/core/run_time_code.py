from importlib import resources

import spacy
from spacy.training import Example

from hypatiax.core.deployment.evaluation_model import evaluate_spacy_model
from hypatiax.core.evaluation.testing_model import test_spacy_model
from hypatiax.core.preprocessing.preparation_data import (
    preparation_data,
    preparation_unlabeled_multitask_data,
    preparation_unlabeled_single_data,
)
from hypatiax.core.training.training_spacy import Training

i = 1
# Define configuration for data preparation
config_data_preparation = {
    "modules": "datasets",
    "domain": "queries",
    "sub_domain": "tableau",
    "actions": "training",
    "filename": "formulas_nor.xlsx",
    "dtype": "desc",
    "sizefile": "sm",
    "test_size": 0.2,
    "task_type": "single",
    "ner_entity": "ner_queries_desc",
    "dataset_normalized": None,
    "val_data": False,
    "option": None,
}
config_data_prep = pd.DataFrame.from_dict(config_data_preparation, columns=list(config_data_preparation.keys()))
config_path = resources.files("hypatiax.models.queries.tableau.model_configs").joinpath(f"config_data_preparation_{i}")
config_data_prep.to_csv(config_path)
# Preparing the Data
X_train, X_val, X_test = preparation_data(**config_data_preparation)

# Define configuration for model training
config_training = {
    "domain": "queries",
    "sub_domain": "tableau",
    "train_data": X_train,
    "dtype": "desc",
    "output_model": "Description_sm",
    "niter": 400,
    "drop": 0.5,
    "batchsize": 8,
    "patience": 10,
    "n_checkpoint": 100,
    "val_data": X_val,
    "option": None,
}
config_training = pd.DataFrame.from_dict(config_training, columns=list(config_training.keys()))
config_training_path = resources.files("hypatiax.models.queries.tableau.model_configs").joinpath(f"config_training_{i}")
config_data_prep.to_csv(config_training_path)

# Training the Model
trainer = Training(**config_training)
history, nlp = trainer.train()

# Save the trained model
trainer.save_model()
trainer.plot_history(history)

# Determine the appropriate entity path based on the dtype
if config_data_preparation["dtype"] == "both":
    entity_path = resources.files(
        f'hypatiax.data_spacy.{config_data_preparation["domain"]}.{config_data_preparation["sub_domain"]}'
    ).joinpath(f'ner_{config_data_preparation["sub_domain"]}')
else:
    entity_path = resources.files(
        f'hypatiax.data_spacy.{config_data_preparation["domain"]}.{config_data_preparation["sub_domain"]}'
    ).joinpath(f'ner_{config_data_preparation["sub_domain"]}_{config_data_preparation["dtype"]}')

# Validate the Model
validation_data = X_val
if X_val != None:
    evaluate_spacy_model(entity_path, validation_data)

# Evaluate the Model
test_data = X_test
test_spacy_model(entity_path, test_data)

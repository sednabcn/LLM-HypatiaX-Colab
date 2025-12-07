import time
from importlib import resources

import pandas as pd
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


def save_config(test_id,config,time_id):
        config_data_prep=pd.DataFrame.from_dict(config[0],columns=list(config[0].keys()))
        config_path=resources.files('hypatiax.models.queries.tableau.model_configs').joinpath(f'config_data_preparation_{test_id}_{time_id}')
        config_data_prep.to_csv(config_path)
        config_training=pd.DataFrame.from_dict(config[1],columns=list(config[1].keys()))
        config_training_path=resources.files('hypatiax.models.queries.tableau.model_configs').joinpath(f'config_training_{test_id}_{time_id}')
        config_data_prep.to_csv(config_training_path)


def run_test(test_id,config):
    """
    Simulate running a test given a configuration.
    Normally, you would call the appropriate functions and modules here based on the config.
    """
    # Placeholder for running a test
    print(f"Running test {test_id} with data_configuration: {config[0]} and training_config {config[1]}")
    # Example function calls (commented out because they are not defined)
    X_train, X_val, X_test = preparation_data(**config[0])

    # Update the training configuration with dynamic data
    config[1].update({'train_data': X_train, 'val_data': X_val})

    # Training the model
    trainer = Training(**config[1])
    history, nlp = trainer.train()

    # Save the trained model
    trainer.save_model()
    trainer.plot_history(history)

    # Determine the appropriate entity path based on the dtype
    ner_model_file=f'ner_{config[1]["sub_domain"]}_{config[1]["dtype"]}'
    if config[1]["dtype"] == "both":
          ner_model_file=f'ner_{config[1]["sub_domain"]}'
    entity_path = resources.files(f'hypatiax.data_spacy.{config[1]["domain"]}.{config[1]["sub_domain"]}').joinpath(ner_model_file)
    # return results
    results = {'test_id': test_id}
    if X_val is not None:
        results['validation_result'] = evaluate_spacy_model(entity_path, X_val)
    if X_test is not None:
        results['test_result'] = test_spacy_model(entity_path, X_test)

    return results

# Running all tests and collecting results
(year,month,day,hr,minutes,sec,_,_,_)=time.localtime()
time_proc=f'{year}_{month)_{day}_{hr}_{minutes}_{sec}'

# Example configurations for each test
test_configurations={}
test_configurations =
# single-non-split-desc-sm,
{'1':[{'modules': 'datasets', 'domain': 'queries','sub_domain':'tableau','actions':'training','filename':'formulas_nor.xlsx', 'dtype': 'desc','sizefile': 'sm','test_size': 0.2, 'task_type':'single','ner_entity': 'ner_queries_desc','dataset_normalized':None,'val_data':False, 'option':None},{'domain': 'queries','sub_domain':'tableau','train_data':None,'dtype':'desc','output_model_name':'Description_sm','niter': 400,'drop': 0.5,'batchsize': 8,'patience': 10,'n_checkpoint': 100,'val_data':None,'option': None}],
 '2':[{'modules': 'datasets', 'domain': 'queries','sub_domain':'tableau','actions':'training','filename':'formulas_nor.xlsx', 'dtype': 'formulas','sizefile': 'sm','test_size': 0.2,'task_type':'single','ner_entity': 'ner_queries_formulas','dataset_normalized':None,'val_data':False, 'option':None},{'domain': 'queries','sub_domain':'tableau','train_data':None,'dtype':'formulas','output_model_name':'Formulas_sm','niter': 400,'drop': 0.5,'batchsize': 8,'patience': 10,'n_checkpoint': 100,'val_data:None','option': None}],
# multitask-option 1-sm
'3':[{'modules': 'datasets', 'domain': 'queries','sub_domain':'tableau','actions':'training','filename':'formulas_nor_combined.xlsx', 'dtype': 'both','sizefile': 'sm','test_size': 0.2,'task_type':'multitask','ner_entity': 'ner_queries','dataset_normalized':None,'val_data':False,'option':None},{'domain': 'queries','sub_domain':'tableau','train_data':None,'dtype':'both','output_model_name':'Multitask_1_sm','niter': 400,'drop': 0.5,'batchsize': 8,'patience': 10,'n_checkpoint': 100,'val_data':None,'option':1}],
# multitask-option 2-sm
'4':[{'modules': 'datasets', 'domain': 'queries','sub_domain':'tableau','actions':'training','filename':'formulas_nor_combined.xlsx', 'dtype': 'both','sizefile': 'sm','test_size': 0.2,'task_type':'multitask','ner_entity': 'ner_queries','dataset_normalized':None,'val_data':False,'option':None},{'domain': 'queries','sub_domain':'tableau','train_data':None,'dtype':'both','output_model_name':'Multitask_1_sm','niter': 400,'drop': 0.5,'batchsize': 8,'patience': 10,'n_checkpoint': 100,'val_data':None,'option':1}],
# single -non-split-both -ner-queries-sm
'5':[{'modules': 'datasets', 'domain': 'queries','sub_domain':'tableau','actions':'training','filename':'formulas_nor_combined.xlsx', 'dtype': 'both','sizefile': 'sm','test_size': 0.2,'task_type':'single','ner_entity': 'ner_queries','dataset_normalized':None,'val_data':False,'option':None},{'domain': 'queries','sub_domain':'tableau','train_data':None,'dtype':'both','output_model_name':'Combined_sm','niter': 400,'drop': 0.5,'batchsize': 8,'patience': 10,'n_checkpoint': 100,'val_data':None,'option': None}],
#single-splitting-both-ner-queries-sm
'6':[{'modules': 'datasets', 'domain': 'queries','sub_domain':'tableau','actions':'training','filename':'formulas_nor_combined.xlsx', 'dtype': 'both','sizefile': 'sm','test_size': 0.2,'task_type':'single','ner_entity': 'ner_queries','dataset_normalized':None,'val_data':True,'option':'split'},{'domain': 'queries','sub_domain':'tableau','train_data':None,'dtype':'both','output_model_name':'Combined_sm','niter': 400,'drop': 0.5,'batchsize': 8,'patience': 10,'n_checkpoint': 100,'val_data':None,'option': None}],
# single-split-desc-bsm
'7':[{'modules': 'datasets', 'domain': 'queries','sub_domain':'tableau','actions':'training','filename':'gformulas_nor_combined.xlsx', 'dtype': 'desc','sizefile': 'bsm','test_size': 0.2,'task_type':'single','ner_entity': 'ner_queries_desc','dataset_normalized':None,'val_data':True,'option':'split'},{'domain': 'queries','sub_domain':'tableau','train_data':None,'dtype':'desc','output_model_name':'Combined_desc_bsm','niter': 400,'drop': 0.5,'batchsize': 8,'patience': 10,'n_checkpoint': 100,'val_data':None,'option': None}],
# single-split-formulas-bsm
'8':[{'modules': 'datasets', 'domain': 'queries','sub_domain':'tableau','actions':'training','filename':'gformulas_nor_combined.xlsx', 'dtype': 'formulas', 'sizefile': 'bsm','test_size': 0.2,'task_type':'single','ner_entity': 'ner_queries_formulas','dataset_normalized':None,'val_data':True,'option':'split'},{'domain': 'queries','sub_domain':'tableau','train_data':None,'dtype':'formulas','output_model_name':'Combined_formulas_bsm','niter': 400,'drop': 0.5,'batchsize': 8,'patience': 10,'n_checkpoint': 100,'val_data':None,'option': None}],
# multitask-option 1-bsm
'9':[{'modules': 'datasets', 'domain': 'queries','sub_domain':'tableau','actions':'training','filename':'gformulas_nor_combined.xlsx', 'dtype': 'both', 'sizefile': 'bsm','test_size': 0.2,'task_type':'multitask','ner_entity': 'ner_queries','dataset_normalized':None,'val_data':True,'option':'split'},{'domain': 'queries','sub_domain':'tableau','train_data':None,'dtype':'both','output_model_name':'Multitask_1_bsm','niter': 400,'drop': 0.5,'batchsize': 8,'patience': 10,'n_checkpoint': 100,'val_data':None,'option':1}],
# multitask-option 2-bsm
'10':[{'modules': 'datasets', 'domain': 'queries','sub_domain':'tableau','actions':'training','filename':'gformulas_nor_combined.xlsx', 'dtype': 'both','sizefile': 'bsm', 'test_size': 0.2,'task_type':'multitask','ner_entity': 'ner_queries','dataset_normalized':None,'val_data':True, 'option':'split'},{'domain': 'queries','sub_domain':'tableau','train_data':None,'dtype':'both','output_model_name':'Multitask_2_bsm','niter': 400,'drop': 0.5,'batchsize': 8,'patience': 10,'n_checkpoint': 100,'val_data':None,'option':2}],
# single-split-both-bsm
'11':[{'modules': 'datasets', 'domain': 'queries','sub_domain':'tableau','actions':'training','filename':'gformulas_nor_combined.xlsx', 'dtype': 'both','sizefile': 'bsm', 'test_size': 0.2,'task_type':'single','ner_entity': 'ner_queries','dataset_normalized':None,'val_data':True,'option':'split'},{'domain': 'queries','sub_domain':'tableau','train_data':None,'dtype':'both','output_model_name':'Combined_both_bsm','niter': 400,'drop': 0.5,'batchsize': 8,'patience': 10,'n_checkpoint': 100,'val_data':None,'option': None}]
}

results = []
 for id,config in test_configurations.items():
    result = run_test(id,config)
    results.append(result)
    run_save_config(id,config,time_proc)

# Optionally convert results into a DataFrame for better visualization and analysis
results_df = pd.DataFrame(results)
results_df.to_csv(f'results_val_test_{time_proc}')
print(results_df)

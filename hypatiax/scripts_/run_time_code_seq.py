import time
from importlib import resources
from pathlib import Path

import pandas as pd
import spacy
from spacy.training import Example

from hypatiax.core.deployment.evaluation_model import evaluate_spacy_model
from hypatiax.core.evaluation.testing_model import test_spacy_model
from hypatiax.core.preprocessing.preparation_data import preparation_data
from hypatiax.core.training.training_spacy import Training


def save_config(test_id, config, time_id):
    """
    Save data preparation and training configurations to CSV files.

    Args:
        test_id (str): Test identifier
        config (list): List containing [data_prep_config, training_config]
        time_id (str): Timestamp identifier
    """
    try:
        # Save data preparation config
        config_data_prep = pd.DataFrame([config[0]])  # Wrap in list for single row
        config_path = resources.files(
            "hypatiax.models.queries.tableau.model_configs"
        ).joinpath(f"config_data_preparation_{test_id}_{time_id}.csv")
        config_data_prep.to_csv(config_path, index=False)
        print(
            f"  ✓ Saved data prep config: config_data_preparation_{test_id}_{time_id}.csv"
        )

        # Save training config (exclude non-serializable data)
        config_training_save = {
            k: v for k, v in config[1].items() if k not in ["train_data", "val_data"]
        }
        config_training = pd.DataFrame([config_training_save])  # Wrap in list
        config_training_path = resources.files(
            "hypatiax.models.queries.tableau.model_configs"
        ).joinpath(f"config_training_{test_id}_{time_id}.csv")
        config_training.to_csv(config_training_path, index=False)  # Fixed variable name
        print(f"  ✓ Saved training config: config_training_{test_id}_{time_id}.csv")

    except Exception as e:
        print(f"  ✗ Error saving config for test {test_id}: {e}")


def run_test(test_id, config):
    """
    Run a complete training and evaluation test given a configuration.

    Args:
        test_id (str): Test identifier
        config (list): List containing [data_prep_config, training_config]

    Returns:
        dict: Results containing test_id, validation and test scores
    """
    print(f"\n{'='*70}")
    print(f"RUNNING TEST {test_id}")
    print(f"{'='*70}")
    print(
        f"Data Config: dtype={config[0]['dtype']}, sizefile={config[0]['sizefile']}, "
        f"task_type={config[0]['task_type']}"
    )
    print(
        f"Training Config: model={config[1]['output_model_name']}, "
        f"niter={config[1]['niter']}, option={config[1].get('option', None)}"
    )

    results = {"test_id": test_id, "status": "failed"}

    try:
        # Step 1: Prepare data
        print("\n[1/4] Preparing data...")
        X_train, X_val, X_test = preparation_data(**config[0])
        print(f"  ✓ Train samples: {len(X_train) if X_train else 0}")
        print(f"  ✓ Val samples: {len(X_val) if X_val else 0}")
        print(f"  ✓ Test samples: {len(X_test) if X_test else 0}")

        # Step 2: Update training configuration with dynamic data
        config[1].update({"train_data": X_train, "val_data": X_val})

        # Step 3: Train the model
        print("\n[2/4] Training model...")
        trainer = Training(**config[1])
        history, nlp = trainer.train()
        print(f"  ✓ Training completed")

        # Step 4: Save the trained model
        print("\n[3/4] Saving model...")
        model_path = trainer.save_model()
        print(f"  ✓ Model saved")

        try:
            trainer.plot_history(history)
            print(f"  ✓ Training history plotted")
        except Exception as e:
            print(f"  ⚠ Could not plot history: {e}")

        # Determine the model path for evaluation
        model_base_path = resources.files(
            f'hypatiax.models.{config[1]["domain"]}.{config[1]["sub_domain"]}'
        )
        model_full_path = str(model_base_path.joinpath(config[1]["output_model_name"]))

        # Step 5: Evaluate
        print("\n[4/4] Evaluating model...")

        # Validation
        if X_val is not None and len(X_val) > 0:
            try:
                print("  Running validation...")
                validation_result = evaluate_spacy_model(model_full_path, X_val)
                results["validation_result"] = validation_result
                results["val_precision"] = validation_result.get("ents_p", 0.0)
                results["val_recall"] = validation_result.get("ents_r", 0.0)
                results["val_f1"] = validation_result.get("ents_f", 0.0)
                print(f"  ✓ Validation F1: {results['val_f1']:.4f}")
            except Exception as e:
                print(f"  ✗ Validation error: {e}")
                results["validation_error"] = str(e)
        else:
            print("  ⚠ No validation data available")
            results["validation_result"] = None

        # Testing
        if X_test is not None and len(X_test) > 0:
            try:
                print("  Running testing...")
                test_result = test_spacy_model(model_full_path, X_test)
                results["test_result"] = test_result
                results["test_precision"] = test_result.get("ents_p", 0.0)
                results["test_recall"] = test_result.get("ents_r", 0.0)
                results["test_f1"] = test_result.get("ents_f", 0.0)
                print(f"  ✓ Test F1: {results['test_f1']:.4f}")
            except Exception as e:
                print(f"  ✗ Testing error: {e}")
                results["test_error"] = str(e)
        else:
            print("  ⚠ No test data available")
            results["test_result"] = None

        results["status"] = "completed"
        results["model_path"] = model_full_path
        results["model_name"] = config[1]["output_model_name"]
        results["dtype"] = config[1]["dtype"]
        results["sizefile"] = config[0]["sizefile"]
        results["task_type"] = config[0]["task_type"]

        print(f"\n✓ Test {test_id} completed successfully")

    except Exception as e:
        print(f"\n✗ Test {test_id} failed with error: {e}")
        results["error"] = str(e)
        import traceback

        results["traceback"] = traceback.format_exc()

    return results


def main():
    """
    Main execution function to run all test configurations sequentially.
    """
    # Generate timestamp
    (year, month, day, hr, minutes, sec, _, _, _) = time.localtime()
    time_proc = f"{year}_{month}_{day}_{hr}_{minutes}_{sec}"  # Fixed syntax

    print(f"{'='*70}")
    print(f"SEQUENTIAL NER MODEL TESTING")
    print(f"Timestamp: {time_proc}")
    print(f"{'='*70}")

    # Example configurations for each test
    test_configurations = {
        # single-non-split-desc-sm
        "1": [
            {
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
            },
            {
                "domain": "queries",
                "sub_domain": "tableau",
                "train_data": None,
                "dtype": "desc",
                "output_model_name": "Description_sm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "val_data": None,
                "option": None,
            },
        ],
        # single-non-split-formulas-sm
        "2": [
            {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "formulas_nor.xlsx",
                "dtype": "formulas",
                "sizefile": "sm",
                "test_size": 0.2,
                "task_type": "single",
                "ner_entity": "ner_queries_formulas",
                "dataset_normalized": None,
                "val_data": False,
                "option": None,
            },
            {
                "domain": "queries",
                "sub_domain": "tableau",
                "train_data": None,
                "dtype": "formulas",
                "output_model_name": "Formulas_sm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "val_data": None,
                "option": None,
            },
        ],
        # multitask-option 1-sm
        "3": [
            {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "formulas_nor_combined.xlsx",
                "dtype": "both",
                "sizefile": "sm",
                "test_size": 0.2,
                "task_type": "multitask",
                "ner_entity": "ner_queries",
                "dataset_normalized": None,
                "val_data": False,
                "option": None,
            },
            {
                "domain": "queries",
                "sub_domain": "tableau",
                "train_data": None,
                "dtype": "both",
                "output_model_name": "Multitask_1_sm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "val_data": None,
                "option": 1,
            },
        ],
        # multitask-option 2-sm
        "4": [
            {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "formulas_nor_combined.xlsx",
                "dtype": "both",
                "sizefile": "sm",
                "test_size": 0.2,
                "task_type": "multitask",
                "ner_entity": "ner_queries",
                "dataset_normalized": None,
                "val_data": False,
                "option": None,
            },
            {
                "domain": "queries",
                "sub_domain": "tableau",
                "train_data": None,
                "dtype": "both",
                "output_model_name": "Multitask_2_sm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "val_data": None,
                "option": 2,
            },
        ],
        # single-non-split-both-ner-queries-sm
        "5": [
            {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "formulas_nor_combined.xlsx",
                "dtype": "both",
                "sizefile": "sm",
                "test_size": 0.2,
                "task_type": "single",
                "ner_entity": "ner_queries",
                "dataset_normalized": None,
                "val_data": False,
                "option": None,
            },
            {
                "domain": "queries",
                "sub_domain": "tableau",
                "train_data": None,
                "dtype": "both",
                "output_model_name": "Combined_sm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "val_data": None,
                "option": None,
            },
        ],
        # single-splitting-both-ner-queries-sm
        "6": [
            {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "formulas_nor_combined.xlsx",
                "dtype": "both",
                "sizefile": "sm",
                "test_size": 0.2,
                "task_type": "single",
                "ner_entity": "ner_queries",
                "dataset_normalized": None,
                "val_data": True,
                "option": "split",
            },
            {
                "domain": "queries",
                "sub_domain": "tableau",
                "train_data": None,
                "dtype": "both",
                "output_model_name": "Combined_split_sm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "val_data": None,
                "option": None,
            },
        ],
        # single-split-desc-bsm
        "7": [
            {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "gformulas_nor_combined.xlsx",
                "dtype": "desc",
                "sizefile": "bsm",
                "test_size": 0.2,
                "task_type": "single",
                "ner_entity": "ner_queries_desc",
                "dataset_normalized": None,
                "val_data": True,
                "option": "split",
            },
            {
                "domain": "queries",
                "sub_domain": "tableau",
                "train_data": None,
                "dtype": "desc",
                "output_model_name": "Combined_desc_bsm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "val_data": None,
                "option": None,
            },
        ],
        # single-split-formulas-bsm
        "8": [
            {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "gformulas_nor_combined.xlsx",
                "dtype": "formulas",
                "sizefile": "bsm",
                "test_size": 0.2,
                "task_type": "single",
                "ner_entity": "ner_queries_formulas",
                "dataset_normalized": None,
                "val_data": True,
                "option": "split",
            },
            {
                "domain": "queries",
                "sub_domain": "tableau",
                "train_data": None,
                "dtype": "formulas",
                "output_model_name": "Combined_formulas_bsm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "val_data": None,
                "option": None,
            },
        ],
        # multitask-option 1-bsm
        "9": [
            {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "gformulas_nor_combined.xlsx",
                "dtype": "both",
                "sizefile": "bsm",
                "test_size": 0.2,
                "task_type": "multitask",
                "ner_entity": "ner_queries",
                "dataset_normalized": None,
                "val_data": True,
                "option": "split",
            },
            {
                "domain": "queries",
                "sub_domain": "tableau",
                "train_data": None,
                "dtype": "both",
                "output_model_name": "Multitask_1_bsm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "val_data": None,
                "option": 1,
            },
        ],
        # multitask-option 2-bsm
        "10": [
            {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "gformulas_nor_combined.xlsx",
                "dtype": "both",
                "sizefile": "bsm",
                "test_size": 0.2,
                "task_type": "multitask",
                "ner_entity": "ner_queries",
                "dataset_normalized": None,
                "val_data": True,
                "option": "split",
            },
            {
                "domain": "queries",
                "sub_domain": "tableau",
                "train_data": None,
                "dtype": "both",
                "output_model_name": "Multitask_2_bsm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "val_data": None,
                "option": 2,
            },
        ],
        # single-split-both-bsm
        "11": [
            {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "gformulas_nor_combined.xlsx",
                "dtype": "both",
                "sizefile": "bsm",
                "test_size": 0.2,
                "task_type": "single",
                "ner_entity": "ner_queries",
                "dataset_normalized": None,
                "val_data": True,
                "option": "split",
            },
            {
                "domain": "queries",
                "sub_domain": "tableau",
                "train_data": None,
                "dtype": "both",
                "output_model_name": "Combined_both_bsm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "val_data": None,
                "option": None,
            },
        ],
    }

    # Run all tests
    results = []
    total_tests = len(test_configurations)

    for idx, (test_id, config) in enumerate(test_configurations.items(), 1):
        print(f"\n\n{'#'*70}")
        print(f"# Test {idx}/{total_tests}: ID={test_id}")
        print(f"{'#'*70}")

        try:
            result = run_test(test_id, config)
            results.append(result)

            # Save config after each test
            save_config(test_id, config, time_proc)

        except Exception as e:
            print(f"\n✗ Test {test_id} crashed: {e}")
            results.append({"test_id": test_id, "status": "crashed", "error": str(e)})

    # Save results to CSV
    print(f"\n\n{'='*70}")
    print("GENERATING FINAL REPORT")
    print(f"{'='*70}")

    results_df = pd.DataFrame(results)
    results_filename = f"results_val_test_{time_proc}.csv"
    results_df.to_csv(results_filename, index=False)

    print(f"\n✓ Results saved to: {results_filename}")
    print(f"\nSummary:")
    print(f"  Total tests: {total_tests}")
    print(f"  Completed: {sum(1 for r in results if r.get('status') == 'completed')}")
    print(
        f"  Failed: {sum(1 for r in results if r.get('status') in ['failed', 'crashed'])}"
    )

    # Display summary table
    summary_cols = ["test_id", "status", "model_name", "val_f1", "test_f1"]
    available_cols = [col for col in summary_cols if col in results_df.columns]
    if available_cols:
        print(f"\n{results_df[available_cols].to_string(index=False)}")

    return results_df


if __name__ == "__main__":
    results = main()
    print("\n✓ All tests completed!")

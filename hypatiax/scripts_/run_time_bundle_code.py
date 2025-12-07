import time
from importlib import resources
from pathlib import Path

import pandas as pd

from hypatiax.core.deployment.evaluation_model import evaluate_spacy_model
from hypatiax.core.evaluation.testing_model import test_spacy_model
from hypatiax.core.preprocessing.preparation_data import preparation_data
from hypatiax.core.training.training_spacy import Training


def create_test_configurations():
    """
    Create test configurations for different NER training scenarios.

    Returns:
        list: List of test configuration dictionaries
    """
    test_configurations = [
        # Test 1: Description only - small dataset
        {
            "test_id": "1",
            "data_prep": {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "formulas_nor.xlsx",
                "dtype": "desc",
                "sizefile": "sm",
                "test_size": 0.2,
                "task_type": "single",
                "ner_entity": "ner_tableau_desc",
                "dataset_normalized": None,
                "val_data": True,
                "option": None,
            },
            "training": {
                "domain": "queries",
                "sub_domain": "tableau",
                "dtype": "desc",
                "output_model_name": "Description_sm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "option": None,
            },
        },
        # Test 2: Formulas only - small dataset
        {
            "test_id": "2",
            "data_prep": {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "formulas_nor.xlsx",
                "dtype": "formulas",
                "sizefile": "sm",
                "test_size": 0.2,
                "task_type": "single",
                "ner_entity": "ner_tableau_formulas",
                "dataset_normalized": None,
                "val_data": True,
                "option": None,
            },
            "training": {
                "domain": "queries",
                "sub_domain": "tableau",
                "dtype": "formulas",
                "output_model_name": "Formulas_sm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "option": None,
            },
        },
        # Test 3: Combined - large dataset
        {
            "test_id": "3",
            "data_prep": {
                "modules": "datasets",
                "domain": "queries",
                "sub_domain": "tableau",
                "actions": "training",
                "filename": "gformulas_nor_combined.xlsx",
                "dtype": "both",
                "sizefile": "bsm",
                "test_size": 0.2,
                "task_type": "single",
                "ner_entity": "ner_tableau",
                "dataset_normalized": None,
                "val_data": True,
                "option": "split",
            },
            "training": {
                "domain": "queries",
                "sub_domain": "tableau",
                "dtype": "both",
                "output_model_name": "Combined_bsm",
                "niter": 400,
                "drop": 0.5,
                "batchsize": 8,
                "patience": 10,
                "n_checkpoint": 100,
                "option": None,
            },
        },
    ]

    return test_configurations


def run_test(config):
    """
    Run a complete NER training and evaluation test.

    Args:
        config (dict): Configuration dictionary containing 'test_id', 'data_prep', and 'training'

    Returns:
        dict: Results containing test_id, status, and metrics
    """
    test_id = config["test_id"]
    print(f"\n{'='*70}")
    print(f"RUNNING TEST {test_id}")
    print(f"{'='*70}")
    print(
        f"Config: dtype={config['data_prep']['dtype']}, "
        f"sizefile={config['data_prep']['sizefile']}, "
        f"model={config['training']['output_model_name']}"
    )

    results = {
        "test_id": test_id,
        "status": "failed",
        "dtype": config["data_prep"]["dtype"],
        "sizefile": config["data_prep"]["sizefile"],
        "model_name": config["training"]["output_model_name"],
    }

    try:
        # Step 1: Prepare data
        print("\n[1/5] Preparing data...")
        X_train, X_val, X_test = preparation_data(**config["data_prep"])

        if X_train is None or len(X_train) == 0:
            raise ValueError("No training data available")

        print(f"  ✓ Train samples: {len(X_train)}")
        print(f"  ✓ Val samples: {len(X_val) if X_val else 0}")
        print(f"  ✓ Test samples: {len(X_test) if X_test else 0}")

        results["train_samples"] = len(X_train)
        results["val_samples"] = len(X_val) if X_val else 0
        results["test_samples"] = len(X_test) if X_test else 0

        # Step 2: Setup training configuration
        print("\n[2/5] Setting up training...")
        training_config = config["training"].copy()
        training_config["train_data"] = X_train
        training_config["val_data"] = X_val

        # Step 3: Train the model
        print("\n[3/5] Training model...")
        trainer = Training(**training_config)
        history, nlp = trainer.train()
        print(f"  ✓ Training completed")

        # Step 4: Save the model
        print("\n[4/5] Saving model...")
        model_path = trainer.save_model()
        results["model_path"] = str(model_path)
        print(f"  ✓ Model saved to: {model_path}")

        # Plot training history
        try:
            trainer.plot_history(history)
            print(f"  ✓ Training history plotted")
        except Exception as e:
            print(f"  ⚠ Could not plot history: {e}")

        # Get model path for evaluation
        try:
            model_base_path = resources.files(
                f"hypatiax.models.{config['training']['domain']}.{config['training']['sub_domain']}"
            )
            model_full_path = str(model_base_path.joinpath(config["training"]["output_model_name"]))
        except Exception as e:
            print(f"  ⚠ Could not construct resource path: {e}")
            # Fallback to direct path
            model_full_path = config["training"]["output_model_name"]

        # Step 5: Evaluate the model
        print("\n[5/5] Evaluating model...")

        # Validation
        if X_val is not None and len(X_val) > 0:
            try:
                print("  Running validation...")
                val_scores = evaluate_spacy_model(model_full_path, X_val)
                results["val_precision"] = round(val_scores.get("ents_p", 0.0), 4)
                results["val_recall"] = round(val_scores.get("ents_r", 0.0), 4)
                results["val_f1"] = round(val_scores.get("ents_f", 0.0), 4)
                print(f"  ✓ Validation F1: {results['val_f1']:.4f}")
            except Exception as e:
                print(f"  ✗ Validation error: {e}")
                results["val_error"] = str(e)
                results["val_precision"] = 0.0
                results["val_recall"] = 0.0
                results["val_f1"] = 0.0
        else:
            print("  ⚠ No validation data available")
            results["val_precision"] = None
            results["val_recall"] = None
            results["val_f1"] = None

        # Testing
        if X_test is not None and len(X_test) > 0:
            try:
                print("  Running testing...")
                test_scores = test_spacy_model(model_full_path, X_test)
                results["test_precision"] = round(test_scores.get("ents_p", 0.0), 4)
                results["test_recall"] = round(test_scores.get("ents_r", 0.0), 4)
                results["test_f1"] = round(test_scores.get("ents_f", 0.0), 4)
                print(f"  ✓ Test F1: {results['test_f1']:.4f}")
            except Exception as e:
                print(f"  ✗ Testing error: {e}")
                results["test_error"] = str(e)
                results["test_precision"] = 0.0
                results["test_recall"] = 0.0
                results["test_f1"] = 0.0
        else:
            print("  ⚠ No test data available")
            results["test_precision"] = None
            results["test_recall"] = None
            results["test_f1"] = None

        results["status"] = "completed"
        print(f"\n✓ Test {test_id} completed successfully")

    except Exception as e:
        print(f"\n✗ Test {test_id} failed: {e}")
        results["error"] = str(e)
        import traceback

        results["traceback"] = traceback.format_exc()

    return results


def save_results(results_df, timestamp):
    """
    Save results to CSV file.

    Args:
        results_df (pd.DataFrame): Results dataframe
        timestamp (str): Timestamp string for filename

    Returns:
        str: Filename where results were saved
    """
    try:
        filename = f"bundle_test_results_{timestamp}.csv"
        results_df.to_csv(filename, index=False)
        print(f"\n✓ Results saved to: {filename}")
        return filename
    except Exception as e:
        print(f"\n✗ Error saving results: {e}")
        return None


def main():
    """
    Main execution function to run all bundled tests.
    """
    # Generate timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    print(f"{'='*70}")
    print(f"BUNDLED NER MODEL TESTING")
    print(f"Timestamp: {timestamp}")
    print(f"{'='*70}")

    # Get test configurations
    test_configurations = create_test_configurations()

    print(f"\nTotal tests to run: {len(test_configurations)}")

    # Run all tests and collect results
    results = []
    for idx, config in enumerate(test_configurations, 1):
        print(f"\n\n{'#'*70}")
        print(f"# Test {idx}/{len(test_configurations)}: ID={config['test_id']}")
        print(f"{'#'*70}")

        try:
            result = run_test(config)
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test {config['test_id']} crashed: {e}")
            results.append({"test_id": config["test_id"], "status": "crashed", "error": str(e)})

    # Convert results to DataFrame
    print(f"\n\n{'='*70}")
    print("GENERATING FINAL REPORT")
    print(f"{'='*70}")

    results_df = pd.DataFrame(results)

    # Save results
    results_file = save_results(results_df, timestamp)

    # Print summary
    print(f"\nSummary:")
    print(f"  Total tests: {len(test_configurations)}")
    print(f"  Completed: {sum(1 for r in results if r.get('status') == 'completed')}")
    print(f"  Failed: {sum(1 for r in results if r.get('status') in ['failed', 'crashed'])}")

    # Display results table
    display_cols = ["test_id", "status", "model_name", "dtype", "val_f1", "test_f1"]
    available_cols = [col for col in display_cols if col in results_df.columns]

    if available_cols:
        print(f"\nResults Summary:")
        print(results_df[available_cols].to_string(index=False))

    # Highlight best performing model
    if "test_f1" in results_df.columns:
        completed_tests = results_df[results_df["status"] == "completed"].copy()
        if not completed_tests.empty and completed_tests["test_f1"].notna().any():
            best_idx = completed_tests["test_f1"].idxmax()
            best_test = completed_tests.loc[best_idx]
            print(f"\n{'='*70}")
            print(f"BEST PERFORMING MODEL")
            print(f"{'='*70}")
            print(f"Test ID: {best_test['test_id']}")
            print(f"Model: {best_test.get('model_name', 'N/A')}")
            print(f"Test F1: {best_test['test_f1']:.4f}")
            if "model_path" in best_test and pd.notna(best_test["model_path"]):
                print(f"Path: {best_test['model_path']}")

    print(f"\n{'='*70}")
    print("ALL TESTS COMPLETED!")
    print(f"{'='*70}")

    return results_df


if __name__ == "__main__":
    try:
        results = main()
        print(f"\n✓ Testing pipeline completed successfully!")
    except Exception as e:
        print(f"\n✗ Testing pipeline failed: {e}")
        import traceback

        traceback.print_exc()

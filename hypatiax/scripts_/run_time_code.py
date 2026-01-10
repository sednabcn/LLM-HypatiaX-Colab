from importlib import resources
from pathlib import Path

import pandas as pd
import spacy
from spacy.training import Example

from hypatiax.core.deployment.evaluation_model import evaluate_spacy_model
from hypatiax.core.evaluation.testing_model import test_spacy_model
from hypatiax.core.preprocessing.preparation_data import preparation_data
from hypatiax.core.training.training_spacy import Training


def main():
    """
    Main execution function for NER model training and evaluation pipeline.
    """
    i = 1  # Run/experiment identifier

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
        "val_data": True,  # Changed to True to enable validation
        "option": None,
    }

    # Save data preparation config
    try:
        config_data_prep = pd.DataFrame(
            [config_data_preparation]
        )  # Fixed: wrap in list
        config_path = resources.files(
            "hypatiax.models.queries.tableau.model_configs"
        ).joinpath(f"config_data_preparation_{i}.csv")
        config_data_prep.to_csv(config_path, index=False)
        print(f"✓ Data preparation config saved to: {config_path}")
    except Exception as e:
        print(f"Warning: Could not save data preparation config: {e}")

    # Preparing the Data
    print("\n" + "=" * 60)
    print("STEP 1: PREPARING DATA")
    print("=" * 60)

    try:
        result = preparation_data(**config_data_preparation)

        # Handle return values based on val_data setting
        if config_data_preparation["val_data"]:
            X_train, X_val, X_test = result
            print(f"✓ Training samples: {len(X_train) if X_train else 0}")
            print(f"✓ Validation samples: {len(X_val) if X_val else 0}")
            print(f"✓ Test samples: {len(X_test) if X_test else 0}")
        else:
            X_train, _, X_test = result
            X_val = None
            print(f"✓ Training samples: {len(X_train) if X_train else 0}")
            print(f"✓ Test samples: {len(X_test) if X_test else 0}")

    except Exception as e:
        print(f"✗ Error preparing data: {e}")
        raise

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

    # Save training config (exclude train_data and val_data to avoid serialization issues)
    try:
        config_training_save = {
            k: v
            for k, v in config_training.items()
            if k not in ["train_data", "val_data"]
        }
        config_training_save["train_samples"] = len(X_train) if X_train else 0
        config_training_save["val_samples"] = len(X_val) if X_val else 0

        config_training_df = pd.DataFrame([config_training_save])  # Fixed: wrap in list
        config_training_path = resources.files(
            "hypatiax.models.queries.tableau.model_configs"
        ).joinpath(f"config_training_{i}.csv")
        config_training_df.to_csv(
            config_training_path, index=False
        )  # Fixed: use correct variable
        print(f"✓ Training config saved to: {config_training_path}")
    except Exception as e:
        print(f"Warning: Could not save training config: {e}")

    # Training the Model
    print("\n" + "=" * 60)
    print("STEP 2: TRAINING MODEL")
    print("=" * 60)

    try:
        trainer = Training(**config_training)
        history, nlp = trainer.train()
        print("✓ Model training completed")
    except Exception as e:
        print(f"✗ Error during training: {e}")
        raise

    # Save the trained model
    print("\n" + "=" * 60)
    print("STEP 3: SAVING MODEL")
    print("=" * 60)

    try:
        model_path = trainer.save_model()
        print(f"✓ Model saved successfully")

        # Plot and save training history
        trainer.plot_history(history)
        print("✓ Training history plotted")
    except Exception as e:
        print(f"✗ Error saving model: {e}")
        raise

    # Determine the model path for evaluation
    # The model is saved, so we need to get its path
    try:
        # Construct model path based on config
        model_base_path = resources.files(
            f"hypatiax.models.{config_training['domain']}.{config_training['sub_domain']}"
        )
        model_path = model_base_path.joinpath(config_training["output_model"])
        model_path_str = str(model_path)
        print(f"Model path for evaluation: {model_path_str}")
    except Exception as e:
        print(f"Warning: Could not construct model path: {e}")
        model_path_str = config_training["output_model"]  # Fallback

    # Validate the Model (if validation data exists)
    if X_val is not None and len(X_val) > 0:
        print("\n" + "=" * 60)
        print("STEP 4: VALIDATING MODEL")
        print("=" * 60)

        try:
            validation_scores = evaluate_spacy_model(model_path_str, X_val)
            print("✓ Validation completed")

            # Check if model meets quality threshold
            f1_threshold = 0.75
            if validation_scores.get("ents_f", 0) >= f1_threshold:
                print(
                    f"✓ Model passed validation (F1: {validation_scores['ents_f']:.4f} >= {f1_threshold})"
                )
            else:
                print(
                    f"⚠ Model below threshold (F1: {validation_scores['ents_f']:.4f} < {f1_threshold})"
                )

        except Exception as e:
            print(f"✗ Error during validation: {e}")
            # Continue to testing even if validation fails
    else:
        print("\n⚠ Skipping validation (no validation data available)")

    # Test the Model
    if X_test is not None and len(X_test) > 0:
        print("\n" + "=" * 60)
        print("STEP 5: TESTING MODEL")
        print("=" * 60)

        try:
            test_scores = test_spacy_model(model_path_str, X_test)
            print("✓ Testing completed")

            # Print final results
            print("\n" + "=" * 60)
            print("FINAL TEST RESULTS")
            print("=" * 60)
            print(f"Precision: {test_scores.get('ents_p', 0):.4f}")
            print(f"Recall:    {test_scores.get('ents_r', 0):.4f}")
            print(f"F1-Score:  {test_scores.get('ents_f', 0):.4f}")
            print("=" * 60)

        except Exception as e:
            print(f"✗ Error during testing: {e}")
            raise
    else:
        print("\n⚠ Skipping testing (no test data available)")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)

    return {
        "model_path": model_path_str,
        "training_history": history,
        "validation_scores": validation_scores if X_val else None,
        "test_scores": test_scores if X_test else None,
    }


if __name__ == "__main__":
    try:
        results = main()
        print(f"\nModel ready for deployment at: {results['model_path']}")
    except Exception as e:
        print(f"\n✗ Pipeline failed with error: {e}")
        raise

import logging
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

import pandas as pd

"""
Enhanced test runner with error handling, logging, and parallel execution.
Supports multiple simulation modes and full integration.

Usage:
    python run_time_parallel_code.py --mode quick
    python run_time_parallel_code.py --mode realistic
    python run_time_parallel_code.py --mode full
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# ============================================================================
# TEST CONFIGURATIONS
# ============================================================================

test_configurations = [
    {
        "test_id": 1,
        "name": "Description_Small",
        "modules": "datasets",
        "domain": "queries",
        "sub_domain": "tableau",
        "dtype": "desc",
        "filename": "formulas_nor.xlsx",
        "sizefile": "sm",
        "ner_entity": "ner_tableau_desc",
        "niter": 400,
        "output_model_name": "Description_sm",
    },
    {
        "test_id": 2,
        "name": "Formulas_Small",
        "modules": "datasets",
        "domain": "queries",
        "sub_domain": "tableau",
        "dtype": "formulas",
        "filename": "formulas_nor.xlsx",
        "sizefile": "sm",
        "ner_entity": "ner_tableau_formulas",
        "niter": 400,
        "output_model_name": "Formulas_sm",
    },
    {
        "test_id": 3,
        "name": "Combined_Large",
        "modules": "datasets",
        "domain": "queries",
        "sub_domain": "tableau",
        "dtype": "combined",
        "filename": "formulas_nor_combined.xlsx",
        "sizefile": "bdsm",
        "ner_entity": "ner_tableau",
        "niter": 400,
        "output_model_name": "Combined_bsm",
    },
]


# ============================================================================
# SIMULATION MODE 1: QUICK MOCK
# ============================================================================


def simulate_quick_test(config: Dict) -> Dict:
    """
    Quick simulation with instant results for infrastructure testing.

    Args:
        config: Test configuration dictionary

    Returns:
        Simulated test results
    """
    test_id = config["test_id"]
    logging.info(f"Quick simulation - Test {test_id}: {config['name']}")

    # Simulate different data sizes
    size_map = {"sm": 100, "bdsm": 500, "bsm": 500, "bg": 1000}
    sizefile = config["sizefile"]
    base_samples = size_map.get(sizefile, 100)

    # Mock data preparation
    train_samples = int(base_samples * 0.6)
    val_samples = int(base_samples * 0.2)
    test_samples = int(base_samples * 0.2)

    # Mock performance metrics (with some variation)
    base_f1 = random.uniform(0.75, 0.92)

    result = {
        "test_id": test_id,
        "name": config["name"],
        "status": "completed",
        "dtype": config["dtype"],
        "sizefile": sizefile,
        "model_name": config["output_model_name"],
        "train_samples": train_samples,
        "val_samples": val_samples,
        "test_samples": test_samples,
        "val_precision": round(base_f1 + random.uniform(-0.03, 0.03), 4),
        "val_recall": round(base_f1 + random.uniform(-0.03, 0.03), 4),
        "val_f1": round(base_f1, 4),
        "test_precision": round(base_f1 + random.uniform(-0.05, 0.02), 4),
        "test_recall": round(base_f1 + random.uniform(-0.05, 0.02), 4),
        "test_f1": round(base_f1 + random.uniform(-0.04, 0.01), 4),
        "training_time": round(random.uniform(30, 120), 2),
    }

    logging.info(f"Test {test_id} - Simulated F1: {result['test_f1']:.4f}")
    return result


# ============================================================================
# SIMULATION MODE 2: REALISTIC SIMULATION
# ============================================================================


def simulate_realistic_test(config: Dict) -> Dict:
    """
    Realistic simulation that mimics actual training behavior with delays.

    Args:
        config: Test configuration dictionary

    Returns:
        Simulated test results with realistic timing
    """
    test_id = config["test_id"]
    test_name = config["name"]

    logging.info(f"Realistic simulation - Test {test_id}: {test_name}")

    result = {
        "test_id": test_id,
        "name": test_name,
        "status": "failed",
        "dtype": config["dtype"],
        "sizefile": config["sizefile"],
        "model_name": config["output_model_name"],
    }

    try:
        # Step 1: Simulate data preparation (1-3 seconds)
        logging.info(f"Test {test_id} - [1/4] Preparing data...")
        time.sleep(random.uniform(1, 3))

        size_map = {"sm": 100, "bdsm": 500, "bsm": 500, "bg": 1000}
        base_samples = size_map.get(config["sizefile"], 100)

        train_samples = int(base_samples * 0.6)
        val_samples = int(base_samples * 0.2)
        test_samples = int(base_samples * 0.2)

        result.update(
            {
                "train_samples": train_samples,
                "val_samples": val_samples,
                "test_samples": test_samples,
            }
        )

        logging.info(
            f"Test {test_id} - Train: {train_samples}, Val: {val_samples}, Test: {test_samples}"
        )

        # Step 2: Simulate training (5-15 seconds based on size)
        logging.info(f"Test {test_id} - [2/4] Training model...")
        niter = config.get("niter", 400)
        training_time = (niter / 100) * random.uniform(1.5, 3.0)
        time.sleep(min(training_time / 50, 5))  # Scaled down for demo

        result["training_time"] = round(training_time, 2)
        logging.info(f"Test {test_id} - Estimated training time: {training_time:.2f}s")

        # Step 3: Simulate validation (1-2 seconds)
        logging.info(f"Test {test_id} - [3/4] Validating model...")
        time.sleep(random.uniform(0.5, 1))

        # Generate realistic metrics based on config
        dtype = config["dtype"]
        base_f1_map = {"desc": 0.85, "formulas": 0.82, "combined": 0.88, "both": 0.88}
        base_f1 = base_f1_map.get(dtype, 0.85)

        # Add some noise
        val_f1 = base_f1 + random.uniform(-0.05, 0.08)
        val_precision = val_f1 + random.uniform(-0.03, 0.04)
        val_recall = val_f1 + random.uniform(-0.04, 0.03)

        result.update(
            {
                "val_precision": round(max(0, min(1, val_precision)), 4),
                "val_recall": round(max(0, min(1, val_recall)), 4),
                "val_f1": round(max(0, min(1, val_f1)), 4),
            }
        )

        logging.info(f"Test {test_id} - Validation F1: {result['val_f1']:.4f}")

        # Step 4: Simulate testing (1-2 seconds)
        logging.info(f"Test {test_id} - [4/4] Testing model...")
        time.sleep(random.uniform(0.5, 1))

        # Test metrics usually slightly lower than validation
        test_f1 = val_f1 - random.uniform(0.01, 0.04)
        test_precision = test_f1 + random.uniform(-0.02, 0.03)
        test_recall = test_f1 + random.uniform(-0.03, 0.02)

        result.update(
            {
                "test_precision": round(max(0, min(1, test_precision)), 4),
                "test_recall": round(max(0, min(1, test_recall)), 4),
                "test_f1": round(max(0, min(1, test_f1)), 4),
            }
        )

        result["status"] = "completed"
        logging.info(f"Test {test_id} - Test F1: {result['test_f1']:.4f} - COMPLETED")

    except Exception as e:
        logging.error(f"Test {test_id} - Error: {e}")
        result["error"] = str(e)

    return result


# ============================================================================
# SIMULATION MODE 3: FULL INTEGRATION (requires hypatiax)
# ============================================================================


def run_full_integration_test(config: Dict) -> Dict:
    """
    Full integration test with actual hypatiax function calls.

    Args:
        config: Test configuration dictionary

    Returns:
        Actual test results
    """
    try:
        from hypatiax.core.deployment.evaluation_model import evaluate_spacy_model
        from hypatiax.core.evaluation.testing_model import test_spacy_model
        from hypatiax.core.preprocessing.preparation_data import preparation_data
        from hypatiax.core.training.training_spacy import Training
    except ImportError as e:
        logging.error(f"Cannot import hypatiax modules: {e}")
        return {
            "test_id": config["test_id"],
            "status": "error",
            "error": "hypatiax package not available - use quick or realistic mode",
        }

    test_id = config["test_id"]
    test_name = config["name"]

    logging.info(f"Full integration - Test {test_id}: {test_name}")

    result = {
        "test_id": test_id,
        "name": test_name,
        "status": "failed",
        "dtype": config["dtype"],
        "sizefile": config["sizefile"],
        "model_name": config["output_model_name"],
    }

    try:
        # Step 1: Prepare data
        logging.info(f"Test {test_id} - [1/4] Preparing data...")
        data_prep_config = {
            "modules": config["modules"],
            "domain": config["domain"],
            "sub_domain": config["sub_domain"],
            "actions": "training",
            "filename": config["filename"],
            "dtype": config["dtype"],
            "sizefile": config["sizefile"],
            "test_size": 0.2,
            "task_type": "single",
            "ner_entity": config["ner_entity"],
            "dataset_normalized": None,
            "val_data": True,
            "option": None,
        }

        X_train, X_val, X_test = preparation_data(**data_prep_config)

        result.update(
            {
                "train_samples": len(X_train) if X_train else 0,
                "val_samples": len(X_val) if X_val else 0,
                "test_samples": len(X_test) if X_test else 0,
            }
        )

        logging.info(
            f"Test {test_id} - Train: {result['train_samples']}, Val: {result['val_samples']}, Test: {result['test_samples']}"
        )

        # Step 2: Train model
        logging.info(f"Test {test_id} - [2/4] Training model...")
        training_config = {
            "domain": config["domain"],
            "sub_domain": config["sub_domain"],
            "train_data": X_train,
            "val_data": X_val,
            "dtype": config["dtype"],
            "output_model_name": config["output_model_name"],
            "niter": config.get("niter", 400),
            "drop": 0.5,
            "batchsize": 8,
            "patience": 10,
            "n_checkpoint": 100,
            "option": None,
        }

        start_time = time.time()
        trainer = Training(**training_config)
        history, nlp = trainer.train()
        training_time = time.time() - start_time

        result["training_time"] = round(training_time, 2)
        logging.info(f"Test {test_id} - Training completed in {training_time:.2f}s")

        # Save model
        model_path = trainer.save_model()
        result["model_path"] = str(model_path)

        # Step 3: Validate
        if X_val and len(X_val) > 0:
            logging.info(f"Test {test_id} - [3/4] Validating model...")
            val_scores = evaluate_spacy_model(nlp, X_val)
            result.update(
                {
                    "val_precision": round(val_scores.get("ents_p", 0.0), 4),
                    "val_recall": round(val_scores.get("ents_r", 0.0), 4),
                    "val_f1": round(val_scores.get("ents_f", 0.0), 4),
                }
            )
            logging.info(f"Test {test_id} - Validation F1: {result['val_f1']:.4f}")

        # Step 4: Test
        if X_test and len(X_test) > 0:
            logging.info(f"Test {test_id} - [4/4] Testing model...")
            test_scores = test_spacy_model(nlp, X_test)
            result.update(
                {
                    "test_precision": round(test_scores.get("ents_p", 0.0), 4),
                    "test_recall": round(test_scores.get("ents_r", 0.0), 4),
                    "test_f1": round(test_scores.get("ents_f", 0.0), 4),
                }
            )
            logging.info(f"Test {test_id} - Test F1: {result['test_f1']:.4f}")

        result["status"] = "completed"
        logging.info(f"Test {test_id} - COMPLETED")

    except Exception as e:
        logging.error(f"Test {test_id} - Error: {e}", exc_info=True)
        result["error"] = str(e)
        import traceback

        result["traceback"] = traceback.format_exc()

    return result


# ============================================================================
# TEST EXECUTION FUNCTION
# ============================================================================


def run_test(config: Dict, mode: str = "realistic") -> Dict:
    """
    Run a test using the specified mode.

    Args:
        config: Test configuration dictionary
        mode: Execution mode ('quick', 'realistic', or 'full')

    Returns:
        dict: Test results with test_id and either result or error
    """
    mode = mode.lower()

    if mode == "quick":
        return simulate_quick_test(config)
    elif mode == "realistic":
        return simulate_realistic_test(config)
    elif mode == "full":
        return run_full_integration_test(config)
    else:
        logging.error(f"Invalid mode: {mode}. Using 'realistic' as default.")
        return simulate_realistic_test(config)


# ============================================================================
# PARALLEL EXECUTION
# ============================================================================


def run_all_tests_concurrently(
    mode: str = "realistic", max_workers: Optional[int] = None
) -> List[Dict]:
    """
    Run all tests concurrently using ThreadPoolExecutor.

    Args:
        mode: Execution mode ('quick', 'realistic', or 'full')
        max_workers: Maximum number of worker threads.
            Defaults to min(3, os.cpu_count())

    Returns:
        list: List of test results
    """
    if max_workers is None:
        max_workers = min(3, os.cpu_count() or 1)

    logging.info(f"=" * 70)
    logging.info(f"Starting parallel test execution")
    logging.info(f"Mode: {mode.upper()}")
    logging.info(f"Tests: {len(test_configurations)}")
    logging.info(f"Workers: {max_workers}")
    logging.info(f"=" * 70)

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_test = {
            executor.submit(run_test, config, mode): config
            for config in test_configurations
        }

        for future in as_completed(future_to_test):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                config = future_to_test[future]
                logging.error(f"Unexpected error for test {config['test_id']}: {e}")
                results.append(
                    {
                        "test_id": config["test_id"],
                        "name": config.get("name", "Unknown"),
                        "status": "error",
                        "error": f"Unexpected error: {str(e)}",
                    }
                )

    logging.info(f"=" * 70)
    logging.info("All tests completed")
    logging.info(f"=" * 70)

    return results


# ============================================================================
# RESULTS DISPLAY
# ============================================================================


def print_results_summary(results_df: pd.DataFrame):
    """
    Print a formatted summary of test results.

    Args:
        results_df: DataFrame containing test results
    """
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)

    # Display main results
    display_cols = [
        "test_id",
        "name",
        "status",
        "dtype",
        "sizefile",
        "val_f1",
        "test_f1",
        "training_time",
    ]
    available_cols = [col for col in display_cols if col in results_df.columns]

    if available_cols:
        print(results_df[available_cols].to_string(index=False))
    else:
        print(results_df.to_string(index=False))

    # Statistics
    print("\n" + "=" * 80)
    success_count = (results_df["status"] == "completed").sum()
    error_count = (results_df["status"].isin(["failed", "error"])).sum()

    print(f"Total Tests:    {len(results_df)}")
    print(f"Completed:      {success_count}")
    print(f"Failed/Errors:  {error_count}")

    # Best model
    if "test_f1" in results_df.columns:
        completed = results_df[results_df["status"] == "completed"]
        if not completed.empty and completed["test_f1"].notna().any():
            best_idx = completed["test_f1"].idxmax()
            best = completed.loc[best_idx]
            print("\n" + "=" * 80)
            print("BEST PERFORMING MODEL")
            print("=" * 80)
            print(f"Test ID:   {best['test_id']}")
            print(f"Name:      {best.get('name', 'N/A')}")
            print(f"Model:     {best.get('model_name', 'N/A')}")
            print(f"Test F1:   {best['test_f1']:.4f}")
            if "model_path" in best and pd.notna(best["model_path"]):
                print(f"Path:      {best['model_path']}")

    print("=" * 80 + "\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Main execution function."""
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run NER model tests in parallel")
    parser.add_argument(
        "--mode",
        type=str,
        default="realistic",
        choices=["quick", "realistic", "full"],
        help="Execution mode: quick (instant mock), realistic (timed simulation), full (actual training)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of parallel workers (default: min(3, CPU count))",
    )

    args = parser.parse_args()

    print(f"\n{'=' * 80}")
    print(f"NER MODEL TESTING - {args.mode.upper()} MODE")
    print(f"{'=' * 80}")

    # Run tests concurrently and collect results
    start_time = time.time()
    results = run_all_tests_concurrently(mode=args.mode, max_workers=args.workers)
    total_time = time.time() - start_time

    # Convert results into a DataFrame for better visualization and analysis
    results_df = pd.DataFrame(results)

    # Sort by test_id
    if "test_id" in results_df.columns:
        results_df = results_df.sort_values("test_id").reset_index(drop=True)

    # Print summary
    print_results_summary(results_df)

    print(f"Total execution time: {total_time:.2f}s\n")

    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{args.mode}_{timestamp}.csv"
    results_df.to_csv(filename, index=False)
    print(f"✓ Results saved to: {filename}\n")

    return results_df


if __name__ == "__main__":
    main()

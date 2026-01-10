import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

"""
Enhanced test runner with error handling, logging, and parallel execution.

Features:
- Error handling to prevent one test failure from stopping others
- Detailed logging for test progress and issues
- Parallel execution using ThreadPoolExecutor for independent tests
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Example configurations for each test
test_configurations = [
    {
        "test_id": 1,
        "modules": "datasets",
        "domain": "queries",
        "sub_domain": "tableau",
        "dtype": "desc",
        "filename": "formulas_nor.xlsx",
        "sizefile": "sm",
        "ner_entity": "ner_tableau_desc",
    },
    {
        "test_id": 2,
        "modules": "datasets",
        "domain": "queries",
        "sub_domain": "tableau",
        "dtype": "formulas",
        "filename": "formulas_nor.xlsx",
        "sizefile": "sm",
        "ner_entity": "ner_tableau_formulas",
    },
    {
        "test_id": 3,
        "modules": "datasets",
        "domain": "queries",
        "sub_domain": "tableau",
        "dtype": "combined",
        "filename": "formulas_nor_combined.xlsx",  # Fixed typo
        "sizefile": "bdsm",
        "ner_entity": "ner_tableau",
    },
]


def run_test(config):
    """
    Run a test given a configuration and log results or exceptions.

    Args:
        config (dict): Test configuration parameters

    Returns:
        dict: Test results with test_id and either result or error
    """
    try:
        logging.info(f"Starting test {config['test_id']} with configuration: {config}")

        # TODO: Replace simulation with actual test execution
        # Example of actual implementation:
        # X_train, X_val, X_test = preparation_data(**config)
        # trainer = Training(**config)
        # history, nlp = trainer.train()
        # results = evaluate_spacy_model(nlp, X_val)
        # return {'test_id': config['test_id'], 'result': results}

        # Simulate a result for demonstration
        simulated_result = {
            "test_id": config["test_id"],
            "status": "success",
            "result": f"Result for test {config['test_id']}",
        }

        logging.info(f"Completed test {config['test_id']} successfully.")
        return simulated_result

    except Exception as e:
        logging.error(f"Error running test {config['test_id']}: {e}", exc_info=True)
        return {"test_id": config["test_id"], "status": "error", "error": str(e)}


def run_all_tests_concurrently(max_workers=None):
    """
    Run all tests concurrently using ThreadPoolExecutor.

    Args:
        max_workers (int, optional): Maximum number of worker threads.
            Defaults to min(32, os.cpu_count() + 4)

    Returns:
        list: List of test results
    """
    if max_workers is None:
        max_workers = min(3, os.cpu_count() or 1)

    logging.info(f"Starting parallel test execution with {max_workers} workers")
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_test = {
            executor.submit(run_test, config): config for config in test_configurations
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
                        "status": "error",
                        "error": f"Unexpected error: {str(e)}",
                    }
                )

    logging.info("All tests completed")
    return results


def main():
    """Main execution function."""
    # Run tests concurrently and collect results
    results = run_all_tests_concurrently()

    # Convert results into a DataFrame for better visualization and analysis
    results_df = pd.DataFrame(results)

    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print(results_df.to_string(index=False))
    print("=" * 80 + "\n")

    # Summary statistics
    success_count = sum(1 for r in results if r.get("status") == "success")
    error_count = len(results) - success_count

    print(f"Total Tests: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {error_count}")

    return results_df


if __name__ == "__main__":
    main()

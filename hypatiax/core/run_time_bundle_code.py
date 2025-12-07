import pandas as pd

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
        "filename": "gformulas_nor_combined.xlsx",
        "sizefile": "bdsm",
        "ner_entity": "ner_tableau",
    },
    # Add more configurations for other tests
]


def run_test(config):
    """
    Simulate running a test given a configuration.
    Normally, you would call the appropriate functions and modules here based on the config.
    """
    # Placeholder for running a test
    print(f"Running test {config['test_id']} with configuration: {config}")
    # Example function calls (commented out because they are not defined)
    X_train, X_val, X_test = preparation_data(**config)
    trainer = Training(**config)
    history, nlp = trainer.train()
    # Save the trained model
    trainer.save_model()
    trainer.plot_history(history)

    results = evaluate_spacy_model(nlp, X_val)
    test_spacy_model(entity_path, test_data)
    # return results

    # Simulate a result
    return {"test_id": config["test_id"], "result": f"Result for {config['test_id']}"}


# Running all tests and collecting results
results = []
for config in test_configurations:
    result = run_test(config)
    results.append(result)

# Optionally convert results into a DataFrame for better visualization and analysis
results_df = pd.DataFrame(results)
print(results_df)

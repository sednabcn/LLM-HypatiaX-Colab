
┌──(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab/tests]
└─$ tree
.
├── benchmark
│   └── __init__.py
├── conftest.py
├── docs
│   ├── Complete-Test-Guide.md
│   ├── domain_testing.md
│   ├── fixture_guide.md
│   ├── __init__.py
│   ├── testing_guide.md
│   └── Usage_test_runner.md
├── e2e
│   ├── conftest.py
│   ├── __init__.py
│   └── test_hybrid_system_e2e.py
├── fixtures
│   ├── common
│   │   ├── fixtures.py
│   │   └── __init__.py
│   ├── conftest.py
│   ├── create_all_fixtures.sh
│   ├── data
│   │   ├── fixtures.py
│   │   └── __init__.py
│   ├── defi
│   │   ├── __init__.py
│   │   ├── protocols
│   │   │   ├── fixtures.py
│   │   │   └── __init__.py
│   │   └── risk
│   │       ├── fixtures.py
│   │       └── __init__.py
│   ├── __init__.py
│   ├── llm
│   │   ├── anthropic
│   │   │   ├── fixtures.py
│   │   │   └── __init__.py
│   │   ├── google
│   │   │   ├── fixtures.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── models
│   │   ├── fixtures.py
│   │   └── __init__.py
│   ├── ner
│   │   ├── entities
│   │   │   ├── fixtures.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   └── sentences
│   │       ├── fixtures.py
│   │       ├── __init__.py
│   │       ├── raw_sentences.py
│   │       └── sample_sentences.py
│   └── symbolic
│       ├── expressions
│       │   ├── fixtures.py
│       │   └── __init__.py
│       ├── formulas
│       │   ├── fixtures.py
│       │   └── __init__.py
│       └── __init__.py
├── __init__.py
├── integration
│   ├── agents
│   │   └── __init__.py
│   ├── conftest.py
│   ├── data
│   │   ├── __init__.py
│   │   ├── test_loading_data_testing_spacy.py
│   │   ├── test_loading_formulas_combined_test.py
│   │   ├── test_loading_formulas_test.py
│   │   ├── test_normalize.py
│   │   └── test_tableau_data_csv.py
│   ├── defi
│   │   └── __init__.py
│   ├── docs
│   │   ├── integration_quickstart.md
│   │   ├── #integration_testing_documentation.md#
│   │   ├── integration_testing_documentation.md
│   │   └── usage-test-extrapolation.md
│   ├── extrapolation
│   │   ├── __init__.py
│   │   └── test_extrapolation.py
│   ├── __init__.py
│   ├── llm
│   │   ├── conftest.py
│   │   ├── __init__.py
│   │   └── test_real_llm_integration.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── template2-integration.py
│   │   ├── test-model-loading.py
│   │   └── test_training_spacy.py
│   ├── ner
│   │   ├── __init__.py
│   │   ├── test_desc_formulas.py
│   │   ├── test_entity_desc.py
│   │   ├── test_entity_formulas.py
│   │   ├── test_F_ner_tableau_desc.py
│   │   ├── test_F_ner_tableau_formulas.py
│   │   ├── test_ner_desc.py
│   │   ├── test_ner_formulas.py
│   │   └── test_rename_files.py
│   ├── performance
│   │   ├── __init__.py
│   │   └── test_performance_integration.py
│   ├── symbolic
│   │   └── __init__.py
│   ├── tableau
│   │   └── __init__.py
│   ├── transformers
│   │   └── __init__.py
│   └── validators
│       └── __init__.py
├── pytest.ini
├── QUICK_RFERENCE.md
├── unit
│   ├── agents
│   │   └── __init__.py
│   ├── api_keys
│   │   └── test_anthropic_key.py
│   ├── conftest.py
│   ├── data
│   │   └── __init__.py
│   ├── defi
│   │   ├── __init__.py
│   │   ├── test_formulas.py
│   │   └── test_suite_defi_formulas.py
│   ├── __init__.py
│   ├── llm
│   │   ├── conftest.py
│   │   ├── __init__.py
│   │   ├── run_tests.sh
│   │   ├── test_anthropic_provider_mock.py
│   │   ├── test_anthropic_provider.py
│   │   ├── test_edge_cases.py
│   │   ├── test_gogle_provider.py
│   │   └── test_google_provider_mock.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── test_description_model.py
│   │   ├── test_description_model.py~
│   │   ├── test_formulas_check_1.py
│   │   ├── test_formulas_check_1.py~
│   │   ├── test_formulas_model.py
│   │   └── test_formulas_model.py~
│   ├── ner
│   │   ├── conftest.py
│   │   ├── __init__.py
│   │   └── tableau
│   │       ├── __init__.py
│   │       ├── test_entity_desc.py
│   │       └── test_entity_formulas.py
│   ├── risk
│   │   ├── __init__.py
│   │   ├── test_risk_formulas_30.py
│   │   └── test_risk_formulas_full.py
│   ├── symbolic
│   │   ├── conftest.py
│   │   ├── __init__.py
│   │   ├── patch_tests_symbolic_engine.py
│   │   ├── test_symbolic_engine.py
│   │   └── test_symbolic_validator.py
│   ├── tableau
│   │   └── __init__.py
│   ├── test_outputs
│   │   ├── selected_formulas.json
│   │   └── validator_test_results_20251121_150313.json
│   ├── transformers
│   │   └── __init__.py
│   └── validators
│       ├── __init__.py
│       ├── test_ensemble_validator.py
│       ├── test_hybrid_suite_validators.py
│       └── test_suite_validators.py
└── VALIDATION_CHECKLIST.md

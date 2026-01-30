hypatiax/
│
├── 📂 tests/
│   ├── __init__.py
│   │
│   ├── 📂 unit/                        # Fast, isolated tests
│   │   ├── __init__.py
│   │   ├── test_preprocessing.py       # Tests for preprocessing modules
│   │   ├── test_training_spacy.py      # SpaCy training tests
│   │   ├── test_training_transformer.py
│   │   ├── test_evaluation.py
│   │   ├── test_deployment.py
│   │   ├── test_mappings.py            # Mapping strategy tests
│   │   └── test_utils.py               # Utility function tests
│   │
│   ├── 📂 integration/                 # End-to-end workflow tests
│   │   ├── __init__.py
│   │   ├── test_pipeline_spacy.py      # Full spaCy pipeline
│   │   ├── test_pipeline_transformer.py
│   │   ├── test_pipeline_rag.py
│   │   ├── test_pipeline_hybrid.py
│   │   └── test_api_endpoints.py       # API integration tests
│   │
│   ├── 📂 benchmark/                   # Performance tests
│   │   ├── __init__.py
│   │   ├── test_performance.py         # Speed/memory benchmarks
│   │   ├── test_scalability.py         # Load testing
│   │   └── benchmark_results.json      # Historical benchmarks
│   │
│   ├── 📂 fixtures/                    # Shared test data
│   │   ├── __init__.py
│   │   ├── sample_data.py              # Sample datasets
│   │   ├── mock_models.py              # Mock model objects
│   │   └── test_configs.py             # Test configurations
│   │
│   ├── 📂 conftest.py                  # Pytest configuration & fixtures
│   │
│   └── 📂 data/                        # Test datasets
│       ├── sample_train.json
│       ├── sample_test.json
│       └── expected_outputs.json
│
├── 📂 core/
│   ├── preprocessing/
│   │   ├── preparation_data.py         # NO test files here
│   │   └── preprocessing_pipeline.py
│   ├── training/
│   │   ├── training_spacy.py           # NO test files here
│   │   └── ...
│   └── ...
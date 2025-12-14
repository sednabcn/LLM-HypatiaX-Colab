┌──(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/datasets]
└─$ tree
.
├── docs
│   ├── 20_formulas_to_generate.md
│   ├── Usage-defi-dataset-generator.docx
│   ├── usage-full-dataset-generator.md
│   └── Usage-risk-dataset-generator.docx
├── finance
│   ├── agent
│   │   ├── agent_queries.py
│   │   ├── __init__.py
│   │   └── test.py
│   ├── analytics
│   │   ├── analytics_data.py
│   │   ├── __init__.py
│   │   └── test.py
│   ├── combined
│   │   ├── combined_data.py
│   │   ├── combined_local_data.py
│   │   └── __init__.py
│   ├── defi
│   │   ├── data
│   │   │   ├── defi_formulas_20251126_205624.json
│   │   │   ├── defi_formulas_at_market.txt~
│   │   │   ├── defi_formulas_fixed_20251126_211441.json
│   │   │   ├── defi_summary_20251126_205624.csv
│   │   │   ├── defi_summary_fixed_20251126_211441.csv
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── llm
│   │   ├── __init__.py
│   │   ├── llm_queries.py
│   │   └── test.py
│   ├── normalize
│   │   ├── __init__.py
│   │   ├── normalize_data.py
│   │   └── test.py
│   ├── risk
│   │   ├── data
│   │   │   ├── __init__.py
│   │   │   └── risk_comprehensive.json
│   │   └── __init__.py
│   └── transformer
│       ├── __init__.py
│       ├── test.py
│       └── transformer_queries.py
├── generators
│   ├── dataset-generator.py
│   ├── datasets_generation.py
│   ├── finance
│   │   ├── defi
│   │   │   ├── defi_advanced_dataset_generator.py
│   │   │   ├── defi_dataset_20_generator.py
│   │   │   ├── defi_dataset_generator.py
│   │   │   ├── defi_dataset_generator_units.py
│   │   │   ├── defi_dataset_master_generator.py
│   │   │   ├── docs
│   │   │   │   └── defi_generators.md
│   │   │   ├── enhanced_defi_advanced_dataset_generator.py
│   │   │   ├── __init__.py
│   │   │   └── output
│   │   │       ├── defi_dataset_generated_report.txt
│   │   │       ├── defi_datasets_generated_report.txt
│   │   │       └── defi_formulas_at_market.txt
│   │   ├── __init__.py
│   │   └── risk
│   │       ├── docs
│   │       ├── __init__.py
│   │       ├── outputs
│   │       │   ├── risk_dataset_at the market.txt
│   │       │   ├── risk_dataset_at_the_market.txt
│   │       │   └── risk_dataset_generator_report.txt
│   │       ├── risk_advanced_dataset_generator.py
│   │       ├── risk_dataset_20_generator.py
│   │       └── risk_dataset_generator.py
│   ├── full_dataset_generator.py
│   ├── hypatiax_dataset.py
│   ├── __init__.py
│   └── queries
│       ├── finance
│       │   ├── defi
│       │   │   ├── defi_queries_dataset_generator.py
│       │   │   └── __init__.py
│       │   ├── __init__.py
│       │   └── risk
│       │       ├── __init__.py
│       │       └── risk_queries_dataset_generator.py
│       ├── __init__.py
│       ├── perfume_clinical
│       │   ├── ai_perfume_clinical_lab_150.py
│       │   ├── ai_perfume_clinical_lab_75.py
│       │   ├── __init__.py
│       │   ├── notes.md
│       │   ├── notes.md~
│       │   └── perfume_clinical_lab.py
│       └── tableau
│           ├── __init__.py
│           └── tableau_queries_iris_dataset_generator.py
├── __init__.py
├── __pycache__
│   └── __init__.cpython-312.pyc
├── queries
│   ├── agent
│   │   ├── agent_queries.py
│   │   ├── __init__.py
│   │   └── test.py
│   ├── analytics
│   │   ├── analytics_data.py
│   │   ├── __init__.py
│   │   └── test.py
│   ├── combined
│   │   ├── combined_data.py
│   │   ├── combined_local_data.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── combined_data.cpython-312.pyc
│   │       └── __init__.cpython-312.pyc
│   ├── __init__.py
│   ├── llm
│   │   ├── __init__.py
│   │   ├── llm_queries.py
│   │   └── test.py
│   ├── normalize
│   │   ├── __init__.py
│   │   ├── normalize_data.py
│   │   └── test.py
│   ├── __pycache__
│   │   └── __init__.cpython-312.pyc
│   ├── tableau
│   │   ├── agent
│   │   │   └── __init__.py
│   │   ├── data
│   │   │   ├── __init__.py
│   │   │   ├── tableau_data.csv
│   │   │   └── test.py
│   │   ├── __init__.py
│   │   ├── llm
│   │   │   └── __init__.py
│   │   ├── __pycache__
│   │   │   └── __init__.cpython-312.pyc
│   │   ├── testing
│   │   │   ├── formulas_test_combined.xlsx
│   │   │   ├── formulas_test_nor_combined.xlsx
│   │   │   ├── formulas_test_nor.xlsx
│   │   │   ├── formulas_test.xlsx
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   └── __init__.cpython-312.pyc
│   │   │   ├── test_combined.py
│   │   │   ├── testing_versions
│   │   │   │   └── __init__.py
│   │   │   ├── test.py
│   │   │   └── test_update_labels.py
│   │   ├── testing_spacy
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   └── __init__.cpython-312.pyc
│   │   │   ├── Test_desc_data.json
│   │   │   ├── Test_formulas_data.json
│   │   │   ├── testing_spacy_versions
│   │   │   │   └── __init__.py
│   │   │   ├── test.py
│   │   │   ├── Test_tableau_both_sm_data.json
│   │   │   ├── Test_tableau_desc_sm_data.json
│   │   │   └── Test_tableau_formulas_sm_data.json
│   │   ├── training
│   │   │   ├── formulas_combined.xlsx
│   │   │   ├── formulas_nor_combined.xlsx
│   │   │   ├── formulas_nor.xlsx
│   │   │   ├── formulas.xlsx
│   │   │   ├── gformulas_combined.xlsx
│   │   │   ├── gformulas.csv
│   │   │   ├── gformulas_nor_combined.xlsx
│   │   │   ├── gformulas_nor.xlsx
│   │   │   ├── gformulas.xlsx
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   └── __init__.cpython-312.pyc
│   │   │   ├── test_combined.py
│   │   │   ├── test.py
│   │   │   ├── test_update_labels.py
│   │   │   └── training_versions
│   │   │       └── __init__.py
│   │   ├── training_spacy
│   │   │   ├── __init__.py
│   │   │   ├── test.py
│   │   │   ├── Train_desc_data.json
│   │   │   ├── Train_formulas_data.json
│   │   │   ├── training_spacy_versions
│   │   │   │   └── __init__.py
│   │   │   ├── Train_tableau_both_bsm_data.json
│   │   │   ├── Train_tableau_both_sm_data.json
│   │   │   ├── Train_tableau_desc_bsm_data.json
│   │   │   ├── Train_tableau_desc_sm_data.json
│   │   │   ├── Train_tableau_formulas_bsm_data.json
│   │   │   └── Train_tableau_formulas_sm_data.json
│   │   ├── transformer
│   │   │   └── __init__.py
│   │   ├── validation
│   │   │   ├── __init__.py
│   │   │   ├── test.py
│   │   │   └── validation_versions
│   │   │       └── __init__.py
│   │   └── validation_spacy
│   │       └── __init__.py
│   └── transformer
│       ├── __init__.py
│       ├── test.py
│       └── transformer_queries.py
└── validation
    ├── docs
    │   └── usage-validation.md
    ├── __init__.py
    └── validate_dataset.py

59 directories, 155 files

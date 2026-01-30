──(py312)(agagora㉿localhost)-[~/Downloads/LLM-HypatiaX-OLD/hypatiax]
└─$ tree                                                                                                             
.
├── auto_migrate.py
├── config
│   ├── base.py
│   ├── config.py
│   ├── config-tools.md
│   ├── constants.py
│   ├── __init__.py
│   ├── ModelConfig.md
│   ├── model_configs.py
│   ├
│   ├── paths.py
│   ├── __pycache__
│   │
├── core
│   ├── deployment
│   │   ├── docs.txt
│   │   ├── evaluate_model.py
│   │
│   │   ├── evaluate_model-tools.md
│   │   └── __init__.py
│   ├── evaluation
│   │   ├── docs.txt
│   │   ├── __init__.py
│   │   ├── spacy_update.md
│   │   ├
│   │   ├── testing_model.py
│   │   ├
│   │   └
│   ├── __init__.py
│   ├── preprocessing
│   │   ├── __init__.py
│   │   ├── preparation_data.py
│   │   └
│   └── training
│       ├── docs.txt
│       ├── __init__.py
│       └── training_spacy.py
├── custom_entities
│   ├── __init__.py
│   ├── ner_entity.py
│   └── __pycache__
│  ├├── custom_ner
│   ├── custom_ruler.py
│   ├── __init__.py
│   ├── __pycache__
│   │
│   ├── queries
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │
│   │   └── tableau
│   │       ├── components
│   │       │   ├── __init__.py
│   │       │   ├── ruler_tableau_desc.py
│   │       │   ├── ruler_tableau_formulas.py
│   │       │   └── ruler_tableau.py
│   │       ├── custom_tableau_components.py
│   │       ├── custom_tableau_desc_components.py
│   │       ├── custom_tableau_formulas_components.py
│   │       ├── __init__.py
│   │       ├── __pycache__
│   │       │
│   │       ├── rules
│   │       │   ├── __init__.py
│   │       │   ├── __pycache__
│   │       │   ├── ruler_tableau_both.jsonl
│   │       │   ├── ruler_tableau_desc.jsonl
│   │       │   ├── ruler_tableau_formulas.jsonl
│   │       │   └── ruler_tableau.jsonl
│   │       └── scripts
│   │           ├── __init__.py
│   │           ├── proc_timed.py
│   │           ├── proc_timef.py
│   │           └── proc_time.py
│   └── rule_file_analyzer.py
├── datasets
│   ├── __init__.py
│   ├── __pycache__
│   │   └
│   └── queries
│       ├── combined
│       │   ├── combined_data.py
│       │   ├── combined_local_data.py
│       │   ├── __init__.py
│       │   └── __pycache__
│       │   
│       ├── __init__.py
│       ├── normalize
│       │   ├── __init__.py
│       │   └── test.py
│       ├── __pycache__
│       │   
│       └── tableau
│           ├── data
│           │   ├── __init__.py
│           │   ├── tableau_data.csv
│           │   └── test.py
│           ├── __init__.py
│           ├── __pycache__
│           │   
│           ├── testing
│           │   ├── formulas_test_combined.xlsx
│           │   ├── formulas_test_nor_combined.xlsx
│           │   ├── formulas_test_nor.xlsx
│           │   ├── formulas_test.xlsx
│           │   ├── __init__.py
│           │   ├── __pycache__
│           │   │
│           │   ├── test_combined.py
│           │   └── test.py
│           ├── testing_spacy
│           │   ├── __init__.py
│           │   ├── __pycache__
│           │   │ 
│           │   ├── Test_desc_data.json
│           │   ├── Test_formulas_data.json
│           │   ├── test.py
│           │   ├── Test_tableau_both_sm_data.json
│           │   ├── Test_tableau_desc_sm_data.json
│           │   └── Test_tableau_formulas_sm_data.json
│           ├── training
│           │   ├── formulas_combined.xlsx
│           │   ├── formulas_nor_combined.xlsx
│           │   ├── formulas_nor.xlsx
│           │   ├── formulas.xlsx
│           │   ├── gformulas_combined.xlsx
│           │   ├── gformulas.csv
│           │   ├── gformulas_nor_combined.xlsx
│           │   ├── gformulas_nor.xlsx
│           │   ├── gformulas.xlsx
│           │   ├── __init__.py
│           │   ├── __pycache__
│           │   │
│           │   ├── test_combined.py
│           │   ├── test.py
│           │   └── test_update_labels.py
│           ├── training_spacy
│           │   ├── __init__.py
│           │   ├── test.py
│           │   ├── Train_desc_data.json
│           │   ├── Train_formulas_data.json
│           │   ├── Train_tableau_both_bsm_data.json
│           │   ├── Train_tableau_both_sm_data.json
│           │   ├── Train_tableau_desc_bsm_data.json
│           │   ├── Train_tableau_desc_sm_data.json
│           │   ├── Train_tableau_formulas_bsm_data.json
│           │   └── Train_tableau_formulas_sm_data.json
│           ├── validation
│           │   ├── __init__.py
│           │   └── test.py
│           └── validation_spacy
│               └── __init__.py
├── data_spacy
│   ├── corpus
│   │   └── __init__.py
│   ├── embedding
│   │   └── __init__.py
│   ├── __init__.py
│   ├── pipelines
│   │   └── __init__.py
│   ├── pre_trained_models
│   │   ├── en_core_web_sm
│   │   │   ├── en_core_web_sm-3.7.1
│   │   │   │   ├── accuracy.json
│   │   │   │   ├── attribute_ruler
│   │   │   │   │   └── patterns
│   │   │   │   ├── config.cfg
│   │   │   │   ├── lemmatizer
│   │   │   │   │   └── lookups
│   │   │   │   │       └── lookups.bin
│   │   │   │   ├── LICENSE
│   │   │   │   ├── LICENSES_SOURCES
│   │   │   │   ├── meta.json
│   │   │   │   ├── ner
│   │   │   │   │   ├── cfg
│   │   │   │   │   ├── model
│   │   │   │   │   └── moves
│   │   │   │   ├── parser
│   │   │   │   │   ├── cfg
│   │   │   │   │   ├── model
│   │   │   │   │   └── moves
│   │   │   │   ├── README.md
│   │   │   │   ├── senter
│   │   │   │   │   ├── cfg
│   │   │   │   │   └── model
│   │   │   │   ├── tagger
│   │   │   │   │   ├── cfg
│   │   │   │   │   └── model
│   │   │   │   ├── tok2vec
│   │   │   │   │   ├── cfg
│   │   │   │   │   └── model
│   │   │   │   ├── tokenizer
│   │   │   │   └── vocab
│   │   │   │       ├── key2row
│   │   │   │       ├── lookups.bin
│   │   │   │       ├── strings.json
│   │   │   │       ├── vectors
│   │   │   │       └── vectors.cfg
│   │   │   ├── en_core_web_sm-3.8.0
│   │   │   │   ├── accuracy.json
│   │   │   │   ├── attribute_ruler
│   │   │   │   │   └── patterns
│   │   │   │   ├── config.cfg
│   │   │   │   ├── lemmatizer
│   │   │   │   │   └── lookups
│   │   │   │   │       └── lookups.bin
│   │   │   │   ├── LICENSE
│   │   │   │   ├── LICENSES_SOURCES
│   │   │   │   ├── meta.json
│   │   │   │   ├── ner
│   │   │   │   │   ├── cfg
│   │   │   │   │   ├── model
│   │   │   │   │   └── moves
│   │   │   │   ├── parser
│   │   │   │   │   ├── cfg
│   │   │   │   │   ├── model
│   │   │   │   │   └── moves
│   │   │   │   ├── README.md
│   │   │   │   ├── senter
│   │   │   │   │   ├── cfg
│   │   │   │   │   └── model
│   │   │   │   ├── tagger
│   │   │   │   │   ├── cfg
│   │   │   │   │   └── model
│   │   │   │   ├── tok2vec
│   │   │   │   │   ├── cfg
│   │   │   │   │   └── model
│   │   │   │   ├── tokenizer
│   │   │   │   └── vocab
│   │   │   │       ├── key2row
│   │   │   │       ├── lookups.bin
│   │   │   │       ├── strings.json
│   │   │   │       ├── vectors
│   │   │   │       └── vectors.cfg
│   │   │   ├── __init__.py
│   │   │   ├── meta.json
│   │   │   └── __pycache__
│   │   │       
│   │   ├── en_core_web_sm-3.8.0.dist-info
│   │   │   ├── direct_url.json
│   │   │   ├── entry_points.txt
│   │   │   ├── INSTALLER
│   │   │   ├── LICENSE
│   │   │   ├── LICENSES_SOURCES
│   │   │   ├── METADATA
│   │   │   ├── RECORD
│   │   │   ├── REQUESTED
│   │   │   ├── top_level.txt
│   │   │   └── WHEEL
│   │   └── __init__.py
│   ├── __pycache__
│   │   
│   └── queries
│       ├── __init__.py
│       ├── __pycache__
│       │   
│       └── tableau
│           ├── __init__.py
│           ├── ner_tableau
│           │   ├── attribute_ruler
│           │   │   └── patterns
│           │   ├── config.cfg
│           │   ├── lemmatizer
│           │   │   └── lookups
│           │   │       └── lookups.bin
│           │   ├── meta.json
│           │   ├── ner
│           │   │   ├── cfg
│           │   │   ├── model
│           │   │   └── moves
│           │   ├── parser
│           │   │   ├── cfg
│           │   │   ├── model
│           │   │   └── moves
│           │   ├── senter
│           │   │   ├── cfg
│           │   │   └── model
│           │   ├── tagger
│           │   │   ├── cfg
│           │   │   └── model
│           │   ├── tok2vec
│           │   │   ├── cfg
│           │   │   └── model
│           │   ├── tokenizer
│           │   └── vocab
│           │       ├── key2row
│           │       ├── lookups.bin
│           │       ├── strings.json
│           │       ├── vectors
│           │       └── vectors.cfg
│           ├── ner_tableau_desc
│           │   ├── attribute_ruler
│           │   │   └── patterns
│           │   ├── config.cfg
│           │   ├── lemmatizer
│           │   │   └── lookups
│           │   │       └── lookups.bin
│           │   ├── meta.json
│           │   ├── ner
│           │   │   ├── cfg
│           │   │   ├── model
│           │   │   └── moves
│           │   ├── parser
│           │   │   ├── cfg
│           │   │   ├── model
│           │   │   └── moves
│           │   ├── senter
│           │   │   ├── cfg
│           │   │   └── model
│           │   ├── tagger
│           │   │   ├── cfg
│           │   │   └── model
│           │   ├── tok2vec
│           │   │   ├── cfg
│           │   │   └── model
│           │   ├── tokenizer
│           │   └── vocab
│           │       ├── key2row
│           │       ├── lookups.bin
│           │       ├── strings.json
│           │       ├── vectors
│           │       └── vectors.cfg
│           ├── ner_tableau_formulas
│           │   ├── attribute_ruler
│           │   │   └── patterns
│           │   ├── config.cfg
│           │   ├── lemmatizer
│           │   │   └── lookups
│           │   │       └── lookups.bin
│           │   ├── meta.json
│           │   ├── ner
│           │   │   ├── cfg
│           │   │   ├── model
│           │   │   └── moves
│           │   ├── parser
│           │   │   ├── cfg
│           │   │   ├── model
│           │   │   └── moves
│           │   ├── senter
│           │   │   ├── cfg
│           │   │   └── model
│           │   ├── tagger
│           │   │   ├── cfg
│           │   │   └── model
│           │   ├── tok2vec
│           │   │   ├── cfg
│           │   │   └── model
│           │   ├── tokenizer
│           │   └── vocab
│           │       ├── key2row
│           │       ├── lookups.bin
│           │       ├── strings.json
│           │       ├── vectors
│           │       └── vectors.cfg
│           ├── __pycache__
│           │   ├── __init__.cpython-312.pyc
│           │   ├── test_ner_desc.cpython-312.pyc
│           │   └── test_ner_formulas.cpython-312.pyc
│           ├── testing_spacy
│           │   ├── __init__.py
│           │   ├── Test_desc_data.spacy
│           │   ├── Test_formulas_data.spacy
│           │   ├── Test_tableau_both_dsm_data.spacy
│           │   ├── Test_tableau_desc_sm_data.spacy
│           │   └── Test_tableau_formulas_sm_data.spacy
│           ├── training_spacy
│           │   ├── __init__.py
│           │   ├── Train_desc_data.spacy
│           │   ├── Train_formulas_data.spacy
│           │   ├── Train_tableau_both_bdsm_data.spacy
│           │   ├── Train_tableau_both_dsm_data.spacy
│           │   ├── Train_tableau_desc_bsm_data.spacy
│           │   ├── Train_tableau_desc_sm_data.spacy
│           │   ├── Train_tableau_formulas_bsm_data.spacy
│           │   └── Train_tableau_formulas_sm_data.spacy
│           └── vocab
│               ├── __init__.py
│               ├── vocab_tableau_both_Combined_bdsm
│               ├── vocab_tableau_both_Combined_dsm
│               ├── vocab_tableau_desc_Description_bsm
│               ├── vocab_tableau_desc_Description_sm
│               ├── vocab_tableau_formulas_Formula (Tableau)_bsm
│               └── vocab_tableau_formulas_Formula (Tableau)_sm
├── demo
│   ├── COMPLETE-FILE-OVERVIEW.pdf
│   ├── complete-system-guide
│   │   ├── advanced_configuration.md
│   │   ├── API.md
│   │   ├── 
│   │   ├── benchmark
│   │   │   └── benchmark01.py
│   │   ├── custom_demos
│   │   │   ├── batch_processing_demo.py
│   │   │   
│   │   │   └── simple_clidemo.py
│   │   ├── example_engine.py
│   │   ├── Examples-API.md
│   │   ├── example_ui.py
│   │   ├── guide.md
│   │   ├── install_dependencies.sh
│   │   ├── 
│   │   ├── integration-patterns
│   │   │   ├── pattern1.py
│   │   │   ├── pattern2.py
│   │   │   ├── pattern3.py
│   │   │   ├── pattern4.py
│   │   │   └── pattern5.py
│   │   ├── run_interactive_demo.py
│   │   ├── usage_basic.py
│   │   ├── usage_basic.py~
│   │   ├── usage_examples.py
│   │   ├── Web-Interface(Complete Stack).html
│   │   ├── 
│   │   └── you're-all-set.md
│   ├── COMPLETE_SYSTEM_GUIDE.pdf
│   ├── config.py
│   ├── demo_examples.py
│   ├── demo_flow.md
│   ├── 
│   ├── demo_interactive.py
│   ├── demo_web_api.py
│   ├── engine.py
│   ├── examples.py
│   ├── __init__.py
│   ├── README.md
│   ├── templates
│   │   ├── demo.html
│   │   ├── demo.html~
│   │   ├── demo-interactive.html
│   │   ├── linkedin_full_demo.html
│   │   └── linkein_visual_demo.html
│   ├── ui.py
│   ├── update
│   │   ├── compare_old_vs_new.py
│   │   ├── Demo-setup-guide.docx
│   │   ├── Demo-setup-guide.pdf
│   │   ├── Guide-Action.pdf
│   │   ├── Guide.docx
│   │   ├── modern_llm_mapper.py
│   │   ├── OLD-NEW-TECNIQUES.docx
│   │   ├── OLD-NEW-TECNIQUES.pdf
│   │   ├── production_files.md
│   │   ├── SETUP_AND_RUN.docx
│   │   └── SETUP_AND_RUN.pdf
│   ├── USAGE-DEMO.md
│   ├─
│   ├── usage-demo-tools.md
│   ├── USAGE_LINKEDIN_DEMO.md
│   ├── utils
│   │   ├── demo_helpers.py
│   │   └── __init__.py
│   ├── WEB-DEMO-SETUP.md
│   └── WEB-DEMO-SETUP.pdf
├── docs
│   ├── docs.txt
│   ├── llm_history
│   │   ├── ai-agents-timeline.docx
│   │   ├── cronolgy_mapper.docx
│   │   ├── hypatiax-technology-evolution-timeline.docx
│   │   └── timeline_mapper.docx
│   └── run_ner_training
│       ├── run_test_parallel_code_integration-tools.md
│       ├── run_time_bundle_code_tools.md
│       ├── run_time_code_errors.md
│       ├── run_time_code_seq_tools.md
│       └── run_time_parallels_simulations_code.md
├── examples
│   ├── basic_usage.py
│   ├── evaluation_example.py
│   ├── __init__.py
│   └── training_example.py
├── experiments
│   ├── basic
│   │   ├── basic-strategies.pdf
│   │   ├── comparion.py
│   │   ├── entities_mapping.py
│   │   ├── __init__.py
│   │   ├── joint_training_output.txt
│   │   ├
│   │   ├── joint_training.py
│   │   ├── seq_flow.obj
│   │   ├── seq_flow.pdf
│   │   ├── seq-pipeline.svg
│   │   ├── sequential_pipeline_output.txt
│   │   ├── sequential_pipeline.py
│   │   ├
│   │   ├── strategy-comparison.html
│   │   ├── usage-strategy1-1.2.md
│   │   └── usage_strategy.md
│   └── __init__.py
├── __init__.py
├── mappings
│   ├── __init__.py
│   └── mapping.py
├── migrate_tests.py
├── models
│   ├── __init__.py
│   ├── __pycache__
│   │   
│   └── queries
│       ├── __init__.py
│       ├── __pycache__
│       │   
│       └── tableau
│           ├── checkpoints
│           │   └── __init__.py
│           ├── __init__.py
│           ├── model_configs
│           │   └── __init__.py
│           ├── __pycache__
│           │   
│           ├── trained_models
│           │   ├── Combined_multi_task_data_400.0.5.8
│           │   │   ├── attribute_ruler
│           │   │   │   └── patterns
│           │   │   ├── config.cfg
│           │   │   ├── lemmatizer
│           │   │   │   └── lookups
│           │   │   │       └── lookups.bin
│           │   │   ├── meta.json
│           │   │   ├── ner
│           │   │   │   ├── cfg
│           │   │   │   ├── model
│           │   │   │   └── moves
│           │   │   ├── parser
│           │   │   │   ├── cfg
│           │   │   │   ├── model
│           │   │   │   └── moves
│           │   │   ├── senter
│           │   │   │   ├── cfg
│           │   │   │   └── model
│           │   │   ├── tagger
│           │   │   │   ├── cfg
│           │   │   │   └── model
│           │   │   ├── tok2vec
│           │   │   │   ├── cfg
│           │   │   │   └── model
│           │   │   ├── tokenizer
│           │   │   └── vocab
│           │   │       ├── key2row
│           │   │       ├── lookups.bin
│           │   │       ├── strings.json
│           │   │       ├── vectors
│           │   │       └── vectors.cfg
│           │   ├── __init__.py
│           │   └── __pycache__
│           │   
│           └── training_history
│               └── __init__.py
├── patterns
│   ├── custom_patterns.py
│   ├── __init__.py
│   ├── __pycache__
│   │   
│   └── queries
│       ├── __init__.py
│       ├── __pycache__
│       │   
│       └── tableau
│           ├── generation.py
│           ├── __init__.py
│           ├── __pycache__
│           ├── test_create_ruler_tableau.py
│           ├──
│           └── test_rules_tableau_patterns.py
├── __pycache__
│   ├
├── scripts_
│   ├── __init__.py
│   ├── ner_test_simultion_package.py
│   ├── run_test_parallel_code_integration.py
│   ├── run_time_bundle_code.py
│   ├── run_time_code.py
│   ├── run_time_code_seq.py
│   ├── run_time_parallel_code.py
│   ├── script_combined_data.py
│   ├── script_custom_entities.py
│   ├── script_custom_ner.py
│   └── script_custom_patterns.py
└── utils
    ├── colab.py
    ├── files_local.py
    ├── files.py
    ├── __init__.py
    ├── path_manager.py
    ├── __pycache__
    │  ├── tree_id_op.py
    └── utils.py

151 directories, 476 files

┌──(py312)(agagora㉿localhost)-[~/Downloads/LLM-HypatiaX-OLD/hypatiax]
└─$        
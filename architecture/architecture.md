──(agagora㉿localhost)-[~/Downloads/LLM-HypatiaX]
└─$ tree                                                                                                           
.
├── build
│   ├── lib
│   │   ├── hypatiax
│   │   │   ├── core
│   │   │   │   ├── deployment
│   │   │   │   │   ├── docs.txt
│   │   │   │   │   ├── evaluate_model.py
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── docs.txt
│   │   │   │   ├── evaluation
│   │   │   │   │   ├── docs.txt
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── testing_model.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── preprocessing
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── preparation_data.py
│   │   │   │   ├── run_time_bundle_code.py
│   │   │   │   ├── run_time_code.py
│   │   │   │   ├── run_time_code_seq.py
│   │   │   │   ├── run_time_parallel_code.py
│   │   │   │   └── training
│   │   │   │       ├── docs.txt
│   │   │   │       ├── __init__.py
│   │   │   │       └── training_spacy.py
│   │   │   ├── custom_entities
│   │   │   │   ├── __init__.py
│   │   │   │   └── ner_entity.py
│   │   │   ├── custom_ner
│   │   │   │   ├── custom_ruler.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── queries
│   │   │   │       ├── components
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── ruler_queries_desc.py
│   │   │   │       │   ├── ruler_queries_formulas.py
│   │   │   │       │   └── ruler_queries.py
│   │   │   │       ├── custom_queries_components.py
│   │   │   │       ├── custom_queries_desc_components.py
│   │   │   │       ├── custom_queries_formulas_components.py
│   │   │   │       ├── __init__.py
│   │   │   │       ├── rules
│   │   │   │       │   └── __init__.py
│   │   │   │       ├── scripts
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── proc_timed.py
│   │   │   │       │   ├── proc_timef.py
│   │   │   │       │   └── proc_time.py
│   │   │   │       ├── tableau
│   │   │   │       │   ├── components
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   ├── ruler_tableau_desc.py
│   │   │   │       │   │   ├── ruler_tableau_formulas.py
│   │   │   │       │   │   └── ruler_tableau.py
│   │   │   │       │   ├── custom_tableau_components.py
│   │   │   │       │   ├── custom_tableau_desc_components.py
│   │   │   │       │   ├── custom_tableau_formulas_components.py
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── rules
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   └── rules_versions
│   │   │   │       │   │       └── __init__.py
│   │   │   │       │   ├── scripts
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   ├── proc_timed.py
│   │   │   │       │   │   ├── proc_timef.py
│   │   │   │       │   │   └── proc_time.py
│   │   │   │       │   └── tests
│   │   │   │       │       ├── __init__.py
│   │   │   │       │       ├── test_F_ner_tableau_desc.py
│   │   │   │       │       ├── test_F_ner_tableau_formulas.py
│   │   │   │       │       ├── test_tableau_desc.py
│   │   │   │       │       ├── test_tableau_formulas.py
│   │   │   │       │       └── test_tableau.py
│   │   │   │       └── tests
│   │   │   │           ├── __init__.py
│   │   │   │           ├── test_F_ner_queries_desc.py
│   │   │   │           ├── test_F_ner_queries_desc.txt
│   │   │   │           ├── test_F_ner_queries_formulas.py
│   │   │   │           ├── test_F_queries_formulas.txt
│   │   │   │           ├── test_queries_both_version1.txt
│   │   │   │           ├── test_queries_desc.py
│   │   │   │           ├── test_queries_desc.txt
│   │   │   │           ├── test_queries_desc_version1.txt
│   │   │   │           ├── test_queries_formulas.py
│   │   │   │           ├── test_queries_formulas_version1.txt
│   │   │   │           └── test_queries.py
│   │   │   ├── datasets
│   │   │   │   ├── __init__.py
│   │   │   │   └── queries
│   │   │   │       ├── combined
│   │   │   │       │   ├── combined_data.py
│   │   │   │       │   └── __init__.py
│   │   │   │       ├── data
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── tableau_data.csv
│   │   │   │       │   └── test.py
│   │   │   │       ├── __init__.py
│   │   │   │       ├── normalize
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   └── test.py
│   │   │   │       ├── tableau
│   │   │   │       │   ├── data
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   └── test.py
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── testing
│   │   │   │       │   │   ├── formulas_test_combined.xlsx
│   │   │   │       │   │   ├── formulas_test_nor_combined.xlsx
│   │   │   │       │   │   ├── formulas_test_nor.xlsx
│   │   │   │       │   │   ├── formulas_test.xlsx
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   ├── test_combined.py
│   │   │   │       │   │   ├── testing_versions
│   │   │   │       │   │   │   └── __init__.py
│   │   │   │       │   │   ├── test.py
│   │   │   │       │   │   └── test_update_labels.py
│   │   │   │       │   ├── testing_spacy
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   ├── Test_desc_data.json
│   │   │   │       │   │   ├── Test_formulas_data.json
│   │   │   │       │   │   ├── testing_spacy_versions
│   │   │   │       │   │   │   └── __init__.py
│   │   │   │       │   │   ├── test.py
│   │   │   │       │   │   ├── Test_tableau_both_sm_data.json
│   │   │   │       │   │   ├── Test_tableau_desc_sm_data.json
│   │   │   │       │   │   └── Test_tableau_formulas_sm_data.json
│   │   │   │       │   ├── training
│   │   │   │       │   │   ├── formulas_combined.xlsx
│   │   │   │       │   │   ├── formulas_nor_combined.xlsx
│   │   │   │       │   │   ├── formulas_nor.xlsx
│   │   │   │       │   │   ├── formulas.xlsx
│   │   │   │       │   │   ├── gformulas_combined.xlsx
│   │   │   │       │   │   ├── gformulas.csv
│   │   │   │       │   │   ├── gformulas_nor_combined.xlsx
│   │   │   │       │   │   ├── gformulas_nor.xlsx
│   │   │   │       │   │   ├── gformulas.xlsx
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   ├── test_combined.py
│   │   │   │       │   │   ├── test.py
│   │   │   │       │   │   ├── test_update_labels.py
│   │   │   │       │   │   └── training_versions
│   │   │   │       │   │       └── __init__.py
│   │   │   │       │   ├── training_spacy
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   ├── test.py
│   │   │   │       │   │   ├── Train_desc_data.json
│   │   │   │       │   │   ├── Train_formulas_data.json
│   │   │   │       │   │   ├── training_spacy_versions
│   │   │   │       │   │   │   └── __init__.py
│   │   │   │       │   │   ├── Train_tableau_both_bsm_data.json
│   │   │   │       │   │   ├── Train_tableau_both_sm_data.json
│   │   │   │       │   │   ├── Train_tableau_desc_bsm_data.json
│   │   │   │       │   │   ├── Train_tableau_desc_sm_data.json
│   │   │   │       │   │   ├── Train_tableau_formulas_bsm_data.json
│   │   │   │       │   │   └── Train_tableau_formulas_sm_data.json
│   │   │   │       │   └── validation
│   │   │   │       │       ├── __init__.py
│   │   │   │       │       ├── test.py
│   │   │   │       │       └── validation_versions
│   │   │   │       │           └── __init__.py
│   │   │   │       ├── testing
│   │   │   │       │   ├── formulas_test_combined.xlsx
│   │   │   │       │   ├── formulas_test_nor_combined.xlsx
│   │   │   │       │   ├── formulas_test_nor.xlsx
│   │   │   │       │   ├── formulas_test.xlsx
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── test_combined.py
│   │   │   │       │   └── test.py
│   │   │   │       ├── testing_spacy
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── Test_desc_data.json
│   │   │   │       │   ├── Test_formulas_data.json
│   │   │   │       │   └── test.py
│   │   │   │       ├── training
│   │   │   │       │   ├── formulas_combined.xlsx
│   │   │   │       │   ├── formulas_nor_combined.xlsx
│   │   │   │       │   ├── formulas_nor.xlsx
│   │   │   │       │   ├── formulas.xlsx
│   │   │   │       │   ├── gformulas_combined.xlsx
│   │   │   │       │   ├── gformulas_nor_combined.xlsx
│   │   │   │       │   ├── gformulas_nor.xlsx
│   │   │   │       │   ├── gformulas.xlsx
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── test_combined.py
│   │   │   │       │   └── test.py
│   │   │   │       ├── training_spacy
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── test.py
│   │   │   │       │   ├── Train_desc_data.json
│   │   │   │       │   └── Train_formulas_data.json
│   │   │   │       └── validation
│   │   │   │           ├── __init__.py
│   │   │   │           └── test.py
│   │   │   ├── data_spacy
│   │   │   │   ├── corpus
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── embedding
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pipelines
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── pre_trained_models
│   │   │   │   │   ├── en_core_web_sm
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   └── meta.json
│   │   │   │   │   └── __init__.py
│   │   │   │   └── queries
│   │   │   │       ├── __init__.py
│   │   │   │       ├── ner_queries
│   │   │   │       │   ├── config.cfg
│   │   │   │       │   ├── meta.json
│   │   │   │       │   └── tokenizer
│   │   │   │       ├── ner_queries_desc
│   │   │   │       │   ├── config.cfg
│   │   │   │       │   ├── meta.json
│   │   │   │       │   └── tokenizer
│   │   │   │       ├── ner_queries_formulas
│   │   │   │       │   ├── config.cfg
│   │   │   │       │   ├── meta.json
│   │   │   │       │   └── tokenizer
│   │   │   │       ├── ner_versions
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   └── version03052024-2209
│   │   │   │       │       ├── __init__.py
│   │   │   │       │       ├── ner_queries
│   │   │   │       │       │   ├── attribute_ruler
│   │   │   │       │       │   │   └── patterns
│   │   │   │       │       │   ├── config.cfg
│   │   │   │       │       │   ├── lemmatizer
│   │   │   │       │       │   │   └── lookups
│   │   │   │       │       │   │       └── lookups.bin
│   │   │   │       │       │   ├── meta.json
│   │   │   │       │       │   ├── ner
│   │   │   │       │       │   │   ├── cfg
│   │   │   │       │       │   │   ├── model
│   │   │   │       │       │   │   └── moves
│   │   │   │       │       │   ├── parser
│   │   │   │       │       │   │   ├── cfg
│   │   │   │       │       │   │   ├── model
│   │   │   │       │       │   │   └── moves
│   │   │   │       │       │   ├── senter
│   │   │   │       │       │   │   ├── cfg
│   │   │   │       │       │   │   └── model
│   │   │   │       │       │   ├── tagger
│   │   │   │       │       │   │   ├── cfg
│   │   │   │       │       │   │   └── model
│   │   │   │       │       │   ├── tok2vec
│   │   │   │       │       │   │   ├── cfg
│   │   │   │       │       │   │   └── model
│   │   │   │       │       │   ├── tokenizer
│   │   │   │       │       │   └── vocab
│   │   │   │       │       │       ├── key2row
│   │   │   │       │       │       ├── lookups.bin
│   │   │   │       │       │       ├── strings.json
│   │   │   │       │       │       ├── vectors
│   │   │   │       │       │       └── vectors.cfg
│   │   │   │       │       ├── ner_queries_desc
│   │   │   │       │       │   ├── attribute_ruler
│   │   │   │       │       │   │   └── patterns
│   │   │   │       │       │   ├── config.cfg
│   │   │   │       │       │   ├── lemmatizer
│   │   │   │       │       │   │   └── lookups
│   │   │   │       │       │   │       └── lookups.bin
│   │   │   │       │       │   ├── meta.json
│   │   │   │       │       │   ├── ner
│   │   │   │       │       │   │   ├── cfg
│   │   │   │       │       │   │   ├── model
│   │   │   │       │       │   │   └── moves
│   │   │   │       │       │   ├── parser
│   │   │   │       │       │   │   ├── cfg
│   │   │   │       │       │   │   ├── model
│   │   │   │       │       │   │   └── moves
│   │   │   │       │       │   ├── senter
│   │   │   │       │       │   │   ├── cfg
│   │   │   │       │       │   │   └── model
│   │   │   │       │       │   ├── tagger
│   │   │   │       │       │   │   ├── cfg
│   │   │   │       │       │   │   └── model
│   │   │   │       │       │   ├── tok2vec
│   │   │   │       │       │   │   ├── cfg
│   │   │   │       │       │   │   └── model
│   │   │   │       │       │   ├── tokenizer
│   │   │   │       │       │   └── vocab
│   │   │   │       │       │       ├── key2row
│   │   │   │       │       │       ├── lookups.bin
│   │   │   │       │       │       ├── strings.json
│   │   │   │       │       │       ├── vectors
│   │   │   │       │       │       └── vectors.cfg
│   │   │   │       │       └── ner_queries_formulas
│   │   │   │       │           ├── attribute_ruler
│   │   │   │       │           │   └── patterns
│   │   │   │       │           ├── config.cfg
│   │   │   │       │           ├── lemmatizer
│   │   │   │       │           │   └── lookups
│   │   │   │       │           │       └── lookups.bin
│   │   │   │       │           ├── meta.json
│   │   │   │       │           ├── ner
│   │   │   │       │           │   ├── cfg
│   │   │   │       │           │   ├── model
│   │   │   │       │           │   └── moves
│   │   │   │       │           ├── parser
│   │   │   │       │           │   ├── cfg
│   │   │   │       │           │   ├── model
│   │   │   │       │           │   └── moves
│   │   │   │       │           ├── senter
│   │   │   │       │           │   ├── cfg
│   │   │   │       │           │   └── model
│   │   │   │       │           ├── tagger
│   │   │   │       │           │   ├── cfg
│   │   │   │       │           │   └── model
│   │   │   │       │           ├── tok2vec
│   │   │   │       │           │   ├── cfg
│   │   │   │       │           │   └── model
│   │   │   │       │           ├── tokenizer
│   │   │   │       │           └── vocab
│   │   │   │       │               ├── key2row
│   │   │   │       │               ├── lookups.bin
│   │   │   │       │               ├── strings.json
│   │   │   │       │               ├── vectors
│   │   │   │       │               └── vectors.cfg
│   │   │   │       ├── tableau
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── ner_versions
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   └── version03052024-2209
│   │   │   │       │   │       └── __init__.py
│   │   │   │       │   ├── testing_spacy
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   ├── Test_desc_data.spacy
│   │   │   │       │   │   ├── Test_formulas_data.spacy
│   │   │   │       │   │   ├── testing_spacy_versions
│   │   │   │       │   │   │   └── __init__.py
│   │   │   │       │   │   ├── test.py
│   │   │   │       │   │   ├── Test_tableau_both_dsm_data.spacy
│   │   │   │       │   │   ├── Test_tableau_desc_sm_data.spacy
│   │   │   │       │   │   └── Test_tableau_formulas_sm_data.spacy
│   │   │   │       │   ├── test_ner_desc.py
│   │   │   │       │   ├── test_ner_formulas.py
│   │   │   │       │   ├── training_spacy
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   ├── test.py
│   │   │   │       │   │   ├── Train_desc_data.spacy
│   │   │   │       │   │   ├── Train_formulas_data.spacy
│   │   │   │       │   │   ├── training_spacy_versions
│   │   │   │       │   │   │   └── __init__.py
│   │   │   │       │   │   ├── Train_tableau_both_bdsm_data.spacy
│   │   │   │       │   │   ├── Train_tableau_both_dsm_data.spacy
│   │   │   │       │   │   ├── Train_tableau_desc_bsm_data.spacy
│   │   │   │       │   │   ├── Train_tableau_desc_sm_data.spacy
│   │   │   │       │   │   ├── Train_tableau_formulas_bsm_data.spacy
│   │   │   │       │   │   └── Train_tableau_formulas_sm_data.spacy
│   │   │   │       │   └── vocab
│   │   │   │       │       ├── __init__.py
│   │   │   │       │       ├── vocab_tableau_both_Combined_bdsm
│   │   │   │       │       ├── vocab_tableau_both_Combined_dsm
│   │   │   │       │       ├── vocab_tableau_desc_Description_bsm
│   │   │   │       │       ├── vocab_tableau_desc_Description_sm
│   │   │   │       │       ├── vocab_tableau_formulas_Formula (Tableau)_bsm
│   │   │   │       │       ├── vocab_tableau_formulas_Formula (Tableau)_sm
│   │   │   │       │       └── vocab_versions
│   │   │   │       │           ├── __init__.py
│   │   │   │       │           └── version-09052024-1705
│   │   │   │       │               └── __init__.py
│   │   │   │       ├── testing_spacy
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── Test_desc_data.spacy
│   │   │   │       │   ├── Test_formulas_data.spacy
│   │   │   │       │   └── test.py
│   │   │   │       ├── test_ner_desc.py
│   │   │   │       ├── test_ner_formulas.py
│   │   │   │       ├── training_spacy
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── test.py
│   │   │   │       │   ├── Train_desc_data.spacy
│   │   │   │       │   └── Train_formulas_data.spacy
│   │   │   │       └── vocab
│   │   │   │           ├── __init__.py
│   │   │   │           └── version-03052024-2209
│   │   │   │               └── __init__.py
│   │   │   ├── __init__.py
│   │   │   ├── mappings
│   │   │   │   ├── __init__.py
│   │   │   │   └── mapping.py
│   │   │   ├── models
│   │   │   │   ├── __init__.py
│   │   │   │   └── queries
│   │   │   │       ├── checkpoints
│   │   │   │       │   └── __init__.py
│   │   │   │       ├── __init__.py
│   │   │   │       ├── model_configs
│   │   │   │       │   └── __init__.py
│   │   │   │       ├── tableau
│   │   │   │       │   ├── checkpoints
│   │   │   │       │   │   └── __init__.py
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── model_configs
│   │   │   │       │   │   └── __init__.py
│   │   │   │       │   ├── trained_models
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   ├── test_comb_multi_task_model.py
│   │   │   │       │   │   ├── test_description_model.py
│   │   │   │       │   │   ├── test_formulas_model.py
│   │   │   │       │   │   └── trained_models_versions
│   │   │   │       │   │       └── __init__.py
│   │   │   │       │   └── training_history
│   │   │   │       │       ├── __init__.py
│   │   │   │       │       └── training_history_versions
│   │   │   │       │           └── __init__.py
│   │   │   │       ├── trained_models
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── test_comb_multi_task_model.py
│   │   │   │       │   ├── test_description_model.py
│   │   │   │       │   ├── test_description_model.txt
│   │   │   │       │   ├── test_formulas_model.py
│   │   │   │       │   ├── test_formulas_model.txt
│   │   │   │       │   ├── test_multi_task_400_model.txt
│   │   │   │       │   └── versions
│   │   │   │       │       └── __init__.py
│   │   │   │       └── training_history
│   │   │   │           └── __init__.py
│   │   │   ├── patterns
│   │   │   │   ├── custom_patterns.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── queries
│   │   │   │       ├── generation.py
│   │   │   │       ├── __init__.py
│   │   │   │       ├── patterns_queries.txt
│   │   │   │       ├── tableau
│   │   │   │       │   ├── generation.py
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── test_create_ruler_tableau.py
│   │   │   │       │   └── test_rules_tableau_patterns.py
│   │   │   │       ├── test_create_ruler_queries.py
│   │   │   │       ├── test.py
│   │   │   │       ├── test_rules_queries_patterns.py
│   │   │   │       └── test_rules_queries_patterns.txt
│   │   │   ├── scripts_
│   │   │   │   ├── __init__.py
│   │   │   │   ├── script_combined_data.py
│   │   │   │   ├── script_custom_entities.py
│   │   │   │   ├── script_custom_ner.py
│   │   │   │   └── script_custom_patterns.py
│   │   │   └── utils
│   │   │       ├── colab.py
│   │   │       ├── files_local.py
│   │   │       ├── files.py
│   │   │       ├── __init__.py
│   │   │       ├── tree_id_op.py
│   │   │       └── utils.py
│   │   └── tests
│   │       ├── docs.py
│   │       ├── __init__.py
│   │       ├── test_desc_formulas.py
│   │       ├── test_desc_formulas.txt
│   │       ├── test_desc.py
│   │       ├── test_desc.txt
│   │       ├── test_entity_desc.py
│   │       ├── test_entity_formulas.py
│   │       ├── test_formulas.py
│   │       ├── test_formulas.txt
│   │       ├── test_read_files.py
│   │       └── test_rename_files.py
│   └── scripts-3.11
│       ├── script_combined_data.py
│       ├── script_custom_entities.py
│       ├── script_custom_ner.py
│       └── script_custom_patterns.py
├── dist
│   ├── hypatiax-0.1.1.dev1+gffab0de-py3-none-any.whl
│   ├── hypatiax-0.1.1.dev1+gffab0de.tar.gz
│   ├── hypatiax-0.1.1.dev2+g11d0743.d20240418-py3-none-any.whl
│   ├── hypatiax-0.1.1.dev2+g11d0743.d20240418.tar.gz
│   ├── hypatiax-0.1.1.dev2+g11d0743.d20240419-py3-none-any.whl
│   ├── hypatiax-0.1.1.dev2+g11d0743.d20240419.tar.gz
│   ├── hypatiax-0.1.1.dev2+g11d0743.d20240506-py3-none-any.whl
│   ├── hypatiax-0.1.1.dev2+g11d0743.d20240506.tar.gz
│   ├── hypatiax-0.1.1.dev2+g11d0743.d20240518-py3-none-any.whl
│   ├── hypatiax-0.1.1.dev2+g11d0743.d20240518.tar.gz
│   ├── hypatiax-0.1.1.dev8+ge54293f.d20240519-py3-none-any.whl
│   ├── hypatiax-0.1.1.dev8+ge54293f.d20240519.tar.gz
│   ├── hypatiax-0.1.1.dev8+ge54293f.d20250301-py3-none-any.whl
│   ├── hypatiax-0.1.1.dev8+ge54293f.d20250301.tar.gz
│   ├── hypatiax-0.1.dev1+g44d3a40.d20240418-py3-none-any.whl
│   └── hypatiax-0.1.dev1+g44d3a40.d20240418.tar.gz
├── FreelancerLLM-HypatiaX.docx
├── hypatiax
│   ├── core
│   │   ├── deployment
│   │   │   ├── docs.txt
│   │   │   ├── evaluate_model.py
│   │   │   └── __init__.py
│   │   ├── docs.txt
│   │   ├── evaluation
│   │   │   ├── docs.txt
│   │   │   ├── __init__.py
│   │   │   └── testing_model.py
│   │   ├── __init__.py
│   │   ├── preprocessing
│   │   │   ├── __init__.py
│   │   │   └── preparation_data.py
│   │   ├── run_time_bundle_code.py
│   │   ├── run_time_code.py
│   │   ├── run_time_code_seq.py
│   │   ├── run_time_parallel_code.py
│   │   └── training
│   │       ├── docs.txt
│   │       ├── __init__.py
│   │       └── training_spacy.py
│   ├── custom_entities
│   │   ├── __init__.py
│   │   └── ner_entity.py
│   ├── custom_ner
│   │   ├── custom_ruler.py
│   │   ├── __init__.py
│   │   └── queries
│   │       ├── __init__.py
│   │       └── tableau
│   │           ├── components
│   │           │   ├── __init__.py
│   │           │   ├── ruler_tableau_desc.py
│   │           │   ├── ruler_tableau_formulas.py
│   │           │   └── ruler_tableau.py
│   │           ├── custom_tableau_components.py
│   │           ├── custom_tableau_desc_components.py
│   │           ├── custom_tableau_formulas_components.py
│   │           ├── __init__.py
│   │           ├── rules
│   │           │   ├── __init__.py
│   │           │   ├── ruler_tableau_desc.jsonl
│   │           │   ├── ruler_tableau_formulas.jsonl
│   │           │   ├── ruler_tableau.jsonl
│   │           │   └── rules_versions
│   │           │       └── __init__.py
│   │           ├── scripts
│   │           │   ├── __init__.py
│   │           │   ├── proc_timed.py
│   │           │   ├── proc_timef.py
│   │           │   └── proc_time.py
│   │           └── tests
│   │               ├── __init__.py
│   │               ├── test_F_ner_tableau_desc.py
│   │               ├── test_F_ner_tableau_formulas.py
│   │               ├── #test_tableau_desc.py#
│   │               ├── test_tableau_desc.py
│   │               ├── test_tableau_formulas.py
│   │               └── test_tableau.py
│   ├── datasets
│   │   ├── __init__.py
│   │   └── queries
│   │       ├── combined
│   │       │   ├── combined_data.py
│   │       │   └── __init__.py
│   │       ├── __init__.py
│   │       ├── normalize
│   │       │   ├── __init__.py
│   │       │   └── test.py
│   │       └── tableau
│   │           ├── data
│   │           │   ├── __init__.py
│   │           │   ├── tableau_data.csv
│   │           │   └── test.py
│   │           ├── __init__.py
│   │           ├── testing
│   │           │   ├── formulas_test_combined.xlsx
│   │           │   ├── formulas_test_nor_combined.xlsx
│   │           │   ├── formulas_test_nor.xlsx
│   │           │   ├── formulas_test.xlsx
│   │           │   ├── __init__.py
│   │           │   ├── test_combined.py
│   │           │   ├── testing_versions
│   │           │   │   └── __init__.py
│   │           │   ├── test.py
│   │           │   └── test_update_labels.py
│   │           ├── testing_spacy
│   │           │   ├── __init__.py
│   │           │   ├── Test_desc_data.json
│   │           │   ├── Test_formulas_data.json
│   │           │   ├── testing_spacy_versions
│   │           │   │   └── __init__.py
│   │           │   ├── test.py
│   │           │   ├── Test_tableau_both_sm_data.json
│   │           │   ├── Test_tableau_desc_sm_data.json
│   │           │   └── Test_tableau_formulas_sm_data.json
│   │           ├── training
│   │           │   ├── formulas_combined.xlsx
│   │           │   ├── formulas_nor_combined.xlsx
│   │           │   ├── formulas_nor.xlsx
│   │           │   ├── formulas.xlsx
│   │           │   ├── gformulas_combined.xlsx
│   │           │   ├── gformulas.csv
│   │           │   ├── gformulas_nor_combined.xlsx
│   │           │   ├── gformulas_nor.xlsx
│   │           │   ├── gformulas.xlsx
│   │           │   ├── __init__.py
│   │           │   ├── test_combined.py
│   │           │   ├── test.py
│   │           │   ├── test_update_labels.py
│   │           │   └── training_versions
│   │           │       └── __init__.py
│   │           ├── training_spacy
│   │           │   ├── __init__.py
│   │           │   ├── test.py
│   │           │   ├── Train_desc_data.json
│   │           │   ├── Train_formulas_data.json
│   │           │   ├── training_spacy_versions
│   │           │   │   └── __init__.py
│   │           │   ├── Train_tableau_both_bsm_data.json
│   │           │   ├── Train_tableau_both_sm_data.json
│   │           │   ├── Train_tableau_desc_bsm_data.json
│   │           │   ├── Train_tableau_desc_sm_data.json
│   │           │   ├── Train_tableau_formulas_bsm_data.json
│   │           │   └── Train_tableau_formulas_sm_data.json
│   │           ├── validation
│   │           │   ├── __init__.py
│   │           │   ├── test.py
│   │           │   └── validation_versions
│   │           │       └── __init__.py
│   │           └── validation_spacy
│   │               └── __init__.py
│   ├── data_spacy
│   │   ├── corpus
│   │   │   └── __init__.py
│   │   ├── embedding
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── pipelines
│   │   │   └── __init__.py
│   │   ├── pre_trained_models
│   │   │   ├── en_core_web_sm
│   │   │   │   ├── en_core_web_sm-3.7.1
│   │   │   │   │   ├── accuracy.json
│   │   │   │   │   ├── attribute_ruler
│   │   │   │   │   │   └── patterns
│   │   │   │   │   ├── config.cfg
│   │   │   │   │   ├── lemmatizer
│   │   │   │   │   │   └── lookups
│   │   │   │   │   │       └── lookups.bin
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── LICENSES_SOURCES
│   │   │   │   │   ├── meta.json
│   │   │   │   │   ├── ner
│   │   │   │   │   │   ├── cfg
│   │   │   │   │   │   ├── model
│   │   │   │   │   │   └── moves
│   │   │   │   │   ├── parser
│   │   │   │   │   │   ├── cfg
│   │   │   │   │   │   ├── model
│   │   │   │   │   │   └── moves
│   │   │   │   │   ├── README.md
│   │   │   │   │   ├── senter
│   │   │   │   │   │   ├── cfg
│   │   │   │   │   │   └── model
│   │   │   │   │   ├── tagger
│   │   │   │   │   │   ├── cfg
│   │   │   │   │   │   └── model
│   │   │   │   │   ├── tok2vec
│   │   │   │   │   │   ├── cfg
│   │   │   │   │   │   └── model
│   │   │   │   │   ├── tokenizer
│   │   │   │   │   └── vocab
│   │   │   │   │       ├── key2row
│   │   │   │   │       ├── lookups.bin
│   │   │   │   │       ├── strings.json
│   │   │   │   │       ├── vectors
│   │   │   │   │       └── vectors.cfg
│   │   │   │   ├── __init__.py
│   │   │   │   └── meta.json
│   │   │   ├── en_core_web_sm-3.7.1.dist-info
│   │   │   │   ├── direct_url.json
│   │   │   │   ├── entry_points.txt
│   │   │   │   ├── INSTALLER
│   │   │   │   ├── LICENSE
│   │   │   │   ├── LICENSES_SOURCES
│   │   │   │   ├── METADATA
│   │   │   │   ├── RECORD
│   │   │   │   ├── REQUESTED
│   │   │   │   ├── top_level.txt
│   │   │   │   └── WHEEL
│   │   │   └── __init__.py
│   │   └── queries
│   │       ├── __init__.py
│   │       └── tableau
│   │           ├── __init__.py
│   │           ├── ner_tableau
│   │           │   ├── attribute_ruler
│   │           │   │   └── patterns
│   │           │   ├── config.cfg
│   │           │   ├── lemmatizer
│   │           │   │   └── lookups
│   │           │   │       └── lookups.bin
│   │           │   ├── meta.json
│   │           │   ├── ner
│   │           │   │   ├── cfg
│   │           │   │   ├── model
│   │           │   │   └── moves
│   │           │   ├── parser
│   │           │   │   ├── cfg
│   │           │   │   ├── model
│   │           │   │   └── moves
│   │           │   ├── senter
│   │           │   │   ├── cfg
│   │           │   │   └── model
│   │           │   ├── tagger
│   │           │   │   ├── cfg
│   │           │   │   └── model
│   │           │   ├── tok2vec
│   │           │   │   ├── cfg
│   │           │   │   └── model
│   │           │   ├── tokenizer
│   │           │   └── vocab
│   │           │       ├── key2row
│   │           │       ├── lookups.bin
│   │           │       ├── strings.json
│   │           │       ├── vectors
│   │           │       └── vectors.cfg
│   │           ├── ner_tableau_desc
│   │           │   ├── attribute_ruler
│   │           │   │   └── patterns
│   │           │   ├── config.cfg
│   │           │   ├── lemmatizer
│   │           │   │   └── lookups
│   │           │   │       └── lookups.bin
│   │           │   ├── meta.json
│   │           │   ├── ner
│   │           │   │   ├── cfg
│   │           │   │   ├── model
│   │           │   │   └── moves
│   │           │   ├── parser
│   │           │   │   ├── cfg
│   │           │   │   ├── model
│   │           │   │   └── moves
│   │           │   ├── senter
│   │           │   │   ├── cfg
│   │           │   │   └── model
│   │           │   ├── tagger
│   │           │   │   ├── cfg
│   │           │   │   └── model
│   │           │   ├── tok2vec
│   │           │   │   ├── cfg
│   │           │   │   └── model
│   │           │   ├── tokenizer
│   │           │   └── vocab
│   │           │       ├── key2row
│   │           │       ├── lookups.bin
│   │           │       ├── strings.json
│   │           │       ├── vectors
│   │           │       └── vectors.cfg
│   │           ├── ner_tableau_formulas
│   │           │   ├── attribute_ruler
│   │           │   │   └── patterns
│   │           │   ├── config.cfg
│   │           │   ├── lemmatizer
│   │           │   │   └── lookups
│   │           │   │       └── lookups.bin
│   │           │   ├── meta.json
│   │           │   ├── ner
│   │           │   │   ├── cfg
│   │           │   │   ├── model
│   │           │   │   └── moves
│   │           │   ├── parser
│   │           │   │   ├── cfg
│   │           │   │   ├── model
│   │           │   │   └── moves
│   │           │   ├── senter
│   │           │   │   ├── cfg
│   │           │   │   └── model
│   │           │   ├── tagger
│   │           │   │   ├── cfg
│   │           │   │   └── model
│   │           │   ├── tok2vec
│   │           │   │   ├── cfg
│   │           │   │   └── model
│   │           │   ├── tokenizer
│   │           │   └── vocab
│   │           │       ├── key2row
│   │           │       ├── lookups.bin
│   │           │       ├── strings.json
│   │           │       ├── vectors
│   │           │       └── vectors.cfg
│   │           ├── ner_versions
│   │           │   ├── __init__.py
│   │           │   └── version03052024-2209
│   │           │       ├── __init__.py
│   │           │       ├── ner_queries
│   │           │       │   ├── attribute_ruler
│   │           │       │   │   └── patterns
│   │           │       │   ├── config.cfg
│   │           │       │   ├── lemmatizer
│   │           │       │   │   └── lookups
│   │           │       │   │       └── lookups.bin
│   │           │       │   ├── meta.json
│   │           │       │   ├── ner
│   │           │       │   │   ├── cfg
│   │           │       │   │   ├── model
│   │           │       │   │   └── moves
│   │           │       │   ├── parser
│   │           │       │   │   ├── cfg
│   │           │       │   │   ├── model
│   │           │       │   │   └── moves
│   │           │       │   ├── senter
│   │           │       │   │   ├── cfg
│   │           │       │   │   └── model
│   │           │       │   ├── tagger
│   │           │       │   │   ├── cfg
│   │           │       │   │   └── model
│   │           │       │   ├── tok2vec
│   │           │       │   │   ├── cfg
│   │           │       │   │   └── model
│   │           │       │   ├── tokenizer
│   │           │       │   └── vocab
│   │           │       │       ├── key2row
│   │           │       │       ├── lookups.bin
│   │           │       │       ├── strings.json
│   │           │       │       ├── vectors
│   │           │       │       └── vectors.cfg
│   │           │       ├── ner_queries_desc
│   │           │       │   ├── attribute_ruler
│   │           │       │   │   └── patterns
│   │           │       │   ├── config.cfg
│   │           │       │   ├── lemmatizer
│   │           │       │   │   └── lookups
│   │           │       │   │       └── lookups.bin
│   │           │       │   ├── meta.json
│   │           │       │   ├── ner
│   │           │       │   │   ├── cfg
│   │           │       │   │   ├── model
│   │           │       │   │   └── moves
│   │           │       │   ├── parser
│   │           │       │   │   ├── cfg
│   │           │       │   │   ├── model
│   │           │       │   │   └── moves
│   │           │       │   ├── senter
│   │           │       │   │   ├── cfg
│   │           │       │   │   └── model
│   │           │       │   ├── tagger
│   │           │       │   │   ├── cfg
│   │           │       │   │   └── model
│   │           │       │   ├── tok2vec
│   │           │       │   │   ├── cfg
│   │           │       │   │   └── model
│   │           │       │   ├── tokenizer
│   │           │       │   └── vocab
│   │           │       │       ├── key2row
│   │           │       │       ├── lookups.bin
│   │           │       │       ├── strings.json
│   │           │       │       ├── vectors
│   │           │       │       └── vectors.cfg
│   │           │       └── ner_queries_formulas
│   │           │           ├── attribute_ruler
│   │           │           │   └── patterns
│   │           │           ├── config.cfg
│   │           │           ├── lemmatizer
│   │           │           │   └── lookups
│   │           │           │       └── lookups.bin
│   │           │           ├── meta.json
│   │           │           ├── ner
│   │           │           │   ├── cfg
│   │           │           │   ├── model
│   │           │           │   └── moves
│   │           │           ├── parser
│   │           │           │   ├── cfg
│   │           │           │   ├── model
│   │           │           │   └── moves
│   │           │           ├── senter
│   │           │           │   ├── cfg
│   │           │           │   └── model
│   │           │           ├── tagger
│   │           │           │   ├── cfg
│   │           │           │   └── model
│   │           │           ├── tok2vec
│   │           │           │   ├── cfg
│   │           │           │   └── model
│   │           │           ├── tokenizer
│   │           │           └── vocab
│   │           │               ├── key2row
│   │           │               ├── lookups.bin
│   │           │               ├── strings.json
│   │           │               ├── vectors
│   │           │               └── vectors.cfg
│   │           ├── testing_spacy
│   │           │   ├── __init__.py
│   │           │   ├── Test_desc_data.spacy
│   │           │   ├── Test_formulas_data.spacy
│   │           │   ├── testing_spacy_versions
│   │           │   │   └── __init__.py
│   │           │   ├── test.py
│   │           │   ├── Test_tableau_both_dsm_data.spacy
│   │           │   ├── Test_tableau_desc_sm_data.spacy
│   │           │   └── Test_tableau_formulas_sm_data.spacy
│   │           ├── test_ner_desc.py
│   │           ├── test_ner_formulas.py
│   │           ├── training_spacy
│   │           │   ├── __init__.py
│   │           │   ├── test.py
│   │           │   ├── Train_desc_data.spacy
│   │           │   ├── Train_formulas_data.spacy
│   │           │   ├── training_spacy_versions
│   │           │   │   └── __init__.py
│   │           │   ├── Train_tableau_both_bdsm_data.spacy
│   │           │   ├── Train_tableau_both_dsm_data.spacy
│   │           │   ├── Train_tableau_desc_bsm_data.spacy
│   │           │   ├── Train_tableau_desc_sm_data.spacy
│   │           │   ├── Train_tableau_formulas_bsm_data.spacy
│   │           │   └── Train_tableau_formulas_sm_data.spacy
│   │           └── vocab
│   │               ├── __init__.py
│   │               ├── vocab_tableau_both_Combined_bdsm
│   │               ├── vocab_tableau_both_Combined_dsm
│   │               ├── vocab_tableau_desc_Description_bsm
│   │               ├── vocab_tableau_desc_Description_sm
│   │               ├── vocab_tableau_formulas_Formula (Tableau)_bsm
│   │               ├── vocab_tableau_formulas_Formula (Tableau)_sm
│   │               └── vocab_versions
│   │                   ├── __init__.py
│   │                   └── version-09052024-1705
│   │                       └── __init__.py
│   ├── __init__.py
│   ├── mappings
│   │   ├── __init__.py
│   │   └── mapping.py
│   ├── models
│   │   ├── __init__.py
│   │   └── queries
│   │       ├── __init__.py
│   │       └── tableau
│   │           ├── checkpoints
│   │           │   └── __init__.py
│   │           ├── __init__.py
│   │           ├── model_configs
│   │           │   └── __init__.py
│   │           ├── trained_models
│   │           │   ├── __init__.py
│   │           │   ├── test_comb_multi_task_model.py
│   │           │   ├── test_description_model.py
│   │           │   ├── test_formulas_model.py
│   │           │   └── trained_models_versions
│   │           │       └── __init__.py
│   │           └── training_history
│   │               ├── __init__.py
│   │               └── training_history_versions
│   │                   └── __init__.py
│   ├── patterns
│   │   ├── custom_patterns.py
│   │   ├── __init__.py
│   │   └── queries
│   │       ├── __init__.py
│   │       └── tableau
│   │           ├── generation.py
│   │           ├── __init__.py
│   │           ├── test_create_ruler_tableau.py
│   │           └── test_rules_tableau_patterns.py
│   ├── scripts_
│   │   ├── __init__.py
│   │   ├── script_combined_data.py
│   │   ├── script_custom_entities.py
│   │   ├── script_custom_entities.py~
│   │   ├── script_custom_ner.py
│   │   └── script_custom_patterns.py
│   └── utils
│       ├── colab.py
│       ├── colab.py~
│       ├── files_local.py
│       ├── files.py
│       ├── __init__.py
│       ├── tree_id_op.py
│       └── utils.py
├── hypatiax.egg-info
│   ├── dependency_links.txt
│   ├── entry_points.txt
│   ├── not-zip-safe
│   ├── PKG-INFO
│   ├── requires.txt
│   ├── SOURCES.txt
│   └── top_level.txt
├── HypatiaX-OCt2024.docx
├── hypatiax_versions
│   ├── core
│   │   ├── deployment
│   │   │   └── __init__.py
│   │   ├── evaluation
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── preprocessing
│   │   │   └── __init__.py
│   │   └── training
│   │       └── __init__.py
│   ├── custom_entities
│   │   └── __init__.py
│   ├── custom_ner
│   │   ├── __init__.py
│   │   └── queries
│   │       └── tableau
│   │           ├── components
│   │           │   └── __init__.py
│   │           ├── custom_tableau_components.py
│   │           ├── custom_tableau_desc_components.py
│   │           ├── custom_tableau_formulas_components.py
│   │           ├── __init__.py
│   │           ├── rules
│   │           │   ├── __init__.py
│   │           │   └── rules_versions
│   │           │       └── __init__.py
│   │           ├── scripts
│   │           │   └── __init__.py
│   │           └── tests
│   │               ├── __init__.py
│   │               ├── test_F_ner_tableau_desc.py
│   │               ├── test_F_ner_tableau_formulas.py
│   │               ├── test_tableau_desc.py
│   │               ├── test_tableau_formulas.py
│   │               └── test_tableau.py
│   ├── datasets
│   │   ├── __init__.py
│   │   └── queries
│   │       ├── combined
│   │       │   └── __init__.py
│   │       ├── __init__.py
│   │       ├── normalize
│   │       │   ├── __init__.py
│   │       │   └── test.py
│   │       └── tableau
│   │           ├── data
│   │           │   ├── __init__.py
│   │           │   ├── tableau_data.csv
│   │           │   └── test.py
│   │           ├── __init__.py
│   │           ├── testing
│   │           │   ├── formulas_test_combined.xlsx
│   │           │   ├── formulas_test_nor_combined.xlsx
│   │           │   ├── formulas_test_nor.xlsx
│   │           │   ├── formulas_test.xlsx
│   │           │   ├── __init__.py
│   │           │   ├── test_combined.py
│   │           │   ├── testing_versions
│   │           │   │   └── __init__.py
│   │           │   ├── test.py
│   │           │   └── test_update_labels.py
│   │           ├── testing_spacy
│   │           │   ├── __init__.py
│   │           │   ├── Test_desc_data.json
│   │           │   ├── Test_formulas_data.json
│   │           │   ├── testing_spacy_versions
│   │           │   │   └── __init__.py
│   │           │   ├── test.py
│   │           │   ├── Test_tableau_both_sm_data.json
│   │           │   ├── Test_tableau_desc_sm_data.json
│   │           │   └── Test_tableau_formulas_sm_data.json
│   │           ├── training
│   │           │   ├── formulas_combined.xlsx
│   │           │   ├── formulas_nor_combined.xlsx
│   │           │   ├── formulas_nor.xlsx
│   │           │   ├── formulas.xlsx
│   │           │   ├── gformulas_combined.xlsx
│   │           │   ├── gformulas.csv
│   │           │   ├── gformulas_nor_combined.xlsx
│   │           │   ├── gformulas_nor.xlsx
│   │           │   ├── gformulas.xlsx
│   │           │   ├── __init__.py
│   │           │   ├── test_combined.py
│   │           │   ├── test.py
│   │           │   ├── test_update_labels.py
│   │           │   └── training_versions
│   │           │       └── __init__.py
│   │           ├── training_spacy
│   │           │   ├── __init__.py
│   │           │   ├── test.py
│   │           │   ├── Train_desc_data.json
│   │           │   ├── Train_formulas_data.json
│   │           │   ├── training_spacy_versions
│   │           │   │   └── __init__.py
│   │           │   ├── Train_tableau_both_bsm_data.json
│   │           │   ├── Train_tableau_both_sm_data.json
│   │           │   ├── Train_tableau_desc_bsm_data.json
│   │           │   ├── Train_tableau_desc_sm_data.json
│   │           │   ├── Train_tableau_formulas_bsm_data.json
│   │           │   └── Train_tableau_formulas_sm_data.json
│   │           └── validation
│   │               ├── __init__.py
│   │               ├── test.py
│   │               └── validation_versions
│   │                   └── __init__.py
│   ├── data_spacy
│   │   ├── corpus
│   │   │   └── __init__.py
│   │   ├── embedding
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── pipelines
│   │   │   └── __init__.py
│   │   ├── pre_trained_models
│   │   │   ├── en_core_web_sm
│   │   │   │   ├── en_core_web_sm-3.7.1
│   │   │   │   │   ├── accuracy.json
│   │   │   │   │   ├── attribute_ruler
│   │   │   │   │   │   └── patterns
│   │   │   │   │   ├── config.cfg
│   │   │   │   │   ├── lemmatizer
│   │   │   │   │   │   └── lookups
│   │   │   │   │   │       └── lookups.bin
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── LICENSES_SOURCES
│   │   │   │   │   ├── meta.json
│   │   │   │   │   ├── ner
│   │   │   │   │   │   ├── cfg
│   │   │   │   │   │   ├── model
│   │   │   │   │   │   └── moves
│   │   │   │   │   ├── parser
│   │   │   │   │   │   ├── cfg
│   │   │   │   │   │   ├── model
│   │   │   │   │   │   └── moves
│   │   │   │   │   ├── README.md
│   │   │   │   │   ├── senter
│   │   │   │   │   │   ├── cfg
│   │   │   │   │   │   └── model
│   │   │   │   │   ├── tagger
│   │   │   │   │   │   ├── cfg
│   │   │   │   │   │   └── model
│   │   │   │   │   ├── tok2vec
│   │   │   │   │   │   ├── cfg
│   │   │   │   │   │   └── model
│   │   │   │   │   ├── tokenizer
│   │   │   │   │   └── vocab
│   │   │   │   │       ├── key2row
│   │   │   │   │       ├── lookups.bin
│   │   │   │   │       ├── strings.json
│   │   │   │   │       ├── vectors
│   │   │   │   │       └── vectors.cfg
│   │   │   │   ├── __init__.py
│   │   │   │   └── meta.json
│   │   │   ├── en_core_web_sm-3.7.1.dist-info
│   │   │   │   ├── direct_url.json
│   │   │   │   ├── entry_points.txt
│   │   │   │   ├── INSTALLER
│   │   │   │   ├── LICENSE
│   │   │   │   ├── LICENSES_SOURCES
│   │   │   │   ├── METADATA
│   │   │   │   ├── RECORD
│   │   │   │   ├── REQUESTED
│   │   │   │   ├── top_level.txt
│   │   │   │   └── WHEEL
│   │   │   └── __init__.py
│   │   └── queries
│   │       ├── __init__.py
│   │       └── tableau
│   │           ├── __init__.py
│   │           ├── ner_versions
│   │           │   ├── __init__.py
│   │           │   └── version03052024-2209
│   │           │       ├── __init__.py
│   │           │       ├── ner_queries
│   │           │       │   ├── attribute_ruler
│   │           │       │   │   └── patterns
│   │           │       │   ├── config.cfg
│   │           │       │   ├── lemmatizer
│   │           │       │   │   └── lookups
│   │           │       │   │       └── lookups.bin
│   │           │       │   ├── meta.json
│   │           │       │   ├── ner
│   │           │       │   │   ├── cfg
│   │           │       │   │   ├── model
│   │           │       │   │   └── moves
│   │           │       │   ├── parser
│   │           │       │   │   ├── cfg
│   │           │       │   │   ├── model
│   │           │       │   │   └── moves
│   │           │       │   ├── senter
│   │           │       │   │   ├── cfg
│   │           │       │   │   └── model
│   │           │       │   ├── tagger
│   │           │       │   │   ├── cfg
│   │           │       │   │   └── model
│   │           │       │   ├── tok2vec
│   │           │       │   │   ├── cfg
│   │           │       │   │   └── model
│   │           │       │   ├── tokenizer
│   │           │       │   └── vocab
│   │           │       │       ├── key2row
│   │           │       │       ├── lookups.bin
│   │           │       │       ├── strings.json
│   │           │       │       ├── vectors
│   │           │       │       └── vectors.cfg
│   │           │       ├── ner_queries_desc
│   │           │       │   ├── attribute_ruler
│   │           │       │   │   └── patterns
│   │           │       │   ├── config.cfg
│   │           │       │   ├── lemmatizer
│   │           │       │   │   └── lookups
│   │           │       │   │       └── lookups.bin
│   │           │       │   ├── meta.json
│   │           │       │   ├── ner
│   │           │       │   │   ├── cfg
│   │           │       │   │   ├── model
│   │           │       │   │   └── moves
│   │           │       │   ├── parser
│   │           │       │   │   ├── cfg
│   │           │       │   │   ├── model
│   │           │       │   │   └── moves
│   │           │       │   ├── senter
│   │           │       │   │   ├── cfg
│   │           │       │   │   └── model
│   │           │       │   ├── tagger
│   │           │       │   │   ├── cfg
│   │           │       │   │   └── model
│   │           │       │   ├── tok2vec
│   │           │       │   │   ├── cfg
│   │           │       │   │   └── model
│   │           │       │   ├── tokenizer
│   │           │       │   └── vocab
│   │           │       │       ├── key2row
│   │           │       │       ├── lookups.bin
│   │           │       │       ├── strings.json
│   │           │       │       ├── vectors
│   │           │       │       └── vectors.cfg
│   │           │       └── ner_queries_formulas
│   │           │           ├── attribute_ruler
│   │           │           │   └── patterns
│   │           │           ├── config.cfg
│   │           │           ├── lemmatizer
│   │           │           │   └── lookups
│   │           │           │       └── lookups.bin
│   │           │           ├── meta.json
│   │           │           ├── ner
│   │           │           │   ├── cfg
│   │           │           │   ├── model
│   │           │           │   └── moves
│   │           │           ├── parser
│   │           │           │   ├── cfg
│   │           │           │   ├── model
│   │           │           │   └── moves
│   │           │           ├── senter
│   │           │           │   ├── cfg
│   │           │           │   └── model
│   │           │           ├── tagger
│   │           │           │   ├── cfg
│   │           │           │   └── model
│   │           │           ├── tok2vec
│   │           │           │   ├── cfg
│   │           │           │   └── model
│   │           │           ├── tokenizer
│   │           │           └── vocab
│   │           │               ├── key2row
│   │           │               ├── lookups.bin
│   │           │               ├── strings.json
│   │           │               ├── vectors
│   │           │               └── vectors.cfg
│   │           ├── testing_spacy
│   │           │   ├── __init__.py
│   │           │   ├── Test_desc_data.spacy
│   │           │   ├── Test_formulas_data.spacy
│   │           │   ├── testing_spacy_versions
│   │           │   │   └── __init__.py
│   │           │   ├── test.py
│   │           │   ├── Test_tableau_both_dsm_data.spacy
│   │           │   ├── Test_tableau_desc_sm_data.spacy
│   │           │   └── Test_tableau_formulas_sm_data.spacy
│   │           ├── test_ner_desc.py
│   │           ├── test_ner_formulas.py
│   │           ├── training_spacy
│   │           │   ├── __init__.py
│   │           │   ├── test.py
│   │           │   ├── Train_desc_data.spacy
│   │           │   ├── Train_formulas_data.spacy
│   │           │   ├── training_spacy_versions
│   │           │   │   └── __init__.py
│   │           │   ├── Train_tableau_both_bdsm_data.spacy
│   │           │   ├── Train_tableau_both_dsm_data.spacy
│   │           │   ├── Train_tableau_desc_bsm_data.spacy
│   │           │   ├── Train_tableau_desc_sm_data.spacy
│   │           │   ├── Train_tableau_formulas_bsm_data.spacy
│   │           │   └── Train_tableau_formulas_sm_data.spacy
│   │           └── vocab
│   │               ├── __init__.py
│   │               ├── vocab_tableau_both_Combined_bdsm
│   │               ├── vocab_tableau_both_Combined_dsm
│   │               ├── vocab_tableau_desc_Description_bsm
│   │               ├── vocab_tableau_desc_Description_sm
│   │               ├── vocab_tableau_formulas_Formula (Tableau)_bsm
│   │               ├── vocab_tableau_formulas_Formula (Tableau)_sm
│   │               └── vocab_versions
│   │                   ├── __init__.py
│   │                   └── version-09052024-1705
│   │                       └── __init__.py
│   ├── __init__.py
│   ├── mappings
│   │   └── __init__.py
│   ├── models
│   │   ├── __init__.py
│   │   └── queries
│   │       ├── __init__.py
│   │       └── tableau
│   │           ├── checkpoints
│   │           │   └── __init__.py
│   │           ├── __init__.py
│   │           ├── model_configs
│   │           │   └── __init__.py
│   │           ├── trained_models
│   │           │   ├── __init__.py
│   │           │   ├── test_comb_multi_task_model.py
│   │           │   ├── test_description_model.py
│   │           │   ├── test_formulas_model.py
│   │           │   └── trained_models_versions
│   │           │       ├── __init__.py
│   │           │       └── version-0.0-28042024-2108
│   │           │           ├── Combined__multi_task_data_200.0.5.8
│   │           │           │   ├── attribute_ruler
│   │           │           │   │   └── patterns
│   │           │           │   ├── config.cfg
│   │           │           │   ├── lemmatizer
│   │           │           │   │   └── lookups
│   │           │           │   │       └── lookups.bin
│   │           │           │   ├── meta.json
│   │           │           │   ├── ner
│   │           │           │   │   ├── cfg
│   │           │           │   │   ├── model
│   │           │           │   │   └── moves
│   │           │           │   ├── parser
│   │           │           │   │   ├── cfg
│   │           │           │   │   ├── model
│   │           │           │   │   └── moves
│   │           │           │   ├── senter
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tagger
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tok2vec
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tokenizer
│   │           │           │   └── vocab
│   │           │           │       ├── key2row
│   │           │           │       ├── lookups.bin
│   │           │           │       ├── strings.json
│   │           │           │       ├── vectors
│   │           │           │       └── vectors.cfg
│   │           │           ├── Combined_multi_task_data_200.0.5.8
│   │           │           │   ├── attribute_ruler
│   │           │           │   │   └── patterns
│   │           │           │   ├── config.cfg
│   │           │           │   ├── lemmatizer
│   │           │           │   │   └── lookups
│   │           │           │   │       └── lookups.bin
│   │           │           │   ├── meta.json
│   │           │           │   ├── ner
│   │           │           │   │   ├── cfg
│   │           │           │   │   ├── model
│   │           │           │   │   └── moves
│   │           │           │   ├── parser
│   │           │           │   │   ├── cfg
│   │           │           │   │   ├── model
│   │           │           │   │   └── moves
│   │           │           │   ├── senter
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tagger
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tok2vec
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tokenizer
│   │           │           │   └── vocab
│   │           │           │       ├── key2row
│   │           │           │       ├── lookups.bin
│   │           │           │       ├── strings.json
│   │           │           │       ├── vectors
│   │           │           │       └── vectors.cfg
│   │           │           ├── Combined_multi_task_data_400.0.5.8
│   │           │           │   ├── attribute_ruler
│   │           │           │   │   └── patterns
│   │           │           │   ├── config.cfg
│   │           │           │   ├── lemmatizer
│   │           │           │   │   └── lookups
│   │           │           │   │       └── lookups.bin
│   │           │           │   ├── meta.json
│   │           │           │   ├── ner
│   │           │           │   │   ├── cfg
│   │           │           │   │   ├── model
│   │           │           │   │   └── moves
│   │           │           │   ├── parser
│   │           │           │   │   ├── cfg
│   │           │           │   │   ├── model
│   │           │           │   │   └── moves
│   │           │           │   ├── senter
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tagger
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tok2vec
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tokenizer
│   │           │           │   └── vocab
│   │           │           │       ├── key2row
│   │           │           │       ├── lookups.bin
│   │           │           │       ├── strings.json
│   │           │           │       ├── vectors
│   │           │           │       └── vectors.cfg
│   │           │           ├── custom_desc_components_old.py
│   │           │           ├── custom_desc_components.py
│   │           │           ├── custom_formulas_components_old.py
│   │           │           ├── custom_formulas_components.py
│   │           │           ├── Description_Tableau_data
│   │           │           │   ├── attribute_ruler
│   │           │           │   │   └── patterns
│   │           │           │   ├── config.cfg
│   │           │           │   ├── lemmatizer
│   │           │           │   │   └── lookups
│   │           │           │   │       └── lookups.bin
│   │           │           │   ├── meta.json
│   │           │           │   ├── ner
│   │           │           │   │   ├── cfg
│   │           │           │   │   ├── model
│   │           │           │   │   └── moves
│   │           │           │   ├── parser
│   │           │           │   │   ├── cfg
│   │           │           │   │   ├── model
│   │           │           │   │   └── moves
│   │           │           │   ├── senter
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tagger
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tok2vec
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tokenizer
│   │           │           │   └── vocab
│   │           │           │       ├── key2row
│   │           │           │       ├── lookups.bin
│   │           │           │       ├── strings.json
│   │           │           │       ├── vectors
│   │           │           │       └── vectors.cfg
│   │           │           ├── Formulas_Tableau_data
│   │           │           │   ├── attribute_ruler
│   │           │           │   │   └── patterns
│   │           │           │   ├── config.cfg
│   │           │           │   ├── lemmatizer
│   │           │           │   │   └── lookups
│   │           │           │   │       └── lookups.bin
│   │           │           │   ├── meta.json
│   │           │           │   ├── ner
│   │           │           │   │   ├── cfg
│   │           │           │   │   ├── model
│   │           │           │   │   └── moves
│   │           │           │   ├── parser
│   │           │           │   │   ├── cfg
│   │           │           │   │   ├── model
│   │           │           │   │   └── moves
│   │           │           │   ├── senter
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tagger
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tok2vec
│   │           │           │   │   ├── cfg
│   │           │           │   │   └── model
│   │           │           │   ├── tokenizer
│   │           │           │   └── vocab
│   │           │           │       ├── key2row
│   │           │           │       ├── lookups.bin
│   │           │           │       ├── strings.json
│   │           │           │       ├── vectors
│   │           │           │       └── vectors.cfg
│   │           │           ├── test_description_model.txt
│   │           │           ├── test_formulas_model_old.txt
│   │           │           ├── test_formulas_model.txt
│   │           │           └── test_multi_task_400_model.txt
│   │           └── training_history
│   │               ├── __init__.py
│   │               └── training_history_versions
│   │                   └── __init__.py
│   ├── modifications
│   │   ├── ruler_versions.py
│   │   ├── version_manager.docx
│   │   ├── version_manager_gpt.docx
│   │   └── version_manager.py
│   ├── patterns
│   │   ├── __init__.py
│   │   └── queries
│   │       ├── __init__.py
│   │       └── tableau
│   │           ├── __init__.py
│   │           ├── test_create_ruler_tableau.py
│   │           └── test_rules_tableau_patterns.py
│   ├── scripts_
│   │   ├── __init__.py
│   │   ├── script_combined_data.py
│   │   ├── script_custom_entities.py
│   │   ├── script_custom_ner.py
│   │   └── script_custom_patterns.py
│   ├── tests
│   │   ├── docs.py
│   │   ├── __init__.py
│   │   ├── test_desc_formulas.py
│   │   ├── test_desc.py
│   │   ├── test_entity_desc.py
│   │   ├── test_entity_formulas.py
│   │   ├── test_formulas.py
│   │   └── test_rename_files.py
│   └── utils
│       └── __init__.py
├── LICENSE
├── MANIFEST.in
├── pyproject.toml
├── pytest.ini
├── README.md
├── README.rst
├── setup.py
├── tests
│   ├── docs.py
│   ├── __init__.py
│   ├── test_desc_formulas.py
│   ├── test_desc.py
│   ├── test_entity_desc.py
│   ├── test_entity_formulas.py
│   ├── test_formulas.py
│   └── test_rename_files.py
├── top_level.txt
├── _version.py
└── VisibilityOCt2024.docx

417 directories, 1109 files

┌──(agagora㉿localhost)-[~/Downloads/LLM-HypatiaX]
└─$                                                     
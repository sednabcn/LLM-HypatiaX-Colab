# HypatiaX Project Documentation

Generated: 2025-11-14 16:50:28

---

## 📊 Project Statistics

- **Total Modules**: 395
- **Total Classes**: 192
- **Total Functions**: 0

# Project Structure

```
├── __init__.py
├── agents
│   ├── __init__.py
│   ├── base
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── coordinators
│   │   └── __init__.py
│   ├── learning
│   │   └── __init__.py
│   ├── memory
│   │   └── __init__.py
│   ├── specialists
│   │   ├── __init__.py
│   │   └── parser_agent.py
│   └── workflows
│       ├── __init__.py
│       └── hybrid_workflow.py
├── auto_migrate.py
├── backup_before_extension
│   ├── config
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── model_configs.py
│   │   └── paths.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── deployment
│   │   │   ├── __init__.py
│   │   │   └── evaluate_model.py
│   │   ├── evaluation
│   │   │   ├── __init__.py
│   │   │   └── testing_model.py
│   │   ├── preprocessing
│   │   │   ├── __init__.py
│   │   │   └── preparation_data.py
│   │   └── training
│   │       ├── __init__.py
│   │       └── training_spacy.py
│   ├── custom_entities
│   │   ├── __init__.py
│   │   └── ner_entity.py
│   ├── custom_ner
│   │   ├── __init__.py
│   │   ├── custom_ruler.py
│   │   ├── queries
│   │   │   ├── __init__.py
│   │   │   └── tableau
│   │   │       ├── __init__.py
│   │   │       ├── components
│   │   │       │   ├── __init__.py
│   │   │       │   ├── ruler_tableau.py
│   │   │       │   ├── ruler_tableau_desc.py
│   │   │       │   └── ruler_tableau_formulas.py
│   │   │       ├── custom_tableau_components.py
│   │   │       ├── custom_tableau_desc_components.py
│   │   │       ├── custom_tableau_formulas_components.py
│   │   │       └── rules
│   │   │           └── __init__.py
│   │   └── rule_file_analyzer.py
│   ├── data_spacy
│   │   ├── __init__.py
│   │   ├── corpus
│   │   │   └── __init__.py
│   │   ├── embedding
│   │   │   └── __init__.py
│   │   ├── pipelines
│   │   │   └── __init__.py
│   │   ├── pre_trained_models
│   │   │   ├── __init__.py
│   │   │   └── en_core_web_sm
│   │   │       └── __init__.py
│   │   └── queries
│   │       ├── __init__.py
│   │       └── tableau
│   │           ├── __init__.py
│   │           ├── testing_spacy
│   │           │   └── __init__.py
│   │           ├── training_spacy
│   │           │   └── __init__.py
│   │           └── vocab
│   │               └── __init__.py
│   ├── datasets
│   │   ├── __init__.py
│   │   └── queries
│   │       ├── __init__.py
│   │       ├── combined
│   │       │   ├── __init__.py
│   │       │   ├── combined_data.py
│   │       │   └── combined_local_data.py
│   │       ├── normalize
│   │       │   ├── __init__.py
│   │       │   ├── normalize_data.py
│   │       │   └── test.py
│   │       └── tableau
│   │           ├── __init__.py
│   │           ├── data
│   │           │   ├── __init__.py
│   │           │   └── test.py
│   │           ├── testing
│   │           │   ├── __init__.py
│   │           │   ├── test.py
│   │           │   └── test_combined.py
│   │           ├── testing_spacy
│   │           │   ├── __init__.py
│   │           │   └── test.py
│   │           ├── training
│   │           │   ├── __init__.py
│   │           │   ├── test.py
│   │           │   ├── test_combined.py
│   │           │   └── test_update_labels.py
│   │           ├── training_spacy
│   │           │   ├── __init__.py
│   │           │   └── test.py
│   │           ├── validation
│   │           │   ├── __init__.py
│   │           │   └── test.py
│   │           └── validation_spacy
│   │               └── __init__.py
│   ├── demo
│   │   ├── __init__.py
│   │   ├── complete-system-guide
│   │   │   ├── benchmark
│   │   │   │   └── benchmark01.py
│   │   │   ├── custom_demos
│   │   │   │   ├── batch_processing_demo.py
│   │   │   │   └── simple_clidemo.py
│   │   │   ├── example_engine.py
│   │   │   ├── example_ui.py
│   │   │   ├── integration-patterns
│   │   │   │   ├── pattern1.py
│   │   │   │   ├── pattern2.py
│   │   │   │   ├── pattern3.py
│   │   │   │   ├── pattern4.py
│   │   │   │   └── pattern5.py
│   │   │   ├── run_interactive_demo.py
│   │   │   ├── usage_basic.py
│   │   │   └── usage_examples.py
│   │   ├── config.py
│   │   ├── demo_examples.py
│   │   ├── demo_interactive.py
│   │   ├── demo_web_api.py
│   │   ├── engine.py
│   │   ├── examples.py
│   │   ├── ui.py
│   │   ├── update
│   │   │   ├── compare_old_vs_new.py
│   │   │   └── modern_llm_mapper.py
│   │   └── utils
│   │       ├── __init__.py
│   │       └── demo_helpers.py
│   ├── examples
│   │   ├── __init__.py
│   │   ├── basic_usage.py
│   │   ├── evaluation_example.py
│   │   └── training_example.py
│   ├── experiments
│   │   ├── __init__.py
│   │   ├── experiment_tracker.py
│   │   └── ner
│   │       ├── __init__.py
│   │       └── queries
│   │           └── tableau
│   │               ├── custom_ner
│   │               │   ├── __init__.py
│   │               │   └── entities_mapping.py
│   │               ├── pipeline
│   │               │   ├── __init__.py
│   │               │   ├── joint_training.py
│   │               │   └── sequential_pipeline.py
│   │               └── training
│   │                   └── __init__.py
│   ├── mappings
│   │   ├── __init__.py
│   │   └── mapping.py
│   ├── models
│   │   ├── __init__.py
│   │   └── queries
│   │       ├── __init__.py
│   │       └── tableau
│   │           ├── __init__.py
│   │           ├── checkpoints
│   │           │   └── __init__.py
│   │           ├── model_configs
│   │           │   └── __init__.py
│   │           ├── trained_models
│   │           │   └── __init__.py
│   │           └── training_history
│   │               └── __init__.py
│   ├── patterns
│   │   ├── __init__.py
│   │   ├── custom_patterns.py
│   │   └── queries
│   │       ├── __init__.py
│   │       └── tableau
│   │           ├── __init__.py
│   │           ├── generation.py
│   │           ├── test_create_ruler_tableau.py
│   │           └── test_rules_tableau_patterns.py
│   ├── scripts_
│   │   ├── __init__.py
│   │   ├── ner_test_simultion_package.py
│   │   ├── proc_time.py
│   │   ├── proc_timed.py
│   │   ├── proc_timef.py
│   │   ├── run_test_parallel_code_integration.py
│   │   ├── run_time_bundle_code.py
│   │   ├── run_time_code.py
│   │   ├── run_time_code_seq.py
│   │   ├── run_time_parallel_code.py
│   │   ├── script_combined_data.py
│   │   ├── script_custom_entities.py
│   │   ├── script_custom_ner.py
│   │   └── script_custom_patterns.py
│   └── utils
│       ├── __init__.py
│       ├── colab.py
│       ├── files.py
│       ├── files_local.py
│       ├── path_manager.py
│       ├── tree_id_op.py
│       └── utils.py
├── config
│   ├── __init__.py
│   ├── agent_config.py
│   ├── api_key_management.py
│   ├── base.py
│   ├── config.py
│   ├── constants.py
│   ├── google_credentials_manager.py
│   ├── llm_config.py
│   ├── model_configs.py
│   ├── paths.py
│   ├── rag_config.py
│   ├── tool_config.py
│   ├── transformer_config.py
│   └── transformer_config_.py
├── core
│   ├── __init__.py
│   ├── deployment
│   │   ├── __init__.py
│   │   ├── deployment-evaluate_model.py
│   │   ├── deployment_api.py
│   │   ├── deployment_batch.py
│   │   ├── deployment_pipeline.py
│   │   ├── evaluate_model.py
│   │   └── evaluation_unified.py
│   ├── evaluation
│   │   ├── __init__.py
│   │   └── testing_model.py
│   ├── preprocessing
│   │   ├── __init__.py
│   │   ├── llm_prep.py
│   │   ├── preparation_data.py
│   │   ├── preprocessing_pipeline.py
│   │   └── transformer_prep.py
│   ├── run_complete_pipeline.py
│   └── training
│       ├── __init__.py
│       ├── training_llm.py
│       ├── training_llm_.py
│       ├── training_rag.py
│       ├── training_rag_.py
│       ├── training_spacy.py
│       ├── training_tranformer_.py
│       ├── training_transformer.py
│       └── training_transformer_.py
├── custom_entities
│   ├── __init__.py
│   └── ner_entity.py
├── custom_ner
│   ├── __init__.py
│   ├── custom_ruler.py
│   ├── queries
│   │   ├── __init__.py
│   │   └── tableau
│   │       ├── __init__.py
│   │       ├── components
│   │       │   ├── __init__.py
│   │       │   ├── ruler_tableau.py
│   │       │   ├── ruler_tableau_desc.py
│   │       │   └── ruler_tableau_formulas.py
│   │       ├── custom_tableau_components.py
│   │       ├── custom_tableau_desc_components.py
│   │       ├── custom_tableau_formulas_components.py
│   │       ├── hybrid
│   │       │   └── __init__.py
│   │       ├── rules
│   │       │   └── __init__.py
│   │       └── transformer
│   │           └── __init__.py
│   └── rule_file_analyzer.py
├── data_spacy
│   ├── __init__.py
│   ├── corpus
│   │   └── __init__.py
│   ├── embedding
│   │   └── __init__.py
│   ├── pipelines
│   │   └── __init__.py
│   ├── pre_trained_models
│   │   ├── __init__.py
│   │   └── en_core_web_sm
│   │       └── __init__.py
│   └── queries
│       ├── __init__.py
│       └── tableau
│           ├── __init__.py
│           ├── testing_spacy
│           │   └── __init__.py
│           ├── training_spacy
│           │   └── __init__.py
│           └── vocab
│               └── __init__.py
├── datasets
│   ├── __init__.py
│   ├── dataset-generator.py
│   ├── hypatiax_dataset.py
│   └── queries
│       ├── __init__.py
│       ├── agent
│       │   ├── __init__.py
│       │   ├── agent_queries.py
│       │   └── test.py
│       ├── analytics
│       │   ├── __init__.py
│       │   ├── analytics_data.py
│       │   └── test.py
│       ├── combined
│       │   ├── __init__.py
│       │   ├── combined_data.py
│       │   └── combined_local_data.py
│       ├── llm
│       │   ├── __init__.py
│       │   ├── llm_queries.py
│       │   └── test.py
│       ├── normalize
│       │   ├── __init__.py
│       │   ├── normalize_data.py
│       │   └── test.py
│       ├── tableau
│       │   ├── __init__.py
│       │   ├── agent
│       │   │   └── __init__.py
│       │   ├── data
│       │   │   ├── __init__.py
│       │   │   └── test.py
│       │   ├── llm
│       │   │   └── __init__.py
│       │   ├── testing
│       │   │   ├── __init__.py
│       │   │   ├── test.py
│       │   │   └── test_combined.py
│       │   ├── testing_spacy
│       │   │   ├── __init__.py
│       │   │   └── test.py
│       │   ├── training
│       │   │   ├── __init__.py
│       │   │   ├── test.py
│       │   │   ├── test_combined.py
│       │   │   └── test_update_labels.py
│       │   ├── training_spacy
│       │   │   ├── __init__.py
│       │   │   └── test.py
│       │   ├── transformer
│       │   │   └── __init__.py
│       │   ├── validation
│       │   │   ├── __init__.py
│       │   │   └── test.py
│       │   └── validation_spacy
│       │       └── __init__.py
│       └── transformer
│           ├── __init__.py
│           ├── test.py
│           └── transformer_queries.py
├── demo
│   ├── __init__.py
│   ├── complete-system-guide
│   │   ├── benchmark
│   │   │   └── benchmark01.py
│   │   ├── custom_demos
│   │   │   ├── batch_processing_demo.py
│   │   │   └── simple_clidemo.py
│   │   ├── example_engine.py
│   │   ├── example_ui.py
│   │   ├── integration-patterns
│   │   │   ├── pattern1.py
│   │   │   ├── pattern2.py
│   │   │   ├── pattern3.py
│   │   │   ├── pattern4.py
│   │   │   └── pattern5.py
│   │   ├── run_interactive_demo.py
│   │   ├── usage_basic.py
│   │   └── usage_examples.py
│   ├── config.py
│   ├── demo_examples.py
│   ├── demo_interactive.py
│   ├── demo_web_api.py
│   ├── engine.py
│   ├── examples.py
│   ├── ui.py
│   ├── update
│   │   ├── compare_old_vs_new.py
│   │   └── modern_llm_mapper.py
│   └── utils
│       ├── __init__.py
│       └── demo_helpers.py
├── examples
│   ├── Complete-system-integration.py
│   ├── Example-DFei-Risk-Metric.py
│   ├── __init__.py
│   ├── agent_example.py
│   ├── basic_usage.py
│   ├── evaluation_example.py
│   ├── hybrid_example.py
│   ├── llm_example.py
│   ├── modern-llm-first-mapper.py
│   ├── training_example.py
│   └── transformer_example.py
├── experiments
│   ├── __init__.py
│   ├── agents
│   │   └── __init__.py
│   ├── experiment_tracker.py
│   ├── hybrid
│   │   └── __init__.py
│   ├── llm
│   │   └── __init__.py
│   ├── ner
│   │   ├── __init__.py
│   │   └── queries
│   │       └── tableau
│   │           ├── custom_ner
│   │           │   ├── __init__.py
│   │           │   └── entities_mapping.py
│   │           ├── pipeline
│   │           │   ├── __init__.py
│   │           │   ├── joint_training.py
│   │           │   └── sequential_pipeline.py
│   │           └── training
│   │               └── __init__.py
│   └── transformers
│       └── __init__.py
├── mappings
│   ├── __init__.py
│   ├── agent_mapping.py
│   ├── hybrid_mapping.py
│   ├── llm_mapping.py
│   ├── llm_mapping_.py
│   ├── mapping.py
│   ├── mapping_.py
│   ├── mapping_hybrid.py
│   ├── mapping_plus.py
│   ├── modern-llm-first-mapper.py
│   └── transformer_mapping.py
├── model_implementations
│   ├── __init__.py
│   ├── agents
│   │   └── __init__.py
│   ├── llm
│   │   └── __init__.py
│   ├── ner
│   │   └── __init__.py
│   └── transformers
│       └── __init__.py
├── models
│   ├── __init__.py
│   └── queries
│       ├── __init__.py
│       └── tableau
│           ├── __init__.py
│           ├── checkpoints
│           │   └── __init__.py
│           ├── model_configs
│           │   └── __init__.py
│           ├── trained_models
│           │   └── __init__.py
│           └── training_history
│               └── __init__.py
├── patterns
│   ├── __init__.py
│   ├── custom_patterns.py
│   └── queries
│       ├── __init__.py
│       └── tableau
│           ├── __init__.py
│           ├── generation.py
│           ├── test_create_ruler_tableau.py
│           └── test_rules_tableau_patterns.py
├── scripts_
│   ├── __init__.py
│   ├── migration
│   │   └── __init__.py
│   ├── ner_test_simultion_package.py
│   ├── proc_time.py
│   ├── proc_timed.py
│   ├── proc_timef.py
│   ├── run_test_parallel_code_integration.py
│   ├── run_time_bundle_code.py
│   ├── run_time_code.py
│   ├── run_time_code_seq.py
│   ├── run_time_parallel_code.py
│   ├── script_combined_data.py
│   ├── script_custom_entities.py
│   ├── script_custom_ner.py
│   └── script_custom_patterns.py
├── tests
│   ├── __init__.py
│   ├── e2e
│   │   └── __init__.py
│   ├── integration
│   │   └── __init__.py
│   └── unit
│       ├── test_agents
│       │   └── __init__.py
│       ├── test_llm
│       │   └── __init__.py
│       ├── test_ner
│       │   └── __init__.py
│       ├── test_tools
│       │   └── __init__.py
│       └── test_transformers
│           └── __init__.py
├── tools
│   ├── __init__.py
│   ├── formal
│   │   └── __init__.py
│   ├── libraries
│   │   ├── cpu-only.py
│   │   ├── optimize-cpu-libraries.py
│   │   └── optimized-cpu-parallel-libraries.py
│   ├── llm_providers
│   │   ├── __init__.py
│   │   ├── anthropic_provider.py
│   │   ├── base_provider.py
│   │   ├── base_provider_.py
│   │   ├── cohere_provider.py
│   │   ├── llm-formula-generator.py
│   │   └── openai_provider.py
│   ├── numerical
│   │   └── __init__.py
│   ├── symbolic
│   │   ├── __init__.py
│   │   ├── symbolic_validator.py
│   │   ├── symbolic_validator_.py
│   │   └── sympy_wrapper.py
│   ├── transformers
│   │   └── __init__.py
│   ├── validation
│   │   ├── Backtester.py
│   │   ├── __init__.py
│   │   └── symbolic_validator.py
│   └── visualization
│       ├── __init__.py
│       ├── hypatiax-visualization-scripts.py
│       └── hypatiax_visualizer.py
└── utils
    ├── __init__.py
    ├── colab.py
    ├── files.py
    ├── files_local.py
    ├── path_manager.py
    ├── tree_id_op.py
    └── utils.py
```

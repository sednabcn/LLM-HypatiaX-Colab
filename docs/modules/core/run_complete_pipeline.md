# Module: `core/run_complete_pipeline.py`

## Description

MASTER INTEGRATION SCRIPT
Executes complete pipeline from data preparation to deployment
All steps: Preprocessing → Training → Evaluation → Deployment

**Last Modified**: 2025-11-07T15:38:55.059944

## Dependencies

- `argparse`
- `datetime`
- `deployment_pipeline`
- `evaluation_unified`
- `json`
- `logging`
- `mapping_plus`
- `os`
- `pathlib`
- `preprocessing_pipeline`
- `subprocess`
- `sys`
- `training_llm`
- `training_rag`
- `training_spacy`
- `training_transformer`

## Classes

### `PipelineConfig`

Configuration for complete pipeline

**Methods**:

- `__init__(self)`

### `PipelineExecutor`

Execute complete ML pipeline

**Methods**:

- `__init__(self, config: PipelineConfig)`
- `_create_directories(self)`
  - Create necessary directories
- `_setup_logging(self)`
  - Setup logging
- `log(self, message: str, level: str)`
  - Log message
- `step_prepare_data(self)`
  - Step 1: Data Preparation
- `step_train_spacy(self)`
  - Step 2: Train spaCy NER Model
- `step_train_transformer(self)`
  - Step 3: Train Transformer Model
- `step_train_rag(self)`
  - Step 4: Train RAG Model
- `step_train_llm(self)`
  - Step 5: Setup LLM Integration
- `step_evaluate_all(self)`
  - Step 6: Evaluate All Models
- `step_deploy(self)`
  - Step 7: Deploy Models
- `_create_sample_data(self)`
  - Create sample training data
- `_create_sample_test_data(self)`
  - Create sample test data
- `run_pipeline(self, steps: list)`
  - Run complete pipeline
- `print_summary(self)`
  - Print pipeline summary
- `save_results(self)`
  - Save pipeline results

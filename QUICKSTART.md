# HypatiaX Quick Start Guide

**Generated automatically from project structure**

---

## 🚀 Installation

```bash
# Clone the repository
git clone <repository-url>
cd LLM-HypatiaX

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .

# Download spaCy model
python -m spacy download en_core_web_sm
```

## 🔧 Fix Known Issues

Before running, fix the rule file naming issue:

```bash
python rule_file_analyzer.py
./fix_rules.sh
```

## 📦 Core Components

### NER

Located in: `hypatiax/ner/`
Files: 18

### TRAINING

Located in: `hypatiax/training/`
Files: 15

### EVALUATION

Located in: `hypatiax/evaluation/`
Files: 2

### PREPROCESSING

Located in: `hypatiax/preprocessing/`
Files: 5

### DEPLOYMENT

Located in: `hypatiax/deployment/`
Files: 7

## 🎯 Entry Points

### `auto_migrate.py`

Smart Auto-Migrate System with Automatic Backup
================================================

Keeps ALL older versions with timestamps
Automatic backup before/after file operations
Auto-restore on validation failure

Features:

- Tracks all file/directory changes
- Creates timestamped backups automatically
- Validates content (JSONL, JSON, NER models)
- Auto-restores from last good backup if broken
- Decorator & context manager for automatic protection
- Version history with rollback capability

```bash
python auto_migrate.py
```

### `custom_ner/rule_file_analyzer.py`

HypatiaX Rule File Analyzer
============================

Analyzes the rule file versioning system and identifies the disconnect
between expected and actual rule file naming conventions.

This script helps solve the BLOCKER identified in the morning assessment.

```bash
python custom_ner/rule_file_analyzer.py
```

### `demo/engine.py`

HypatiaX Engine - Core Processing Logic
Handles NER model integration, entity extraction, and formula generation

```bash
python demo/engine.py
```

### `demo/ui.py`

HypatiaX UI Components - Reusable UI building blocks
Provides rich console output, visualizations, and interactive components

```bash
python demo/ui.py
```

### `demo/examples.py`

HypatiaX Examples - Advanced example management and generation
Handles example datasets, validation, and benchmarking

```bash
python demo/examples.py
```

### `demo/demo_web_api.py`

No description available

```bash
python demo/demo_web_api.py
```

### `demo/demo_examples.py`

HypatiaX Demo Examples
Curated examples for demonstrating different capabilities

Curated example library
50+ example queries organized by category
Description, formula, and combined examples
Real-world use cases
Easy to access programmatically

```bash
python demo/demo_examples.py
```

### `demo/config.py`

HypatiaX Demo Configuration
Centralized configuration for all demo components
Easy to update and maintain

```bash
python demo/config.py
```

### `demo/demo_interactive.py`

HypatiaX Interactive Demo
Demonstrates NER capabilities for Tableau query processing

Main command-line demo

Interactive menu system
Multiple demo modes (desc, formulas, both)
Batch processing
Model comparison
Works with OR without trained models

```bash
python demo/demo_interactive.py
```

### `datasets/hypatiax_dataset.py`

HypatiaX Complete Dataset Generator
Generates comprehensive datasets for DeFi formula testing and validation

```bash
python datasets/hypatiax_dataset.py
```

### `datasets/dataset-generator.py`

HypatiaX Complete Dataset Generator
Generates comprehensive datasets for DeFi formula testing and validation

```bash
python datasets/dataset-generator.py
```

### `experiments/experiment_tracker.py`

Experiment tracking utility for HypatiaX
Registers and tracks experiments across all technologies

```bash
python experiments/experiment_tracker.py
```

### `utils/path_manager.py`

No description available

```bash
python utils/path_manager.py
```

### `utils/utils.py`

No description available

```bash
python utils/utils.py
```

### `core/run_complete_pipeline.py`

MASTER INTEGRATION SCRIPT
Executes complete pipeline from data preparation to deployment
All steps: Preprocessing → Training → Evaluation → Deployment

```bash
python core/run_complete_pipeline.py
```

### `config/google_credentials_manager.py`

Google Credentials Manager for HypatiaX
Handles Google Cloud API keys and OAuth credentials
Location: hypatiax/config/google_credentials_manager.py

```bash
python config/google_credentials_manager.py
```

### `config/api_key_management.py`

API Key Manager for HypatiaX
Secure storage, retrieval, and validation of API keys
Location: hypatiax/config/api_key_manager.py

```bash
python config/api_key_management.py
```

### `config/config.py`

Universal configuration for HypatiaX project.
Works in: Local development, GitHub Actions, Docker, Cloud environments.

```bash
python config/config.py
```

### `mappings/mapping_.py`

Improved Description-to-Formula Mapping System
Supports multiple strategies: vocab mapping, sentence mapping, regex, NER-based, and ML models

```bash
python mappings/mapping_.py
```

### `mappings/modern-llm-first-mapper.py`

Modern LLM-First Formula Mapping (2025 Trends)
Primary: Few-shot prompting with GPT-4/Claude
Fallback: Fine-tuned smaller models for cost/latency

```bash
python mappings/modern-llm-first-mapper.py
```

### `mappings/mapping_hybrid.py`

Hybrid Formula Mapping System
Integrates ALL techniques: spaCy NER, Transformers, RAG, LLM, Rule-based, Ensemble

```bash
python mappings/mapping_hybrid.py
```

### `mappings/mapping_plus.py`

No description available

```bash
python mappings/mapping_plus.py
```

### `scripts_/run_test_parallel_code_integration.py`

No description available

```bash
python scripts_/run_test_parallel_code_integration.py
```

### `scripts_/ner_test_simultion_package.py`

No description available

```bash
python scripts_/ner_test_simultion_package.py
```

### `scripts_/script_custom_ner.py`

No description available

```bash
python scripts_/script_custom_ner.py
```

### `scripts_/run_time_code.py`

No description available

```bash
python scripts_/run_time_code.py
```

### `scripts_/script_custom_entities.py`

No description available

```bash
python scripts_/script_custom_entities.py
```

### `scripts_/script_custom_patterns.py`

No description available

```bash
python scripts_/script_custom_patterns.py
```

### `scripts_/run_time_bundle_code.py`

No description available

```bash
python scripts_/run_time_bundle_code.py
```

### `scripts_/run_time_code_seq.py`

No description available

```bash
python scripts_/run_time_code_seq.py
```

### `scripts_/run_time_parallel_code.py`

No description available

```bash
python scripts_/run_time_parallel_code.py
```

### `scripts_/script_combined_data.py`

No description available

```bash
python scripts_/script_combined_data.py
```

### `examples/modern-llm-first-mapper.py`

Modern LLM-First Formula Mapping (2025 Trends)
Primary: Few-shot prompting with GPT-4/Claude
Fallback: Fine-tuned smaller models for cost/latency

```bash
python examples/modern-llm-first-mapper.py
```

### `examples/llm_example.py`

No description available

```bash
python examples/llm_example.py
```

### `examples/hybrid_example.py`

No description available

```bash
python examples/hybrid_example.py
```

### `examples/agent_example.py`

No description available

```bash
python examples/agent_example.py
```

### `examples/transformer_example.py`

No description available

```bash
python examples/transformer_example.py
```

### `custom_ner/queries/tableau/custom_tableau_components.py`

Custom Tableau Components with Auto-Migration
Loads NER rules with automatic change detection and backup for combined tableau rules.

```bash
python custom_ner/queries/tableau/custom_tableau_components.py
```

### `custom_ner/queries/tableau/custom_tableau_formulas_components.py`

Custom Tableau Formulas Components with Auto-Migration
Loads NER rules with automatic change detection and backup.

```bash
python custom_ner/queries/tableau/custom_tableau_formulas_components.py
```

### `tools/visualization/hypatiax_visualizer.py`

HypatiaX Visualization Scripts
Beautiful, professional charts for DeFi analysis

```bash
python tools/visualization/hypatiax_visualizer.py
```

### `tools/visualization/hypatiax-visualization-scripts.py`

HypatiaX Visualization Scripts
Beautiful, professional charts for DeFi analysis

```bash
python tools/visualization/hypatiax-visualization-scripts.py
```

### `demo/update/compare_old_vs_new.py`

Comparison Demo: Old Sequential Pipeline vs Modern LLM (2025)
============================================================

Shows side-by-side comparison to demonstrate why LLMs are better.

Usage:
    python compare_old_vs_new.py

```bash
python demo/update/compare_old_vs_new.py
```

### `demo/update/modern_llm_mapper.py`

Modern LLM-Based Formula Mapper (2025 Approach)
==============================================

Uses GPT-4/Claude API with few-shot prompting for formula generation.
NO training required. 95%+ accuracy out of the box.

Usage:
    python modern_llm_mapper.py --input "calculate area of circle"
    python modern_llm_mapper.py --batch test_sentences.txt
    python modern_llm_mapper.py --demo

```bash
python demo/update/modern_llm_mapper.py
```

### `demo/complete-system-guide/custom_demos/batch_processing_demo.py`

No description available

```bash
python demo/complete-system-guide/custom_demos/batch_processing_demo.py
```

### `demo/complete-system-guide/custom_demos/simple_clidemo.py`

No description available

```bash
python demo/complete-system-guide/custom_demos/simple_clidemo.py
```

### `demo/complete-system-guide/integration-patterns/pattern5.py`

No description available

```bash
python demo/complete-system-guide/integration-patterns/pattern5.py
```

### `datasets/queries/normalize/normalize_data.py`

No description available

```bash
python datasets/queries/normalize/normalize_data.py
```

### `datasets/queries/normalize/test.py`

No description available

```bash
python datasets/queries/normalize/test.py
```

### `datasets/queries/agent/test.py`

Test module for data processing.

```bash
python datasets/queries/agent/test.py
```

### `datasets/queries/agent/agent_queries.py`

AGENT processing for queries domain.

```bash
python datasets/queries/agent/agent_queries.py
```

### `datasets/queries/analytics/test.py`

Test module for data processing.

```bash
python datasets/queries/analytics/test.py
```

### `datasets/queries/analytics/analytics_data.py`

Analytics operations for queries data.
Provides visualization and metrics computation.

```bash
python datasets/queries/analytics/analytics_data.py
```

### `datasets/queries/llm/test.py`

Test module for data processing.

```bash
python datasets/queries/llm/test.py
```

### `datasets/queries/llm/llm_queries.py`

LLM processing for queries domain.

```bash
python datasets/queries/llm/llm_queries.py
```

### `datasets/queries/transformer/test.py`

Test module for data processing.

```bash
python datasets/queries/transformer/test.py
```

### `datasets/queries/transformer/transformer_queries.py`

TRANSFORMER processing for queries domain.

```bash
python datasets/queries/transformer/transformer_queries.py
```

### `experiments/ner/queries/tableau/custom_ner/entities_mapping.py`

Strategy 1 - Point 2 & 3 Implementation
Point 2: Entities[Desc] → Entities[Formula] (Entity Mapping)
Point 3: Entities[Formula] → Formula String (Formula Generation)

```bash
python experiments/ner/queries/tableau/custom_ner/entities_mapping.py
```

### `experiments/ner/queries/tableau/pipeline/sequential_pipeline.py`

Strategy 1: Sequential Pipeline for Description → Formula Generation
Input: Natural language description
Output: Mathematical formula

Pipeline Steps:

1. Description → Entities[Desc] (Supervised NER)
2. Formulas → Entities[Formula] (Supervised NER for training data)
3. (Desc, Entities[Desc]) → Mapping → (Formula, Entities[Formula]) (Supervised)
4. Entities[Formula] → Formula Generation (Classification/Rule-based)

Each step is evaluated independently with metrics.

```bash
python experiments/ner/queries/tableau/pipeline/sequential_pipeline.py
```

### `experiments/ner/queries/tableau/pipeline/joint_training.py`

Strategy 2: Joint Training on (Description, Formula) Pairs
End-to-end training with realistic error propagation

```bash
python experiments/ner/queries/tableau/pipeline/joint_training.py
```

### `patterns/queries/tableau/test_create_ruler_tableau.py`

No description available

```bash
python patterns/queries/tableau/test_create_ruler_tableau.py
```

### `patterns/queries/tableau/test_rules_tableau_patterns.py`

No description available

```bash
python patterns/queries/tableau/test_rules_tableau_patterns.py
```

### `core/deployment/evaluation_unified.py`

Unified Evaluation Framework
Evaluates all models (spaCy, Transformer, RAG, LLM, Ensemble)

```bash
python core/deployment/evaluation_unified.py
```

### `core/deployment/evaluate_model.py`

No description available

```bash
python core/deployment/evaluate_model.py
```

### `core/deployment/deployment-evaluate_model.py`

Updated Model Evaluation for Deployment
Evaluates formula accuracy, not just NER entities

```bash
python core/deployment/deployment-evaluate_model.py
```

### `core/deployment/deployment_api.py`

REST API for Formula Generation
Provides endpoints for real-time formula mapping

```bash
python core/deployment/deployment_api.py
```

### `core/deployment/deployment_pipeline.py`

Deployment Pipeline for Formula Mapping Models
Handles model serving, API creation, and production deployment

```bash
python core/deployment/deployment_pipeline.py
```

### `core/deployment/deployment_batch.py`

Batch Processing for Formula Generation
Process large batches of descriptions efficiently

```bash
python core/deployment/deployment_batch.py
```

### `core/preprocessing/preprocessing_pipeline.py`

Data Preprocessing Pipeline for Formula Mapping
Handles data loading, cleaning, augmentation, and format conversion

```bash
python core/preprocessing/preprocessing_pipeline.py
```

### `core/training/training_transformer_.py`

Modern Transformer Training (2025 Best Practices)
Uses: LoRA fine-tuning on modern open-source models
Replaces: Full fine-tuning of outdated models like T5-small

```bash
python core/training/training_transformer_.py
```

### `core/training/training_llm.py`

Modern LLM Training for Formula Mapping (2025)
Primary approach: Few-shot prompting with prompt optimization
Features:

- Prompt caching for cost reduction
- Batch processing with rate limiting
- Automatic prompt optimization
- Structured output parsing
- Multi-provider support (OpenAI, Anthropic, local LLMs)

```bash
python core/training/training_llm.py
```

### `core/training/training_tranformer_.py`

Transformer-based Training for Formula Mapping
Uses BERT/T5 models via Hugging Face Transformers

```bash
python core/training/training_tranformer_.py
```

### `core/training/training_rag.py`

Modern RAG System (2025 Best Practices)
Uses: Vector DB + Reranking + LLM Generation (not just retrieval)
Replaces: Simple vector search with voting

```bash
python core/training/training_rag.py
```

### `core/training/training_rag_.py`

RAG (Retrieval Augmented Generation) Training for Formula Mapping
Uses vector embeddings and similarity search

```bash
python core/training/training_rag_.py
```

### `core/training/training_llm_.py`

LLM-based Formula Mapping
Uses GPT/Claude APIs with few-shot prompting

```bash
python core/training/training_llm_.py
```

### `core/evaluation/testing_model.py`

No description available

```bash
python core/evaluation/testing_model.py
```

### `backup_before_extension/custom_ner/rule_file_analyzer.py`

HypatiaX Rule File Analyzer
============================

Analyzes the rule file versioning system and identifies the disconnect
between expected and actual rule file naming conventions.

This script helps solve the BLOCKER identified in the morning assessment.

```bash
python backup_before_extension/custom_ner/rule_file_analyzer.py
```

### `backup_before_extension/demo/engine.py`

HypatiaX Engine - Core Processing Logic
Handles NER model integration, entity extraction, and formula generation

```bash
python backup_before_extension/demo/engine.py
```

### `backup_before_extension/demo/ui.py`

HypatiaX UI Components - Reusable UI building blocks
Provides rich console output, visualizations, and interactive components

```bash
python backup_before_extension/demo/ui.py
```

### `backup_before_extension/demo/examples.py`

HypatiaX Examples - Advanced example management and generation
Handles example datasets, validation, and benchmarking

```bash
python backup_before_extension/demo/examples.py
```

### `backup_before_extension/demo/demo_web_api.py`

No description available

```bash
python backup_before_extension/demo/demo_web_api.py
```

### `backup_before_extension/demo/demo_examples.py`

HypatiaX Demo Examples
Curated examples for demonstrating different capabilities

Curated example library
50+ example queries organized by category
Description, formula, and combined examples
Real-world use cases
Easy to access programmatically

```bash
python backup_before_extension/demo/demo_examples.py
```

### `backup_before_extension/demo/config.py`

HypatiaX Demo Configuration
Centralized configuration for all demo components
Easy to update and maintain

```bash
python backup_before_extension/demo/config.py
```

### `backup_before_extension/demo/demo_interactive.py`

HypatiaX Interactive Demo
Demonstrates NER capabilities for Tableau query processing

Main command-line demo

Interactive menu system
Multiple demo modes (desc, formulas, both)
Batch processing
Model comparison
Works with OR without trained models

```bash
python backup_before_extension/demo/demo_interactive.py
```

### `backup_before_extension/experiments/experiment_tracker.py`

Experiment tracking utility for HypatiaX
Registers and tracks experiments across all technologies

```bash
python backup_before_extension/experiments/experiment_tracker.py
```

### `backup_before_extension/utils/path_manager.py`

No description available

```bash
python backup_before_extension/utils/path_manager.py
```

### `backup_before_extension/utils/utils.py`

No description available

```bash
python backup_before_extension/utils/utils.py
```

### `backup_before_extension/scripts_/run_test_parallel_code_integration.py`

No description available

```bash
python backup_before_extension/scripts_/run_test_parallel_code_integration.py
```

### `backup_before_extension/scripts_/ner_test_simultion_package.py`

No description available

```bash
python backup_before_extension/scripts_/ner_test_simultion_package.py
```

### `backup_before_extension/scripts_/script_custom_ner.py`

No description available

```bash
python backup_before_extension/scripts_/script_custom_ner.py
```

### `backup_before_extension/scripts_/run_time_code.py`

No description available

```bash
python backup_before_extension/scripts_/run_time_code.py
```

### `backup_before_extension/scripts_/script_custom_entities.py`

No description available

```bash
python backup_before_extension/scripts_/script_custom_entities.py
```

### `backup_before_extension/scripts_/script_custom_patterns.py`

No description available

```bash
python backup_before_extension/scripts_/script_custom_patterns.py
```

### `backup_before_extension/scripts_/run_time_bundle_code.py`

No description available

```bash
python backup_before_extension/scripts_/run_time_bundle_code.py
```

### `backup_before_extension/scripts_/run_time_code_seq.py`

No description available

```bash
python backup_before_extension/scripts_/run_time_code_seq.py
```

### `backup_before_extension/scripts_/run_time_parallel_code.py`

No description available

```bash
python backup_before_extension/scripts_/run_time_parallel_code.py
```

### `backup_before_extension/scripts_/script_combined_data.py`

No description available

```bash
python backup_before_extension/scripts_/script_combined_data.py
```

### `backup_before_extension/custom_ner/queries/tableau/custom_tableau_components.py`

Custom Tableau Components with Auto-Migration
Loads NER rules with automatic change detection and backup for combined tableau rules.

```bash
python backup_before_extension/custom_ner/queries/tableau/custom_tableau_components.py
```

### `backup_before_extension/custom_ner/queries/tableau/custom_tableau_formulas_components.py`

Custom Tableau Formulas Components with Auto-Migration
Loads NER rules with automatic change detection and backup.

```bash
python backup_before_extension/custom_ner/queries/tableau/custom_tableau_formulas_components.py
```

### `backup_before_extension/demo/update/compare_old_vs_new.py`

Comparison Demo: Old Sequential Pipeline vs Modern LLM (2025)
============================================================

Shows side-by-side comparison to demonstrate why LLMs are better.

Usage:
    python compare_old_vs_new.py

```bash
python backup_before_extension/demo/update/compare_old_vs_new.py
```

### `backup_before_extension/demo/update/modern_llm_mapper.py`

Modern LLM-Based Formula Mapper (2025 Approach)
==============================================

Uses GPT-4/Claude API with few-shot prompting for formula generation.
NO training required. 95%+ accuracy out of the box.

Usage:
    python modern_llm_mapper.py --input "calculate area of circle"
    python modern_llm_mapper.py --batch test_sentences.txt
    python modern_llm_mapper.py --demo

```bash
python backup_before_extension/demo/update/modern_llm_mapper.py
```

### `backup_before_extension/demo/complete-system-guide/custom_demos/batch_processing_demo.py`

No description available

```bash
python backup_before_extension/demo/complete-system-guide/custom_demos/batch_processing_demo.py
```

### `backup_before_extension/demo/complete-system-guide/custom_demos/simple_clidemo.py`

No description available

```bash
python backup_before_extension/demo/complete-system-guide/custom_demos/simple_clidemo.py
```

### `backup_before_extension/demo/complete-system-guide/integration-patterns/pattern5.py`

No description available

```bash
python backup_before_extension/demo/complete-system-guide/integration-patterns/pattern5.py
```

### `backup_before_extension/datasets/queries/normalize/normalize_data.py`

No description available

```bash
python backup_before_extension/datasets/queries/normalize/normalize_data.py
```

### `backup_before_extension/datasets/queries/normalize/test.py`

No description available

```bash
python backup_before_extension/datasets/queries/normalize/test.py
```

### `backup_before_extension/experiments/ner/queries/tableau/custom_ner/entities_mapping.py`

Strategy 1 - Point 2 & 3 Implementation
Point 2: Entities[Desc] → Entities[Formula] (Entity Mapping)
Point 3: Entities[Formula] → Formula String (Formula Generation)

```bash
python backup_before_extension/experiments/ner/queries/tableau/custom_ner/entities_mapping.py
```

### `backup_before_extension/experiments/ner/queries/tableau/pipeline/sequential_pipeline.py`

Strategy 1: Sequential Pipeline for Description → Formula Generation
Input: Natural language description
Output: Mathematical formula

Pipeline Steps:

1. Description → Entities[Desc] (Supervised NER)
2. Formulas → Entities[Formula] (Supervised NER for training data)
3. (Desc, Entities[Desc]) → Mapping → (Formula, Entities[Formula]) (Supervised)
4. Entities[Formula] → Formula Generation (Classification/Rule-based)

Each step is evaluated independently with metrics.

```bash
python backup_before_extension/experiments/ner/queries/tableau/pipeline/sequential_pipeline.py
```

### `backup_before_extension/experiments/ner/queries/tableau/pipeline/joint_training.py`

Strategy 2: Joint Training on (Description, Formula) Pairs
End-to-end training with realistic error propagation

```bash
python backup_before_extension/experiments/ner/queries/tableau/pipeline/joint_training.py
```

### `backup_before_extension/patterns/queries/tableau/test_create_ruler_tableau.py`

No description available

```bash
python backup_before_extension/patterns/queries/tableau/test_create_ruler_tableau.py
```

### `backup_before_extension/patterns/queries/tableau/test_rules_tableau_patterns.py`

No description available

```bash
python backup_before_extension/patterns/queries/tableau/test_rules_tableau_patterns.py
```

### `backup_before_extension/core/deployment/evaluate_model.py`

No description available

```bash
python backup_before_extension/core/deployment/evaluate_model.py
```

### `backup_before_extension/core/evaluation/testing_model.py`

No description available

```bash
python backup_before_extension/core/evaluation/testing_model.py
```

### `setup.py`

Package entry points defined in setup.py

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/unit/test_entity_formulas.py
pytest tests/unit/test_description_model.py
pytest tests/unit/test_comb_multi_task_model.py
```

## 📚 Examples

- `demo/examples.py`
  HypatiaX Examples - Advanced example management and generation
Handles example datasets, validation,...
- `demo/demo_examples.py`
  HypatiaX Demo Examples
Curated examples for demonstrating different capabilities

Curated example li...

- `examples/training_example.py`
  No description available...
- `examples/llm_example.py`
  No description available...
- `examples/hybrid_example.py`
  No description available...
- `examples/agent_example.py`
  No description available...
- `examples/evaluation_example.py`
  No description available...
- `examples/transformer_example.py`
  No description available...
- `demo/complete-system-guide/usage_examples.py`
  3. examples.py - Example Management System
Purpose: Manage training/test examples with categorizatio...
- `demo/complete-system-guide/example_ui.py`
  2. ui.py - Reusable UI Components
Purpose: Rich console output, visualizations, and interactive comp...
- `demo/complete-system-guide/example_engine.py`
  1. engine.py - Core Processing Engine
Purpose: Handles NER model integration, entity extraction, and...
- `backup_before_extension/demo/examples.py`
  HypatiaX Examples - Advanced example management and generation
Handles example datasets, validation,...
- `backup_before_extension/demo/demo_examples.py`
  HypatiaX Demo Examples
Curated examples for demonstrating different capabilities

Curated example li...

- `backup_before_extension/examples/training_example.py`
  No description available...
- `backup_before_extension/examples/evaluation_example.py`
  No description available...
- `backup_before_extension/demo/complete-system-guide/usage_examples.py`
  3. examples.py - Example Management System
Purpose: Manage training/test examples with categorizatio...
- `backup_before_extension/demo/complete-system-guide/example_ui.py`
  2. ui.py - Reusable UI Components
Purpose: Rich console output, visualizations, and interactive comp...
- `backup_before_extension/demo/complete-system-guide/example_engine.py`
  1. engine.py - Core Processing Engine
Purpose: Handles NER model integration, entity extraction, and...

## 🔄 Common Workflows

### 1. Training a New Model

```python
from hypatiax.core.training import training_spacy

# Configure and train model
# See hypatiax/core/training/ for details
```

### 2. Using Custom NER

```python
from hypatiax.custom_ner.queries.tableau import custom_tableau_components

# Load and use NER model
# See tests/ for usage examples
```

### 3. Evaluating Models

```python
from hypatiax.core.evaluation import testing_model

# Evaluate model performance
```

## ⚠️ Troubleshooting

### Rule File Not Found Error

Run the fix script:

```bash
python rule_file_analyzer.py
./fix_rules.sh
```

### NLTK Not Found

```bash
pip install nltk
```

### Import Errors

Make sure you installed the package:

```bash
pip install -e .
```

## 📖 Additional Resources

- Full documentation: See `docs_generated/`
- API reference: See `docs_generated/modules/`
- Test examples: See `tests/`
- Training data: See `hypatiax/datasets/queries/tableau/`

## 🏗️ Architecture Overview

```
hypatiax/
├── core/              # Core functionality
│   ├── training/      # Model training
│   ├── evaluation/    # Model evaluation
│   └── preprocessing/ # Data preprocessing
├── custom_ner/        # Custom NER components
│   └── queries/       # Query-specific NER
│       └── tableau/   # Tableau query NER
├── datasets/          # Training/test datasets
├── data_spacy/        # spaCy models and data
└── models/            # Trained models
```

# Module: `core/deployment/deployment_pipeline.py`

## Description

Deployment Pipeline for Formula Mapping Models
Handles model serving, API creation, and production deployment

**Last Modified**: 2025-11-07T15:32:25.862854

## Dependencies

- `dataclasses`
- `datetime`
- `flask`
- `flask_cors`
- `json`
- `logging`
- `mapping_plus`
- `pathlib`
- `pickle`
- `spacy`
- `torch`
- `training_rag`
- `transformers`
- `typing`

## Constants

- `FLASK_AVAILABLE`
- `FLASK_AVAILABLE`

## Classes

### `DeploymentConfig`

Configuration for deployment

**Decorators**: `dataclass`

### `ModelRegistry`

Registry for loading and managing multiple models

**Methods**:

- `__init__(self, model_dir: str)`
- `register_spacy_model(self, name: str, model_path: str)`
  - Register spaCy NER model
- `register_transformer_model(self, name: str, model_path: str)`
  - Register Transformer model
- `register_rag_model(self, name: str, model_path: str)`
  - Register RAG model
- `register_ensemble_mapper(self, name: str, mapper)`
  - Register ensemble mapper
- `get_model(self, name: str) -> Optional[Dict]`
  - Get registered model
- `list_models(self) -> List[str]`
  - List all registered models
- `get_metadata(self) -> Dict`
  - Get all model metadata

### `PredictionService`

Service for making predictions

**Methods**:

- `__init__(self, registry: ModelRegistry)`
- `predict_with_spacy(self, model_name: str, text: str) -> Dict`
  - Predict using spaCy NER model
- `predict_with_transformer(self, model_name: str, text: str) -> Dict`
  - Predict using Transformer model
- `predict_with_rag(self, model_name: str, text: str) -> Dict`
  - Predict using RAG model
- `predict_with_ensemble(self, model_name: str, text: str, ner_entities: Optional[List]) -> Dict`
  - Predict using ensemble mapper
- `predict(self, model_name: str, text: str, ner_entities: Optional[List]) -> Dict`
  - Universal predict method

### `DeploymentAPI`

REST API for model deployment

**Methods**:

- `__init__(self, config: DeploymentConfig)`
- `_setup_logging(self)`
  - Setup logging configuration
- `_setup_routes(self)`
  - Setup API routes
- `run(self)`
  - Start the API server

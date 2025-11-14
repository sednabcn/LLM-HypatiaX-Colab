# Module: `core/deployment/deployment_api.py`

## Description

REST API for Formula Generation
Provides endpoints for real-time formula mapping

**Last Modified**: 2025-11-07T16:19:22.760790

## Dependencies

- `dataclasses`
- `flask`
- `flask_cors`
- `json`
- `logging`
- `mapping_plus`
- `pathlib`
- `spacy`
- `torch`
- `training_rag`
- `transformers`
- `typing`

## Classes

### `DeploymentConfig`

Configuration for deployment

**Decorators**: `dataclass`

### `ModelRegistry`

Registry for all available models

**Methods**:

- `__init__(self)`
- `register_spacy_model(self, name: str, model_path: str)`
  - Register spaCy NER model
- `register_transformer_model(self, name: str, model_path: str)`
  - Register Transformer model
- `register_rag_model(self, name: str, model_path: str)`
  - Register RAG model
- `register_ensemble_mapper(self, name: str, mapper)`
  - Register ensemble mapper
- `get_model(self, name: str)`
  - Get model by name
- `list_models(self) -> List[str]`
  - List all registered models

### `DeploymentAPI`

Flask API for formula generation

**Methods**:

- `__init__(self, config: DeploymentConfig)`
- `_register_routes(self)`
  - Register API endpoints
- `_generate_formula(self, description: str, model_info: Dict) -> Dict`
  - Generate formula using specified model
- `run(self)`
  - Start the API server

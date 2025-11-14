# Module: `mappings/mapping_hybrid.py`

## Description

Hybrid Formula Mapping System
Integrates ALL techniques: spaCy NER, Transformers, RAG, LLM, Rule-based, Ensemble

**Last Modified**: 2025-11-07T15:37:47.169158

## Dependencies

- `collections`
- `dataclasses`
- `json`
- `mapping_plus`
- `numpy`
- `pathlib`
- `re`
- `spacy`
- `torch`
- `training_llm`
- `training_rag`
- `transformers`
- `typing`

## Classes

### `HybridConfig`

Configuration for hybrid mapping

**Decorators**: `dataclass`

### `HybridFormulaMapper`

Unified mapper using all available techniques

**Methods**:

- `__init__(self, config: HybridConfig)`
- `_init_spacy(self)`
  - Initialize spaCy NER model
- `_init_transformer(self)`
  - Initialize Transformer model
- `_init_rag(self)`
  - Initialize RAG model
- `_init_llm(self)`
  - Initialize LLM client
- `_init_ensemble(self)`
  - Initialize ensemble mapper
- `predict_with_spacy(self, description: str) -> Dict`
  - Extract entities using spaCy NER
- `predict_with_transformer(self, description: str) -> Dict`
  - Generate formula using Transformer
- `predict_with_rag(self, description: str) -> Dict`
  - Generate formula using RAG
- `predict_with_llm(self, description: str) -> Dict`
  - Generate formula using LLM
- `predict_with_ensemble(self, description: str, ner_entities: Optional[List]) -> Dict`
  - Generate formula using ensemble mapper
- `predict_hybrid(self, description: str, use_cache: bool) -> Dict`
  - Hybrid prediction using all available techniques
- `batch_predict(self, descriptions: List[str]) -> List[Dict]`
  - Predict formulas for multiple descriptions
- `evaluate_techniques(self, test_data: List[Dict]) -> Dict`
  - Evaluate performance of each technique
- `export_results(self, results: List[Dict], output_path: str)`
  - Export prediction results to JSON

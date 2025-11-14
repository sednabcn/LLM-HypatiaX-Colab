# Module: `demo/engine.py`

## Description

HypatiaX Engine - Core Processing Logic
Handles NER model integration, entity extraction, and formula generation

**Last Modified**: 2025-11-10T20:41:00.582604

## Dependencies

- `dataclasses`
- `logging`
- `pandas`
- `pathlib`
- `re`
- `spacy`
- `time`
- `typing`

## Classes

### `Entity`

Represents an extracted entity from text

**Decorators**: `dataclass`

### `ProcessingResult`

Container for processing results

**Decorators**: `dataclass`

### `HypatiaXEngine`

Core processing engine for HypatiaX
Handles model loading, entity extraction, and formula generation

**Methods**:

- `__init__(self, desc_model_path: Optional[str], formula_model_path: Optional[str], use_gpu: bool)`
  - Initialize the HypatiaX engine
- `load_models(self) -> bool`
  - Load spaCy NER models
- `_load_vocab_mappings(self) -> Dict[<ast.Tuple object at 0x7fa6f889af50>]`
  - Load vocabulary mappings for fallback processing
- `extract_entities(self, text: str, use_model: bool) -> List[Entity]`
  - Extract entities from text using NER model or fallback
- `_extract_entities_rule_based(self, text: str) -> List[Entity]`
  - Rule-based entity extraction fallback
- `generate_formula(self, query: str, entities: List[Entity], method: str) -> str`
  - Generate Tableau formula from query and entities
- `_vocab_mapping(self, query: str, entities: List[Entity]) -> str`
  - Vocabulary-based formula generation
- `_sentence_mapping(self, query: str, entities: List[Entity]) -> str`
  - Sentence pattern-based formula generation
- `_regex_mapping(self, query: str, entities: List[Entity]) -> str`
  - Regex-based formula generation
- `_ner_mapping(self, query: str, entities: List[Entity]) -> str`
  - NER model-based formula generation
- `calculate_confidence(self, entities: List[Entity], formula: str) -> float`
  - Calculate confidence score for generated formula
- `process(self, query: str, method: str, use_model: bool) -> ProcessingResult`
  - Process a query end-to-end
- `batch_process(self, queries: List[str], method: str, use_model: bool) -> List[ProcessingResult]`
  - Process multiple queries
- `get_stats(self) -> Dict[<ast.Tuple object at 0x7fa6f8633010>]`
  - Get processing statistics
- `export_results(self, results: List[ProcessingResult], output_path: str, format: str) -> bool`
  - Export processing results

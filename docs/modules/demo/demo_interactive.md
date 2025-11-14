# Module: `demo/demo_interactive.py`

## Description

HypatiaX Interactive Demo
Demonstrates NER capabilities for Tableau query processing

Main command-line demo

Interactive menu system
Multiple demo modes (desc, formulas, both)
Batch processing
Model comparison
Works with OR without trained models

**Last Modified**: 2025-11-10T19:54:44.659720

## Dependencies

- `hypatiax.utils.model_loader`
- `json`
- `pathlib`
- `sys`
- `traceback`
- `typing`

## Classes

### `HypatiaXDemo`

Interactive demo for HypatiaX NER system
Showcases description and formula entity extraction

**Methods**:

- `__init__(self, model_type: str)`
  - Initialize demo with a model type
- `_load_model(self)`
  - Load the trained spaCy model
- `process_text(self, text: str) -> Dict`
  - Process text and extract entities
- `_mock_entities(self, text: str) -> List[Dict]`
  - Generate mock entities for demo mode
- `display_result(self, result: Dict)`
  - Display processing result in a formatted way
- `run_example(self, example_text: str)`
  - Run a single example
- `run_examples(self, examples: List[str])`
  - Run multiple examples
- `interactive_mode(self)`
  - Run in interactive mode

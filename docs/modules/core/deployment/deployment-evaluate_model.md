# Module: `core/deployment/deployment-evaluate_model.py`

## Description

Updated Model Evaluation for Deployment
Evaluates formula accuracy, not just NER entities

**Last Modified**: 2025-11-07T16:18:46.393446

## Dependencies

- `json`
- `numpy`
- `pandas`
- `pathlib`
- `spacy`
- `spacy.scorer`
- `spacy.training`
- `typing`

## Classes

### `FormulaAccuracyEvaluator`

Evaluate formula prediction accuracy

**Methods**:

- `__init__(self, model_path: str)`
- `exact_match(self, predicted: str, ground_truth: str) -> bool`
  - Check exact string match
- `partial_match(self, predicted: str, ground_truth: str) -> float`
  - Calculate token-level overlap
- `syntax_correctness(self, formula: str) -> bool`
  - Check if formula has valid syntax
- `semantic_correctness(self, predicted: str, ground_truth: str) -> bool`
  - Check if operations match semantically
- `evaluate_predictions(self, predictions: List[Dict]) -> Dict`
  - Evaluate list of predictions
- `evaluate_from_file(self, predictions_file: str) -> Dict`
  - Load predictions from file and evaluate
- `evaluate_ner_model(self, test_file: str) -> Dict`
  - Evaluate spaCy NER model (backward compatibility)
- `generate_report(self, metrics: Dict, output_file: str)`
  - Generate evaluation report

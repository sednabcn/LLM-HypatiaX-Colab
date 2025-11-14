# Module: `core/deployment/evaluation_unified.py`

## Description

Unified Evaluation Framework
Evaluates all models (spaCy, Transformer, RAG, LLM, Ensemble)

**Last Modified**: 2025-11-07T15:18:57.400305

## Dependencies

- `dataclasses`
- `json`
- `matplotlib.pyplot`
- `numpy`
- `pandas`
- `pathlib`
- `seaborn`
- `spacy`
- `spacy.scorer`
- `spacy.training`
- `typing`

## Classes

### `EvaluationMetrics`

Container for evaluation metrics

**Decorators**: `dataclass`

### `FormulaEvaluator`

Evaluate formula predictions

**Methods**:

- `exact_match(predicted: str, ground_truth: str) -> bool`
  - Check exact string match
- `normalize_formula(formula: str) -> str`
  - Normalize formula for comparison
- `partial_match(predicted: str, ground_truth: str) -> float`
  - Calculate partial match score
- `check_syntax(formula: str) -> bool`
  - Check if formula has valid syntax
- `check_semantic(predicted: str, ground_truth: str, query: str) -> bool`
  - Check semantic correctness

### `ModelEvaluator`

Evaluate different model types

**Methods**:

- `__init__(self)`
- `evaluate_predictions(self, predictions: List[Dict]) -> EvaluationMetrics`
  - Evaluate a list of predictions
- `evaluate_spacy_ner(self, model_path: str, test_data: List[Tuple]) -> Dict`
  - Evaluate spaCy NER model
- `evaluate_from_file(self, predictions_file: str) -> EvaluationMetrics`
  - Evaluate predictions from JSON file

### `ComparisonReport`

Generate comparison reports across models

**Methods**:

- `__init__(self)`
- `add_model_results(self, model_name: str, metrics: EvaluationMetrics)`
  - Add results for a model
- `generate_table(self) -> pd.DataFrame`
  - Generate comparison table
- `plot_comparison(self, save_path: str)`
  - Plot comparison chart
- `save_report(self, output_path: str)`
  - Save detailed report

# Module: `core/preprocessing/preprocessing_pipeline.py`

## Description

Data Preprocessing Pipeline for Formula Mapping
Handles data loading, cleaning, augmentation, and format conversion

**Last Modified**: 2025-11-07T15:13:26.256881

## Dependencies

- `collections`
- `json`
- `numpy`
- `pandas`
- `pathlib`
- `re`
- `sklearn.model_selection`
- `typing`

## Classes

### `DataValidator`

Validate and clean input data

**Methods**:

- `validate_description(text: str) -> bool`
  - Check if description is valid
- `validate_formula(formula: str) -> bool`
  - Check if formula has basic structure
- `clean_text(text: str) -> str`
  - Clean and normalize text

### `DataAugmenter`

Augment training data with variations

**Methods**:

- `augment_description(desc: str, num_variants: int) -> List[str]`
  - Create variations of descriptions
- `add_noise(desc: str) -> str`
  - Add slight noise to create robustness

### `FormatConverter`

Convert between different data formats

**Methods**:

- `to_spacy_format(data: pd.DataFrame, text_col: str, entity_col: Optional[str]) -> List[Tuple]`
  - Convert to spaCy training format
- `_parse_entities(text: str, entity_data: str) -> List[Tuple]`
  - Parse entity annotations
- `_auto_detect_entities(text: str) -> List[Tuple]`
  - Auto-detect common entities
- `to_mapping_format(data: pd.DataFrame, desc_col: str, formula_col: str) -> List[Tuple[<ast.Tuple object at 0x7fa6f8620a10>]]`
  - Convert to mapping training format
- `to_transformer_format(data: pd.DataFrame, desc_col: str, formula_col: str) -> Dict[<ast.Tuple object at 0x7fa6f85747d0>]`
  - Convert to Hugging Face format

### `DataSplitter`

Split data into train/val/test sets with stratification

**Methods**:

- `split_data(data: List, train_ratio: float, val_ratio: float, test_ratio: float, shuffle: bool, random_seed: int) -> Tuple`
  - Split data maintaining distribution
- `stratified_split(data: pd.DataFrame, stratify_col: str, train_ratio: float, val_ratio: float) -> Tuple`
  - Split maintaining class distribution

### `PreprocessingPipeline`

Main preprocessing pipeline

**Methods**:

- `__init__(self, config: Dict)`
- `load_data(self, filepath: str, file_format: str) -> pd.DataFrame`
  - Load data from various formats
- `clean_data(self, data: pd.DataFrame, desc_col: str, formula_col: str) -> pd.DataFrame`
  - Clean and validate data
- `augment_data(self, data: pd.DataFrame, desc_col: str, formula_col: str, augment_factor: int) -> pd.DataFrame`
  - Augment training data
- `prepare_for_spacy(self, data: pd.DataFrame, desc_col: str, output_path: str)`
  - Prepare data for spaCy NER training
- `prepare_for_mapping(self, data: pd.DataFrame, desc_col: str, formula_col: str, output_path: str)`
  - Prepare data for ensemble mapping training
- `prepare_for_transformer(self, data: pd.DataFrame, desc_col: str, formula_col: str, output_path: str)`
  - Prepare data for transformer models
- `run_full_pipeline(self, input_file: str, output_dir: str, desc_col: str, formula_col: str, augment: bool, prepare_all_formats: bool)`
  - Run complete preprocessing pipeline

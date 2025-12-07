#!/usr/bin/python3
"""
Data Preprocessing Pipeline for Formula Mapping
Handles data loading, cleaning, augmentation, and format conversion
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class DataValidator:
    """Validate and clean input data"""

    @staticmethod
    def validate_description(text: str) -> bool:
        """Check if description is valid"""
        if not text or not isinstance(text, str):
            return False
        if len(text.strip()) < 3:
            return False
        return True

    @staticmethod
    def validate_formula(formula: str) -> bool:
        """Check if formula has basic structure"""
        if not formula or not isinstance(formula, str):
            return False
        # Must have at least a function or operation
        if not re.search(r"[A-Z]{2,}|[\+\-\*/]", formula):
            return False
        return True

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        text = re.sub(r"\s+", " ", text)  # Normalize whitespace
        text = text.strip()
        return text


class DataAugmenter:
    """Augment training data with variations"""

    @staticmethod
    def augment_description(desc: str, num_variants: int = 3) -> List[str]:
        """Create variations of descriptions"""
        variants = [desc]

        # Synonym replacements
        synonyms = {
            "total": ["sum", "aggregate"],
            "average": ["mean", "avg"],
            "count": ["number of", "tally"],
            "maximum": ["max", "highest"],
            "minimum": ["min", "lowest"],
        }

        desc_lower = desc.lower()
        for original, alternatives in synonyms.items():
            if original in desc_lower:
                for alt in alternatives[: num_variants - 1]:
                    variant = re.sub(rf"\b{original}\b", alt, desc, flags=re.IGNORECASE)
                    if variant != desc:
                        variants.append(variant)

        return list(set(variants))[:num_variants]

    @staticmethod
    def add_noise(desc: str) -> str:
        """Add slight noise to create robustness"""
        # Random case changes
        if np.random.random() > 0.5:
            words = desc.split()
            if words:
                idx = np.random.randint(len(words))
                words[idx] = words[idx].lower()
                return " ".join(words)
        return desc


class FormatConverter:
    """Convert between different data formats"""

    @staticmethod
    def to_spacy_format(data: pd.DataFrame, text_col: str, entity_col: Optional[str] = None) -> List[Tuple]:
        """Convert to spaCy training format"""
        spacy_data = []

        for idx, row in data.iterrows():
            text = row[text_col]

            if entity_col and entity_col in row:
                # Parse entities from column
                entities = FormatConverter._parse_entities(text, row[entity_col])
            else:
                # Auto-detect entities
                entities = FormatConverter._auto_detect_entities(text)

            spacy_data.append((text, {"entities": entities}))

        return spacy_data

    @staticmethod
    def _parse_entities(text: str, entity_data: str) -> List[Tuple]:
        """Parse entity annotations"""
        entities = []
        try:
            # Assuming entity_data is JSON string: [{"text": "sum", "label": "OPER", "start": 0, "end": 3}]
            entity_list = json.loads(entity_data) if isinstance(entity_data, str) else entity_data
            for ent in entity_list:
                entities.append((ent["start"], ent["end"], ent["label"]))
        except:
            pass
        return entities

    @staticmethod
    def _auto_detect_entities(text: str) -> List[Tuple]:
        """Auto-detect common entities"""
        entities = []

        # Operations
        operations = {
            "sum": "OPER",
            "total": "OPER",
            "average": "OPER",
            "avg": "OPER",
            "count": "OPER",
            "max": "OPER",
            "min": "OPER",
            "median": "OPER",
        }

        for op, label in operations.items():
            pattern = rf"\b{op}\b"
            for match in re.finditer(pattern, text.lower()):
                entities.append((match.start(), match.end(), label))

        # Column names (capitalized words)
        for match in re.finditer(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text):
            entities.append((match.start(), match.end(), "TARGET"))

        return entities

    @staticmethod
    def to_mapping_format(data: pd.DataFrame, desc_col: str, formula_col: str) -> List[Tuple[str, str]]:
        """Convert to mapping training format"""
        mapping_data = []

        for idx, row in data.iterrows():
            desc = str(row[desc_col]).strip()
            formula = str(row[formula_col]).strip()

            if DataValidator.validate_description(desc) and DataValidator.validate_formula(formula):
                mapping_data.append((desc, formula))

        return mapping_data

    @staticmethod
    def to_transformer_format(data: pd.DataFrame, desc_col: str, formula_col: str) -> Dict[str, List]:
        """Convert to Hugging Face format"""
        return {"input_text": data[desc_col].tolist(), "target_text": data[formula_col].tolist()}


class DataSplitter:
    """Split data into train/val/test sets with stratification"""

    @staticmethod
    def split_data(
        data: List,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        shuffle: bool = True,
        random_seed: int = 42,
    ) -> Tuple:
        """Split data maintaining distribution"""

        if shuffle:
            np.random.seed(random_seed)
            np.random.shuffle(data)

        n = len(data)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)

        train_data = data[:train_end]
        val_data = data[train_end:val_end]
        test_data = data[val_end:]

        return train_data, val_data, test_data

    @staticmethod
    def stratified_split(
        data: pd.DataFrame, stratify_col: str, train_ratio: float = 0.7, val_ratio: float = 0.15
    ) -> Tuple:
        """Split maintaining class distribution"""
        from sklearn.model_selection import train_test_split

        train_data, temp_data = train_test_split(
            data, train_size=train_ratio, stratify=data[stratify_col], random_state=42
        )

        val_size = val_ratio / (1 - train_ratio)
        val_data, test_data = train_test_split(
            temp_data, train_size=val_size, stratify=temp_data[stratify_col], random_state=42
        )

        return train_data, val_data, test_data


class PreprocessingPipeline:
    """Main preprocessing pipeline"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.validator = DataValidator()
        self.augmenter = DataAugmenter()
        self.converter = FormatConverter()
        self.splitter = DataSplitter()

    def load_data(self, filepath: str, file_format: str = "csv") -> pd.DataFrame:
        """Load data from various formats"""
        if file_format == "csv":
            return pd.read_csv(filepath)
        elif file_format == "json":
            return pd.read_json(filepath)
        elif file_format == "excel":
            return pd.read_excel(filepath)
        else:
            raise ValueError(f"Unsupported format: {file_format}")

    def clean_data(self, data: pd.DataFrame, desc_col: str, formula_col: str) -> pd.DataFrame:
        """Clean and validate data"""

        # Remove invalid entries
        data = data[
            data[desc_col].apply(self.validator.validate_description)
            & data[formula_col].apply(self.validator.validate_formula)
        ].copy()

        # Clean text
        data[desc_col] = data[desc_col].apply(self.validator.clean_text)
        data[formula_col] = data[formula_col].apply(self.validator.clean_text)

        # Remove duplicates
        data = data.drop_duplicates(subset=[desc_col])

        return data

    def augment_data(
        self, data: pd.DataFrame, desc_col: str, formula_col: str, augment_factor: int = 2
    ) -> pd.DataFrame:
        """Augment training data"""

        augmented_rows = []

        for idx, row in data.iterrows():
            desc = row[desc_col]
            formula = row[formula_col]

            # Create variants
            variants = self.augmenter.augment_description(desc, augment_factor)

            for variant in variants:
                new_row = row.copy()
                new_row[desc_col] = variant
                augmented_rows.append(new_row)

        return pd.DataFrame(augmented_rows)

    def prepare_for_spacy(self, data: pd.DataFrame, desc_col: str, output_path: str):
        """Prepare data for spaCy NER training"""

        spacy_data = self.converter.to_spacy_format(data, desc_col)

        # Split data
        train_data, val_data, test_data = self.splitter.split_data(spacy_data)

        # Save
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / "train_spacy.json", "w") as f:
            json.dump(train_data, f, indent=2)

        with open(output_dir / "val_spacy.json", "w") as f:
            json.dump(val_data, f, indent=2)

        with open(output_dir / "test_spacy.json", "w") as f:
            json.dump(test_data, f, indent=2)

        return train_data, val_data, test_data

    def prepare_for_mapping(self, data: pd.DataFrame, desc_col: str, formula_col: str, output_path: str):
        """Prepare data for ensemble mapping training"""

        mapping_data = self.converter.to_mapping_format(data, desc_col, formula_col)

        # Split data
        train_data, val_data, test_data = self.splitter.split_data(mapping_data)

        # Save
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / "train_mapping.json", "w") as f:
            json.dump(train_data, f, indent=2)

        with open(output_dir / "val_mapping.json", "w") as f:
            json.dump(val_data, f, indent=2)

        with open(output_dir / "test_mapping.json", "w") as f:
            json.dump(test_data, f, indent=2)

        return train_data, val_data, test_data

    def prepare_for_transformer(self, data: pd.DataFrame, desc_col: str, formula_col: str, output_path: str):
        """Prepare data for transformer models"""

        transformer_data = self.converter.to_transformer_format(data, desc_col, formula_col)

        # Create DataFrame for splitting
        df = pd.DataFrame(transformer_data)

        # Split
        train_df, val_df, test_df = self.splitter.stratified_split(df, stratify_col="target_text")

        # Save
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        train_df.to_json(output_dir / "train_transformer.json", orient="records")
        val_df.to_json(output_dir / "val_transformer.json", orient="records")
        test_df.to_json(output_dir / "test_transformer.json", orient="records")

        return train_df, val_df, test_df

    def run_full_pipeline(
        self,
        input_file: str,
        output_dir: str,
        desc_col: str = "Description",
        formula_col: str = "Formula",
        augment: bool = True,
        prepare_all_formats: bool = True,
    ):
        """Run complete preprocessing pipeline"""

        print("=" * 70)
        print("PREPROCESSING PIPELINE")
        print("=" * 70)

        # Load
        print(f"\n1. Loading data from {input_file}...")
        data = self.load_data(input_file)
        print(f"   Loaded {len(data)} records")

        # Clean
        print("\n2. Cleaning data...")
        data = self.clean_data(data, desc_col, formula_col)
        print(f"   {len(data)} records after cleaning")

        # Augment
        if augment:
            print("\n3. Augmenting data...")
            data = self.augment_data(data, desc_col, formula_col)
            print(f"   {len(data)} records after augmentation")

        # Prepare for different formats
        output_path = Path(output_dir)

        if prepare_all_formats:
            print("\n4. Preparing data for all formats...")

            # SpaCy format
            print("   - SpaCy NER format...")
            self.prepare_for_spacy(data, desc_col, output_path / "spacy")

            # Mapping format
            print("   - Ensemble mapping format...")
            self.prepare_for_mapping(data, desc_col, formula_col, output_path / "mapping")

            # Transformer format
            print("   - Transformer format...")
            self.prepare_for_transformer(data, desc_col, formula_col, output_path / "transformer")

        print("\n✅ Preprocessing complete!")
        print(f"   Output saved to: {output_path}")
        print("=" * 70)

        return data


# Example usage
if __name__ == "__main__":
    # Create sample data
    sample_data = {
        "Description": [
            "average of Petal Length",
            "sum of Sales",
            "count of customers",
            "total revenue by region",
            "maximum price",
        ],
        "Formula": [
            "AVG([Petal Length])",
            "SUM([Sales])",
            "COUNT([Customer])",
            "SUM([Revenue]) GROUP BY [Region]",
            "MAX([Price])",
        ],
    }

    df = pd.DataFrame(sample_data)
    df.to_csv("sample_input.csv", index=False)

    # Run pipeline
    pipeline = PreprocessingPipeline()
    pipeline.run_full_pipeline(
        input_file="sample_input.csv", output_dir="./preprocessed_data", augment=True, prepare_all_formats=True
    )

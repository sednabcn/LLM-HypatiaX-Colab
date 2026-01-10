"""Transformer data preprocessing"""

import json
from typing import Any, Dict, List

from transformers import AutoTokenizer


class TransformerPreprocessor:
    """Preprocess data for transformer models"""

    def __init__(self, model_name: str = "bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def prepare_seq2seq_data(
        self, input_texts: List[str], target_texts: List[str], max_length: int = 512
    ) -> Dict[str, Any]:
        """Prepare data for sequence-to-sequence task"""
        inputs = self.tokenizer(
            input_texts,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        targets = self.tokenizer(
            target_texts,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        return {
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs["attention_mask"],
            "labels": targets["input_ids"],
        }

    def save_prepared_data(self, data: Dict, output_path: str):
        """Save prepared data to file"""
        # Save as JSON for now (can be extended to other formats)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

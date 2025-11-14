from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TransformerConfig:
    """Configuration for transformer training"""
    model_name: str = "google/flan-t5-base"
    use_lora: bool = True
    lora_r: int = 8
    learning_rate: float = 3e-4
    batch_size: int = 8
    num_epochs: int = 10
    output_dir: str = "./models/queries/tableau/transformers/t5_formula_mapper"

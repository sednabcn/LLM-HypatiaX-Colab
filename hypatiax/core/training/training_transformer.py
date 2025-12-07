"""Transformer model training"""

from typing import Any, Dict

import torch
from transformers import AutoModelForSeq2SeqLM, Trainer, TrainingArguments


class TransformerTrainer:
    """Train transformer models for expression mapping"""

    def __init__(self, model_name: str = "t5-base", output_dir: str = "models/queries/tableau/transformers"):
        self.model_name = model_name
        self.output_dir = output_dir
        self.model = None

    def initialize_model(self):
        """Initialize model for training"""
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

    def train(
        self, train_dataset, eval_dataset=None, num_epochs: int = 10, learning_rate: float = 5e-5, batch_size: int = 16
    ):
        """Train the transformer model"""
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=num_epochs,
            learning_rate=learning_rate,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            evaluation_strategy="epoch" if eval_dataset else "no",
            save_strategy="epoch",
            logging_dir=f"{self.output_dir}/logs",
            load_best_model_at_end=True if eval_dataset else False,
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
        )

        trainer.train()
        return trainer

    def save_model(self, path: str = None):
        """Save trained model"""
        save_path = path or f"{self.output_dir}/final_model"
        self.model.save_pretrained(save_path)

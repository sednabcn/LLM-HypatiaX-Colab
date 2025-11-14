#!/usr/bin/python3
"""
Transformer-based Training for Formula Mapping
Uses BERT/T5 models via Hugging Face Transformers
"""

import torch
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM,
    T5ForConditionalGeneration,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback
)
import matplotlib.pyplot as plt


@dataclass
class TransformerConfig:
    """Configuration for transformer training"""
    model_name: str = "t5-small"
    max_length: int = 128
    learning_rate: float = 5e-5
    batch_size: int = 16
    num_epochs: int = 10
    warmup_steps: int = 500
    weight_decay: float = 0.01
    save_steps: int = 100
    eval_steps: int = 100
    early_stopping_patience: int = 3
    output_dir: str = "./models/transformer"


class FormulaMappingDataset(Dataset):
    """Dataset for seq2seq formula mapping"""
    
    def __init__(self, data: List[Dict], tokenizer, max_length: int = 128):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Add prefix for T5
        input_text = f"translate description to formula: {item['input_text']}"
        
        # Tokenize input
        input_encoding = self.tokenizer(
            input_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Tokenize target
        target_encoding = self.tokenizer(
            item['target_text'],
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': input_encoding['input_ids'].squeeze(),
            'attention_mask': input_encoding['attention_mask'].squeeze(),
            'labels': target_encoding['input_ids'].squeeze()
        }


class TransformerTrainer:
    """Train transformer models for formula mapping"""
    
    def __init__(self, config: TransformerConfig = None):
        self.config = config or TransformerConfig()
        self.tokenizer = None
        self.model = None
        self.trainer = None
        self.history = {
            'train_loss': [],
            'eval_loss': [],
            'epoch': []
        }
    
    def load_data(self, train_path: str, val_path: str) -> Tuple[List, List]:
        """Load training and validation data"""
        with open(train_path, 'r') as f:
            train_data = json.load(f)
        
        with open(val_path, 'r') as f:
            val_data = json.load(f)
        
        return train_data, val_data
    
    def prepare_model(self):
        """Initialize tokenizer and model"""
        print(f"Loading {self.config.model_name}...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.config.model_name)
        
        print(f"Model loaded: {self.model.num_parameters():,} parameters")
    
    def train(self, train_data: List[Dict], val_data: List[Dict]):
        """Train the model"""
        
        # Create datasets
        train_dataset = FormulaMappingDataset(
            train_data, self.tokenizer, self.config.max_length
        )
        val_dataset = FormulaMappingDataset(
            val_data, self.tokenizer, self.config.max_length
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            weight_decay=self.config.weight_decay,
            logging_dir=f'{self.config.output_dir}/logs',
            logging_steps=50,
            evaluation_strategy="steps",
            eval_steps=self.config.eval_steps,
            save_steps=self.config.save_steps,
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to="none"
        )
        
        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            self.tokenizer,
            model=self.model,
            padding=True
        )
        
        # Trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
            callbacks=[EarlyStoppingCallback(
                early_stopping_patience=self.config.early_stopping_patience
            )]
        )
        
        # Train
        print("\nStarting training...")
        train_result = self.trainer.train()
        
        # Save model
        self.trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir)
        
        # Extract history
        for log in self.trainer.state.log_history:
            if 'loss' in log:
                self.history['train_loss'].append(log['loss'])
                self.history['epoch'].append(log['epoch'])
            if 'eval_loss' in log:
                self.history['eval_loss'].append(log['eval_loss'])
        
        print("\n✅ Training complete!")
        return train_result
    
    def plot_history(self, save_path: str = None):
        """Plot training history"""
        plt.figure(figsize=(10, 6))
        
        if self.history['train_loss']:
            plt.plot(self.history['train_loss'], label='Training Loss')
        
        if self.history['eval_loss']:
            plt.plot(self.history['eval_loss'], label='Validation Loss')
        
        plt.xlabel('Steps')
        plt.ylabel('Loss')
        plt.title('Training History - Transformer Model')
        plt.legend()
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
        
        plt.show()
    
    def predict(self, descriptions: List[str]) -> List[str]:
        """Generate formulas for descriptions"""
        self.model.eval()
        predictions = []
        
        for desc in descriptions:
            input_text = f"translate description to formula: {desc}"
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                max_length=self.config.max_length,
                truncation=True
            )
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=self.config.max_length,
                    num_beams=4,
                    early_stopping=True
                )
            
            formula = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            predictions.append(formula)
        
        return predictions


def main():
    """Example usage"""
    print("="*70)
    print("TRANSFORMER TRAINING FOR FORMULA MAPPING")
    print("="*70)
    
    # Configuration
    config = TransformerConfig(
        model_name="t5-small",
        num_epochs=5,
        batch_size=8,
        output_dir="./models/transformer_formula_mapper"
    )
    
    # Initialize trainer
    trainer = TransformerTrainer(config)
    trainer.prepare_model()
    
    # Load data
    train_data, val_data = trainer.load_data(
        './preprocessed_data/transformer/train_transformer.json',
        './preprocessed_data/transformer/val_transformer.json'
    )
    
    print(f"\nTraining samples: {len(train_data)}")
    print(f"Validation samples: {len(val_data)}")
    
    # Train
    trainer.train(train_data, val_data)
    
    # Plot history
    trainer.plot_history('./models/transformer_formula_mapper/training_plot.png')
    
    # Test predictions
    test_descriptions = [
        "average of Sales",
        "sum of Revenue by Region",
        "count unique customers"
    ]
    
    print("\n" + "="*70)
    print("TEST PREDICTIONS")
    print("="*70)
    
    predictions = trainer.predict(test_descriptions)
    for desc, formula in zip(test_descriptions, predictions):
        print(f"\nInput: {desc}")
        print(f"Predicted: {formula}")


if __name__ == "__main__":
    main()

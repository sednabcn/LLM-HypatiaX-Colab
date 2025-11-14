"""Transformer model configurations"""
from typing import Dict, Any

class TransformerConfig:
    """Configuration for BERT/T5 models"""
    
    # Model selection
    BERT_MODEL = "bert-base-uncased"
    T5_MODEL = "t5-base"
    
    # Training hyperparameters
    LEARNING_RATE = 5e-5
    BATCH_SIZE = 16
    NUM_EPOCHS = 10
    MAX_LENGTH = 512
    
    # Paths
    TRANSFORMER_MODEL_DIR = "models/queries/tableau/transformers"
    TRANSFORMER_DATA_DIR = "datasets/queries/tableau/transformer"
    
    @classmethod
    def get_config(cls, model_type: str = "bert") -> Dict[str, Any]:
        """Get configuration for specific model type"""
        return {
            "model_name": cls.BERT_MODEL if model_type == "bert" else cls.T5_MODEL,
            "learning_rate": cls.LEARNING_RATE,
            "batch_size": cls.BATCH_SIZE,
            "num_epochs": cls.NUM_EPOCHS,
            "max_length": cls.MAX_LENGTH,
            "model_dir": cls.TRANSFORMER_MODEL_DIR,
            "data_dir": cls.TRANSFORMER_DATA_DIR,
        }

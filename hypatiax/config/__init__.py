"""
HypatiaX Configuration Module

This module provides centralized configuration management for:
- Paths (datasets, models, outputs)
- Model training parameters
- Data processing settings
- Entity labels and constants

Usage:
    from hypatiax.config import config, paths, ModelConfig
    
    # Access paths
    datasets_path = paths.datasets
    
    # Access model config
    training_params = ModelConfig.training_desc()
"""

from .base import Config
from .paths import PathConfig, paths
from .model_configs import ModelConfig, TrainingConfig, DataConfig
from .constants import EntityLabels, FileFormats, DEFAULT_STOPWORDS

# Global config instance
config = Config()

__all__ = [
    'config',
    'paths',
    'Config',
    'PathConfig',
    'ModelConfig',
    'TrainingConfig',
    'DataConfig',
    'EntityLabels',
    'FileFormats',
    'DEFAULT_STOPWORDS'
]

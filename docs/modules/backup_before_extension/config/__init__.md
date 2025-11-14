# Module: `backup_before_extension/config/__init__.py`

## Description

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

**Last Modified**: 2025-11-09T18:19:05.601183

## Dependencies

- `base`
- `constants`
- `model_configs`
- `paths`

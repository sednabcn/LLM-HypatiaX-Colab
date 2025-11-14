"""
Base Configuration Class

Central configuration management for HypatiaX.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
from dataclasses import dataclass, asdict


class Config:
    """
    Main configuration class that ties together all config components.
    
    Usage:
        config = Config()
        config.print_all()
        config.save_to_file('config.json')
    """
    
    def __init__(self):
        from .paths import paths
        from .model_configs import ModelConfig
        from .constants import EntityLabels
        
        self.paths = paths
        self.models = ModelConfig
        self.entities = EntityLabels
        
        # Environment detection
        self.environment = self._detect_environment()
        self.debug_mode = os.getenv('HYPATIAX_DEBUG', 'False').lower() == 'true'
    
    def _detect_environment(self) -> str:
        """Detect execution environment"""
        if 'COLAB_GPU' in os.environ or os.path.exists('/content'):
            return 'colab'
        elif os.getenv('GITHUB_ACTIONS') == 'true':
            return 'github'
        elif os.path.exists('/kaggle'):
            return 'kaggle'
        elif os.path.exists('/.dockerenv'):
            return 'docker'
        else:
            return 'local'
    
    def print_all(self):
        """Print all configuration settings"""
        print("=" * 70)
        print("HypatiaX Configuration")
        print("=" * 70)
        print(f"Environment: {self.environment}")
        print(f"Debug Mode:  {self.debug_mode}")
        print()
        
        # Print paths
        self.paths.print_paths()
        
        print()
        print("Model Configurations Available:")
        print("  - ModelConfig.training_desc()")
        print("  - ModelConfig.training_formulas()")
        print("  - ModelConfig.training_combined()")
        print("=" * 70)
    
    def save_to_file(self, filepath: str):
        """Save configuration to JSON file"""
        config_dict = {
            'environment': self.environment,
            'debug_mode': self.debug_mode,
            'paths': {
                'root': str(self.paths.root),
                'hypatiax': str(self.paths.hypatiax),
                'datasets': str(self.paths.datasets),
                'data_spacy': str(self.paths.data_spacy),
                'outputs': str(self.paths.outputs)
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"✅ Configuration saved to {filepath}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        parts = key.split('.')
        obj = self
        
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return default
        
        return obj


@dataclass
class BaseDataConfig:
    """Base configuration for data processing"""
    test_size: float = 0.2
    val_size: float = 0.1
    random_state: int = 42
    shuffle: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def update(self, **kwargs):
        """Update configuration"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

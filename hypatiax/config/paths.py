"""
Path Configuration Management

Handles all path-related configurations with environment detection.
"""

import os
from pathlib import Path
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


class PathConfig:
    """
    Centralized path management for HypatiaX.
    
    Automatically detects project root and sets up all necessary paths.
    Supports multiple environments (local, Colab, GitHub Actions, etc.)
    
    Usage:
        from hypatiax.config import paths
        
        # Access paths
        datasets_dir = paths.datasets
        output_file = paths.get_output_path('models', 'my_model')
    """
    
    def __init__(self, project_name: str = "LLM-HypatiaX-OLD"):
        self.project_name = project_name
        self.environment = self._detect_environment()
        
        # Get root directory
        env_root = os.getenv('HYPATIAX_ROOT')
        if env_root:
            self.root = Path(env_root)
        else:
            self.root = self._find_project_root()
        
        # Core directories
        self.hypatiax = self.root / 'hypatiax'
        self.datasets = self.hypatiax / 'datasets'
        self.data_spacy = self.hypatiax / 'data_spacy'
        self.custom_ner = self.hypatiax / 'custom_ner'
        self.outputs = self.root / 'outputs'
        
        # Subdirectories within datasets
        self.datasets_queries = self.datasets / 'queries'
        self.datasets_tableau = self.datasets_queries / 'tableau'
        self.training_data = self.datasets_tableau / 'training'
        self.testing_data = self.datasets_tableau / 'testing'
        self.training_spacy = self.datasets_tableau / 'training_spacy'
        self.testing_spacy = self.datasets_tableau / 'testing_spacy'
        
        # Model directories
        self.models = self.data_spacy / 'queries' / 'tableau'
        self.custom_rules = self.custom_ner / 'queries' / 'tableau' / 'rules'
        
        # Create outputs directory
        self.outputs.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"PathConfig initialized - Environment: {self.environment}")
    
    def _detect_environment(self) -> str:
        """Detect the current execution environment"""
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
    
    def _find_project_root(self) -> Path:
        """Find project root directory"""
        # Start from this file's location
        current = Path(__file__).resolve().parent.parent.parent
        
        # Check if we're already in the project root
        if (current / 'hypatiax').exists():
            return current
        
        # Search in parent directories
        for _ in range(5):
            if (current / 'hypatiax').exists():
                return current
            current = current.parent
        
        # Fallback: use current working directory
        logger.warning(f"Could not find project root. Using: {Path.cwd()}")
        return Path.cwd()
    
    def get_output_path(self, *parts: str, create_dir: bool = True) -> Path:
        """
        Get path within outputs directory.
        
        Args:
            *parts: Path components (e.g., 'models', 'my_model')
            create_dir: If True, create parent directories
        
        Returns:
            Path object
        
        Example:
            path = paths.get_output_path('models', 'ner_desc', 'model.pkl')
            # Returns: outputs/models/ner_desc/model.pkl
        """
        path = self.outputs.joinpath(*parts)
        
        if create_dir:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        return path
    
    def get_dataset_path(self, 
                        domain: str = 'queries',
                        sub_domain: str = 'tableau',
                        action: str = 'training',
                        filename: Optional[str] = None) -> Path:
        """
        Get dataset path with standard structure.
        
        Args:
            domain: Domain name (e.g., 'queries')
            sub_domain: Sub-domain name (e.g., 'tableau')
            action: Action type ('training', 'testing', 'training_spacy', etc.)
            filename: Optional filename to append
        
        Returns:
            Path to dataset directory or file
        
        Example:
            path = paths.get_dataset_path('queries', 'tableau', 'training', 'formulas_nor.xlsx')
        """
        base_path = self.datasets / domain / sub_domain / action
        
        if filename:
            return base_path / filename
        return base_path
    
    def get_model_path(self,
                      domain: str = 'queries',
                      sub_domain: str = 'tableau',
                      model_name: Optional[str] = None) -> Path:
        """
        Get model path within data_spacy directory.
        
        Args:
            domain: Domain name
            sub_domain: Sub-domain name
            model_name: Optional model directory name
        
        Returns:
            Path to model directory
        """
        base_path = self.data_spacy / domain / sub_domain
        
        if model_name:
            return base_path / model_name
        return base_path
    
    def get_rules_path(self,
                      domain: str = 'queries',
                      sub_domain: str = 'tableau',
                      filename: Optional[str] = None) -> Path:
        """Get path to custom rules files"""
        base_path = self.custom_ner / domain / sub_domain / 'rules'
        
        if filename:
            return base_path / filename
        return base_path
    
    def validate_path(self, path: Union[str, Path]) -> bool:
        """Check if path exists and is accessible"""
        try:
            p = Path(path)
            return p.exists() and os.access(p, os.R_OK)
        except Exception as e:
            logger.error(f"Error validating path {path}: {e}")
            return False
    
    def ensure_directory(self, *parts: str) -> Path:
        """Create directory if it doesn't exist"""
        path = self.root.joinpath(*parts)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def print_paths(self):
        """Print all configured paths"""
        print("=" * 70)
        print("Path Configuration")
        print("=" * 70)
        print(f"Environment:      {self.environment}")
        print(f"Root:             {self.root}")
        print(f"HypatiaX:         {self.hypatiax}")
        print(f"Datasets:         {self.datasets}")
        print(f"Data Spacy:       {self.data_spacy}")
        print(f"Custom NER:       {self.custom_ner}")
        print(f"Outputs:          {self.outputs}")
        print()
        print("Dataset Subdirectories:")
        print(f"  Training:       {self.training_data}")
        print(f"  Testing:        {self.testing_data}")
        print(f"  Training Spacy: {self.training_spacy}")
        print(f"  Testing Spacy:  {self.testing_spacy}")
        print()
        print("Model Directories:")
        print(f"  Models:         {self.models}")
        print(f"  Custom Rules:   {self.custom_rules}")
        print("=" * 70)
    
    def to_dict(self) -> dict:
        """Convert paths to dictionary"""
        return {
            'environment': self.environment,
            'root': str(self.root),
            'hypatiax': str(self.hypatiax),
            'datasets': str(self.datasets),
            'data_spacy': str(self.data_spacy),
            'custom_ner': str(self.custom_ner),
            'outputs': str(self.outputs),
            'training_data': str(self.training_data),
            'testing_data': str(self.testing_data),
            'models': str(self.models),
            'custom_rules': str(self.custom_rules)
        }


# Global paths instance
paths = PathConfig()

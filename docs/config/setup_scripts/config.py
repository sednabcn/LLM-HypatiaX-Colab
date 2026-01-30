"""
Universal configuration for HypatiaX project.
Works in: Local development, GitHub Actions, Docker, Cloud environments.
"""
import os
import sys
from pathlib import Path
from typing import Optional, Dict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PathConfig:
    """
    Universal path configuration for HypatiaX.
    
    Priority for finding project root:
    1. HYPATIAX_ROOT environment variable (explicit override)
    2. Detect from current file location (development)
    3. Detect from installed package location (production)
    4. Current working directory (fallback)
    
    Environment detection:
    - Local development: Uses project structure
    - GitHub Actions: Uses GITHUB_WORKSPACE
    - Docker: Uses /app or custom mount point
    - Cloud: Uses environment variables
    """
    
    def __init__(self, custom_root: Optional[Path] = None):
        """
        Initialize path configuration.
        
        Args:
            custom_root: Optional custom root directory (for testing/override)
        """
        self.environment = self._detect_environment()
        self._root = custom_root or self._find_project_root()
        self._setup_paths()
        self._validate_environment()
        
        logger.info(f"PathConfig initialized: environment={self.environment}, root={self._root}")
    
    @staticmethod
    def _detect_environment() -> str:
        """Detect the current execution environment."""
        if os.getenv('GITHUB_ACTIONS'):
            return 'github'
        elif os.getenv('DOCKER_CONTAINER'):
            return 'docker'
        elif os.getenv('AWS_EXECUTION_ENV'):
            return 'aws'
        elif os.getenv('GOOGLE_CLOUD_PROJECT'):
            return 'gcp'
        elif os.getenv('CI'):
            return 'ci'
        else:
            return 'local'
    
    def _find_project_root(self) -> Path:
        """
        Find the project root directory with multi-environment support.
        
        Returns:
            Path: Absolute path to project root
        """
        # 1. Environment variable (highest priority)
        env_root = os.getenv('HYPATIAX_ROOT')
        if env_root:
            root = Path(env_root).resolve()
            if root.exists():
                logger.info(f"Using HYPATIAX_ROOT from environment: {root}")
                return root
            else:
                logger.warning(f"HYPATIAX_ROOT set but path doesn't exist: {root}")
        
        # 2. GitHub Actions specific
        if self.environment == 'github':
            github_workspace = os.getenv('GITHUB_WORKSPACE')
            if github_workspace:
                root = Path(github_workspace).resolve()
                logger.info(f"Using GITHUB_WORKSPACE: {root}")
                return root
        
        # 3. Docker specific
        if self.environment == 'docker':
            # Common Docker mount points
            for docker_path in ['/app', '/workspace', '/code']:
                path = Path(docker_path)
                if path.exists() and (path / 'hypatiax').exists():
                    logger.info(f"Using Docker path: {path}")
                    return path
        
        # 4. Search upward from current file location (development)
        current = Path(__file__).resolve().parent
        markers = [
            'setup.py',
            'pyproject.toml',
            '.git',
            'hypatiax',  # Main package directory
            'README.md',
            'requirements.txt'
        ]
        
        for _ in range(6):  # Search up to 6 levels
            # Check if this looks like project root
            if any((current / marker).exists() for marker in markers):
                # Extra validation: must have hypatiax directory
                if (current / 'hypatiax').exists():
                    logger.info(f"Found project root by search: {current}")
                    return current
            
            # Move up one level
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent
        
        # 5. Check if we're installed as a package
        try:
            import hypatiax
            package_path = Path(hypatiax.__file__).resolve().parent.parent
            if package_path.exists():
                logger.info(f"Using installed package location: {package_path}")
                return package_path
        except ImportError:
            pass
        
        # 6. Fallback to current working directory
        cwd = Path.cwd()
        logger.warning(f"Using current working directory as fallback: {cwd}")
        return cwd
    
    def _setup_paths(self):
        """Setup all standard paths."""
        self._hypatiax = self._root / 'hypatiax'
        self._datasets = self._hypatiax / 'datasets'
        self._data_spacy = self._hypatiax / 'data_spacy'
        self._tests = self._root / 'tests'
        
        # Output directory - environment specific
        if self.environment in ['github', 'ci']:
            # In CI, use temp directory or workspace
            self._outputs = self._root / 'ci_outputs'
        elif self.environment == 'docker':
            # In Docker, use /tmp or mounted volume
            docker_output = os.getenv('HYPATIAX_OUTPUT_DIR', '/tmp/hypatiax_outputs')
            self._outputs = Path(docker_output)
        else:
            # Local development
            self._outputs = self._root / 'outputs'
        
        # Ensure outputs directory exists
        self._outputs.mkdir(parents=True, exist_ok=True)
    
    def _validate_environment(self):
        """Validate that the environment is properly configured."""
        issues = []
        
        # Check critical directories exist
        if not self._hypatiax.exists():
            issues.append(f"hypatiax package not found at {self._hypatiax}")
        
        if not self._datasets.exists():
            issues.append(f"datasets directory not found at {self._datasets}")
        
        if not self._data_spacy.exists():
            issues.append(f"data_spacy directory not found at {self._data_spacy}")
        
        # In CI/production, missing directories might be okay
        if issues and self.environment == 'local':
            logger.warning("Environment validation issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
            logger.warning("You may need to set HYPATIAX_ROOT environment variable")
    
    # Properties
    @property
    def root(self) -> Path:
        """Project root directory."""
        return self._root
    
    @property
    def hypatiax(self) -> Path:
        """HypatiaX package directory."""
        return self._hypatiax
    
    @property
    def datasets(self) -> Path:
        """Datasets directory."""
        return self._datasets
    
    @property
    def data_spacy(self) -> Path:
        """Spacy data directory."""
        return self._data_spacy
    
    @property
    def outputs(self) -> Path:
        """Output directory (environment-aware)."""
        return self._outputs
    
    @property
    def tests(self) -> Path:
        """Tests directory."""
        return self._tests
    
    # Path builders
    def get_dataset_path(self, *parts: str) -> Path:
        """
        Get path within datasets directory.
        
        Example:
            config.get_dataset_path('queries', 'tableau', 'training')
        """
        path = self.datasets.joinpath(*parts)
        return path
    
    def get_spacy_path(self, *parts: str) -> Path:
        """
        Get path within spacy data directory.
        
        Example:
            config.get_spacy_path('queries', 'tableau', 'ner_tableau_desc')
        """
        path = self.data_spacy.joinpath(*parts)
        return path
    
    def get_output_path(self, *parts: str, create: bool = True) -> Path:
        """
        Get path within outputs directory.
        
        Args:
            *parts: Path components
            create: Whether to create parent directories (default: True)
        
        Example:
            config.get_output_path('training_spacy', 'tableau')
        """
        path = self.outputs.joinpath(*parts)
        if create:
            path.parent.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_test_path(self, *parts: str) -> Path:
        """
        Get path within tests directory.
        
        Example:
            config.get_test_path('data', 'sample.xlsx')
        """
        path = self.tests.joinpath(*parts)
        return path
    
    # Utility methods
    def exists(self, path_type: str) -> bool:
        """
        Check if a standard path exists.
        
        Args:
            path_type: One of 'root', 'hypatiax', 'datasets', 'data_spacy', 'outputs', 'tests'
        """
        path_map = {
            'root': self.root,
            'hypatiax': self.hypatiax,
            'datasets': self.datasets,
            'data_spacy': self.data_spacy,
            'outputs': self.outputs,
            'tests': self.tests
        }
        
        if path_type not in path_map:
            raise ValueError(f"Unknown path_type: {path_type}. Must be one of {list(path_map.keys())}")
        
        return path_map[path_type].exists()
    
    def ensure_output_dirs(self, *subdirs: str) -> Dict[str, Path]:
        """
        Ensure multiple output subdirectories exist.
        
        Args:
            *subdirs: Subdirectory names to create
        
        Returns:
            Dict mapping subdirectory name to Path
        
        Example:
            dirs = config.ensure_output_dirs('training_spacy', 'testing_spacy', 'vocab')
            # dirs = {'training_spacy': Path(...), 'testing_spacy': Path(...), 'vocab': Path(...)}
        """
        result = {}
        for subdir in subdirs:
            path = self.outputs / subdir
            path.mkdir(parents=True, exist_ok=True)
            result[subdir] = path
        return result
    
    def to_dict(self) -> Dict[str, str]:
        """
        Export configuration as dictionary.
        
        Returns:
            Dict with all paths as strings
        """
        return {
            'environment': self.environment,
            'root': str(self.root),
            'hypatiax': str(self.hypatiax),
            'datasets': str(self.datasets),
            'data_spacy': str(self.data_spacy),
            'outputs': str(self.outputs),
            'tests': str(self.tests)
        }
    
    def print_config(self):
        """Print complete configuration for debugging."""
        print("=" * 70)
        print("HypatiaX Path Configuration")
        print("=" * 70)
        print(f"Environment:      {self.environment}")
        print(f"Project Root:     {self.root}")
        print(f"HypatiaX Package: {self.hypatiax}")
        print(f"Datasets:         {self.datasets}")
        print(f"Spacy Data:       {self.data_spacy}")
        print(f"Outputs:          {self.outputs}")
        print(f"Tests:            {self.tests}")
        print("=" * 70)
        
        # Validation status
        print("\nPath Status:")
        status_map = {
            'root': self.root,
            'hypatiax': self.hypatiax,
            'datasets': self.datasets,
            'data_spacy': self.data_spacy,
            'outputs': self.outputs,
            'tests': self.tests
        }
        
        for name, path in status_map.items():
            status = "✅ EXISTS" if path.exists() else "❌ MISSING"
            print(f"  {status:12} {name:15} {path}")
        
        # Environment variables
        print("\nEnvironment Variables:")
        env_vars = [
            'HYPATIAX_ROOT',
            'GITHUB_WORKSPACE',
            'GITHUB_ACTIONS',
            'CI',
            'DOCKER_CONTAINER'
        ]
        for var in env_vars:
            value = os.getenv(var)
            if value:
                print(f"  {var:20} = {value}")
        
        print("=" * 70)
    
    def __repr__(self) -> str:
        return f"PathConfig(environment={self.environment}, root={self._root})"


# Global configuration instance
# This will be initialized once when the module is imported
try:
    config = PathConfig()
except Exception as e:
    logger.error(f"Failed to initialize default config: {e}")
    # Fallback to minimal config
    config = None


def get_config(custom_root: Optional[Path] = None) -> PathConfig:
    """
    Get or create path configuration instance.
    
    Args:
        custom_root: Optional custom root directory for testing
        
    Returns:
        PathConfig instance
    """
    if custom_root:
        return PathConfig(custom_root)
    
    if config is None:
        return PathConfig()
    
    return config


# Convenience function for quick debugging
def show_config():
    """Print current configuration (for debugging)."""
    if config:
        config.print_config()
    else:
        print("⚠️  Configuration not initialized")


if __name__ == "__main__":
    # When run directly, print configuration
    show_config()

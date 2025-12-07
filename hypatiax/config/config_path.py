"""
Universal configuration for HypatiaX project.
Works in: Local development, GitHub Actions, Docker, Cloud environments.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class PathConfig:
    """
    Universal path configuration for HypatiaX.

    Priority for finding project root:
    1. HYPATIAX_ROOT environment variable (explicit override)
    2. GITHUB_WORKSPACE (GitHub Actions)
    3. Docker standard paths (/app, /workspace, /code)
    4. Detect from current file location (development)
    5. Detect from installed package location (production)
    6. Current working directory (fallback)

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
        if os.getenv("GITHUB_ACTIONS"):
            return "github"
        elif os.getenv("DOCKER_CONTAINER"):
            return "docker"
        elif os.getenv("AWS_EXECUTION_ENV") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
            return "aws"
        elif os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("K_SERVICE"):
            return "gcp"
        elif os.getenv("AZURE_FUNCTIONS_ENVIRONMENT"):
            return "azure"
        elif os.getenv("CI"):
            return "ci"
        else:
            return "local"

    def _find_project_root(self) -> Path:
        """
        Find the project root directory with multi-environment support.

        Returns:
            Path: Absolute path to project root
        """
        # 1. Environment variable (highest priority)
        env_root = os.getenv("HYPATIAX_ROOT")
        if env_root:
            root = Path(env_root).resolve()
            if root.exists():
                logger.info(f"Using HYPATIAX_ROOT from environment: {root}")
                return root
            else:
                logger.warning(f"HYPATIAX_ROOT set but path doesn't exist: {root}")

        # 2. GitHub Actions specific
        if self.environment == "github":
            github_workspace = os.getenv("GITHUB_WORKSPACE")
            if github_workspace:
                root = Path(github_workspace).resolve()
                logger.info(f"Using GITHUB_WORKSPACE: {root}")
                return root

        # 3. Docker specific - check common mount points
        if self.environment == "docker":
            docker_paths = [Path("/app"), Path("/workspace"), Path("/code"), Path("/opt/hypatiax")]
            for docker_path in docker_paths:
                if docker_path.exists() and (docker_path / "hypatiax").exists():
                    logger.info(f"Using Docker path: {docker_path}")
                    return docker_path

        # 4. Cloud-specific paths
        if self.environment in ["aws", "gcp", "azure"]:
            cloud_paths = [
                Path("/var/task"),  # AWS Lambda
                Path("/workspace"),  # Common cloud path
                Path("/app"),  # Common cloud path
            ]
            for cloud_path in cloud_paths:
                if cloud_path.exists() and (cloud_path / "hypatiax").exists():
                    logger.info(f"Using cloud path: {cloud_path}")
                    return cloud_path

        # 5. Search upward from current file location (development)
        current = Path(__file__).resolve().parent
        markers = ["setup.py", "pyproject.toml", ".git", "hypatiax", "README.md", "requirements.txt", "requirements"]

        for _ in range(8):  # Search up to 8 levels
            # Check if this looks like project root
            marker_count = sum(1 for marker in markers if (current / marker).exists())

            # If we find 2+ markers and hypatiax directory, this is likely the root
            if marker_count >= 2 and (current / "hypatiax").exists():
                logger.info(f"Found project root by search: {current}")
                return current

            # Move up one level
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent

        # 6. Check if we're installed as a package
        try:
            import hypatiax

            package_path = Path(hypatiax.__file__).resolve().parent.parent
            if package_path.exists():
                logger.info(f"Using installed package location: {package_path}")
                return package_path
        except ImportError:
            pass

        # 7. Fallback to current working directory
        cwd = Path.cwd()
        logger.warning(f"Using current working directory as fallback: {cwd}")
        return cwd

    def _setup_paths(self):
        """Setup all standard paths based on project structure."""
        # Core directories
        self._hypatiax = self._root / "hypatiax"

        # Data directories
        self._datasets = self._hypatiax / "datasets"
        self._data_spacy = self._hypatiax / "data_spacy"

        # Code organization directories
        self._agents = self._hypatiax / "agents"
        self._core = self._hypatiax / "core"
        self._models = self._hypatiax / "models"
        self._tools = self._hypatiax / "tools"
        self._utils = self._hypatiax / "utils"
        self._custom_entities = self._hypatiax / "custom_entities"
        self._custom_ner = self._hypatiax / "custom_ner"

        # Configuration and patterns
        self._config = self._hypatiax / "config"
        self._patterns = self._hypatiax / "patterns"
        self._mappings = self._hypatiax / "mappings"

        # Testing and examples
        self._tests = self._root / "tests"
        self._examples = self._hypatiax / "examples"
        self._experiments = self._hypatiax / "experiments"

        # Documentation
        self._docs = self._hypatiax / "docs"
        self._demo = self._hypatiax / "demo"

        # Output directory - environment specific
        if self.environment in ["github", "ci"]:
            self._outputs = self._root / "ci_outputs"
        elif self.environment == "docker":
            docker_output = os.getenv("HYPATIAX_OUTPUT_DIR", "/tmp/hypatiax_outputs")
            self._outputs = Path(docker_output)
        elif self.environment in ["aws", "gcp", "azure"]:
            cloud_output = os.getenv("HYPATIAX_OUTPUT_DIR", "/tmp/hypatiax_outputs")
            self._outputs = Path(cloud_output)
        else:
            self._outputs = self._root / "outputs"

        # Ensure outputs directory exists
        try:
            self._outputs.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            logger.warning(f"Could not create outputs directory {self._outputs}: {e}")
            # Fallback to temp directory
            import tempfile

            self._outputs = Path(tempfile.gettempdir()) / "hypatiax_outputs"
            self._outputs.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using fallback outputs directory: {self._outputs}")

    def _validate_environment(self):
        """Validate that the environment is properly configured."""
        issues = []
        warnings = []

        # Critical directories that must exist
        critical_dirs = {
            "hypatiax": self._hypatiax,
        }

        # Important directories that should exist
        important_dirs = {
            "datasets": self._datasets,
            "data_spacy": self._data_spacy,
            "core": self._core,
            "models": self._models,
            "tools": self._tools,
        }

        # Check critical directories
        for name, path in critical_dirs.items():
            if not path.exists():
                issues.append(f"{name} directory not found at {path}")

        # Check important directories
        for name, path in important_dirs.items():
            if not path.exists():
                warnings.append(f"{name} directory not found at {path}")

        # Report issues
        if issues:
            logger.error("Critical environment validation issues:")
            for issue in issues:
                logger.error(f"  - {issue}")
            if self.environment == "local":
                logger.error("You may need to set HYPATIAX_ROOT environment variable")

        if warnings and self.environment == "local":
            logger.warning("Environment validation warnings:")
            for warning in warnings:
                logger.warning(f"  - {warning}")

    # Properties for core paths
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

    # Properties for code organization
    @property
    def agents(self) -> Path:
        """Agents directory."""
        return self._agents

    @property
    def core(self) -> Path:
        """Core directory."""
        return self._core

    @property
    def models(self) -> Path:
        """Models directory."""
        return self._models

    @property
    def tools(self) -> Path:
        """Tools directory."""
        return self._tools

    @property
    def utils(self) -> Path:
        """Utils directory."""
        return self._utils

    @property
    def custom_entities(self) -> Path:
        """Custom entities directory."""
        return self._custom_entities

    @property
    def custom_ner(self) -> Path:
        """Custom NER directory."""
        return self._custom_ner

    @property
    def config_dir(self) -> Path:
        """Config directory."""
        return self._config

    @property
    def patterns(self) -> Path:
        """Patterns directory."""
        return self._patterns

    @property
    def mappings(self) -> Path:
        """Mappings directory."""
        return self._mappings

    @property
    def examples(self) -> Path:
        """Examples directory."""
        return self._examples

    @property
    def experiments(self) -> Path:
        """Experiments directory."""
        return self._experiments

    @property
    def docs(self) -> Path:
        """Documentation directory."""
        return self._docs

    @property
    def demo(self) -> Path:
        """Demo directory."""
        return self._demo

    # Path builder methods
    def get_dataset_path(self, *parts: str) -> Path:
        """Get path within datasets directory."""
        return self.datasets.joinpath(*parts)

    def get_spacy_path(self, *parts: str) -> Path:
        """Get path within spacy data directory."""
        return self.data_spacy.joinpath(*parts)

    def get_output_path(self, *parts: str, create: bool = True) -> Path:
        """
        Get path within outputs directory.

        Args:
            *parts: Path components
            create: Whether to create parent directories (default: True)
        """
        path = self.outputs.joinpath(*parts)
        if create:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                logger.warning(f"Could not create directory {path.parent}: {e}")
        return path

    def get_test_path(self, *parts: str) -> Path:
        """Get path within tests directory."""
        return self.tests.joinpath(*parts)

    def get_agent_path(self, *parts: str) -> Path:
        """Get path within agents directory."""
        return self.agents.joinpath(*parts)

    def get_model_path(self, *parts: str) -> Path:
        """Get path within models directory."""
        return self.models.joinpath(*parts)

    def get_tool_path(self, *parts: str) -> Path:
        """Get path within tools directory."""
        return self.tools.joinpath(*parts)

    # Utility methods
    def exists(self, path_type: str) -> bool:
        """Check if a standard path exists."""
        path_map = {
            "root": self.root,
            "hypatiax": self.hypatiax,
            "datasets": self.datasets,
            "data_spacy": self.data_spacy,
            "outputs": self.outputs,
            "tests": self.tests,
            "agents": self.agents,
            "core": self.core,
            "models": self.models,
            "tools": self.tools,
            "utils": self.utils,
        }

        if path_type not in path_map:
            raise ValueError(f"Unknown path_type: {path_type}. Must be one of {list(path_map.keys())}")

        return path_map[path_type].exists()

    def ensure_output_dirs(self, *subdirs: str) -> Dict[str, Path]:
        """
        Ensure multiple output subdirectories exist.

        Returns:
            Dict mapping subdirectory name to Path
        """
        result = {}
        for subdir in subdirs:
            path = self.outputs / subdir
            try:
                path.mkdir(parents=True, exist_ok=True)
                result[subdir] = path
            except (PermissionError, OSError) as e:
                logger.warning(f"Could not create output directory {path}: {e}")
                result[subdir] = path
        return result

    def list_available_paths(self) -> List[str]:
        """List all available path properties."""
        return [
            "root",
            "hypatiax",
            "datasets",
            "data_spacy",
            "outputs",
            "tests",
            "agents",
            "core",
            "models",
            "tools",
            "utils",
            "custom_entities",
            "custom_ner",
            "config_dir",
            "patterns",
            "mappings",
            "examples",
            "experiments",
            "docs",
            "demo",
        ]

    def to_dict(self) -> Dict[str, str]:
        """Export configuration as dictionary."""
        return {
            "environment": self.environment,
            "root": str(self.root),
            "hypatiax": str(self.hypatiax),
            "datasets": str(self.datasets),
            "data_spacy": str(self.data_spacy),
            "outputs": str(self.outputs),
            "tests": str(self.tests),
            "agents": str(self.agents),
            "core": str(self.core),
            "models": str(self.models),
            "tools": str(self.tools),
        }

    def print_config_path(self):
        """Print complete configuration for debugging."""
        print("=" * 80)
        print("HypatiaX Path Configuration")
        print("=" * 80)
        print(f"Environment:      {self.environment}")
        print(f"Project Root:     {self.root}")
        print(f"HypatiaX Package: {self.hypatiax}")
        print("-" * 80)
        print("Data Directories:")
        print(f"  Datasets:       {self.datasets}")
        print(f"  Spacy Data:     {self.data_spacy}")
        print(f"  Outputs:        {self.outputs}")
        print("-" * 80)
        print("Code Directories:")
        print(f"  Agents:         {self.agents}")
        print(f"  Core:           {self.core}")
        print(f"  Models:         {self.models}")
        print(f"  Tools:          {self.tools}")
        print(f"  Utils:          {self.utils}")
        print("-" * 80)
        print("Other Directories:")
        print(f"  Tests:          {self.tests}")
        print(f"  Examples:       {self.examples}")
        print(f"  Docs:           {self.docs}")
        print("=" * 80)

        # Validation status
        print("\nPath Status:")
        status_map = {
            "root": self.root,
            "hypatiax": self.hypatiax,
            "datasets": self.datasets,
            "data_spacy": self.data_spacy,
            "outputs": self.outputs,
            "agents": self.agents,
            "core": self.core,
            "models": self.models,
            "tools": self.tools,
        }

        for name, path in status_map.items():
            status = "✅ EXISTS" if path.exists() else "❌ MISSING"
            print(f"  {status:12} {name:15} {path}")

        # Environment variables
        print("\nRelevant Environment Variables:")
        env_vars = [
            "HYPATIAX_ROOT",
            "HYPATIAX_OUTPUT_DIR",
            "GITHUB_WORKSPACE",
            "GITHUB_ACTIONS",
            "CI",
            "DOCKER_CONTAINER",
            "AWS_EXECUTION_ENV",
            "GOOGLE_CLOUD_PROJECT",
        ]
        has_vars = False
        for var in env_vars:
            value = os.getenv(var)
            if value:
                print(f"  {var:25} = {value}")
                has_vars = True

        if not has_vars:
            print("  (none set)")

        print("=" * 80)

    def __repr__(self) -> str:
        return f"PathConfig(environment={self.environment}, root={self._root})"


# Global configuration instance
try:
    config_path = PathConfig()
except Exception as e:
    logger.error(f"Failed to initialize default config: {e}")
    config_path = None


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

    if config_path is None:
        return PathConfig()

    return config_path


def show_config_path():
    """Print current configuration (for debugging)."""
    if config_path:
        config_path.print_config_path()
    else:
        print("⚠️  Configuration not initialized")
        print("Try: from hypatiax.config import PathConfig; PathConfig().print_config()")


if __name__ == "__main__":
    show_config_path()

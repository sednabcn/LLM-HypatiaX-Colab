"""
HypatiaX Secrets Configuration - Complements PathConfig

Add this to your existing config.py file, or save as secrets_config.py
Works alongside the existing PathConfig class for managing API keys and secrets.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class SecretsConfig:
    """
    Manage API keys and secrets for HypatiaX.
    
    Integrates with existing PathConfig and works in:
    - Local development (reads from .env file)
    - GitHub Actions (reads from secrets via environment variables)
    - Docker (reads from environment variables)
    - Cloud deployments (GCP, AWS, Azure)
    
    Usage:
        from hypatiax.config import config, secrets
        
        # Use paths from PathConfig
        data_path = config.datasets / "training_data.json"
        
        # Use secrets from SecretsConfig
        client = OpenAI(api_key=secrets.openai_api_key)
    """
    
    def __init__(self, env_file: Optional[str] = ".env", path_config: Optional[Any] = None):
        """
        Initialize secrets configuration.
        
        Args:
            env_file: Path to .env file (relative to project root)
            path_config: Optional PathConfig instance for resolving paths
        """
        self.path_config = path_config
        self.environment = self._detect_environment()
        self._source = "not_loaded"
        
        # Load environment variables
        self._load_env_file(env_file)
        self._load_secrets()
        
        logger.info(f"SecretsConfig initialized: environment={self.environment}, source={self._source}")
    
    def _detect_environment(self) -> str:
        """Detect execution environment (sync with PathConfig)."""
        if os.getenv('GITHUB_ACTIONS'):
            return 'github'
        elif os.getenv('DOCKER_CONTAINER'):
            return 'docker'
        elif os.getenv('AWS_EXECUTION_ENV') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
            return 'aws'
        elif os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('K_SERVICE'):
            return 'gcp'
        elif os.getenv('AZURE_FUNCTIONS_ENVIRONMENT'):
            return 'azure'
        elif os.getenv('CI'):
            return 'ci'
        else:
            return 'local'
    
    def _load_env_file(self, env_file: str):
        """Load .env file if it exists."""
        # Try to find .env file
        env_paths = []
        
        # 1. If we have PathConfig, use project root
        if self.path_config:
            env_paths.append(self.path_config.root / env_file)
        
        # 2. Current working directory
        env_paths.append(Path.cwd() / env_file)
        
        # 3. Script directory
        env_paths.append(Path(__file__).parent / env_file)
        
        # 4. Parent directories (search upward)
        current = Path.cwd()
        for _ in range(5):
            env_paths.append(current / env_file)
            current = current.parent
        
        # Try each path
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                self._source = f"local {env_path}"
                logger.info(f"Loaded environment from {env_path}")
                return
        
        # No .env file found - will use environment variables
        self._source = "environment variables"
        if self.environment == 'local':
            logger.warning(
                f"No .env file found. Searched locations:\n" + 
                "\n".join(f"  - {p}" for p in env_paths[:3])
            )
    
    def _load_secrets(self):
        """Load all secrets from environment variables."""
        
        # ============================================================
        # LLM API Keys
        # ============================================================
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_org_id = os.getenv('OPENAI_ORG_ID')
        
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cloud_project = os.getenv('GOOGLE_CLOUD_PROJECT')
        
        self.huggingface_token = os.getenv('HUGGINGFACE_TOKEN')
        self.huggingface_hub_token = os.getenv('HF_TOKEN')  # Alternative name
        
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        
        self.azure_openai_key = os.getenv('AZURE_OPENAI_KEY')
        self.azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        
        # ============================================================
        # Cloud Provider Credentials
        # ============================================================
        self.gcp_project_id = os.getenv('GCP_PROJECT_ID')
        self.gcp_location = os.getenv('GCP_LOCATION', 'us-central1')
        self.gcp_service_account_key = os.getenv('GCP_SERVICE_ACCOUNT_KEY')
        
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        self.azure_subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        self.azure_tenant_id = os.getenv('AZURE_TENANT_ID')
        
        # ============================================================
        # Storage
        # ============================================================
        self.gcs_bucket = os.getenv('GCS_BUCKET')
        self.s3_bucket = os.getenv('S3_BUCKET')
        self.azure_storage_account = os.getenv('AZURE_STORAGE_ACCOUNT')
        self.azure_storage_key = os.getenv('AZURE_STORAGE_KEY')
        
        # ============================================================
        # Database
        # ============================================================
        self.db_connection_string = os.getenv('DB_CONNECTION_STRING')
        self.postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
        self.postgres_port = os.getenv('POSTGRES_PORT', '5432')
        self.postgres_db = os.getenv('POSTGRES_DB')
        self.postgres_user = os.getenv('POSTGRES_USER')
        self.postgres_password = os.getenv('POSTGRES_PASSWORD')
        
        self.mongodb_uri = os.getenv('MONGODB_URI')
        self.redis_url = os.getenv('REDIS_URL')
        
        # ============================================================
        # GitHub
        # ============================================================
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repository = os.getenv('GITHUB_REPOSITORY')
        
        # ============================================================
        # Weights & Biases (W&B)
        # ============================================================
        self.wandb_api_key = os.getenv('WANDB_API_KEY')
        self.wandb_project = os.getenv('WANDB_PROJECT', 'hypatiax')
        self.wandb_entity = os.getenv('WANDB_ENTITY')
        
        # ============================================================
        # MLflow
        # ============================================================
        self.mlflow_tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
        self.mlflow_experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME', 'hypatiax')
        
        # ============================================================
        # Application Settings
        # ============================================================
        self.environment_name = os.getenv('ENVIRONMENT', 'development')
        self.debug = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # HypatiaX specific
        self.hypatiax_api_key = os.getenv('HYPATIAX_API_KEY')
        self.hypatiax_model_version = os.getenv('HYPATIAX_MODEL_VERSION', 'latest')
    
    def validate(self, required_keys: List[str], raise_error: bool = True) -> Dict[str, bool]:
        """
        Validate that required secrets are present.
        
        Args:
            required_keys: List of attribute names that must be set
            raise_error: Whether to raise ValueError on missing keys (default: True)
            
        Returns:
            Dict mapping key names to whether they exist
            
        Raises:
            ValueError: If any required keys are missing and raise_error=True
            
        Example:
            secrets.validate(['openai_api_key', 'gcp_project_id'])
        """
        missing = []
        status = {}
        
        for key in required_keys:
            value = getattr(self, key, None)
            exists = bool(value)
            status[key] = exists
            
            if not exists:
                missing.append(key)
        
        if missing and raise_error:
            error_msg = (
                f"Missing required secrets: {', '.join(missing)}\n"
                f"Loaded from: {self._source}\n"
                f"Environment: {self.environment}\n"
                f"\n"
                f"To fix:\n"
            )
            
            if self.environment == 'local':
                error_msg += f"  - Create .env file in project root with:\n"
                for key in missing:
                    error_msg += f"      {key.upper()}=your-key-here\n"
            elif self.environment == 'github':
                error_msg += f"  - Add secrets to GitHub repository:\n"
                error_msg += f"      Settings → Secrets and variables → Actions\n"
                for key in missing:
                    error_msg += f"      Add: {key.upper()}\n"
            else:
                error_msg += f"  - Set environment variables:\n"
                for key in missing:
                    error_msg += f"      export {key.upper()}=your-key-here\n"
            
            raise ValueError(error_msg)
        
        return status
    
    def get_llm_client(self, provider: str = 'openai', **kwargs):
        """
        Get LLM client for specified provider.
        
        Args:
            provider: One of 'openai', 'anthropic', 'google', 'cohere', 'azure'
            **kwargs: Additional arguments passed to client constructor
            
        Returns:
            Configured client instance
            
        Example:
            client = secrets.get_llm_client('openai')
            response = client.chat.completions.create(...)
        """
        if provider == 'openai':
            if not self.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY not configured. "
                    "Set it in .env file or environment variables."
                )
            from openai import OpenAI
            return OpenAI(
                api_key=self.openai_api_key,
                organization=self.openai_org_id,
                **kwargs
            )
        
        elif provider == 'anthropic':
            if not self.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            from anthropic import Anthropic
            return Anthropic(api_key=self.anthropic_api_key, **kwargs)
        
        elif provider == 'google':
            if not self.google_api_key:
                raise ValueError("GOOGLE_API_KEY not configured")
            import google.generativeai as genai
            genai.configure(api_key=self.google_api_key)
            return genai
        
        elif provider == 'cohere':
            if not self.cohere_api_key:
                raise ValueError("COHERE_API_KEY not configured")
            import cohere
            return cohere.Client(api_key=self.cohere_api_key, **kwargs)
        
        elif provider == 'azure':
            if not self.azure_openai_key or not self.azure_openai_endpoint:
                raise ValueError("AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT not configured")
            from openai import AzureOpenAI
            return AzureOpenAI(
                api_key=self.azure_openai_key,
                azure_endpoint=self.azure_openai_endpoint,
                api_version=kwargs.get('api_version', '2024-02-15-preview'),
                **kwargs
            )
        
        else:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Must be one of: openai, anthropic, google, cohere, azure"
            )
    
    def get_masked_key(self, key_name: str) -> str:
        """
        Get masked version of API key for safe logging.
        
        Args:
            key_name: Name of the key attribute
            
        Returns:
            Masked key string (e.g., "sk-proj-...x7Qz")
            
        Example:
            logger.info(f"Using key: {secrets.get_masked_key('openai_api_key')}")
            # Output: Using key: sk-proj-...x7Qz
        """
        key = getattr(self, key_name, None)
        if not key:
            return "NOT_SET"
        if len(key) < 12:
            return "***"
        return f"{key[:8]}...{key[-4:]}"
    
    @property
    def is_github_actions(self) -> bool:
        """Check if running in GitHub Actions."""
        return self.environment == 'github'
    
    @property
    def is_local(self) -> bool:
        """Check if running in local development."""
        return self.environment == 'local'
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment_name == 'production'
    
    @property
    def is_cloud(self) -> bool:
        """Check if running in cloud environment."""
        return self.environment in ['aws', 'gcp', 'azure']
    
    def to_dict(self, mask_secrets: bool = True) -> Dict[str, Any]:
        """
        Export configuration as dictionary.
        
        Args:
            mask_secrets: Whether to mask secret values (default: True)
        """
        config_dict = {
            'environment': self.environment,
            'source': self._source,
            'environment_name': self.environment_name,
            'debug': self.debug,
        }
        
        # Add API key status
        api_keys = [
            'openai_api_key', 'anthropic_api_key', 'google_api_key',
            'huggingface_token', 'cohere_api_key', 'azure_openai_key'
        ]
        
        for key in api_keys:
            if mask_secrets:
                config_dict[key] = self.get_masked_key(key)
            else:
                config_dict[key] = getattr(self, key, None)
        
        return config_dict
    
    def print_status(self):
        """Print configuration status (safe for logging)."""
        print("=" * 70)
        print("HypatiaX Secrets Configuration")
        print("=" * 70)
        print(f"Environment:      {self.environment}")
        print(f"Source:           {self._source}")
        print(f"Environment Name: {self.environment_name}")
        print(f"Debug Mode:       {self.debug}")
        print()
        
        print("LLM API Keys Status:")
        print(f"  OpenAI:         {self.get_masked_key('openai_api_key')}")
        print(f"  Anthropic:      {self.get_masked_key('anthropic_api_key')}")
        print(f"  Google:         {self.get_masked_key('google_api_key')}")
        print(f"  HuggingFace:    {self.get_masked_key('huggingface_token')}")
        print(f"  Cohere:         {self.get_masked_key('cohere_api_key')}")
        print(f"  Azure OpenAI:   {self.get_masked_key('azure_openai_key')}")
        print()
        
        print("Cloud Configuration:")
        print(f"  GCP Project:    {self.gcp_project_id or 'NOT_SET'}")
        print(f"  GCS Bucket:     {self.gcs_bucket or 'NOT_SET'}")
        print(f"  AWS Region:     {self.aws_region}")
        print(f"  S3 Bucket:      {self.s3_bucket or 'NOT_SET'}")
        print()
        
        print("Experiment Tracking:")
        print(f"  W&B API Key:    {self.get_masked_key('wandb_api_key')}")
        print(f"  W&B Project:    {self.wandb_project}")
        print(f"  MLflow URI:     {self.mlflow_tracking_uri or 'NOT_SET'}")
        print("=" * 70)
    
    def __repr__(self) -> str:
        return (
            f"SecretsConfig("
            f"environment={self.environment}, "
            f"source={self._source})"
        )


# ============================================================
# Integration with existing PathConfig
# ============================================================

def initialize_configs(custom_root: Optional[Path] = None):
    """
    Initialize both PathConfig and SecretsConfig together.
    
    Args:
        custom_root: Optional custom root for PathConfig
        
    Returns:
        Tuple of (PathConfig, SecretsConfig)
    """
    # Import PathConfig from the same module
    from hypatiax.config import PathConfig, config as path_config
    
    # Use existing path_config or create new one
    if custom_root:
        path_cfg = PathConfig(custom_root)
    else:
        path_cfg = path_config if path_config else PathConfig()
    
    # Create secrets config with path config reference
    secrets_cfg = SecretsConfig(path_config=path_cfg)
    
    return path_cfg, secrets_cfg


# Global secrets instance
try:
    # Try to import existing PathConfig
    from hypatiax.config import config as path_config
    secrets = SecretsConfig(path_config=path_config)
except (ImportError, Exception) as e:
    logger.warning(f"Could not integrate with PathConfig: {e}")
    secrets = SecretsConfig()


# ============================================================
# Convenience Functions
# ============================================================

def get_secrets(custom_root: Optional[Path] = None) -> SecretsConfig:
    """
    Get or create secrets configuration instance.
    
    Args:
        custom_root: Optional custom root directory
        
    Returns:
        SecretsConfig instance
    """
    if custom_root:
        from hypatiax.config import PathConfig
        path_cfg = PathConfig(custom_root)
        return SecretsConfig(path_config=path_cfg)
    
    return secrets


def show_secrets():
    """Print current secrets configuration (for debugging)."""
    if secrets:
        secrets.print_status()
    else:
        print("⚠️  Secrets configuration not initialized")


# ============================================================
# Usage Examples
# ============================================================

def example_basic_usage():
    """Example 1: Basic usage with existing PathConfig"""
    from hypatiax.config import config, secrets
    
    # Use paths from PathConfig
    training_data = config.datasets / "training_data.json"
    print(f"Loading data from: {training_data}")
    
    # Use secrets from SecretsConfig
    secrets.validate(['openai_api_key'])
    client = secrets.get_llm_client('openai')
    
    print("✅ Configuration ready!")


def example_standalone():
    """Example 2: Using SecretsConfig standalone"""
    secrets_cfg = SecretsConfig()
    
    # Validate required keys
    try:
        secrets_cfg.validate(['openai_api_key', 'anthropic_api_key'])
        print("✅ All required secrets present")
    except ValueError as e:
        print(f"❌ Missing secrets:\n{e}")


def example_github_actions():
    """Example 3: Usage in GitHub Actions"""
    from hypatiax.config import config, secrets
    
    if secrets.is_github_actions:
        print("Running in GitHub Actions")
        # Secrets are loaded from GitHub Secrets automatically
    else:
        print("Running locally")
        # Secrets are loaded from .env file
    
    # Same code works in both environments!
    client = secrets.get_llm_client('openai')


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("HypatiaX Secrets Configuration Test")
    print("=" * 70 + "\n")
    
    show_secrets()
    
    print("\n" + "=" * 70)
    print("Integration Test")
    print("=" * 70 + "\n")
    
    try:
        from hypatiax.config import config
        print("✅ PathConfig loaded successfully")
        print(f"   Project root: {config.root}")
    except Exception as e:
        print(f"⚠️  Could not load PathConfig: {e}")
    
    print("\n✅ SecretsConfig ready for use!")

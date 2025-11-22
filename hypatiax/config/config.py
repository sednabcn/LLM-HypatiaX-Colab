"""
HypatiaX Secrets Configuration - Complements PathConfig

UPDATED: Now searches for .env in both project root AND hypatiax/ directory
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
    
    UPDATED: Searches for .env files in multiple locations:
    1. Project root (.env)
    2. hypatiax/ directory (hypatiax/.env)  # NEW!
    3. Current working directory
    4. Script directory
    5. Parent directories
    """
    
    def __init__(self, env_file: Optional[str] = ".env", path_config: Optional[Any] = None):
        """
        Initialize secrets configuration.
        
        Args:
            env_file: Name of .env file (default: ".env")
            path_config: Optional PathConfig instance for resolving paths
        """
        self.path_config = path_config
        self.environment = self._detect_environment()
        self._source = "not_loaded"
        self._loaded_files = []
        
        # Load environment variables from multiple locations
        self._load_env_files(env_file)
        self._load_secrets()
        
        logger.info(f"SecretsConfig initialized: environment={self.environment}, loaded={len(self._loaded_files)} file(s)")
    
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
    
    def _load_env_files(self, env_file: str):
        """
        Load .env files from multiple locations.
        
        NEW: Now loads from BOTH root and hypatiax/ directories!
        This allows you to keep:
        - Project config in root .env (HYPATIAX_ROOT, etc.)
        - API keys in hypatiax/.env (OPENAI_API_KEY, etc.)
        """
        env_paths = []
        
        # 1. If we have PathConfig, use project root AND hypatiax directory
        if self.path_config:
            env_paths.append(self.path_config.root / env_file)
            env_paths.append(self.path_config.hypatiax / env_file)  # NEW!
        
        # 2. Current working directory
        env_paths.append(Path.cwd() / env_file)
        
        # 3. Script directory
        env_paths.append(Path(__file__).parent / env_file)
        
        # 4. Parent directories (search upward)
        current = Path.cwd()
        for _ in range(5):
            env_paths.append(current / env_file)
            current = current.parent
        
        # Try each path and load ALL that exist
        loaded_count = 0
        for env_path in env_paths:
            if env_path.exists() and env_path not in self._loaded_files:
                try:
                    load_dotenv(env_path, override=False)  # Don't override existing vars
                    self._loaded_files.append(env_path)
                    loaded_count += 1
                    logger.info(f"Loaded environment from {env_path}")
                except Exception as e:
                    logger.warning(f"Failed to load {env_path}: {e}")
        
        # Set source information
        if loaded_count == 0:
            self._source = "environment variables only"
            if self.environment == 'local':
                logger.warning(
                    f"No .env file found. Searched locations:\n" + 
                    "\n".join(f"  - {p}" for p in env_paths[:5])
                )
        elif loaded_count == 1:
            self._source = f"local {self._loaded_files[0]}"
        else:
            self._source = f"local {loaded_count} files: " + ", ".join(str(f) for f in self._loaded_files)
    
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
        
        self.huggingface_token = os.getenv('HUGGINGFACE_API_KEY')
        self.huggingface_hub_token = os.getenv('HF_TOKEN')
        
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
                error_msg += f"  - Add to .env file in project root or hypatiax/ directory:\n"
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
        """Get LLM client for specified provider."""
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
        """Get masked version of API key for safe logging."""
        key = getattr(self, key_name, None)
        if not key:
            return "NOT_SET"
        if len(key) < 12:
            return "***"
        return f"{key[:8]}...{key[-4:]}"
    
    @property
    def is_github_actions(self) -> bool:
        return self.environment == 'github'
    
    @property
    def is_local(self) -> bool:
        return self.environment == 'local'
    
    @property
    def is_production(self) -> bool:
        return self.environment_name == 'production'
    
    @property
    def is_cloud(self) -> bool:
        return self.environment in ['aws', 'gcp', 'azure']
    
    def to_dict(self, mask_secrets: bool = True) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        config_dict = {
            'environment': self.environment,
            'source': self._source,
            'loaded_files': [str(f) for f in self._loaded_files],
            'environment_name': self.environment_name,
            'debug': self.debug,
        }
        
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
        if self._loaded_files:
            print(f"Loaded files:")
            for f in self._loaded_files:
                print(f"  - {f}")
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
            f"loaded={len(self._loaded_files)} file(s))"
        )


def create_secrets(custom_root: Optional[Path] = None, path_config=None) -> SecretsConfig:
    """Create a new SecretsConfig instance."""
    if path_config is None and custom_root:
        try:
            from hypatiax.config.config_path import PathConfig
            path_config = PathConfig(custom_root)
        except ImportError:
            logger.warning("Could not import PathConfig")
    
    return SecretsConfig(path_config=path_config)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("HypatiaX Secrets Configuration Test")
    print("=" * 70 + "\n")
    
    print("Creating SecretsConfig instance...")
    secrets_test = create_secrets()
    secrets_test.print_status()

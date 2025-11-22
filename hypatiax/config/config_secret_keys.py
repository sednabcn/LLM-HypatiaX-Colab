"""
HypatiaX Unified Configuration Class

This single class handles secrets/config for:
- Local development (reads from .env file)
- GitHub Actions (reads from environment variables/secrets)
- Cloud deployments (GCP, AWS, Azure)

Usage:
    from hypatia_x.config import config
    
    # Automatic - works everywhere!
    client = OpenAI(api_key=config.openai_api_key)
"""

import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv


class HypatiaConfig:
    """
    Unified configuration that works everywhere:
    - Locally with .env files
    - In GitHub Actions with secrets
    - In cloud environments with secret managers
    
    Example:
        # Create config instance
        config = HypatiaConfig()
        
        # Validate required keys
        config.validate(['openai_api_key'])
        
        # Use the secrets
        from openai import OpenAI
        client = OpenAI(api_key=config.openai_api_key)
    """
    
    def __init__(self, env_file: Optional[str] = ".env"):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file (default: ".env")
                     Set to None to skip .env loading
        """
        # Try to load .env file (for local development)
        if env_file and Path(env_file).exists():
            load_dotenv(env_file)
            self._source = f"local {env_file} file"
        else:
            self._source = "environment variables"
        
        # Load all secrets from environment
        self._load_secrets()
    
    def _load_secrets(self):
        """Load secrets from environment variables"""
        
        # ============================================================
        # LLM API Keys
        # ============================================================
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.huggingface_token = os.getenv('HUGGINGFACE_AP_KEY')
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        
        # ============================================================
        # Cloud Provider Credentials
        # ============================================================
        self.gcp_project_id = os.getenv('GCP_PROJECT_ID')
        self.gcp_location = os.getenv('GCP_LOCATION', 'us-central1')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.azure_subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        
        # ============================================================
        # Storage
        # ============================================================
        self.gcs_bucket = os.getenv('GCS_BUCKET')
        self.s3_bucket = os.getenv('S3_BUCKET')
        
        # ============================================================
        # Database
        # ============================================================
        self.db_connection_string = os.getenv('DB_CONNECTION_STRING')
        self.postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
        self.postgres_port = os.getenv('POSTGRES_PORT', '5432')
        self.postgres_db = os.getenv('POSTGRES_DB')
        self.postgres_user = os.getenv('POSTGRES_USER')
        self.postgres_password = os.getenv('POSTGRES_PASSWORD')
        
        # ============================================================
        # GitHub
        # ============================================================
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repository = os.getenv('GITHUB_REPOSITORY')
        
        # ============================================================
        # Application Settings
        # ============================================================
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    def validate(self, required_keys: List[str]):
        """
        Validate that required secrets are present.
        
        Args:
            required_keys: List of attribute names that must be set
            
        Raises:
            ValueError: If any required keys are missing
            
        Example:
            config.validate(['openai_api_key', 'gcp_project_id'])
        """
        missing = []
        for key in required_keys:
            value = getattr(self, key, None)
            if not value:
                missing.append(key)
        
        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}\n"
                f"Loaded from: {self._source}\n"
                f"\n"
                f"To fix:\n"
                f"  - Local: Add to .env file\n"
                f"  - GitHub Actions: Add to repository secrets\n"
                f"  - Cloud: Set environment variables\n"
            )
    
    def get_llm_client(self, provider: str = 'openai'):
        """
        Get LLM client for specified provider.
        
        Args:
            provider: One of 'openai', 'anthropic', 'google', 'cohere'
            
        Returns:
            Configured client instance
            
        Example:
            client = config.get_llm_client('openai')
            response = client.chat.completions.create(...)
        """
        if provider == 'openai':
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY not configured")
            from openai import OpenAI
            return OpenAI(api_key=self.openai_api_key)
        
        elif provider == 'anthropic':
            if not self.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            from anthropic import Anthropic
            return Anthropic(api_key=self.anthropic_api_key)
        
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
            return cohere.Client(api_key=self.cohere_api_key)
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    @property
    def is_github_actions(self) -> bool:
        """Check if running in GitHub Actions"""
        return os.getenv('GITHUB_ACTIONS') == 'true'
    
    @property
    def is_local(self) -> bool:
        """Check if running in local development"""
        return not self.is_github_actions and Path('.env').exists()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == 'production'
    
    def get_masked_key(self, key_name: str) -> str:
        """
        Get masked version of API key for safe logging.
        
        Args:
            key_name: Name of the key attribute
            
        Returns:
            Masked key string (e.g., "sk-proj-...x7Qz")
            
        Example:
            print(f"Using key: {config.get_masked_key('openai_api_key')}")
            # Output: Using key: sk-proj-...x7Qz
        """
        key = getattr(self, key_name, None)
        if not key:
            return "NOT_SET"
        if len(key) < 12:
            return "***"
        return f"{key[:8]}...{key[-4:]}"
    
    def __repr__(self):
        return (
            f"HypatiaConfig("
            f"source={self._source}, "
            f"is_github_actions={self.is_github_actions}, "
            f"environment={self.environment})"
        )
    
    def print_status(self):
        """Print configuration status (safe for logging)"""
        print("="*60)
        print("HypatiaX Configuration Status")
        print("="*60)
        print(f"Environment: {self.environment}")
        print(f"Source: {self._source}")
        print(f"GitHub Actions: {self.is_github_actions}")
        print(f"Local: {self.is_local}")
        print(f"Debug: {self.debug}")
        print()
        print("API Keys Status:")
        print(f"  OpenAI: {self.get_masked_key('openai_api_key')}")
        print(f"  Anthropic: {self.get_masked_key('anthropic_api_key')}")
        print(f"  Google: {self.get_masked_key('google_api_key')}")
        print(f"  HuggingFace: {self.get_masked_key('huggingface_token')}")
        print()
        print("Cloud Configuration:")
        print(f"  GCP Project: {self.gcp_project_id or 'NOT_SET'}")
        print(f"  GCS Bucket: {self.gcs_bucket or 'NOT_SET'}")
        print(f"  AWS Region: {self.aws_region}")
        print("="*60)


# ============================================================
# Singleton Instance (recommended usage)
# ============================================================
config = HypatiaConfig()


# ============================================================
# Usage Examples
# ============================================================

def example_basic_usage():
    """Example 1: Basic usage"""
    from hypatia_x.config import config
    
    # Validate required secrets
    config.validate(['openai_api_key'])
    
    # Use the secrets
    from openai import OpenAI
    client = OpenAI(api_key=config.openai_api_key)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)


def example_multi_provider():
    """Example 2: Multiple LLM providers"""
    from hypatia_x.config import config
    
    # Get different LLM clients
    openai_client = config.get_llm_client('openai')
    anthropic_client = config.get_llm_client('anthropic')
    
    # Use them
    openai_response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Explain AI"}]
    )
    
    anthropic_response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Explain AI"}]
    )


def example_conditional_logic():
    """Example 3: Different behavior based on environment"""
    from hypatia_x.config import config
    
    if config.is_local:
        print("Running in local development mode")
        # Use smaller model, less data, etc.
        model = "gpt-3.5-turbo"
        max_iterations = 10
    elif config.is_github_actions:
        print("Running in CI/CD")
        # Run full test suite
        model = "gpt-4"
        max_iterations = 100
    elif config.is_production:
        print("Running in production")
        # Use production settings
        model = "gpt-4-turbo"
        max_iterations = 1000


def example_safe_logging():
    """Example 4: Safe logging of configuration"""
    from hypatia_x.config import config
    import logging
    
    # Print status (masks sensitive data)
    config.print_status()
    
    # Safe logging
    logging.info(f"Using OpenAI key: {config.get_masked_key('openai_api_key')}")
    # Output: Using OpenAI key: sk-proj-...x7Qz


if __name__ == "__main__":
    # Show configuration status
    config.print_status()
    
    # Validate that we have OpenAI key
    try:
        config.validate(['openai_api_key'])
        print("\n✅ Configuration valid!")
    except ValueError as e:
        print(f"\n❌ Configuration error:\n{e}")

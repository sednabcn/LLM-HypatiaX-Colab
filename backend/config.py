"""
Unified Configuration Settings for HypatiaX API
File: backend/config.py
Version: 2.1.0
"""

import os
from datetime import timedelta
from pathlib import Path


class Config:
    """Base configuration class with all features"""

    # ========================================================================
    # SECURITY SETTINGS
    # ========================================================================
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # ========================================================================
    # APPLICATION SETTINGS
    # ========================================================================
    DEBUG = os.getenv("DEBUG", "True") == "True"
    TESTING = False

    # API Information
    API_VERSION = "2.1.0"
    API_TITLE = "HypatiaX Unified Formula API"
    API_DESCRIPTION = (
        "HypatiaX Tableau NER + Mathematical Formula Extraction + DeFi Analytics"
    )
    API_PREFIX = "/api"

    # ========================================================================
    # CORS SETTINGS
    # ========================================================================
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000",
    ).split(",")

    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
    CORS_EXPOSE_HEADERS = ["Content-Range", "X-Content-Range"]
    CORS_MAX_AGE = 600  # 10 minutes

    # ========================================================================
    # PATH CONFIGURATION
    # ========================================================================
    # Base directories
    BASE_DIR = Path(__file__).parent
    PROJECT_ROOT = BASE_DIR.parent

    # HypatiaX model paths
    HYPATIAX_DIR = PROJECT_ROOT / "hypatiax"
    MODELS_DIR = HYPATIAX_DIR / "data_spacy" / "queries" / "tableau"

    # Specific model paths
    NER_DESC_MODEL = str(MODELS_DIR / "ner_tableau_desc")
    NER_FORMULA_MODEL = str(MODELS_DIR / "ner_tableau_formulas")

    # Service directories
    SERVICES_DIR = BASE_DIR / "services"
    API_DIR = BASE_DIR / "api"

    # Data directories
    DATA_DIR = BASE_DIR / "data"
    UPLOAD_DIR = DATA_DIR / "uploads"
    CACHE_DIR = DATA_DIR / "cache"

    # ========================================================================
    # LOGGING CONFIGURATION
    # ========================================================================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/app.log"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

    # ========================================================================
    # REQUEST LIMITS
    # ========================================================================
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    RATELIMIT_ENABLED = False
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = "memory://"

    # Per-endpoint rate limits
    RATELIMIT_MAP = {
        "/api/hypatiax/map": "50 per minute",
        "/api/hypatiax/batch": "10 per minute",
        "/api/ner/extract-formula": "50 per minute",
        "/api/ner/batch-extract": "10 per minute",
        "/api/defi/analyze-position": "100 per minute",
    }

    # ========================================================================
    # CACHE CONFIGURATION
    # ========================================================================
    CACHE_ENABLED = True
    CACHE_TYPE = "simple"  # Options: simple, redis, memcached
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes

    # ========================================================================
    # SERVICE-SPECIFIC SETTINGS
    # ========================================================================

    # HypatiaX Settings
    HYPATIAX_ENABLED = True
    HYPATIAX_FALLBACK_MODE = True  # Use mock mode if models not loaded
    HYPATIAX_CONFIDENCE_THRESHOLD = 0.7

    # NER Service Settings
    NER_ENABLED = True
    NER_MAX_TEXT_LENGTH = 10000  # characters
    NER_BATCH_MAX_SIZE = 100  # max items in batch

    # DeFi Calculator Settings
    DEFI_ENABLED = True
    DEFI_DEFAULT_FEE_RATE = 0.003  # 0.3% Uniswap V2
    DEFI_MAX_DAYS_ELAPSED = 3650  # ~10 years max

    # ========================================================================
    # TIMEOUT SETTINGS
    # ========================================================================
    REQUEST_TIMEOUT = 30  # seconds
    MODEL_LOAD_TIMEOUT = 60  # seconds
    CALCULATION_TIMEOUT = 10  # seconds

    # ========================================================================
    # FEATURE FLAGS
    # ========================================================================
    FEATURES = {
        "hypatiax": True,
        "ner_service": True,
        "defi_calculator": True,
        "agents": False,  # Optional feature
        "batch_processing": True,
        "async_processing": False,  # Future feature
        "caching": True,
        "rate_limiting": False,
    }

    # ========================================================================
    # DATABASE SETTINGS (for future use)
    # ========================================================================
    DATABASE_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///hypatiax.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # ========================================================================
    # MONITORING & HEALTH CHECK
    # ========================================================================
    HEALTH_CHECK_ENABLED = True
    HEALTH_CHECK_PATH = "/api/health"
    METRICS_ENABLED = False  # Prometheus metrics

    # ========================================================================
    # ERROR HANDLING
    # ========================================================================
    PROPAGATE_EXCEPTIONS = True
    TRAP_HTTP_EXCEPTIONS = False
    TRAP_BAD_REQUEST_ERRORS = False

    # ========================================================================
    # SESSION CONFIGURATION (if needed)
    # ========================================================================
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)


class DevelopmentConfig(Config):
    """Development environment configuration"""

    DEBUG = True
    TESTING = False

    # Detailed logging in development
    LOG_LEVEL = "DEBUG"
    JSONIFY_PRETTYPRINT_REGULAR = True

    # No rate limiting in development
    RATELIMIT_ENABLED = False

    # Enable all features for testing
    FEATURES = {
        "hypatiax": True,
        "ner_service": True,
        "defi_calculator": True,
        "agents": True,
        "batch_processing": True,
        "async_processing": False,
        "caching": True,
        "rate_limiting": False,
    }

    # More permissive CORS in development
    CORS_ORIGINS = ["*"]


class ProductionConfig(Config):
    """Production environment configuration"""

    DEBUG = False
    TESTING = False

    # Production logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")

    # Enable rate limiting in production
    RATELIMIT_ENABLED = True

    # Stricter CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://yourdomain.com").split(",")

    # Enable caching
    CACHE_TYPE = os.getenv("CACHE_TYPE", "redis")
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Database in production
    DATABASE_ENABLED = True

    # Enable monitoring
    METRICS_ENABLED = True

    # Stricter feature flags
    FEATURES = {
        "hypatiax": True,
        "ner_service": True,
        "defi_calculator": True,
        "agents": False,
        "batch_processing": True,
        "async_processing": False,
        "caching": True,
        "rate_limiting": True,
    }


class TestingConfig(Config):
    """Testing environment configuration"""

    TESTING = True
    DEBUG = True

    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Disable external services in testing
    HYPATIAX_ENABLED = False
    NER_ENABLED = False
    DEFI_ENABLED = False

    # Fast timeouts for testing
    REQUEST_TIMEOUT = 5
    MODEL_LOAD_TIMEOUT = 10
    CALCULATION_TIMEOUT = 2

    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False

    # All features available for testing
    FEATURES = {
        "hypatiax": True,
        "ner_service": True,
        "defi_calculator": True,
        "agents": True,
        "batch_processing": True,
        "async_processing": False,
        "caching": False,  # Disable cache in tests
        "rate_limiting": False,
    }


class DockerConfig(Config):
    """Docker/Container environment configuration"""

    DEBUG = False

    # Use environment variables in Docker
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Redis cache in Docker
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # PostgreSQL in Docker
    DATABASE_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://user:password@postgres:5432/hypatiax"
    )

    # Container-friendly paths
    LOG_FILE = "/var/log/hypatiax/app.log"
    DATA_DIR = Path("/data")
    UPLOAD_DIR = Path("/data/uploads")
    CACHE_DIR = Path("/data/cache")


# ============================================================================
# CONFIGURATION REGISTRY
# ============================================================================

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "docker": DockerConfig,
    "default": DevelopmentConfig,
}


def get_config(env=None):
    """
    Get configuration based on environment

    Args:
        env: Environment name (development, production, testing, docker)

    Returns:
        Configuration class
    """
    if env is None:
        env = os.getenv("FLASK_ENV", "development")

    config_class = config.get(env, config["default"])

    # Log which config is being used
    print(f"📋 Loading configuration: {config_class.__name__}")

    return config_class


def validate_config(config_obj):
    """
    Validate configuration settings

    Args:
        config_obj: Configuration object

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []

    # Check required directories exist or can be created
    required_dirs = ["LOG_FILE", "DATA_DIR", "UPLOAD_DIR"]
    for dir_name in required_dirs:
        if hasattr(config_obj, dir_name):
            path = Path(getattr(config_obj, dir_name))
            if dir_name == "LOG_FILE":
                path = path.parent

            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create directory {path}: {e}")

    # Validate model paths if HypatiaX is enabled
    if config_obj.HYPATIAX_ENABLED:
        if not Path(config_obj.HYPATIAX_DIR).exists():
            errors.append(f"HypatiaX directory not found: {config_obj.HYPATIAX_DIR}")

    # Validate CORS origins
    if not config_obj.CORS_ORIGINS:
        errors.append("CORS_ORIGINS cannot be empty")

    # Check rate limiting configuration
    if config_obj.RATELIMIT_ENABLED and not config_obj.RATELIMIT_DEFAULT:
        errors.append("RATELIMIT_DEFAULT must be set when rate limiting is enabled")

    return len(errors) == 0, errors


# ============================================================================
# CONFIGURATION HELPER FUNCTIONS
# ============================================================================


def ensure_directories(config_obj):
    """Create necessary directories if they don't exist"""
    directories = [
        config_obj.DATA_DIR,
        config_obj.UPLOAD_DIR,
        config_obj.CACHE_DIR,
        Path(config_obj.LOG_FILE).parent,
    ]

    for directory in directories:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory ensured: {directory}")


def print_config_summary(config_obj):
    """Print configuration summary"""
    print("\n" + "=" * 80)
    print("📋 CONFIGURATION SUMMARY")
    print("=" * 80)
    print(f"Environment: {config_obj.__class__.__name__}")
    print(f"Debug Mode: {config_obj.DEBUG}")
    print(f"API Version: {config_obj.API_VERSION}")
    print(f"Log Level: {config_obj.LOG_LEVEL}")
    print(f"Rate Limiting: {'Enabled' if config_obj.RATELIMIT_ENABLED else 'Disabled'}")
    print(f"Cache: {'Enabled' if config_obj.CACHE_ENABLED else 'Disabled'}")
    print(f"\nEnabled Features:")
    for feature, enabled in config_obj.FEATURES.items():
        status = "✅" if enabled else "❌"
        print(f"  {status} {feature}")
    print("=" * 80 + "\n")


# Example usage
if __name__ == "__main__":
    # Test configuration loading
    config_obj = get_config()
    print_config_summary(config_obj)

    # Validate configuration
    is_valid, errors = validate_config(config_obj)
    if is_valid:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")


# 🚀 How to Use

# In your app.py
# from config import get_config, ensure_directories, print_config_summary

# Load config based on environment
# config_obj = get_config()  # Uses FLASK_ENV environment variable
# app.config.from_object(config_obj)

# Ensure directories exist
# ensure_directories(config_obj)

# Print summary
# print_config_summary(config_obj)

# 📋 Environment Variables You Can Set

# Set environment
# export FLASK_ENV=production  # or development, testing, docker

# Override settings
# export DEBUG=False
# export LOG_LEVEL=WARNING
# export CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
# export SECRET_KEY=your-secret-key-here
# export REDIS_URL=redis://localhost:6379/0

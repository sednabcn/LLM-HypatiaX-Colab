"""
HypatiaX Configuration Module

UPDATED: Implements lazy initialization pattern using a proxy object.
This avoids circular imports and import-time side effects.

Structure:
- config_path.py: PathConfig for project paths
- config.py: SecretsConfig for API keys and credentials
- __init__.py: Integrates both with lazy initialization

Usage:
    from hypatiax.config import config_path, secrets

    # Use paths (eager initialization - always available)
    data_file = config_path.datasets / "training.json"

    # Use secrets (lazy initialization - created on first access)
    secrets.validate(['anthropic_api_key'])
    client = secrets.get_llm_client('anthropic')

    # Or use alias 'config' for backward compatibility
    from hypatiax.config import config
    data_file = config.datasets / "training.json"
"""

import logging

from hypatiax.config.config_path import PathConfig, config_path

logger = logging.getLogger(__name__)

# Alias for backward compatibility
config = config_path

# ============================================================
# Lazy Initialization for SecretsConfig
# ============================================================

# Import SecretsConfig class (not an instance!)
try:
    from hypatiax.config.config import SecretsConfig

    _has_secrets_class = True
except ImportError as e:
    SecretsConfig = None
    _has_secrets_class = False
    import warnings

    warnings.warn(
        f"SecretsConfig not available: {e}\n"
        f"Secrets functionality will be disabled. "
        f"Ensure hypatiax/config/config.py exists with SecretsConfig class."
    )

# Global instance (created lazily)
_secrets_instance = None
_secrets_initialization_attempted = False


class _SecretsProxy:
    """
    Proxy object for lazy initialization of SecretsConfig.

    This proxy intercepts all attribute access and creates the real
    SecretsConfig instance only on first access. This provides:
    - Safe imports (no side effects at import time)
    - Avoids circular import issues
    - Only initializes when actually needed
    - Transparent to users (works exactly like direct instance)

    Implementation:
    - __getattr__: Intercepts attribute access (secrets.openai_api_key)
    - __call__: Allows reinitializing with custom parameters
    - __dir__: Shows available attributes for IDE autocomplete
    - __repr__: Provides helpful string representation
    """

    def __init__(self):
        """Initialize the proxy (lightweight, no side effects)."""
        self._proxy_initialized = True

    def __getattr__(self, name):
        """
        Intercept attribute access and create real instance if needed.

        Called when: secrets.openai_api_key, secrets.validate(), etc.
        """
        # Avoid infinite recursion on our own attributes
        if name.startswith("_proxy_"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        # Create real instance on first access
        global _secrets_instance, _secrets_initialization_attempted

        if _secrets_instance is None:
            if not _has_secrets_class:
                raise ImportError(
                    "SecretsConfig class not available. "
                    "Cannot create secrets instance. "
                    "Ensure hypatiax/config/config.py exists."
                )

            if not _secrets_initialization_attempted:
                _secrets_initialization_attempted = True
                logger.info(
                    "🔧 Lazy initialization: Creating SecretsConfig instance on first access"
                )

                try:
                    # Create instance with PathConfig integration
                    _secrets_instance = SecretsConfig(path_config=config_path)
                    logger.info("✅ SecretsConfig initialized successfully")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize SecretsConfig: {e}")
                    _secrets_instance = None
                    raise RuntimeError(
                        f"Failed to initialize SecretsConfig: {e}\n"
                        f"This may be due to missing dependencies or configuration issues."
                    ) from e

        # Forward attribute access to real instance
        if _secrets_instance is None:
            raise RuntimeError(
                "SecretsConfig instance is None. "
                "Initialization may have failed. Check logs for details."
            )

        return getattr(_secrets_instance, name)

    def __call__(self, custom_root=None, path_config=None):
        """
        Allow calling the proxy to reinitialize with custom parameters.

        Usage:
            secrets = secrets(custom_root=Path("/custom/path"))
        """
        global _secrets_instance

        if not _has_secrets_class:
            raise ImportError("SecretsConfig class not available")

        logger.info("🔄 Reinitializing SecretsConfig with custom parameters")

        if path_config is not None:
            _secrets_instance = SecretsConfig(path_config=path_config)
        elif custom_root:
            custom_path_config = PathConfig(custom_root)
            _secrets_instance = SecretsConfig(path_config=custom_path_config)
        else:
            _secrets_instance = SecretsConfig(path_config=config_path)

        return _secrets_instance

    def __dir__(self):
        """
        Provide attribute list for IDE autocomplete.

        Returns attributes from SecretsConfig class for better IDE support.
        """
        if _secrets_instance is not None:
            return dir(_secrets_instance)
        elif _has_secrets_class:
            # Return class attributes for autocomplete before initialization
            return [attr for attr in dir(SecretsConfig) if not attr.startswith("_")]
        else:
            return []

    def __repr__(self):
        """Provide helpful string representation."""
        if _secrets_instance is not None:
            return repr(_secrets_instance)
        else:
            return (
                "<SecretsProxy: not yet initialized - will be created on first access>"
            )

    def __bool__(self):
        """
        Allow boolean checks: if secrets: ...
        Returns True if SecretsConfig class is available.
        """
        return _has_secrets_class


# Create the proxy (lightweight, no side effects!)
secrets = _SecretsProxy() if _has_secrets_class else None


# ============================================================
# Convenience Functions
# ============================================================


def get_secrets(custom_root=None, force_reinit=False):
    """
    Get the secrets instance (or create/reinitialize it).

    Args:
        custom_root: Optional custom root directory
        force_reinit: Force reinitialization even if already initialized

    Returns:
        SecretsConfig instance

    Example:
        # Get existing instance (or create on first call)
        secrets = get_secrets()

        # Create with custom root
        secrets = get_secrets(custom_root=Path("/my/project"))

        # Force reinitialization
        secrets = get_secrets(force_reinit=True)
    """
    global _secrets_instance

    if not _has_secrets_class:
        raise ImportError(
            "SecretsConfig not available. Ensure hypatiax/config/config.py exists."
        )

    # Reinitialize if requested or if custom_root provided
    if force_reinit or custom_root is not None:
        if custom_root:
            custom_path_config = PathConfig(custom_root)
            _secrets_instance = SecretsConfig(path_config=custom_path_config)
        else:
            _secrets_instance = SecretsConfig(path_config=config_path)
        return _secrets_instance

    # Lazy initialization on first call
    if _secrets_instance is None:
        _secrets_instance = SecretsConfig(path_config=config_path)

    return _secrets_instance


def has_secrets() -> bool:
    """
    Check if SecretsConfig is available.

    Returns:
        True if SecretsConfig class is available, False otherwise
    """
    return _has_secrets_class


def is_secrets_initialized() -> bool:
    """
    Check if secrets instance has been initialized.

    Returns:
        True if the real SecretsConfig instance exists, False otherwise
    """
    return _secrets_instance is not None


# ============================================================
# Display Configuration
# ============================================================


def show_all_config():
    """Display both path and secrets configuration."""
    print("\n" + "=" * 80)
    print("HYPATIAX CONFIGURATION STATUS")
    print("=" * 80 + "\n")

    # Show path config
    if config_path:
        config_path.print_config_path()
    else:
        print("⚠️  PathConfig not initialized")

    print("\n")

    # Show secrets config
    if not _has_secrets_class:
        print("⚠️  SecretsConfig class not available")
        print(
            "To enable: Ensure hypatiax/config/config.py exists with SecretsConfig class"
        )
    elif _secrets_instance is None:
        print("ℹ️  SecretsConfig not yet initialized (lazy loading)")
        print("It will be created automatically on first access to 'secrets'")
        print("\nTo initialize now, call: get_secrets()")
    else:
        _secrets_instance.print_status()

    print("\n" + "=" * 80)


def show_initialization_status():
    """Show detailed initialization status (for debugging)."""
    print("\n" + "=" * 70)
    print("INITIALIZATION STATUS")
    print("=" * 70)
    print(f"SecretsConfig class available:  {_has_secrets_class}")
    print(f"Secrets instance initialized:   {_secrets_instance is not None}")
    print(f"Initialization attempted:       {_secrets_initialization_attempted}")

    if _secrets_instance:
        print(f"Instance type:                  {type(_secrets_instance).__name__}")
        print(f"Environment:                    {_secrets_instance.environment}")
        print(f"Source:                         {_secrets_instance._source}")

    print("=" * 70 + "\n")


# ============================================================
# Exports
# ============================================================

__all__ = [
    # Path configuration (eager, always available)
    "PathConfig",
    "config",  # Alias for config_path (backward compatible)
    "config_path",  # Explicit path config
    # Secrets configuration (lazy initialization)
    "secrets",  # Lazy proxy instance
    "get_secrets",  # Function to get/create secrets instance
    # Utility functions
    "has_secrets",  # Check if SecretsConfig is available
    "is_secrets_initialized",  # Check if instance is created
    "show_all_config",  # Display all configuration
    "show_initialization_status",  # Show initialization details
]

# Only export SecretsConfig class if available
if _has_secrets_class:
    __all__.append("SecretsConfig")


# ============================================================
# Test/Debug Mode
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("HYPATIAX CONFIG MODULE TEST")
    print("=" * 80 + "\n")

    # Show initialization status
    show_initialization_status()

    # Show all configuration
    show_all_config()

    # Test lazy initialization
    print("\n" + "=" * 80)
    print("TESTING LAZY INITIALIZATION")
    print("=" * 80)

    if has_secrets():
        print("\n1. Secrets proxy created (but not initialized yet)")
        print(f"   Proxy object: {secrets}")
        print(f"   Is initialized? {is_secrets_initialized()}")

        print("\n2. Accessing secrets for the first time...")
        try:
            env = secrets.environment  # This triggers initialization!
            print(f"   ✅ Success! Environment: {env}")
            print(f"   Is initialized? {is_secrets_initialized()}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("\n3. Second access (uses existing instance)...")
        try:
            env_name = secrets.environment_name
            print(f"   ✅ Environment name: {env_name}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print("⚠️  SecretsConfig not available")

    print("\n" + "=" * 80)
    print("✅ Test complete!")
    print("=" * 80 + "\n")

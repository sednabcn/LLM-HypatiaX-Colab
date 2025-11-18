"""
HypatiaX Configuration Module
"""

from hypatiax.config.paths import PathConfig, config

# Try to import SecretsConfig
try:
    from hypatiax.config.config_secret_keys import SecretsConfig, secrets
    _has_secrets = True
except ImportError as e:
    SecretsConfig = None
    secrets = None
    _has_secrets = False
    import warnings
    warnings.warn(f"SecretsConfig not available: {e}")

__all__ = [
    'PathConfig',
    'config',
]

if _has_secrets:
    __all__.extend(['SecretsConfig', 'secrets'])

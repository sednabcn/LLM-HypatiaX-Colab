# Module: `config/api_key_management.py`

## Description

API Key Manager for HypatiaX
Secure storage, retrieval, and validation of API keys
Location: hypatiax/config/api_key_manager.py

**Last Modified**: 2025-11-13T23:03:44.785351

## Dependencies

- `anthropic`
- `argparse`
- `cohere`
- `cryptography.fernet`
- `dataclasses`
- `getpass`
- `google.generativeai`
- `huggingface_hub`
- `json`
- `keyring`
- `openai`
- `os`
- `pathlib`
- `typing`

## Constants

- `SERVICE_NAME`
- `PROVIDERS`

## Classes

### `APIKeyConfig`

Configuration for API key storage

**Decorators**: `dataclass`

### `APIKeyManager`

Manages API keys with multiple storage strategies
Priority: System Keyring > Environment Variables > Encrypted File > Prompt User

**Methods**:

- `__init__(self, config: APIKeyConfig)`
- `_get_or_create_cipher(self) -> Fernet`
  - Get or create encryption cipher
- `get_api_key(self, provider: str) -> Optional[str]`
  - Get API key with fallback priority:
- `set_api_key(self, provider: str, api_key: str, storage: str) -> bool`
  - Store API key with specified storage method
- `delete_api_key(self, provider: str) -> bool`
  - Delete API key from all storage locations
- `list_configured_providers(self) -> Dict[<ast.Tuple object at 0x7fa6f86f0e90>]`
  - List which providers have API keys configured
- `validate_api_key(self, provider: str, api_key: str) -> bool`
  - Validate API key by making a test request
- `_validate_anthropic(self, api_key: str) -> bool`
  - Validate Anthropic API key
- `_validate_openai(self, api_key: str) -> bool`
  - Validate OpenAI API key
- `_validate_deepseek(self, api_key: str) -> bool`
  - Validate DeepSeek API key
- `_validate_huggingface(self, api_key: str) -> bool`
  - Validate HuggingFace API key
- `_validate_cohere(self, api_key: str) -> bool`
  - Validate Cohere API key
- `_validate_google(self, api_key: str) -> bool`
  - Validate Google API key
- `_read_from_env_file(self, env_var: str) -> Optional[str]`
  - Read API key from .env file
- `_write_to_env_file(self, env_var: str, api_key: str)`
  - Write API key to .env file
- `_remove_from_env_file(self, env_var: str)`
  - Remove API key from .env file
- `_read_from_encrypted_file(self, env_var: str) -> Optional[str]`
  - Read API key from encrypted file
- `_write_to_encrypted_file(self, env_var: str, api_key: str)`
  - Write API key to encrypted file
- `_remove_from_encrypted_file(self, env_var: str)`
  - Remove API key from encrypted file
- `prompt_for_api_key(self, provider: str, store: bool, storage: str) -> Optional[str]`
  - Prompt user to enter API key interactively
- `interactive_setup(self)`
  - Interactive setup for all API keys

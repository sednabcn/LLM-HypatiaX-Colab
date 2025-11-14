# Module: `config/google_credentials_manager.py`

## Description

Google Credentials Manager for HypatiaX
Handles Google Cloud API keys and OAuth credentials
Location: hypatiax/config/google_credentials_manager.py

**Last Modified**: 2025-11-13T23:00:15.325973

## Dependencies

- `argparse`
- `dataclasses`
- `getpass`
- `json`
- `keyring`
- `os`
- `pathlib`
- `typing`

## Constants

- `SERVICE_NAME`

## Classes

### `GoogleCredentialsConfig`

Configuration for Google credentials

**Decorators**: `dataclass`

### `GoogleCredentialsManager`

Manage Google API credentials securely

**Methods**:

- `__init__(self, config: GoogleCredentialsConfig)`
- `set_api_key(self, api_key: str, service_name: str) -> bool`
  - Store Google API key
- `get_api_key(self, service_name: str) -> Optional[str]`
  - Get Google API key
- `set_oauth_credentials(self, credentials_dict: Dict) -> bool`
  - Store OAuth 2.0 credentials from Google Cloud Console
- `get_oauth_credentials(self) -> Optional[Dict]`
  - Get OAuth 2.0 credentials
- `load_credentials_from_file(self, filepath: str) -> bool`
  - Load credentials from downloaded JSON file
- `setup_interactive(self)`
  - Interactive setup for Google credentials
- `_setup_api_key(self)`
  - Setup API key interactively
- `_setup_oauth(self)`
  - Setup OAuth credentials interactively

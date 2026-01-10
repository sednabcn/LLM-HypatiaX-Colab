#!/usr/bin/env python3
"""
Google Credentials Manager for HypatiaX
Handles Google Cloud API keys and OAuth credentials
Location: hypatiax/config/google_credentials_manager.py
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import keyring


@dataclass
class GoogleCredentialsConfig:
    """Configuration for Google credentials"""

    config_dir: str = "./config"
    credentials_file: str = "google_credentials.json"
    use_keyring: bool = True


class GoogleCredentialsManager:
    """Manage Google API credentials securely"""

    SERVICE_NAME = "HypatiaX_Google"

    def __init__(self, config: GoogleCredentialsConfig = None):
        self.config = config or GoogleCredentialsConfig()
        self.config_path = Path(self.config.config_dir)
        self.credentials_file = self.config_path / self.config.credentials_file

        # Ensure config directory exists
        self.config_path.mkdir(parents=True, exist_ok=True)

    def set_api_key(self, api_key: str, service_name: str = "default") -> bool:
        """
        Store Google API key

        Args:
            api_key: The Google API key
            service_name: Name of the service (e.g., "gmail", "drive", "sheets")

        Returns:
            bool: Success status
        """

        try:
            if self.config.use_keyring:
                keyring.set_password(
                    self.SERVICE_NAME, f"api_key_{service_name}", api_key
                )
                print(f"✅ Google API key for {service_name} stored in keyring")
            else:
                # Store in environment variable
                os.environ[f"GOOGLE_API_KEY_{service_name.upper()}"] = api_key
                print(f"✅ Google API key for {service_name} stored in environment")

            return True

        except Exception as e:
            print(f"❌ Failed to store API key: {e}")
            return False

    def get_api_key(self, service_name: str = "default") -> Optional[str]:
        """
        Get Google API key

        Args:
            service_name: Name of the service

        Returns:
            The API key or None
        """

        # Try keyring
        if self.config.use_keyring:
            try:
                key = keyring.get_password(self.SERVICE_NAME, f"api_key_{service_name}")
                if key:
                    return key
            except Exception:
                pass

        # Try environment variable
        key = os.getenv(f"GOOGLE_API_KEY_{service_name.upper()}")
        if key:
            return key

        return None

    def set_oauth_credentials(self, credentials_dict: Dict) -> bool:
        """
        Store OAuth 2.0 credentials from Google Cloud Console

        Args:
            credentials_dict: The credentials dictionary from downloaded JSON

        Example credentials_dict:
        {
            "client_id": "123456789.apps.googleusercontent.com",
            "client_secret": "GOCSPX-abc123...",
            "redirect_uris": ["http://localhost:8080/"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        """

        try:
            # Save to file
            with open(self.credentials_file, "w") as f:
                json.dump(credentials_dict, f, indent=2)

            # Restrict permissions (Unix-like systems)
            try:
                os.chmod(self.credentials_file, 0o600)
            except:
                pass

            # Also store in keyring
            if self.config.use_keyring:
                keyring.set_password(
                    self.SERVICE_NAME,
                    "client_id",
                    credentials_dict.get("client_id", ""),
                )
                keyring.set_password(
                    self.SERVICE_NAME,
                    "client_secret",
                    credentials_dict.get("client_secret", ""),
                )

            print(f"✅ OAuth credentials saved to {self.credentials_file}")
            return True

        except Exception as e:
            print(f"❌ Failed to save OAuth credentials: {e}")
            return False

    def get_oauth_credentials(self) -> Optional[Dict]:
        """
        Get OAuth 2.0 credentials

        Returns:
            Credentials dictionary or None
        """

        # Try file first
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to read credentials file: {e}")

        # Try keyring
        if self.config.use_keyring:
            try:
                client_id = keyring.get_password(self.SERVICE_NAME, "client_id")
                client_secret = keyring.get_password(self.SERVICE_NAME, "client_secret")

                if client_id and client_secret:
                    return {"client_id": client_id, "client_secret": client_secret}
            except Exception:
                pass

        return None

    def load_credentials_from_file(self, filepath: str) -> bool:
        """
        Load credentials from downloaded JSON file

        Args:
            filepath: Path to the credentials JSON file from Google Cloud Console

        Returns:
            bool: Success status
        """

        try:
            with open(filepath, "r") as f:
                credentials = json.load(f)

            # Handle different credential formats
            if "installed" in credentials:
                creds = credentials["installed"]
            elif "web" in credentials:
                creds = credentials["web"]
            else:
                creds = credentials

            return self.set_oauth_credentials(creds)

        except Exception as e:
            print(f"❌ Failed to load credentials from file: {e}")
            return False

    def setup_interactive(self):
        """Interactive setup for Google credentials"""

        print("\n" + "=" * 60)
        print("🔐 Google Credentials Setup")
        print("=" * 60)

        print("\nWhat type of credentials do you want to set up?")
        print("1. API Key (for simple API access)")
        print("2. OAuth 2.0 (for Gmail API, Drive, etc.)")

        choice = input("\nEnter choice (1-2): ").strip()

        if choice == "1":
            self._setup_api_key()
        elif choice == "2":
            self._setup_oauth()
        else:
            print("❌ Invalid choice")

    def _setup_api_key(self):
        """Setup API key interactively"""

        print("\n📋 API Key Setup")
        print("-" * 60)
        print("\nTo get your API key:")
        print("1. Go to: https://console.cloud.google.com/apis/credentials")
        print("2. Click 'Create Credentials' → 'API Key'")
        print("3. Copy the generated key")
        print("4. IMPORTANT: Click 'Restrict Key' to secure it!")
        print()

        service = input("Service name (e.g., gmail, drive, sheets): ").strip().lower()
        if not service:
            service = "default"

        import getpass

        api_key = getpass.getpass("Enter your Google API key (hidden): ").strip()

        if api_key:
            if self.set_api_key(api_key, service):
                print(f"\n✅ API key for {service} configured successfully!")
            else:
                print("\n❌ Failed to configure API key")
        else:
            print("\n❌ No API key entered")

    def _setup_oauth(self):
        """Setup OAuth credentials interactively"""

        print("\n📋 OAuth 2.0 Setup")
        print("-" * 60)
        print("\nTo get OAuth credentials:")
        print("1. Go to: https://console.cloud.google.com/apis/credentials")
        print("2. Click 'Create Credentials' → 'OAuth client ID'")
        print("3. Choose 'Desktop app' or 'Web application'")
        print("4. Download the JSON file")
        print()

        filepath = input("Enter path to downloaded credentials JSON file: ").strip()

        if filepath and Path(filepath).exists():
            if self.load_credentials_from_file(filepath):
                print("\n✅ OAuth credentials configured successfully!")
            else:
                print("\n❌ Failed to configure OAuth credentials")
        else:
            print("\n❌ File not found")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Manage Google credentials")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Setup command
    subparsers.add_parser("setup", help="Interactive setup")

    # Set API key
    api_parser = subparsers.add_parser("set-api-key", help="Set API key")
    api_parser.add_argument("--service", default="default", help="Service name")

    # Load OAuth
    oauth_parser = subparsers.add_parser("load-oauth", help="Load OAuth credentials")
    oauth_parser.add_argument("filepath", help="Path to credentials JSON file")

    args = parser.parse_args()

    manager = GoogleCredentialsManager()

    if args.command == "setup":
        manager.setup_interactive()

    elif args.command == "set-api-key":
        import getpass

        api_key = getpass.getpass("Enter API key: ")
        manager.set_api_key(api_key, args.service)

    elif args.command == "load-oauth":
        manager.load_credentials_from_file(args.filepath)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

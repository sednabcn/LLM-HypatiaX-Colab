#!/usr/bin/env python3
"""
API Key Manager for HypatiaX
Secure storage, retrieval, and validation of API keys
Location: hypatiax/config/api_key_manager.py
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass
import keyring  # For secure system keyring storage
from cryptography.fernet import Fernet
import getpass


@dataclass
class APIKeyConfig:
    """Configuration for API key storage"""
    use_keyring: bool = True  # Use system keyring (most secure)
    use_env_file: bool = True  # Fallback to .env file
    use_encrypted_file: bool = False  # Encrypted JSON file
    config_dir: str = "./config"
    env_file: str = ".env"
    encrypted_file: str = ".api_keys.encrypted"


class APIKeyManager:
    """
    Manages API keys with multiple storage strategies
    Priority: System Keyring > Environment Variables > Encrypted File > Prompt User
    """
    
    # Service name for keyring
    SERVICE_NAME = "HypatiaX"
    
    # Supported providers
    PROVIDERS = {
        "ANTHROPIC": "ANTHROPIC_API_KEY",
        "OPENAI": "OPENAI_API_KEY",
        "DEEPSEEK": "DEEPSEEK_API_KEY",
        "HUGGINGFACE": "HUGGINGFACE_API_KEY",
        "COHERE": "COHERE_API_KEY",
        "GOOGLE": "GOOGLE_API_KEY"
    }
    
    def __init__(self, config: APIKeyConfig = None):
        self.config = config or APIKeyConfig()
        self.config_path = Path(self.config.config_dir)
        self.env_file_path = self.config_path / self.config.env_file
        self.encrypted_file_path = self.config_path / self.config.encrypted_file
        
        # Ensure config directory exists
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Load encryption key if using encrypted storage
        self.cipher = None
        if self.config.use_encrypted_file:
            self.cipher = self._get_or_create_cipher()
    
    def _get_or_create_cipher(self) -> Fernet:
        """Get or create encryption cipher"""
        key_file = self.config_path / ".encryption.key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Restrict permissions (Unix-like systems)
            try:
                os.chmod(key_file, 0o600)
            except:
                pass
        
        return Fernet(key)
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key with fallback priority:
        1. System keyring (most secure)
        2. Environment variables
        3. .env file
        4. Encrypted file
        5. Prompt user
        """
        
        provider = provider.upper()
        env_var = self.PROVIDERS.get(provider, f"{provider}_API_KEY")
        
        # 1. Try system keyring
        if self.config.use_keyring:
            try:
                key = keyring.get_password(self.SERVICE_NAME, env_var)
                if key:
                    return key
            except Exception as e:
                print(f"Warning: Keyring access failed: {e}")
        
        # 2. Try environment variable
        key = os.getenv(env_var)
        if key:
            return key
        
        # 3. Try .env file
        if self.config.use_env_file and self.env_file_path.exists():
            key = self._read_from_env_file(env_var)
            if key:
                return key
        
        # 4. Try encrypted file
        if self.config.use_encrypted_file:
            key = self._read_from_encrypted_file(env_var)
            if key:
                return key
        
        # 5. No key found - return None (caller decides whether to prompt)
        return None
    
    def set_api_key(self, provider: str, api_key: str, 
                     storage: str = "keyring") -> bool:
        """
        Store API key with specified storage method
        
        Args:
            provider: Provider name (e.g., "ANTHROPIC", "OPENAI")
            api_key: The API key to store
            storage: Storage method ("keyring", "env", "encrypted")
        
        Returns:
            bool: Success status
        """
        
        provider = provider.upper()
        env_var = self.PROVIDERS.get(provider, f"{provider}_API_KEY")
        
        try:
            if storage == "keyring":
                keyring.set_password(self.SERVICE_NAME, env_var, api_key)
                print(f"✅ API key for {provider} stored in system keyring")
                
            elif storage == "env":
                self._write_to_env_file(env_var, api_key)
                print(f"✅ API key for {provider} stored in .env file")
                
            elif storage == "encrypted":
                self._write_to_encrypted_file(env_var, api_key)
                print(f"✅ API key for {provider} stored in encrypted file")
                
            else:
                print(f"❌ Unknown storage method: {storage}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to store API key: {e}")
            return False
    
    def delete_api_key(self, provider: str) -> bool:
        """Delete API key from all storage locations"""
        
        provider = provider.upper()
        env_var = self.PROVIDERS.get(provider, f"{provider}_API_KEY")
        
        success = True
        
        # Delete from keyring
        try:
            keyring.delete_password(self.SERVICE_NAME, env_var)
            print(f"✅ Deleted {provider} key from keyring")
        except keyring.errors.PasswordDeleteError:
            pass  # Key didn't exist
        except Exception as e:
            print(f"⚠️ Failed to delete from keyring: {e}")
            success = False
        
        # Remove from .env file
        if self.env_file_path.exists():
            self._remove_from_env_file(env_var)
        
        # Remove from encrypted file
        if self.encrypted_file_path.exists():
            self._remove_from_encrypted_file(env_var)
        
        return success
    
    def list_configured_providers(self) -> Dict[str, bool]:
        """List which providers have API keys configured"""
        
        configured = {}
        
        for provider, env_var in self.PROVIDERS.items():
            has_key = self.get_api_key(provider) is not None
            configured[provider] = has_key
        
        return configured
    
    def validate_api_key(self, provider: str, api_key: str = None) -> bool:
        """
        Validate API key by making a test request
        
        Args:
            provider: Provider name
            api_key: API key to validate (if None, uses stored key)
        
        Returns:
            bool: Whether key is valid
        """
        
        if api_key is None:
            api_key = self.get_api_key(provider)
        
        if not api_key:
            return False
        
        provider = provider.upper()
        
        try:
            if provider == "ANTHROPIC":
                return self._validate_anthropic(api_key)
            elif provider == "OPENAI":
                return self._validate_openai(api_key)
            elif provider == "DEEPSEEK":
                return self._validate_deepseek(api_key)
            elif provider == "HUGGINGFACE":
                return self._validate_huggingface(api_key)
            elif provider == "COHERE":
                return self._validate_cohere(api_key)
            elif provider == "GOOGLE":
                return self._validate_google(api_key)
            else:
                print(f"⚠️ Validation not implemented for {provider}")
                return True  # Assume valid
                
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False
    
    def _validate_anthropic(self, api_key: str) -> bool:
        """Validate Anthropic API key"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            # Make a minimal test request
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception as e:
            print(f"❌ Anthropic key validation failed: {e}")
            return False
    
    def _validate_openai(self, api_key: str) -> bool:
        """Validate OpenAI API key"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            # Make a minimal test request
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception as e:
            print(f"❌ OpenAI key validation failed: {e}")
            return False
    
    def _validate_deepseek(self, api_key: str) -> bool:
        """Validate DeepSeek API key"""
        # DeepSeek uses OpenAI-compatible API
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            response = client.chat.completions.create(
                model="deepseek-chat",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception as e:
            print(f"❌ DeepSeek key validation failed: {e}")
            return False
    
    def _validate_huggingface(self, api_key: str) -> bool:
        """Validate HuggingFace API key"""
        try:
            from huggingface_hub import HfApi
            api = HfApi()
            user_info = api.whoami(token=api_key)
            print(f"✅ Logged in as: {user_info['name']}")
            return True
        except Exception as e:
            print(f"❌ HuggingFace key validation failed: {e}")
            return False
    
    def _validate_cohere(self, api_key: str) -> bool:
        """Validate Cohere API key"""
        try:
            import cohere
            client = cohere.Client(api_key=api_key)
            # Make a minimal test request
            response = client.generate(
                prompt="Test",
                max_tokens=5,
                model="command"
            )
            return True
        except Exception as e:
            print(f"❌ Cohere key validation failed: {e}")
            return False
    
    def _validate_google(self, api_key: str) -> bool:
        """Validate Google API key"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            # Make a minimal test request with Gemini
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Hi", 
                generation_config=genai.types.GenerationConfig(max_output_tokens=5))
            return True
        except Exception as e:
            print(f"❌ Google API key validation failed: {e}")
            return False
    
    def _read_from_env_file(self, env_var: str) -> Optional[str]:
        """Read API key from .env file"""
        
        if not self.env_file_path.exists():
            return None
        
        try:
            with open(self.env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{env_var}="):
                        return line.split('=', 1)[1].strip('"\'')
        except Exception as e:
            print(f"Warning: Failed to read .env file: {e}")
        
        return None
    
    def _write_to_env_file(self, env_var: str, api_key: str):
        """Write API key to .env file"""
        
        lines = []
        updated = False
        
        # Read existing content
        if self.env_file_path.exists():
            with open(self.env_file_path, 'r') as f:
                lines = f.readlines()
        
        # Update or append
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{env_var}="):
                lines[i] = f'{env_var}="{api_key}"\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'{env_var}="{api_key}"\n')
        
        # Write back
        with open(self.env_file_path, 'w') as f:
            f.writelines(lines)
        
        # Restrict permissions
        try:
            os.chmod(self.env_file_path, 0o600)
        except:
            pass
    
    def _remove_from_env_file(self, env_var: str):
        """Remove API key from .env file"""
        
        if not self.env_file_path.exists():
            return
        
        with open(self.env_file_path, 'r') as f:
            lines = f.readlines()
        
        # Filter out the line
        lines = [line for line in lines if not line.strip().startswith(f"{env_var}=")]
        
        with open(self.env_file_path, 'w') as f:
            f.writelines(lines)
    
    def _read_from_encrypted_file(self, env_var: str) -> Optional[str]:
        """Read API key from encrypted file"""
        
        if not self.encrypted_file_path.exists() or not self.cipher:
            return None
        
        try:
            with open(self.encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            keys_dict = json.loads(decrypted_data.decode())
            
            return keys_dict.get(env_var)
            
        except Exception as e:
            print(f"Warning: Failed to read encrypted file: {e}")
            return None
    
    def _write_to_encrypted_file(self, env_var: str, api_key: str):
        """Write API key to encrypted file"""
        
        if not self.cipher:
            raise ValueError("Encryption not configured")
        
        # Read existing keys
        keys_dict = {}
        if self.encrypted_file_path.exists():
            try:
                with open(self.encrypted_file_path, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                keys_dict = json.loads(decrypted_data.decode())
            except:
                pass
        
        # Update key
        keys_dict[env_var] = api_key
        
        # Encrypt and write
        json_data = json.dumps(keys_dict).encode()
        encrypted_data = self.cipher.encrypt(json_data)
        
        with open(self.encrypted_file_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Restrict permissions
        try:
            os.chmod(self.encrypted_file_path, 0o600)
        except:
            pass
    
    def _remove_from_encrypted_file(self, env_var: str):
        """Remove API key from encrypted file"""
        
        if not self.encrypted_file_path.exists() or not self.cipher:
            return
        
        try:
            with open(self.encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            keys_dict = json.loads(decrypted_data.decode())
            
            if env_var in keys_dict:
                del keys_dict[env_var]
                
                # Write back
                json_data = json.dumps(keys_dict).encode()
                encrypted_data = self.cipher.encrypt(json_data)
                
                with open(self.encrypted_file_path, 'wb') as f:
                    f.write(encrypted_data)
                    
        except Exception as e:
            print(f"Warning: Failed to remove from encrypted file: {e}")
    
    def prompt_for_api_key(self, provider: str, 
                          store: bool = True,
                          storage: str = "keyring") -> Optional[str]:
        """
        Prompt user to enter API key interactively
        
        Args:
            provider: Provider name
            store: Whether to store the key
            storage: Storage method to use
        
        Returns:
            The entered API key or None
        """
        
        provider = provider.upper()
        
        print(f"\n🔑 API Key Setup for {provider}")
        print(f"=" * 50)
        
        # Provide instructions based on provider
        instructions = {
            "ANTHROPIC": "Get your key at: https://console.anthropic.com/settings/keys",
            "OPENAI": "Get your key at: https://platform.openai.com/api-keys",
            "DEEPSEEK": "Get your key at: https://platform.deepseek.com/api_keys",
            "HUGGINGFACE": "Get your key at: https://huggingface.co/settings/tokens",
            "COHERE": "Get your key at: https://dashboard.cohere.com/api-keys",
            "GOOGLE": "Get your key at: https://makersuite.google.com/app/apikey"
        }
        
        if provider in instructions:
            print(f"ℹ️  {instructions[provider]}")
        
        print()
        
        # Prompt for key (hidden input)
        api_key = getpass.getpass(f"Enter your {provider} API key (input hidden): ").strip()
        
        if not api_key:
            print("❌ No API key entered")
            return None
        
        # Validate key if possible
        print("\n⏳ Validating API key...")
        if self.validate_api_key(provider, api_key):
            print("✅ API key is valid!")
            
            # Store key if requested
            if store:
                if self.set_api_key(provider, api_key, storage):
                    print(f"✅ API key stored using {storage} method")
                else:
                    print("⚠️  Failed to store API key, but you can still use it this session")
            
            return api_key
        else:
            print("❌ API key validation failed")
            
            # Ask if user wants to use it anyway
            use_anyway = input("Use this key anyway? (y/N): ").strip().lower()
            if use_anyway == 'y':
                if store:
                    self.set_api_key(provider, api_key, storage)
                return api_key
            
            return None
    
    def interactive_setup(self):
        """Interactive setup for all API keys"""
        
        print("\n" + "="*60)
        print("🔑 HypatiaX API Key Configuration")
        print("="*60)
        
        print("\nConfigured providers:")
        configured = self.list_configured_providers()
        
        for provider, has_key in configured.items():
            status = "✅ Configured" if has_key else "❌ Not configured"
            print(f"  {provider}: {status}")
        
        print("\n" + "="*60)
        
        # Ask which providers to configure
        print("\nWhich providers would you like to configure?")
        print("1. Anthropic Claude (Recommended for 2025)")
        print("2. OpenAI GPT")
        print("3. DeepSeek")
        print("4. Cohere")
        print("5. Google Gemini")
        print("6. HuggingFace")
        print("7. All of the above")
        print("8. Skip")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        providers_to_setup = []
        if choice == "1":
            providers_to_setup = ["ANTHROPIC"]
        elif choice == "2":
            providers_to_setup = ["OPENAI"]
        elif choice == "3":
            providers_to_setup = ["DEEPSEEK"]
        elif choice == "4":
            providers_to_setup = ["COHERE"]
        elif choice == "5":
            providers_to_setup = ["GOOGLE"]
        elif choice == "6":
            providers_to_setup = ["HUGGINGFACE"]
        elif choice == "7":
            providers_to_setup = ["ANTHROPIC", "OPENAI", "DEEPSEEK", "COHERE", "GOOGLE", "HUGGINGFACE"]
        
        # Storage method
        print("\nChoose storage method:")
        print("1. System Keyring (Most Secure) - Recommended")
        print("2. .env file (Convenient)")
        print("3. Encrypted file")
        
        storage_choice = input("\nEnter choice (1-3): ").strip()
        storage_map = {"1": "keyring", "2": "env", "3": "encrypted"}
        storage = storage_map.get(storage_choice, "keyring")
        
        # Setup each provider
        for provider in providers_to_setup:
            if not configured.get(provider):
                self.prompt_for_api_key(provider, store=True, storage=storage)
        
        print("\n✅ Setup complete!")
        print(f"\nConfigured providers: {sum(1 for v in self.list_configured_providers().values() if v)}/{len(self.PROVIDERS)}")


def main():
    """CLI interface for API key management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage HypatiaX API keys")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Setup command
    subparsers.add_parser('setup', help='Interactive API key setup')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get API key')
    get_parser.add_argument('provider', help='Provider name (e.g., ANTHROPIC)')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set API key')
    set_parser.add_argument('provider', help='Provider name')
    set_parser.add_argument('--storage', choices=['keyring', 'env', 'encrypted'], 
                           default='keyring', help='Storage method')
    
    # Delete command
    del_parser = subparsers.add_parser('delete', help='Delete API key')
    del_parser.add_argument('provider', help='Provider name')
    
    # List command
    subparsers.add_parser('list', help='List configured providers')
    
    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate API key')
    val_parser.add_argument('provider', help='Provider name')
    
    args = parser.parse_args()
    
    manager = APIKeyManager()
    
    if args.command == 'setup':
        manager.interactive_setup()
        
    elif args.command == 'get':
        key = manager.get_api_key(args.provider)
        if key:
            # Mask key for security
            masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
            print(f"API key for {args.provider}: {masked}")
        else:
            print(f"❌ No API key found for {args.provider}")
            print(f"\nRun 'python api_key_manager.py setup' to configure")
    
    elif args.command == 'set':
        key = manager.prompt_for_api_key(args.provider, store=True, storage=args.storage)
        if not key:
            print("❌ Failed to set API key")
    
    elif args.command == 'delete':
        if manager.delete_api_key(args.provider):
            print(f"✅ Deleted API key for {args.provider}")
        else:
            print(f"❌ Failed to delete API key for {args.provider}")
    
    elif args.command == 'list':
        print("\n📋 Configured API Keys:")
        print("="*50)
        configured = manager.list_configured_providers()
        for provider, has_key in configured.items():
            status = "✅ Configured" if has_key else "❌ Not configured"
            print(f"  {provider}: {status}")
        print()
    
    elif args.command == 'validate':
        print(f"⏳ Validating {args.provider} API key...")
        if manager.validate_api_key(args.provider):
            print(f"✅ {args.provider} API key is valid!")
        else:
            print(f"❌ {args.provider} API key validation failed")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

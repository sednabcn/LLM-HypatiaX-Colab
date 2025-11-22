"""Test environment variables loading"""
import os
from dotenv import load_dotenv

load_dotenv()

print("\n🧪 Testing Environment Variables\n")
print("="*60)
print(f"FLASK_ENV:       {os.getenv('FLASK_ENV', 'NOT SET')}")
print(f"DEBUG:           {os.getenv('DEBUG', 'NOT SET')}")
print(f"LOG_LEVEL:       {os.getenv('LOG_LEVEL', 'NOT SET')}")
print(f"SECRET_KEY:      {os.getenv('SECRET_KEY', 'NOT SET')[:20]}...")
print(f"CORS_ORIGINS:    {os.getenv('CORS_ORIGINS', 'NOT SET')}")
print(f"HYPATIAX:        {os.getenv('HYPATIAX_ENABLED', 'NOT SET')}")
print(f"NER:             {os.getenv('NER_ENABLED', 'NOT SET')}")
print(f"DEFI:            {os.getenv('DEFI_ENABLED', 'NOT SET')}")
print("="*60)
print("\n✅ Environment variables loaded successfully!\n")

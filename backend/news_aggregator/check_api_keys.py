# check_api_keys.py
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

print("=== CHECKING API KEYS ===")
print(f"SECRET_KEY loaded: {'Yes' if hasattr(settings, 'SECRET_KEY') else 'No'}")
print(f"NEWS_API_KEY: {getattr(settings, 'NEWS_API_KEY', 'NOT SET')}")
print(f"GOOGLE_NEWS_API_KEY: {getattr(settings, 'GOOGLE_NEWS_API_KEY', 'NOT SET')}")

# Check if .env file exists
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
print(f"\n.env file exists: {os.path.exists(env_path)}")
if os.path.exists(env_path):
    print(f".env file path: {env_path}")
    with open(env_path, 'r') as f:
        content = f.read()
        print("Content preview:")
        print(content[:200] + "..." if len(content) > 200 else content)
else:
    print("❌ .env file NOT FOUND!")

# Test direct environment variables
print(f"\nDirect environment variables:")
print(f"NEWS_API_KEY from os.environ: {os.environ.get('NEWS_API_KEY', 'NOT SET')}")
print(f"GOOGLE_NEWS_API_KEY from os.environ: {os.environ.get('GOOGLE_NEWS_API_KEY', 'NOT SET')}")
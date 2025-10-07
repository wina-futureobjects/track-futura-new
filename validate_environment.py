#!/usr/bin/env python3
"""
TrackFutura Environment Validation Script
Validates that all environment variables are properly configured
"""

import os
import sys

def validate_environment():
    """Validate all required environment variables"""
    print("🔍 TrackFutura Environment Validation")
    print("=" * 50)
    
    # Required environment variables
    required_vars = {
        'DJANGO_SETTINGS_MODULE': 'Django settings module',
        'SECRET_KEY': 'Django secret key',
        'APIFY_API_TOKEN': 'Apify API token for data scraping',
        'OPENAI_API_KEY': 'OpenAI API key for sentiment analysis',
    }
    
    # Optional environment variables
    optional_vars = {
        'PINECONE_API_KEY': 'Pinecone API key for vector database',
        'BRIGHTDATA_API_KEY': 'BrightData API key for data collection',
        'BRIGHTDATA_WEBHOOK_TOKEN': 'BrightData webhook authentication',
        'DATABASE_NAME': 'Database name',
        'DATABASE_USER': 'Database user',
        'DATABASE_PASSWORD': 'Database password',
        'EMAIL_HOST_USER': 'Email configuration',
        'EMAIL_HOST_PASSWORD': 'Email password',
    }
    
    # Check if .env file exists
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ Found {env_file} file")
        # Load .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ Loaded environment variables from .env")
        except ImportError:
            print("⚠️  python-dotenv not installed, reading from system environment")
    else:
        print(f"❌ {env_file} file not found")
        print("💡 Copy .env.example to .env and configure your values")
    
    print("\n📋 Required Variables:")
    print("-" * 30)
    
    missing_required = []
    
    for var, description in required_vars.items():
        value = os.getenv(var, '')
        if value:
            # Hide sensitive values
            if 'KEY' in var or 'TOKEN' in var or 'SECRET' in var:
                display_value = f"{value[:10]}..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set ({description})")
            missing_required.append(var)
    
    print("\n📋 Optional Variables:")
    print("-" * 30)
    
    for var, description in optional_vars.items():
        value = os.getenv(var, '')
        if value:
            if 'KEY' in var or 'TOKEN' in var or 'PASSWORD' in var:
                display_value = f"{value[:10]}..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"⚪ {var}: Not set ({description})")
    
    print("\n" + "=" * 50)
    
    if missing_required:
        print("❌ Validation Failed!")
        print(f"Missing required variables: {', '.join(missing_required)}")
        print("\n💡 To fix this:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env and add your API keys")
        print("3. Run this script again")
        return False
    else:
        print("✅ Environment validation passed!")
        print("🚀 Your TrackFutura project is ready to run")
        return True

def check_project_structure():
    """Check if project structure is correct"""
    print("\n🏗️  Project Structure Check")
    print("-" * 30)
    
    required_paths = [
        'backend/',
        'frontend/',
        'backend/manage.py',
        'frontend/package.json',
        '.env.example',
        'docker-compose.yml',
        'README.md'
    ]
    
    missing_paths = []
    
    for path in required_paths:
        if os.path.exists(path):
            print(f"✅ {path}")
        else:
            print(f"❌ {path}")
            missing_paths.append(path)
    
    if missing_paths:
        print(f"\n⚠️  Missing paths: {', '.join(missing_paths)}")
        return False
    else:
        print("\n✅ Project structure is correct")
        return True

def check_no_hardcoded_keys():
    """Check for any remaining hardcoded API keys"""
    print("\n🔒 Security Check")
    print("-" * 30)
    
    # Check if any obvious hardcoded keys exist
    suspicious_patterns = [
        'apify_api_',
        'sk-',  # OpenAI keys
        'pcsk_'  # Pinecone keys
    ]
    
    print("Checking for hardcoded API keys...")
    
    # Simple check in main files
    files_to_check = [
        'backend/config/settings.py',
        '.env',
        'README.md'
    ]
    
    found_hardcoded = False
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in suspicious_patterns:
                        if pattern in content and 'your-' not in content and 'example' not in content:
                            # Check if it's not in a comment or example
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if pattern in line and not line.strip().startswith('#') and 'your-' not in line:
                                    print(f"⚠️  Possible hardcoded key in {file_path}:{i+1}")
                                    found_hardcoded = True
            except Exception as e:
                print(f"⚠️  Could not check {file_path}: {e}")
    
    if not found_hardcoded:
        print("✅ No hardcoded API keys detected")
        return True
    else:
        print("❌ Possible hardcoded keys found - please review")
        return False

def main():
    """Main validation function"""
    env_valid = validate_environment()
    structure_valid = check_project_structure()
    security_valid = check_no_hardcoded_keys()
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    if env_valid and structure_valid and security_valid:
        print("🎉 All checks passed!")
        print("✅ Environment configured correctly")
        print("✅ Project structure is valid")
        print("✅ No security issues detected")
        print("\n🚀 Ready to start development:")
        print("   Backend:  cd backend && python manage.py runserver 8080")
        print("   Frontend: cd frontend && npm run dev")
        return True
    else:
        print("❌ Some checks failed")
        if not env_valid:
            print("   - Fix environment variable configuration")
        if not structure_valid:
            print("   - Fix project structure issues")
        if not security_valid:
            print("   - Review security concerns")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Google Ads Authentication Setup Script
Guides user through OAuth2 setup and credential configuration
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from auth.credentials_manager import CredentialsManager

def setup_environment():
    """Setup environment variables and configuration"""
    config_dir = Path(__file__).parent.parent / "config"
    env_file = config_dir / ".env"
    env_example = config_dir / ".env.example"
    
    print("🔧 Google Ads Authentication Setup")
    print("=" * 50)
    
    # Check if .env file exists
    if not env_file.exists():
        if env_example.exists():
            print(f"📋 Copying .env.example to .env")
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
        else:
            print("❌ .env.example file not found!")
            return False
    
    # Load environment variables
    load_dotenv(env_file)
    
    print(f"📁 Configuration directory: {config_dir}")
    print(f"📄 Environment file: {env_file}")
    
    # Check required environment variables
    required_vars = [
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET", 
        "GOOGLE_ADS_DEVELOPER_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value or value.startswith("your_"):
            missing_vars.append(var)
    
    if missing_vars:
        print("\n❌ Missing or incomplete environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print(f"\n📝 Please edit {env_file} and set the required values.")
        print("\n📚 Setup instructions:")
        print("   1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print("   2. Create OAuth2 credentials (Desktop Application)")
        print("   3. Get Google Ads Developer Token from: https://ads.google.com/")
        print("   4. Update the .env file with your actual values")
        return False
    
    print("\n✅ Environment variables configured!")
    return True

def test_authentication():
    """Test the authentication setup"""
    print("\n🔐 Testing Authentication...")
    print("-" * 30)
    
    try:
        # Initialize credentials manager
        creds_manager = CredentialsManager()
        
        # Get credentials (this will trigger OAuth flow if needed)
        print("🌐 Getting OAuth2 credentials...")
        creds = creds_manager.get_credentials()
        
        if creds and creds.valid:
            print("✅ Authentication successful!")
            print(f"📧 Authenticated user: {getattr(creds, 'id_token', {}).get('email', 'Unknown')}")
            return True
        else:
            print("❌ Authentication failed!")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting Google Ads API Setup...")
    
    # Step 1: Setup environment
    if not setup_environment():
        print("\n❌ Setup failed. Please configure your environment variables.")
        sys.exit(1)
    
    # Step 2: Test authentication
    if not test_authentication():
        print("\n❌ Authentication failed. Please check your credentials.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Run list_accounts.py to see your available accounts")
    print("   2. Use the account IDs in other scripts")
    print("   3. Start managing your Google Ads campaigns!")

if __name__ == "__main__":
    main()

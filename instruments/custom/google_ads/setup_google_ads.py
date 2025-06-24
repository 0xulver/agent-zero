#!/usr/bin/env python3
"""
Google Ads API Complete Setup Script

This self-contained script handles the complete Google Ads API setup:
1. Installs required dependencies
2. Generates refresh token
3. Tests the connection
4. Lists accessible accounts
"""

import sys
import subprocess
import os

def install_package(package_name):
    """Install a Python package using pip."""
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', package_name, '--quiet'
        ])
        return True
    except subprocess.CalledProcessError:
        return False

def ensure_dependencies():
    """Ensure all required dependencies are installed."""
    print("🔄 Checking and installing dependencies...")
    
    dependencies = [
        'PyYAML',
        'google-ads>=24.0.0',
        'google-auth-oauthlib>=1.0.0'
    ]
    
    for dep in dependencies:
        print(f"   Installing {dep}...")
        if not install_package(dep):
            print(f"❌ Failed to install {dep}")
            return False
    
    print("✅ All dependencies installed successfully!")
    return True

def load_config():
    """Load the google-ads.yaml configuration file."""
    import yaml
    
    config_file = "/a0/google-ads.yaml"
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        return config, config_file
    except FileNotFoundError:
        print(f"❌ Configuration file {config_file} not found.")
        return None, config_file
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None, config_file

def save_config(config, config_file):
    """Save configuration back to YAML file."""
    import yaml
    
    try:
        with open(config_file, 'w') as file:
            yaml.dump(config, file, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False

def generate_refresh_token():
    """Generate refresh token using OAuth2 flow."""
    import webbrowser
    from urllib.parse import urlparse, parse_qs
    from google_auth_oauthlib.flow import Flow
    
    print("\n🔑 Generating Refresh Token")
    print("=" * 30)
    
    config, config_file = load_config()
    if not config:
        return False
    
    # Check required fields
    required_fields = ['client_id', 'client_secret']
    for field in required_fields:
        if not config.get(field):
            print(f"❌ Missing {field} in configuration")
            return False
    
    # Create OAuth2 flow
    client_config = {
        "web": {
            "client_id": config['client_id'],
            "client_secret": config['client_secret'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080"]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/adwords'],
        redirect_uri="http://localhost:8080"
    )
    
    # Generate authorization URL
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    print("📋 Please follow these steps:")
    print("1. A browser window will open (or copy the URL below)")
    print("2. Sign in with your Google Ads account")
    print("3. Grant permissions")
    print("4. Copy the full redirect URL from your browser")
    print()
    print(f"Authorization URL: {auth_url}")
    print()
    
    # Try to open browser
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened automatically")
    except:
        print("⚠️  Could not open browser automatically")
    
    print()
    redirect_url = input("Paste the full redirect URL here: ").strip()
    
    if not redirect_url.startswith('http://localhost:8080'):
        print("❌ Invalid redirect URL")
        return False
    
    try:
        # Extract authorization code
        parsed_url = urlparse(redirect_url)
        auth_code = parse_qs(parsed_url.query).get('code', [None])[0]
        
        if not auth_code:
            print("❌ Could not extract authorization code")
            return False
        
        # Exchange for tokens
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        if credentials.refresh_token:
            config['refresh_token'] = credentials.refresh_token
            if save_config(config, config_file):
                print("✅ Refresh token generated and saved!")
                return True
        else:
            print("❌ No refresh token received")
            return False
            
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return False

def test_connection():
    """Test the Google Ads API connection."""
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    
    print("\n🔍 Testing API Connection")
    print("=" * 25)
    
    config, config_file = load_config()
    if not config:
        return False
    
    # Check if refresh token exists
    if not config.get('refresh_token') or config.get('refresh_token') == 'INSERT_REFRESH_TOKEN_HERE':
        print("❌ Refresh token not found. Please generate it first.")
        return False
    
    try:
        # Initialize client
        client = GoogleAdsClient.load_from_storage(config_file)
        
        # Test connection
        customer_service = client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()
        
        print("✅ Connection successful!")
        print("\n📋 Accessible Customer Accounts:")
        
        if accessible_customers.resource_names:
            for i, resource_name in enumerate(accessible_customers.resource_names, 1):
                customer_id = resource_name.split('/')[-1]
                print(f"   {i}. Customer ID: {customer_id}")
        else:
            print("   No accessible customers found")
        
        return True
        
    except GoogleAdsException as ex:
        print(f"❌ Google Ads API Error: {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"   - {error.message}")
        return False
        
    except Exception as ex:
        print(f"❌ Connection error: {ex}")
        return False

def main():
    """Main setup function."""
    print("🚀 Google Ads API Setup")
    print("=" * 25)
    
    # Step 1: Install dependencies
    if not ensure_dependencies():
        print("❌ Setup failed: Could not install dependencies")
        return False
    
    # Step 2: Check if refresh token already exists
    config, _ = load_config()
    if config and config.get('refresh_token') and config.get('refresh_token') != 'INSERT_REFRESH_TOKEN_HERE':
        print("✅ Refresh token already exists, skipping generation")
    else:
        # Step 3: Generate refresh token
        if not generate_refresh_token():
            print("❌ Setup failed: Could not generate refresh token")
            return False
    
    # Step 4: Test connection
    if test_connection():
        print("\n🎉 Google Ads API setup completed successfully!")
        print("You can now use the Google Ads integration with Agent Zero.")
        return True
    else:
        print("❌ Setup failed: Connection test failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

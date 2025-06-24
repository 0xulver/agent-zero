#!/usr/bin/env python3
"""
Google Ads API Connection Test

This script tests the connection to the Google Ads API using the credentials
stored in google-ads.yaml file.
"""

import sys
import subprocess

# Check and install dependencies
def install_dependencies():
    """Install required packages if not available."""
    required_packages = [
        'PyYAML',
        'google-ads'
    ]

    for package in required_packages:
        try:
            if package == 'google-ads':
                from google.ads.googleads.client import GoogleAdsClient
            else:
                __import__(package.lower().replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

# Install dependencies first
install_dependencies()

import yaml
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Configuration - multiple possible locations
import os
CONFIG_PATHS = [
    "/a0/google-ads.yaml",           # Primary location when run by Agent Zero
    "google-ads.yaml",               # Current directory (for testing)
    "/root/google-ads.yaml",         # Home directory in container
    os.path.expanduser("~/google-ads.yaml")  # User home directory
]

def load_config():
    """Load the google-ads.yaml configuration file from multiple possible locations."""
    for config_path in CONFIG_PATHS:
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            print(f"✅ Loaded configuration from {config_path}")
            return config, config_path
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"❌ Error loading config from {config_path}: {e}")
            continue

    print(f"❌ Configuration file not found in any of these locations:")
    for path in CONFIG_PATHS:
        print(f"   - {path}")
    return None, None

def test_connection():
    """Test the Google Ads API connection."""
    print("Google Ads API Connection Test")
    print("=" * 30)
    
    # Load configuration
    config, config_file = load_config()
    if not config:
        return False
    
    # Check required fields
    required_fields = ['developer_token', 'client_id', 'client_secret', 'refresh_token', 'login_customer_id']
    missing_fields = []
    
    for field in required_fields:
        if not config.get(field) or config.get(field) == f"INSERT_{field.upper()}_HERE":
            missing_fields.append(field)
    
    if missing_fields:
        print("❌ Missing or incomplete configuration fields:")
        for field in missing_fields:
            print(f"   - {field}")
        print("\nPlease complete your google-ads.yaml configuration.")
        if 'refresh_token' in missing_fields:
            print("Run generate_refresh_token.py to generate the refresh token.")
        return False
    
    print("✅ Configuration file found and appears complete.")
    print(f"   Developer Token: {config['developer_token'][:10]}...")
    print(f"   Client ID: {config['client_id'][:20]}...")
    print(f"   Login Customer ID: {config['login_customer_id']}")
    print()
    
    try:
        print("🔄 Initializing Google Ads client...")
        
        # Initialize the Google Ads client
        googleads_client = GoogleAdsClient.load_from_storage(config_file)
        
        print("✅ Client initialized successfully.")
        print()
        
        print("🔄 Testing API connection by listing accessible customers...")
        
        # Test the connection by listing accessible customers
        customer_service = googleads_client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()
        
        print("✅ API connection successful!")
        print()
        print("📋 Accessible customer accounts:")
        
        if accessible_customers.resource_names:
            for i, resource_name in enumerate(accessible_customers.resource_names, 1):
                customer_id = resource_name.split('/')[-1]
                print(f"   {i}. Customer ID: {customer_id}")
        else:
            print("   No accessible customers found.")
        
        print()
        print("🎉 Connection test completed successfully!")
        print("Your Google Ads API integration is ready to use.")
        
        return True
        
    except GoogleAdsException as ex:
        print("❌ Google Ads API Error:")
        print(f"   Request ID: {ex.request_id}")
        print(f"   Status: {ex.error.code().name}")
        print("   Errors:")
        for error in ex.failure.errors:
            print(f"   - {error.message}")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"     Field: {field_path_element.field_name}")
        
        print("\n💡 Common solutions:")
        print("   - Verify your developer token is approved and active")
        print("   - Check that your OAuth2 credentials are correct")
        print("   - Ensure your login_customer_id has access to the accounts")
        print("   - Verify your refresh token is valid (regenerate if needed)")
        
        return False
        
    except Exception as ex:
        print(f"❌ Unexpected error: {ex}")
        print("\n💡 This might be due to:")
        print("   - Network connectivity issues")
        print("   - Invalid configuration format")
        print("   - Missing dependencies (run: pip install google-ads)")
        
        return False

def main():
    """Main function."""
    success = test_connection()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

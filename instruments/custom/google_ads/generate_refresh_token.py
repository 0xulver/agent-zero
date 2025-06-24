#!/usr/bin/env python3
"""
Google Ads API Refresh Token Generator

This script generates a refresh token for the Google Ads API by following the OAuth2 flow.
It reads the client credentials from google-ads.yaml and updates the file with the refresh token.
"""

import os
import sys
import yaml
import webbrowser
from urllib.parse import urlparse, parse_qs
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# Configuration
CONFIG_FILE = "/a0/google-ads.yaml"
SCOPES = ['https://www.googleapis.com/auth/adwords']

def load_config():
    """Load the google-ads.yaml configuration file."""
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file {CONFIG_FILE} not found.")
        print("Please ensure you have created the google-ads.yaml file with your credentials.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)

def save_config(config):
    """Save the updated configuration back to the YAML file."""
    try:
        with open(CONFIG_FILE, 'w') as file:
            yaml.dump(config, file, default_flow_style=False, sort_keys=False)
        print(f"Configuration updated successfully in {CONFIG_FILE}")
    except Exception as e:
        print(f"Error saving configuration: {e}")
        sys.exit(1)

def generate_refresh_token():
    """Generate a refresh token using OAuth2 flow."""
    print("Google Ads API Refresh Token Generator")
    print("=" * 40)
    
    # Load configuration
    config = load_config()
    
    # Check if required fields are present
    required_fields = ['client_id', 'client_secret']
    for field in required_fields:
        if not config.get(field):
            print(f"Error: {field} is missing from the configuration file.")
            sys.exit(1)
    
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
        scopes=SCOPES,
        redirect_uri="http://localhost:8080"
    )
    
    # Generate authorization URL
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    print("\nStep 1: Authorization")
    print("-" * 20)
    print("Opening your web browser for Google OAuth2 authorization...")
    print(f"If the browser doesn't open automatically, please visit this URL:")
    print(f"\n{auth_url}\n")
    
    # Try to open browser automatically
    try:
        webbrowser.open(auth_url)
    except Exception:
        print("Could not open browser automatically.")
    
    print("After authorizing the application:")
    print("1. You'll be redirected to a localhost URL")
    print("2. Copy the ENTIRE URL from your browser's address bar")
    print("3. Paste it below")
    print()
    
    # Get authorization response
    while True:
        auth_response = input("Paste the full redirect URL here: ").strip()
        if auth_response.startswith('http://localhost:8080'):
            break
        print("Please paste the complete URL starting with 'http://localhost:8080'")
    
    try:
        # Extract authorization code from URL
        parsed_url = urlparse(auth_response)
        auth_code = parse_qs(parsed_url.query).get('code', [None])[0]
        
        if not auth_code:
            print("Error: Could not extract authorization code from URL.")
            sys.exit(1)
        
        print("\nStep 2: Exchanging authorization code for tokens...")
        print("-" * 50)
        
        # Exchange authorization code for tokens
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        if credentials.refresh_token:
            print("✅ Success! Refresh token generated.")
            print(f"Refresh Token: {credentials.refresh_token}")
            
            # Update configuration with refresh token
            config['refresh_token'] = credentials.refresh_token
            save_config(config)
            
            print("\n🎉 Setup Complete!")
            print("Your google-ads.yaml file has been updated with the refresh token.")
            print("You can now test the connection using test_connection.py")
            
        else:
            print("❌ Error: No refresh token received.")
            print("This might happen if you've already authorized this application.")
            print("Try revoking access at https://myaccount.google.com/permissions and run this script again.")
            
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_refresh_token()

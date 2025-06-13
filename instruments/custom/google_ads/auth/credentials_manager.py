"""
Google Ads OAuth2 Credentials Manager
Handles authentication and token refresh for Google Ads API
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Ads API scopes
SCOPES = ['https://www.googleapis.com/auth/adwords']

class CredentialsManager:
    """Manages Google Ads API OAuth2 credentials"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(__file__).parent.parent / "config"
        self.token_path = self.config_dir / "google_ads_token.json"
        self.client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
        self.client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
        
    def get_credentials(self) -> Credentials:
        """
        Get valid OAuth2 credentials, refreshing if necessary
        
        Returns:
            Valid Google OAuth2 credentials
            
        Raises:
            ValueError: If required environment variables are not set
            Exception: If authentication fails
        """
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET must be set. "
                "Check your .env file in the config directory."
            )
        
        creds = None
        
        # Load existing credentials if they exist
        if self.token_path.exists():
            try:
                logger.info(f"Loading existing credentials from {self.token_path}")
                with open(self.token_path, 'r') as f:
                    creds_data = json.load(f)
                    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Error loading existing credentials: {e}")
                creds = None
        
        # Check if credentials are valid or can be refreshed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Refreshing expired credentials")
                    creds.refresh(Request())
                    logger.info("Credentials successfully refreshed")
                except RefreshError as e:
                    logger.warning(f"Error refreshing credentials: {e}")
                    creds = None
            
            # If we still don't have valid credentials, run OAuth flow
            if not creds:
                logger.info("Starting OAuth2 authentication flow")
                creds = self._run_oauth_flow()
            
            # Save the credentials
            self._save_credentials(creds)
        
        return creds
    
    def _run_oauth_flow(self) -> Credentials:
        """Run the OAuth2 flow to get new credentials"""
        client_config = {
            "installed": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
            }
        }
        
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0)
        logger.info("OAuth2 flow completed successfully")
        return creds
    
    def _save_credentials(self, creds: Credentials) -> None:
        """Save credentials to file"""
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Saving credentials to {self.token_path}")
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())
        except Exception as e:
            logger.warning(f"Could not save credentials: {e}")
    
    def clear_credentials(self) -> None:
        """Clear saved credentials (force re-authentication)"""
        if self.token_path.exists():
            self.token_path.unlink()
            logger.info("Credentials cleared")
    
    def get_headers(self, creds: Credentials) -> dict:
        """
        Get headers for Google Ads API requests
        
        Args:
            creds: Valid OAuth2 credentials
            
        Returns:
            Dictionary of headers for API requests
        """
        developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
        if not developer_token:
            raise ValueError("GOOGLE_ADS_DEVELOPER_TOKEN environment variable not set")
        
        headers = {
            'Authorization': f'Bearer {creds.token}',
            'developer-token': developer_token,
            'content-type': 'application/json'
        }
        
        # Add login customer ID if specified
        login_customer_id = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
        if login_customer_id:
            # Format customer ID (remove dashes, ensure 10 digits)
            formatted_id = ''.join(char for char in login_customer_id if char.isdigit())
            headers['login-customer-id'] = formatted_id.zfill(10)
        
        return headers

"""
Google Ads API Client
Main client for interacting with Google Ads API
"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..auth.credentials_manager import CredentialsManager

# Configure logging
logger = logging.getLogger(__name__)

class GoogleAdsClient:
    """Main client for Google Ads API interactions"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(__file__).parent.parent / "config"
        self.api_version = os.environ.get("GOOGLE_ADS_API_VERSION", "v19")
        self.base_url = f"https://googleads.googleapis.com/{self.api_version}"
        self.credentials_manager = CredentialsManager(self.config_dir)
        
    def format_customer_id(self, customer_id: Union[str, int]) -> str:
        """
        Format customer ID to ensure it's 10 digits without dashes
        
        Args:
            customer_id: Customer ID in any format
            
        Returns:
            Formatted customer ID (10 digits, no dashes)
        """
        # Convert to string and remove non-digit characters
        customer_id = str(customer_id)
        customer_id = customer_id.replace('\"', '').replace('"', '')
        customer_id = ''.join(char for char in customer_id if char.isdigit())
        
        # Ensure it's 10 digits with leading zeros if needed
        return customer_id.zfill(10)
    
    def list_accounts(self) -> Dict:
        """
        List all accessible Google Ads accounts
        
        Returns:
            Dictionary containing account information
        """
        try:
            creds = self.credentials_manager.get_credentials()
            headers = self.credentials_manager.get_headers(creds)
            
            url = f"{self.base_url}/customers:listAccessibleCustomers"
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API Error: {response.text}",
                    "status_code": response.status_code
                }
            
            data = response.json()
            accounts = []
            
            if data.get('resourceNames'):
                for resource_name in data['resourceNames']:
                    customer_id = resource_name.split('/')[-1]
                    formatted_id = self.format_customer_id(customer_id)
                    accounts.append({
                        "customer_id": formatted_id,
                        "resource_name": resource_name
                    })
            
            return {
                "success": True,
                "accounts": accounts,
                "count": len(accounts)
            }
            
        except Exception as e:
            logger.error(f"Error listing accounts: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_gaql_query(self, customer_id: Union[str, int], query: str) -> Dict:
        """
        Execute a GAQL (Google Ads Query Language) query
        
        Args:
            customer_id: Google Ads customer ID
            query: GAQL query string
            
        Returns:
            Dictionary containing query results
        """
        try:
            creds = self.credentials_manager.get_credentials()
            headers = self.credentials_manager.get_headers(creds)
            
            formatted_customer_id = self.format_customer_id(customer_id)
            url = f"{self.base_url}/customers/{formatted_customer_id}/googleAds:search"
            
            payload = {"query": query}
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API Error: {response.text}",
                    "status_code": response.status_code,
                    "customer_id": formatted_customer_id,
                    "query": query
                }
            
            data = response.json()
            
            return {
                "success": True,
                "results": data.get('results', []),
                "customer_id": formatted_customer_id,
                "query": query,
                "total_results": len(data.get('results', []))
            }
            
        except Exception as e:
            logger.error(f"Error executing GAQL query: {e}")
            return {
                "success": False,
                "error": str(e),
                "customer_id": self.format_customer_id(customer_id),
                "query": query
            }
    
    def get_campaign_performance(self, customer_id: Union[str, int], days: int = 30) -> Dict:
        """
        Get campaign performance metrics
        
        Args:
            customer_id: Google Ads customer ID
            days: Number of days to look back
            
        Returns:
            Dictionary containing campaign performance data
        """
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.average_cpc
            FROM campaign
            WHERE segments.date DURING LAST_{days}DAYS
            ORDER BY metrics.cost_micros DESC
            LIMIT 50
        """
        
        return self.execute_gaql_query(customer_id, query)
    
    def get_ad_performance(self, customer_id: Union[str, int], days: int = 30) -> Dict:
        """
        Get ad performance metrics
        
        Args:
            customer_id: Google Ads customer ID
            days: Number of days to look back
            
        Returns:
            Dictionary containing ad performance data
        """
        query = f"""
            SELECT
                ad_group_ad.ad.id,
                ad_group_ad.ad.name,
                ad_group_ad.status,
                campaign.name,
                ad_group.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions
            FROM ad_group_ad
            WHERE segments.date DURING LAST_{days}DAYS
            ORDER BY metrics.impressions DESC
            LIMIT 50
        """
        
        return self.execute_gaql_query(customer_id, query)
    
    def get_account_currency(self, customer_id: Union[str, int]) -> Dict:
        """
        Get the account's default currency
        
        Args:
            customer_id: Google Ads customer ID
            
        Returns:
            Dictionary containing currency information
        """
        query = """
            SELECT
                customer.id,
                customer.currency_code
            FROM customer
            LIMIT 1
        """
        
        result = self.execute_gaql_query(customer_id, query)
        
        if result["success"] and result["results"]:
            customer_data = result["results"][0].get("customer", {})
            currency_code = customer_data.get("currencyCode", "Unknown")
            
            return {
                "success": True,
                "customer_id": result["customer_id"],
                "currency_code": currency_code
            }
        
        return result

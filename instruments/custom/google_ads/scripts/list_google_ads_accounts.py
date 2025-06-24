#!/usr/bin/env python3
"""
Lists accessible Google Ads accounts.
This script is a self-contained utility to avoid import issues in the main package.
"""
import yaml
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

CONFIG_FILE = "/a0/google-ads.yaml"

def list_accounts():
    """Loads config, connects to the API, and lists accessible accounts."""
    try:
        googleads_client = GoogleAdsClient.load_from_storage(CONFIG_FILE)
        customer_service = googleads_client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()

        print("📋 Accessible Google Ads Accounts:")
        if accessible_customers.resource_names:
            for i, resource_name in enumerate(accessible_customers.resource_names, 1):
                customer_id = resource_name.split('/')[-1]
                print(f"   {i}. Customer ID: {customer_id}")
        else:
            print("   No accessible customer accounts found.")

    except FileNotFoundError:
        print(f"❌ Error: Configuration file {CONFIG_FILE} not found.")
    except GoogleAdsException as ex:
        print(f"❌ An error occurred with the Google Ads API: {ex}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    list_accounts()

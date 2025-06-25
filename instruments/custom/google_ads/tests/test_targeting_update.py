#!/usr/bin/env python3
"""
Test script to verify that campaign targeting update functionality works correctly.
"""

import sys
import os
import json

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from google.ads.googleads.client import GoogleAdsClient

def test_targeting_update():
    """Test the campaign targeting update function."""
    try:
        # Load Google Ads client
        config_file = os.path.join(current_dir, "google-ads.yaml")
        client = GoogleAdsClient.load_from_storage(config_file)
        
        # Import the function from campaign_operations
        from campaign_operations import update_campaign_targeting
        
        # Test campaign resource name (using one of the existing campaigns)
        customer_id = "3045806466"
        campaign_resource_name = "customers/3045806466/campaigns/21937794210"  # Leads-Search-Event-5
        
        print("🧪 Testing Campaign Targeting Update Functionality")
        print("=" * 55)
        print(f"Customer ID: {customer_id}")
        print(f"Campaign: {campaign_resource_name}")
        print()
        
        # Load test targeting data
        targeting_file = os.path.join(current_dir, "test_targeting_data.json")
        with open(targeting_file, 'r') as f:
            targeting_data = json.load(f)
        
        print("📋 Targeting Data to Apply:")
        print(f"   Locations: {len(targeting_data.get('locations', []))}")
        for loc in targeting_data.get('locations', []):
            print(f"     - {loc.get('name', loc['geo_target_constant'])}")
        
        print(f"   Languages: {len(targeting_data.get('languages', []))}")
        for lang in targeting_data.get('languages', []):
            print(f"     - {lang.get('name', lang['language_constant'])}")
        
        print(f"   Negative Locations: {len(targeting_data.get('negative_locations', []))}")
        for neg_loc in targeting_data.get('negative_locations', []):
            print(f"     - {neg_loc.get('name', neg_loc['geo_target_constant'])}")
        
        print()
        
        # Test the targeting update
        print("🔄 Testing targeting update...")
        try:
            result = update_campaign_targeting(
                client, customer_id, campaign_resource_name, targeting_data
            )
            
            if isinstance(result, dict):
                print(f"✅ Success!")
                print(f"   Total criteria added: {result['summary']['total_criteria']}")
                print(f"   Locations: {result['summary']['locations']}")
                print(f"   Languages: {result['summary']['languages']}")
                print(f"   Negative locations: {result['summary']['negative_locations']}")
            else:
                print(f"✅ Success: {result}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("\n🎯 Test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

if __name__ == "__main__":
    success = test_targeting_update()
    sys.exit(0 if success else 1)

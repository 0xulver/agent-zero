#!/usr/bin/env python3
"""
Test script to verify that bidding strategy update functionality works correctly.
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from google.ads.googleads.client import GoogleAdsClient

def test_bidding_strategy_update():
    """Test the bidding strategy update function."""
    try:
        # Load Google Ads client
        config_file = os.path.join(current_dir, "google-ads.yaml")
        client = GoogleAdsClient.load_from_storage(config_file)
        
        # Import the function from campaign_operations
        from campaign_operations import update_campaign_bidding_strategy
        
        # Test campaign resource name (using one of the existing campaigns)
        customer_id = "3045806466"
        campaign_resource_name = "customers/3045806466/campaigns/21937794210"  # Leads-Search-Event-5
        
        print("🧪 Testing Bidding Strategy Update Functionality")
        print("=" * 55)
        print(f"Customer ID: {customer_id}")
        print(f"Campaign: {campaign_resource_name}")
        print()
        
        # Test different bidding strategies
        test_strategies = [
            "MAXIMIZE_CLICKS",
            "MANUAL_CPC", 
            "ENHANCED_CPC",
            "MAXIMIZE_CONVERSIONS"
        ]
        
        for strategy in test_strategies:
            print(f"🔄 Testing strategy: {strategy}")
            try:
                result = update_campaign_bidding_strategy(
                    client, customer_id, campaign_resource_name, strategy
                )
                
                if isinstance(result, str) and result.startswith("❌"):
                    print(f"   ❌ Failed: {result}")
                else:
                    print(f"   ✅ Success: {result}")
                    
                print()
                
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                print()
        
        print("🎯 Test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

if __name__ == "__main__":
    success = test_bidding_strategy_update()
    sys.exit(0 if success else 1)

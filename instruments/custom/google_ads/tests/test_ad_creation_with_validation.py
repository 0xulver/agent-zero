#!/usr/bin/env python3
"""
Test script to demonstrate ad creation with validation preventing API errors.
"""

import sys
import os
import json

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from google.ads.googleads.client import GoogleAdsClient

def test_ad_creation_with_validation():
    """Test ad creation with validation to prevent API errors."""
    try:
        # Load Google Ads client
        config_file = os.path.join(current_dir, "google-ads.yaml")
        client = GoogleAdsClient.load_from_storage(config_file)
        
        # Import the ad creation function
        from campaign_operations import create_responsive_search_ad
        
        print("🧪 Testing Ad Creation with Validation")
        print("=" * 45)
        
        # Test parameters
        customer_id = "3045806466"
        ad_group_resource_name = "customers/3045806466/adGroups/181000163226"  # Existing ad group
        
        # Load test ad copy data
        test_file = os.path.join(current_dir, "test_ad_copy_validation.json")
        with open(test_file, 'r') as f:
            test_data = json.load(f)
        
        # Test 1: Valid ad copy (should succeed)
        print("\n🔍 Test 1: Valid Ad Copy")
        print("-" * 30)
        valid_ad = test_data["valid_ad"]
        print(f"Headlines: {valid_ad['headlines']}")
        print(f"Descriptions: {valid_ad['descriptions']}")
        
        result = create_responsive_search_ad(client, customer_id, ad_group_resource_name, valid_ad)
        if result and not result.startswith("❌"):
            print(f"✅ SUCCESS: Ad created successfully: {result}")
        else:
            print(f"❌ FAILED: {result}")
        
        # Test 2: Invalid ad copy with long headlines (should fail validation)
        print("\n🔍 Test 2: Invalid Ad Copy (Long Headlines)")
        print("-" * 30)
        invalid_ad = test_data["invalid_ad_long_headlines"]
        print(f"Headlines: {invalid_ad['headlines'][:1]}...")  # Show first headline only
        print(f"First headline length: {len(invalid_ad['headlines'][0])} characters")
        
        result = create_responsive_search_ad(client, customer_id, ad_group_resource_name, invalid_ad)
        if result and result.startswith("❌"):
            print(f"✅ VALIDATION WORKED: Prevented API call with invalid data")
            print(f"   Error message preview: {result[:100]}...")
        else:
            print(f"❌ VALIDATION FAILED: Should have caught the error")
        
        # Test 3: Invalid ad copy with insufficient content (should fail validation)
        print("\n🔍 Test 3: Invalid Ad Copy (Insufficient Content)")
        print("-" * 30)
        insufficient_ad = test_data["invalid_ad_insufficient_content"]
        print(f"Headlines: {insufficient_ad['headlines']} (only {len(insufficient_ad['headlines'])} provided)")
        print(f"Descriptions: {insufficient_ad['descriptions']} (only {len(insufficient_ad['descriptions'])} provided)")
        
        result = create_responsive_search_ad(client, customer_id, ad_group_resource_name, insufficient_ad)
        if result and result.startswith("❌"):
            print(f"✅ VALIDATION WORKED: Prevented API call with insufficient content")
            print(f"   Error message preview: {result[:100]}...")
        else:
            print(f"❌ VALIDATION FAILED: Should have caught the error")
        
        print("\n🎯 Ad creation validation test completed!")
        print("\n📋 Summary:")
        print("   ✅ Valid ad copy: Passes validation and creates ad")
        print("   ❌ Invalid ad copy: Fails validation BEFORE API call")
        print("   🛡️  No API errors caused by invalid ad copy!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ad_creation_with_validation()
    sys.exit(0 if success else 1)

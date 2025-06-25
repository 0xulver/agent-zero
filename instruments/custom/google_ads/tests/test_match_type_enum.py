#!/usr/bin/env python3
"""
Test script to verify that keyword match type enums are working correctly.
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from google.ads.googleads.client import GoogleAdsClient

def test_match_type_enum():
    """Test the match type enum conversion function."""
    try:
        # Load Google Ads client
        config_file = os.path.join(current_dir, "google-ads.yaml")
        client = GoogleAdsClient.load_from_storage(config_file)
        
        # Import the function from campaign_operations
        from campaign_operations import get_keyword_match_type_enum
        
        # Test different match types
        test_cases = ["EXACT", "PHRASE", "BROAD", "exact", "phrase", "broad", "INVALID"]
        
        print("🧪 Testing Keyword Match Type Enum Conversion")
        print("=" * 50)
        
        for match_type_string in test_cases:
            try:
                enum_result = get_keyword_match_type_enum(client, match_type_string)
                print(f"✅ '{match_type_string}' -> {enum_result} (type: {type(enum_result)})")
                print(f"   Integer value: {int(enum_result)}")
                print(f"   Enum name: {enum_result.name}")
                print()
            except Exception as e:
                print(f"❌ '{match_type_string}' -> ERROR: {e}")
                print()
        
        print("🎯 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_match_type_enum()
    sys.exit(0 if success else 1)

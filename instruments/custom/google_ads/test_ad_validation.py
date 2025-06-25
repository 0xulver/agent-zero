#!/usr/bin/env python3
"""
Test script to verify that ad copy length validation works correctly.
"""

import sys
import os
import json

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_ad_validation():
    """Test the ad copy validation function."""
    try:
        # Import the validation function from campaign_operations
        from campaign_operations import validate_ad_copy_lengths
        
        print("🧪 Testing Ad Copy Length Validation")
        print("=" * 45)
        
        # Load test ad copy data
        test_file = os.path.join(current_dir, "test_ad_copy_validation.json")
        with open(test_file, 'r') as f:
            test_data = json.load(f)
        
        # Test each ad copy scenario
        for test_name, ad_data in test_data.items():
            print(f"\n🔍 Testing: {test_name}")
            print("-" * 30)
            
            # Show the ad data
            print(f"Headlines ({len(ad_data.get('headlines', []))}): {ad_data.get('headlines', [])}")
            print(f"Descriptions ({len(ad_data.get('descriptions', []))}): {ad_data.get('descriptions', [])}")
            print(f"Final URL: {ad_data.get('final_url', 'Not provided')}")
            
            # Run validation
            errors = validate_ad_copy_lengths(ad_data)
            
            if errors:
                print(f"❌ Validation FAILED ({len(errors)} errors):")
                for error in errors:
                    print(f"   {error}")
            else:
                print("✅ Validation PASSED - Ad copy is valid!")
        
        print("\n🎯 Validation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_character_limits():
    """Test specific character limit scenarios."""
    print("\n" + "=" * 45)
    print("🔢 Testing Character Limit Edge Cases")
    print("=" * 45)
    
    from campaign_operations import validate_ad_copy_lengths
    
    # Test exactly at limits
    edge_cases = [
        {
            "name": "Exactly at limits",
            "ad_data": {
                "headlines": [
                    "A" * 30,  # Exactly 30 characters
                    "B" * 30,  # Exactly 30 characters
                    "C" * 30   # Exactly 30 characters
                ],
                "descriptions": [
                    "D" * 90,  # Exactly 90 characters
                    "E" * 90   # Exactly 90 characters
                ],
                "final_url": "https://example.com"
            }
        },
        {
            "name": "One character over limits",
            "ad_data": {
                "headlines": [
                    "A" * 31,  # 31 characters - over limit
                    "B" * 30,  # Exactly 30 characters
                    "C" * 30   # Exactly 30 characters
                ],
                "descriptions": [
                    "D" * 91,  # 91 characters - over limit
                    "E" * 90   # Exactly 90 characters
                ],
                "final_url": "https://example.com"
            }
        }
    ]
    
    for test_case in edge_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        print("-" * 30)
        
        ad_data = test_case['ad_data']
        
        # Show character counts
        for i, headline in enumerate(ad_data['headlines'], 1):
            print(f"Headline {i}: {len(headline)} chars")
        
        for i, description in enumerate(ad_data['descriptions'], 1):
            print(f"Description {i}: {len(description)} chars")
        
        # Run validation
        errors = validate_ad_copy_lengths(ad_data)
        
        if errors:
            print(f"❌ Validation FAILED ({len(errors)} errors):")
            for error in errors:
                print(f"   {error}")
        else:
            print("✅ Validation PASSED")

if __name__ == "__main__":
    success = test_ad_validation()
    test_character_limits()
    sys.exit(0 if success else 1)

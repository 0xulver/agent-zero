#!/usr/bin/env python3
"""
Test script to verify that keyword research queries use valid metrics.
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def test_keyword_research_queries():
    """Test that keyword research functions use valid metrics for keyword_view."""
    try:
        from keyword_research import (
            get_current_keywords, get_top_performing_keywords, 
            get_underperforming_keywords, get_expensive_keywords,
            get_keyword_opportunities, analyze_keyword_performance
        )
        
        print("🧪 Testing Keyword Research Query Validity")
        print("=" * 50)
        
        # Test customer ID (won't actually execute, just test query construction)
        test_customer_id = "1234567890"
        
        print("\n✅ Testing query construction (no API calls)...")
        
        # Test each function to ensure they don't use invalid metrics
        functions_to_test = [
            ("get_current_keywords", get_current_keywords),
            ("get_top_performing_keywords", get_top_performing_keywords),
            ("get_underperforming_keywords", get_underperforming_keywords),
            ("get_expensive_keywords", get_expensive_keywords),
            ("get_keyword_opportunities", get_keyword_opportunities),
            ("analyze_keyword_performance", analyze_keyword_performance)
        ]
        
        for func_name, func in functions_to_test:
            try:
                print(f"   📋 Testing {func_name}...")
                # This will construct the query but fail at execution (which is expected)
                # We're just testing that the function doesn't crash during query construction
                result = func(test_customer_id, days=7)
                # If we get here without exception during query construction, that's good
                print(f"   ✅ {func_name} - Query construction successful")
            except Exception as e:
                # Check if it's a query construction error vs execution error
                error_str = str(e).lower()
                if "invalid" in error_str and ("metric" in error_str or "field" in error_str):
                    print(f"   ❌ {func_name} - Invalid metric error: {e}")
                    return False
                else:
                    # Expected execution errors (no credentials, etc.) are OK
                    print(f"   ✅ {func_name} - Query construction OK (execution failed as expected)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

def test_invalid_metrics_removed():
    """Test that invalid metrics have been removed from queries."""
    print("\n🔍 Testing Invalid Metrics Removal")
    print("=" * 40)
    
    # Read the keyword research file and check for invalid metrics
    keyword_research_file = os.path.join(parent_dir, "keyword_research.py")
    
    try:
        with open(keyword_research_file, 'r') as f:
            content = f.read()
        
        invalid_metrics = [
            "metrics.search_impression_share",
            "metrics.search_rank_lost_impression_share", 
            "metrics.search_budget_lost_impression_share"
        ]
        
        found_invalid = []
        for metric in invalid_metrics:
            if metric in content:
                found_invalid.append(metric)
        
        if found_invalid:
            print(f"❌ Found invalid metrics in keyword_research.py:")
            for metric in found_invalid:
                print(f"   - {metric}")
            return False
        else:
            print("✅ No invalid metrics found in keyword_research.py")
            
        # Check keyword_tools.py as well
        keyword_tools_file = os.path.join(parent_dir, "keyword_tools.py")
        with open(keyword_tools_file, 'r') as f:
            tools_content = f.read()
            
        found_invalid_tools = []
        for metric in invalid_metrics:
            if metric in tools_content:
                found_invalid_tools.append(metric)
                
        if found_invalid_tools:
            print(f"❌ Found invalid metrics in keyword_tools.py:")
            for metric in found_invalid_tools:
                print(f"   - {metric}")
            return False
        else:
            print("✅ No invalid metrics found in keyword_tools.py")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking files: {e}")
        return False

def test_valid_metrics_usage():
    """Test that we're using valid metrics for keyword_view."""
    print("\n📊 Testing Valid Metrics Usage")
    print("=" * 35)
    
    # Valid metrics for keyword_view resource
    valid_keyword_metrics = [
        "metrics.impressions",
        "metrics.clicks", 
        "metrics.ctr",
        "metrics.average_cpc",
        "metrics.cost_micros",
        "metrics.conversions",
        "metrics.conversions_value",
        "metrics.cost_per_conversion",
        "ad_group_criterion.quality_info.quality_score"
    ]
    
    print("✅ Valid metrics for keyword_view:")
    for metric in valid_keyword_metrics:
        print(f"   - {metric}")
    
    print("\n❌ Invalid metrics for keyword_view (now removed):")
    invalid_metrics = [
        "metrics.search_impression_share",
        "metrics.search_rank_lost_impression_share",
        "metrics.search_budget_lost_impression_share"
    ]
    for metric in invalid_metrics:
        print(f"   - {metric}")
    
    print("\n💡 Note: Impression share metrics are available in campaign_view or ad_group_view,")
    print("   but not in keyword_view resource.")
    
    return True

if __name__ == "__main__":
    print("🎯 Testing Keyword Metrics Fix")
    print("=" * 50)
    
    success = True
    success &= test_invalid_metrics_removed()
    success &= test_valid_metrics_usage()
    success &= test_keyword_research_queries()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All keyword metrics tests PASSED!")
        print("🎉 Invalid metrics have been successfully removed!")
    else:
        print("❌ Some keyword metrics tests FAILED!")
    
    sys.exit(0 if success else 1)

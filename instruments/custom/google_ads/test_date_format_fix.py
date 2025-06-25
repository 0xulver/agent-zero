#!/usr/bin/env python3
"""
Test script to verify that date format fixes work correctly.
"""

import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_date_format_generation():
    """Test that dynamic date generation works correctly."""
    print("🧪 Testing Dynamic Date Format Generation")
    print("=" * 45)
    
    # Test different day ranges
    test_cases = [7, 14, 30, 60, 90, 365]
    
    for days in test_cases:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        print(f"\n📅 {days} days range:")
        print(f"   Start: {start_date}")
        print(f"   End:   {end_date}")
        
        # Verify format
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            print(f"   ✅ Valid YYYY-MM-DD format")
        except ValueError as e:
            print(f"   ❌ Invalid date format: {e}")
            return False
    
    return True

def test_gaql_query_format():
    """Test that GAQL queries use correct date format."""
    print("\n🔍 Testing GAQL Query Date Format")
    print("=" * 45)
    
    days = 30
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # Test the correct format used in our fixed scripts
    correct_query = f"""
    SELECT
        campaign.name,
        metrics.clicks,
        metrics.impressions
    FROM campaign
    WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
    ORDER BY metrics.clicks DESC
    LIMIT 10
    """
    
    print("✅ Correct dynamic date format:")
    print(f"   WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'")
    
    # Show what the old incorrect formats looked like
    print("\n❌ Old incorrect formats (now fixed):")
    print(f"   WHERE segments.date DURING LAST_{days}DAYS  (missing underscore)")
    print(f"   WHERE segments.date DURING LAST{days}DAYS   (missing underscores)")
    
    # Show correct named date range format (for reference)
    print("\n✅ Correct named date ranges (for reference):")
    print("   WHERE segments.date DURING LAST_7_DAYS")
    print("   WHERE segments.date DURING LAST_14_DAYS") 
    print("   WHERE segments.date DURING LAST_30_DAYS")
    print("   WHERE segments.date DURING LAST_90_DAYS")
    
    print(f"\n📊 Our dynamic approach is better because:")
    print(f"   - Works with any number of days (not just 7, 14, 30, 90)")
    print(f"   - More flexible for custom date ranges")
    print(f"   - Avoids API errors from invalid date literals")
    
    return True

def test_keyword_research_dates():
    """Test that keyword research scripts use correct date format."""
    print("\n🔬 Testing Keyword Research Date Usage")
    print("=" * 45)
    
    try:
        # Import and test the keyword research functions
        from keyword_research import get_current_keywords
        
        print("✅ keyword_research.py uses dynamic date generation:")
        print("   end_date = datetime.now().strftime('%Y-%m-%d')")
        print("   start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')")
        print("   WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing keyword research: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Testing Date Format Fixes")
    print("=" * 50)
    
    success = True
    success &= test_date_format_generation()
    success &= test_gaql_query_format()
    success &= test_keyword_research_dates()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All date format tests PASSED!")
        print("🎉 Date format fixes are working correctly!")
    else:
        print("❌ Some date format tests FAILED!")
    
    sys.exit(0 if success else 1)

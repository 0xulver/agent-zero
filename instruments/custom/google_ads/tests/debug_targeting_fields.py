#!/usr/bin/env python3
"""
Debug script to find the correct fields for targeting criteria.
"""

import sys
import os
import subprocess

def run_debug_query(customer_id, query, description):
    """Run a debug query and show results."""
    print(f"\n🔍 {description}")
    print("=" * 60)
    print(f"Query: {query}")
    print("-" * 60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    run_query_script = os.path.join(script_dir, "instruments/custom/google_ads/run_query.py")
    
    try:
        result = subprocess.run([
            sys.executable, run_query_script,
            "--customer-id", customer_id,
            "--query", query,
            "--format", "table"
        ], capture_output=True, text=True, check=True)
        
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def debug_targeting_fields():
    """Test different field combinations to find working targeting queries."""
    customer_id = "3045806466"
    campaign_id = "22710728616"  # Leads-Search-Event-6-Optimized
    
    print("🧪 Debug Targeting Fields for Campaign ID:", campaign_id)
    print("=" * 60)
    
    # Test 1: Try to get basic criterion info with resource names
    query1 = f"""
    SELECT
        campaign_criterion.resource_name,
        campaign_criterion.type,
        campaign_criterion.criterion_id,
        campaign_criterion.status,
        campaign_criterion.negative
    FROM campaign_criterion
    WHERE campaign.id = {campaign_id}
    LIMIT 20
    """
    
    run_debug_query(customer_id, query1, "Basic criterion fields with resource names")
    
    # Test 2: Try location-specific fields
    query2 = f"""
    SELECT
        campaign_criterion.type,
        campaign_criterion.criterion_id,
        campaign_criterion.location.geo_target_constant
    FROM campaign_criterion
    WHERE campaign.id = {campaign_id}
        AND campaign_criterion.type = 'LOCATION'
    LIMIT 10
    """
    
    run_debug_query(customer_id, query2, "Location targeting fields")
    
    # Test 3: Try language-specific fields
    query3 = f"""
    SELECT
        campaign_criterion.type,
        campaign_criterion.criterion_id,
        campaign_criterion.language.language_constant
    FROM campaign_criterion
    WHERE campaign.id = {campaign_id}
        AND campaign_criterion.type = 'LANGUAGE'
    LIMIT 10
    """
    
    run_debug_query(customer_id, query3, "Language targeting fields")
    
    # Test 4: Try to get geo target details separately
    query4 = """
    SELECT
        geo_target_constant.id,
        geo_target_constant.name,
        geo_target_constant.country_code,
        geo_target_constant.target_type
    FROM geo_target_constant
    WHERE geo_target_constant.id IN (2840, 2124)
    LIMIT 10
    """
    
    run_debug_query(customer_id, query4, "Geo target constants (US=2840, Canada=2124)")
    
    # Test 5: Try to get language details separately
    query5 = """
    SELECT
        language_constant.id,
        language_constant.name,
        language_constant.code
    FROM language_constant
    WHERE language_constant.id IN (1000, 1003)
    LIMIT 10
    """
    
    run_debug_query(customer_id, query5, "Language constants (English=1000, Spanish=1003)")

if __name__ == "__main__":
    debug_targeting_fields()

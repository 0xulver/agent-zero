#!/usr/bin/env python3
"""
Test alternative approaches to get targeting data.
"""

import sys
import os
import subprocess

def run_query(customer_id, query, description):
    """Run a query and show results."""
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

def test_alternative_approaches():
    """Test different approaches to get targeting information."""
    customer_id = "3045806466"
    campaign_id = "22710728616"
    
    print("🧪 Testing Alternative Targeting Approaches")
    print("=" * 50)
    
    # Approach 1: Try using campaign resource with targeting fields
    query1 = f"""
    SELECT 
        campaign.id,
        campaign.name,
        campaign.geo_target_type_setting.positive_geo_target_type,
        campaign.geo_target_type_setting.negative_geo_target_type
    FROM campaign
    WHERE campaign.id = {campaign_id}
    """
    
    run_query(customer_id, query1, "Campaign geo target settings")
    
    # Approach 2: Try geographic_view resource
    query2 = f"""
    SELECT 
        campaign.id,
        campaign.name,
        geographic_view.country_criterion_id,
        geographic_view.location_type
    FROM geographic_view
    WHERE campaign.id = {campaign_id}
    LIMIT 10
    """
    
    run_query(customer_id, query2, "Geographic view for campaign")
    
    # Approach 3: Try language_view resource
    query3 = f"""
    SELECT 
        campaign.id,
        campaign.name,
        language_view.resource_name
    FROM language_view
    WHERE campaign.id = {campaign_id}
    LIMIT 10
    """
    
    run_query(customer_id, query3, "Language view for campaign")
    
    # Approach 4: Try user_location_view
    query4 = f"""
    SELECT 
        campaign.id,
        campaign.name,
        user_location_view.country_criterion_id,
        user_location_view.targeting_location
    FROM user_location_view
    WHERE campaign.id = {campaign_id}
    LIMIT 10
    """
    
    run_query(customer_id, query4, "User location view for campaign")
    
    # Approach 5: Try a different campaign_criterion query structure
    query5 = f"""
    SELECT 
        campaign.id,
        campaign.name
    FROM campaign_criterion
    WHERE campaign.id = {campaign_id}
    LIMIT 5
    """
    
    run_query(customer_id, query5, "Campaign info from campaign_criterion resource")

if __name__ == "__main__":
    test_alternative_approaches()

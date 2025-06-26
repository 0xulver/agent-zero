#!/usr/bin/env python3
"""
Debug script to understand campaign targeting structure.
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

def debug_targeting_queries():
    """Run various debug queries to understand targeting structure."""
    customer_id = "3045806466"
    
    print("🧪 Debug Campaign Targeting Queries")
    print("=" * 50)
    
    # Query 1: Check what's in campaign_criterion
    query1 = """
    SELECT
        campaign_criterion.resource_name,
        campaign_criterion.campaign,
        campaign_criterion.criterion_id,
        campaign_criterion.type,
        campaign_criterion.status
    FROM campaign_criterion
    LIMIT 10
    """
    
    run_debug_query(customer_id, query1, "Basic campaign_criterion structure")
    
    # Query 2: Check for any targeting criteria
    query2 = """
    SELECT
        campaign.id,
        campaign.name,
        campaign_criterion.type,
        campaign_criterion.criterion_id,
        campaign_criterion.status
    FROM campaign_criterion
    WHERE campaign_criterion.type IN ('LOCATION', 'LANGUAGE', 'AGE_RANGE', 'GENDER')
    LIMIT 20
    """
    
    run_debug_query(customer_id, query2, "All targeting criteria types")
    
    # Query 3: Check campaign settings
    query3 = """
    SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.geo_target_type_setting.positive_geo_target_type,
        campaign.geo_target_type_setting.negative_geo_target_type
    FROM campaign
    WHERE campaign.status IN ('ENABLED', 'PAUSED')
    LIMIT 10
    """
    
    run_debug_query(customer_id, query3, "Campaign geo target settings")
    
    # Query 4: Check for location criteria specifically
    query4 = """
    SELECT
        campaign.id,
        campaign.name,
        campaign_criterion.criterion_id,
        campaign_criterion.type,
        campaign_criterion.negative
    FROM campaign_criterion
    WHERE campaign_criterion.type = 'LOCATION'
    LIMIT 20
    """
    
    run_debug_query(customer_id, query4, "Location targeting criteria only")
    
    # Query 5: Check for language criteria specifically
    query5 = """
    SELECT
        campaign.id,
        campaign.name,
        campaign_criterion.criterion_id,
        campaign_criterion.type,
        campaign_criterion.negative
    FROM campaign_criterion
    WHERE campaign_criterion.type = 'LANGUAGE'
    LIMIT 20
    """
    
    run_debug_query(customer_id, query5, "Language targeting criteria only")
    
    # Query 6: Check account-level settings
    query6 = """
    SELECT
        customer.id,
        customer.descriptive_name,
        customer.currency_code,
        customer.time_zone
    FROM customer
    LIMIT 5
    """
    
    run_debug_query(customer_id, query6, "Account-level information")

if __name__ == "__main__":
    debug_targeting_queries()

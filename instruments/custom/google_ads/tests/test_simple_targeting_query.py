#!/usr/bin/env python3
"""
Test simple targeting queries to isolate the issue.
"""

import sys
import os
import subprocess

def run_simple_query(customer_id, query, description):
    """Run a simple query and show results."""
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

def test_simple_queries():
    """Test very simple queries to understand the data structure."""
    customer_id = "3045806466"
    campaign_id = "22710728616"
    
    print("🧪 Testing Simple Targeting Queries")
    print("=" * 50)
    
    # Test 1: Just count criteria
    query1 = f"""
    SELECT campaign_criterion.resource_name
    FROM campaign_criterion
    WHERE campaign.id = {campaign_id}
    """
    
    run_simple_query(customer_id, query1, "Count criteria for campaign")
    
    # Test 2: Try without WHERE clause to see if data exists at all
    query2 = """
    SELECT 
        campaign_criterion.type,
        campaign_criterion.criterion_id
    FROM campaign_criterion
    LIMIT 5
    """
    
    run_simple_query(customer_id, query2, "Sample criteria from any campaign")
    
    # Test 3: Try a different resource to verify query runner works
    query3 = """
    SELECT 
        campaign.id,
        campaign.name,
        campaign.status
    FROM campaign
    LIMIT 3
    """
    
    run_simple_query(customer_id, query3, "Sample campaigns (verify query runner)")
    
    # Test 4: Try ad group criteria instead
    query4 = f"""
    SELECT 
        ad_group_criterion.type,
        ad_group_criterion.criterion_id,
        ad_group_criterion.keyword.text
    FROM ad_group_criterion
    WHERE campaign.id = {campaign_id}
    LIMIT 5
    """
    
    run_simple_query(customer_id, query4, "Ad group criteria for same campaign")

if __name__ == "__main__":
    test_simple_queries()

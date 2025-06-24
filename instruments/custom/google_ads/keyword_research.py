#!/usr/bin/env python3
"""
Google Ads Keyword Research Tool

This tool provides comprehensive keyword research capabilities by using the run_query.py
script internally to execute specialized GAQL queries for keyword analysis.
"""

import sys
import subprocess
import argparse
import os
from datetime import datetime, timedelta

def run_gaql_query(customer_id, query, output_format="table"):
    """Execute a GAQL query using the run_query.py script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    run_query_script = os.path.join(script_dir, "run_query.py")
    
    try:
        result = subprocess.run([
            sys.executable, run_query_script,
            "--customer-id", customer_id,
            "--query", query,
            "--format", output_format
        ], capture_output=True, text=True, check=True)
        
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"❌ Error executing query: {e.stderr}"

def get_current_keywords(customer_id, days=30, min_impressions=10):
    """Get all current keywords from active campaigns with performance data."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        campaign.name,
        ad_group.name,
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.cost_micros,
        metrics.conversions,
        metrics.average_cpc
    FROM keyword_view
    WHERE
        campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND ad_group_criterion.status = 'ENABLED'
        AND segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND metrics.impressions >= {min_impressions}
    ORDER BY metrics.impressions DESC
    LIMIT 100
    """

    print(f"🔍 Getting current keywords for last {days} days (min {min_impressions} impressions)...")
    return run_gaql_query(customer_id, query)

def get_top_performing_keywords(customer_id, days=30, min_conversions=1):
    """Get top performing keywords by conversion value."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        campaign.name,
        metrics.conversions,
        metrics.conversions_value,
        metrics.cost_micros,
        metrics.cost_per_conversion,
        metrics.search_impression_share,
        metrics.ctr
    FROM keyword_view
    WHERE
        campaign.status = 'ENABLED'
        AND segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND metrics.conversions >= {min_conversions}
    ORDER BY metrics.conversions_value DESC
    LIMIT 50
    """

    print(f"🏆 Getting top performing keywords (min {min_conversions} conversions)...")
    return run_gaql_query(customer_id, query)

def get_underperforming_keywords(customer_id, days=30, min_impressions=1000, max_ctr=0.02):
    """Find keywords with high impressions but low CTR (optimization opportunities)."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        campaign.name,
        ad_group.name,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.average_cpc,
        metrics.cost_micros,
        metrics.conversions
    FROM keyword_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND metrics.impressions >= {min_impressions}
        AND metrics.ctr < {max_ctr}
        AND campaign.status = 'ENABLED'
    ORDER BY metrics.impressions DESC
    LIMIT 30
    """

    print(f"⚠️  Finding underperforming keywords (>{min_impressions} impressions, <{max_ctr*100}% CTR)...")
    return run_gaql_query(customer_id, query)

def get_expensive_keywords(customer_id, days=30, min_cost_micros=10000000):
    """Find high-cost keywords that may need optimization."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        campaign.name,
        metrics.cost_micros,
        metrics.clicks,
        metrics.conversions,
        metrics.cost_per_conversion,
        metrics.ctr,
        metrics.average_cpc
    FROM keyword_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND metrics.cost_micros >= {min_cost_micros}
        AND campaign.status = 'ENABLED'
    ORDER BY metrics.cost_micros DESC
    LIMIT 25
    """

    cost_threshold = min_cost_micros / 1000000  # Convert to currency units
    print(f"💰 Finding expensive keywords (>${cost_threshold}+ spend)...")
    return run_gaql_query(customer_id, query)

def get_keyword_opportunities(customer_id, days=30):
    """Find keyword expansion opportunities by analyzing search terms."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        search_term_view.search_term,
        campaign.name,
        ad_group.name,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.conversions,
        metrics.cost_micros
    FROM search_term_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND metrics.impressions >= 10
        AND metrics.clicks >= 1
        AND campaign.status = 'ENABLED'
    ORDER BY metrics.conversions DESC, metrics.clicks DESC
    LIMIT 50
    """

    print(f"🔎 Finding keyword expansion opportunities from search terms...")
    return run_gaql_query(customer_id, query)

def get_keyword_quality_scores(customer_id):
    """Get quality scores for keywords to identify optimization needs."""
    query = """
    SELECT 
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        campaign.name,
        ad_group.name,
        ad_group_criterion.quality_info.quality_score,
        ad_group_criterion.quality_info.creative_quality_score,
        ad_group_criterion.quality_info.post_click_quality_score,
        ad_group_criterion.quality_info.search_predicted_ctr,
        metrics.impressions,
        metrics.clicks
    FROM keyword_view 
    WHERE 
        campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND ad_group_criterion.status = 'ENABLED'
        AND ad_group_criterion.quality_info.quality_score IS NOT NULL
    ORDER BY ad_group_criterion.quality_info.quality_score ASC
    LIMIT 50
    """
    
    print("📊 Getting keyword quality scores...")
    return run_gaql_query(customer_id, query)

def analyze_keyword_competition(customer_id, days=30):
    """Analyze keyword competition metrics."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        campaign.name,
        metrics.search_impression_share,
        metrics.search_rank_lost_impression_share,
        metrics.search_budget_lost_impression_share,
        metrics.top_impression_percentage,
        metrics.absolute_top_impression_percentage,
        metrics.impressions,
        metrics.clicks
    FROM keyword_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND campaign.status = 'ENABLED'
        AND metrics.impressions >= 100
    ORDER BY metrics.search_impression_share ASC
    LIMIT 40
    """

    print("🥊 Analyzing keyword competition metrics...")
    return run_gaql_query(customer_id, query)

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Google Ads Keyword Research Tool')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--action', required=True, 
                       choices=['current', 'top-performing', 'underperforming', 'expensive', 
                               'opportunities', 'quality-scores', 'competition'],
                       help='Type of keyword analysis to perform')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze (default: 30)')
    parser.add_argument('--min-impressions', type=int, default=10, help='Minimum impressions filter')
    parser.add_argument('--min-conversions', type=int, default=1, help='Minimum conversions filter')
    parser.add_argument('--max-ctr', type=float, default=0.02, help='Maximum CTR for underperforming keywords')
    parser.add_argument('--min-cost', type=int, default=10000000, help='Minimum cost in micros for expensive keywords')
    
    args = parser.parse_args()
    
    print("🚀 Google Ads Keyword Research Tool")
    print("=" * 40)
    
    if args.action == 'current':
        result = get_current_keywords(args.customer_id, args.days, args.min_impressions)
    elif args.action == 'top-performing':
        result = get_top_performing_keywords(args.customer_id, args.days, args.min_conversions)
    elif args.action == 'underperforming':
        result = get_underperforming_keywords(args.customer_id, args.days, args.min_impressions, args.max_ctr)
    elif args.action == 'expensive':
        result = get_expensive_keywords(args.customer_id, args.days, args.min_cost)
    elif args.action == 'opportunities':
        result = get_keyword_opportunities(args.customer_id, args.days)
    elif args.action == 'quality-scores':
        result = get_keyword_quality_scores(args.customer_id)
    elif args.action == 'competition':
        result = analyze_keyword_competition(args.customer_id, args.days)
    
    print(result)

if __name__ == "__main__":
    main()

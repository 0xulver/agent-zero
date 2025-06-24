#!/usr/bin/env python3
"""
Google Ads Campaign Analysis Tool

This tool provides comprehensive campaign analysis capabilities by using the run_query.py
script internally to execute specialized GAQL queries for campaign performance analysis.
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

def get_campaign_overview(customer_id, days=30):
    """Get comprehensive campaign performance overview."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.advertising_channel_type,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value,
        metrics.cost_per_conversion,
        metrics.average_cpc
    FROM campaign
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
    ORDER BY metrics.cost_micros DESC
    LIMIT 50
    """

    print(f"📊 Getting campaign overview for last {days} days...")
    return run_gaql_query(customer_id, query)

def get_top_campaigns(customer_id, days=30, metric="conversion_value"):
    """Get top performing campaigns by specified metric."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    order_field = f"metrics.{metric}"

    query = f"""
    SELECT
        campaign.name,
        campaign.status,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value,
        metrics.cost_per_conversion
    FROM campaign
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND campaign.status = 'ENABLED'
        AND metrics.{metric} > 0
    ORDER BY {order_field} DESC
    LIMIT 20
    """

    print(f"🏆 Getting top campaigns by {metric}...")
    return run_gaql_query(customer_id, query)

def get_underperforming_campaigns(customer_id, days=30, min_cost=5000000):
    """Find campaigns with high spend but low performance."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    cost_threshold = min_cost / 1000000  # Convert to currency units

    query = f"""
    SELECT
        campaign.name,
        campaign.status,
        metrics.cost_micros,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.conversions,
        metrics.conversions_value,
        metrics.cost_per_conversion
    FROM campaign
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND metrics.cost_micros >= {min_cost}
        AND (metrics.conversions = 0 OR metrics.ctr < 0.01)
        AND campaign.status = 'ENABLED'
    ORDER BY metrics.cost_micros DESC
    LIMIT 15
    """

    print(f"⚠️  Finding underperforming campaigns (>${cost_threshold}+ spend, low performance)...")
    return run_gaql_query(customer_id, query)

def get_campaign_trends(customer_id, days=30):
    """Analyze campaign performance trends over time."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        campaign.name,
        segments.date,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND campaign.status = 'ENABLED'
        AND metrics.impressions > 0
    ORDER BY campaign.name, segments.date DESC
    LIMIT 200
    """

    print(f"📈 Analyzing campaign trends over last {days} days...")
    return run_gaql_query(customer_id, query, "csv")

def get_campaign_device_performance(customer_id, days=30):
    """Analyze campaign performance by device type."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        campaign.name,
        segments.device,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value,
        metrics.average_cpc
    FROM campaign
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND campaign.status = 'ENABLED'
        AND metrics.impressions > 100
    ORDER BY campaign.name, metrics.cost_micros DESC
    LIMIT 100
    """

    print(f"📱 Analyzing campaign performance by device...")
    return run_gaql_query(customer_id, query)

def get_campaign_budget_analysis(customer_id):
    """Analyze campaign budgets and spending patterns."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        campaign.name,
        campaign.status,
        campaign_budget.amount_micros,
        campaign_budget.delivery_method,
        campaign_budget.period,
        metrics.cost_micros,
        metrics.impressions,
        metrics.clicks
    FROM campaign
    WHERE
        campaign.status = 'ENABLED'
        AND segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
    ORDER BY campaign_budget.amount_micros DESC
    LIMIT 30
    """

    print("💰 Analyzing campaign budgets and spending...")
    return run_gaql_query(customer_id, query)

def get_campaign_geographic_performance(customer_id, days=30):
    """Analyze campaign performance by geographic location."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        campaign.name,
        geographic_view.country_criterion_id,
        geographic_view.location_type,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.cost_micros,
        metrics.conversions
    FROM geographic_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND campaign.status = 'ENABLED'
        AND metrics.impressions > 50
    ORDER BY campaign.name, metrics.cost_micros DESC
    LIMIT 100
    """

    print(f"🌍 Analyzing campaign performance by geography...")
    return run_gaql_query(customer_id, query)

def get_campaign_ad_schedule_performance(customer_id, days=30):
    """Analyze campaign performance by time of day and day of week."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        campaign.name,
        segments.hour,
        segments.day_of_week,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.cost_micros,
        metrics.conversions
    FROM campaign
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND campaign.status = 'ENABLED'
        AND metrics.impressions > 10
    ORDER BY campaign.name, segments.day_of_week, segments.hour
    LIMIT 200
    """

    print(f"⏰ Analyzing campaign performance by time schedule...")
    return run_gaql_query(customer_id, query, "csv")

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Google Ads Campaign Analysis Tool')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--action', required=True, 
                       choices=['overview', 'top-campaigns', 'underperforming', 'trends', 
                               'device-performance', 'budget-analysis', 'geographic', 'schedule'],
                       help='Type of campaign analysis to perform')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze (default: 30)')
    parser.add_argument('--metric', default='conversion_value', 
                       choices=['conversion_value', 'conversions', 'clicks', 'impressions', 'cost_micros'],
                       help='Metric for top campaigns analysis')
    parser.add_argument('--min-cost', type=int, default=5000000, 
                       help='Minimum cost in micros for underperforming analysis')
    
    args = parser.parse_args()
    
    print("🚀 Google Ads Campaign Analysis Tool")
    print("=" * 42)
    
    if args.action == 'overview':
        result = get_campaign_overview(args.customer_id, args.days)
    elif args.action == 'top-campaigns':
        result = get_top_campaigns(args.customer_id, args.days, args.metric)
    elif args.action == 'underperforming':
        result = get_underperforming_campaigns(args.customer_id, args.days, args.min_cost)
    elif args.action == 'trends':
        result = get_campaign_trends(args.customer_id, args.days)
    elif args.action == 'device-performance':
        result = get_campaign_device_performance(args.customer_id, args.days)
    elif args.action == 'budget-analysis':
        result = get_campaign_budget_analysis(args.customer_id)
    elif args.action == 'geographic':
        result = get_campaign_geographic_performance(args.customer_id, args.days)
    elif args.action == 'schedule':
        result = get_campaign_ad_schedule_performance(args.customer_id, args.days)
    
    print(result)

if __name__ == "__main__":
    main()

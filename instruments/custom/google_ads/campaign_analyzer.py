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

def get_campaign_targeting_settings(customer_id, campaign_id=None):
    """Retrieve and display current location and language targeting for campaigns."""

    # Base query for campaign criterion (targeting settings)
    base_query = """
    SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign_criterion.criterion_id,
        campaign_criterion.type,
        campaign_criterion.status,
        campaign_criterion.negative
    FROM campaign_criterion
    WHERE
        campaign.status IN ('ENABLED', 'PAUSED')
        AND campaign_criterion.type IN ('LOCATION', 'LANGUAGE')
        AND campaign_criterion.status IN ('ENABLED', 'PAUSED')
    """

    # Add campaign filter if specific campaign ID is provided
    if campaign_id:
        query = base_query + f" AND campaign.id = {campaign_id}"
        print(f"🎯 Getting targeting settings for campaign ID: {campaign_id}...")
    else:
        query = base_query + " ORDER BY campaign.name, campaign_criterion.type"
        print("🎯 Getting targeting settings for all campaigns...")

    query += " LIMIT 200"

    return run_gaql_query(customer_id, query)

def get_campaign_targeting_summary(customer_id, campaign_id=None):
    """Get a formatted summary of campaign targeting settings with readable names."""

    # First get the basic targeting information
    basic_query = """
    SELECT
        campaign.id,
        campaign.name,
        campaign_criterion.criterion_id,
        campaign_criterion.type,
        campaign_criterion.negative,
        campaign_criterion.status
    FROM campaign_criterion
    WHERE
        campaign.status IN ('ENABLED', 'PAUSED')
        AND campaign_criterion.type IN ('LOCATION', 'LANGUAGE')
    """

    # Add campaign filter if specific campaign ID is provided
    if campaign_id:
        basic_query += f" AND campaign.id = {campaign_id}"
        print(f"🌍 Getting targeting summary for campaign ID: {campaign_id}...")
    else:
        basic_query += " ORDER BY campaign.name, campaign_criterion.type"
        print("🌍 Getting targeting summary for all campaigns...")

    basic_query += " LIMIT 200"

    print("\n🎯 CAMPAIGN TARGETING SUMMARY:")
    print("=" * 50)
    basic_result = run_gaql_query(customer_id, basic_query)

    # Get geo target information separately
    geo_query = """
    SELECT
        geo_target_constant.resource_name,
        geo_target_constant.id,
        geo_target_constant.name,
        geo_target_constant.country_code,
        geo_target_constant.target_type,
        geo_target_constant.canonical_name
    FROM geo_target_constant
    WHERE geo_target_constant.status = 'ENABLED'
    LIMIT 50
    """

    print("\n📍 SAMPLE GEO TARGETS (for reference):")
    print("=" * 50)
    geo_result = run_gaql_query(customer_id, geo_query)

    # Get language information separately
    language_query = """
    SELECT
        language_constant.resource_name,
        language_constant.id,
        language_constant.name,
        language_constant.code
    FROM language_constant
    LIMIT 20
    """

    print("\n🗣️ SAMPLE LANGUAGES (for reference):")
    print("=" * 50)
    language_result = run_gaql_query(customer_id, language_query)

    return f"{basic_result}\n{geo_result}\n{language_result}"

def diagnose_campaign_targeting(customer_id, campaign_name_or_id):
    """Comprehensive targeting diagnostic for a specific campaign."""
    import os
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException

    # First, try to find the campaign by name or ID
    if campaign_name_or_id.isdigit():
        # It's a campaign ID
        campaign_filter = f"campaign.id = {campaign_name_or_id}"
        identifier = f"ID {campaign_name_or_id}"
        campaign_id = campaign_name_or_id
    else:
        # It's a campaign name - use LIKE for partial matching
        campaign_filter = f"campaign.name LIKE '%{campaign_name_or_id}%'"
        identifier = f"name containing '{campaign_name_or_id}'"
        campaign_id = None

    print(f"🔍 Diagnosing targeting for campaign with {identifier}...")

    # Get campaign basic info first
    campaign_info_query = f"""
    SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.advertising_channel_type,
        campaign.start_date,
        campaign.end_date
    FROM campaign
    WHERE {campaign_filter}
    LIMIT 5
    """

    print("\n📋 CAMPAIGN INFORMATION:")
    print("=" * 50)
    campaign_info = run_gaql_query(customer_id, campaign_info_query)

    # If we found campaigns and don't have a specific ID, extract it
    if not campaign_id:
        # Try to extract campaign ID from the results for detailed analysis
        # For now, we'll use the query approach
        pass

    # Get detailed targeting using direct API approach
    print("\n🎯 DETAILED TARGETING ANALYSIS:")
    print("=" * 50)

    try:
        # Use direct API call to get accurate targeting data
        # Try different credential paths in order of preference
        credentials_paths = [
            # Current working directory
            'google-ads.yaml',
            # Instruments directory relative to current working directory
            'instruments/custom/google_ads/google-ads.yaml',
            # Absolute path to /a0/ directory
            '/a0/google-ads.yaml',
            # Home directory
            os.path.expanduser('~/google-ads.yaml'),
            # Script directory
            os.path.join(os.path.dirname(__file__), 'google-ads.yaml')
        ]

        client = None
        for path in credentials_paths:
            try:
                if os.path.exists(path):
                    print(f"🔑 Using credentials from: {path}")
                    client = GoogleAdsClient.load_from_storage(path)
                    break
            except Exception as e:
                print(f"⚠️  Failed to load credentials from {path}: {e}")
                continue

        if not client:
            print("🔑 Trying default credential location...")
            client = GoogleAdsClient.load_from_storage()  # Try default

        ga_service = client.get_service("GoogleAdsService")

        # Query for targeting criteria
        targeting_query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign_criterion.type,
            campaign_criterion.criterion_id,
            campaign_criterion.status,
            campaign_criterion.negative
        FROM campaign_criterion
        WHERE {campaign_filter}
        """

        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = targeting_query

        response = ga_service.search(request=search_request)

        # Process and categorize the results
        location_criteria = []
        language_criteria = []
        age_criteria = []
        other_criteria = []

        for row in response:
            criterion_type = row.campaign_criterion.type_
            criterion_id = row.campaign_criterion.criterion_id
            is_negative = row.campaign_criterion.negative
            status = row.campaign_criterion.status

            criterion_info = {
                'id': criterion_id,
                'negative': is_negative,
                'status': status.name,
                'type_code': criterion_type
            }

            if criterion_type == 7:  # LOCATION
                location_criteria.append(criterion_info)
            elif criterion_type == 20:  # LANGUAGE
                language_criteria.append(criterion_info)
            elif criterion_type == 6:  # AGE_RANGE
                age_criteria.append(criterion_info)
            else:
                other_criteria.append(criterion_info)

        # Format the results
        targeting_analysis = []
        targeting_analysis.append("📍 LOCATION TARGETING:")
        targeting_analysis.append("-" * 30)

        if location_criteria:
            for loc in location_criteria:
                prefix = "❌ EXCLUDED:" if loc['negative'] else "✅ INCLUDED:"
                status_icon = "🟢" if loc['status'] == 'ENABLED' else "🟡" if loc['status'] == 'PAUSED' else "🔴"

                # Decode common location IDs
                location_name = decode_location_id(loc['id'])
                targeting_analysis.append(f"  {prefix} {location_name} (ID: {loc['id']}) {status_icon}")
        else:
            targeting_analysis.append("  No explicit location targeting found")

        targeting_analysis.append("\n🗣️ LANGUAGE TARGETING:")
        targeting_analysis.append("-" * 30)

        if language_criteria:
            for lang in language_criteria:
                prefix = "❌ EXCLUDED:" if lang['negative'] else "✅ INCLUDED:"
                status_icon = "🟢" if lang['status'] == 'ENABLED' else "🟡" if lang['status'] == 'PAUSED' else "🔴"

                # Decode common language IDs
                language_name = decode_language_id(lang['id'])
                targeting_analysis.append(f"  {prefix} {language_name} (ID: {lang['id']}) {status_icon}")
        else:
            targeting_analysis.append("  No explicit language targeting found")

        if age_criteria:
            targeting_analysis.append("\n👥 AGE TARGETING:")
            targeting_analysis.append("-" * 30)
            for age in age_criteria:
                age_name = decode_age_range_id(age['id'])
                status_icon = "🟢" if age['status'] == 'ENABLED' else "🟡" if age['status'] == 'PAUSED' else "🔴"
                targeting_analysis.append(f"  ✅ {age_name} (ID: {age['id']}) {status_icon}")

        if other_criteria:
            targeting_analysis.append("\n🎯 OTHER TARGETING:")
            targeting_analysis.append("-" * 30)
            for other in other_criteria:
                targeting_analysis.append(f"  Type {other['type_code']}: ID {other['id']} (Status: {other['status']})")

        targeting_result = "\n".join(targeting_analysis)

    except Exception as e:
        targeting_result = f"❌ Error getting detailed targeting: {e}\nFalling back to basic query..."
        targeting_result += run_gaql_query(customer_id, f"""
        SELECT campaign.id, campaign.name FROM campaign_criterion WHERE {campaign_filter} LIMIT 10
        """)

    return f"{campaign_info}\n{targeting_result}"

def decode_location_id(location_id):
    """Decode common location criterion IDs to readable names."""
    location_map = {
        2840: "United States",
        2124: "Canada",
        2826: "United Kingdom",
        2250: "France",
        2276: "Germany",
        1023191: "New York, NY, USA",
        1014044: "California, USA",
        1023511: "Texas, USA"
    }
    return location_map.get(location_id, f"Location ID {location_id}")

def decode_language_id(language_id):
    """Decode common language criterion IDs to readable names."""
    language_map = {
        1000: "English",
        1003: "Spanish",
        1002: "French",
        1001: "German",
        1004: "Italian",
        1005: "Portuguese"
    }
    return language_map.get(language_id, f"Language ID {language_id}")

def decode_age_range_id(age_id):
    """Decode age range criterion IDs to readable names."""
    age_map = {
        30000: "18-24 years",
        30001: "25-34 years",
        30002: "35-44 years",
        30003: "45-54 years",
        30004: "55-64 years",
        30005: "65+ years"
    }
    return age_map.get(age_id, f"Age Range ID {age_id}")

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Google Ads Campaign Analysis Tool')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--action', required=True,
                       choices=['overview', 'top-campaigns', 'underperforming', 'trends',
                               'device-performance', 'budget-analysis', 'geographic', 'schedule',
                               'targeting', 'targeting-summary', 'diagnose-targeting'],
                       help='Type of campaign analysis to perform')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze (default: 30)')
    parser.add_argument('--metric', default='conversion_value',
                       choices=['conversion_value', 'conversions', 'clicks', 'impressions', 'cost_micros'],
                       help='Metric for top campaigns analysis')
    parser.add_argument('--min-cost', type=int, default=5000000,
                       help='Minimum cost in micros for underperforming analysis')
    parser.add_argument('--campaign-id', type=str,
                       help='Specific campaign ID for targeting analysis')
    parser.add_argument('--campaign-name', type=str,
                       help='Campaign name or partial name for targeting diagnosis')

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
    elif args.action == 'targeting':
        result = get_campaign_targeting_settings(args.customer_id, args.campaign_id)
    elif args.action == 'targeting-summary':
        result = get_campaign_targeting_summary(args.customer_id, args.campaign_id)
    elif args.action == 'diagnose-targeting':
        if not args.campaign_name and not args.campaign_id:
            print("❌ Error: --campaign-name or --campaign-id required for targeting diagnosis")
            return 1
        campaign_identifier = args.campaign_name or args.campaign_id
        result = diagnose_campaign_targeting(args.customer_id, campaign_identifier)

    print(result)

if __name__ == "__main__":
    main()

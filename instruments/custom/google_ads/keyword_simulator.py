#!/usr/bin/env python3
"""
Google Ads Keyword Simulation and Forecasting Tool

This tool provides keyword simulation capabilities by analyzing historical data
and providing recommendations for keyword optimization and expansion.
"""

import sys
import subprocess
import argparse
import os
import json
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

def get_keyword_ideas_and_metrics(customer_id, keyword_texts):
    """Get keyword ideas and metrics using KeywordPlanIdeaService."""
    try:
        # Import Google Ads client
        from google.ads.googleads.client import GoogleAdsClient
        import yaml

        # Load configuration
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(script_dir, "google-ads.yaml")

        if not os.path.exists(config_file):
            return None

        client = GoogleAdsClient.load_from_storage(config_file)
        keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")

        # Create keyword seed
        keyword_seed = client.get_type("KeywordSeed")
        keyword_seed.keywords.extend(keyword_texts)

        # Create keyword plan idea request
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = customer_id
        request.language = "languageConstants/1000"  # English
        request.geo_target_constants.append("geoTargetConstants/2840")  # United States

        # Set keyword seed
        request.keyword_seed = keyword_seed

        # Include adult keywords and set page size
        request.include_adult_keywords = False
        request.page_size = 1000

        print("🔄 Fetching keyword metrics from Google Ads API...")

        # Execute the request
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)

        results = []

        for idea in response.results:
            keyword_text = idea.text

            # Get metrics
            metrics = idea.keyword_idea_metrics
            search_volume = metrics.avg_monthly_searches if metrics.avg_monthly_searches else 0
            competition = metrics.competition.name if metrics.competition else "UNKNOWN"
            competition_index = metrics.competition_index if metrics.competition_index else 0

            # Get bid estimates
            low_bid = 0
            high_bid = 0
            if metrics.low_top_of_page_bid_micros:
                low_bid = metrics.low_top_of_page_bid_micros
            if metrics.high_top_of_page_bid_micros:
                high_bid = metrics.high_top_of_page_bid_micros

            keyword_data = {
                'keyword': keyword_text,
                'avg_monthly_searches': search_volume,
                'competition': competition,
                'competition_index': competition_index,
                'low_top_of_page_bid_micros': low_bid,
                'high_top_of_page_bid_micros': high_bid
            }

            results.append(keyword_data)

        print(f"✅ Retrieved metrics for {len(results)} keyword ideas")
        return results

    except Exception as e:
        print(f"❌ Error getting keyword metrics: {e}")
        return None

def simulate_keyword_performance(customer_id, days=90):
    """Simulate keyword performance based on historical data."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        campaign.name,
        ad_group.name,
        segments.date,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value,
        metrics.ctr,
        metrics.average_cpc,
        metrics.cost_per_conversion
    FROM keyword_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND ad_group_criterion.status = 'ENABLED'
        AND metrics.impressions > 0
    ORDER BY ad_group_criterion.keyword.text, segments.date DESC
    LIMIT 500
    """

    print(f"🔮 Simulating keyword performance based on {days} days of historical data...")
    return run_gaql_query(customer_id, query, "csv")

def analyze_keyword_trends(customer_id, days=60):
    """Analyze keyword performance trends to identify patterns."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        campaign.name,
        segments.week,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr
    FROM keyword_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND campaign.status = 'ENABLED'
        AND metrics.impressions >= 100
    ORDER BY ad_group_criterion.keyword.text, segments.week DESC
    LIMIT 300
    """

    print(f"📈 Analyzing keyword trends over {days} days...")
    return run_gaql_query(customer_id, query, "csv")

def find_keyword_expansion_opportunities(customer_id, days=30):
    """Find new keyword opportunities from search terms and competitor analysis."""
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
        metrics.cost_micros,
        metrics.conversions_value
    FROM search_term_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND metrics.impressions >= 10
        AND metrics.clicks >= 2
        AND campaign.status = 'ENABLED'
    ORDER BY metrics.conversions_value DESC, metrics.clicks DESC
    LIMIT 50
    """

    print(f"🔍 Finding keyword expansion opportunities from search terms...")
    return run_gaql_query(customer_id, query)

def simulate_bid_changes(customer_id, days=30):
    """Simulate the impact of bid changes on keyword performance."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        campaign.name,
        ad_group.name,
        ad_group_criterion.cpc_bid_micros,
        metrics.average_cpc,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.search_impression_share,
        metrics.search_rank_lost_impression_share,
        metrics.search_budget_lost_impression_share
    FROM keyword_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND ad_group_criterion.status = 'ENABLED'
        AND metrics.impressions >= 50
    ORDER BY metrics.search_rank_lost_impression_share DESC
    LIMIT 40
    """

    print(f"💰 Simulating bid optimization opportunities...")
    return run_gaql_query(customer_id, query)

def analyze_seasonal_patterns(customer_id, days=365):
    """Analyze seasonal patterns in keyword performance."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        ad_group_criterion.keyword.text,
        segments.month,
        segments.day_of_week,
        segments.hour,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr
    FROM keyword_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND campaign.status = 'ENABLED'
        AND metrics.impressions >= 100
    ORDER BY ad_group_criterion.keyword.text, segments.month, segments.day_of_week
    LIMIT 500
    """

    print(f"📅 Analyzing seasonal patterns in keyword performance...")
    return run_gaql_query(customer_id, query, "csv")

def predict_keyword_performance(customer_id, keyword_text, days=30):
    """Predict performance for a specific keyword based on similar keywords."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        campaign.name,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value,
        metrics.average_cpc,
        metrics.cost_per_conversion
    FROM keyword_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND campaign.status = 'ENABLED'
        AND ad_group_criterion.keyword.text LIKE '%{keyword_text}%'
        AND metrics.impressions > 0
    ORDER BY metrics.impressions DESC
    LIMIT 20
    """

    print(f"🎯 Predicting performance for keywords similar to '{keyword_text}'...")
    return run_gaql_query(customer_id, query)

def generate_keyword_recommendations(customer_id, days=30):
    """Generate keyword recommendations based on performance analysis."""
    print("🤖 Generating keyword recommendations...")
    print("=" * 50)
    
    # Get underperforming keywords
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    underperforming_query = f"""
    SELECT
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        campaign.name,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.cost_micros,
        metrics.conversions
    FROM keyword_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND campaign.status = 'ENABLED'
        AND metrics.impressions >= 1000
        AND (metrics.ctr < 0.01 OR (metrics.cost_micros > 10000000 AND metrics.conversions = 0))
    ORDER BY metrics.cost_micros DESC
    LIMIT 15
    """
    
    print("❌ Keywords recommended for REMOVAL or BID REDUCTION:")
    underperforming = run_gaql_query(customer_id, underperforming_query)
    print(underperforming)
    
    print("\n" + "=" * 50)
    
    # Get high-potential search terms
    expansion_query = f"""
    SELECT
        search_term_view.search_term,
        campaign.name,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.conversions,
        metrics.conversions_value
    FROM search_term_view
    WHERE
        segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        AND metrics.conversions > 0
        AND metrics.ctr > 0.02
        AND campaign.status = 'ENABLED'
    ORDER BY metrics.conversions_value DESC
    LIMIT 15
    """
    
    print("✅ Search terms recommended for KEYWORD ADDITION:")
    expansion = run_gaql_query(customer_id, expansion_query)
    print(expansion)
    
    return "Keyword recommendations generated successfully!"

def simulate_keywords_from_file(customer_id, keywords_file, days=90):
    """Simulate performance for multiple keywords from a JSON file using KeywordPlanIdeaService."""
    try:
        with open(keywords_file, 'r') as f:
            keywords_data = json.load(f)

        print(f"📊 Getting keyword ideas and metrics for {len(keywords_data)} keywords...")
        print("=" * 60)

        # Extract keyword texts
        keyword_texts = []
        for keyword_info in keywords_data:
            keyword_text = keyword_info.get('text', keyword_info.get('keyword', ''))
            if keyword_text:
                keyword_texts.append(keyword_text)

        if not keyword_texts:
            return "❌ No valid keywords found in file"

        # Get keyword ideas using KeywordPlanIdeaService
        keyword_metrics = get_keyword_ideas_and_metrics(customer_id, keyword_texts)

        if not keyword_metrics:
            return "❌ Failed to get keyword metrics from Google Ads API"

        # Process and format results
        results = []

        print(f"\n📈 KEYWORD METRICS ANALYSIS")
        print("=" * 60)

        for keyword_data in keyword_metrics:
            keyword_text = keyword_data.get('keyword', '')
            search_volume = keyword_data.get('avg_monthly_searches', 0)
            competition = keyword_data.get('competition', 'UNKNOWN')
            competition_index = keyword_data.get('competition_index', 0)
            low_top_bid = keyword_data.get('low_top_of_page_bid_micros', 0) / 1000000
            high_top_bid = keyword_data.get('high_top_of_page_bid_micros', 0) / 1000000

            # Calculate estimated metrics based on industry benchmarks
            # These are estimates since we don't have actual campaign data
            estimated_ctr = 2.0  # Average CTR for search ads
            estimated_conv_rate = 2.5  # Average conversion rate

            # Adjust estimates based on competition
            if competition == 'HIGH':
                estimated_ctr *= 0.8  # Higher competition = lower CTR
                estimated_conv_rate *= 0.9
            elif competition == 'LOW':
                estimated_ctr *= 1.2  # Lower competition = higher CTR
                estimated_conv_rate *= 1.1

            # Calculate potential performance at different bid levels
            avg_bid = (low_top_bid + high_top_bid) / 2 if high_top_bid > 0 else low_top_bid

            # Estimate monthly performance
            monthly_impressions = search_volume * 0.1  # Assume 10% impression share
            monthly_clicks = monthly_impressions * (estimated_ctr / 100)
            monthly_cost = monthly_clicks * avg_bid
            monthly_conversions = monthly_clicks * (estimated_conv_rate / 100)

            keyword_result = {
                'keyword': keyword_text,
                'avg_monthly_searches': search_volume,
                'competition': competition,
                'competition_index': competition_index,
                'low_top_bid': round(low_top_bid, 2),
                'high_top_bid': round(high_top_bid, 2),
                'avg_bid': round(avg_bid, 2),
                'estimated_monthly_impressions': int(monthly_impressions),
                'estimated_monthly_clicks': int(monthly_clicks),
                'estimated_monthly_cost': round(monthly_cost, 2),
                'estimated_monthly_conversions': round(monthly_conversions, 2),
                'estimated_ctr': round(estimated_ctr, 2),
                'estimated_conversion_rate': round(estimated_conv_rate, 2),
                'estimated_cost_per_conversion': round(monthly_cost / monthly_conversions, 2) if monthly_conversions > 0 else 0
            }

            results.append(keyword_result)

            print(f"🔍 {keyword_text}")
            print(f"   Search Volume: {search_volume:,}/month | Competition: {competition} ({competition_index}/100)")
            print(f"   Bid Range: ${low_top_bid:.2f} - ${high_top_bid:.2f}")
            print(f"   Est. Monthly: {int(monthly_clicks)} clicks, ${monthly_cost:.2f} cost, {monthly_conversions:.1f} conversions")
            print()

        # Generate summary report
        if results:
            print(f"\n📈 KEYWORD OPPORTUNITY SUMMARY")
            print("=" * 60)
            print(f"Keywords analyzed: {len(results)}")
            print(f"Analysis based on Google Ads Keyword Planner data")

            print("\n🎯 Best Keywords by Search Volume:")
            sorted_by_volume = sorted(results, key=lambda x: x['avg_monthly_searches'], reverse=True)[:10]
            for i, kw in enumerate(sorted_by_volume, 1):
                print(f"{i:2d}. {kw['keyword']:<35} Volume: {kw['avg_monthly_searches']:>6,}/mo | Competition: {kw['competition']:<6} | Bid: ${kw['avg_bid']:>5.2f}")

            print("\n💰 Most Cost-Effective Keywords (Low Competition + Good Volume):")
            # Score based on volume/competition ratio and reasonable bid
            scored_keywords = []
            for kw in results:
                if kw['avg_monthly_searches'] > 0 and kw['avg_bid'] > 0:
                    # Higher score = better opportunity
                    volume_score = kw['avg_monthly_searches'] / 1000  # Normalize volume
                    competition_penalty = kw['competition_index'] / 100  # 0-1 scale
                    bid_penalty = min(kw['avg_bid'] / 5.0, 1.0)  # Penalize high bids

                    opportunity_score = volume_score * (1 - competition_penalty) * (1 - bid_penalty)
                    scored_keywords.append((kw, opportunity_score))

            scored_keywords.sort(key=lambda x: x[1], reverse=True)

            for i, (kw, score) in enumerate(scored_keywords[:10], 1):
                est_monthly_cost = kw['estimated_monthly_cost']
                est_monthly_conv = kw['estimated_monthly_conversions']
                print(f"{i:2d}. {kw['keyword']:<35} Score: {score:>5.1f} | Est: ${est_monthly_cost:>6.0f}/mo, {est_monthly_conv:>4.1f} conv")

            print("\n📊 Competition Analysis:")
            high_comp = len([k for k in results if k['competition'] == 'HIGH'])
            med_comp = len([k for k in results if k['competition'] == 'MEDIUM'])
            low_comp = len([k for k in results if k['competition'] == 'LOW'])

            print(f"   High Competition: {high_comp} keywords")
            print(f"   Medium Competition: {med_comp} keywords")
            print(f"   Low Competition: {low_comp} keywords")

            avg_volume = sum(k['avg_monthly_searches'] for k in results) / len(results)
            avg_bid = sum(k['avg_bid'] for k in results if k['avg_bid'] > 0) / len([k for k in results if k['avg_bid'] > 0])

            print(f"\n📈 Overall Metrics:")
            print(f"   Average Monthly Searches: {avg_volume:,.0f}")
            print(f"   Average Suggested Bid: ${avg_bid:.2f}")
            print(f"   Total Estimated Monthly Cost: ${sum(k['estimated_monthly_cost'] for k in results):,.2f}")
            print(f"   Total Estimated Monthly Conversions: {sum(k['estimated_monthly_conversions'] for k in results):.1f}")

            return json.dumps(results, indent=2)
        else:
            return "⚠️  No keyword metrics found for any of the provided keywords"

    except FileNotFoundError:
        return f"❌ Keywords file not found: {keywords_file}"
    except json.JSONDecodeError:
        return f"❌ Invalid JSON format in keywords file: {keywords_file}"
    except Exception as e:
        return f"❌ Error processing keywords file: {e}"

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Google Ads Keyword Simulation Tool')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--action', required=True,
                       choices=['simulate', 'trends', 'expansion', 'bid-simulation',
                               'seasonal', 'predict', 'recommendations'],
                       help='Type of simulation/analysis to perform')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze (default: 30)')
    parser.add_argument('--keyword', help='Specific keyword for prediction analysis')
    parser.add_argument('--keywords-file', help='JSON file containing list of keywords for batch simulation')
    
    args = parser.parse_args()
    
    print("🚀 Google Ads Keyword Simulation Tool")
    print("=" * 42)
    
    result = ""

    if args.action == 'simulate':
        if args.keywords_file:
            # Batch simulation from file
            result = simulate_keywords_from_file(args.customer_id, args.keywords_file, args.days)
        else:
            # Original single simulation
            result = simulate_keyword_performance(args.customer_id, args.days)
    elif args.action == 'trends':
        result = analyze_keyword_trends(args.customer_id, args.days)
    elif args.action == 'expansion':
        result = find_keyword_expansion_opportunities(args.customer_id, args.days)
    elif args.action == 'bid-simulation':
        result = simulate_bid_changes(args.customer_id, args.days)
    elif args.action == 'seasonal':
        result = analyze_seasonal_patterns(args.customer_id, args.days)
    elif args.action == 'predict':
        if not args.keyword:
            print("❌ --keyword parameter required for prediction analysis")
            return
        result = predict_keyword_performance(args.customer_id, args.keyword, args.days)
    elif args.action == 'recommendations':
        result = generate_keyword_recommendations(args.customer_id, args.days)
    else:
        result = "❌ Unknown action specified"

    if result:
        print(result)

if __name__ == "__main__":
    main()

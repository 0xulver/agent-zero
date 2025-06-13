#!/usr/bin/env python3
"""
Run GAQL Query Script
Execute custom Google Ads Query Language queries
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from core.google_ads_client import GoogleAdsClient
from core.data_formatter import DataFormatter

def save_results(data, output_dir, filename_prefix):
    """Save results to files"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON
    json_file = output_dir / f"{filename_prefix}_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    return json_file

def get_sample_queries():
    """Return sample GAQL queries"""
    return {
        "campaigns": """
            SELECT 
                campaign.id,
                campaign.name,
                campaign.status,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros
            FROM campaign 
            WHERE segments.date DURING LAST_30DAYS
            ORDER BY metrics.cost_micros DESC
            LIMIT 10
        """,
        "keywords": """
            SELECT 
                keyword.text,
                keyword.match_type,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions
            FROM keyword_view
            WHERE segments.date DURING LAST_30DAYS
            ORDER BY metrics.clicks DESC
            LIMIT 20
        """,
        "ads": """
            SELECT
                ad_group_ad.ad.id,
                ad_group_ad.ad.name,
                campaign.name,
                ad_group.name,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions
            FROM ad_group_ad
            WHERE segments.date DURING LAST_30DAYS
            AND metrics.impressions > 100
            ORDER BY metrics.clicks DESC
            LIMIT 15
        """,
        "account_info": """
            SELECT
                customer.id,
                customer.currency_code,
                customer.time_zone,
                customer.descriptive_name
            FROM customer
            LIMIT 1
        """
    }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Execute Google Ads GAQL queries')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--query', help='GAQL query to execute')
    parser.add_argument('--sample', choices=['campaigns', 'keywords', 'ads', 'account_info'],
                       help='Use a predefined sample query')
    parser.add_argument('--format', choices=['table', 'csv', 'json'], default='table',
                       help='Output format (default: table)')
    parser.add_argument('--list-samples', action='store_true',
                       help='List available sample queries')
    
    args = parser.parse_args()
    
    # List sample queries if requested
    if args.list_samples:
        print("📋 Available sample queries:")
        print("=" * 40)
        samples = get_sample_queries()
        for name, query in samples.items():
            print(f"\n🔍 {name}:")
            print(f"   Usage: --sample {name}")
            print(f"   Query: {query.strip()[:100]}...")
        return
    
    # Validate arguments
    if not args.query and not args.sample:
        print("❌ Error: Either --query or --sample must be specified")
        print("Use --list-samples to see available sample queries")
        sys.exit(1)
    
    # Load environment variables
    config_dir = Path(__file__).parent.parent / "config"
    env_file = config_dir / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
    
    # Determine query to use
    if args.sample:
        samples = get_sample_queries()
        query = samples.get(args.sample)
        if not query:
            print(f"❌ Error: Unknown sample query '{args.sample}'")
            sys.exit(1)
        print(f"📋 Using sample query: {args.sample}")
    else:
        query = args.query
        print(f"📋 Using custom query")
    
    print("🔍 Executing GAQL Query...")
    print("=" * 50)
    print(f"Customer ID: {args.customer_id}")
    print(f"Format: {args.format}")
    print(f"Query: {query.strip()}")
    print()
    
    try:
        # Initialize client
        client = GoogleAdsClient()
        
        # Get currency info for formatting
        print("💰 Getting account currency...")
        currency_result = client.get_account_currency(args.customer_id)
        currency_code = "USD"  # default
        
        if currency_result["success"]:
            currency_code = currency_result["currency_code"]
            print(f"   Currency: {currency_code}")
        else:
            print(f"   Warning: Could not get currency, using {currency_code}")
        
        # Execute query
        print("⚡ Executing query...")
        result = client.execute_gaql_query(args.customer_id, query)
        
        if not result["success"]:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        
        # Format and display results
        formatter = DataFormatter()
        
        if args.format == "table":
            formatted_output = formatter.format_as_table(result, currency_code)
            print(formatted_output)
            
        elif args.format == "csv":
            formatted_output = formatter.format_as_csv(result, currency_code)
            print(formatted_output)
            
        else:  # json
            formatted_output = formatter.format_as_json(result)
            print(formatted_output)
        
        # Save results
        output_dir = Path("/work_dir/google_ads_results")
        query_type = args.sample if args.sample else "custom_query"
        filename_prefix = f"query_{query_type}_{args.customer_id}"
        json_file = save_results(result, output_dir, filename_prefix)
        
        # Save formatted output
        if args.format != "json":
            output_file = output_dir / f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{args.format}"
            with open(output_file, 'w') as f:
                f.write(formatted_output)
            print(f"\n💾 Formatted output saved: {output_file}")
        
        print(f"💾 Raw data saved: {json_file}")
        
        # Show results summary
        if result["results"]:
            print(f"\n📊 Query Results Summary:")
            print(f"   Total results: {len(result['results'])}")
            print(f"   Customer ID: {result['customer_id']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

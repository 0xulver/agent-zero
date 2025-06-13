#!/usr/bin/env python3
"""
Get Performance Data Script
Retrieves campaign or ad performance metrics
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

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Get Google Ads performance data')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--type', choices=['campaign', 'ad'], required=True, 
                       help='Type of performance data to retrieve')
    parser.add_argument('--days', type=int, default=30, 
                       help='Number of days to look back (default: 30)')
    parser.add_argument('--format', choices=['table', 'csv', 'json'], default='table',
                       help='Output format (default: table)')
    
    args = parser.parse_args()
    
    # Load environment variables
    config_dir = Path(__file__).parent.parent / "config"
    env_file = config_dir / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
    
    print(f"📊 Getting {args.type} performance data...")
    print("=" * 50)
    print(f"Customer ID: {args.customer_id}")
    print(f"Days: {args.days}")
    print(f"Format: {args.format}")
    print()
    
    try:
        # Initialize client
        client = GoogleAdsClient()
        
        # Get currency info first
        print("💰 Getting account currency...")
        currency_result = client.get_account_currency(args.customer_id)
        currency_code = "USD"  # default
        
        if currency_result["success"]:
            currency_code = currency_result["currency_code"]
            print(f"   Currency: {currency_code}")
        else:
            print(f"   Warning: Could not get currency, using {currency_code}")
        
        # Get performance data
        print(f"📈 Fetching {args.type} performance data...")
        
        if args.type == "campaign":
            result = client.get_campaign_performance(args.customer_id, args.days)
        else:  # ad
            result = client.get_ad_performance(args.customer_id, args.days)
        
        if not result["success"]:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        
        # Format and display results
        formatter = DataFormatter()
        
        if args.format == "table":
            formatted_output = formatter.format_as_table(result, currency_code)
            print(formatted_output)
            
            # Also create summary
            summary = formatter.create_summary_report(result, args.type, currency_code)
            print("\n" + "="*50)
            print(summary)
            
        elif args.format == "csv":
            formatted_output = formatter.format_as_csv(result, currency_code)
            print(formatted_output)
            
        else:  # json
            formatted_output = formatter.format_as_json(result)
            print(formatted_output)
        
        # Save results
        output_dir = Path("/work_dir/google_ads_results")
        filename_prefix = f"{args.type}_performance_{args.customer_id}_{args.days}days"
        json_file = save_results(result, output_dir, filename_prefix)
        
        # Save formatted output
        if args.format != "json":
            output_file = output_dir / f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{args.format}"
            with open(output_file, 'w') as f:
                f.write(formatted_output)
            print(f"\n💾 Formatted output saved: {output_file}")
        
        print(f"💾 Raw data saved: {json_file}")
        
        # Show key insights
        if result["results"]:
            print(f"\n🔍 Key Insights:")
            print(f"   Total {args.type}s found: {len(result['results'])}")
            
            if args.type == "campaign":
                active_campaigns = [r for r in result["results"] 
                                  if r.get("campaign", {}).get("status") == "ENABLED"]
                print(f"   Active campaigns: {len(active_campaigns)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

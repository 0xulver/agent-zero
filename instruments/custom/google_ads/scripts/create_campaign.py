#!/usr/bin/env python3
"""
Create Campaign Script
Creates a new Google Ads campaign with basic setup
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
from tools.campaign_manager import CampaignManager

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
    parser = argparse.ArgumentParser(description='Create a new Google Ads campaign')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--name', required=True, help='Campaign name')
    parser.add_argument('--budget', type=float, required=True, 
                       help='Daily budget amount in account currency')
    parser.add_argument('--keywords', required=True, 
                       help='Comma-separated list of keywords')
    parser.add_argument('--ad-group-name', 
                       help='Ad group name (default: [Campaign Name] - Ad Group 1)')
    parser.add_argument('--location', default='US',
                       help='Target location (default: US)')
    
    args = parser.parse_args()
    
    # Load environment variables
    config_dir = Path(__file__).parent.parent / "config"
    env_file = config_dir / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
    
    print("🚀 Creating Google Ads Campaign...")
    print("=" * 50)
    print(f"Customer ID: {args.customer_id}")
    print(f"Campaign Name: {args.name}")
    print(f"Budget: {args.budget}")
    print(f"Keywords: {args.keywords}")
    print(f"Ad Group: {args.ad_group_name or f'{args.name} - Ad Group 1'}")
    print(f"Location: {args.location}")
    print()
    
    try:
        # Parse keywords
        keywords = [kw.strip() for kw in args.keywords.split(',')]
        
        # Initialize client and campaign manager
        client = GoogleAdsClient()
        campaign_manager = CampaignManager(client)
        
        # Get account currency first
        print("💰 Getting account currency...")
        currency_result = client.get_account_currency(args.customer_id)
        currency_code = "USD"  # default
        
        if currency_result["success"]:
            currency_code = currency_result["currency_code"]
            print(f"   Currency: {currency_code}")
        else:
            print(f"   Warning: Could not get currency, using {currency_code}")
        
        # Create campaign
        print("🏗️  Creating campaign...")
        result = campaign_manager.create_search_campaign(
            customer_id=args.customer_id,
            campaign_name=args.name,
            budget_amount=args.budget,
            keywords=keywords,
            ad_group_name=args.ad_group_name,
            target_location=args.location
        )
        
        if not result["success"]:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        
        # Display results
        print("✅ Campaign creation completed!")
        print()
        
        if "campaign_details" in result:
            details = result["campaign_details"]
            print("📋 Campaign Details:")
            print(f"   Name: {details['campaign_name']}")
            print(f"   Budget: {details['budget_amount']} {currency_code}/day")
            print(f"   Ad Group: {details['ad_group_name']}")
            print(f"   Keywords: {len(details['keywords'])} keywords")
            print(f"   Location: {details['target_location']}")
            print(f"   Type: {details['campaign_type']}")
            print(f"   Status: {details['status']}")
        
        if "next_steps" in result:
            print("\n📝 Next Steps:")
            for i, step in enumerate(result["next_steps"], 1):
                print(f"   {i}. {step}")
        
        if "warning" in result:
            print(f"\n⚠️  Warning: {result['warning']}")
        
        # Save results
        output_dir = Path("/work_dir/google_ads_results")
        filename_prefix = f"campaign_creation_{args.customer_id}"
        json_file = save_results(result, output_dir, filename_prefix)
        
        print(f"\n💾 Results saved: {json_file}")
        
        # Show keyword summary
        print(f"\n🔍 Keywords to be added:")
        for i, keyword in enumerate(keywords, 1):
            print(f"   {i}. {keyword}")
        
        print(f"\n💡 Tips:")
        print(f"   - Review and test your campaign before enabling")
        print(f"   - Add compelling ad copy")
        print(f"   - Set up conversion tracking")
        print(f"   - Monitor performance regularly")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

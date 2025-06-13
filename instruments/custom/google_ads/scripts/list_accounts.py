#!/usr/bin/env python3
"""
List Google Ads Accounts Script
Shows all accessible Google Ads accounts
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from core.google_ads_client import GoogleAdsClient
from core.data_formatter import DataFormatter

def save_results(data, output_dir):
    """Save results to files"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_file = output_dir / "accounts_list.json"
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    # Save formatted text
    formatter = DataFormatter()
    text_content = formatter.format_accounts_list(data)
    text_file = output_dir / "accounts_list.txt"
    with open(text_file, 'w') as f:
        f.write(text_content)
    
    return json_file, text_file

def main():
    """Main function"""
    # Load environment variables
    config_dir = Path(__file__).parent.parent / "config"
    env_file = config_dir / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
    
    print("📋 Listing Google Ads Accounts...")
    print("=" * 40)
    
    try:
        # Initialize client
        client = GoogleAdsClient()
        
        # Get accounts
        print("🔍 Fetching accessible accounts...")
        result = client.list_accounts()
        
        if not result["success"]:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        
        # Format and display results
        formatter = DataFormatter()
        formatted_output = formatter.format_accounts_list(result)
        print(formatted_output)
        
        # Save results
        output_dir = Path("/work_dir/google_ads_results")
        json_file, text_file = save_results(result, output_dir)
        
        print(f"\n💾 Results saved:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📄 Text: {text_file}")
        
        # Show account IDs for easy copying
        if result["accounts"]:
            print(f"\n📝 Account IDs for use in other scripts:")
            for account in result["accounts"]:
                print(f"   {account['customer_id']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

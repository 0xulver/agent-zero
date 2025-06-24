#!/usr/bin/env python3
"""
Google Ads Campaign Creator

This tool creates actual campaigns, ad groups, keywords, and ads using the Google Ads API.
It handles the complete campaign creation workflow.
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Add the script directory to Python path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

def install_dependencies():
    """Install required dependencies if not available."""
    try:
        import yaml
        from google.ads.googleads.client import GoogleAdsClient
        from google.ads.googleads.errors import GoogleAdsException
    except ImportError:
        print("Installing required dependencies...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "PyYAML", "google-ads"], 
                      capture_output=True, text=True)
        print("✅ Dependencies installed")

def load_config():
    """Load the google-ads.yaml configuration file from multiple possible locations."""
    config_paths = [
        "/a0/google-ads.yaml",           # Primary location when run by Agent Zero
        "google-ads.yaml",               # Current directory (for testing)
        "/root/google-ads.yaml",         # Home directory in container
        os.path.expanduser("~/google-ads.yaml")  # User home directory
    ]
    
    for config_path in config_paths:
        try:
            import yaml
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            print(f"✅ Loaded configuration from {config_path}")
            return config, config_path
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"❌ Error loading config from {config_path}: {e}")
            continue
    
    print(f"❌ Configuration file not found in any of these locations:")
    for path in config_paths:
        print(f"   - {path}")
    return None, None

def create_campaign(client, customer_id, campaign_name, budget_micros):
    """Create a new search campaign."""
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    
    try:
        # Create campaign budget
        campaign_budget_service = client.get_service("CampaignBudgetService")
        campaign_budget_operation = client.get_type("CampaignBudgetOperation")
        campaign_budget = campaign_budget_operation.create
        
        campaign_budget.name = f"{campaign_name} Budget"
        campaign_budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        campaign_budget.amount_micros = budget_micros
        
        # Submit budget creation
        budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[campaign_budget_operation]
        )
        budget_resource_name = budget_response.results[0].resource_name
        print(f"✅ Created campaign budget: {budget_resource_name}")
        
        # Create campaign
        campaign_service = client.get_service("CampaignService")
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        
        campaign.name = campaign_name
        campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        campaign.status = client.enums.CampaignStatusEnum.PAUSED  # Start paused
        campaign.manual_cpc.enhanced_cpc_enabled = True
        campaign.campaign_budget = budget_resource_name
        campaign.network_settings.target_google_search = True
        campaign.network_settings.target_search_network = True
        campaign.network_settings.target_content_network = False
        campaign.network_settings.target_partner_search_network = False
        
        # Submit campaign creation
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        campaign_resource_name = campaign_response.results[0].resource_name
        print(f"✅ Created campaign: {campaign_resource_name}")
        
        return campaign_resource_name
        
    except GoogleAdsException as ex:
        print(f"❌ Campaign creation failed: {ex}")
        return None

def create_ad_group(client, customer_id, campaign_resource_name, ad_group_name, cpc_bid_micros):
    """Create an ad group within a campaign."""
    from google.ads.googleads.errors import GoogleAdsException
    
    try:
        ad_group_service = client.get_service("AdGroupService")
        ad_group_operation = client.get_type("AdGroupOperation")
        ad_group = ad_group_operation.create
        
        ad_group.name = ad_group_name
        ad_group.campaign = campaign_resource_name
        ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
        ad_group.cpc_bid_micros = cpc_bid_micros
        
        # Submit ad group creation
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_operation]
        )
        ad_group_resource_name = ad_group_response.results[0].resource_name
        print(f"✅ Created ad group: {ad_group_resource_name}")
        
        return ad_group_resource_name
        
    except GoogleAdsException as ex:
        print(f"❌ Ad group creation failed: {ex}")
        return None

def create_keywords(client, customer_id, ad_group_resource_name, keywords_data):
    """Create keywords in an ad group."""
    from google.ads.googleads.errors import GoogleAdsException
    
    try:
        ad_group_criterion_service = client.get_service("AdGroupCriterionService")
        operations = []
        
        for keyword_data in keywords_data:
            ad_group_criterion_operation = client.get_type("AdGroupCriterionOperation")
            ad_group_criterion = ad_group_criterion_operation.create
            
            ad_group_criterion.ad_group = ad_group_resource_name
            ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
            ad_group_criterion.keyword.text = keyword_data["text"]
            ad_group_criterion.keyword.match_type = getattr(
                client.enums.KeywordMatchTypeEnum, keyword_data["match_type"]
            )
            
            if "max_cpc_micros" in keyword_data:
                ad_group_criterion.cpc_bid_micros = keyword_data["max_cpc_micros"]
            
            operations.append(ad_group_criterion_operation)
        
        # Submit keyword creation
        keyword_response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=operations
        )
        
        print(f"✅ Created {len(keyword_response.results)} keywords")
        return [result.resource_name for result in keyword_response.results]
        
    except GoogleAdsException as ex:
        print(f"❌ Keyword creation failed: {ex}")
        return []

def create_responsive_search_ad(client, customer_id, ad_group_resource_name, ad_data):
    """Create a responsive search ad."""
    from google.ads.googleads.errors import GoogleAdsException
    
    try:
        ad_group_ad_service = client.get_service("AdGroupAdService")
        ad_group_ad_operation = client.get_type("AdGroupAdOperation")
        ad_group_ad = ad_group_ad_operation.create
        
        ad_group_ad.ad_group = ad_group_resource_name
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.ENABLED
        
        # Create responsive search ad
        responsive_search_ad = ad_group_ad.ad.responsive_search_ad
        
        # Add headlines (minimum 3, maximum 15)
        for headline in ad_data["headlines"][:15]:
            headline_asset = client.get_type("AdTextAsset")
            headline_asset.text = headline
            responsive_search_ad.headlines.append(headline_asset)
        
        # Add descriptions (minimum 2, maximum 4)
        for description in ad_data["descriptions"][:4]:
            description_asset = client.get_type("AdTextAsset")
            description_asset.text = description
            responsive_search_ad.descriptions.append(description_asset)
        
        # Set final URLs
        ad_group_ad.ad.final_urls.append(ad_data.get("final_url", "https://example.com"))
        
        # Submit ad creation
        ad_response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_group_ad_operation]
        )
        
        ad_resource_name = ad_response.results[0].resource_name
        print(f"✅ Created responsive search ad: {ad_resource_name}")
        
        return ad_resource_name
        
    except GoogleAdsException as ex:
        print(f"❌ Ad creation failed: {ex}")
        return None

def create_complete_campaign(customer_id, campaign_config):
    """Create a complete campaign with ad groups, keywords, and ads."""
    install_dependencies()
    
    # Load configuration and initialize client
    config, config_file = load_config()
    if not config:
        return "❌ Failed to load configuration"
    
    try:
        from google.ads.googleads.client import GoogleAdsClient
        client = GoogleAdsClient.load_from_storage(config_file)
        print(f"✅ Google Ads client initialized")
    except Exception as e:
        return f"❌ Failed to initialize Google Ads client: {e}"
    
    print(f"🚀 Creating complete campaign: {campaign_config['name']}")
    
    # Step 1: Create campaign
    campaign_resource_name = create_campaign(
        client, customer_id, 
        campaign_config["name"], 
        campaign_config["budget_micros"]
    )
    
    if not campaign_resource_name:
        return "❌ Failed to create campaign"
    
    # Step 2: Create ad groups with keywords and ads
    created_resources = {
        "campaign": campaign_resource_name,
        "ad_groups": [],
        "keywords": [],
        "ads": []
    }
    
    for ad_group_config in campaign_config["ad_groups"]:
        # Create ad group
        ad_group_resource_name = create_ad_group(
            client, customer_id, campaign_resource_name,
            ad_group_config["name"], ad_group_config["cpc_bid_micros"]
        )
        
        if ad_group_resource_name:
            created_resources["ad_groups"].append(ad_group_resource_name)
            
            # Create keywords
            if "keywords" in ad_group_config:
                keyword_resources = create_keywords(
                    client, customer_id, ad_group_resource_name, 
                    ad_group_config["keywords"]
                )
                created_resources["keywords"].extend(keyword_resources)
            
            # Create ads
            if "ads" in ad_group_config:
                for ad_data in ad_group_config["ads"]:
                    ad_resource = create_responsive_search_ad(
                        client, customer_id, ad_group_resource_name, ad_data
                    )
                    if ad_resource:
                        created_resources["ads"].append(ad_resource)
    
    print(f"🎉 Campaign creation completed!")
    print(f"   Campaign: {campaign_resource_name}")
    print(f"   Ad Groups: {len(created_resources['ad_groups'])}")
    print(f"   Keywords: {len(created_resources['keywords'])}")
    print(f"   Ads: {len(created_resources['ads'])}")
    
    return created_resources

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Google Ads Campaign Creator')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--config-file', required=True, help='JSON file with campaign configuration')
    
    args = parser.parse_args()
    
    print("🚀 Google Ads Campaign Creator")
    print("=" * 35)
    
    # Load campaign configuration
    try:
        with open(args.config_file, 'r') as f:
            campaign_config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config file: {e}")
        return
    
    # Create campaign
    result = create_complete_campaign(args.customer_id, campaign_config)
    
    if isinstance(result, dict):
        print("\n📊 Created Resources:")
        print(json.dumps(result, indent=2))
    else:
        print(result)

if __name__ == "__main__":
    main()

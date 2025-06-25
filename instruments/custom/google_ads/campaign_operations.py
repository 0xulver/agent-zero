#!/usr/bin/env python3
"""
Google Ads Campaign Operations Tool

This tool provides comprehensive campaign management operations including:
- Update campaign status, budgets, and settings
- Manage keywords (pause, enable, update bids, add/remove)
- Manage ads (pause, enable, update copy)
- Manage negative keywords
- Automated optimization operations
- Bid management and adjustments
"""

import sys
import subprocess
import argparse
import os
import json
from datetime import datetime, timedelta

def install_dependencies():
    """Install required dependencies if not already installed."""
    try:
        import google.ads.googleads
    except ImportError:
        print("📦 Installing Google Ads API dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-ads==23.1.0"])
        print("✅ Dependencies installed successfully")

def load_config():
    """Load Google Ads API configuration."""
    config_paths = [
        "/a0/google-ads.yaml",
        "google-ads.yaml",
        os.path.expanduser("~/google-ads.yaml"),
        "/tmp/google-ads.yaml"
    ]

    for config_file in config_paths:
        if os.path.exists(config_file):
            print(f"✅ Found config file: {config_file}")
            return True, config_file

    print(f"❌ Configuration file not found in any of these locations:")
    for path in config_paths:
        print(f"   - {path}")
    return False, None

def update_campaign_status(client, customer_id, campaign_resource_name, status):
    """Update campaign status (ENABLED, PAUSED, REMOVED)."""
    from google.ads.googleads.errors import GoogleAdsException
    
    try:
        campaign_service = client.get_service("CampaignService")
        campaign_operation = client.get_type("CampaignOperation")
        
        campaign = campaign_operation.update
        campaign.resource_name = campaign_resource_name
        
        # Set status
        if status.upper() == "ENABLED":
            campaign.status = client.enums.CampaignStatusEnum.ENABLED
        elif status.upper() == "PAUSED":
            campaign.status = client.enums.CampaignStatusEnum.PAUSED
        elif status.upper() == "REMOVED":
            campaign.status = client.enums.CampaignStatusEnum.REMOVED
        else:
            return f"❌ Invalid status: {status}. Use ENABLED, PAUSED, or REMOVED"
        
        campaign_operation.update_mask.paths.append("status")
        
        response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        
        print(f"✅ Updated campaign status to {status}: {response.results[0].resource_name}")
        return response.results[0].resource_name
        
    except GoogleAdsException as ex:
        return f"❌ Failed to update campaign status: {ex}"

def update_campaign_budget(client, customer_id, campaign_resource_name, budget_micros):
    """Update campaign daily budget."""
    from google.ads.googleads.errors import GoogleAdsException
    
    try:
        # First get the current budget resource name
        campaign_service = client.get_service("CampaignService")
        campaign_query = f"""
        SELECT campaign.campaign_budget
        FROM campaign 
        WHERE campaign.resource_name = '{campaign_resource_name}'
        """
        
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = campaign_query
        
        response = campaign_service.search(request=search_request)
        budget_resource_name = None
        for row in response:
            budget_resource_name = row.campaign.campaign_budget
            break
        
        if not budget_resource_name:
            return "❌ Could not find campaign budget"
        
        # Update the budget
        campaign_budget_service = client.get_service("CampaignBudgetService")
        budget_operation = client.get_type("CampaignBudgetOperation")
        
        budget = budget_operation.update
        budget.resource_name = budget_resource_name
        budget.amount_micros = budget_micros
        
        budget_operation.update_mask.paths.append("amount_micros")
        
        budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[budget_operation]
        )
        
        print(f"✅ Updated campaign budget to ${budget_micros/1000000:.2f}: {budget_response.results[0].resource_name}")
        return budget_response.results[0].resource_name
        
    except GoogleAdsException as ex:
        return f"❌ Failed to update campaign budget: {ex}"

def update_keyword_status(client, customer_id, keyword_resource_name, status):
    """Update keyword status (ENABLED, PAUSED, REMOVED)."""
    from google.ads.googleads.errors import GoogleAdsException
    
    try:
        ad_group_criterion_service = client.get_service("AdGroupCriterionService")
        criterion_operation = client.get_type("AdGroupCriterionOperation")
        
        criterion = criterion_operation.update
        criterion.resource_name = keyword_resource_name
        
        # Set status
        if status.upper() == "ENABLED":
            criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        elif status.upper() == "PAUSED":
            criterion.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
        elif status.upper() == "REMOVED":
            criterion.status = client.enums.AdGroupCriterionStatusEnum.REMOVED
        else:
            return f"❌ Invalid status: {status}. Use ENABLED, PAUSED, or REMOVED"
        
        criterion_operation.update_mask.paths.append("status")
        
        response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=[criterion_operation]
        )
        
        print(f"✅ Updated keyword status to {status}: {response.results[0].resource_name}")
        return response.results[0].resource_name
        
    except GoogleAdsException as ex:
        return f"❌ Failed to update keyword status: {ex}"

def update_keyword_bid(client, customer_id, keyword_resource_name, bid_micros):
    """Update keyword bid amount."""
    from google.ads.googleads.errors import GoogleAdsException
    
    try:
        ad_group_criterion_service = client.get_service("AdGroupCriterionService")
        criterion_operation = client.get_type("AdGroupCriterionOperation")
        
        criterion = criterion_operation.update
        criterion.resource_name = keyword_resource_name
        criterion.cpc_bid_micros = bid_micros
        
        criterion_operation.update_mask.paths.append("cpc_bid_micros")
        
        response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=[criterion_operation]
        )
        
        print(f"✅ Updated keyword bid to ${bid_micros/1000000:.2f}: {response.results[0].resource_name}")
        return response.results[0].resource_name
        
    except GoogleAdsException as ex:
        return f"❌ Failed to update keyword bid: {ex}"

def update_ad_status(client, customer_id, ad_resource_name, status):
    """Update ad status (ENABLED, PAUSED, REMOVED)."""
    from google.ads.googleads.errors import GoogleAdsException
    
    try:
        ad_group_ad_service = client.get_service("AdGroupAdService")
        ad_operation = client.get_type("AdGroupAdOperation")
        
        ad = ad_operation.update
        ad.resource_name = ad_resource_name
        
        # Set status
        if status.upper() == "ENABLED":
            ad.status = client.enums.AdGroupAdStatusEnum.ENABLED
        elif status.upper() == "PAUSED":
            ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
        elif status.upper() == "REMOVED":
            ad.status = client.enums.AdGroupAdStatusEnum.REMOVED
        else:
            return f"❌ Invalid status: {status}. Use ENABLED, PAUSED, or REMOVED"
        
        ad_operation.update_mask.paths.append("status")
        
        response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_operation]
        )
        
        print(f"✅ Updated ad status to {status}: {response.results[0].resource_name}")
        return response.results[0].resource_name
        
    except GoogleAdsException as ex:
        return f"❌ Failed to update ad status: {ex}"

def get_keyword_match_type_enum(client, match_type_string):
    """Convert match type string to proper Google Ads API enum."""
    match_type = match_type_string.upper() if match_type_string else "BROAD"

    print(f"DEBUG: Converting match type string '{match_type_string}' -> '{match_type}'")

    if match_type == "EXACT":
        enum_result = client.enums.KeywordMatchTypeEnum.EXACT
    elif match_type == "PHRASE":
        enum_result = client.enums.KeywordMatchTypeEnum.PHRASE
    elif match_type == "BROAD":
        enum_result = client.enums.KeywordMatchTypeEnum.BROAD
    else:
        # Default to BROAD if unknown match type
        print(f"⚠️ Unknown match type '{match_type}', defaulting to BROAD")
        enum_result = client.enums.KeywordMatchTypeEnum.BROAD

    print(f"DEBUG: Enum result type: {type(enum_result)}, value: {enum_result}")
    print(f"DEBUG: Enum integer value: {int(enum_result)}")
    return enum_result

def check_campaign_match_type_restrictions(client, customer_id, ad_group_resource_name):
    """Check if campaign settings restrict match types to BROAD only."""
    try:
        # Extract campaign ID from ad group resource name
        # Format: customers/{customer_id}/adGroups/{ad_group_id}
        ad_group_id = ad_group_resource_name.split('/')[-1]

        # Get campaign info from ad group
        googleads_service = client.get_service("GoogleAdsService")
        query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.bidding_strategy_type,
            campaign.bidding_strategy_system_status,
            ad_group.id,
            ad_group.name
        FROM ad_group
        WHERE ad_group.id = {ad_group_id}
        """

        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = query

        response = googleads_service.search(request=search_request)

        for row in response:
            campaign_id = row.campaign.id
            campaign_name = row.campaign.name
            bid_strategy = row.campaign.bidding_strategy_type

            print(f"📊 Campaign Analysis:")
            print(f"   Campaign: {campaign_name} (ID: {campaign_id})")
            print(f"   Bid Strategy: {bid_strategy}")

            # Check if bid strategy forces broad match
            conversion_focused_strategies = [
                "MAXIMIZE_CONVERSIONS",
                "MAXIMIZE_CONVERSION_VALUE",
                "TARGET_CPA",
                "TARGET_ROAS"
            ]

            if str(bid_strategy) in conversion_focused_strategies:
                print(f"⚠️  WARNING: Campaign uses {bid_strategy} which may have 'Broad Match Keywords Setting' enabled")
                print(f"   This forces ALL keywords to behave as BROAD match regardless of specified match type")
                print(f"   PHRASE and EXACT match types will be automatically converted to BROAD")
                return True, campaign_name, str(bid_strategy)
            else:
                print(f"✅ Campaign uses {bid_strategy} - PHRASE and EXACT match types should work")
                return False, campaign_name, str(bid_strategy)

        return False, "Unknown", "Unknown"

    except Exception as e:
        print(f"⚠️  Could not check campaign settings: {e}")
        print(f"   Proceeding with BROAD match conversion as safety measure")
        return True, "Unknown", "Unknown"

def add_keywords_to_ad_group(client, customer_id, ad_group_resource_name, keywords_data):
    """Add new keywords to an existing ad group."""
    from google.ads.googleads.errors import GoogleAdsException

    try:
        # First, check campaign settings for match type restrictions
        has_restrictions, campaign_name, bid_strategy = check_campaign_match_type_restrictions(
            client, customer_id, ad_group_resource_name
        )

        ad_group_criterion_service = client.get_service("AdGroupCriterionService")
        operations = []

        print(f"\n🔧 Processing {len(keywords_data)} keywords for campaign: {campaign_name}")

        for i, keyword_data in enumerate(keywords_data):
            print(f"\n--- Keyword {i+1}/{len(keywords_data)} ---")
            criterion_operation = client.get_type("AdGroupCriterionOperation")
            criterion = criterion_operation.create

            # Set match type based on campaign analysis
            match_type_string = keyword_data.get("match_type", "BROAD")
            original_keyword = keyword_data["text"]

            if has_restrictions and match_type_string.upper() in ["EXACT", "PHRASE"]:
                print(f"🔄 CAMPAIGN RESTRICTION: {match_type_string} → BROAD conversion required")
                print(f"   Reason: Campaign '{campaign_name}' uses {bid_strategy}")
                print(f"   This bid strategy enables 'Broad Match Keywords Setting'")
                print(f"   Original: '{original_keyword}' ({match_type_string})")

                if match_type_string.upper() == "EXACT":
                    # For EXACT keywords, add quotes to maintain precision with BROAD match
                    keyword_text = f'"{original_keyword}"'
                    print(f"   Converted: '{keyword_text}' (BROAD with quotes for precision)")
                else:
                    # For PHRASE keywords, use as-is with BROAD match
                    keyword_text = original_keyword
                    print(f"   Converted: '{keyword_text}' (BROAD)")

                criterion.keyword.match_type = 4  # BROAD

            elif not has_restrictions and match_type_string.upper() in ["EXACT", "PHRASE"]:
                print(f"✅ ATTEMPTING: {match_type_string} match type (campaign allows it)")
                print(f"   Keyword: '{original_keyword}' ({match_type_string})")
                keyword_text = original_keyword

                # Try to use the requested match type
                if match_type_string.upper() == "EXACT":
                    criterion.keyword.match_type = 2  # EXACT
                elif match_type_string.upper() == "PHRASE":
                    criterion.keyword.match_type = 3  # PHRASE
                else:
                    criterion.keyword.match_type = 4  # BROAD

            else:
                # BROAD match type - always works
                print(f"✅ BROAD match type: '{original_keyword}'")
                keyword_text = original_keyword
                criterion.keyword.match_type = 4  # BROAD

            criterion.keyword.text = keyword_text
            criterion.ad_group = ad_group_resource_name

            # Set bid if provided
            if "bid_micros" in keyword_data:
                criterion.cpc_bid_micros = keyword_data["bid_micros"]

            operations.append(criterion_operation)

        # WORKAROUND: Process one operation at a time to avoid library serialization bug
        results = []
        for i, operation in enumerate(operations):
            print(f"DEBUG: Sending operation {i+1}/{len(operations)} to API...")
            try:
                response = ad_group_criterion_service.mutate_ad_group_criteria(
                    customer_id=customer_id, operations=[operation]
                )
                results.extend([result.resource_name for result in response.results])
                print(f"✅ Successfully added keyword {i+1}")
            except Exception as e:
                print(f"❌ Failed to add keyword {i+1}: {e}")
                return f"❌ Failed to add keyword {i+1}: {e}"

        print(f"✅ Added {len(results)} keywords to ad group")
        return results

    except GoogleAdsException as ex:
        return f"❌ Failed to add keywords: {ex}"

def add_negative_keywords(client, customer_id, campaign_resource_name, negative_keywords):
    """Add negative keywords to a campaign."""
    from google.ads.googleads.errors import GoogleAdsException

    try:
        campaign_criterion_service = client.get_service("CampaignCriterionService")
        operations = []

        for neg_keyword in negative_keywords:
            criterion_operation = client.get_type("CampaignCriterionOperation")
            criterion = criterion_operation.create

            criterion.campaign = campaign_resource_name
            criterion.negative = True
            criterion.keyword.text = neg_keyword["text"]

            # Set match type using direct integer assignment like debug script
            match_type_string = neg_keyword.get("match_type", "BROAD")
            if match_type_string.upper() == "EXACT":
                criterion.keyword.match_type = 2
            elif match_type_string.upper() == "PHRASE":
                criterion.keyword.match_type = 3
            elif match_type_string.upper() == "BROAD":
                criterion.keyword.match_type = 4
            else:
                criterion.keyword.match_type = 4  # Default to BROAD

            operations.append(criterion_operation)

        response = campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=operations
        )

        print(f"✅ Added {len(response.results)} negative keywords to campaign")
        return [result.resource_name for result in response.results]

    except GoogleAdsException as ex:
        return f"❌ Failed to add negative keywords: {ex}"

def create_ad_group(client, customer_id, campaign_resource_name, ad_group_name, cpc_bid_micros):
    """Create a new ad group within an existing campaign."""
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
        return f"❌ Ad group creation failed: {ex}"

def create_ad_group_with_content(client, customer_id, campaign_resource_name, ad_group_config):
    """Create a complete ad group with keywords and ads in an existing campaign."""
    from google.ads.googleads.errors import GoogleAdsException

    try:
        # Step 1: Create the ad group
        ad_group_resource_name = create_ad_group(
            client, customer_id, campaign_resource_name,
            ad_group_config["name"], ad_group_config["cpc_bid_micros"]
        )

        if ad_group_resource_name.startswith("❌"):
            return ad_group_resource_name

        created_resources = {
            "ad_group": ad_group_resource_name,
            "keywords": [],
            "ads": []
        }

        # Step 2: Add keywords if provided
        if "keywords" in ad_group_config and ad_group_config["keywords"]:
            keyword_resources = add_keywords_to_ad_group(
                client, customer_id, ad_group_resource_name,
                ad_group_config["keywords"]
            )
            if isinstance(keyword_resources, list):
                created_resources["keywords"] = keyword_resources
            else:
                print(f"⚠️ Warning: {keyword_resources}")

        # Step 3: Create ads if provided
        if "ads" in ad_group_config and ad_group_config["ads"]:
            for ad_data in ad_group_config["ads"]:
                ad_resource = create_responsive_search_ad(
                    client, customer_id, ad_group_resource_name, ad_data
                )
                if ad_resource and not ad_resource.startswith("❌"):
                    created_resources["ads"].append(ad_resource)
                else:
                    print(f"⚠️ Warning: {ad_resource}")

        print(f"✅ Created complete ad group with {len(created_resources['keywords'])} keywords and {len(created_resources['ads'])} ads")
        return created_resources

    except Exception as ex:
        return f"❌ Failed to create ad group with content: {ex}"

def create_responsive_search_ad(client, customer_id, ad_group_resource_name, ad_data):
    """Create a responsive search ad in an ad group."""
    from google.ads.googleads.errors import GoogleAdsException

    try:
        ad_group_ad_service = client.get_service("AdGroupAdService")
        ad_group_ad_operation = client.get_type("AdGroupAdOperation")

        ad_group_ad = ad_group_ad_operation.create
        ad_group_ad.ad_group = ad_group_resource_name
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.ENABLED

        # Create responsive search ad
        ad_group_ad.ad.type_ = client.enums.AdTypeEnum.RESPONSIVE_SEARCH_AD

        # Add headlines
        for headline_text in ad_data.get("headlines", []):
            headline = client.get_type("AdTextAsset")
            headline.text = headline_text[:30]  # Google Ads limit
            ad_group_ad.ad.responsive_search_ad.headlines.append(headline)

        # Add descriptions
        for description_text in ad_data.get("descriptions", []):
            description = client.get_type("AdTextAsset")
            description.text = description_text[:90]  # Google Ads limit
            ad_group_ad.ad.responsive_search_ad.descriptions.append(description)

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
        return f"❌ Ad creation failed: {ex}"

def pause_underperforming_keywords(client, customer_id, min_impressions=100, max_ctr=0.02, days=30):
    """Automatically pause underperforming keywords based on performance thresholds."""
    from google.ads.googleads.errors import GoogleAdsException

    try:
        # First, get underperforming keywords
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        query = f"""
        SELECT
            ad_group_criterion.resource_name,
            ad_group_criterion.keyword.text,
            campaign.name,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr
        FROM keyword_view
        WHERE
            campaign.status = 'ENABLED'
            AND ad_group.status = 'ENABLED'
            AND ad_group_criterion.status = 'ENABLED'
            AND segments.date >= '{start_date}'
            AND segments.date <= '{end_date}'
            AND metrics.impressions >= {min_impressions}
            AND metrics.ctr <= {max_ctr}
        """

        googleads_service = client.get_service("GoogleAdsService")
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = query

        response = googleads_service.search(request=search_request)

        # Pause the underperforming keywords
        paused_keywords = []
        for row in response:
            keyword_resource = row.ad_group_criterion.resource_name
            result = update_keyword_status(client, customer_id, keyword_resource, "PAUSED")
            if not result.startswith("❌"):
                paused_keywords.append({
                    "resource_name": keyword_resource,
                    "keyword": row.ad_group_criterion.keyword.text,
                    "campaign": row.campaign.name,
                    "ad_group": row.ad_group.name,
                    "impressions": row.metrics.impressions,
                    "ctr": row.metrics.ctr
                })

        print(f"✅ Paused {len(paused_keywords)} underperforming keywords")
        return paused_keywords

    except GoogleAdsException as ex:
        return f"❌ Failed to pause underperforming keywords: {ex}"

def optimize_keyword_bids(client, customer_id, target_position=3, days=30):
    """Automatically adjust keyword bids based on performance to achieve target position."""
    from google.ads.googleads.errors import GoogleAdsException

    try:
        # Get keyword performance data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        query = f"""
        SELECT
            ad_group_criterion.resource_name,
            ad_group_criterion.keyword.text,
            ad_group_criterion.cpc_bid_micros,
            metrics.average_position,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc
        FROM keyword_view
        WHERE
            campaign.status = 'ENABLED'
            AND ad_group.status = 'ENABLED'
            AND ad_group_criterion.status = 'ENABLED'
            AND segments.date >= '{start_date}'
            AND segments.date <= '{end_date}'
            AND metrics.impressions >= 50
        """

        googleads_service = client.get_service("GoogleAdsService")
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = query

        response = googleads_service.search(request=search_request)

        # Adjust bids based on position
        optimized_keywords = []
        for row in response:
            current_position = row.metrics.average_position
            current_bid = row.ad_group_criterion.cpc_bid_micros
            keyword_resource = row.ad_group_criterion.resource_name

            # Calculate bid adjustment
            new_bid = current_bid
            if current_position > target_position:
                # Increase bid by 20% if position is worse than target
                new_bid = int(current_bid * 1.2)
            elif current_position < target_position - 1:
                # Decrease bid by 10% if position is much better than target
                new_bid = int(current_bid * 0.9)

            # Apply bid change if significant
            if abs(new_bid - current_bid) > current_bid * 0.05:  # 5% threshold
                result = update_keyword_bid(client, customer_id, keyword_resource, new_bid)
                if not result.startswith("❌"):
                    optimized_keywords.append({
                        "resource_name": keyword_resource,
                        "keyword": row.ad_group_criterion.keyword.text,
                        "old_bid": current_bid / 1000000,
                        "new_bid": new_bid / 1000000,
                        "position": current_position
                    })

        print(f"✅ Optimized bids for {len(optimized_keywords)} keywords")
        return optimized_keywords

    except GoogleAdsException as ex:
        return f"❌ Failed to optimize keyword bids: {ex}"

def bulk_update_campaign_budgets(client, customer_id, budget_adjustments):
    """Update multiple campaign budgets in bulk."""
    results = []

    for adjustment in budget_adjustments:
        campaign_resource = adjustment["campaign_resource_name"]
        new_budget = adjustment["budget_micros"]

        result = update_campaign_budget(client, customer_id, campaign_resource, new_budget)
        results.append({
            "campaign": campaign_resource,
            "budget": new_budget / 1000000,
            "result": result
        })

    return results

def perform_campaign_operations(customer_id, operation_type, **kwargs):
    """Main function to perform various campaign operations."""
    install_dependencies()

    # Load configuration and initialize client
    config_exists, config_file = load_config()
    if not config_exists:
        return "❌ Failed to load configuration"

    try:
        from google.ads.googleads.client import GoogleAdsClient
        client = GoogleAdsClient.load_from_storage(config_file)
        print(f"✅ Google Ads client initialized")
    except Exception as e:
        return f"❌ Failed to initialize Google Ads client: {e}"

    print(f"🔧 Performing operation: {operation_type}")

    if operation_type == "update_campaign_status":
        return update_campaign_status(
            client, customer_id,
            kwargs["campaign_resource_name"],
            kwargs["status"]
        )

    elif operation_type == "update_campaign_budget":
        return update_campaign_budget(
            client, customer_id,
            kwargs["campaign_resource_name"],
            kwargs["budget_micros"]
        )

    elif operation_type == "update_keyword_status":
        return update_keyword_status(
            client, customer_id,
            kwargs["keyword_resource_name"],
            kwargs["status"]
        )

    elif operation_type == "update_keyword_bid":
        return update_keyword_bid(
            client, customer_id,
            kwargs["keyword_resource_name"],
            kwargs["bid_micros"]
        )

    elif operation_type == "update_ad_status":
        return update_ad_status(
            client, customer_id,
            kwargs["ad_resource_name"],
            kwargs["status"]
        )

    elif operation_type == "add_keywords":
        return add_keywords_to_ad_group(
            client, customer_id,
            kwargs["ad_group_resource_name"],
            kwargs["keywords_data"]
        )

    elif operation_type == "add_negative_keywords":
        return add_negative_keywords(
            client, customer_id,
            kwargs["campaign_resource_name"],
            kwargs["negative_keywords"]
        )

    elif operation_type == "pause_underperforming":
        return pause_underperforming_keywords(
            client, customer_id,
            kwargs.get("min_impressions", 100),
            kwargs.get("max_ctr", 0.02),
            kwargs.get("days", 30)
        )

    elif operation_type == "optimize_bids":
        return optimize_keyword_bids(
            client, customer_id,
            kwargs.get("target_position", 3),
            kwargs.get("days", 30)
        )

    elif operation_type == "bulk_budget_update":
        return bulk_update_campaign_budgets(
            client, customer_id,
            kwargs["budget_adjustments"]
        )

    elif operation_type == "create_ad_group":
        return create_ad_group(
            client, customer_id,
            kwargs["campaign_resource_name"],
            kwargs["ad_group_name"],
            kwargs["cpc_bid_micros"]
        )

    elif operation_type == "create_ad_group_with_content":
        return create_ad_group_with_content(
            client, customer_id,
            kwargs["campaign_resource_name"],
            kwargs["ad_group_config"]
        )

    else:
        return f"❌ Unknown operation type: {operation_type}"

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Google Ads Campaign Operations Tool')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--operation', required=True,
                       choices=[
                           'update_campaign_status', 'update_campaign_budget',
                           'update_keyword_status', 'update_keyword_bid',
                           'update_ad_status', 'add_keywords', 'add_negative_keywords',
                           'pause_underperforming', 'optimize_bids', 'bulk_budget_update',
                           'create_ad_group', 'create_ad_group_with_content'
                       ],
                       help='Operation to perform')

    # Campaign operations
    parser.add_argument('--campaign-resource-name', help='Campaign resource name')
    parser.add_argument('--status', choices=['ENABLED', 'PAUSED', 'REMOVED'], help='Status to set')
    parser.add_argument('--budget-micros', type=int, help='Budget in micros (e.g., 50000000 = $50)')

    # Keyword operations
    parser.add_argument('--keyword-resource-name', help='Keyword resource name')
    parser.add_argument('--ad-group-resource-name', help='Ad group resource name')
    parser.add_argument('--bid-micros', type=int, help='Bid in micros (e.g., 1000000 = $1)')

    # Ad operations
    parser.add_argument('--ad-resource-name', help='Ad resource name')

    # Ad group creation
    parser.add_argument('--ad-group-name', help='Name for new ad group')
    parser.add_argument('--ad-group-config-file', help='JSON file with complete ad group configuration')

    # Bulk operations
    parser.add_argument('--keywords-file', help='JSON file with keywords data')
    parser.add_argument('--negative-keywords-file', help='JSON file with negative keywords')
    parser.add_argument('--budget-adjustments-file', help='JSON file with budget adjustments')

    # Optimization parameters
    parser.add_argument('--min-impressions', type=int, default=100, help='Minimum impressions for optimization')
    parser.add_argument('--max-ctr', type=float, default=0.02, help='Maximum CTR for underperforming keywords')
    parser.add_argument('--target-position', type=float, default=3.0, help='Target average position for bid optimization')
    parser.add_argument('--days', type=int, default=30, help='Days of data to analyze')

    args = parser.parse_args()

    print("🔧 Google Ads Campaign Operations Tool")
    print("=" * 42)

    # Prepare operation parameters
    kwargs = {}

    if args.operation == 'update_campaign_status':
        if not args.campaign_resource_name or not args.status:
            print("❌ --campaign-resource-name and --status required")
            return
        kwargs = {
            "campaign_resource_name": args.campaign_resource_name,
            "status": args.status
        }

    elif args.operation == 'update_campaign_budget':
        if not args.campaign_resource_name or not args.budget_micros:
            print("❌ --campaign-resource-name and --budget-micros required")
            return
        kwargs = {
            "campaign_resource_name": args.campaign_resource_name,
            "budget_micros": args.budget_micros
        }

    elif args.operation == 'update_keyword_status':
        if not args.keyword_resource_name or not args.status:
            print("❌ --keyword-resource-name and --status required")
            return
        kwargs = {
            "keyword_resource_name": args.keyword_resource_name,
            "status": args.status
        }

    elif args.operation == 'update_keyword_bid':
        if not args.keyword_resource_name or not args.bid_micros:
            print("❌ --keyword-resource-name and --bid-micros required")
            return
        kwargs = {
            "keyword_resource_name": args.keyword_resource_name,
            "bid_micros": args.bid_micros
        }

    elif args.operation == 'update_ad_status':
        if not args.ad_resource_name or not args.status:
            print("❌ --ad-resource-name and --status required")
            return
        kwargs = {
            "ad_resource_name": args.ad_resource_name,
            "status": args.status
        }

    elif args.operation == 'add_keywords':
        if not args.ad_group_resource_name or not args.keywords_file:
            print("❌ --ad-group-resource-name and --keywords-file required")
            return
        try:
            with open(args.keywords_file, 'r') as f:
                keywords_data = json.load(f)
            kwargs = {
                "ad_group_resource_name": args.ad_group_resource_name,
                "keywords_data": keywords_data
            }
        except Exception as e:
            print(f"❌ Failed to load keywords file: {e}")
            return

    elif args.operation == 'add_negative_keywords':
        if not args.campaign_resource_name or not args.negative_keywords_file:
            print("❌ --campaign-resource-name and --negative-keywords-file required")
            return
        try:
            with open(args.negative_keywords_file, 'r') as f:
                negative_keywords = json.load(f)
            kwargs = {
                "campaign_resource_name": args.campaign_resource_name,
                "negative_keywords": negative_keywords
            }
        except Exception as e:
            print(f"❌ Failed to load negative keywords file: {e}")
            return

    elif args.operation == 'pause_underperforming':
        kwargs = {
            "min_impressions": args.min_impressions,
            "max_ctr": args.max_ctr,
            "days": args.days
        }

    elif args.operation == 'optimize_bids':
        kwargs = {
            "target_position": args.target_position,
            "days": args.days
        }

    elif args.operation == 'bulk_budget_update':
        if not args.budget_adjustments_file:
            print("❌ --budget-adjustments-file required")
            return
        try:
            with open(args.budget_adjustments_file, 'r') as f:
                budget_adjustments = json.load(f)
            kwargs = {
                "budget_adjustments": budget_adjustments
            }
        except Exception as e:
            print(f"❌ Failed to load budget adjustments file: {e}")
            return

    elif args.operation == 'create_ad_group':
        if not args.campaign_resource_name or not args.ad_group_name or not args.bid_micros:
            print("❌ --campaign-resource-name, --ad-group-name, and --bid-micros required")
            return
        kwargs = {
            "campaign_resource_name": args.campaign_resource_name,
            "ad_group_name": args.ad_group_name,
            "cpc_bid_micros": args.bid_micros
        }

    elif args.operation == 'create_ad_group_with_content':
        if not args.campaign_resource_name or not args.ad_group_config_file:
            print("❌ --campaign-resource-name and --ad-group-config-file required")
            return
        try:
            with open(args.ad_group_config_file, 'r') as f:
                ad_group_config = json.load(f)
            kwargs = {
                "campaign_resource_name": args.campaign_resource_name,
                "ad_group_config": ad_group_config
            }
        except Exception as e:
            print(f"❌ Failed to load ad group config file: {e}")
            return

    # Perform the operation
    result = perform_campaign_operations(args.customer_id, args.operation, **kwargs)

    # Output results
    if isinstance(result, (dict, list)):
        print("\n📊 Operation Results:")
        print(json.dumps(result, indent=2))
    else:
        print(f"\n📋 Result: {result}")

if __name__ == "__main__":
    main()

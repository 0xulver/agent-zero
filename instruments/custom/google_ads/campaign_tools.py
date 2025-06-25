"""
Campaign Management Tools

This module provides classes and functions for Google Ads campaign
management, operations, and analysis.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

try:
    from .utils import get_google_ads_client, validate_customer_id, format_currency
    from .query_runner import run_gaql_query
except ImportError:
    from utils import get_google_ads_client, validate_customer_id, format_currency
    from query_runner import run_gaql_query


class CampaignManager:
    """Class for high-level campaign management operations."""
    
    def __init__(self, customer_id: str, config_path: Optional[str] = None):
        self.customer_id = validate_customer_id(customer_id)
        self.client = get_google_ads_client(config_path)
    
    def list_campaigns(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all campaigns with optional status filter."""
        query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            campaign_budget.amount_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM campaign
        WHERE campaign.status != 'REMOVED'
        """
        
        if status_filter:
            query += f" AND campaign.status = '{status_filter.upper()}'"
        
        query += " ORDER BY campaign.name"
        
        result = run_gaql_query(self.customer_id, query, "raw")
        return result if isinstance(result, list) else []
    
    def get_campaign_performance(self, campaign_id: str, days: int = 30) -> Dict[str, Any]:
        """Get performance metrics for a specific campaign."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_per_conversion
        FROM campaign
        WHERE campaign.id = {campaign_id}
        AND segments.date >= '{start_date}'
        AND segments.date <= '{end_date}'
        """
        
        result = run_gaql_query(self.customer_id, query, "raw")
        return result[0] if isinstance(result, list) and result else {}


class CampaignOperations:
    """Class for specific campaign operations like keyword management."""
    
    def __init__(self, customer_id: str, config_path: Optional[str] = None):
        self.customer_id = validate_customer_id(customer_id)
        self.client = get_google_ads_client(config_path)
    
    def add_keywords_to_ad_group(self, ad_group_resource_name: str, 
                               keywords_data: List[Dict[str, Any]]) -> List[str]:
        """Add keywords to an ad group."""
        try:
            ad_group_criterion_service = self.client.get_service("AdGroupCriterionService")
            operations = []
            
            for keyword_data in keywords_data:
                operation = self.client.get_type("AdGroupCriterionOperation")
                criterion = operation.create
                
                # Set keyword properties
                criterion.ad_group = ad_group_resource_name
                criterion.keyword.text = keyword_data["text"]
                
                # Handle match type
                match_type = keyword_data.get("match_type", "BROAD").upper()
                if match_type == "EXACT":
                    criterion.keyword.match_type = self.client.enums.KeywordMatchTypeEnum.EXACT
                elif match_type == "PHRASE":
                    criterion.keyword.match_type = self.client.enums.KeywordMatchTypeEnum.PHRASE
                else:
                    criterion.keyword.match_type = self.client.enums.KeywordMatchTypeEnum.BROAD
                
                # Set bid if provided
                if "bid_micros" in keyword_data:
                    criterion.cpc_bid_micros = keyword_data["bid_micros"]
                
                operations.append(operation)
            
            # Execute operations
            response = ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=self.customer_id, operations=operations
            )
            
            return [result.resource_name for result in response.results]
            
        except Exception as e:
            raise RuntimeError(f"Failed to add keywords: {e}")
    
    def pause_keywords(self, keyword_resource_names: List[str]) -> bool:
        """Pause specified keywords."""
        try:
            ad_group_criterion_service = self.client.get_service("AdGroupCriterionService")
            operations = []
            
            for resource_name in keyword_resource_names:
                operation = self.client.get_type("AdGroupCriterionOperation")
                criterion = operation.update
                criterion.resource_name = resource_name
                criterion.status = self.client.enums.AdGroupCriterionStatusEnum.PAUSED
                operation.update_mask = self.client.get_type("FieldMask")
                operation.update_mask.paths.append("status")
                
                operations.append(operation)
            
            # Execute operations
            ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=self.customer_id, operations=operations
            )
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Failed to pause keywords: {e}")
    
    def update_keyword_bids(self, keyword_bids: List[Dict[str, Any]]) -> bool:
        """Update bids for specified keywords."""
        try:
            ad_group_criterion_service = self.client.get_service("AdGroupCriterionService")
            operations = []
            
            for keyword_bid in keyword_bids:
                operation = self.client.get_type("AdGroupCriterionOperation")
                criterion = operation.update
                criterion.resource_name = keyword_bid["resource_name"]
                criterion.cpc_bid_micros = keyword_bid["bid_micros"]
                
                operation.update_mask = self.client.get_type("FieldMask")
                operation.update_mask.paths.append("cpc_bid_micros")
                
                operations.append(operation)
            
            # Execute operations
            ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=self.customer_id, operations=operations
            )
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Failed to update keyword bids: {e}")
    
    def create_ad_group(self, campaign_resource_name: str, ad_group_name: str,
                       cpc_bid_micros: int = 1000000) -> str:
        """Create a new ad group in a campaign."""
        try:
            ad_group_service = self.client.get_service("AdGroupService")
            
            operation = self.client.get_type("AdGroupOperation")
            ad_group = operation.create
            
            ad_group.name = ad_group_name
            ad_group.campaign = campaign_resource_name
            ad_group.status = self.client.enums.AdGroupStatusEnum.ENABLED
            ad_group.type_ = self.client.enums.AdGroupTypeEnum.SEARCH_STANDARD
            ad_group.cpc_bid_micros = cpc_bid_micros
            
            response = ad_group_service.mutate_ad_groups(
                customer_id=self.customer_id, operations=[operation]
            )
            
            return response.results[0].resource_name
            
        except Exception as e:
            raise RuntimeError(f"Failed to create ad group: {e}")


def analyze_campaign_performance(customer_id: str, days: int = 30) -> str:
    """Generate a campaign performance analysis report."""
    manager = CampaignManager(customer_id)
    campaigns = manager.list_campaigns("ENABLED")
    
    if not campaigns:
        return "No enabled campaigns found."
    
    report = []
    report.append(f"Campaign Performance Analysis ({days} days)")
    report.append("=" * 60)
    
    total_impressions = 0
    total_clicks = 0
    total_cost = 0
    total_conversions = 0
    
    for campaign in campaigns:
        impressions = campaign.get('metrics.impressions', 0)
        clicks = campaign.get('metrics.clicks', 0)
        cost = campaign.get('metrics.cost_micros', 0) / 1_000_000
        conversions = campaign.get('metrics.conversions', 0)
        
        total_impressions += impressions
        total_clicks += clicks
        total_cost += cost
        total_conversions += conversions
        
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cpc = cost / clicks if clicks > 0 else 0
        
        report.append(f"\n📊 {campaign.get('campaign.name', 'Unknown')}")
        report.append(f"   Status: {campaign.get('campaign.status', 'Unknown')}")
        report.append(f"   Type: {campaign.get('campaign.advertising_channel_type', 'Unknown')}")
        report.append(f"   Impressions: {impressions:,}")
        report.append(f"   Clicks: {clicks:,} (CTR: {ctr:.2f}%)")
        report.append(f"   Cost: ${cost:.2f} (CPC: ${cpc:.2f})")
        report.append(f"   Conversions: {conversions}")
    
    # Summary
    overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    overall_cpc = total_cost / total_clicks if total_clicks > 0 else 0
    
    report.append(f"\n📈 OVERALL SUMMARY")
    report.append(f"   Total Impressions: {total_impressions:,}")
    report.append(f"   Total Clicks: {total_clicks:,} (CTR: {overall_ctr:.2f}%)")
    report.append(f"   Total Cost: ${total_cost:.2f} (CPC: ${overall_cpc:.2f})")
    report.append(f"   Total Conversions: {total_conversions}")
    
    return "\n".join(report)

"""
Keyword Research and Simulation Tools

This module provides classes and functions for keyword research,
analysis, and performance simulation using the Google Ads API.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

try:
    from .utils import get_google_ads_client, validate_customer_id, format_currency, format_percentage
    from .query_runner import run_gaql_query
except ImportError:
    from utils import get_google_ads_client, validate_customer_id, format_currency, format_percentage
    from query_runner import run_gaql_query


class KeywordResearcher:
    """Class for keyword research and analysis."""
    
    def __init__(self, customer_id: str, config_path: Optional[str] = None):
        self.customer_id = validate_customer_id(customer_id)
        self.client = get_google_ads_client(config_path)
    
    def get_keyword_ideas(self, seed_keywords: List[str], language: str = "en", 
                         country: str = "US") -> List[Dict[str, Any]]:
        """Get keyword ideas using KeywordPlanIdeaService."""
        try:
            keyword_plan_idea_service = self.client.get_service("KeywordPlanIdeaService")
            
            # Create keyword seed
            keyword_seed = self.client.get_type("KeywordSeed")
            keyword_seed.keywords.extend(seed_keywords)
            
            # Create request
            request = self.client.get_type("GenerateKeywordIdeasRequest")
            request.customer_id = self.customer_id
            request.language = f"languageConstants/1000"  # English
            request.geo_target_constants.append("geoTargetConstants/2840")  # United States
            request.keyword_seed = keyword_seed
            request.include_adult_keywords = False
            request.page_size = 1000
            
            # Execute request
            response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
            
            results = []
            for idea in response.results:
                metrics = idea.keyword_idea_metrics
                
                keyword_data = {
                    'keyword': idea.text,
                    'avg_monthly_searches': metrics.avg_monthly_searches if metrics.avg_monthly_searches else 0,
                    'competition': metrics.competition.name if metrics.competition else "UNKNOWN",
                    'competition_index': metrics.competition_index if metrics.competition_index else 0,
                    'low_top_bid_micros': metrics.low_top_of_page_bid_micros if metrics.low_top_of_page_bid_micros else 0,
                    'high_top_bid_micros': metrics.high_top_of_page_bid_micros if metrics.high_top_of_page_bid_micros else 0,
                }
                
                results.append(keyword_data)
            
            return results
            
        except Exception as e:
            raise RuntimeError(f"Failed to get keyword ideas: {e}")
    
    def analyze_existing_keywords(self, days: int = 30) -> List[Dict[str, Any]]:
        """Analyze performance of existing keywords."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        query = f"""
        SELECT
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            campaign.name,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc,
            metrics.search_impression_share
        FROM keyword_view
        WHERE
            segments.date >= '{start_date}'
            AND segments.date <= '{end_date}'
            AND campaign.status = 'ENABLED'
            AND ad_group.status = 'ENABLED'
            AND ad_group_criterion.status = 'ENABLED'
        ORDER BY metrics.impressions DESC
        """
        
        result = run_gaql_query(self.customer_id, query, "raw")
        return result if isinstance(result, list) else []


class KeywordSimulator:
    """Class for keyword performance simulation."""
    
    def __init__(self, customer_id: str, config_path: Optional[str] = None):
        self.customer_id = validate_customer_id(customer_id)
        self.client = get_google_ads_client(config_path)
        self.researcher = KeywordResearcher(customer_id, config_path)
    
    def simulate_keywords_from_list(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Simulate performance for a list of keywords."""
        # Get keyword ideas and metrics
        keyword_data = self.researcher.get_keyword_ideas(keywords)
        
        results = []
        for kw in keyword_data:
            # Calculate estimated performance
            search_volume = kw['avg_monthly_searches']
            competition = kw['competition']
            low_bid = kw['low_top_bid_micros'] / 1_000_000
            high_bid = kw['high_top_bid_micros'] / 1_000_000
            avg_bid = (low_bid + high_bid) / 2 if high_bid > 0 else low_bid
            
            # Estimate CTR based on competition
            if competition == 'HIGH':
                estimated_ctr = 1.5
                estimated_conv_rate = 2.0
            elif competition == 'MEDIUM':
                estimated_ctr = 2.0
                estimated_conv_rate = 2.5
            else:  # LOW
                estimated_ctr = 2.5
                estimated_conv_rate = 3.0
            
            # Calculate monthly estimates (assuming 10% impression share)
            monthly_impressions = search_volume * 0.1
            monthly_clicks = monthly_impressions * (estimated_ctr / 100)
            monthly_cost = monthly_clicks * avg_bid
            monthly_conversions = monthly_clicks * (estimated_conv_rate / 100)
            
            result = {
                'keyword': kw['keyword'],
                'search_volume': search_volume,
                'competition': competition,
                'competition_index': kw['competition_index'],
                'avg_bid': round(avg_bid, 2),
                'estimated_monthly_impressions': int(monthly_impressions),
                'estimated_monthly_clicks': int(monthly_clicks),
                'estimated_monthly_cost': round(monthly_cost, 2),
                'estimated_monthly_conversions': round(monthly_conversions, 2),
                'estimated_ctr': estimated_ctr,
                'estimated_conversion_rate': estimated_conv_rate,
                'cost_per_conversion': round(monthly_cost / monthly_conversions, 2) if monthly_conversions > 0 else 0
            }
            
            results.append(result)
        
        return results
    
    def find_opportunity_keywords(self, keywords: List[str], 
                                min_volume: int = 100, 
                                max_competition_index: int = 70) -> List[Dict[str, Any]]:
        """Find keywords with good opportunity (volume vs competition)."""
        all_results = self.simulate_keywords_from_list(keywords)
        
        opportunities = []
        for result in all_results:
            if (result['search_volume'] >= min_volume and 
                result['competition_index'] <= max_competition_index):
                
                # Calculate opportunity score
                volume_score = result['search_volume'] / 1000
                competition_penalty = result['competition_index'] / 100
                bid_penalty = min(result['avg_bid'] / 5.0, 1.0)
                
                opportunity_score = volume_score * (1 - competition_penalty) * (1 - bid_penalty)
                result['opportunity_score'] = round(opportunity_score, 2)
                
                opportunities.append(result)
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        return opportunities


def analyze_keyword_competition(customer_id: str, days: int = 30) -> str:
    """Analyze keyword competition for existing keywords."""
    researcher = KeywordResearcher(customer_id)
    keywords = researcher.analyze_existing_keywords(days)
    
    if not keywords:
        return "No keyword data found for the specified period."
    
    # Analyze competition levels
    high_comp = len([k for k in keywords if k.get('competition') == 'HIGH'])
    med_comp = len([k for k in keywords if k.get('competition') == 'MEDIUM'])
    low_comp = len([k for k in keywords if k.get('competition') == 'LOW'])
    
    report = []
    report.append(f"Keyword Competition Analysis ({days} days)")
    report.append("=" * 50)
    report.append(f"Total keywords analyzed: {len(keywords)}")
    report.append(f"High competition: {high_comp}")
    report.append(f"Medium competition: {med_comp}")
    report.append(f"Low competition: {low_comp}")
    
    # Top performing keywords
    top_keywords = sorted(keywords, key=lambda x: x.get('metrics.impressions', 0), reverse=True)[:10]
    
    report.append("\nTop 10 Keywords by Impressions:")
    report.append("-" * 40)
    for i, kw in enumerate(top_keywords, 1):
        impressions = kw.get('metrics.impressions', 0)
        clicks = kw.get('metrics.clicks', 0)
        ctr = kw.get('metrics.ctr', 0) * 100
        keyword_text = kw.get('ad_group_criterion.keyword.text', 'Unknown')
        
        report.append(f"{i:2d}. {keyword_text:<30} {impressions:>6,} imp | {clicks:>4} clicks | {ctr:>5.1f}% CTR")
    
    return "\n".join(report)

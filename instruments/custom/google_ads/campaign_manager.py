#!/usr/bin/env python3
"""
Google Ads Campaign Management Tool

This tool provides comprehensive campaign management capabilities including:
- Creating new campaigns
- Managing ad groups
- Creating and updating ads
- Managing keywords
- Setting bids and budgets
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

def create_campaign_structure(customer_id, campaign_name, budget_micros, keywords_data, ad_copy_data):
    """
    Create a complete campaign structure with ad groups, keywords, and ads.
    
    Args:
        customer_id: Google Ads customer ID
        campaign_name: Name for the new campaign
        budget_micros: Daily budget in micros (e.g., 50000000 = $50)
        keywords_data: List of dicts with keyword info
        ad_copy_data: Dict with ad copy elements
    """
    print(f"🚀 Creating campaign structure for '{campaign_name}'...")
    
    # This would use the Google Ads API mutate operations
    # For now, we'll provide the structure and queries needed
    
    campaign_structure = {
        "campaign": {
            "name": campaign_name,
            "budget_micros": budget_micros,
            "status": "PAUSED",  # Start paused for review
            "advertising_channel_type": "SEARCH",
            "bidding_strategy_type": "MAXIMIZE_CLICKS"
        },
        "ad_groups": [],
        "keywords": keywords_data,
        "ads": ad_copy_data
    }
    
    print("📋 Campaign structure prepared:")
    print(json.dumps(campaign_structure, indent=2))
    
    return campaign_structure

def get_campaign_templates():
    """Get predefined campaign templates for different business types."""
    templates = {
        "lead_generation": {
            "bidding_strategy": "MAXIMIZE_CONVERSIONS",
            "ad_groups": ["Main Keywords", "Branded", "Competitor"],
            "ad_extensions": ["sitelinks", "callouts", "structured_snippets"],
            "targeting": {
                "locations": ["United States"],
                "languages": ["English"],
                "devices": ["desktop", "mobile", "tablet"]
            }
        },
        "ecommerce": {
            "bidding_strategy": "TARGET_ROAS",
            "ad_groups": ["Product Categories", "Brand Terms", "Generic Terms"],
            "ad_extensions": ["price", "promotion", "sitelinks"],
            "targeting": {
                "locations": ["United States"],
                "languages": ["English"],
                "devices": ["desktop", "mobile", "tablet"]
            }
        },
        "local_business": {
            "bidding_strategy": "MAXIMIZE_CLICKS",
            "ad_groups": ["Services", "Location", "Emergency"],
            "ad_extensions": ["location", "call", "sitelinks"],
            "targeting": {
                "locations": ["radius_around_business"],
                "languages": ["English"],
                "devices": ["mobile", "desktop"]
            }
        }
    }
    
    print("📋 Available campaign templates:")
    for template_name, template_data in templates.items():
        print(f"\n🎯 {template_name.upper()}:")
        print(f"   Bidding: {template_data['bidding_strategy']}")
        print(f"   Ad Groups: {', '.join(template_data['ad_groups'])}")
        print(f"   Extensions: {', '.join(template_data['ad_extensions'])}")
    
    return templates

def generate_ad_copy(business_type, keywords, unique_selling_points, call_to_action="Learn More"):
    """
    Generate ad copy variations based on keywords and business information.
    
    Args:
        business_type: Type of business (e.g., "education", "fitness", "consulting")
        keywords: List of target keywords
        unique_selling_points: List of USPs
        call_to_action: CTA text
    """
    print(f"✍️  Generating ad copy for {business_type} business...")
    
    # Ad copy templates based on business type
    templates = {
        "education": {
            "headlines": [
                "Master {keyword} Skills Today",
                "Professional {keyword} Training",
                "Learn {keyword} From Experts",
                "{keyword} Certification Course",
                "Transform Your {keyword} Skills"
            ],
            "descriptions": [
                "Join thousands who've mastered {keyword}. Expert instruction, proven results.",
                "Professional {keyword} training with lifetime access. Start your journey today.",
                "Get certified in {keyword}. Industry-recognized program with job placement support."
            ]
        },
        "fitness": {
            "headlines": [
                "Get Fit With {keyword}",
                "Professional {keyword} Training",
                "Transform Your Body Today",
                "{keyword} Classes Near You",
                "Expert {keyword} Coaching"
            ],
            "descriptions": [
                "Professional {keyword} training. Achieve your fitness goals with expert guidance.",
                "Join our {keyword} program. Proven results, supportive community, flexible schedule.",
                "Transform your fitness with {keyword}. Personal training available."
            ]
        },
        "consulting": {
            "headlines": [
                "Expert {keyword} Consulting",
                "Grow Your Business Today",
                "Professional {keyword} Services",
                "{keyword} Strategy That Works",
                "Results-Driven {keyword}"
            ],
            "descriptions": [
                "Expert {keyword} consulting. Proven strategies to grow your business fast.",
                "Professional {keyword} services. Get results with our proven methodology.",
                "Transform your business with expert {keyword} consulting. Free consultation."
            ]
        }
    }
    
    # Generate ad variations
    ad_variations = []
    template = templates.get(business_type, templates["consulting"])
    
    for i, keyword in enumerate(keywords[:5]):  # Limit to 5 keywords
        # Create headline variations
        headlines = []
        for headline_template in template["headlines"][:3]:
            headline = headline_template.format(keyword=keyword.title())
            if len(headline) <= 30:  # Google Ads headline limit
                headlines.append(headline)
        
        # Create description variations
        descriptions = []
        for desc_template in template["descriptions"][:2]:
            description = desc_template.format(keyword=keyword)
            if len(description) <= 90:  # Google Ads description limit
                descriptions.append(description)
        
        # Add USPs to descriptions if space allows
        if unique_selling_points:
            usp_desc = f"{unique_selling_points[0]}. {call_to_action}!"
            if len(usp_desc) <= 90:
                descriptions.append(usp_desc)
        
        ad_variation = {
            "ad_group": f"{keyword.title()} Ad Group",
            "headlines": headlines,
            "descriptions": descriptions,
            "final_url": "https://example.com",  # Would be provided by user
            "display_url": "example.com"
        }
        
        ad_variations.append(ad_variation)
    
    print(f"📝 Generated {len(ad_variations)} ad variations:")
    for i, ad in enumerate(ad_variations, 1):
        print(f"\n🎯 Ad Variation {i} - {ad['ad_group']}:")
        print(f"   Headlines: {ad['headlines']}")
        print(f"   Descriptions: {ad['descriptions']}")
    
    return ad_variations

def create_keyword_list(seed_keywords, match_types=["EXACT", "PHRASE", "BROAD"]):
    """
    Create a comprehensive keyword list with different match types.
    
    Args:
        seed_keywords: List of base keywords
        match_types: List of match types to create
    """
    print(f"🔑 Creating keyword list from {len(seed_keywords)} seed keywords...")
    
    keyword_list = []
    
    for keyword in seed_keywords:
        for match_type in match_types:
            keyword_entry = {
                "text": keyword.lower(),
                "match_type": match_type,
                "max_cpc_micros": 2000000,  # $2.00 default max CPC
                "status": "ENABLED"
            }
            keyword_list.append(keyword_entry)
    
    # Add keyword variations
    variations = []
    for keyword in seed_keywords:
        # Add common variations
        if "class" in keyword.lower():
            variations.append(keyword.replace("class", "course"))
            variations.append(keyword.replace("class", "training"))
        if "training" in keyword.lower():
            variations.append(keyword.replace("training", "course"))
            variations.append(keyword.replace("training", "class"))
    
    # Add variations to keyword list
    for variation in variations:
        for match_type in ["EXACT", "PHRASE"]:  # Only exact and phrase for variations
            keyword_entry = {
                "text": variation.lower(),
                "match_type": match_type,
                "max_cpc_micros": 1500000,  # $1.50 for variations
                "status": "ENABLED"
            }
            keyword_list.append(keyword_entry)
    
    print(f"📊 Created {len(keyword_list)} keyword entries:")
    for match_type in match_types:
        count = len([k for k in keyword_list if k["match_type"] == match_type])
        print(f"   {match_type}: {count} keywords")
    
    return keyword_list

def optimize_campaign_settings(campaign_data, performance_goals):
    """
    Optimize campaign settings based on performance goals.
    
    Args:
        campaign_data: Current campaign configuration
        performance_goals: Dict with target CPA, ROAS, etc.
    """
    print("⚙️  Optimizing campaign settings...")
    
    optimizations = {
        "bidding_strategy": "MAXIMIZE_CONVERSIONS",
        "target_cpa_micros": performance_goals.get("target_cpa_micros", 50000000),  # $50
        "budget_adjustments": [],
        "keyword_adjustments": [],
        "ad_schedule": {
            "enabled": True,
            "peak_hours": [9, 10, 11, 14, 15, 16, 17, 18, 19, 20],
            "bid_modifier": 1.2
        },
        "device_adjustments": {
            "mobile": 0.9,  # 10% decrease for mobile
            "tablet": 0.8,  # 20% decrease for tablet
            "desktop": 1.0  # Baseline
        }
    }
    
    print("🎯 Recommended optimizations:")
    print(f"   Bidding Strategy: {optimizations['bidding_strategy']}")
    print(f"   Target CPA: ${optimizations['target_cpa_micros'] / 1000000}")
    print(f"   Peak Hours Bid Modifier: +{(optimizations['ad_schedule']['bid_modifier'] - 1) * 100}%")
    print(f"   Device Modifiers: Mobile {optimizations['device_adjustments']['mobile']}x, Tablet {optimizations['device_adjustments']['tablet']}x")
    
    return optimizations

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Google Ads Campaign Management Tool')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--action', required=True, 
                       choices=['create-structure', 'templates', 'generate-ads', 'create-keywords', 'optimize'],
                       help='Campaign management action to perform')
    parser.add_argument('--campaign-name', help='Name for new campaign')
    parser.add_argument('--budget', type=int, default=50000000, help='Daily budget in micros (default: $50)')
    parser.add_argument('--business-type', default='consulting', 
                       choices=['education', 'fitness', 'consulting'],
                       help='Type of business for ad copy generation')
    parser.add_argument('--keywords', nargs='+', help='List of seed keywords')
    parser.add_argument('--usps', nargs='+', help='Unique selling points')
    parser.add_argument('--cta', default='Learn More', help='Call to action text')
    
    args = parser.parse_args()
    
    print("🚀 Google Ads Campaign Management Tool")
    print("=" * 44)
    
    if args.action == 'templates':
        result = get_campaign_templates()
    elif args.action == 'generate-ads':
        if not args.keywords:
            print("❌ --keywords parameter required for ad generation")
            return
        result = generate_ad_copy(args.business_type, args.keywords, args.usps or [], args.cta)
    elif args.action == 'create-keywords':
        if not args.keywords:
            print("❌ --keywords parameter required for keyword creation")
            return
        result = create_keyword_list(args.keywords)
    elif args.action == 'create-structure':
        if not args.campaign_name or not args.keywords:
            print("❌ --campaign-name and --keywords parameters required")
            return
        keywords_data = create_keyword_list(args.keywords)
        ad_copy_data = generate_ad_copy(args.business_type, args.keywords, args.usps or [], args.cta)
        result = create_campaign_structure(args.customer_id, args.campaign_name, args.budget, keywords_data, ad_copy_data)
    elif args.action == 'optimize':
        performance_goals = {"target_cpa_micros": 50000000}  # Default $50 CPA
        result = optimize_campaign_settings({}, performance_goals)
    else:
        result = "❌ Unknown action specified"
    
    if isinstance(result, (dict, list)):
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

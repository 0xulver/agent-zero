#!/usr/bin/env python3
"""
Google Ads Campaign Configuration Generator

This tool generates complete campaign configurations that can be used with the campaign_creator.py
to actually create campaigns in Google Ads. It combines keyword research, ad copy generation,
and campaign structure planning.
"""

import sys
import argparse
import json
import os
from datetime import datetime

def generate_keyword_variations(seed_keywords, match_types=["EXACT", "PHRASE", "BROAD"]):
    """Generate keyword variations with different match types."""
    
    keywords = []
    
    for seed_keyword in seed_keywords:
        # Add base keyword with all match types
        for match_type in match_types:
            keywords.append({
                "text": seed_keyword.lower(),
                "match_type": match_type,
                "max_cpc_micros": 2000000  # $2.00 default
            })
        
        # Generate variations
        variations = []
        base = seed_keyword.lower()
        
        # Add common variations
        if "class" in base:
            variations.extend([
                base.replace("class", "course"),
                base.replace("class", "training"),
                base.replace("class", "lesson")
            ])
        
        if "training" in base:
            variations.extend([
                base.replace("training", "course"),
                base.replace("training", "class"),
                base.replace("training", "program")
            ])
        
        # Add location-based variations if applicable
        if "near me" not in base:
            variations.append(f"{base} near me")
            variations.append(f"local {base}")
        
        # Add intent-based variations
        variations.extend([
            f"best {base}",
            f"professional {base}",
            f"affordable {base}",
            f"{base} cost",
            f"{base} price"
        ])
        
        # Add variations with exact and phrase match only
        for variation in variations:
            if variation != base:  # Avoid duplicates
                for match_type in ["EXACT", "PHRASE"]:
                    keywords.append({
                        "text": variation,
                        "match_type": match_type,
                        "max_cpc_micros": 1500000  # $1.50 for variations
                    })
    
    return keywords

def create_ad_group_structure(keywords, ad_copy_data, max_keywords_per_group=20):
    """Create ad group structure from keywords and ad copy."""
    
    # Group keywords by theme
    keyword_themes = {}
    
    for keyword in keywords:
        # Simple theme detection based on first significant word
        words = keyword["text"].split()
        theme_word = None
        
        # Skip common words to find theme
        skip_words = ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
        for word in words:
            if word not in skip_words and len(word) > 2:
                theme_word = word
                break
        
        if not theme_word:
            theme_word = "main"
        
        if theme_word not in keyword_themes:
            keyword_themes[theme_word] = []
        keyword_themes[theme_word].append(keyword)
    
    # Create ad groups
    ad_groups = []
    
    for theme, theme_keywords in keyword_themes.items():
        # Split large keyword groups
        keyword_chunks = [theme_keywords[i:i + max_keywords_per_group] 
                         for i in range(0, len(theme_keywords), max_keywords_per_group)]
        
        for i, keyword_chunk in enumerate(keyword_chunks):
            suffix = f" {i+1}" if len(keyword_chunks) > 1 else ""
            
            # Find relevant ad copy for this theme
            relevant_headlines = []
            relevant_descriptions = []
            
            for ad_group_data in ad_copy_data.get("ad_groups", []):
                # Check if this ad group is relevant to the theme
                if theme.lower() in ad_group_data["name"].lower() or any(
                    theme.lower() in kw.lower() for kw in ad_group_data.get("keywords", [])
                ):
                    relevant_headlines.extend(ad_group_data.get("headlines", []))
                    relevant_descriptions.extend(ad_group_data.get("descriptions", []))
            
            # Use general ad copy if no theme-specific copy found
            if not relevant_headlines and ad_copy_data.get("ad_groups"):
                first_ad_group = ad_copy_data["ad_groups"][0]
                relevant_headlines = first_ad_group.get("headlines", [])
                relevant_descriptions = first_ad_group.get("descriptions", [])
            
            ad_group = {
                "name": f"{theme.title()}{suffix}",
                "cpc_bid_micros": 2000000,  # $2.00 default bid
                "keywords": keyword_chunk,
                "ads": [{
                    "headlines": relevant_headlines[:15],  # Max 15 headlines
                    "descriptions": relevant_descriptions[:4],  # Max 4 descriptions
                    "final_url": "https://example.com",  # To be updated by user
                    "display_url": "example.com"
                }]
            }
            
            ad_groups.append(ad_group)
    
    return ad_groups

def generate_campaign_config(campaign_name, keywords, business_info, budget_daily_micros=50000000):
    """Generate complete campaign configuration."""
    
    print(f"🏗️  Generating campaign configuration for '{campaign_name}'...")
    
    # Generate keyword variations
    keyword_list = generate_keyword_variations(keywords)
    print(f"   Generated {len(keyword_list)} keyword variations")
    
    # Generate ad copy using the ad_copy_generator
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ad_copy_script = os.path.join(script_dir, "ad_copy_generator.py")
    
    # Create temporary file for ad copy
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        # Run ad copy generator
        import subprocess
        cmd = [
            sys.executable, ad_copy_script,
            "--campaign-name", campaign_name,
            "--keywords"] + keywords + [
            "--industry", business_info.get("industry", "general"),
            "--output-file", temp_file
        ]
        
        if business_info.get("brand_name"):
            cmd.extend(["--brand-name", business_info["brand_name"]])
        
        if business_info.get("location"):
            cmd.extend(["--location", business_info["location"]])
        
        if business_info.get("unique_selling_points"):
            cmd.extend(["--usps"] + business_info["unique_selling_points"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            with open(temp_file, 'r') as f:
                ad_copy_data = json.load(f)
            print(f"   Generated ad copy with {len(ad_copy_data.get('ad_groups', []))} ad group themes")
        else:
            print(f"   Warning: Ad copy generation failed, using basic templates")
            ad_copy_data = {"ad_groups": []}
    
    except Exception as e:
        print(f"   Warning: Could not generate ad copy ({e}), using basic templates")
        ad_copy_data = {"ad_groups": []}
    
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass
    
    # Create ad group structure
    ad_groups = create_ad_group_structure(keyword_list, ad_copy_data)
    print(f"   Created {len(ad_groups)} ad groups")
    
    # Build complete campaign configuration
    campaign_config = {
        "name": campaign_name,
        "budget_micros": budget_daily_micros,
        "advertising_channel_type": "SEARCH",
        "bidding_strategy": "MAXIMIZE_CLICKS",
        "status": "PAUSED",  # Start paused for review
        "network_settings": {
            "target_google_search": True,
            "target_search_network": True,
            "target_content_network": False,
            "target_partner_search_network": False
        },
        "ad_groups": ad_groups,
        "campaign_level_settings": {
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date": None,
            "ad_rotation": "OPTIMIZE",
            "frequency_cap": None
        },
        "targeting": {
            "locations": business_info.get("target_locations", ["United States"]),
            "languages": business_info.get("target_languages", ["English"]),
            "demographics": business_info.get("demographics", {}),
            "audiences": business_info.get("audiences", [])
        },
        "extensions": ad_copy_data.get("ad_groups", [{}])[0].get("extensions", {}),
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "total_keywords": len(keyword_list),
            "total_ad_groups": len(ad_groups),
            "estimated_daily_budget": f"${budget_daily_micros / 1000000:.2f}",
            "business_info": business_info
        }
    }
    
    return campaign_config

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Google Ads Campaign Configuration Generator')
    parser.add_argument('--campaign-name', required=True, help='Name of the campaign')
    parser.add_argument('--keywords', nargs='+', required=True, help='Seed keywords for the campaign')
    parser.add_argument('--budget', type=int, default=50000000, help='Daily budget in micros (default: $50)')
    parser.add_argument('--industry', default='general', help='Industry type')
    parser.add_argument('--brand-name', help='Business/brand name')
    parser.add_argument('--location', help='Business location')
    parser.add_argument('--target-locations', nargs='+', default=["United States"], help='Target locations')
    parser.add_argument('--usps', nargs='+', help='Unique selling points')
    parser.add_argument('--output-file', help='Output JSON file for campaign config')
    
    args = parser.parse_args()
    
    print("🚀 Google Ads Campaign Configuration Generator")
    print("=" * 50)
    
    # Prepare business info
    business_info = {
        "industry": args.industry,
        "brand_name": args.brand_name,
        "location": args.location,
        "target_locations": args.target_locations,
        "target_languages": ["English"],
        "unique_selling_points": args.usps or []
    }
    
    # Generate campaign configuration
    campaign_config = generate_campaign_config(
        args.campaign_name,
        args.keywords,
        business_info,
        args.budget
    )
    
    # Output results
    output_file = args.output_file or f"{args.campaign_name.lower().replace(' ', '_')}_config.json"
    
    with open(output_file, 'w') as f:
        json.dump(campaign_config, f, indent=2)
    
    print(f"\n💾 Campaign configuration saved to: {output_file}")
    print(f"📊 Configuration Summary:")
    print(f"   Campaign: {campaign_config['name']}")
    print(f"   Daily Budget: ${campaign_config['budget_micros'] / 1000000:.2f}")
    print(f"   Ad Groups: {len(campaign_config['ad_groups'])}")
    print(f"   Total Keywords: {campaign_config['metadata']['total_keywords']}")
    print(f"   Target Locations: {', '.join(campaign_config['targeting']['locations'])}")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Review the configuration in {output_file}")
    print(f"   2. Update final URLs in the ad groups")
    print(f"   3. Run: python campaign_creator.py --customer-id YOUR_ID --config-file {output_file}")

if __name__ == "__main__":
    main()

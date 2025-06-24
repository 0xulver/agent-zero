#!/usr/bin/env python3
"""
Google Ads Ad Copy Generator

This tool generates high-converting ad copy using proven templates and best practices.
It creates headlines, descriptions, and complete ad variations optimized for different industries.
"""

import sys
import argparse
import json
import re
from datetime import datetime

def generate_headlines(keywords, business_info, industry="general"):
    """Generate compelling headlines for Google Ads."""
    
    # Industry-specific headline templates
    templates = {
        "education": [
            "Master {keyword} in {timeframe}",
            "Professional {keyword} Training",
            "Learn {keyword} From Experts",
            "{keyword} Certification Course",
            "Transform Your {keyword} Skills",
            "Expert {keyword} Instruction",
            "Get {keyword} Certified Today",
            "Advanced {keyword} Program",
            "{keyword} Mastery Course",
            "Professional {keyword} Academy"
        ],
        "fitness": [
            "Get Fit With {keyword}",
            "Professional {keyword} Training",
            "Transform Your Body Today",
            "{keyword} Classes Near You",
            "Expert {keyword} Coaching",
            "Achieve Your {keyword} Goals",
            "Personal {keyword} Training",
            "{keyword} Transformation",
            "Elite {keyword} Program",
            "Results-Driven {keyword}"
        ],
        "consulting": [
            "Expert {keyword} Consulting",
            "Grow Your Business Today",
            "Professional {keyword} Services",
            "{keyword} Strategy That Works",
            "Results-Driven {keyword}",
            "Transform Your {keyword}",
            "Expert {keyword} Solutions",
            "Proven {keyword} Methods",
            "{keyword} Success Formula",
            "Strategic {keyword} Advice"
        ],
        "ecommerce": [
            "Best {keyword} Deals",
            "Premium {keyword} Collection",
            "Top-Rated {keyword} Store",
            "Quality {keyword} Products",
            "Exclusive {keyword} Offers",
            "Shop {keyword} Online",
            "Trusted {keyword} Retailer",
            "Affordable {keyword} Options",
            "{keyword} Sale - Save Big",
            "Free Shipping on {keyword}"
        ],
        "healthcare": [
            "Expert {keyword} Care",
            "Professional {keyword} Services",
            "Trusted {keyword} Specialists",
            "Advanced {keyword} Treatment",
            "Compassionate {keyword} Care",
            "Leading {keyword} Clinic",
            "Experienced {keyword} Team",
            "Quality {keyword} Solutions",
            "Personalized {keyword} Care",
            "Modern {keyword} Facility"
        ]
    }
    
    # Get templates for the industry
    industry_templates = templates.get(industry, templates["general"] if "general" in templates else templates["consulting"])
    
    headlines = []
    
    for keyword in keywords[:5]:  # Limit to 5 keywords
        keyword_clean = keyword.lower().strip()
        keyword_title = keyword.title()
        
        for template in industry_templates:
            # Replace placeholders
            headline = template.format(
                keyword=keyword_title,
                timeframe=business_info.get("timeframe", "30 Days"),
                location=business_info.get("location", "")
            )
            
            # Ensure headline meets Google Ads requirements
            if len(headline) <= 30 and headline not in headlines:
                headlines.append(headline)
    
    # Add business-specific headlines
    if business_info.get("brand_name"):
        brand_headlines = [
            f"{business_info['brand_name']} - Trusted Choice",
            f"Choose {business_info['brand_name']}",
            f"{business_info['brand_name']} Experts"
        ]
        headlines.extend([h for h in brand_headlines if len(h) <= 30])
    
    # Add urgency/action headlines
    action_headlines = [
        "Start Today - Free Trial",
        "Limited Time Offer",
        "Book Your Consultation",
        "Get Started Now",
        "Free Quote Available"
    ]
    headlines.extend([h for h in action_headlines if len(h) <= 30])
    
    return headlines[:15]  # Google Ads allows max 15 headlines

def generate_descriptions(keywords, business_info, industry="general"):
    """Generate compelling descriptions for Google Ads."""
    
    # Industry-specific description templates
    templates = {
        "education": [
            "Join thousands who've mastered {keyword}. Expert instruction, proven results, lifetime access.",
            "Professional {keyword} training with certification. Industry-recognized program with job placement support.",
            "Transform your career with {keyword} skills. Expert-led courses, flexible schedule, money-back guarantee.",
            "Learn {keyword} from industry experts. Hands-on training, real-world projects, career support included."
        ],
        "fitness": [
            "Professional {keyword} training. Achieve your fitness goals with expert guidance and personalized plans.",
            "Join our {keyword} program. Proven results, supportive community, flexible schedule that fits your life.",
            "Transform your fitness with {keyword}. Personal training available, all fitness levels welcome.",
            "Expert {keyword} coaching. Get the body you want with our proven system and ongoing support."
        ],
        "consulting": [
            "Expert {keyword} consulting. Proven strategies to grow your business fast. Free consultation available.",
            "Professional {keyword} services. Get results with our proven methodology and experienced team.",
            "Transform your business with expert {keyword} consulting. Customized solutions for your success.",
            "Results-driven {keyword} solutions. Increase revenue, reduce costs, improve efficiency. Call today."
        ],
        "ecommerce": [
            "Shop premium {keyword} products. Fast shipping, easy returns, satisfaction guaranteed. Order today.",
            "Best selection of {keyword} online. Competitive prices, expert reviews, secure checkout available.",
            "Quality {keyword} products at unbeatable prices. Free shipping on orders over $50. Shop now.",
            "Trusted {keyword} retailer since {year}. Thousands of satisfied customers. Browse our collection."
        ],
        "healthcare": [
            "Expert {keyword} care from experienced professionals. Compassionate service, modern facility, insurance accepted.",
            "Professional {keyword} services. State-of-the-art equipment, personalized treatment plans, convenient scheduling.",
            "Trusted {keyword} specialists. Quality care, proven results, patient-focused approach. Schedule today.",
            "Advanced {keyword} treatment options. Experienced team, latest technology, comprehensive care available."
        ]
    }
    
    # Get templates for the industry
    industry_templates = templates.get(industry, templates["consulting"])
    
    descriptions = []
    
    for keyword in keywords[:3]:  # Limit to 3 keywords for descriptions
        keyword_clean = keyword.lower().strip()
        
        for template in industry_templates:
            # Replace placeholders
            description = template.format(
                keyword=keyword_clean,
                year=business_info.get("established_year", "2020"),
                location=business_info.get("location", "")
            )
            
            # Ensure description meets Google Ads requirements
            if len(description) <= 90 and description not in descriptions:
                descriptions.append(description)
    
    # Add business-specific descriptions with USPs
    if business_info.get("unique_selling_points"):
        for usp in business_info["unique_selling_points"][:2]:
            usp_desc = f"{usp}. {business_info.get('call_to_action', 'Contact us today')}!"
            if len(usp_desc) <= 90:
                descriptions.append(usp_desc)
    
    return descriptions[:4]  # Google Ads allows max 4 descriptions

def generate_ad_extensions(business_info, keywords):
    """Generate ad extensions (sitelinks, callouts, etc.)."""
    
    extensions = {
        "sitelinks": [],
        "callouts": [],
        "structured_snippets": {}
    }
    
    # Generate sitelinks
    common_sitelinks = [
        {"text": "About Us", "url": "/about"},
        {"text": "Contact", "url": "/contact"},
        {"text": "Services", "url": "/services"},
        {"text": "Testimonials", "url": "/testimonials"},
        {"text": "Free Quote", "url": "/quote"},
        {"text": "Portfolio", "url": "/portfolio"}
    ]
    
    extensions["sitelinks"] = common_sitelinks[:4]  # Max 4 sitelinks
    
    # Generate callouts
    common_callouts = [
        "Free Consultation",
        "Expert Team",
        "Proven Results",
        "Money Back Guarantee",
        "24/7 Support",
        "Licensed & Insured",
        "Fast Response",
        "Competitive Pricing"
    ]
    
    # Add business-specific callouts
    if business_info.get("certifications"):
        common_callouts.extend(business_info["certifications"])
    
    extensions["callouts"] = common_callouts[:10]  # Max 10 callouts
    
    # Generate structured snippets
    extensions["structured_snippets"] = {
        "Services": keywords[:5],
        "Brands": business_info.get("brands", []),
        "Types": business_info.get("service_types", [])
    }
    
    return extensions

def create_campaign_ad_copy(campaign_name, keywords, business_info, industry="general"):
    """Create complete ad copy for a campaign."""
    
    print(f"✍️  Generating ad copy for '{campaign_name}' campaign...")
    print(f"   Industry: {industry}")
    print(f"   Keywords: {', '.join(keywords)}")
    
    # Generate headlines and descriptions
    headlines = generate_headlines(keywords, business_info, industry)
    descriptions = generate_descriptions(keywords, business_info, industry)
    extensions = generate_ad_extensions(business_info, keywords)
    
    # Create ad groups based on keyword themes
    ad_groups = []
    
    # Group keywords by theme
    keyword_groups = {}
    for keyword in keywords:
        # Simple grouping by first word
        first_word = keyword.split()[0].lower()
        if first_word not in keyword_groups:
            keyword_groups[first_word] = []
        keyword_groups[first_word].append(keyword)
    
    # Create ad group for each keyword theme
    for theme, theme_keywords in keyword_groups.items():
        ad_group = {
            "name": f"{theme.title()} - {campaign_name}",
            "keywords": theme_keywords,
            "headlines": [h for h in headlines if theme in h.lower() or any(kw.lower() in h.lower() for kw in theme_keywords)],
            "descriptions": descriptions,
            "extensions": extensions
        }
        
        # Ensure we have enough headlines (minimum 3)
        if len(ad_group["headlines"]) < 3:
            ad_group["headlines"] = headlines[:3]
        
        ad_groups.append(ad_group)
    
    # If no themed groups, create one main ad group
    if not ad_groups:
        ad_groups = [{
            "name": f"Main - {campaign_name}",
            "keywords": keywords,
            "headlines": headlines,
            "descriptions": descriptions,
            "extensions": extensions
        }]
    
    campaign_ad_copy = {
        "campaign_name": campaign_name,
        "industry": industry,
        "ad_groups": ad_groups,
        "total_headlines": len(headlines),
        "total_descriptions": len(descriptions),
        "created_at": datetime.now().isoformat()
    }
    
    print(f"📝 Generated ad copy:")
    print(f"   Ad Groups: {len(ad_groups)}")
    print(f"   Headlines: {len(headlines)}")
    print(f"   Descriptions: {len(descriptions)}")
    print(f"   Sitelinks: {len(extensions['sitelinks'])}")
    print(f"   Callouts: {len(extensions['callouts'])}")
    
    return campaign_ad_copy

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Google Ads Ad Copy Generator')
    parser.add_argument('--campaign-name', required=True, help='Name of the campaign')
    parser.add_argument('--keywords', nargs='+', required=True, help='List of target keywords')
    parser.add_argument('--industry', default='general', 
                       choices=['education', 'fitness', 'consulting', 'ecommerce', 'healthcare', 'general'],
                       help='Industry type for ad copy optimization')
    parser.add_argument('--brand-name', help='Business/brand name')
    parser.add_argument('--location', help='Business location')
    parser.add_argument('--usps', nargs='+', help='Unique selling points')
    parser.add_argument('--cta', default='Learn More', help='Call to action')
    parser.add_argument('--output-file', help='Output JSON file for ad copy')
    
    args = parser.parse_args()
    
    print("🚀 Google Ads Ad Copy Generator")
    print("=" * 37)
    
    # Prepare business info
    business_info = {
        "brand_name": args.brand_name,
        "location": args.location,
        "unique_selling_points": args.usps or [],
        "call_to_action": args.cta,
        "timeframe": "30 Days",
        "established_year": "2020"
    }
    
    # Generate ad copy
    ad_copy = create_campaign_ad_copy(
        args.campaign_name, 
        args.keywords, 
        business_info, 
        args.industry
    )
    
    # Output results
    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(ad_copy, f, indent=2)
        print(f"💾 Ad copy saved to {args.output_file}")
    else:
        print("\n📋 Generated Ad Copy:")
        print(json.dumps(ad_copy, indent=2))

if __name__ == "__main__":
    main()

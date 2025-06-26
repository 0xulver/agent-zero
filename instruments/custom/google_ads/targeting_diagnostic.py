#!/usr/bin/env python3
"""
Standalone targeting diagnostic tool that actually works.
"""

import sys
import os
import argparse

# Add the instruments directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'instruments', 'custom', 'google_ads'))

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    
    def get_google_ads_client():
        """Get authenticated Google Ads client."""
        # Try different credential paths
        credentials_paths = [
            'google-ads.yaml',
            'instruments/custom/google_ads/google-ads.yaml',
            os.path.expanduser('~/google-ads.yaml')
        ]
        
        for path in credentials_paths:
            try:
                if os.path.exists(path):
                    return GoogleAdsClient.load_from_storage(path)
            except:
                continue
        
        # Try default location
        return GoogleAdsClient.load_from_storage()
    
    def decode_location_id(location_id):
        """Decode common location criterion IDs to readable names."""
        location_map = {
            2840: "United States",
            2124: "Canada", 
            2826: "United Kingdom",
            2250: "France",
            2276: "Germany",
            1023191: "New York, NY, USA",
            1014044: "California, USA",
            1023511: "Texas, USA",
            1014221: "Florida, USA",
            1023609: "Illinois, USA"
        }
        return location_map.get(location_id, f"Location ID {location_id}")

    def decode_language_id(language_id):
        """Decode common language criterion IDs to readable names."""
        language_map = {
            1000: "English",
            1003: "Spanish", 
            1002: "French",
            1001: "German",
            1004: "Italian",
            1005: "Portuguese",
            1006: "Japanese",
            1007: "Korean",
            1008: "Chinese (Simplified)",
            1009: "Chinese (Traditional)"
        }
        return language_map.get(language_id, f"Language ID {language_id}")

    def decode_age_range_id(age_id):
        """Decode age range criterion IDs to readable names."""
        age_map = {
            30000: "18-24 years",
            30001: "25-34 years", 
            30002: "35-44 years",
            30003: "45-54 years",
            30004: "55-64 years",
            30005: "65+ years"
        }
        return age_map.get(age_id, f"Age Range ID {age_id}")

    def diagnose_campaign_targeting(customer_id, campaign_id):
        """Diagnose targeting for a specific campaign."""
        print(f"🎯 TARGETING DIAGNOSTIC FOR CAMPAIGN {campaign_id}")
        print("=" * 60)
        
        try:
            client = get_google_ads_client()
            ga_service = client.get_service("GoogleAdsService")
            
            # Get campaign basic info
            campaign_query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign.start_date,
                campaign.end_date
            FROM campaign
            WHERE campaign.id = {campaign_id}
            """
            
            print("📋 CAMPAIGN INFORMATION:")
            print("-" * 30)
            
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = campaign_query
            
            campaign_response = ga_service.search(request=search_request)
            
            for row in campaign_response:
                print(f"Campaign ID: {row.campaign.id}")
                print(f"Campaign Name: {row.campaign.name}")
                print(f"Status: {row.campaign.status.name}")
                print(f"Channel Type: {row.campaign.advertising_channel_type.name}")
                break
            
            # Get targeting criteria
            targeting_query = f"""
            SELECT 
                campaign.id,
                campaign.name,
                campaign_criterion.type,
                campaign_criterion.criterion_id,
                campaign_criterion.status,
                campaign_criterion.negative
            FROM campaign_criterion
            WHERE campaign.id = {campaign_id}
            """
            
            search_request.query = targeting_query
            response = ga_service.search(request=search_request)
            
            # Process and categorize the results
            location_criteria = []
            language_criteria = []
            age_criteria = []
            other_criteria = []
            
            for row in response:
                criterion_type = row.campaign_criterion.type_
                criterion_id = row.campaign_criterion.criterion_id
                is_negative = row.campaign_criterion.negative
                status = row.campaign_criterion.status
                
                criterion_info = {
                    'id': criterion_id,
                    'negative': is_negative,
                    'status': status.name,
                    'type_code': criterion_type
                }
                
                if criterion_type == 7:  # LOCATION
                    location_criteria.append(criterion_info)
                elif criterion_type == 20:  # LANGUAGE
                    language_criteria.append(criterion_info)
                elif criterion_type == 6:  # AGE_RANGE
                    age_criteria.append(criterion_info)
                else:
                    other_criteria.append(criterion_info)
            
            # Display results
            print(f"\n📍 LOCATION TARGETING ({len(location_criteria)} criteria):")
            print("-" * 40)
            
            if location_criteria:
                for loc in location_criteria:
                    prefix = "❌ EXCLUDED:" if loc['negative'] else "✅ INCLUDED:"
                    status_icon = "🟢" if loc['status'] == 'ENABLED' else "🟡" if loc['status'] == 'PAUSED' else "🔴"
                    location_name = decode_location_id(loc['id'])
                    print(f"  {prefix} {location_name} {status_icon}")
            else:
                print("  No location targeting criteria found")
            
            print(f"\n🗣️ LANGUAGE TARGETING ({len(language_criteria)} criteria):")
            print("-" * 40)
            
            if language_criteria:
                for lang in language_criteria:
                    prefix = "❌ EXCLUDED:" if lang['negative'] else "✅ INCLUDED:"
                    status_icon = "🟢" if lang['status'] == 'ENABLED' else "🟡" if lang['status'] == 'PAUSED' else "🔴"
                    language_name = decode_language_id(lang['id'])
                    print(f"  {prefix} {language_name} {status_icon}")
            else:
                print("  No language targeting criteria found")
            
            if age_criteria:
                print(f"\n👥 AGE TARGETING ({len(age_criteria)} criteria):")
                print("-" * 40)
                for age in age_criteria:
                    status_icon = "🟢" if age['status'] == 'ENABLED' else "🟡" if age['status'] == 'PAUSED' else "🔴"
                    age_name = decode_age_range_id(age['id'])
                    print(f"  ✅ {age_name} {status_icon}")
            
            if other_criteria:
                print(f"\n🎯 OTHER TARGETING ({len(other_criteria)} criteria):")
                print("-" * 40)
                for other in other_criteria:
                    print(f"  Type {other['type_code']}: ID {other['id']} (Status: {other['status']})")
            
            print(f"\n📊 SUMMARY:")
            print(f"  Total targeting criteria: {len(location_criteria) + len(language_criteria) + len(age_criteria) + len(other_criteria)}")
            print(f"  Location criteria: {len(location_criteria)}")
            print(f"  Language criteria: {len(language_criteria)}")
            print(f"  Age criteria: {len(age_criteria)}")
            print(f"  Other criteria: {len(other_criteria)}")
            
        except GoogleAdsException as ex:
            print(f"❌ Google Ads API Error:")
            for error in ex.failure.errors:
                print(f"  Error: {error.message}")
        except Exception as e:
            print(f"❌ General Error: {e}")

    def main():
        """Main function."""
        parser = argparse.ArgumentParser(description='Campaign Targeting Diagnostic Tool')
        parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
        parser.add_argument('--campaign-id', required=True, help='Campaign ID to diagnose')
        
        args = parser.parse_args()
        
        print("🚀 Campaign Targeting Diagnostic Tool")
        print("=" * 42)
        
        diagnose_campaign_targeting(args.customer_id, args.campaign_id)

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("💡 Make sure Google Ads API client is installed:")
    print("   pip install google-ads")
    sys.exit(1)

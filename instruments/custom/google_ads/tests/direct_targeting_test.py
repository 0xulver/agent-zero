#!/usr/bin/env python3
"""
Direct test using Google Ads API client to get targeting data.
"""

import sys
import os

# Add the instruments directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'instruments', 'custom', 'google_ads'))

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    
    def get_google_ads_client():
        """Get authenticated Google Ads client."""
        # Use the same credentials as other scripts
        credentials_path = os.path.join(os.path.dirname(__file__), 'instruments', 'custom', 'google_ads', 'google-ads.yaml')
        if os.path.exists(credentials_path):
            return GoogleAdsClient.load_from_storage(credentials_path)
        else:
            return GoogleAdsClient.load_from_storage()
    
    def test_direct_targeting_query():
        """Test targeting query directly with Google Ads client."""
        customer_id = "3045806466"
        campaign_id = "22710728616"
        
        print("🧪 Direct Google Ads API Targeting Test")
        print("=" * 50)
        
        try:
            client = get_google_ads_client()
            ga_service = client.get_service("GoogleAdsService")
            
            # Test query
            query = f"""
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
            
            print(f"🔍 Executing query: {query}")
            print("-" * 50)
            
            # Execute the query
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            print("📊 Raw API Response:")
            print("-" * 30)
            
            count = 0
            for row in response:
                count += 1
                print(f"\nRow {count}:")
                print(f"  Campaign ID: {row.campaign.id}")
                print(f"  Campaign Name: {row.campaign.name}")
                print(f"  Criterion Type: {row.campaign_criterion.type_}")
                print(f"  Criterion ID: {row.campaign_criterion.criterion_id}")
                print(f"  Status: {row.campaign_criterion.status}")
                print(f"  Negative: {row.campaign_criterion.negative}")
                
                # Try to access location/language specific fields
                if hasattr(row.campaign_criterion, 'location'):
                    print(f"  Location: {row.campaign_criterion.location}")
                if hasattr(row.campaign_criterion, 'language'):
                    print(f"  Language: {row.campaign_criterion.language}")
                    
                if count >= 10:  # Limit output
                    break
            
            print(f"\n✅ Total rows found: {count}")
            
        except GoogleAdsException as ex:
            print(f"❌ Google Ads API Error:")
            for error in ex.failure.errors:
                print(f"  Error: {error.message}")
                print(f"  Code: {error.error_code}")
        except Exception as e:
            print(f"❌ General Error: {e}")
    
    if __name__ == "__main__":
        test_direct_targeting_query()

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("💡 Make sure Google Ads API client is installed:")
    print("   pip install google-ads")
    sys.exit(1)

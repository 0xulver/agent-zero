# Google Ads API Integration

## Problem
Set up and manage Google Ads campaigns programmatically through the Google Ads API.

## Solution
This instrument provides tools to:
1. Generate refresh token for Google Ads API authentication
2. Test API connection
3. Set up campaigns
4. Monitor campaign performance
5. Optimize campaigns

## Available Scripts

### 1. Setup and Authentication
```bash
# Generate refresh token (one-time setup)
python /a0/instruments/custom/google_ads/generate_refresh_token.py

# Test API connection
python /a0/instruments/custom/google_ads/test_connection.py
```

### 2. Campaign Management
```bash
# Set up a new campaign
python /a0/instruments/custom/google_ads/setup_campaign.py --customer-id CUSTOMER_ID --campaign-name "Campaign Name" --budget 1000

# Monitor campaigns
python /a0/instruments/custom/google_ads/monitor_campaigns.py --customer-id CUSTOMER_ID

# Optimize campaigns
python /a0/instruments/custom/google_ads/optimize_campaigns.py --customer-id CUSTOMER_ID
```

## Prerequisites
- Google Ads API developer token
- OAuth2 credentials (client_id, client_secret)
- Manager Account (MCC) ID
- google-ads.yaml configuration file

## Configuration
The instrument reads configuration from `/a0/google-ads.yaml` file.

## First Time Setup
1. Run the refresh token generator
2. Test the connection
3. Start managing campaigns

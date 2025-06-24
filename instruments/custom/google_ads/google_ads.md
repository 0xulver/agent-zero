# Google Ads API Integration

## Problem
Set up and manage Google Ads campaigns programmatically through the Google Ads API.

## Solution
This instrument provides a complete Google Ads API integration with automatic dependency management and setup.

## Quick Setup (Recommended)
```bash
# Complete setup in one command - installs dependencies, generates refresh token, and tests connection
python /a0/instruments/custom/google_ads/setup_google_ads.py
```

## Individual Scripts (Advanced)
```bash
# Generate refresh token only
python /a0/instruments/custom/google_ads/generate_refresh_token.py

# Test API connection only
python /a0/instruments/custom/google_ads/test_connection.py

# Execute GAQL queries
python /a0/instruments/custom/google_ads/run_query.py --customer-id "1234567890" --query "SELECT campaign.name, metrics.clicks FROM campaign LIMIT 10" --format table
```

## Prerequisites
- Google Ads API developer token
- OAuth2 credentials (client_id, client_secret)
- Manager Account (MCC) ID
- google-ads.yaml configuration file in /a0/ directory

## Configuration File
The instrument reads from `/a0/google-ads.yaml` which should contain:
```yaml
developer_token: YOUR_DEVELOPER_TOKEN
client_id: YOUR_CLIENT_ID
client_secret: YOUR_CLIENT_SECRET
refresh_token: INSERT_REFRESH_TOKEN_HERE  # Will be auto-generated
login_customer_id: YOUR_MCC_ID
use_proto_plus: true
```

## First Time Setup Process
1. Ensure your google-ads.yaml file has the required credentials
2. Run the setup script: `python /a0/instruments/custom/google_ads/setup_google_ads.py`
3. Follow the OAuth2 authorization process in your browser
4. The script will automatically test the connection and show accessible accounts

## Available Scripts

### Query Execution
```bash
# Run custom GAQL queries with different output formats
python /a0/instruments/custom/google_ads/run_query.py --customer-id "CUSTOMER_ID" --query "YOUR_GAQL_QUERY" --format table

# Debug mode (shows field extraction details)
python /a0/instruments/custom/google_ads/run_query.py --customer-id "CUSTOMER_ID" --query "YOUR_GAQL_QUERY" --format table --debug
```

### Working Query Examples

#### Basic Campaign Data (Always Works)
```bash
# Simple campaign list
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT campaign.name, campaign.status, campaign.id FROM campaign LIMIT 10" --format table

# Campaign with basic info
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT campaign.name, campaign.status FROM campaign" --format json
```

#### Campaign Performance (Requires Date Range)
```bash
# Last 30 days performance
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT campaign.name, metrics.clicks, metrics.impressions, metrics.cost_micros FROM campaign WHERE segments.date DURING LAST_30DAYS ORDER BY metrics.clicks DESC LIMIT 10" --format table

# Specific date range
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT campaign.name, metrics.clicks, metrics.impressions FROM campaign WHERE segments.date >= '2025-05-01' AND segments.date <= '2025-06-24' ORDER BY metrics.clicks DESC LIMIT 10" --format table
```

#### Ad Group Data
```bash
# Ad groups with campaign info
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT campaign.name, ad_group.name, ad_group.status FROM ad_group LIMIT 10" --format table

# Ad group performance
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT ad_group.name, metrics.clicks, metrics.impressions FROM ad_group WHERE segments.date DURING LAST_7DAYS LIMIT 10" --format csv
```

#### Troubleshooting Empty Results
```bash
# If getting N/A values, try debug mode:
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT campaign.name, campaign.status FROM campaign LIMIT 5" --format table --debug

# Start with simple queries first:
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT campaign.id FROM campaign LIMIT 5" --format table
```

## Features
- ✅ Automatic dependency installation
- ✅ Self-contained scripts (no import issues)
- ✅ Interactive OAuth2 flow
- ✅ Connection testing with detailed error messages
- ✅ Lists all accessible customer accounts
- ✅ GAQL query execution with multiple output formats
- ✅ Command-line interface for easy automation

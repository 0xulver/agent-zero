# Problem
Manage Google Ads campaigns programmatically including creation, monitoring, and optimization

# Solution
Use the Google Ads instrument to interact with the Google Ads API. This instrument provides comprehensive campaign management capabilities.

## Prerequisites
1. Google Ads API credentials (OAuth2 client configuration)
2. Google Ads Developer Token
3. Access to Google Ads accounts

## Available Operations

### 1. Setup Authentication
```bash
python /a0/instruments/custom/google_ads/scripts/setup_auth.py
```
This will guide you through the OAuth2 authentication process and save your credentials.

### 2. List Available Accounts
```bash
python /a0/instruments/custom/google_ads/scripts/list_accounts.py
```
Shows all Google Ads accounts you have access to.

### 3. Get Campaign Performance
```bash
python /a0/instruments/custom/google_ads/scripts/get_performance.py \
  --customer-id "1234567890" \
  --type campaign \
  --days 30
```

### 4. Get Ad Performance
```bash
python /a0/instruments/custom/google_ads/scripts/get_performance.py \
  --customer-id "1234567890" \
  --type ad \
  --days 30
```

### 5. Execute Custom GAQL Query
```bash
python /a0/instruments/custom/google_ads/scripts/run_query.py \
  --customer-id "1234567890" \
  --query "SELECT campaign.name, metrics.clicks FROM campaign LIMIT 10" \
  --format table
```

### 6. Create Campaign
```bash
python /a0/instruments/custom/google_ads/scripts/create_campaign.py \
  --customer-id "1234567890" \
  --name "My New Campaign" \
  --budget 1000 \
  --keywords "keyword1,keyword2,keyword3"
```

### 7. Monitor and Optimize
```bash
python /a0/instruments/custom/google_ads/scripts/optimize.py \
  --customer-id "1234567890" \
  --target-roas 4.0
```

## Configuration
Set up your environment variables in `/a0/instruments/custom/google_ads/config/.env`:
- GOOGLE_ADS_DEVELOPER_TOKEN
- GOOGLE_ADS_CLIENT_ID  
- GOOGLE_ADS_CLIENT_SECRET
- GOOGLE_ADS_LOGIN_CUSTOMER_ID (optional)

## Output
All results are saved to `/work_dir/google_ads_results/` with timestamps for easy tracking.

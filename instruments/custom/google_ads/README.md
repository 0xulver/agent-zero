# Google Ads Instrument for Agent Zero

A comprehensive Google Ads integration for Agent Zero that provides campaign management, performance monitoring, and optimization capabilities.

## Features

- **OAuth2 Authentication** - Secure authentication with Google Ads API
- **Account Management** - List and manage multiple Google Ads accounts
- **Performance Analytics** - Campaign and ad performance reporting
- **GAQL Queries** - Execute custom Google Ads Query Language queries
- **Campaign Creation** - Create new campaigns with basic setup (simulation)
- **Optimization Analysis** - Automated performance analysis and recommendations
- **Multiple Output Formats** - Table, CSV, and JSON output formats
- **Data Persistence** - All results saved to `/work_dir/google_ads_results/`

## Prerequisites

1. **Google Ads Account** with API access
2. **Google Cloud Project** with Google Ads API enabled
3. **OAuth2 Credentials** (Client ID and Secret)
4. **Google Ads Developer Token**

## Setup Instructions

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Ads API
4. Go to "Credentials" → "Create Credentials" → "OAuth Client ID"
5. Choose "Desktop Application" as the application type
6. Download the OAuth client configuration

### 2. Google Ads Developer Token

1. Sign in to [Google Ads](https://ads.google.com/)
2. Go to Tools & Settings → API Center
3. Apply for a Developer Token
4. Wait for approval (usually 1-3 business days)

### 3. Environment Configuration

1. Copy the environment template:
   ```bash
   cp /a0/instruments/custom/google_ads/config/.env.example /a0/instruments/custom/google_ads/config/.env
   ```

2. Edit the `.env` file with your credentials:
   ```bash
   nano /a0/instruments/custom/google_ads/config/.env
   ```

3. Set the following values:
   ```
   GOOGLE_ADS_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
   GOOGLE_ADS_CLIENT_SECRET=your_client_secret_here
   GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_here
   GOOGLE_ADS_LOGIN_CUSTOMER_ID=  # Optional: Manager Account ID
   ```

### 4. Install Dependencies

```bash
# Install required Python packages
pip install -r /a0/instruments/custom/google_ads/requirements.txt
```

### 5. Authentication Setup

Run the authentication setup script:
```bash
python /a0/instruments/custom/google_ads/scripts/setup_auth.py
```

This will guide you through the OAuth2 flow and save your credentials.

## Usage

### List Available Accounts
```bash
python /a0/instruments/custom/google_ads/scripts/list_accounts.py
```

### Get Campaign Performance
```bash
python /a0/instruments/custom/google_ads/scripts/get_performance.py \
  --customer-id "1234567890" \
  --type campaign \
  --days 30 \
  --format table
```

### Get Ad Performance
```bash
python /a0/instruments/custom/google_ads/scripts/get_performance.py \
  --customer-id "1234567890" \
  --type ad \
  --days 30 \
  --format csv
```

### Execute Custom GAQL Query
```bash
python /a0/instruments/custom/google_ads/scripts/run_query.py \
  --customer-id "1234567890" \
  --query "SELECT campaign.name, metrics.clicks FROM campaign LIMIT 10" \
  --format json
```

### Use Sample Queries
```bash
# List available sample queries
python /a0/instruments/custom/google_ads/scripts/run_query.py --list-samples

# Run a sample query
python /a0/instruments/custom/google_ads/scripts/run_query.py \
  --customer-id "1234567890" \
  --sample campaigns \
  --format table
```

### Create Campaign (Simulation)
```bash
python /a0/instruments/custom/google_ads/scripts/create_campaign.py \
  --customer-id "1234567890" \
  --name "My New Campaign" \
  --budget 100.00 \
  --keywords "keyword1,keyword2,keyword3"
```

### Optimization Analysis
```bash
python /a0/instruments/custom/google_ads/scripts/optimize.py \
  --customer-id "1234567890" \
  --target-roas 4.0 \
  --target-ctr 2.5 \
  --days 30
```

## Output Files

All results are automatically saved to `/work_dir/google_ads_results/` with timestamps:

- **JSON files** - Raw API response data
- **Formatted files** - Human-readable reports (table/CSV format)
- **Analysis reports** - Optimization recommendations and insights

## Sample GAQL Queries

The instrument includes several predefined sample queries:

- **campaigns** - Basic campaign performance metrics
- **keywords** - Keyword performance analysis
- **ads** - Ad performance data
- **account_info** - Account information and settings

## Error Handling

- **Authentication errors** - Clear guidance for credential setup
- **API errors** - Detailed error messages with troubleshooting tips
- **Rate limiting** - Automatic handling of API quotas
- **Token refresh** - Automatic OAuth token refresh

## Limitations

- **Campaign creation** is currently simulated (not actually created)
- **Campaign modifications** are simulated for safety
- **Real campaign management** requires additional Google Ads API implementation

## Security

- **OAuth2 tokens** are stored locally in the config directory
- **Credentials** are never logged or exposed
- **API calls** use secure HTTPS connections
- **Environment variables** keep sensitive data separate

## Troubleshooting

### Authentication Issues
1. Verify your OAuth2 credentials are correct
2. Check that the Google Ads API is enabled in your project
3. Ensure your Developer Token is approved and valid

### API Errors
1. Check your account access permissions
2. Verify customer IDs are correct (10 digits, no dashes)
3. Review API quota limits in Google Cloud Console

### Permission Errors
1. Ensure scripts are executable: `chmod +x instruments/custom/google_ads/scripts/*.py`
2. Check file permissions in the config directory

## Support

For issues and questions:
1. Check the error messages for specific guidance
2. Review the Google Ads API documentation
3. Verify your account setup and permissions

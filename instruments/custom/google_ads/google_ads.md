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

## Keyword Research & Analysis Tools

### 1. Keyword Research Tool (`keyword_research.py`)
Comprehensive keyword analysis using specialized GAQL queries:

```bash
# Get all current keywords with performance data
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action current --days 30

# Find top performing keywords by conversions
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action top-performing --min-conversions 1

# Identify underperforming keywords (high impressions, low CTR)
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action underperforming --min-impressions 1000 --max-ctr 0.02

# Find expensive keywords that need optimization
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action expensive --min-cost 10000000

# Discover keyword expansion opportunities from search terms
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action opportunities

# Analyze keyword quality scores
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action quality-scores

# Check keyword competition metrics
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action competition
```

### 2. Campaign Analysis Tool (`campaign_analyzer.py`)
Comprehensive campaign performance analysis:

```bash
# Get campaign overview with key metrics
python /a0/instruments/custom/google_ads/campaign_analyzer.py --customer-id "3045806466" --action overview --days 30

# Find top performing campaigns by conversion value
python /a0/instruments/custom/google_ads/campaign_analyzer.py --customer-id "3045806466" --action top-campaigns --metric conversion_value

# Identify underperforming campaigns
python /a0/instruments/custom/google_ads/campaign_analyzer.py --customer-id "3045806466" --action underperforming --min-cost 5000000

# Analyze campaign trends over time (CSV output)
python /a0/instruments/custom/google_ads/campaign_analyzer.py --customer-id "3045806466" --action trends --days 60

# Campaign performance by device type
python /a0/instruments/custom/google_ads/campaign_analyzer.py --customer-id "3045806466" --action device-performance

# Budget analysis and spending patterns
python /a0/instruments/custom/google_ads/campaign_analyzer.py --customer-id "3045806466" --action budget-analysis

# Geographic performance analysis
python /a0/instruments/custom/google_ads/campaign_analyzer.py --customer-id "3045806466" --action geographic

# Performance by time schedule (CSV output)
python /a0/instruments/custom/google_ads/campaign_analyzer.py --customer-id "3045806466" --action schedule
```

### 3. Keyword Simulation Tool (`keyword_simulator.py`)
Advanced keyword forecasting and simulation:

```bash
# Simulate keyword performance based on historical data
python /a0/instruments/custom/google_ads/keyword_simulator.py --customer-id "3045806466" --action simulate --days 90

# Analyze keyword performance trends
python /a0/instruments/custom/google_ads/keyword_simulator.py --customer-id "3045806466" --action trends --days 60

# Find keyword expansion opportunities
python /a0/instruments/custom/google_ads/keyword_simulator.py --customer-id "3045806466" --action expansion

# Simulate bid optimization opportunities
python /a0/instruments/custom/google_ads/keyword_simulator.py --customer-id "3045806466" --action bid-simulation

# Analyze seasonal patterns (requires longer history)
python /a0/instruments/custom/google_ads/keyword_simulator.py --customer-id "3045806466" --action seasonal --days 365

# Predict performance for specific keyword
python /a0/instruments/custom/google_ads/keyword_simulator.py --customer-id "3045806466" --action predict --keyword "acting classes"

# Generate comprehensive keyword recommendations
python /a0/instruments/custom/google_ads/keyword_simulator.py --customer-id "3045806466" --action recommendations
```

### 1. Current Keyword Analysis

#### Get All Active Keywords
```bash
# Get all keywords from active campaigns with performance data
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT campaign.name, ad_group.name, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM keyword_view WHERE campaign.status = 'ENABLED' AND ad_group.status = 'ENABLED' AND ad_group_criterion.status = 'ENABLED' AND segments.date DURING LAST_30DAYS ORDER BY metrics.impressions DESC LIMIT 50" --format table

# Get top performing keywords by conversion value
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, metrics.conversions, metrics.conversion_value, metrics.cost_micros, metrics.search_impression_share FROM keyword_view WHERE campaign.status = 'ENABLED' AND segments.date DURING LAST_30DAYS AND metrics.conversions > 0 ORDER BY metrics.conversion_value DESC LIMIT 20" --format table
```

#### Keyword Performance Analysis
```bash
# Keywords with high impressions but low CTR (optimization opportunities)
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT ad_group_criterion.keyword.text, metrics.impressions, metrics.clicks, metrics.ctr, metrics.average_cpc, campaign.name FROM keyword_view WHERE segments.date DURING LAST_30DAYS AND metrics.impressions > 1000 AND metrics.ctr < 0.02 ORDER BY metrics.impressions DESC LIMIT 25" --format table

# High-cost keywords with low conversion rates
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT ad_group_criterion.keyword.text, metrics.cost_micros, metrics.clicks, metrics.conversions, metrics.cost_per_conversion FROM keyword_view WHERE segments.date DURING LAST_30DAYS AND metrics.cost_micros > 50000000 AND metrics.conversions < 1 ORDER BY metrics.cost_micros DESC LIMIT 20" --format table
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

### 4. Custom GAQL Queries (`run_query.py`)
For advanced users who want to write custom queries:

```bash
# Execute any custom GAQL query
python /a0/instruments/custom/google_ads/run_query.py --customer-id "3045806466" --query "SELECT campaign.name, metrics.clicks FROM campaign LIMIT 10" --format table
```

## Keyword Research Workflow

### Step 1: Current State Analysis
```bash
# Start with current keyword analysis
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action current --days 30
```

### Step 2: Performance Optimization
```bash
# Find underperforming keywords to pause or optimize
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action underperforming

# Find expensive keywords with poor ROI
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action expensive
```

### Step 3: Expansion Opportunities
```bash
# Discover new keyword opportunities
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action opportunities

# Get comprehensive recommendations
python /a0/instruments/custom/google_ads/keyword_simulator.py --customer-id "3045806466" --action recommendations
```

### Step 4: Forecasting & Simulation
```bash
# Simulate performance for potential changes
python /a0/instruments/custom/google_ads/keyword_simulator.py --customer-id "3045806466" --action simulate

# Analyze trends for strategic planning
python /a0/instruments/custom/google_ads/keyword_simulator.py --customer-id "3045806466" --action trends
```

## Features
- ✅ Automatic dependency installation
- ✅ Self-contained scripts (no import issues)
- ✅ Interactive OAuth2 flow
- ✅ Connection testing with detailed error messages
- ✅ Lists all accessible customer accounts
- ✅ GAQL query execution with multiple output formats
- ✅ **Specialized keyword research tools**
- ✅ **Campaign performance analysis**
- ✅ **Keyword simulation and forecasting**
- ✅ **Automated optimization recommendations**
- ✅ Command-line interface for easy automation

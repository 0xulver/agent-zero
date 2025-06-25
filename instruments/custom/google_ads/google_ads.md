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

## Campaign Creation & Management Tools

### 5. Campaign Configuration Generator (`campaign_config_generator.py`)
Generate complete campaign configurations ready for creation:

```bash
# Generate campaign configuration with keywords and ad copy
python /a0/instruments/custom/google_ads/campaign_config_generator.py --campaign-name "Voice Training Campaign" --keywords "voice training" "public speaking" "vocal coaching" --budget 50000000 --industry education --brand-name "Voice Academy" --output-file voice_campaign_config.json

# Generate ecommerce campaign
python /a0/instruments/custom/google_ads/campaign_config_generator.py --campaign-name "Fitness Equipment Store" --keywords "home gym equipment" "fitness gear" "workout equipment" --budget 100000000 --industry ecommerce --target-locations "United States" "Canada"
```

### 6. Ad Copy Generator (`ad_copy_generator.py`)
Generate high-converting ad copy using proven templates:

```bash
# Generate ad copy for education business
python /a0/instruments/custom/google_ads/ad_copy_generator.py --campaign-name "Acting Classes" --keywords "acting classes" "drama training" "theater course" --industry education --brand-name "Drama Academy" --usps "Expert Instructors" "Small Class Sizes" --cta "Enroll Today"

# Generate ad copy for fitness business
python /a0/instruments/custom/google_ads/ad_copy_generator.py --campaign-name "Personal Training" --keywords "personal trainer" "fitness coaching" "weight loss" --industry fitness --location "New York" --output-file fitness_ads.json
```

### 7. Campaign Creator (`campaign_creator.py`)
Actually create campaigns in Google Ads using the API:

```bash
# Create campaign from configuration file
python /a0/instruments/custom/google_ads/campaign_creator.py --customer-id "3045806466" --config-file voice_campaign_config.json
```

### 8. Campaign Manager (`campaign_manager.py`)
High-level campaign management and optimization:

```bash
# Get campaign templates
python /a0/instruments/custom/google_ads/campaign_manager.py --customer-id "3045806466" --action templates

# Generate ad copy variations
python /a0/instruments/custom/google_ads/campaign_manager.py --customer-id "3045806466" --action generate-ads --business-type education --keywords "voice training" "public speaking" --usps "Expert Instructors" "Proven Results"

# Create keyword list with variations
python /a0/instruments/custom/google_ads/campaign_manager.py --customer-id "3045806466" --action create-keywords --keywords "voice training" "public speaking"

# Get optimization recommendations
python /a0/instruments/custom/google_ads/campaign_manager.py --customer-id "3045806466" --action optimize
```

### 9. Campaign Operations (`campaign_operations.py`)
**NEW** - Complete campaign management operations for existing campaigns:

```bash
# Update campaign status (pause/enable/remove campaigns)
python /a0/instruments/custom/google_ads/campaign_operations.py --customer-id "3045806466" --operation update_campaign_status --campaign-resource-name "customers/3045806466/campaigns/12345" --status PAUSED

# Update campaign budget
python /a0/instruments/custom/google_ads/campaign_operations.py --customer-id "3045806466" --operation update_campaign_budget --campaign-resource-name "customers/3045806466/campaigns/12345" --budget-micros 75000000

# Update keyword status (pause/enable underperforming keywords)
python /a0/instruments/custom/google_ads/campaign_operations.py --customer-id "3045806466" --operation update_keyword_status --keyword-resource-name "customers/3045806466/adGroupCriteria/12345~67890" --status PAUSED

# Update keyword bids
python /a0/instruments/custom/google_ads/campaign_operations.py --customer-id "3045806466" --operation update_keyword_bid --keyword-resource-name "customers/3045806466/adGroupCriteria/12345~67890" --bid-micros 2000000

# Update ad status (pause/enable ads)
python /a0/instruments/custom/google_ads/campaign_operations.py --customer-id "3045806466" --operation update_ad_status --ad-resource-name "customers/3045806466/adGroupAds/12345~67890" --status PAUSED

# Add new keywords to existing ad group
python /a0/instruments/custom/google_ads/campaign_operations.py --customer-id "3045806466" --operation add_keywords --ad-group-resource-name "customers/3045806466/adGroups/12345" --keywords-file new_keywords.json

# Add negative keywords to campaign
python /a0/instruments/custom/google_ads/campaign_operations.py --customer-id "3045806466" --operation add_negative_keywords --campaign-resource-name "customers/3045806466/campaigns/12345" --negative-keywords-file negative_keywords.json

# Automatically pause underperforming keywords
python /a0/instruments/custom/google_ads/campaign_operations.py --customer-id "3045806466" --operation pause_underperforming --min-impressions 100 --max-ctr 0.02 --days 30

# Automatically optimize keyword bids for target position
python /a0/instruments/custom/google_ads/campaign_operations.py --customer-id "3045806466" --operation optimize_bids --target-position 3.0 --days 30

# Bulk update campaign budgets
python /a0/instruments/custom/google_ads/campaign_operations.py --customer-id "3045806466" --operation bulk_budget_update --budget-adjustments-file budget_changes.json

# Create new ad group in existing campaign
python /a0/instruments/custom/google_ads/campaign_operations.py --customer-id "3045806466" --operation create_ad_group --campaign-resource-name "customers/3045806466/campaigns/12345" --ad-group-name "Advanced Charisma Training" --bid-micros 2000000

# Create complete ad group with keywords and ads
python /a0/instruments/custom/google_ads/campaign_operations.py --customer-id "3045806466" --operation create_ad_group_with_content --campaign-resource-name "customers/3045806466/campaigns/12345" --ad-group-config-file ad_group_config.json
```

## Complete Campaign Creation Workflow

### Step 1: Research & Planning
```bash
# Analyze current performance
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action current --days 30

# Find expansion opportunities
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action opportunities

# Get optimization recommendations
python /a0/instruments/custom/google_ads/keyword_simulator.py --customer-id "3045806466" --action recommendations
```

### Step 2: Generate Campaign Configuration
```bash
# Create complete campaign config with keywords and ad copy
python /a0/instruments/custom/google_ads/campaign_config_generator.py --campaign-name "New Voice Training Campaign" --keywords "voice training" "vocal coaching" "public speaking classes" --budget 75000000 --industry education --brand-name "Voice Mastery Academy" --usps "Expert Instructors" "Proven Results" "Flexible Schedule"
```

### Step 3: Review & Create Campaign
```bash
# Review the generated configuration file
# Update final URLs and any specific settings
# Then create the actual campaign
python /a0/instruments/custom/google_ads/campaign_creator.py --customer-id "3045806466" --config-file new_voice_training_campaign_config.json
```

### Step 4: Monitor & Optimize
```bash
# Monitor campaign performance
python /a0/instruments/custom/google_ads/campaign_analyzer.py --customer-id "3045806466" --action overview --days 7

# Analyze keyword performance
python /a0/instruments/custom/google_ads/keyword_research.py --customer-id "3045806466" --action current --days 7
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
- ✅ **Complete campaign creation workflow**
- ✅ **AI-powered ad copy generation**
- ✅ **Campaign structure optimization**
- ✅ **Keyword variation generation**
- ✅ **Industry-specific templates**
- ✅ **🆕 FULL CAMPAIGN MANAGEMENT OPERATIONS**
- ✅ **🆕 Update campaign status, budgets, and settings**
- ✅ **🆕 Create new ad groups in existing campaigns**
- ✅ **🆕 Manage keywords (pause, enable, update bids, add/remove)**
- ✅ **🆕 Manage ads (pause, enable, update status)**
- ✅ **🆕 Negative keyword management**
- ✅ **🆕 Automated bid optimization**
- ✅ **🆕 Automated underperforming keyword pausing**
- ✅ **🆕 Bulk operations for efficiency**
- ✅ Command-line interface for easy automation

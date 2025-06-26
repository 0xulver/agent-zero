# Campaign Targeting Diagnostic Tool Implementation

## Issue Resolved ✅

**Problem**: Multiple failures to query for campaign targeting settings due to lack of a proper diagnostic function for retrieving location and language targeting information.

**Solution**: Added comprehensive targeting diagnostic functions to `campaign_analyzer.py` that correctly query the `campaign_criterion` resource.

## Implementation Details

### **New Functions Added**

#### 1. `get_campaign_targeting_settings(customer_id, campaign_id=None)`
**Purpose**: Retrieve basic targeting settings for campaigns
**Query Resource**: `campaign_criterion`
**Output**: Raw targeting data with criterion IDs

```python
def get_campaign_targeting_settings(customer_id, campaign_id=None):
    """Retrieve and display current location and language targeting for campaigns."""
```

**GAQL Query**:
```sql
SELECT
    campaign.id,
    campaign.name,
    campaign.status,
    campaign_criterion.campaign,
    campaign_criterion.criterion_id,
    campaign_criterion.type,
    campaign_criterion.status,
    campaign_criterion.negative,
    campaign_criterion.location.geo_target_constant,
    campaign_criterion.language.language_constant
FROM campaign_criterion
WHERE
    campaign.status IN ('ENABLED', 'PAUSED')
    AND campaign_criterion.type IN ('LOCATION', 'LANGUAGE')
```

#### 2. `get_campaign_targeting_summary(customer_id, campaign_id=None)`
**Purpose**: Get detailed targeting with human-readable names
**Query Resource**: `campaign_criterion` with joins to `geo_target_constant` and `language_constant`
**Output**: Formatted summary with readable location and language names

```python
def get_campaign_targeting_summary(customer_id, campaign_id=None):
    """Get a formatted summary of campaign targeting settings with readable names."""
```

**Location Query**:
```sql
SELECT
    campaign.id,
    campaign.name,
    campaign_criterion.criterion_id,
    campaign_criterion.negative,
    campaign_criterion.status,
    geo_target_constant.name,
    geo_target_constant.country_code,
    geo_target_constant.target_type,
    geo_target_constant.canonical_name
FROM campaign_criterion
WHERE
    campaign.status IN ('ENABLED', 'PAUSED')
    AND campaign_criterion.type = 'LOCATION'
```

**Language Query**:
```sql
SELECT
    campaign.id,
    campaign.name,
    campaign_criterion.criterion_id,
    campaign_criterion.negative,
    campaign_criterion.status,
    language_constant.name,
    language_constant.code
FROM campaign_criterion
WHERE
    campaign.status IN ('ENABLED', 'PAUSED')
    AND campaign_criterion.type = 'LANGUAGE'
```

#### 3. `diagnose_campaign_targeting(customer_id, campaign_name_or_id)`
**Purpose**: Comprehensive targeting diagnosis for specific campaigns
**Features**: 
- Search by campaign ID or name
- Campaign basic information
- Complete targeting breakdown
- Support for partial name matching

```python
def diagnose_campaign_targeting(customer_id, campaign_name_or_id):
    """Comprehensive targeting diagnostic for a specific campaign."""
```

### **Command Line Interface**

#### New Actions Added:
1. **`targeting`** - Basic targeting settings
2. **`targeting-summary`** - Detailed targeting with readable names  
3. **`diagnose-targeting`** - Comprehensive targeting diagnosis

#### New Arguments Added:
- **`--campaign-id`** - Specific campaign ID for targeting analysis
- **`--campaign-name`** - Campaign name or partial name for targeting diagnosis

## Usage Examples

### **1. Get Targeting for All Campaigns**
```bash
python instruments/custom/google_ads/campaign_analyzer.py \
  --customer-id "3045806466" \
  --action targeting
```
**Use Case**: Quick overview of all campaign targeting settings
**Output**: Raw targeting data with criterion IDs

### **2. Get Detailed Targeting Summary**
```bash
python instruments/custom/google_ads/campaign_analyzer.py \
  --customer-id "3045806466" \
  --action targeting-summary
```
**Use Case**: Detailed view with readable location and language names
**Output**: Formatted summary with human-readable names

### **3. Get Targeting for Specific Campaign by ID**
```bash
python instruments/custom/google_ads/campaign_analyzer.py \
  --customer-id "3045806466" \
  --action targeting \
  --campaign-id "12345"
```
**Use Case**: Focus on one specific campaign by ID
**Output**: Targeting settings for specified campaign only

### **4. Diagnose Targeting by Campaign Name**
```bash
python instruments/custom/google_ads/campaign_analyzer.py \
  --customer-id "3045806466" \
  --action diagnose-targeting \
  --campaign-name "Voice Training"
```
**Use Case**: Comprehensive targeting diagnosis for campaigns containing "Voice Training"
**Output**: Campaign info + complete targeting breakdown

### **5. Diagnose Targeting by Campaign ID**
```bash
python instruments/custom/google_ads/campaign_analyzer.py \
  --customer-id "3045806466" \
  --action diagnose-targeting \
  --campaign-id "12345"
```
**Use Case**: Comprehensive targeting diagnosis for specific campaign ID
**Output**: Campaign info + complete targeting breakdown

## Key Features

### **✅ Correct Resource Usage**
- **Uses `campaign_criterion` resource** - The correct resource for targeting settings
- **Supports both location and language targeting** - Comprehensive coverage
- **Handles negative targeting** - Shows excluded locations/languages
- **Status-aware** - Shows enabled/paused/removed criteria

### **✅ Flexible Query Options**
- **All campaigns** - Account-wide targeting overview
- **Specific campaign by ID** - Precise targeting for known campaign
- **Campaign search by name** - Find campaigns by partial name match
- **Multiple output formats** - Raw data or formatted summaries

### **✅ Human-Readable Output**
- **Geo target names** - "United States" instead of "geoTargetConstants/2840"
- **Language names** - "English" instead of "languageConstants/1000"
- **Country codes** - ISO country codes for locations
- **Target types** - City, State, Country, etc.

### **✅ Comprehensive Information**
- **Campaign basic info** - ID, name, status, channel type
- **Location targeting** - Included and excluded locations
- **Language targeting** - Target languages
- **Criterion status** - Active, paused, or removed targeting

## Error Handling

### **Missing Required Arguments**
```bash
# This will show error
python instruments/custom/google_ads/campaign_analyzer.py \
  --customer-id "3045806466" \
  --action diagnose-targeting

# Error: --campaign-name or --campaign-id required for targeting diagnosis
```

### **Invalid Customer ID**
```bash
# This will show Google Ads API error
python instruments/custom/google_ads/campaign_analyzer.py \
  --customer-id "invalid" \
  --action targeting

# Error: Google Ads API authentication or validation error
```

### **Non-existent Campaign**
```bash
# This will return empty results
python instruments/custom/google_ads/campaign_analyzer.py \
  --customer-id "3045806466" \
  --action targeting \
  --campaign-id "99999999"

# Result: No matching campaigns found
```

## Technical Implementation

### **Query Strategy**
1. **Basic targeting** - Single query to `campaign_criterion`
2. **Detailed summary** - Separate queries for locations and languages with joins
3. **Comprehensive diagnosis** - Multiple queries for campaign info + targeting

### **Resource Relationships**
- **`campaign_criterion`** ← Primary resource for targeting
- **`geo_target_constant`** ← Joined for location names
- **`language_constant`** ← Joined for language names
- **`campaign`** ← Joined for campaign information

### **Filter Logic**
- **Campaign status**: `IN ('ENABLED', 'PAUSED')` - Active campaigns only
- **Criterion type**: `IN ('LOCATION', 'LANGUAGE')` - Targeting criteria only
- **Campaign ID**: `campaign.id = {id}` - Specific campaign filter
- **Campaign name**: `campaign.name CONTAINS_IGNORE_CASE '{name}'` - Partial name search

## Status

✅ **Targeting diagnostic tool implemented**
✅ **Three levels of targeting analysis available**
✅ **Correct campaign_criterion resource usage**
✅ **Human-readable output with geo/language names**
✅ **Flexible campaign selection (ID or name)**
✅ **Comprehensive error handling**
✅ **Command-line interface integrated**
✅ **Documentation and examples provided**

**The targeting diagnostic tool is now fully functional and ready for production use.** 🎯

## Benefits

1. **🔍 Diagnostic Capability** - Quickly identify targeting issues
2. **📊 Comprehensive Analysis** - Complete targeting overview
3. **🎯 Precise Targeting** - Focus on specific campaigns
4. **📖 Readable Output** - Human-friendly location and language names
5. **🛠️ Troubleshooting** - Identify misconfigured targeting settings
6. **⚡ Quick Access** - Command-line interface for rapid diagnosis

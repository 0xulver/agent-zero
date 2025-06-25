# Google Ads Toolkit

A comprehensive toolkit for managing Google Ads campaigns, keywords, and performance analysis.

## 📁 Directory Structure

```
instruments/custom/google_ads/
├── 🔧 Core Tools
│   ├── campaign_operations.py      # Campaign management & operations
│   ├── campaign_creator.py         # Create new campaigns
│   ├── campaign_analyzer.py        # Campaign performance analysis
│   ├── campaign_manager.py         # High-level campaign management
│   ├── campaign_tools.py          # Modular campaign operations class
│   ├── keyword_research.py        # Keyword analysis & research
│   ├── keyword_simulator.py       # Keyword performance simulation
│   ├── keyword_tools.py           # Keyword utilities
│   ├── run_query.py               # Execute custom GAQL queries
│   └── query_runner.py            # Query execution utilities
│
├── 🛠️ Setup & Configuration
│   ├── setup_google_ads.py        # Initial setup wizard
│   ├── generate_refresh_token.py  # OAuth token generation
│   ├── google-ads.yaml           # API configuration
│   └── requirements.txt          # Python dependencies
│
├── 📚 Documentation & Examples
│   ├── google_ads.md             # Complete usage guide
│   ├── examples/                 # Sample configuration files
│   │   ├── ad_group_config.json
│   │   ├── budget_adjustments.json
│   │   ├── negative_keywords.json
│   │   └── new_keywords.json
│   └── examples/test_data/       # Test data for validation
│
├── 🧪 Tests & Validation
│   └── tests/                    # Test scripts for functionality
│       ├── test_connection.py
│       ├── test_ad_validation.py
│       ├── test_targeting_update.py
│       └── ...
│
└── 🔧 Utilities
    └── utils.py                  # Common utility functions
```

## 🚀 Quick Start

### 1. Setup
```bash
cd instruments/custom/google_ads
python setup_google_ads.py
```

### 2. Basic Usage
```bash
# Get campaign performance
python campaign_analyzer.py --customer-id "YOUR_ID" --action performance

# Research keywords
python keyword_research.py --customer-id "YOUR_ID" --action current

# Execute custom query
python run_query.py --customer-id "YOUR_ID" --query "SELECT campaign.name FROM campaign LIMIT 5"
```

## 📖 Core Tools Overview

### Campaign Management
- **`campaign_operations.py`** - Complete campaign operations (create, update, optimize)
- **`campaign_creator.py`** - Create new campaigns from configuration
- **`campaign_analyzer.py`** - Analyze campaign performance and metrics
- **`campaign_manager.py`** - High-level campaign management workflows

### Keyword Tools
- **`keyword_research.py`** - Comprehensive keyword analysis and research
- **`keyword_simulator.py`** - Simulate keyword performance scenarios (improved v2 with modular structure)
- **`keyword_tools.py`** - Keyword utilities and helper functions

### Query & Analysis
- **`run_query.py`** - Execute custom GAQL queries with flexible output (improved v2 with modular structure)
- **`query_runner.py`** - Query execution utilities and helpers

## 🎯 Agent-Friendly Design

This toolkit is optimized for AI agent usage:

### ✅ **Clear Separation of Concerns**
- **Core tools** in root directory for easy discovery
- **Test files** isolated in `tests/` folder
- **Examples** organized in `examples/` folder
- **Documentation** clearly marked

### ✅ **Consistent Interface**
- All tools use `--customer-id` parameter
- Standardized output formats (JSON, CSV, table)
- Clear error messages and validation

### ✅ **Comprehensive Documentation**
- `google_ads.md` - Complete usage guide
- Inline docstrings in all functions
- Example configurations provided

### ✅ **Robust Error Handling**
- Input validation before API calls
- Clear error messages with specific details
- Graceful failure handling

## 🔧 For Developers

### Running Tests
```bash
# Run specific test
python tests/test_connection.py

# Test ad validation
python tests/test_ad_validation.py
```

### Adding New Features
1. Add core functionality to appropriate tool file
2. Add tests to `tests/` folder
3. Add examples to `examples/` folder
4. Update documentation

## 📋 Key Features

- ✅ **Campaign Management** - Create, update, analyze campaigns
- ✅ **Keyword Research** - Find opportunities and analyze performance  
- ✅ **Ad Copy Validation** - Prevent API errors with length validation
- ✅ **Targeting Updates** - Add location and language targeting
- ✅ **Performance Analysis** - Comprehensive metrics and insights
- ✅ **Custom Queries** - Execute any GAQL query with flexible output
- ✅ **Batch Operations** - Efficient bulk updates and modifications

## 🎯 Agent Usage Tips

1. **Start with `google_ads.md`** for complete documentation
2. **Use core tools** in root directory for main functionality
3. **Check `examples/`** for sample configurations
4. **Run tests** to verify functionality before use
5. **Use `--help`** flag on any script for detailed usage

This organized structure makes it easy for agents to:
- Quickly identify core functionality
- Find relevant examples and test data
- Understand the toolkit capabilities
- Execute operations efficiently

#!/usr/bin/env python3
"""
Google Ads GAQL Query Runner

This standalone script executes Google Ads Query Language (GAQL) queries
against the Google Ads API using credentials from google-ads.yaml.
"""

import sys
import subprocess
import argparse
import json
import os

# Check and install dependencies
def install_dependencies():
    """Install required packages if not available."""
    required_packages = [
        'PyYAML',
        'google-ads>=24.0.0',
        'requests'
    ]
    
    for package in required_packages:
        try:
            if package.startswith('google-ads'):
                from google.ads.googleads.client import GoogleAdsClient
            else:
                __import__(package.lower().replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'])

# Install dependencies first
install_dependencies()

import yaml
import requests
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Configuration - multiple possible locations
CONFIG_PATHS = [
    "/a0/google-ads.yaml",           # Primary location when run by Agent Zero
    "google-ads.yaml",               # Current directory (for testing)
    "/root/google-ads.yaml",         # Home directory in container
    os.path.expanduser("~/google-ads.yaml")  # User home directory
]
API_VERSION = "v18"

def load_config():
    """Load the google-ads.yaml configuration file from multiple possible locations."""
    for config_path in CONFIG_PATHS:
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            print(f"✅ Loaded configuration from {config_path}")
            return config, config_path
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"❌ Error loading config from {config_path}: {e}")
            continue

    print(f"❌ Configuration file not found in any of these locations:")
    for path in CONFIG_PATHS:
        print(f"   - {path}")
    return None, None

def format_customer_id(customer_id):
    """Format customer ID to ensure it's 10 digits without dashes."""
    customer_id = str(customer_id)
    customer_id = customer_id.replace('\"', '').replace('"', '')
    customer_id = ''.join(char for char in customer_id if char.isdigit())
    return customer_id.zfill(10)

def execute_gaql_query(customer_id, query, output_format="table", debug=False):
    """
    Execute a GAQL query using the Google Ads API client library.

    Args:
        customer_id: Google Ads customer ID
        query: GAQL query string
        output_format: Output format ("table", "json", or "csv")
        debug: Enable debug output

    Returns:
        Formatted query results
    """
    try:
        # Load configuration
        config, config_file = load_config()
        if not config:
            return "❌ Failed to load configuration"
        
        # Check required fields
        required_fields = ['developer_token', 'client_id', 'client_secret', 'refresh_token']
        for field in required_fields:
            if not config.get(field) or config.get(field) == f"INSERT_{field.upper()}_HERE":
                return f"❌ Missing or incomplete field: {field}"
        
        # Initialize Google Ads client using the found config file
        try:
            client = GoogleAdsClient.load_from_storage(config_file)
            print(f"✅ Google Ads client initialized from {config_file}")
        except Exception as e:
            return f"❌ Failed to initialize Google Ads client: {e}"
        
        # Format customer ID
        formatted_customer_id = format_customer_id(customer_id)
        
        # Execute the query
        ga_service = client.get_service("GoogleAdsService")
        
        print(f"🔄 Executing query for customer {formatted_customer_id}...")
        print(f"Query: {query.strip()}")
        print()
        
        # Execute the search
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = formatted_customer_id
        search_request.query = query
        
        results = ga_service.search(request=search_request)

        # Debug: Print first row structure if debug mode
        if debug:
            try:
                first_row = next(iter(results))
                print(f"Debug: First row structure: {dir(first_row)}")
                if hasattr(first_row, 'campaign'):
                    print(f"Debug: Campaign object: {dir(first_row.campaign)}")
                    if hasattr(first_row.campaign, 'name'):
                        print(f"Debug: Campaign name: {first_row.campaign.name}")
            except StopIteration:
                print("Debug: No results found")
            # Reset results iterator
            results = ga_service.search(request=search_request)

        # Process results based on format
        if output_format.lower() == "json":
            return format_results_as_json(results, debug)
        elif output_format.lower() == "csv":
            return format_results_as_csv(results, query, debug)
        else:
            return format_results_as_table(results, query, debug)
            
    except GoogleAdsException as ex:
        error_msg = f"❌ Google Ads API Error:\n"
        error_msg += f"Request ID: {ex.request_id}\n"
        error_msg += f"Status: {ex.error.code().name}\n"
        error_msg += "Errors:\n"
        for error in ex.failure.errors:
            error_msg += f"  - {error.message}\n"
        return error_msg
        
    except Exception as ex:
        return f"❌ Error executing query: {ex}"

def format_results_as_json(results, debug=False):
    """Format results as JSON."""
    result_list = []
    for row in results:
        row_dict = {}

        # Handle campaign data
        if hasattr(row, 'campaign'):
            campaign_dict = {}
            if hasattr(row.campaign, 'name'):
                campaign_dict['name'] = row.campaign.name
            if hasattr(row.campaign, 'status'):
                campaign_dict['status'] = row.campaign.status.name if hasattr(row.campaign.status, 'name') else str(row.campaign.status)
            if hasattr(row.campaign, 'id'):
                campaign_dict['id'] = str(row.campaign.id)
            row_dict['campaign'] = campaign_dict

        # Handle metrics data
        if hasattr(row, 'metrics'):
            metrics_dict = {}
            if hasattr(row.metrics, 'clicks'):
                metrics_dict['clicks'] = str(row.metrics.clicks)
            if hasattr(row.metrics, 'impressions'):
                metrics_dict['impressions'] = str(row.metrics.impressions)
            if hasattr(row.metrics, 'cost_micros'):
                metrics_dict['cost_micros'] = str(row.metrics.cost_micros)
            if hasattr(row.metrics, 'conversions'):
                metrics_dict['conversions'] = str(row.metrics.conversions)
            row_dict['metrics'] = metrics_dict

        # Handle ad_group data
        if hasattr(row, 'ad_group'):
            ad_group_dict = {}
            if hasattr(row.ad_group, 'name'):
                ad_group_dict['name'] = row.ad_group.name
            if hasattr(row.ad_group, 'status'):
                ad_group_dict['status'] = row.ad_group.status.name if hasattr(row.ad_group.status, 'name') else str(row.ad_group.status)
            row_dict['ad_group'] = ad_group_dict

        result_list.append(row_dict)

    return json.dumps(result_list, indent=2)

def format_results_as_csv(results, query, debug=False):
    """Format results as CSV."""
    # Extract field names from the SELECT clause
    select_part = query.upper().split('FROM')[0].replace('SELECT', '').strip()
    fields = [field.strip() for field in select_part.split(',')]

    csv_lines = [','.join(fields)]

    for row in results:
        row_values = []
        for field in fields:
            # Navigate nested fields (e.g., campaign.name)
            value = get_nested_field_value_improved(row, field, debug)
            # Escape commas and quotes for CSV
            if ',' in str(value) or '"' in str(value):
                value = f'"{str(value).replace(chr(34), chr(34)+chr(34))}"'
            row_values.append(str(value))
        csv_lines.append(','.join(row_values))

    return '\n'.join(csv_lines)

def format_results_as_table(results, query, debug=False):
    """Format results as a readable table."""
    # Extract field names from the SELECT clause
    select_part = query.upper().split('FROM')[0].replace('SELECT', '').strip()
    fields = [field.strip() for field in select_part.split(',')]

    # Collect all rows first to determine column widths
    rows = []
    for row in results:
        row_values = []
        for field in fields:
            value = get_nested_field_value_improved(row, field, debug)
            row_values.append(str(value))
        rows.append(row_values)

    if not rows:
        return "No results found for the query."

    # Calculate column widths
    col_widths = []
    for i, field in enumerate(fields):
        max_width = len(field)
        for row in rows:
            if i < len(row):
                max_width = max(max_width, len(row[i]))
        col_widths.append(min(max_width, 50))  # Cap at 50 chars

    # Format header
    header = " | ".join(field.ljust(col_widths[i]) for i, field in enumerate(fields))
    separator = "-+-".join("-" * width for width in col_widths)

    # Format rows
    formatted_rows = []
    for row in rows:
        formatted_row = " | ".join(
            (row[i] if i < len(row) else "").ljust(col_widths[i])[:col_widths[i]]
            for i in range(len(fields))
        )
        formatted_rows.append(formatted_row)

    result = [header, separator] + formatted_rows
    return '\n'.join(result)

def get_nested_field_value_improved(row, field_path, debug=False):
    """Improved function to get value from nested field path like 'campaign.name'."""
    try:
        # Clean up the field path
        field_path = field_path.strip()
        parts = [part.strip() for part in field_path.split('.')]

        if debug:
            print(f"Debug: Extracting field path: {field_path} -> {parts}")

        current = row

        # Navigate through the nested structure
        for i, part in enumerate(parts):
            part_lower = part.lower()

            if debug:
                print(f"Debug: Looking for part '{part}' in object with attributes: {[attr for attr in dir(current) if not attr.startswith('_')]}")

            if hasattr(current, part_lower):
                current = getattr(current, part_lower)
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                if debug:
                    print(f"Debug: Part '{part}' not found")
                return "N/A"

        # Handle different types of values
        if current is None:
            return "N/A"
        elif hasattr(current, 'name'):  # For enum values like status
            return current.name
        elif hasattr(current, 'value'):  # For some protobuf values
            return str(current.value)
        else:
            result = str(current)
            if debug:
                print(f"Debug: Final value for {field_path}: {result}")
            return result

    except Exception as e:
        if debug:
            print(f"Debug: Error getting field {field_path}: {e}")
        return "N/A"

def get_nested_field_value(row, field_path):
    """Get value from nested field path like 'campaign.name'."""
    return get_nested_field_value_improved(row, field_path, debug=False)

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Execute Google Ads GAQL queries')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--query', required=True, help='GAQL query to execute')
    parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table',
                       help='Output format (default: table)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    print("🚀 Google Ads GAQL Query Runner")
    print("=" * 35)

    result = execute_gaql_query(args.customer_id, args.query, args.format, args.debug)
    print(result)

if __name__ == "__main__":
    main()

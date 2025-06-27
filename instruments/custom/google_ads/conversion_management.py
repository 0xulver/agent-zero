#!/usr/bin/env python3
"""
Google Ads Conversion Management Tool

This script provides comprehensive conversion action management functionality:
- Create new conversion actions
- List existing conversion actions
- Update conversion action settings
- Enable/disable conversion actions
- Set conversion values and attribution models

Usage:
    python conversion_management.py --customer-id "1234567890" --action list
    python conversion_management.py --customer-id "1234567890" --action create --name "Newsletter Signup" --category SIGNUP --value 5.0
    python conversion_management.py --customer-id "1234567890" --action update --conversion-id "123456" --status ENABLED
"""

import argparse
import sys
import os
import json
from typing import Optional, Dict, Any, List

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
except ImportError as e:
    print(f"❌ Error importing Google Ads libraries: {e}")
    print("💡 Make sure to install: pip install google-ads")
    sys.exit(1)

def get_google_ads_client():
    """Get authenticated Google Ads client with robust credential loading."""
    credentials_paths = [
        'google-ads.yaml',
        'instruments/custom/google_ads/google-ads.yaml',
        '/a0/google-ads.yaml',
        os.path.expanduser('~/google-ads.yaml'),
        os.path.join(os.path.dirname(__file__), 'google-ads.yaml')
    ]
    
    for path in credentials_paths:
        try:
            if os.path.exists(path):
                return GoogleAdsClient.load_from_storage(path)
        except Exception:
            continue
    
    # Try default location
    return GoogleAdsClient.load_from_storage()

def list_conversion_actions(customer_id: str, output_format: str = "table") -> str:
    """List all conversion actions for the account."""
    try:
        client = get_google_ads_client()
        ga_service = client.get_service("GoogleAdsService")
        
        query = """
        SELECT
            conversion_action.id,
            conversion_action.name,
            conversion_action.category,
            conversion_action.type,
            conversion_action.status,
            conversion_action.primary_for_goal,
            conversion_action.value_settings.default_value,
            conversion_action.value_settings.default_currency_code,
            conversion_action.attribution_model_settings.attribution_model,
            conversion_action.click_through_lookback_window_days,
            conversion_action.view_through_lookback_window_days
        FROM conversion_action
        WHERE conversion_action.status != 'REMOVED'
        ORDER BY conversion_action.name
        """
        
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = query
        
        response = ga_service.search(request=search_request)
        
        conversions = []
        for row in response:
            ca = row.conversion_action
            conversion_data = {
                'id': ca.id,
                'name': ca.name,
                'category': ca.category.name,
                'type': ca.type.name,
                'status': ca.status.name,
                'primary_for_goal': ca.primary_for_goal,
                'default_value': ca.value_settings.default_value if ca.value_settings else None,
                'currency_code': ca.value_settings.default_currency_code if ca.value_settings else None,
                'attribution_model': ca.attribution_model_settings.attribution_model.name if ca.attribution_model_settings else None,
                'click_lookback_days': ca.click_through_lookback_window_days,
                'view_lookback_days': ca.view_through_lookback_window_days
            }
            conversions.append(conversion_data)
        
        if output_format == "json":
            return json.dumps(conversions, indent=2)
        else:
            # Format as table
            result = ["🎯 CONVERSION ACTIONS", "=" * 50]
            
            if not conversions:
                result.append("No conversion actions found.")
                return "\n".join(result)
            
            for conv in conversions:
                result.append(f"\n📊 {conv['name']} (ID: {conv['id']})")
                result.append(f"   Category: {conv['category']}")
                result.append(f"   Type: {conv['type']}")
                result.append(f"   Status: {conv['status']}")
                result.append(f"   Primary for Goal: {conv['primary_for_goal']}")
                if conv['default_value']:
                    result.append(f"   Default Value: {conv['default_value']} {conv['currency_code']}")
                result.append(f"   Attribution: {conv['attribution_model']}")
                result.append(f"   Click Lookback: {conv['click_lookback_days']} days")
                result.append(f"   View Lookback: {conv['view_lookback_days']} days")
            
            return "\n".join(result)
            
    except GoogleAdsException as ex:
        error_msg = f"❌ Google Ads API Error:\n"
        for error in ex.failure.errors:
            error_msg += f"  {error.message}\n"
        return error_msg
    except Exception as e:
        return f"❌ Error listing conversion actions: {e}"

def create_conversion_action(
    customer_id: str,
    name: str,
    category: str,
    value: Optional[float] = None,
    currency_code: str = "USD",
    attribution_model: str = "LAST_CLICK",
    click_lookback_days: int = 30,
    view_lookback_days: int = 1,
    primary_for_goal: bool = True
) -> str:
    """Create a new conversion action."""
    try:
        client = get_google_ads_client()
        conversion_action_service = client.get_service("ConversionActionService")

        # Create conversion action
        conversion_action = client.get_type("ConversionAction")
        conversion_action.name = name

        # Set category using proper enum access
        if hasattr(client.enums.ConversionActionCategoryEnum, category.upper()):
            conversion_action.category = getattr(client.enums.ConversionActionCategoryEnum, category.upper())
        else:
            # Fallback for common categories
            category_map = {
                'PURCHASE': client.enums.ConversionActionCategoryEnum.PURCHASE,
                'SIGNUP': client.enums.ConversionActionCategoryEnum.SIGNUP,
                'LEAD': client.enums.ConversionActionCategoryEnum.LEAD,
                'DOWNLOAD': client.enums.ConversionActionCategoryEnum.DOWNLOAD,
                'ADD_TO_CART': client.enums.ConversionActionCategoryEnum.ADD_TO_CART,
                'BEGIN_CHECKOUT': client.enums.ConversionActionCategoryEnum.BEGIN_CHECKOUT,
                'SUBSCRIBE': client.enums.ConversionActionCategoryEnum.SUBSCRIBE,
                'CONTACT': client.enums.ConversionActionCategoryEnum.CONTACT
            }
            conversion_action.category = category_map.get(category.upper(), client.enums.ConversionActionCategoryEnum.DEFAULT)

        # Set type and status
        conversion_action.type_ = client.enums.ConversionActionTypeEnum.WEBPAGE
        conversion_action.status = client.enums.ConversionActionStatusEnum.ENABLED
        conversion_action.primary_for_goal = primary_for_goal
        conversion_action.click_through_lookback_window_days = click_lookback_days
        conversion_action.view_through_lookback_window_days = view_lookback_days

        # Set value settings if provided
        if value is not None:
            conversion_action.value_settings.default_value = value
            conversion_action.value_settings.default_currency_code = currency_code
            conversion_action.value_settings.always_use_default_value = True

        # Set attribution model using correct enum values
        attribution_map = {
            'LAST_CLICK': client.enums.AttributionModelEnum.GOOGLE_ADS_LAST_CLICK,
            'FIRST_CLICK': client.enums.AttributionModelEnum.GOOGLE_SEARCH_ATTRIBUTION_FIRST_CLICK,
            'LINEAR': client.enums.AttributionModelEnum.GOOGLE_SEARCH_ATTRIBUTION_LINEAR,
            'TIME_DECAY': client.enums.AttributionModelEnum.GOOGLE_SEARCH_ATTRIBUTION_TIME_DECAY,
            'POSITION_BASED': client.enums.AttributionModelEnum.GOOGLE_SEARCH_ATTRIBUTION_POSITION_BASED,
            'DATA_DRIVEN': client.enums.AttributionModelEnum.GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN
        }
        conversion_action.attribution_model_settings.attribution_model = attribution_map.get(
            attribution_model.upper(), client.enums.AttributionModelEnum.GOOGLE_ADS_LAST_CLICK
        )

        # Create operation
        operation = client.get_type("ConversionActionOperation")
        operation.create = conversion_action

        # Execute request
        request = client.get_type("MutateConversionActionsRequest")
        request.customer_id = customer_id
        request.operations = [operation]

        response = conversion_action_service.mutate_conversion_actions(request=request)

        result = response.results[0]
        return f"✅ Created conversion action: {result.resource_name}"

    except GoogleAdsException as ex:
        error_msg = f"❌ Google Ads API Error:\n"
        for error in ex.failure.errors:
            error_msg += f"  {error.message}\n"
        return error_msg
    except Exception as e:
        return f"❌ Error creating conversion action: {e}"

def update_conversion_action(
    customer_id: str,
    conversion_action_id: str,
    status: Optional[str] = None,
    name: Optional[str] = None,
    value: Optional[float] = None,
    currency_code: Optional[str] = None,
    primary_for_goal: Optional[bool] = None
) -> str:
    """Update an existing conversion action."""
    try:
        client = get_google_ads_client()
        conversion_action_service = client.get_service("ConversionActionService")
        
        # Create conversion action resource name
        resource_name = conversion_action_service.conversion_action_path(
            customer_id, conversion_action_id
        )
        
        # Create conversion action with updates
        conversion_action = client.get_type("ConversionAction")
        conversion_action.resource_name = resource_name

        # Create field mask for updates
        paths = []
        
        if status:
            status_map = {
                'ENABLED': client.enums.ConversionActionStatusEnum.ENABLED,
                'DISABLED': client.enums.ConversionActionStatusEnum.HIDDEN,
                'REMOVED': client.enums.ConversionActionStatusEnum.REMOVED
            }
            conversion_action.status = status_map.get(status.upper(), client.enums.ConversionActionStatusEnum.ENABLED)
            paths.append("status")
        
        if name:
            conversion_action.name = name
            paths.append("name")
        
        if value is not None:
            conversion_action.value_settings.default_value = value
            paths.append("value_settings.default_value")
            if currency_code:
                conversion_action.value_settings.default_currency_code = currency_code
                paths.append("value_settings.default_currency_code")
        
        if primary_for_goal is not None:
            conversion_action.primary_for_goal = primary_for_goal
            paths.append("primary_for_goal")
        
        # Create field mask manually
        update_mask = {"paths": paths}

        # Create operation
        operation = client.get_type("ConversionActionOperation")
        operation.update = conversion_action
        operation.update_mask = update_mask
        
        # Execute request
        request = client.get_type("MutateConversionActionsRequest")
        request.customer_id = customer_id
        request.operations = [operation]
        
        response = conversion_action_service.mutate_conversion_actions(request=request)
        
        result = response.results[0]
        return f"✅ Updated conversion action: {result.resource_name}"
        
    except GoogleAdsException as ex:
        error_msg = f"❌ Google Ads API Error:\n"
        for error in ex.failure.errors:
            error_msg += f"  {error.message}\n"
        return error_msg
    except Exception as e:
        return f"❌ Error updating conversion action: {e}"

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Google Ads Conversion Management Tool')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--action', required=True, 
                       choices=['list', 'create', 'update'],
                       help='Action to perform')
    parser.add_argument('--format', default='table', choices=['table', 'json'],
                       help='Output format for list action')
    
    # Create action arguments
    parser.add_argument('--name', help='Conversion action name')
    parser.add_argument('--category', 
                       choices=['PURCHASE', 'SIGNUP', 'LEAD', 'DOWNLOAD', 'ADD_TO_CART', 'BEGIN_CHECKOUT', 'SUBSCRIBE', 'PHONE_CALL_LEAD', 'IMPORTED_LEAD', 'SUBMIT_LEAD_FORM', 'BOOK_APPOINTMENT', 'REQUEST_QUOTE', 'GET_DIRECTIONS', 'OUTBOUND_CLICK', 'CONTACT', 'ENGAGEMENT', 'STORE_VISIT', 'STORE_SALE', 'QUALIFIED_LEAD', 'CONVERTED_LEAD'],
                       help='Conversion category')
    parser.add_argument('--value', type=float, help='Default conversion value')
    parser.add_argument('--currency', default='USD', help='Currency code (default: USD)')
    parser.add_argument('--attribution-model', default='LAST_CLICK',
                       choices=['LAST_CLICK', 'FIRST_CLICK', 'LINEAR', 'TIME_DECAY', 'POSITION_BASED', 'DATA_DRIVEN'],
                       help='Attribution model (default: LAST_CLICK)')
    parser.add_argument('--click-lookback-days', type=int, default=30,
                       help='Click-through lookback window in days (default: 30)')
    parser.add_argument('--view-lookback-days', type=int, default=1,
                       help='View-through lookback window in days (default: 1)')
    parser.add_argument('--primary-for-goal', type=bool, default=True,
                       help='Whether this is primary for goal (default: True)')
    
    # Update action arguments
    parser.add_argument('--conversion-id', help='Conversion action ID for update')
    parser.add_argument('--status', choices=['ENABLED', 'DISABLED'],
                       help='New status for conversion action (ENABLED or DISABLED)')
    
    args = parser.parse_args()
    
    print("🎯 Google Ads Conversion Management Tool")
    print("=" * 45)
    
    if args.action == 'list':
        result = list_conversion_actions(args.customer_id, args.format)
    elif args.action == 'create':
        if not args.name or not args.category:
            print("❌ Error: --name and --category are required for create action")
            return 1
        result = create_conversion_action(
            args.customer_id,
            args.name,
            args.category,
            args.value,
            args.currency,
            args.attribution_model,
            args.click_lookback_days,
            args.view_lookback_days,
            args.primary_for_goal
        )
    elif args.action == 'update':
        if not args.conversion_id:
            print("❌ Error: --conversion-id is required for update action")
            return 1
        result = update_conversion_action(
            args.customer_id,
            args.conversion_id,
            args.status,
            args.name,
            args.value,
            args.currency,
            args.primary_for_goal
        )
    else:
        result = "❌ Error: Invalid action specified"
        return 1

    print(result)
    return 0

if __name__ == "__main__":
    sys.exit(main())

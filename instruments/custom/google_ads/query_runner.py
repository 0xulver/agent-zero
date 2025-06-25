"""
GAQL Query Runner Module

This module provides functionality to execute Google Ads Query Language (GAQL)
queries against the Google Ads API with various output formats.
"""

import json
from typing import List, Dict, Any, Optional, Union
from tabulate import tabulate

try:
    from .utils import get_google_ads_client, validate_customer_id, print_section_header
except ImportError:
    from utils import get_google_ads_client, validate_customer_id, print_section_header


def run_gaql_query(
    customer_id: str, 
    query: str, 
    output_format: str = "table",
    config_path: Optional[str] = None
) -> Union[str, List[Dict[str, Any]]]:
    """
    Execute a GAQL query and return results in the specified format.
    
    Args:
        customer_id: Google Ads customer ID
        query: GAQL query string
        output_format: Output format ('table', 'json', 'csv', 'raw')
        config_path: Path to google-ads.yaml config file
        
    Returns:
        Query results in the specified format
    """
    try:
        # Validate customer ID
        customer_id = validate_customer_id(customer_id)
        
        # Get Google Ads client
        client = get_google_ads_client(config_path)
        
        # Execute query
        googleads_service = client.get_service("GoogleAdsService")
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = query
        
        response = googleads_service.search(request=search_request)
        
        # Process results
        results = []
        for row in response:
            row_data = _extract_row_data(row, query)
            if row_data:  # Only add non-empty rows
                results.append(row_data)
        
        # Format output
        return _format_output(results, output_format, query)
        
    except Exception as e:
        error_msg = f"❌ Error executing GAQL query: {str(e)}"
        if output_format == "json":
            return json.dumps({"error": str(e)})
        else:
            return error_msg


def _extract_row_data(row, query: str) -> Dict[str, Any]:
    """Extract data from a Google Ads API response row."""
    row_data = {}

    try:
        # Extract fields based on what's available in the row
        # Handle campaign data
        if hasattr(row, 'campaign'):
            campaign = row.campaign
            if hasattr(campaign, 'id'):
                row_data['campaign.id'] = campaign.id
            if hasattr(campaign, 'name'):
                row_data['campaign.name'] = campaign.name
            if hasattr(campaign, 'status'):
                row_data['campaign.status'] = campaign.status.name if hasattr(campaign.status, 'name') else str(campaign.status)
            if hasattr(campaign, 'advertising_channel_type'):
                row_data['campaign.advertising_channel_type'] = campaign.advertising_channel_type.name if hasattr(campaign.advertising_channel_type, 'name') else str(campaign.advertising_channel_type)
            if hasattr(campaign, 'bidding_strategy_type'):
                row_data['campaign.bidding_strategy_type'] = campaign.bidding_strategy_type.name if hasattr(campaign.bidding_strategy_type, 'name') else str(campaign.bidding_strategy_type)

        # Handle campaign budget data
        if hasattr(row, 'campaign_budget'):
            budget = row.campaign_budget
            if hasattr(budget, 'amount_micros'):
                row_data['campaign_budget.amount_micros'] = budget.amount_micros
            if hasattr(budget, 'name'):
                row_data['campaign_budget.name'] = budget.name

        # Handle ad group data
        if hasattr(row, 'ad_group'):
            ad_group = row.ad_group
            if hasattr(ad_group, 'id'):
                row_data['ad_group.id'] = ad_group.id
            if hasattr(ad_group, 'name'):
                row_data['ad_group.name'] = ad_group.name
            if hasattr(ad_group, 'status'):
                row_data['ad_group.status'] = ad_group.status.name if hasattr(ad_group.status, 'name') else str(ad_group.status)

        # Handle ad group criterion (keywords) data
        if hasattr(row, 'ad_group_criterion'):
            criterion = row.ad_group_criterion
            if hasattr(criterion, 'keyword'):
                keyword = criterion.keyword
                if hasattr(keyword, 'text'):
                    row_data['ad_group_criterion.keyword.text'] = keyword.text
                if hasattr(keyword, 'match_type'):
                    row_data['ad_group_criterion.keyword.match_type'] = keyword.match_type.name if hasattr(keyword.match_type, 'name') else str(keyword.match_type)
            if hasattr(criterion, 'status'):
                row_data['ad_group_criterion.status'] = criterion.status.name if hasattr(criterion.status, 'name') else str(criterion.status)

        # Handle metrics data
        if hasattr(row, 'metrics'):
            metrics = row.metrics
            metric_fields = [
                'impressions', 'clicks', 'cost_micros', 'conversions', 'conversions_value',
                'ctr', 'average_cpc', 'cost_per_conversion', 'search_impression_share',
                'search_rank_lost_impression_share', 'top_impression_percentage',
                'absolute_top_impression_percentage'
            ]

            for field in metric_fields:
                if hasattr(metrics, field):
                    row_data[f'metrics.{field}'] = getattr(metrics, field)

        # Handle segments data
        if hasattr(row, 'segments'):
            segments = row.segments
            if hasattr(segments, 'date'):
                row_data['segments.date'] = segments.date
            if hasattr(segments, 'device'):
                row_data['segments.device'] = segments.device.name if hasattr(segments.device, 'name') else str(segments.device)

        # Handle customer data
        if hasattr(row, 'customer'):
            customer = row.customer
            if hasattr(customer, 'id'):
                row_data['customer.id'] = customer.id
            if hasattr(customer, 'descriptive_name'):
                row_data['customer.descriptive_name'] = customer.descriptive_name

    except Exception as e:
        # If extraction fails, try a fallback approach
        try:
            # Fallback: try to extract any available fields
            for attr_name in dir(row):
                if not attr_name.startswith('_') and attr_name not in ['DESCRIPTOR', 'WhichOneof']:
                    try:
                        attr_value = getattr(row, attr_name)
                        if hasattr(attr_value, 'DESCRIPTOR'):
                            # This is a protobuf message
                            row_data.update(_extract_protobuf_fields(attr_value, attr_name))
                        else:
                            row_data[attr_name] = attr_value
                    except Exception:
                        continue
        except Exception:
            pass

    return row_data


def _extract_protobuf_fields(pb_obj, prefix: str = "") -> Dict[str, Any]:
    """Extract fields from a protobuf object."""
    fields = {}

    try:
        # Get all field descriptors
        for field_descriptor in pb_obj.DESCRIPTOR.fields:
            field_name = field_descriptor.name
            full_field_name = f"{prefix}.{field_name}" if prefix else field_name

            try:
                field_value = getattr(pb_obj, field_name)

                # Handle different field types
                if hasattr(field_value, 'DESCRIPTOR'):
                    # Nested message - only go one level deep to avoid infinite recursion
                    if prefix.count('.') < 2:
                        fields.update(_extract_protobuf_fields(field_value, full_field_name))
                elif isinstance(field_value, (list, tuple)):
                    # Repeated field
                    if field_value and len(field_value) < 10:  # Limit list size
                        if hasattr(field_value[0], 'DESCRIPTOR'):
                            # List of messages - only process first few items
                            for i, item in enumerate(field_value[:3]):
                                fields.update(_extract_protobuf_fields(item, f"{full_field_name}[{i}]"))
                        else:
                            # List of primitives
                            fields[full_field_name] = list(field_value)
                else:
                    # Primitive field
                    if hasattr(field_value, 'name'):
                        # Enum field
                        fields[full_field_name] = field_value.name
                    else:
                        fields[full_field_name] = field_value

            except Exception:
                # Skip fields that can't be accessed
                continue

    except Exception:
        # If we can't process the protobuf, just return empty dict
        pass

    return fields


def _format_output(results: List[Dict[str, Any]], output_format: str, query: str) -> Union[str, List[Dict[str, Any]]]:
    """Format query results according to the specified output format."""

    if not results:
        if output_format == "json":
            return json.dumps([])
        else:
            return "No results found."

    # Extract requested fields from the query
    requested_fields = _extract_requested_fields(query)

    if output_format.lower() == "json":
        # Filter results to only include requested fields
        filtered_results = []
        for result in results:
            filtered_result = {}
            for field in requested_fields:
                if field in result:
                    filtered_result[field] = result[field]
            if filtered_result:
                filtered_results.append(filtered_result)
        return json.dumps(filtered_results, indent=2, default=str)

    elif output_format.lower() == "raw":
        return results

    elif output_format.lower() == "csv":
        if not results:
            return ""

        # Use requested fields as headers
        headers = requested_fields if requested_fields else sorted(results[0].keys())

        # Create CSV
        csv_lines = []
        csv_lines.append(",".join(headers))

        for result in results:
            row = []
            for header in headers:
                value = result.get(header, "")
                # Escape commas and quotes in CSV
                if isinstance(value, str) and ("," in value or '"' in value):
                    value = f'"{value.replace(chr(34), chr(34)+chr(34))}"'
                row.append(str(value))
            csv_lines.append(",".join(row))

        return "\n".join(csv_lines)

    else:  # Default to table format
        if not results:
            return "No results found."

        # Use requested fields as headers, or all available fields if none specified
        headers = requested_fields if requested_fields else sorted(results[0].keys())

        # Create table data
        table_data = []
        for result in results:
            row = []
            for header in headers:
                value = result.get(header, "")
                # Truncate long values for table display
                if isinstance(value, str) and len(value) > 30:
                    value = value[:27] + "..."
                row.append(value)
            table_data.append(row)

        # Format as table
        table_output = tabulate(table_data, headers=headers, tablefmt="grid")

        # Add query info
        output_lines = []
        output_lines.append(f"Query: {query}")
        output_lines.append(f"Results: {len(results)} rows")
        output_lines.append("")
        output_lines.append(table_output)

        return "\n".join(output_lines)


def _extract_requested_fields(query: str) -> List[str]:
    """Extract the requested fields from a GAQL SELECT query."""
    try:
        # Find the SELECT clause
        query_upper = query.upper()
        select_start = query_upper.find("SELECT")
        from_start = query_upper.find("FROM")

        if select_start == -1 or from_start == -1:
            return []

        # Extract the field list
        select_clause = query[select_start + 6:from_start].strip()

        # Split by comma and clean up field names
        fields = []
        for field in select_clause.split(','):
            field = field.strip()
            # Remove any aliases (AS keyword)
            if ' AS ' in field.upper():
                field = field.split(' AS ')[0].strip()
            fields.append(field)

        return fields

    except Exception:
        return []


def validate_gaql_query(query: str) -> tuple[bool, str]:
    """
    Validate a GAQL query for basic syntax.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    query = query.strip()
    
    if not query:
        return False, "Query cannot be empty"
    
    if not query.upper().startswith("SELECT"):
        return False, "Query must start with SELECT"
    
    if "FROM" not in query.upper():
        return False, "Query must contain FROM clause"
    
    # Check for balanced parentheses
    open_parens = query.count("(")
    close_parens = query.count(")")
    if open_parens != close_parens:
        return False, "Unbalanced parentheses in query"
    
    return True, ""

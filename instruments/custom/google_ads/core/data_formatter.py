"""
Data Formatter for Google Ads API responses
Handles formatting of API responses into various output formats
"""

import json
import csv
import io
from typing import Dict, List, Any, Optional
from datetime import datetime

class DataFormatter:
    """Formats Google Ads API response data into various output formats"""
    
    @staticmethod
    def format_currency(micros: int, currency_code: str = "USD") -> str:
        """
        Convert micros to currency format
        
        Args:
            micros: Amount in micros (millionths)
            currency_code: Currency code (e.g., USD, EUR)
            
        Returns:
            Formatted currency string
        """
        if micros == 0:
            return f"0.00 {currency_code}"
        
        amount = micros / 1_000_000
        return f"{amount:.2f} {currency_code}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format decimal as percentage"""
        return f"{value * 100:.2f}%"
    
    @staticmethod
    def extract_fields_from_results(results: List[Dict]) -> List[str]:
        """
        Extract field names from GAQL results
        
        Args:
            results: List of result dictionaries
            
        Returns:
            List of field names
        """
        if not results:
            return []
        
        fields = []
        first_result = results[0]
        
        for key, value in first_result.items():
            if isinstance(value, dict):
                for subkey in value:
                    fields.append(f"{key}.{subkey}")
            else:
                fields.append(key)
        
        return fields
    
    @staticmethod
    def get_field_value(result: Dict, field: str) -> str:
        """
        Get field value from result, handling nested fields
        
        Args:
            result: Single result dictionary
            field: Field name (may be nested like "campaign.name")
            
        Returns:
            String value of the field
        """
        if "." in field:
            parent, child = field.split(".", 1)
            parent_value = result.get(parent, {})
            if isinstance(parent_value, dict):
                return str(parent_value.get(child, ""))
            return ""
        else:
            return str(result.get(field, ""))
    
    def format_as_table(self, data: Dict, currency_code: str = "USD") -> str:
        """
        Format API response as a readable table
        
        Args:
            data: API response dictionary
            currency_code: Currency code for formatting costs
            
        Returns:
            Formatted table string
        """
        if not data.get("success"):
            return f"Error: {data.get('error', 'Unknown error')}"
        
        results = data.get("results", [])
        if not results:
            return "No results found."
        
        # Extract field names and calculate column widths
        fields = self.extract_fields_from_results(results)
        field_widths = {field: len(field) for field in fields}
        
        # Calculate maximum field widths
        for result in results:
            for field in fields:
                value = self.get_field_value(result, field)
                # Format cost fields
                if "cost_micros" in field and value.isdigit():
                    value = self.format_currency(int(value), currency_code)
                # Format CTR fields
                elif "ctr" in field and value.replace(".", "").isdigit():
                    value = self.format_percentage(float(value))
                
                field_widths[field] = max(field_widths[field], len(str(value)))
        
        # Build table
        lines = []
        lines.append(f"Results for Customer ID: {data.get('customer_id', 'Unknown')}")
        lines.append("=" * 80)
        
        # Header
        header = " | ".join(f"{field:{field_widths[field]}}" for field in fields)
        lines.append(header)
        lines.append("-" * len(header))
        
        # Data rows
        for result in results:
            row_data = []
            for field in fields:
                value = self.get_field_value(result, field)
                
                # Format special fields
                if "cost_micros" in field and value.isdigit():
                    value = self.format_currency(int(value), currency_code)
                elif "ctr" in field and value.replace(".", "").isdigit():
                    value = self.format_percentage(float(value))
                
                row_data.append(f"{value:{field_widths[field]}}")
            
            lines.append(" | ".join(row_data))
        
        lines.append("")
        lines.append(f"Total results: {len(results)}")
        
        return "\n".join(lines)
    
    def format_as_csv(self, data: Dict, currency_code: str = "USD") -> str:
        """
        Format API response as CSV
        
        Args:
            data: API response dictionary
            currency_code: Currency code for formatting costs
            
        Returns:
            CSV formatted string
        """
        if not data.get("success"):
            return f"Error,{data.get('error', 'Unknown error')}"
        
        results = data.get("results", [])
        if not results:
            return "No results found"
        
        # Extract field names
        fields = self.extract_fields_from_results(results)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(fields)
        
        # Write data rows
        for result in results:
            row_data = []
            for field in fields:
                value = self.get_field_value(result, field)
                
                # Format special fields
                if "cost_micros" in field and value.isdigit():
                    value = str(int(value) / 1_000_000)  # Convert to currency units
                elif "ctr" in field and value.replace(".", "").isdigit():
                    value = str(float(value) * 100)  # Convert to percentage
                
                row_data.append(value)
            
            writer.writerow(row_data)
        
        return output.getvalue()
    
    def format_as_json(self, data: Dict) -> str:
        """
        Format API response as pretty JSON
        
        Args:
            data: API response dictionary
            
        Returns:
            JSON formatted string
        """
        return json.dumps(data, indent=2, default=str)
    
    def format_accounts_list(self, data: Dict) -> str:
        """
        Format accounts list in a readable format
        
        Args:
            data: Accounts list response
            
        Returns:
            Formatted accounts string
        """
        if not data.get("success"):
            return f"Error: {data.get('error', 'Unknown error')}"
        
        accounts = data.get("accounts", [])
        if not accounts:
            return "No accessible accounts found."
        
        lines = []
        lines.append("Accessible Google Ads Accounts:")
        lines.append("=" * 50)
        
        for i, account in enumerate(accounts, 1):
            lines.append(f"{i}. Account ID: {account['customer_id']}")
        
        lines.append("")
        lines.append(f"Total accounts: {len(accounts)}")
        
        return "\n".join(lines)
    
    def create_summary_report(self, data: Dict, report_type: str, currency_code: str = "USD") -> str:
        """
        Create a summary report from performance data
        
        Args:
            data: API response dictionary
            report_type: Type of report (campaign, ad, etc.)
            currency_code: Currency code for formatting
            
        Returns:
            Summary report string
        """
        if not data.get("success"):
            return f"Error generating {report_type} report: {data.get('error', 'Unknown error')}"
        
        results = data.get("results", [])
        if not results:
            return f"No {report_type} data found."
        
        # Calculate totals
        total_impressions = 0
        total_clicks = 0
        total_cost = 0
        total_conversions = 0
        
        for result in results:
            metrics = result.get("metrics", {})
            total_impressions += int(metrics.get("impressions", 0))
            total_clicks += int(metrics.get("clicks", 0))
            total_cost += int(metrics.get("costMicros", 0))
            total_conversions += float(metrics.get("conversions", 0))
        
        # Calculate averages
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
        lines = []
        lines.append(f"{report_type.title()} Performance Summary")
        lines.append("=" * 50)
        lines.append(f"Customer ID: {data.get('customer_id', 'Unknown')}")
        lines.append(f"Total {report_type}s: {len(results)}")
        lines.append("")
        lines.append("Overall Metrics:")
        lines.append(f"  Total Impressions: {total_impressions:,}")
        lines.append(f"  Total Clicks: {total_clicks:,}")
        lines.append(f"  Total Cost: {self.format_currency(total_cost, currency_code)}")
        lines.append(f"  Total Conversions: {total_conversions:.2f}")
        lines.append("")
        lines.append("Average Metrics:")
        lines.append(f"  CTR: {avg_ctr:.2f}%")
        lines.append(f"  CPC: {self.format_currency(int(avg_cpc), currency_code)}")
        lines.append(f"  Conversion Rate: {conversion_rate:.2f}%")
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)

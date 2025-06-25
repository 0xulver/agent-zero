#!/usr/bin/env python3
"""
Google Ads GAQL Query Runner v2

This is the new modular version of the GAQL query runner that uses
absolute imports and proper module structure to avoid ImportError issues.
"""

import sys
import os
import argparse

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import from our modular structure
try:
    from query_runner import run_gaql_query, validate_gaql_query
    from utils import install_dependencies, validate_customer_id, print_section_header
except ImportError as e:
    print(f"❌ Import error: {e}", file=sys.stderr)
    print("Installing dependencies and retrying...", file=sys.stderr)
    
    # Fallback: install dependencies and try again
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-ads>=26.0.0", "PyYAML", "tabulate"])
    
    try:
        from query_runner import run_gaql_query, validate_gaql_query
        from utils import install_dependencies, validate_customer_id, print_section_header
    except ImportError as e2:
        print(f"❌ Still failing after dependency install: {e2}", file=sys.stderr)
        print("Make sure you're running this script from the google_ads directory", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description='Execute Google Ads Query Language (GAQL) queries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get campaign data in table format
  python run_query_v2.py --customer-id 1234567890 --query "SELECT campaign.name, campaign.status FROM campaign" --format table

  # Get keyword data in JSON format
  python run_query_v2.py --customer-id 1234567890 --query "SELECT ad_group_criterion.keyword.text FROM keyword_view" --format json

  # Save results to file
  python run_query_v2.py --customer-id 1234567890 --query "SELECT campaign.name FROM campaign" --format csv --output results.csv
        """
    )
    
    parser.add_argument('--customer-id', required=True, 
                       help='Google Ads customer ID (10 digits)')
    parser.add_argument('--query', required=True,
                       help='GAQL query to execute')
    parser.add_argument('--format', choices=['table', 'json', 'csv', 'raw'], 
                       default='table', help='Output format (default: table)')
    parser.add_argument('--output', help='Output file path (optional)')
    parser.add_argument('--config', help='Path to google-ads.yaml config file')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate the query without executing it')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    try:
        # Validate customer ID
        customer_id = validate_customer_id(args.customer_id)
        
        if args.verbose:
            print_section_header("Google Ads GAQL Query Runner v2")
            print(f"Customer ID: {customer_id}", file=sys.stderr)
            print(f"Query: {args.query}", file=sys.stderr)
            print(f"Format: {args.format}", file=sys.stderr)
            if args.output:
                print(f"Output file: {args.output}", file=sys.stderr)
        
        # Validate query if requested
        if args.validate_only:
            is_valid, error_msg = validate_gaql_query(args.query)
            if is_valid:
                print("✅ Query syntax is valid", file=sys.stderr)
                return 0
            else:
                print(f"❌ Query validation failed: {error_msg}", file=sys.stderr)
                return 1
        
        # Execute query
        if args.verbose:
            print("\n🔄 Executing query...", file=sys.stderr)
        
        result = run_gaql_query(
            customer_id=customer_id,
            query=args.query,
            output_format=args.format,
            config_path=args.config
        )
        
        # Handle output
        if args.output:
            # Write to file
            with open(args.output, 'w') as f:
                if isinstance(result, list):
                    # Raw format returns list
                    import json
                    json.dump(result, f, indent=2, default=str)
                else:
                    f.write(str(result))
            
            if args.verbose:
                print(f"✅ Results saved to {args.output}", file=sys.stderr)
            else:
                print(f"Results saved to {args.output}", file=sys.stderr)
        else:
            # Print to stdout
            if isinstance(result, list):
                # Raw format returns list
                import json
                print(json.dumps(result, indent=2, default=str))
            else:
                print(result)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

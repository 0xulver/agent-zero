#!/usr/bin/env python3
"""
Google Ads Keyword Simulator v2

This is the new modular version that uses absolute imports and proper
module structure to avoid ImportError issues.
"""

import sys
import os
import argparse
import json

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import from our modular structure
try:
    from keyword_tools import KeywordSimulator, KeywordResearcher, analyze_keyword_competition
    from utils import install_dependencies, validate_customer_id, print_section_header
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Installing dependencies and retrying...")
    
    # Fallback: install dependencies and try again
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-ads>=26.0.0", "PyYAML", "tabulate"])
    
    try:
        from keyword_tools import KeywordSimulator, KeywordResearcher, analyze_keyword_competition
        from utils import install_dependencies, validate_customer_id, print_section_header
    except ImportError as e2:
        print(f"❌ Still failing after dependency install: {e2}")
        print("Make sure you're running this script from the google_ads directory")
        sys.exit(1)


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description='Google Ads Keyword Simulation and Research Tool v2',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simulate keywords from a file
  python keyword_simulator.py --customer-id 1234567890 --action simulate --keywords-file keywords.json

  # Analyze existing keyword competition
  python keyword_simulator.py --customer-id 1234567890 --action competition --days 30

  # Analyze competition for new keywords
  python keyword_simulator.py --customer-id 1234567890 --action competition --keywords-file keywords.json

  # Find opportunity keywords
  python keyword_simulator.py --customer-id 1234567890 --action opportunities --keywords-file keywords.json
        """
    )
    
    parser.add_argument('--customer-id', required=True, 
                       help='Google Ads customer ID')
    parser.add_argument('--action', required=True, 
                       choices=['simulate', 'competition', 'opportunities', 'research'],
                       help='Type of analysis to perform')
    parser.add_argument('--keywords-file', 
                       help='JSON file containing list of keywords')
    parser.add_argument('--keywords', nargs='+',
                       help='List of keywords (alternative to --keywords-file)')
    parser.add_argument('--days', type=int, default=30, 
                       help='Number of days to analyze (default: 30)')
    parser.add_argument('--output', 
                       help='Output file path (optional)')
    parser.add_argument('--format', choices=['json', 'table'], default='table',
                       help='Output format (default: table)')
    parser.add_argument('--min-volume', type=int, default=100,
                       help='Minimum search volume for opportunities (default: 100)')
    parser.add_argument('--max-competition', type=int, default=70,
                       help='Maximum competition index for opportunities (default: 70)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    try:
        # Validate customer ID
        customer_id = validate_customer_id(args.customer_id)
        
        if args.verbose:
            print_section_header("Google Ads Keyword Simulator v2")
            print(f"Customer ID: {customer_id}")
            print(f"Action: {args.action}")
        
        # Get keywords list
        keywords = []
        if args.keywords_file:
            with open(args.keywords_file, 'r') as f:
                keywords_data = json.load(f)
                keywords = [kw.get('text', kw.get('keyword', '')) for kw in keywords_data if kw.get('text') or kw.get('keyword')]
        elif args.keywords:
            keywords = args.keywords
        
        # Execute the requested action
        if args.action == 'simulate':
            if not keywords:
                print("❌ No keywords provided. Use --keywords-file or --keywords")
                return 1
            
            simulator = KeywordSimulator(customer_id)
            results = simulator.simulate_keywords_from_list(keywords)
            
            if args.format == 'json':
                output = json.dumps(results, indent=2)
            else:
                output = _format_simulation_table(results)
        
        elif args.action == 'competition':
            # Support both new keywords and existing keyword analysis
            if keywords:
                # Analyze competition for provided keywords (new keywords)
                output = analyze_keyword_competition(customer_id, args.days, keywords)
            else:
                # Analyze existing keywords only
                output = analyze_keyword_competition(customer_id, args.days)
        
        elif args.action == 'opportunities':
            if not keywords:
                print("❌ No keywords provided. Use --keywords-file or --keywords")
                return 1
            
            simulator = KeywordSimulator(customer_id)
            opportunities = simulator.find_opportunity_keywords(
                keywords, args.min_volume, args.max_competition
            )
            
            if args.format == 'json':
                output = json.dumps(opportunities, indent=2)
            else:
                output = _format_opportunities_table(opportunities)
        
        elif args.action == 'research':
            if not keywords:
                print("❌ No keywords provided. Use --keywords-file or --keywords")
                return 1
            
            researcher = KeywordResearcher(customer_id)
            ideas = researcher.get_keyword_ideas(keywords)
            
            if args.format == 'json':
                output = json.dumps(ideas, indent=2)
            else:
                output = _format_research_table(ideas)
        
        # Handle output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✅ Results saved to {args.output}")
        else:
            print(output)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def _format_simulation_table(results):
    """Format simulation results as a table."""
    if not results:
        return "No simulation results found."
    
    lines = []
    lines.append("🎯 KEYWORD SIMULATION RESULTS")
    lines.append("=" * 80)
    
    # Sort by opportunity score if available, otherwise by search volume
    sorted_results = sorted(results, key=lambda x: x.get('search_volume', 0), reverse=True)
    
    for result in sorted_results[:20]:  # Show top 20
        lines.append(f"\n🔍 {result['keyword']}")
        lines.append(f"   Search Volume: {result['search_volume']:,}/month | Competition: {result['competition']}")
        lines.append(f"   Est. Monthly: {result['estimated_monthly_clicks']} clicks, ${result['estimated_monthly_cost']:.2f} cost")
        lines.append(f"   Est. Conversions: {result['estimated_monthly_conversions']:.1f} | CPC: ${result['avg_bid']:.2f}")
    
    return "\n".join(lines)


def _format_opportunities_table(opportunities):
    """Format opportunity results as a table."""
    if not opportunities:
        return "No opportunities found with the specified criteria."
    
    lines = []
    lines.append("💰 KEYWORD OPPORTUNITIES")
    lines.append("=" * 80)
    
    for i, opp in enumerate(opportunities[:15], 1):  # Show top 15
        lines.append(f"\n{i:2d}. {opp['keyword']}")
        lines.append(f"    Score: {opp['opportunity_score']:.1f} | Volume: {opp['search_volume']:,}/mo | Competition: {opp['competition']}")
        lines.append(f"    Est. Cost: ${opp['estimated_monthly_cost']:.2f}/mo | Conversions: {opp['estimated_monthly_conversions']:.1f}")
    
    return "\n".join(lines)


def _format_research_table(ideas):
    """Format research results as a table."""
    if not ideas:
        return "No keyword ideas found."
    
    lines = []
    lines.append("🔬 KEYWORD RESEARCH RESULTS")
    lines.append("=" * 80)
    
    # Sort by search volume
    sorted_ideas = sorted(ideas, key=lambda x: x['avg_monthly_searches'], reverse=True)
    
    for idea in sorted_ideas[:25]:  # Show top 25
        low_bid = idea['low_top_bid_micros'] / 1_000_000
        high_bid = idea['high_top_bid_micros'] / 1_000_000
        
        lines.append(f"\n🔍 {idea['keyword']}")
        lines.append(f"   Volume: {idea['avg_monthly_searches']:,}/month | Competition: {idea['competition']} ({idea['competition_index']}/100)")
        lines.append(f"   Bid Range: ${low_bid:.2f} - ${high_bid:.2f}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())

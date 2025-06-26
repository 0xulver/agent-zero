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

  # Research keywords from competitor URL
  python keyword_simulator.py --customer-id 1234567890 --action research --keywords-file competitor_url.json
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
        
        # Get keywords and URLs from input
        keywords = []
        urls = []
        if args.keywords_file:
            with open(args.keywords_file, 'r') as f:
                keywords_data = json.load(f)

                # Extract keywords
                keywords = [kw.get('text', kw.get('keyword', '')) for kw in keywords_data
                           if kw.get('text') or kw.get('keyword')]

                # Extract URLs
                urls = [kw.get('url', '') for kw in keywords_data if kw.get('url')]

        elif args.keywords:
            keywords = args.keywords
        
        # Execute the requested action
        if args.action == 'simulate':
            if not keywords and not urls:
                print("❌ No keywords or URLs provided. Use --keywords-file or --keywords")
                return 1

            simulator = KeywordSimulator(customer_id)

            # Get keywords from URLs if provided
            all_keywords = keywords.copy() if keywords else []
            if urls:
                researcher = KeywordResearcher(customer_id)
                for url in urls:
                    url_keywords = researcher.get_keyword_ideas_from_url(url, verbose=args.verbose)
                    all_keywords.extend([kw['keyword'] for kw in url_keywords])

            results = simulator.simulate_keywords_from_list(all_keywords)

            if args.format == 'json':
                output = json.dumps(results, indent=2)
            else:
                output = _format_simulation_table(results)
        
        elif args.action == 'competition':
            # Support keywords, URLs, and existing keyword analysis
            all_keywords = keywords.copy() if keywords else []

            # Get keywords from URLs if provided
            if urls:
                researcher = KeywordResearcher(customer_id)
                for url in urls:
                    url_keywords = researcher.get_keyword_ideas_from_url(url, verbose=args.verbose)
                    all_keywords.extend([kw['keyword'] for kw in url_keywords])

            if all_keywords:
                # Analyze competition for provided keywords/URLs (new keywords)
                output = analyze_keyword_competition(customer_id, args.days, all_keywords)
            else:
                # Analyze existing keywords only
                output = analyze_keyword_competition(customer_id, args.days)
        
        elif args.action == 'opportunities':
            if not keywords and not urls:
                print("❌ No keywords or URLs provided. Use --keywords-file or --keywords")
                return 1

            simulator = KeywordSimulator(customer_id)

            # Get keywords from URLs if provided
            all_keywords = keywords.copy() if keywords else []
            if urls:
                researcher = KeywordResearcher(customer_id)
                for url in urls:
                    url_keywords = researcher.get_keyword_ideas_from_url(url, verbose=args.verbose)
                    all_keywords.extend([kw['keyword'] for kw in url_keywords])

            opportunities = simulator.find_opportunity_keywords(
                all_keywords, args.min_volume, args.max_competition
            )

            if args.format == 'json':
                output = json.dumps(opportunities, indent=2)
            else:
                output = _format_opportunities_table(opportunities)
        
        elif args.action == 'research':
            if not keywords and not urls:
                print("❌ No keywords or URLs provided. Use --keywords-file or --keywords")
                return 1

            if args.verbose:
                print(f"🔬 Starting keyword research...")
                if keywords:
                    print(f"📝 Keywords provided: {len(keywords)} keywords")
                    print(f"   Keywords: {keywords}")
                if urls:
                    print(f"🌐 URLs provided: {len(urls)} URLs")
                    print(f"   URLs: {urls}")

            researcher = KeywordResearcher(customer_id)
            ideas = []

            try:
                if keywords and urls:
                    # Mixed input: both keywords and URLs
                    if args.verbose:
                        print(f"🔄 Processing mixed input (keywords + URLs)...")
                    ideas = researcher.get_keyword_ideas_mixed(keywords, urls, verbose=args.verbose)
                elif urls:
                    # URL-only input
                    if args.verbose:
                        print(f"🌐 Processing URL-only input...")
                    for i, url in enumerate(urls, 1):
                        if args.verbose:
                            print(f"🔍 Processing URL {i}/{len(urls)}: {url}")
                        try:
                            url_ideas = researcher.get_keyword_ideas_from_url(url, verbose=args.verbose)
                            if args.verbose:
                                print(f"✅ Successfully extracted {len(url_ideas)} keywords from {url}")
                            ideas.extend(url_ideas)
                        except Exception as url_error:
                            print(f"❌ Failed to process URL {url}: {url_error}")
                            if args.verbose:
                                import traceback
                                traceback.print_exc()
                            # Continue with other URLs
                            continue
                else:
                    # Keyword-only input (original functionality)
                    if args.verbose:
                        print(f"🎯 Processing keyword-only input...")
                    ideas = researcher.get_keyword_ideas(keywords)

                if args.verbose:
                    print(f"📊 Total keyword ideas collected: {len(ideas)}")

                if len(ideas) == 0:
                    print("⚠️  No keyword ideas were found.")
                    if args.verbose:
                        print("💡 This could be due to:")
                        print("   - URLs that are not accessible or have insufficient content")
                        print("   - Keywords that don't generate related ideas")
                        print("   - API limitations or account restrictions")
                    output = "No keyword ideas found."
                else:
                    if args.format == 'json':
                        output = json.dumps(ideas, indent=2)
                    else:
                        output = _format_research_table(ideas)

            except Exception as research_error:
                print(f"❌ Research failed with error: {research_error}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
                return 1
        
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

    # Group by source type if available
    url_ideas = [idea for idea in ideas if idea.get('source_url') or idea.get('source_type') == 'url']
    keyword_ideas = [idea for idea in ideas if idea.get('source_type') == 'keyword' or (not idea.get('source_url') and not idea.get('source_type'))]

    # Show URL-sourced keywords first
    if url_ideas:
        lines.append("\n🌐 KEYWORDS FROM COMPETITOR URLs:")
        lines.append("-" * 50)

        # Group by source URL
        url_groups = {}
        for idea in url_ideas:
            url = idea.get('source_url', 'Unknown URL')
            if url not in url_groups:
                url_groups[url] = []
            url_groups[url].append(idea)

        for url, url_keywords in url_groups.items():
            lines.append(f"\n📍 Source: {url}")
            sorted_url_keywords = sorted(url_keywords, key=lambda x: x['avg_monthly_searches'], reverse=True)

            for idea in sorted_url_keywords[:15]:  # Show top 15 per URL
                low_bid = idea['low_top_bid_micros'] / 1_000_000
                high_bid = idea['high_top_bid_micros'] / 1_000_000

                lines.append(f"   🔍 {idea['keyword']}")
                lines.append(f"      Volume: {idea['avg_monthly_searches']:,}/month | Competition: {idea['competition']} ({idea['competition_index']}/100)")
                lines.append(f"      Bid Range: ${low_bid:.2f} - ${high_bid:.2f}")

    # Show keyword-sourced ideas
    if keyword_ideas:
        if url_ideas:
            lines.append("\n" + "=" * 80)
        lines.append("\n🎯 KEYWORDS FROM SEED KEYWORDS:")
        lines.append("-" * 50)

        sorted_keyword_ideas = sorted(keyword_ideas, key=lambda x: x['avg_monthly_searches'], reverse=True)

        for idea in sorted_keyword_ideas[:25]:  # Show top 25
            low_bid = idea['low_top_bid_micros'] / 1_000_000
            high_bid = idea['high_top_bid_micros'] / 1_000_000

            lines.append(f"\n🔍 {idea['keyword']}")
            lines.append(f"   Volume: {idea['avg_monthly_searches']:,}/month | Competition: {idea['competition']} ({idea['competition_index']}/100)")
            lines.append(f"   Bid Range: ${low_bid:.2f} - ${high_bid:.2f}")

    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Campaign Optimization Script
Analyzes campaign performance and provides optimization recommendations
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from core.google_ads_client import GoogleAdsClient
from core.data_formatter import DataFormatter

def analyze_campaign_performance(results, target_roas=None, target_ctr=None):
    """Analyze campaign performance and generate recommendations"""
    if not results:
        return {"recommendations": ["No campaign data available for analysis"]}
    
    recommendations = []
    total_cost = 0
    total_conversions = 0
    total_clicks = 0
    total_impressions = 0
    
    # Calculate totals
    for result in results:
        metrics = result.get("metrics", {})
        total_cost += int(metrics.get("costMicros", 0))
        total_conversions += float(metrics.get("conversions", 0))
        total_clicks += int(metrics.get("clicks", 0))
        total_impressions += int(metrics.get("impressions", 0))
    
    # Calculate key metrics
    current_roas = (total_conversions * 1000000 / total_cost) if total_cost > 0 else 0
    current_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
    
    # ROAS Analysis
    if target_roas:
        if current_roas < target_roas:
            recommendations.append(f"🎯 ROAS below target ({current_roas:.2f} vs {target_roas:.2f})")
            recommendations.append("   - Consider pausing low-performing campaigns")
            recommendations.append("   - Increase bids on high-converting keywords")
            recommendations.append("   - Review and improve ad copy")
        else:
            recommendations.append(f"✅ ROAS above target ({current_roas:.2f} vs {target_roas:.2f})")
            recommendations.append("   - Consider increasing budget for top performers")
    
    # CTR Analysis
    if target_ctr:
        if current_ctr < target_ctr:
            recommendations.append(f"📈 CTR below target ({current_ctr:.2f}% vs {target_ctr:.2f}%)")
            recommendations.append("   - Improve ad headlines and descriptions")
            recommendations.append("   - Add more relevant keywords")
            recommendations.append("   - Use ad extensions")
    
    # General recommendations based on performance
    if current_ctr < 2.0:
        recommendations.append("📝 Low CTR detected - improve ad relevance")
    
    if conversion_rate < 2.0:
        recommendations.append("🔄 Low conversion rate - optimize landing pages")
    
    # Campaign-specific recommendations
    low_performers = []
    high_performers = []
    
    for result in results:
        campaign = result.get("campaign", {})
        metrics = result.get("metrics", {})
        
        cost = int(metrics.get("costMicros", 0))
        conversions = float(metrics.get("conversions", 0))
        clicks = int(metrics.get("clicks", 0))
        
        if cost > 0:
            campaign_roas = (conversions * 1000000 / cost) if cost > 0 else 0
            campaign_ctr = (clicks / int(metrics.get("impressions", 1)) * 100)
            
            if target_roas and campaign_roas < target_roas * 0.5:
                low_performers.append(campaign.get("name", "Unknown"))
            elif campaign_roas > (target_roas or 3.0):
                high_performers.append(campaign.get("name", "Unknown"))
    
    if low_performers:
        recommendations.append(f"⚠️  Consider pausing low performers: {', '.join(low_performers[:3])}")
    
    if high_performers:
        recommendations.append(f"🚀 Scale up high performers: {', '.join(high_performers[:3])}")
    
    return {
        "current_metrics": {
            "roas": current_roas,
            "ctr": current_ctr,
            "conversion_rate": conversion_rate,
            "total_cost_micros": total_cost,
            "total_conversions": total_conversions
        },
        "recommendations": recommendations,
        "low_performers": low_performers,
        "high_performers": high_performers
    }

def save_results(data, output_dir, filename_prefix):
    """Save results to files"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON
    json_file = output_dir / f"{filename_prefix}_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    return json_file

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Optimize Google Ads campaigns')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID')
    parser.add_argument('--target-roas', type=float, help='Target ROAS for optimization')
    parser.add_argument('--target-ctr', type=float, help='Target CTR percentage')
    parser.add_argument('--days', type=int, default=30, 
                       help='Number of days to analyze (default: 30)')
    
    args = parser.parse_args()
    
    # Load environment variables
    config_dir = Path(__file__).parent.parent / "config"
    env_file = config_dir / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
    
    print("🔧 Google Ads Campaign Optimization Analysis")
    print("=" * 50)
    print(f"Customer ID: {args.customer_id}")
    print(f"Analysis Period: {args.days} days")
    if args.target_roas:
        print(f"Target ROAS: {args.target_roas}")
    if args.target_ctr:
        print(f"Target CTR: {args.target_ctr}%")
    print()
    
    try:
        # Initialize client
        client = GoogleAdsClient()
        
        # Get account currency
        print("💰 Getting account currency...")
        currency_result = client.get_account_currency(args.customer_id)
        currency_code = "USD"  # default
        
        if currency_result["success"]:
            currency_code = currency_result["currency_code"]
            print(f"   Currency: {currency_code}")
        
        # Get campaign performance data
        print("📊 Analyzing campaign performance...")
        performance_result = client.get_campaign_performance(args.customer_id, args.days)
        
        if not performance_result["success"]:
            print(f"❌ Error getting performance data: {performance_result['error']}")
            sys.exit(1)
        
        # Analyze performance
        print("🔍 Generating optimization recommendations...")
        analysis = analyze_campaign_performance(
            performance_result["results"],
            target_roas=args.target_roas,
            target_ctr=args.target_ctr
        )
        
        # Display current metrics
        metrics = analysis["current_metrics"]
        print("\n📈 Current Performance Metrics:")
        print(f"   ROAS: {metrics['roas']:.2f}")
        print(f"   CTR: {metrics['ctr']:.2f}%")
        print(f"   Conversion Rate: {metrics['conversion_rate']:.2f}%")
        print(f"   Total Cost: {DataFormatter.format_currency(metrics['total_cost_micros'], currency_code)}")
        print(f"   Total Conversions: {metrics['total_conversions']:.2f}")
        
        # Display recommendations
        print("\n💡 Optimization Recommendations:")
        for i, rec in enumerate(analysis["recommendations"], 1):
            print(f"   {i}. {rec}")
        
        # Display campaign insights
        if analysis["high_performers"]:
            print(f"\n🚀 Top Performing Campaigns:")
            for campaign in analysis["high_performers"][:5]:
                print(f"   ✅ {campaign}")
        
        if analysis["low_performers"]:
            print(f"\n⚠️  Underperforming Campaigns:")
            for campaign in analysis["low_performers"][:5]:
                print(f"   ❌ {campaign}")
        
        # Create comprehensive report
        optimization_report = {
            "customer_id": args.customer_id,
            "analysis_period_days": args.days,
            "target_roas": args.target_roas,
            "target_ctr": args.target_ctr,
            "currency_code": currency_code,
            "current_metrics": metrics,
            "recommendations": analysis["recommendations"],
            "high_performers": analysis["high_performers"],
            "low_performers": analysis["low_performers"],
            "raw_performance_data": performance_result,
            "generated_at": datetime.now().isoformat()
        }
        
        # Save results
        output_dir = Path("/work_dir/google_ads_results")
        filename_prefix = f"optimization_analysis_{args.customer_id}_{args.days}days"
        json_file = save_results(optimization_report, output_dir, filename_prefix)
        
        print(f"\n💾 Optimization report saved: {json_file}")
        
        # Summary
        print(f"\n📋 Summary:")
        print(f"   Campaigns analyzed: {len(performance_result['results'])}")
        print(f"   Recommendations generated: {len(analysis['recommendations'])}")
        print(f"   High performers: {len(analysis['high_performers'])}")
        print(f"   Low performers: {len(analysis['low_performers'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

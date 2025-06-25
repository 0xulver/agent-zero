"""
Google Ads Automation Toolkit

A comprehensive toolkit for Google Ads campaign management, keyword research,
and performance analysis.

This package provides:
- Campaign creation and management
- Keyword research and analysis
- Performance monitoring and optimization
- GAQL query execution
- Automated bid management
"""

__version__ = "1.0.0"
__author__ = "Agent 0"
__description__ = "Google Ads Automation Toolkit"

# Import main classes and functions for easy access
# Use try/except to handle missing dependencies gracefully
try:
    from .utils import get_google_ads_client as GoogleAdsClient, load_config, install_dependencies
    from .query_runner import run_gaql_query
    from .keyword_tools import KeywordResearcher, KeywordSimulator
    from .campaign_tools import CampaignManager, CampaignOperations

    __all__ = [
        'GoogleAdsClient',
        'load_config',
        'install_dependencies',
        'run_gaql_query',
        'KeywordResearcher',
        'KeywordSimulator',
        'CampaignManager',
        'CampaignOperations'
    ]

except ImportError as e:
    # If imports fail, provide a helpful error message
    import sys
    print(f"⚠️  Google Ads toolkit import error: {e}")
    print("Run 'python -m pip install google-ads PyYAML tabulate' to install dependencies")

    # Provide stub functions to prevent complete failure
    def install_dependencies():
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-ads>=26.0.0", "PyYAML", "tabulate"])
        return True

    __all__ = ['install_dependencies']

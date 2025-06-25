"""
Shared utilities for Google Ads toolkit.

This module provides common functionality used across all Google Ads scripts:
- Configuration loading
- Dependency management  
- Google Ads client initialization
- Common helper functions
"""

import sys
import subprocess
import os
import yaml
from typing import Optional, Dict, Any


def install_dependencies():
    """Install required dependencies if not already installed."""
    required_packages = [
        'PyYAML',
        'google-ads>=26.0.0',
        'tabulate'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package.startswith('google-ads'):
                import google.ads.googleads
            elif package == 'PyYAML':
                import yaml
            elif package == 'tabulate':
                import tabulate
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 Installing missing dependencies: {', '.join(missing_packages)}", file=sys.stderr)
        for package in missing_packages:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ Installed {package}", file=sys.stderr)
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}", file=sys.stderr)
                return False
        print("✅ All dependencies installed successfully", file=sys.stderr)
    
    return True


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load Google Ads configuration from YAML file."""
    if config_path is None:
        # Look for config in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "google-ads.yaml")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML configuration: {e}")


def get_google_ads_client(config_path: Optional[str] = None):
    """Initialize and return a Google Ads client."""
    # Ensure dependencies are installed
    if not install_dependencies():
        raise RuntimeError("Failed to install required dependencies")
    
    try:
        from google.ads.googleads.client import GoogleAdsClient
        
        if config_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, "google-ads.yaml")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Google Ads configuration file not found: {config_path}")
        
        client = GoogleAdsClient.load_from_storage(config_path)
        return client
        
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Google Ads client: {e}")


def format_currency(amount_micros: int) -> str:
    """Convert micros to formatted currency string."""
    return f"${amount_micros / 1_000_000:.2f}"


def format_percentage(value: float) -> str:
    """Format a decimal as a percentage."""
    return f"{value * 100:.2f}%"


def format_number(value: int) -> str:
    """Format a number with thousands separators."""
    return f"{value:,}"


def validate_customer_id(customer_id: str) -> str:
    """Validate and format customer ID."""
    # Remove any dashes or spaces
    clean_id = customer_id.replace('-', '').replace(' ', '')
    
    # Ensure it's numeric and the right length
    if not clean_id.isdigit():
        raise ValueError(f"Customer ID must be numeric: {customer_id}")
    
    if len(clean_id) != 10:
        raise ValueError(f"Customer ID must be 10 digits: {customer_id}")
    
    return clean_id


def get_date_range(days: int) -> tuple:
    """Get start and end dates for a given number of days back."""
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def print_section_header(title: str, width: int = 60):
    """Print a formatted section header."""
    print(f"\n{'=' * width}")
    print(f"{title:^{width}}")
    print(f"{'=' * width}")


def print_subsection_header(title: str, width: int = 60):
    """Print a formatted subsection header."""
    print(f"\n{'-' * width}")
    print(f"{title}")
    print(f"{'-' * width}")


# Alias for backward compatibility
GoogleAdsClient = get_google_ads_client

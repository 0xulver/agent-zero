#!/usr/bin/env python3
"""
Test Installation Script
Verifies that the Google Ads instrument is properly installed and configured
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test Google API imports
        import google.auth
        import google_auth_oauthlib.flow
        import requests
        print("   ✅ Google API libraries")
        
        # Test dotenv
        import dotenv
        print("   ✅ python-dotenv")
        
        # Test our modules
        from auth.credentials_manager import CredentialsManager
        from core.google_ads_client import GoogleAdsClient
        from core.data_formatter import DataFormatter
        from tools.campaign_manager import CampaignManager
        print("   ✅ Google Ads instrument modules")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔧 Testing environment configuration...")
    
    config_dir = Path(__file__).parent.parent / "config"
    env_file = config_dir / ".env"
    env_example = config_dir / ".env.example"
    
    # Check if files exist
    if not env_example.exists():
        print("   ❌ .env.example file missing")
        return False
    print("   ✅ .env.example file exists")
    
    if not env_file.exists():
        print("   ⚠️  .env file not found (run setup_auth.py to create)")
        return False
    print("   ✅ .env file exists")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    # Check required variables
    required_vars = [
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_DEVELOPER_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value or value.startswith("your_"):
            missing_vars.append(var)
        else:
            print(f"   ✅ {var} configured")
    
    if missing_vars:
        print(f"   ⚠️  Missing variables: {', '.join(missing_vars)}")
        return False
    
    return True

def test_directory_structure():
    """Test that all required directories and files exist"""
    print("\n📁 Testing directory structure...")
    
    base_dir = Path(__file__).parent.parent
    
    required_paths = [
        "auth/__init__.py",
        "auth/credentials_manager.py",
        "core/__init__.py", 
        "core/google_ads_client.py",
        "core/data_formatter.py",
        "tools/__init__.py",
        "tools/campaign_manager.py",
        "scripts/setup_auth.py",
        "scripts/list_accounts.py",
        "scripts/get_performance.py",
        "scripts/run_query.py",
        "scripts/create_campaign.py",
        "scripts/optimize.py",
        "config/.env.example",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    for path in required_paths:
        full_path = base_dir / path
        if full_path.exists():
            print(f"   ✅ {path}")
        else:
            print(f"   ❌ {path}")
            missing_files.append(path)
    
    return len(missing_files) == 0

def test_script_permissions():
    """Test that scripts are executable"""
    print("\n🔐 Testing script permissions...")
    
    scripts_dir = Path(__file__).parent
    script_files = [
        "setup_auth.py",
        "list_accounts.py", 
        "get_performance.py",
        "run_query.py",
        "create_campaign.py",
        "optimize.py",
        "test_installation.py"
    ]
    
    all_executable = True
    for script in script_files:
        script_path = scripts_dir / script
        if script_path.exists():
            if os.access(script_path, os.X_OK):
                print(f"   ✅ {script} (executable)")
            else:
                print(f"   ⚠️  {script} (not executable)")
                all_executable = False
        else:
            print(f"   ❌ {script} (missing)")
            all_executable = False
    
    if not all_executable:
        print("\n   💡 To fix permissions, run:")
        print("      chmod +x instruments/custom/google_ads/scripts/*.py")
    
    return all_executable

def test_output_directory():
    """Test that output directory can be created"""
    print("\n📂 Testing output directory...")
    
    output_dir = Path("/work_dir/google_ads_results")
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Test write permissions
        test_file = output_dir / "test_write.txt"
        test_file.write_text("test")
        test_file.unlink()
        
        print(f"   ✅ Output directory accessible: {output_dir}")
        return True
        
    except Exception as e:
        print(f"   ❌ Cannot access output directory: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Google Ads Instrument Installation Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Directory Structure", test_directory_structure),
        ("Script Permissions", test_script_permissions),
        ("Output Directory", test_output_directory),
        ("Environment", test_environment)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Installation test completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Run setup_auth.py to configure authentication")
        print("   2. Run list_accounts.py to test API access")
        print("   3. Start using the Google Ads instrument!")
    else:
        print("\n⚠️  Some tests failed. Please review the issues above.")
        print("\n📚 Common fixes:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Set script permissions: chmod +x scripts/*.py")
        print("   - Configure environment: edit config/.env")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

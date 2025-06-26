#!/usr/bin/env python3
"""
Debug script to test URL parsing in keyword_simulator.py
"""

import json
import sys
import os

def test_url_parsing():
    """Test that URL parsing works correctly."""
    print("🧪 Testing URL Parsing Logic")
    print("=" * 30)
    
    # Test data
    test_data = [
        {
            "url": "https://www.powerfulexecutivevoice.com/"
        }
    ]
    
    print(f"📝 Test data: {json.dumps(test_data, indent=2)}")
    
    # Simulate the parsing logic from keyword_simulator.py
    keywords = []
    urls = []
    
    keywords_data = test_data
    
    # Extract keywords
    keywords = [kw.get('text', kw.get('keyword', '')) for kw in keywords_data 
               if kw.get('text') or kw.get('keyword')]
    
    # Extract URLs
    urls = [kw.get('url', '') for kw in keywords_data if kw.get('url')]
    
    print(f"\n📊 Parsing results:")
    print(f"   Keywords found: {len(keywords)}")
    print(f"   Keywords: {keywords}")
    print(f"   URLs found: {len(urls)}")
    print(f"   URLs: {urls}")
    
    # Test the condition logic
    if not keywords and not urls:
        print("❌ Would trigger 'No keywords or URLs provided' error")
        return False
    elif keywords and urls:
        print("✅ Would trigger mixed input processing")
    elif urls:
        print("✅ Would trigger URL-only processing")
    else:
        print("✅ Would trigger keyword-only processing")
    
    return True

def create_test_file():
    """Create a test file for debugging."""
    test_file = "/tmp/debug_competitor_url.json"
    test_data = [
        {
            "url": "https://www.powerfulexecutivevoice.com/"
        }
    ]
    
    with open(test_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"📁 Created test file: {test_file}")
    print(f"📄 Content: {json.dumps(test_data, indent=2)}")
    
    return test_file

if __name__ == "__main__":
    print("🔍 Debug URL Parsing")
    print("=" * 20)
    
    success = test_url_parsing()
    test_file = create_test_file()
    
    print(f"\n🧪 Manual test command:")
    print(f"python keyword_simulator.py --customer-id '3045806466' --action research --keywords-file {test_file} --verbose")
    
    if success:
        print("\n✅ URL parsing logic appears correct")
    else:
        print("\n❌ URL parsing logic has issues")

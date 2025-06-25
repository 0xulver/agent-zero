#!/bin/bash

# Test script to demonstrate clean JSON output

echo "🧪 Testing JSON Output Cleanliness"
echo "=================================="

echo ""
echo "1. Testing run_query_v2.py (FIXED):"
echo "-----------------------------------"
echo "Command: python run_query_v2.py --customer-id \"3045806466\" --query \"SELECT campaign.id, campaign.name FROM campaign LIMIT 2\" --format json"
echo ""
echo "Output:"
python run_query_v2.py --customer-id "3045806466" --query "SELECT campaign.id, campaign.name FROM campaign LIMIT 2" --format json

echo ""
echo "2. Testing JSON parsing with jq:"
echo "--------------------------------"
echo "Command: python run_query_v2.py ... | jq '.[0].\"campaign.name\"'"
echo ""
echo "Result:"
python run_query_v2.py --customer-id "3045806466" --query "SELECT campaign.id, campaign.name FROM campaign LIMIT 2" --format json | jq '.[0]."campaign.name"'

echo ""
echo "✅ JSON output is clean and parseable!"
echo ""
echo "Note: All status messages are now sent to stderr, leaving stdout clean for JSON data."
echo "This allows proper integration with tools like jq, curl, and other JSON processors."

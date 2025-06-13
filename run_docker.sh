#!/bin/bash

# Agent Zero Docker Runner
# This script runs Agent Zero in Docker with volume mounting for development

echo "Starting Agent Zero in Docker..."
echo "Access at: http://localhost:50001"
echo "Press Ctrl+C to stop"
echo ""

docker run -p 50001:80 \
  -v $(pwd):/a0 \
  -v $(pwd)/work_dir:/root \
  frdel/agent-zero-run

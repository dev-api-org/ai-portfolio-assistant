#!/bin/bash
# Log deployment information

echo "================================================"
echo "Deployment Info"
echo "================================================"
echo "Python version:"
python3 --version
echo ""
echo "Environment variables:"
env | grep -E "GOOGLE_API_KEY|PYTHONPATH|PORT" || echo "No matching env vars"
echo ""
echo "Current directory:"
pwd
echo ""
echo "Files in deployment:"
ls -la
echo "================================================"

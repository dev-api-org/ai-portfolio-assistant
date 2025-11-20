#!/bin/bash
# Check if Streamlit is running

sleep 5

if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ Streamlit is running on port 8501"
    exit 0
else
    echo "❌ Streamlit is NOT running on port 8501"
    echo "Checking logs..."
    tail -n 50 /var/log/web.stdout.log
    exit 1
fi

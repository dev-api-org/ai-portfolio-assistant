#!/usr/bin/env python3
"""
Simple health check script to verify the app can start.
Run this to see if there are any import or startup errors.
"""
import sys
import os

print("=" * 50)
print("Health Check Starting...")
print("=" * 50)

# Check Python version
print(f"Python version: {sys.version}")

# Check environment variables
print(f"\nGOOGLE_API_KEY set: {bool(os.getenv('GOOGLE_API_KEY'))}")
print(f"PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")

# Check if we can import key modules
print("\n--- Testing Imports ---")
try:
    import streamlit
    print("✅ streamlit imported successfully")
except Exception as e:
    print(f"❌ streamlit import failed: {e}")
    sys.exit(1)

try:
    import langchain
    print("✅ langchain imported successfully")
except Exception as e:
    print(f"❌ langchain import failed: {e}")
    sys.exit(1)

try:
    import langchain_google_genai
    print("✅ langchain_google_genai imported successfully")
except Exception as e:
    print(f"❌ langchain_google_genai import failed: {e}")
    sys.exit(1)

# Try to import the app
print("\n--- Testing App Import ---")
try:
    sys.path.insert(0, os.path.dirname(__file__))
    import app
    print("✅ app.py imported successfully")
except Exception as e:
    print(f"❌ app.py import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("✅ Health Check PASSED - App should start!")
print("=" * 50)

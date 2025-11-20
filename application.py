#!/usr/bin/env python3
"""
AWS Elastic Beanstalk entry point for the Streamlit application.
This file is required by EB to properly start the application.
"""

import os
import sys
import pathlib

# Add project root to Python path
ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the Streamlit app - this is the same as app.py
import frontend.streamlit_chat_canvas  # noqa: F401

# For WSGI compatibility (though Streamlit runs via Procfile)
application = None

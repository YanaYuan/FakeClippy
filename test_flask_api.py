#!/usr/bin/env python3
"""
Test script for the Flask version of the API
"""

import sys
import os

# Add the api directory to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from api.index import app

if __name__ == '__main__':
    print("Testing Flask API locally...")
    print("Starting Flask development server on http://localhost:5001")
    print("Available endpoints:")
    print("  - GET  /api        - API info")
    print("  - POST /api/chat   - Chat endpoint")
    print("  - Press Ctrl+C to stop")
    
    app.run(debug=True, host='localhost', port=5001)

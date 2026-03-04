#!/usr/bin/env python
"""Test the database directly in Flask context."""
import time
import sys
sys.path.insert(0, '.')

time.sleep(2)

from app import app
from utils.resume_db import get_analysis_by_id

# Use Flask app context
with app.app_context():
    results = get_analysis_by_id(112)
    if results:
        print(f"✓ Results retrieved: analysis_id={results.get('analysis_id')}")
        print(f"  Keys: {list(results.keys())}")
    else:
        print("✗ get_analysis_by_id returned None")

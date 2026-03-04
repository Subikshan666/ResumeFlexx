#!/usr/bin/env python
"""Test if Flask is running and responsive."""
import requests
import time

time.sleep(2)

try:
    # Test a simple endpoint
    r = requests.get('http://localhost:5000/dashboard')
    print(f"Dashboard endpoint: {r.status_code}")
    if r.status_code != 200:
        print(f"ERROR: Expected 200, got {r.status_code}")
        print(f"Response: {r.text[:200]}")
    else:
        print("✓ Flask app is responsive")
except Exception as e:
    print(f"✗ Cannot connect to Flask: {e}")

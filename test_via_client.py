#!/usr/bin/env python
"""Test the download endpoint using Flask test client."""
import sys
sys.path.insert(0, '.')

from app import app

# Use Flask's test client
with app.test_client() as client:
    response = client.get('/download-report/112')
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.content_type}")
    print(f"Content-Length: {len(response.data)}")
    
    if response.status_code == 200:
        print(f"✓SUCCESS! Got PDF of {len(response.data)} bytes")
    elif response.status_code == 302:
        print(f"✗ Got 302 redirect to: {response.location}")
    else:
        print(f"Response data (first 200 chars): {response.data[:200]}")

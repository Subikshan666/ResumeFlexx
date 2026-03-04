#!/usr/bin/env python
"""Test the download endpoint and capture response details."""
import time
import requests
import sys

time.sleep(2)

try:
    # Test download with ID 112
    url = 'http://localhost:5000/download-report/112'
    print(f"Testing: {url}")
    
    r = requests.get(url, allow_redirects=False, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    print(f"Content-Length: {r.headers.get('Content-Length')}")
    
    if r.status_code == 200:
        print(f"✓ SUCCESS! Got PDF of {len(r.content)} bytes")
        # Save it
        with open('downloaded_report.pdf', 'wb') as f:
            f.write(r.content)
        print("Saved to downloaded_report.pdf")
    elif r.status_code == 302:
        print(f"✗ Got redirect to: {r.headers.get('Location')}")
        print(f"This means the download endpoint returned a redirect instead of the PDF")
    else:
        print(f"✗ Unexpected status: {r.status_code}")
        print(f"Response: {r.text[:500]}")
        
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to Flask app. Is it running?")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

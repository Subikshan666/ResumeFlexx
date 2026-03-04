#!/usr/bin/env python
"""Test HTTP download with different approaches."""
import time
import requests
import sys

time.sleep(2)

try:
    print("Test 1: With redirects=False (current approach)")
    r = requests.get('http://localhost:5000/download-report/112', allow_redirects=False, timeout=10)
    print(f"  Status: {r.status_code}, Content-Type: {r.headers.get('Content-Type')}")
    if r.status_code == 302:
        print(f"  Redirects to: {r.headers.get('Location')}")
    
    print("\nTest 2: With allow_redirects=True")
    r = requests.get('http://localhost:5000/download-report/112', allow_redirects=True, timeout=10)
    print(f"  Status: {r.status_code}, Content-Type: {r.headers.get('Content-Type')}")
    print(f"  Content Length: {len(r.content)}")
    if r.status_code == 200 and r.headers.get('Content-Type') == 'application/pdf':
        print("  ✓ Got PDF file!")
        # Save it
        with open('test_download.pdf', 'wb') as f:
            f.write(r.content)
        print("  Saved to test_download.pdf")
    else:
        print(f"  Response preview: {r.text[:200]}")
    
    print("\nTest 3: Check response history")
    r = requests.get('http://localhost:5000/download-report/112', timeout=10)
    print(f"  Final status: {r.status_code}")
    if r.history:
        for resp in r.history:
            print(f"    Redirect: {resp.status_code} -> {resp.headers.get('Location', 'N/A')}")
    
except Exception as e:
    print(f"✗ Error: {e}")

#!/usr/bin/env python
"""Test the download endpoint with the correct ID."""
import time
import requests
import sys

time.sleep(2)

try:
    # Get the correct ID from database first
    import sqlite3
    conn = sqlite3.connect('resume_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM history ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    if row:
        analysis_id = row[0]
        print(f"Testing with ID: {analysis_id}")
        conn.close()
        
        url = f'http://localhost:5000/download-report/{analysis_id}'
        print(f"URL: {url}")
        
        # Test with allow_redirects=False
        r = requests.get(url, allow_redirects=False, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type')}")
        
        if r.status_code == 200:
            print(f"✓ SUCCESS! Got PDF of {len(r.content)} bytes")
            # Save it
            with open('browser_test_download.pdf', 'wb') as f:
                f.write(r.content)
            print("✓ Saved to browser_test_download.pdf")
        elif r.status_code == 302:
            print(f"✗ Got redirect to: {r.headers.get('Location')}")
            print("  This is the problem - endpoint returns redirect instead of PDF")
        else:
            print(f"✗ Unexpected status: {r.status_code}")
    else:
        print("✗ No analysis records found")
        conn.close()
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python
"""Test the PDF download endpoint."""
import time
import requests
import traceback

time.sleep(2)

try:
    # Test if app is running
    r = requests.get('http://localhost:5000/')
    print(f'✓ App running: Status {r.status_code}')
    
    # Try to download a report that doesn't exist  
    r = requests.get('http://localhost:5000/download-report/999', allow_redirects=False)
    print(f'Download endpoint (non-existent ID): Status {r.status_code}')
    print(f'  Content-Type: {r.headers.get("Content-Type")}')
    if r.status_code != 200:
        print(f'  Response: {r.text[:300]}')
    
    # Check if there's a real analysis in the database
    print("\nChecking database...")
    import sqlite3
    conn = sqlite3.connect('resume_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, filename, score FROM history LIMIT 5')
    rows = cursor.fetchall()
    if rows:
        print(f"✓ Found {len(rows)} analysis record(s)")
        for row_id, filename, score in rows:
            print(f"  ID: {row_id}, File: {filename}, Score: {score}")
            
            # Try to download this one
            r = requests.get(f'http://localhost:5000/download-report/{row_id}', allow_redirects=False)
            print(f'  ✓ Download attempt for ID {row_id}: Status {r.status_code}')
            print(f'    Content-Type: {r.headers.get("Content-Type")}')
            if r.status_code == 200:
                print(f'    PDF Size: {len(r.content)} bytes')
            else:
                print(f'    Response: {r.text[:200]}')
    else:
        print("✗ No analysis records found in database")
        print("  You need to analyze a resume first to test PDF download")
    
    conn.close()
    
except Exception as e:
    print(f'✗ Error: {e}')
    traceback.print_exc()

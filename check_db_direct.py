#!/usr/bin/env python
"""Check the database for analysis records."""
import sqlite3

conn = sqlite3.connect('resume_history.db')
cursor = conn.cursor()

# Check what's in the database
cursor.execute('SELECT id, filename, score FROM history')
rows = cursor.fetchall()

print(f"Analysis records in database: {len(rows)}")
for row_id, filename, score in rows:
    print(f"  ID: {row_id}, Filename: {filename}, Score: {score}")

# Try querying for ID 112 specifically
cursor.execute('SELECT * FROM history WHERE id = 112')
row = cursor.fetchone()
if row:
    print(f"\nRecord 112 exists: {row[:3]}")
else:
    print("\nRecord 112 NOT FOUND")

conn.close()

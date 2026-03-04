#!/usr/bin/env python
"""List all registered Flask routes."""
import sys
sys.path.insert(0, '.')

from app import app

print("Registered Flask routes:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")

# Filter for download
print("\nRoutes matching 'download':")
for rule in app.url_map.iter_rules():
    if 'download' in rule.rule.lower():
        print(f"  {rule.rule} -> {rule.endpoint}")

#!/usr/bin/env python
"""Debug the PDF generation function directly."""
import sys
sys.path.insert(0, '.')

import sqlite3
import json
from utils.resume_db import get_analysis_by_id
from app import generate_pdf_report

# Get the first analysis from database
try:
    results = get_analysis_by_id(113)
    print(f"Results from DB: {results is not None}")
    
    if results:
        print(f"Results keys: {list(results.keys())}")
        print(f"Score: {results.get('score')}")
        print(f"Has missing_skills: {'missing_skills' in results}")
        print(f"Has action_checklist: {'action_checklist' in results}")
        
        # Try to generate PDF
        try:
            pdf_bytes = generate_pdf_report(results)
            print(f"✓ PDF generated successfully! Size: {len(pdf_bytes)} bytes")
        except Exception as e:
            print(f"✗ PDF generation failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("✗ Results is None")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

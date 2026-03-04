#!/usr/bin/env python
"""Test PDF generation with sample data."""
import sys
sys.path.insert(0, '.')

from app import generate_pdf_report

# Sample results data
sample_results = {
    'score': 75.5,
    'ats_score': 82.0,
    'health_score': 88.5,
    'missing_skills': ['Python', 'Docker', 'Kubernetes', 'CI/CD', 'AWS'],
    'health_issues': ['Missing LinkedIn URL', 'Formatting inconsistency', 'Low keyword density'],
    'jd_top_keywords': ['Python', 'AWS', 'Docker', 'React', 'Node.js', 'SQL', 'Git', 'Agile'],
    'action_checklist': {
        'skills': ['Add Python experience', 'Highlight AWS projects'],
        'formatting': ['Fix bullet point alignment'],
        'keywords': ['Increase keyword density']
    },
    'filename': 'resume.pdf'
}

try:
    print("Generating PDF...")
    pdf_bytes = generate_pdf_report(sample_results)
    print(f"PDF generated successfully! Size: {len(pdf_bytes)} bytes")
    
    # Save to file for testing
    with open('test_report.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print("PDF saved to test_report.pdf")
except Exception as e:
    print(f"Error generating PDF: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

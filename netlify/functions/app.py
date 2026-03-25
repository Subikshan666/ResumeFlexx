import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import serverless_wsgi
from app import app  # Import the main Flask app

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

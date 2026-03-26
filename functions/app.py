import sys
import os
import traceback

# Netlify functions are executed in a directory where the root is two levels up from the script
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

try:
    import serverless_wsgi
    from app import app
except Exception as e:
    # If we fail to import, we want to know why
    error_info = traceback.format_exc()
    def handler(event, context):
        return {
            "statusCode": 500,
            "body": f"Import Error:\n{error_info}\n\nRoot Dir: {ROOT_DIR}\nFiles in Root: {os.listdir(ROOT_DIR)}"
        }
else:
    def handler(event, context):
        return serverless_wsgi.handle_request(app, event, context)

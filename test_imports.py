try:
    import flask
    import PyPDF2
    import docx
    import sklearn
    import pandas
    import numpy
    print("All basic dependencies are present.")
except ImportError as e:
    print(f"Missing dependency: {e}")

try:
    from utils.parser import get_text_from_file
    from utils.analyzer import calculate_similarity
    print("Utils imported successfully.")
except Exception as e:
    print(f"Error importing utils: {e}")

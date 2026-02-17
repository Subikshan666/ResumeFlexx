# AI-Based Resume Analyzer

A Flask-based web application that analyzes resumes against job descriptions using Natural Language Processing (NLP) techniques. It provides a match score and suggests missing keywords/skills.

## Features
- **File Support**: Upload resumes in PDF or DOCX format.
- **NLP Analysis**: Uses spaCy and Scikit-learn (TF-IDF) for text comparison.
- **Match Score**: Calculates cosine similarity between resume and job description.
- **Skill Suggestion**: Identifies missing technical skills based on keyword extraction.
- **Clean UI**: Responsive and user-friendly interface.

## Tech Stack
- **Backend**: Python, Flask
- **NLP**: spaCy, Scikit-learn
- **Parsing**: PyPDF2 (PDF), python-docx (DOCX)
- **Frontend**: HTML5, CSS3

## Project Structure
```text
Resume Analyzer/
├── app.py                # Flask Controller
├── requirements.txt      # Project Dependencies
├── utils/
│   ├── parser.py         # Text extraction logic
│   └── analyzer.py       # NLP and Matching logic
├── templates/
│   ├── index.html        # Main landing page
│   └── result.html       # Analysis result page
├── static/
│   ├── css/
│   │   └── style.css     # UI Styling
│   └── uploads/          # Temporary folder for uploads
└── README.md
```

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher installed.

### 2. Install Dependencies
Open your terminal/command prompt and run:
```bash
pip install -r requirements.txt
```

### 3. Download NLP Model
Download the English language model for spaCy:
```bash
python -m spacy download en_core_web_sm
```

### 4. Run the Application
Execute the following command:
```bash
python app.py
```

### 5. Access the App
Open your web browser and go to: `http://127.0.0.1:5000`

## How to Use
1. Upload your resume (PDF or DOCX).
2. Paste the Job Description into the text area.
3. Click "Analyze Resume".
4. View your match score and recommended skills.

## Evaluation Notes for Final Year Project
- **Data Preprocessing**: The system performs tokenization, stop-word removal, and lemmatization.
- **Vectorization**: Uses TF-IDF (Term Frequency-Inverse Document Frequency) to convert text into numerical vectors.
- **Similarity Measure**: Uses Cosine Similarity to determine the mathematical closeness of the two documents.

from flask import Flask, request, redirect, url_for, flash, render_template, jsonify
import os
from werkzeug.utils import secure_filename
from utils.parser import get_text_from_file
from utils.resume_db import init_db, save_analysis, get_dashboard_stats, get_history, delete_history_item, get_analysis_by_id
from utils.analyzer import (
    calculate_similarity, 
    identify_missing_skills, 
    get_recommendations,
    calculate_score_breakdown,
    analyze_power_words,
    check_resume_health,
    analyze_resume_stats,
    analyze_section_coverage,
    calculate_keyword_coverage,
    calculate_ats_readiness,
    build_action_checklist,
    get_top_keywords
)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key_change_me")
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Initialize DB on start
init_db()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    stats = get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/analyze_page')
def analyze_page():
    return render_template('index.html')

@app.route('/history')
def history():
    history_data = get_history()
    return render_template('history.html', history=history_data)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/create_resume')
def create_resume():
    return render_template('create_resume.html')

@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    # Gather form data
    resume_data = {
        'name': request.form.get('name'),
        'title': request.form.get('title'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'location': request.form.get('location'),
        'linkedin': request.form.get('linkedin'),
        'summary': request.form.get('summary'),
        'experience': request.form.get('experience'),
        'education': request.form.get('education'),
        'projects': request.form.get('projects'),
        'skills': request.form.get('skills'),
        'certifications': request.form.get('certifications'),
        'template': request.form.get('template', 'modern')
    }
    return render_template('resume_preview.html', resume=resume_data)

@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    delete_history_item(item_id)
    flash('Analysis record deleted.')
    return redirect(url_for('history'))

@app.route('/view/<int:item_id>')
def view_analysis(item_id):
    results = get_analysis_by_id(item_id)
    if results:
        return render_template('result.html', **results)
    flash('Analysis not found.')
    return redirect(url_for('history'))

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        flash('No file part')
        return redirect(url_for('analyze_page'))
    
    file = request.files['resume']
    jd_text = request.form.get('job_description')

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('analyze_page'))
    
    if not jd_text or len(jd_text.strip()) < 20:
        flash('Please provide a valid job description.')
        return redirect(url_for('analyze_page'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text
        resume_text = get_text_from_file(file_path)
        
        if not resume_text:
            flash('Could not extract text from the resume.')
            return redirect(url_for('analyze_page'))
            
        # Analyze
        score = calculate_similarity(resume_text, jd_text)
        missing_skills = identify_missing_skills(resume_text, jd_text)
        recommendations = get_recommendations(missing_skills)
        
        # New Analysis Features
        score_breakdown = calculate_score_breakdown(missing_skills, score)
        power_word_count, power_words = analyze_power_words(resume_text)
        health_score, health_issues = check_resume_health(resume_text)
        resume_stats = analyze_resume_stats(resume_text)
        section_coverage = analyze_section_coverage(resume_text)
        keyword_coverage = calculate_keyword_coverage(resume_text, jd_text)
        ats_score = calculate_ats_readiness(health_score, missing_skills, resume_stats)
        action_checklist = build_action_checklist(health_issues, missing_skills, resume_stats, section_coverage)
        jd_top_keywords = get_top_keywords(jd_text, limit=12)
        
        results = {
            'score': score, 
            'missing_skills': missing_skills,
            'recommendations': recommendations,
            'score_breakdown': score_breakdown,
            'power_word_count': power_word_count,
            'power_words': power_words,
            'health_score': health_score,
            'health_issues': health_issues,
            'resume_stats': resume_stats,
            'section_coverage': section_coverage,
            'keyword_coverage': keyword_coverage,
            'ats_score': ats_score,
            'action_checklist': action_checklist,
            'jd_top_keywords': jd_top_keywords,
            'filename': filename
        }

        # Save to DB
        save_analysis(filename, score, ats_score, health_score, missing_skills, results)
        
        return render_template('result.html', **results)
    else:
        flash('Allowed file types are PDF and DOCX')
        return redirect(url_for('analyze_page'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

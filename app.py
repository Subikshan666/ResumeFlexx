from flask import Flask, request, redirect, url_for, flash, render_template, jsonify, make_response, send_file
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
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

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

    # Add analytics for preview
    text = " ".join([
        resume_data.get('summary', ''),
        resume_data.get('experience', ''),
        resume_data.get('education', ''),
        resume_data.get('projects', ''),
        resume_data.get('skills', ''),
        resume_data.get('certifications', '')
    ])
    from utils.analyzer import analyze_resume_stats, analyze_power_words, get_top_keywords
    stats = analyze_resume_stats(text)
    power_word_count, power_words = analyze_power_words(text)
    keywords = get_top_keywords(text, limit=10)

    resume_data['word_count'] = stats.get('word_count')
    resume_data['char_count'] = stats.get('char_count')
    resume_data['avg_words_per_sentence'] = stats.get('avg_words_per_sentence')
    resume_data['bullet_count'] = stats.get('bullet_count')
    resume_data['power_word_count'] = power_word_count
    resume_data['power_words'] = power_words
    resume_data['keywords'] = keywords

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

        # Save to DB and capture ID so we can link to PDF route
        analysis_id = save_analysis(filename, score, ats_score, health_score, missing_skills, results)
        results['analysis_id'] = analysis_id
        
        return render_template('result.html', **results)
    else:
        flash('Allowed file types are PDF and DOCX')
        return redirect(url_for('analyze_page'))

def generate_pdf_report(results):
    """Generate a professional PDF report using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=0.75*inch, 
        leftMargin=0.75*inch,
        topMargin=0.75*inch, 
        bottomMargin=0.75*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#2ECC71'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=32
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=colors.HexColor('#2ECC71'),
        borderPadding=8,
        backColor=colors.HexColor('#F0F8F5')
    )
    
    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#16A085'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_LEFT,
        leading=14
    )
    
    # Header
    story.append(Paragraph("📄 Resume Analysis Report", title_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Date and filename
    date_text = f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    story.append(Paragraph(date_text, body_style))
    if results.get('filename'):
        story.append(Paragraph(f"<b>Resume File:</b> {results.get('filename')}", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # === SCORE SUMMARY ===
    story.append(Paragraph("📊 Score Summary", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    scores_data = [
        ['Metric', 'Score', 'Status'],
        [
            'Match Score', 
            f"{results.get('score', 0):.1f}%",
            '✓ Good' if results.get('score', 0) >= 70 else '⚠ Needs Work'
        ],
        [
            'ATS Readiness', 
            f"{results.get('ats_score', 0):.1f}%",
            '✓ Good' if results.get('ats_score', 0) >= 70 else '⚠ Needs Work'
        ],
        [
            'Resume Health', 
            f"{results.get('health_score', 0):.1f}%",
            '✓ Good' if results.get('health_score', 0) >= 70 else '⚠ Needs Work'
        ],
    ]
    
    scores_table = Table(scores_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
    ]))
    story.append(scores_table)
    story.append(Spacer(1, 0.3*inch))
    
    # === MISSING SKILLS ===
    if results.get('missing_skills') and len(results.get('missing_skills')) > 0:
        story.append(Paragraph("🎯 Missing Skills (Add These!)", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        missing_skills = results.get('missing_skills', [])
        for idx, skill in enumerate(missing_skills[:15], 1):
            story.append(Paragraph(f"{idx}. <b>{skill.upper()}</b>", body_style))
        
        if len(missing_skills) > 15:
            story.append(Paragraph(f"<i>...and {len(missing_skills) - 15} more</i>", body_style))
        
        story.append(Spacer(1, 0.2*inch))
    
    # === RESUME STATISTICS ===
    if results.get('resume_stats'):
        story.append(Paragraph("📈 Resume Statistics", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        stats = results.get('resume_stats', {})
        stats_data = [
            ['Metric', 'Value'],
            ['Word Count', str(stats.get('word_count', 0))],
            ['Character Count', str(stats.get('char_count', 0))],
            ['Bullet Points', str(stats.get('bullet_count', 0))],
            ['Avg Words/Sentence', str(stats.get('avg_words_per_sentence', 0))],
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.2*inch))
    
    # === HEALTH ISSUES ===
    if results.get('health_issues') and len(results.get('health_issues')) > 0:
        story.append(Paragraph("⚠️ Health Issues to Fix", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        health_issues = results.get('health_issues', [])
        for idx, issue in enumerate(health_issues[:10], 1):
            story.append(Paragraph(f"{idx}. {issue}", body_style))
        story.append(Spacer(1, 0.2*inch))
    
    # === TOP KEYWORDS ===
    if results.get('jd_top_keywords'):
        story.append(Paragraph("🔑 Top Keywords from Job Description", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        keywords = results.get('jd_top_keywords', [])
        keywords_text = " • ".join([f"<b>{kw}</b>" for kw in keywords[:20]])
        story.append(Paragraph(keywords_text, body_style))
        story.append(Spacer(1, 0.2*inch))
    
    # === ACTION CHECKLIST ===
    if results.get('action_checklist'):
        story.append(Paragraph("✅ Action Checklist", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        action_checklist = results.get('action_checklist', [])
        if isinstance(action_checklist, list):
            for idx, item in enumerate(action_checklist[:12], 1):
                story.append(Paragraph(f"☐ {item}", body_style))
        elif isinstance(action_checklist, dict):
            for category, items in action_checklist.items():
                if items:
                    story.append(Paragraph(f"<b>{category.replace('_', ' ').title()}:</b>", subheading_style))
                    for item in items[:5]:
                        story.append(Paragraph(f"  ☐ {item}", body_style))
    
    # Footer
    story.append(Spacer(1, 0.4*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#7F8C8D'),
        alignment=TA_CENTER
    )
    story.append(Paragraph("—" * 50, footer_style))
    story.append(Paragraph("Generated by ResumeFlexx - Your AI Resume Assistant", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

@app.route("/download-report/<int:analysis_id>")
def download_report(analysis_id: int):
    """Generate and download a PDF report."""
    with open('endpoint_calls.log', 'a') as f:
        f.write(f"[CALL] download_report({analysis_id})\n")
    
    try:
        results = get_analysis_by_id(analysis_id)
        with open('endpoint_calls.log', 'a') as f:
            f.write(f"[RESULTS] Found: {results is not None}\n")
        
        if not results:
            flash("Analysis not found.")
            return redirect(url_for("history"))

        pdf_bytes = generate_pdf_report(results)
        with open('endpoint_calls.log', 'a') as f:
            f.write(f"[PDF] Generated {len(pdf_bytes)} bytes\n")
        
        return send_file(
            BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"Resume_Analysis_Report_{analysis_id}.pdf"
        )
    except Exception as e:
        import traceback
        error_msg = f"Error generating PDF: {str(e)}\nTraceback:\n{traceback.format_exc()}"
        with open('pdf_error.log', 'a') as f:
            f.write(f"\n{datetime.now()}\n{error_msg}\n---\n")
        flash(f"Error generating PDF: {str(e)}")
        return redirect(url_for("history"))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

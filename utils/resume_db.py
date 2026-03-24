import sqlite3
import json
import os
from datetime import datetime

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
DB_PATH = 'resume_history.db'

def get_connection():
    if DATABASE_URL:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL)
        return conn, "%s", RealDictCursor
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn, "?", None

def init_db():
    conn, q, _ = get_connection()
    cursor = conn.cursor()
    
    # Standard SQL for both SQLite and PostgreSQL
    # PostgreSQL doesn't use AUTOINCREMENT, it uses SERIAL or IDENTITY
    if DATABASE_URL:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id SERIAL PRIMARY KEY,
                filename TEXT,
                timestamp TEXT,
                score REAL,
                ats_score REAL,
                health_score REAL,
                missing_skills TEXT,
                results_json TEXT
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                timestamp TEXT,
                score REAL,
                ats_score REAL,
                health_score REAL,
                missing_skills TEXT,
                results_json TEXT
            )
        ''')
    conn.commit()
    conn.close()

def save_analysis(filename, score, ats_score, health_score, missing_skills, results):
    """Persist an analysis run and return its new primary key ID."""
    conn, q, _ = get_connection()
    cursor = conn.cursor()
    
    query = f'''
        INSERT INTO history (filename, timestamp, score, ats_score, health_score, missing_skills, results_json)
        VALUES ({q}, {q}, {q}, {q}, {q}, {q}, {q})
    '''
    
    values = (
        filename,
        datetime.now().strftime('%d/%m/%Y'),
        score,
        ats_score,
        health_score,
        json.dumps(missing_skills),
        json.dumps(results),
    )
    
    cursor.execute(query, values)
    
    if DATABASE_URL:
        # For PostgreSQL, get the last inserted ID
        cursor.execute("SELECT currval(pg_get_serial_sequence('history', 'id'))")
        analysis_id = cursor.fetchone()[0]
    else:
        analysis_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return analysis_id

def get_history():
    conn, q, dict_factory = get_connection()
    if dict_factory:
        cursor = conn.cursor(cursor_factory=dict_factory)
    else:
        cursor = conn.cursor()
        
    cursor.execute('SELECT * FROM history ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        d = dict(row)
        d['missing_skills'] = json.loads(d['missing_skills'])
        history.append(d)
    return history

def get_analysis_by_id(analysis_id):
    conn, q, dict_factory = get_connection()
    if dict_factory:
        cursor = conn.cursor(cursor_factory=dict_factory)
    else:
        cursor = conn.cursor()
        
    cursor.execute(f'SELECT * FROM history WHERE id = {q}', (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None

    d = dict(row)
    results = json.loads(d['results_json'])
    results['analysis_id'] = d['id']
    return results

def get_dashboard_stats():
    conn, q, _ = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM history')
    total_count = cursor.fetchone()[0]
    
    if total_count == 0:
        conn.close()
        return {
            'total_resumes': 0,
            'avg_score': 0,
            'best_score': 0,
            'recent': []
        }
    
    cursor.execute('SELECT AVG(score) FROM history')
    avg_score = round(float(cursor.fetchone()[0] or 0))
    
    cursor.execute('SELECT MAX(score) FROM history')
    best_score = round(float(cursor.fetchone()[0] or 0))
    
    conn.close()
    
    recent = get_history()[:5]
    
    return {
        'total_resumes': total_count,
        'avg_score': avg_score,
        'best_score': best_score,
        'recent': recent
    }

def delete_history_item(item_id):
    conn, q, _ = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM history WHERE id = {q}', (item_id,))
    conn.commit()
    conn.close()

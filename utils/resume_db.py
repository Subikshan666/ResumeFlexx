import sqlite3
import json
import os
from datetime import datetime

DB_PATH = 'resume_history.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (filename, timestamp, score, ats_score, health_score, missing_skills, results_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        filename,
        datetime.now().strftime('%d/%m/%Y'),
        score,
        ats_score,
        health_score,
        json.dumps(missing_skills),
        json.dumps(results)
    ))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM history WHERE id = ?', (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        d = dict(row)
        return json.loads(d['results_json'])
    return None

def get_dashboard_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM history')
    total_count = cursor.fetchone()[0]
    
    if total_count == 0:
        return {
            'total_resumes': 0,
            'avg_score': 0,
            'best_score': 0,
            'recent': []
        }
    
    cursor.execute('SELECT AVG(score) FROM history')
    avg_score = round(cursor.fetchone()[0] or 0)
    
    cursor.execute('SELECT MAX(score) FROM history')
    best_score = round(cursor.fetchone()[0] or 0)
    
    conn.close()
    
    recent = get_history()[:5]
    
    return {
        'total_resumes': total_count,
        'avg_score': avg_score,
        'best_score': best_score,
        'recent': recent
    }

def delete_history_item(item_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM history WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

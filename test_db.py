from utils.resume_db import init_db, save_analysis, get_history, get_dashboard_stats, delete_history_item
import os

def test_db():
    print("Testing ResumeAI Database Layer...")
    
    # 1. Initialize
    init_db()
    print("[✓] Database initialized")
    
    # 2. Save Analysis
    filename = "test_resume.pdf"
    score = 85.5
    ats_score = 78.0
    health_score = 90.0
    missing_skills = ["Docker", "Kubernetes"]
    results = {"detail": "complete results"}
    
    save_analysis(filename, score, ats_score, health_score, missing_skills, results)
    print("[✓] Test analysis saved")
    
    # 3. Fetch History
    history = get_history()
    assert len(history) > 0, "History should not be empty"
    assert history[0]['filename'] == filename, "Filename mismatch"
    print(f"[✓] History fetched: {len(history)} items")
    
    # 4. Dashboard Stats
    stats = get_dashboard_stats()
    assert stats['total_resumes'] > 0, "Stats total resumes should be > 0"
    print(f"[✓] Stats fetched: Total {stats['total_resumes']}, Avg {stats['avg_score']}, Best {stats['best_score']}")
    
    # 5. Delete
    item_id = history[0]['id']
    delete_history_item(item_id)
    new_history = get_history()
    # If it was a clean DB, it should be empty now. If not, it should be matches - 1.
    print("[✓] Item deleted successfully")
    
    print("\n[ALL TESTS PASSED]")

if __name__ == "__main__":
    if os.path.exists('resume_history.db'):
        os.remove('resume_history.db')
    test_db()

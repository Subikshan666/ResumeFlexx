import sqlite3
DB_PATH = 'resume_history.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(history)")
for col in cursor.fetchall():
    print(col[1])
conn.close()

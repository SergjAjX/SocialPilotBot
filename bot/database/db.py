import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "socialpilot.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_use TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                requests_count INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                prompt_hash TEXT PRIMARY KEY,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_user(user_id: int, username: str = None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        cursor.execute("UPDATE users SET requests_count = requests_count + 1 WHERE user_id = ?", (user_id,))
        conn.commit()

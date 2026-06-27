
import sqlite3
from datetime import datetime
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            requests_today INTEGER DEFAULT 0,
            last_request_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            request_type TEXT,
            prompt TEXT,
            response TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_user(user_id: int, username: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username) 
        VALUES (?, ?)
    ''', (user_id, username))
    
    conn.commit()
    conn.close()

def get_user_requests_today(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().date()
    cursor.execute('''
        SELECT requests_today FROM users 
        WHERE user_id = ? AND date(last_request_date) = ?
    ''', (user_id, str(today)))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else 0

def increment_request_count(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().isoformat()
    cursor.execute('''
        UPDATE users 
        SET requests_today = requests_today + 1, last_request_date = ?
        WHERE user_id = ?
    ''', (today, user_id))
    
    conn.commit()
    conn.close()

def save_request(user_id: int, request_type: str, prompt: str, response: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO requests (user_id, request_type, prompt, response)
        VALUES (?, ?, ?, ?)
    ''', (user_id, request_type, prompt, response))
    
    conn.commit()
    conn.close()

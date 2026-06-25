import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "socialpilot.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                requests INTEGER DEFAULT 1,
                provider TEXT DEFAULT 'openrouter',
                selected_model TEXT DEFAULT '1',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_user(user_id: int, username: str = None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.execute("UPDATE users SET requests = requests + 1 WHERE user_id = ?", (user_id,))

def get_user_provider(user_id: int) -> str:
    """Получить выбранного провайдера"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT provider FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 'openrouter'

def set_user_provider(user_id: int, provider: str):
    """Установить провайдера"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE users SET provider = ? WHERE user_id = ?", (provider, user_id))

def get_user_model(user_id: int) -> str:
    """Получить выбранную модель пользователя"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT selected_model FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else '1'

def set_user_model(user_id: int, model_key: str):
    """Установить выбранную модель для пользователя"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE users SET selected_model = ? WHERE user_id = ?", (model_key, user_id))

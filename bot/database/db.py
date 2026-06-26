import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "socialpilot.db")


def init_db():
    """Инициализация базы данных с миграцией"""
    with sqlite3.connect(DB_PATH) as conn:
        # Создаём таблицу если не существует
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
        
        # Проверяем существование колонок (миграция для старых БД)
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'provider' not in columns:
            logger.info("🔄 Миграция: добавляю колонку 'provider'")
            conn.execute("ALTER TABLE users ADD COLUMN provider TEXT DEFAULT 'openrouter'")
        
        if 'selected_model' not in columns:
            logger.info("🔄 Миграция: добавляю колонку 'selected_model'")
            conn.execute("ALTER TABLE users ADD COLUMN selected_model TEXT DEFAULT '1'")


def save_user(user_id: int, username: str = None):
    """Сохранить пользователя и увеличить счётчик запросов"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        conn.execute(
            "UPDATE users SET requests = requests + 1 WHERE user_id = ?",
            (user_id,)
        )


def get_user_provider(user_id: int) -> str:
    """Получить выбранного провайдера"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT provider FROM users WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        return result[0] if result and result[0] else 'openrouter'


def set_user_provider(user_id: int, provider: str):
    """Установить провайдера"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE users SET provider = ? WHERE user_id = ?",
            (provider, user_id)
        )


def get_user_model(user_id: int) -> str:
    """Получить выбранную модель пользователя"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT selected_model FROM users WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        return result[0] if result and result[0] else '1'


def set_user_model(user_id: int, model_key: str):
    """Установить выбранную модель для пользователя"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE users SET selected_model = ? WHERE user_id = ?",
            (model_key, user_id)
        )

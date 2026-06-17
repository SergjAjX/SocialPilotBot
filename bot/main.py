
import asyncio
import os
import logging
from dotenv import load_dotenv

# === КРИТИЧНО ВАЖНО: load_dotenv() ДОЛЖЕН БЫТЬ ПЕРЕД ВСЕМИ ИМПОРТАМИ ===
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Проверяем наличие токенов сразу
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env файле")

if not OPENROUTER_API_KEY:
    logging.warning("⚠️ OPENROUTER_API_KEY не найден. Бот запустится, но AI-функции не будут работать.")

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

# Импортируем обработчики (теперь .env уже загружен)
from bot.handlers import start, idea, optimize
from bot.database.db import init_db


async def set_commands(bot: Bot):
    """Устанавливаем команды бота"""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="idea", description="Сгенерировать идеи для поста"),
        BotCommand(command="optimize", description="Оптимизировать текст поста"),
    ]
    await bot.set_my_commands(commands)


async def main():
    """Основная функция запуска бота"""
    # Инициализация базы данных
    init_db()
    
    # Создаём экземпляры бота и диспетчера
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    
    # Регистрируем роутеры
    dp.include_routers(
        start.router,
        idea.router,
        optimize.router
    )
    
    # Устанавливаем команды
    await set_commands(bot)
    
    # Удаляем вебхук и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    logging.info("✅ SocialPilotBot успешно запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

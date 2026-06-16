
import asyncio
import os
import logging
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv
from bot.handlers import start, idea, optimize
from bot.database.db import init_db

# Явно указываем путь к .env файлу
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Отладочный вывод для проверки
print(f"🔍 Загрузка .env из: {env_path}")
print(f"🔍 BOT_TOKEN загружен: {'✅' if BOT_TOKEN else '❌'}")
print(f"🔍 OPENROUTER_API_KEY загружен: {'✅' if OPENROUTER_API_KEY else '❌'}")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def set_commands():
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="idea", description="Сгенерировать идею поста"),
        BotCommand(command="optimize", description="Оптимизировать текст"),
    ]
    await bot.set_my_commands(commands)

async def main():
    init_db()
    await set_commands()
    dp.include_routers(start.router, idea.router, optimize.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env only for local development
if not os.getenv("RAILWAY_ENVIRONMENT"):
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/hvost_v_fokuse")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found! Add to .env or environment variables")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found! Add to .env or environment variables")

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from bot.handlers import start, commands
from bot.database.db import init_db

async def set_commands(bot: Bot):
    commands_list = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="idea", description="Генерировать идеи для постов"),
        BotCommand(command="optimize", description="Оптимизировать текст"),
        BotCommand(command="analyze", description="Анализировать пост"),
        BotCommand(command="help", description="Справка"),
    ]
    await bot.set_my_commands(commands_list)

async def main():
    init_db()
    logger.info("✅ База данных инициализирована")
    
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    
    dp.include_routers(
        start.router,
        commands.router
    )
    
    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("✅ SocialPilotBot запущен!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

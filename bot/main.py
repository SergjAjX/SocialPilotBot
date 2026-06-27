import asyncio
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# === Загружаем .env ТОЛЬКО для локальной разработки ===
if not os.getenv("RAILWAY_ENVIRONMENT"):
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# === Получаем ключи из переменных окружения ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# === Логирование ===
logger.info(f"🔑 BOT_TOKEN: {'✅' if BOT_TOKEN else '❌'}")
logger.info(f"🔑 OPENROUTER_API_KEY: {'✅' if OPENROUTER_API_KEY else '❌'}")
logger.info(f"🔑 HF_TOKEN: {'✅' if HF_TOKEN else '❌'}")

if not BOT_TOKEN:
    raise ValueError(
        "❌ BOT_TOKEN не найден!\n"
        "Локально: добавь в .env\n"
        "На сервере: добавь в переменные окружения"
    )

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

# ИСПРАВЛЕНО: относительный импорт (убрали префикс bot.)
from handlers import start, idea, optimize, model
from database.db import init_db


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="provider", description="Выбрать AI провайдера"),
        BotCommand(command="model", description="Выбрать AI модель"),
        BotCommand(command="idea", description="Сгенерировать идеи для поста"),
        BotCommand(command="optimize", description="Оптимизировать текст поста"),
    ]
    await bot.set_my_commands(commands)


async def main():
    init_db()
    
    # ИСПРАВЛЕНО: синтаксис parse_mode для aiogram 3.x
    bot = Bot(
        token=BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    dp.include_routers(
        start.router,
        model.router,
        idea.router,
        optimize.router
    )
    
    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("✅ SocialPilotBot успешно запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

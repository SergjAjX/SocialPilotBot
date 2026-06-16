
import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv
from bot.handlers import start, idea, optimize
from bot.database.db import init_db

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
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

from aiogram import Router, types
from aiogram.filters import Command
from bot.database.db import save_user

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    save_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "👋 Привет! Я SocialPilotBot — твой SMM-ассистент.\n\n"
        "Доступные команды:\n"
        "/idea <тема> — сгенерировать идеи для поста\n"
        "/optimize <текст> — оптимизировать текст поста"
    )

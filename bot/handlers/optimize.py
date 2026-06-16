from aiogram import Router, types
from aiogram.filters import Command
from bot.services.openrouter_fallback import OpenRouterClient
from bot.database.db import save_user

router = Router()
client = OpenRouterClient()

@router.message(Command("optimize"))
async def optimize_text(message: types.Message):
    save_user(message.from_user.id, message.from_user.username)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("📝 Напиши текст после команды, например:\n/optimize Мой пост о фитнесе")
        return
    
    text = args[1]
    prompt = f"Оптимизируй этот текст для соцсетей, сделай его более привлекательным и добавь эмодзи:\n\n{text}"
    
    await message.answer("✨ Оптимизирую текст...")
    response = await client.ask(prompt)
    await message.answer(f"📝 Вот оптимизированный вариант:\n\n{response}")

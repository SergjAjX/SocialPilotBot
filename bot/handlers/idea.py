from aiogram import Router, types
from aiogram.filters import Command
from bot.services.openrouter_fallback import OpenRouterClient
from bot.database.db import save_user

router = Router()
client = OpenRouterClient()

@router.message(Command("idea"))
async def generate_idea(message: types.Message):
    save_user(message.from_user.id, message.from_user.username)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("📝 Напиши тему после команды, например:\n/idea фитнес для мам")
        return
    
    topic = args[1]
    prompt = f"Придумай 3 идеи для поста в соцсетях на тему '{topic}'. Для каждой идеи: заголовок и формат (Reels/карусель/опрос)."
    
    await message.answer("🧠 Генерирую идеи через бесплатные модели...")
    response = await client.ask(prompt)
    await message.answer(f"💡 Вот идеи:\n\n{response}")

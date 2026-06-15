from aiogram import Router, types
from aiogram.filters import Command
from bot.services.openrouter_fallback import OpenRouterClient

router = Router()
client = OpenRouterClient()

@router.message(Command("idea"))
async def generate_idea(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("📝 Напиши тему после команды, например:\n/idea фитнес для мам")
        return
    
    topic = args[1]
    prompt = f"Придумай 5 идей для поста в соцсетях на тему '{topic}'. Для каждой идеи напиши заголовок и формат (Reels, карусель, опрос)."
    
    await message.answer("🧠 Генерирую идеи... (использую бесплатные модели)")
    response = await client.ask(prompt)
    await message.answer(f"💡 Вот идеи:\n\n{response}")

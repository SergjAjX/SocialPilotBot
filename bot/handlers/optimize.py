from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("optimize"))
async def optimize_text(message: types.Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("📝 Используй: /optimize [платформа] [текст]\nПример: /optimize telegram Привет, это мой пост...")
        return
    
    platform = args[1]
    text = args[2]
    
    # Здесь будет вызов модели
    await message.answer(f"🔄 Оптимизирую текст для {platform}...\n\n(Функция в разработке, используй /idea пока)")

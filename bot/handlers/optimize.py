from aiogram import Router, types
from aiogram.filters import Command
from bot.services.openrouter_fallback import OpenRouterClient, MODELS as OR_MODELS
from bot.services.huggingface_client import HuggingFaceClient, HF_MODELS
from bot.database.db import save_user, get_user_model, get_user_provider

router = Router()
or_client = OpenRouterClient()
hf_client = HuggingFaceClient()

@router.message(Command("optimize"))
async def optimize_text(message: types.Message):
    save_user(message.from_user.id, message.from_user.username)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("📝 Напиши текст после команды, например:\n/optimize Мой пост о фитнесе")
        return
    
    text = args[1]
    prompt = f"Оптимизируй этот текст для соцсетей, сделай его более привлекательным и добавь эмодзи:\n\n{text}"
    
    provider = get_user_provider(message.from_user.id)
    model_key = get_user_model(message.from_user.id)
    
    if provider == "openrouter":
        model_name = OR_MODELS.get(model_key, OR_MODELS['1'])['name']
        await message.answer(f"✨ Оптимизирую текст через {model_name}...")
        response = await or_client.ask(prompt, model_key)
    else:
        model_name = HF_MODELS.get(model_key, HF_MODELS['1'])['name']
        await message.answer(f"✨ Оптимизирую текст через {model_name}...")
        response = await hf_client.ask(prompt, model_key)
    
    await message.answer(f"📝 Вот оптимизированный вариант:\n\n{response}")

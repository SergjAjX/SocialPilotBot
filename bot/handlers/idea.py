from aiogram import Router, types
from aiogram.filters import Command
from bot.services.openrouter_fallback import OpenRouterClient, MODELS as OR_MODELS
from bot.services.huggingface_client import HuggingFaceClient, HF_MODELS
from bot.database.db import save_user, get_user_model, get_user_provider

router = Router()
or_client = OpenRouterClient()
hf_client = HuggingFaceClient()

@router.message(Command("idea"))
async def generate_idea(message: types.Message):
    save_user(message.from_user.id, message.from_user.username)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("📝 Напиши тему после команды, например:\n/idea фитнес для мам")
        return
    
    topic = args[1]
    prompt = f"Придумай 3 идеи для поста в соцсетях на тему '{topic}'. Для каждой идеи: заголовок и формат (Reels/карусель/опрос)."
    
    provider = get_user_provider(message.from_user.id)
    model_key = get_user_model(message.from_user.id)
    
    if provider == "openrouter":
        model_name = OR_MODELS.get(model_key, OR_MODELS['1'])['name']
        await message.answer(f"🧠 Генерирую идеи через {model_name}...")
        response = await or_client.ask(prompt, model_key)
    else:
        model_name = HF_MODELS.get(model_key, HF_MODELS['1'])['name']
        await message.answer(f"🧠 Генерирую идеи через {model_name}...")
        response = await hf_client.ask(prompt, model_key)
    
    await message.answer(f"💡 Вот идеи:\n\n{response}")

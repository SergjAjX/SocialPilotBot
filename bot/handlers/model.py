from aiogram import Router, types
from aiogram.filters import Command
from bot.database.db import get_user_model, set_user_model, get_user_provider, set_user_provider
from bot.services.openrouter_fallback import OpenRouterClient, MODELS as OR_MODELS
from bot.services.huggingface_client import HuggingFaceClient, HF_MODELS

router = Router()
or_client = OpenRouterClient()
hf_client = HuggingFaceClient()


@router.message(Command("model"))
async def handle_model(message: types.Message):
    """Обработчик команды /model - показывает список или выбирает модель"""
    args = message.text.split(maxsplit=1)
    provider = get_user_provider(message.from_user.id)
    
    # Если указан номер - выбираем модель
    if len(args) >= 2:
        model_key = args[1].strip()
        
        if provider == "openrouter":
            if model_key not in OR_MODELS:
                await message.answer(
                    f"❌ Модель '{model_key}' не найдена.\n\n" + or_client.get_models_list(),
                    parse_mode="HTML"
                )
                return
            set_user_model(message.from_user.id, model_key)
            model_name = OR_MODELS[model_key]['name']
        else:
            if model_key not in HF_MODELS:
                await message.answer(
                    f"❌ Модель '{model_key}' не найдена.\n\n" + hf_client.get_models_list(),
                    parse_mode="HTML"
                )
                return
            set_user_model(message.from_user.id, model_key)
            model_name = HF_MODELS[model_key]['name']
        
        await message.answer(
            f"✅ <b>Модель изменена!</b>\n\n"
            f"🤖 Теперь используется: <b>{model_name}</b>\n\n"
            f"💡 Попробуй: /idea маркетинг",
            parse_mode="HTML"
        )
        return
    
    # Если номер не указан - показываем список
    current_model = get_user_model(message.from_user.id)
    
    if provider == "openrouter":
        current_name = OR_MODELS.get(current_model, OR_MODELS['1'])['name']
        models_list = or_client.get_models_list()
    else:
        current_name = HF_MODELS.get(current_model, HF_MODELS['1'])['name']
        models_list = hf_client.get_models_list()
    
    await message.answer(
        f"🎯 <b>Текущая модель:</b> {current_name}\n\n" + models_list,
        parse_mode="HTML"
    )


@router.message(Command("provider"))
async def handle_provider(message: types.Message):
    """Обработчик команды /provider - выбирает провайдера"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        current = get_user_provider(message.from_user.id)
        current_name = "🌐 OpenRouter" if current == "openrouter" else "🤗 Hugging Face"
        
        text = (
            f"📡 <b>Выбор провайдера:</b>\n\n"
            f"🎯 Текущий: {current_name}\n\n"
            f"<b>1.</b> 🌐 OpenRouter\n"
            f"   • 5 бесплатных моделей через OpenRouter API\n"
            f"   • Стабильная работа\n"
            f"   • Быстрые ответы\n\n"
            f"<b>2.</b> 🤗 Hugging Face\n"
            f"   • 4 модели напрямую от HF\n"
            f"   • Прямой доступ к моделям\n"
            f"   • Может быть медленнее (холодный старт)\n\n"
            f"💡 Используй: /provider 1 или /provider 2"
        )
        await message.answer(text, parse_mode="HTML")
        return
    
    choice = args[1].strip()
    
    if choice == "1":
        set_user_provider(message.from_user.id, "openrouter")
        set_user_model(message.from_user.id, "1")
        await message.answer(
            "✅ <b>Провайдер изменён!</b>\n\n"
            "🌐 Теперь используется: <b>OpenRouter</b>\n"
            f"🤖 Модель по умолчанию: {OR_MODELS['1']['name']}\n\n"
            "💡 Выбери модель: /model",
            parse_mode="HTML"
        )
    elif choice == "2":
        set_user_provider(message.from_user.id, "huggingface")
        set_user_model(message.from_user.id, "1")
        await message.answer(
            "✅ <b>Провайдер изменён!</b>\n\n"
            "🤗 Теперь используется: <b>Hugging Face</b>\n"
            f"🤖 Модель по умолчанию: {HF_MODELS['1']['name']}\n\n"
            "💡 Выбери модель: /model",
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Неверный выбор. Используй /provider 1 или /provider 2")

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.db import (
    save_user, get_user_provider, get_user_model,
    set_user_provider, set_user_model
)
from bot.services.openrouter_fallback import OpenRouterClient, MODELS as OR_MODELS
from bot.services.huggingface_client import HuggingFaceClient, HF_MODELS

router = Router()


def _get_current_settings(user_id: int) -> tuple:
    """Получить текущие настройки пользователя"""
    provider = get_user_provider(user_id)
    model_key = get_user_model(user_id)
    provider_name = "🌐 OpenRouter" if provider == "openrouter" else "🤗 Hugging Face"
    
    if provider == "openrouter":
        model_name = OR_MODELS.get(model_key, OR_MODELS['1'])['name']
    else:
        model_name = HF_MODELS.get(model_key, HF_MODELS['1'])['name']
    
    return provider_name, model_name


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Главное приветствие бота"""
    save_user(message.from_user.id, message.from_user.username)
    
    provider_name, model_name = _get_current_settings(message.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться на канал", url="https://t.me/hvost_v_fokuse")],
        [
            InlineKeyboardButton(text="🤖 Модели", callback_data="show_models"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
        ],
        [InlineKeyboardButton(text="💡 Сгенерировать идею", callback_data="quick_idea")]
    ])
    
    welcome_text = (
        f"👋 <b>Привет, {message.from_user.first_name}!</b>\n\n"
        f"🎯 <b>Я SocialPilotBot — твой AI-ассистент для SMM</b>\n\n"
        f"📊 <b>Что я умею:</b>\n"
        f"• 💡 Генерировать идеи для постов\n"
        f"• ✨ Оптимизировать тексты для соцсетей\n"
        f"• 🎨 Создавать контент-планы\n"
        f"• 📝 Писать посты на любую тему\n\n"
        f"🤖 <b>Доступно 9 AI моделей:</b>\n"
        f"• 5 моделей через OpenRouter\n"
        f"• 4 модели Hugging Face\n\n"
        f"⚙️ <b>Твои настройки:</b>\n"
        f"📡 Провайдер: {provider_name}\n"
        f"🤖 Модель: {model_name}\n\n"
        f"📢 <b>Подпишись на канал</b> — там советы по SMM и маркетингу!\n\n"
        f"💡 <b>Команды:</b>\n"
        f"/idea &lt;тема&gt; — идеи для поста\n"
        f"/optimize &lt;текст&gt; — улучшить текст\n"
        f"/model — выбрать модель\n"
        f"/provider — сменить провайдера"
    )
    
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )


@router.callback_query(F.data == "show_models")
async def show_models_callback(callback: types.CallbackQuery):
    """Показать список моделей"""
    provider = get_user_provider(callback.from_user.id)
    current_model = get_user_model(callback.from_user.id)
    
    if provider == "openrouter":
        current_name = OR_MODELS.get(current_model, OR_MODELS['1'])['name']
        text = f"🎯 <b>Текущая модель:</b> {current_name}\n\n"
        text += "🌐 <b>Модели OpenRouter:</b>\n\n"
        for key, data in OR_MODELS.items():
            text += f"<b>{key}.</b> {data['name']}\n"
            text += f"   {data['description']}\n"
            text += f"   📏 Контекст: {data['context']}\n\n"
    else:
        current_name = HF_MODELS.get(current_model, HF_MODELS['1'])['name']
        text = f"🎯 <b>Текущая модель:</b> {current_name}\n\n"
        text += "🤗 <b>Модели Hugging Face:</b>\n\n"
        for key, data in HF_MODELS.items():
            text += f"<b>{key}.</b> {data['name']}\n"
            text += f"   {data['description']}\n"
            text += f"   📏 Контекст: {data['context']}\n\n"
    
    text += "💡 Используй /model &lt;номер&gt; для выбора\n\n"
    text += "[◀️ Назад](/start)"
    
    # ✅ ИСПРАВЛЕНО: используем edit_text вместо answer
    try:
        await callback.message.edit_text(text, parse_mode="HTML")
    except Exception:
        # Если edit не сработал, отправляем новое сообщение
        await callback.message.answer(text, parse_mode="HTML")
    
    await callback.answer()


@router.callback_query(F.data == "settings")
async def show_settings(callback: types.CallbackQuery):
    """Показать настройки"""
    provider_name, model_name = _get_current_settings(callback.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌐 OpenRouter", callback_data="set_provider_openrouter"),
            InlineKeyboardButton(text="🤗 Hugging Face", callback_data="set_provider_hf")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
    ])
    
    text = (
        f"⚙️ <b>Настройки:</b>\n\n"
        f"📡 <b>Провайдер:</b> {provider_name}\n"
        f"🤖 <b>Модель:</b> {model_name}\n\n"
        f"Выбери провайдера:"
    )
    
    # ✅ ИСПРАВЛЕНО: используем edit_text
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    
    await callback.answer()


@router.callback_query(F.data == "set_provider_openrouter")
async def set_provider_or(callback: types.CallbackQuery):
    """Установить OpenRouter"""
    set_user_provider(callback.from_user.id, "openrouter")
    set_user_model(callback.from_user.id, "1")
    
    text = (
        "✅ <b>Провайдер изменён!</b>\n\n"
        "🌐 Теперь используется: <b>OpenRouter</b>\n"
        f"🤖 Модель: {OR_MODELS['1']['name']}"
    )
    
    # ✅ ИСПРАВЛЕНО: используем edit_text
    try:
        await callback.message.edit_text(text, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, parse_mode="HTML")
    
    await callback.answer("✅ OpenRouter активирован!")


@router.callback_query(F.data == "set_provider_hf")
async def set_provider_hf(callback: types.CallbackQuery):
    """Установить Hugging Face"""
    set_user_provider(callback.from_user.id, "huggingface")
    set_user_model(callback.from_user.id, "1")
    
    text = (
        "✅ <b>Провайдер изменён!</b>\n\n"
        "🤗 Теперь используется: <b>Hugging Face</b>\n"
        f"🤖 Модель: {HF_MODELS['1']['name']}"
    )
    
    # ✅ ИСПРАВЛЕНО: используем edit_text
    try:
        await callback.message.edit_text(text, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, parse_mode="HTML")
    
    await callback.answer("✅ Hugging Face активирован!")


@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: types.CallbackQuery):
    """Вернуться к старту — редактируем текущее сообщение"""
    provider_name, model_name = _get_current_settings(callback.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться на канал", url="https://t.me/hvost_v_fokuse")],
        [
            InlineKeyboardButton(text="🤖 Модели", callback_data="show_models"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
        ],
        [InlineKeyboardButton(text="💡 Сгенерировать идею", callback_data="quick_idea")]
    ])
    
    welcome_text = (
        f"👋 <b>Привет, {callback.from_user.first_name}!</b>\n\n"
        f"⚙️ <b>Твои настройки:</b>\n"
        f"📡 Провайдер: {provider_name}\n"
        f"🤖 Модель: {model_name}\n\n"
        f"💡 <b>Команды:</b>\n"
        f"/idea &lt;тема&gt; — идеи для поста\n"
        f"/optimize &lt;текст&gt; — улучшить текст\n"
        f"/model — выбрать модель\n"
        f"/provider — сменить провайдера"
    )
    
    # ✅ ИСПРАВЛЕНО: используем edit_text вместо answer
    try:
        await callback.message.edit_text(
            welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception:
        # Если edit не сработал (например, сообщение старое), отправляем новое
        await callback.message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    
    await callback.answer()


@router.callback_query(F.data == "quick_idea")
async def quick_idea(callback: types.CallbackQuery):
    """Быстрая генерация идеи"""
    text = (
        "💡 <b>Введи тему для генерации идей:</b>\n\n"
        "Например: фитнес, маркетинг, путешествия\n\n"
        "Используй команду: /idea &lt;твоя тема&gt;"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
    ])
    
    # ✅ ИСПРАВЛЕНО: используем edit_text
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    
    await callback.answer()

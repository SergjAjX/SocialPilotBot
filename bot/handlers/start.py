
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
    """Get current user settings"""
    provider = get_user_provider(user_id)
    model_key = get_user_model(user_id)
    provider_name = "OpenRouter" if provider == "openrouter" else "Hugging Face"
    
    if provider == "openrouter":
        model_name = OR_MODELS.get(model_key, OR_MODELS['1'])['name']
    else:
        model_name = HF_MODELS.get(model_key, HF_MODELS['1'])['name']
    
    return provider_name, model_name


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Main welcome message"""
    save_user(message.from_user.id, message.from_user.username)
    
    provider_name, model_name = _get_current_settings(message.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Subscribe to channel", url="https://t.me/hvost_v_fokuse")],
        [
            InlineKeyboardButton(text="Models", callback_data="show_models"),
            InlineKeyboardButton(text="Settings", callback_data="settings")
        ],
        [InlineKeyboardButton(text="Generate idea", callback_data="quick_idea")]
    ])
    
    welcome_text = (
        f"Hi, {message.from_user.first_name}!\n\n"
        f"I'm SocialPilotBot - your AI assistant for SMM\n\n"
        f"What I can do:\n"
        f"- Generate post ideas\n"
        f"- Optimize texts for social media\n"
        f"- Create content plans\n"
        f"- Write posts on any topic\n\n"
        f"Available 9 AI models:\n"
        f"- 5 models via OpenRouter\n"
        f"- 4 models Hugging Face\n\n"
        f"Your settings:\n"
        f"Provider: {provider_name}\n"
        f"Model: {model_name}\n\n"
        f"Commands:\n"
        f"/idea <topic> - post ideas\n"
        f"/optimize <text> - improve text\n"
        f"/model - select model\n"
        f"/provider - change provider"
    )
    
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )


@router.callback_query(F.data == "show_models")
async def show_models_callback(callback: types.CallbackQuery):
    """Show models list"""
    provider = get_user_provider(callback.from_user.id)
    current_model = get_user_model(callback.from_user.id)
    
    if provider == "openrouter":
        current_name = OR_MODELS.get(current_model, OR_MODELS['1'])['name']
        text = f"Current model: {current_name}\n\n"
        text += "OpenRouter Models:\n\n"
        for key, data in OR_MODELS.items():
            text += f"<b>{key}.</b> {data['name']}\n"
            text += f"   {data['description']}\n"
            text += f"   Context: {data['context']}\n\n"
    else:
        current_name = HF_MODELS.get(current_model, HF_MODELS['1'])['name']
        text = f"Current model: {current_name}\n\n"
        text += "Hugging Face Models:\n\n"
        for key, data in HF_MODELS.items():
            text += f"<b>{key}.</b> {data['name']}\n"
            text += f"   {data['description']}\n"
            text += f"   Context: {data['context']}\n\n"
    
    text += "Use /model <number> to select\n\n"
    text += "[Back](/start)"
    
    try:
        await callback.message.edit_text(text, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, parse_mode="HTML")
    
    await callback.answer()


@router.callback_query(F.data == "settings")
async def show_settings(callback: types.CallbackQuery):
    """Show settings"""
    provider_name, model_name = _get_current_settings(callback.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="OpenRouter", callback_data="set_provider_openrouter"),
            InlineKeyboardButton(text="Hugging Face", callback_data="set_provider_hf")
        ],
        [InlineKeyboardButton(text="Back", callback_data="back_to_start")]
    ])
    
    text = (
        f"Settings:\n\n"
        f"Provider: {provider_name}\n"
        f"Model: {model_name}\n\n"
        f"Choose provider:"
    )
    
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    
    await callback.answer()


@router.callback_query(F.data == "set_provider_openrouter")
async def set_provider_or(callback: types.CallbackQuery):
    """Set OpenRouter"""
    set_user_provider(callback.from_user.id, "openrouter")
    set_user_model(callback.from_user.id, "1")
    
    text = (
        f"Provider changed!\n\n"
        f"Now using: OpenRouter\n"
        f"Model: {OR_MODELS['1']['name']}"
    )
    
    try:
        await callback.message.edit_text(text, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, parse_mode="HTML")
    
    await callback.answer("OpenRouter activated!")


@router.callback_query(F.data == "set_provider_hf")
async def set_provider_hf(callback: types.CallbackQuery):
    """Set Hugging Face"""
    set_user_provider(callback.from_user.id, "huggingface")
    set_user_model(callback.from_user.id, "1")
    
    text = (
        f"Provider changed!\n\n"
        f"Now using: Hugging Face\n"
        f"Model: {HF_MODELS['1']['name']}"
    )
    
    try:
        await callback.message.edit_text(text, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, parse_mode="HTML")
    
    await callback.answer("Hugging Face activated!")


@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: types.CallbackQuery):
    """Back to start"""
    provider_name, model_name = _get_current_settings(callback.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Subscribe to channel", url="https://t.me/hvost_v_fokuse")],
        [
            InlineKeyboardButton(text="Models", callback_data="show_models"),
            InlineKeyboardButton(text="Settings", callback_data="settings")
        ],
        [InlineKeyboardButton(text="Generate idea", callback_data="quick_idea")]
    ])
    
    welcome_text = (
        f"Hi, {callback.from_user.first_name}!\n\n"
        f"Your settings:\n"
        f"Provider: {provider_name}\n"
        f"Model: {model_name}\n\n"
        f"Commands:\n"
        f"/idea <topic> - post ideas\n"
        f"/optimize <text> - improve text\n"
        f"/model - select model\n"
        f"/provider - change provider"
    )
    
    try:
        await callback.message.edit_text(
            welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception:
        await callback.message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    
    await callback.answer()


@router.callback_query(F.data == "quick_idea")
async def quick_idea(callback: types.CallbackQuery):
    """Quick idea generation"""
    text = (
        f"Enter topic for ideas:\n\n"
        f"Example: fitness, marketing, travel\n\n"
        f"Use command: /idea <your topic>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="back_to_start")]
    ])
    
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    
    await callback.answer()

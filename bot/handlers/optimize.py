from aiogram import Router, types
from aiogram.filters import Command
from html import escape as html_escape
from bot.services.openrouter_fallback import OpenRouterClient, MODELS as OR_MODELS
from bot.services.huggingface_client import HuggingFaceClient, HF_MODELS
from bot.database.db import save_user, get_user_model, get_user_provider

router = Router()
or_client = OpenRouterClient()
hf_client = HuggingFaceClient()

MAX_MESSAGE_LENGTH = 4000


async def _split_and_send(message: types.Message, text: str):
    """Разбивает длинное сообщение на части и отправляет"""
    if len(text) <= MAX_MESSAGE_LENGTH:
        await message.answer(text)
    else:
        chunks = []
        current_chunk = ""
        for line in text.split('\n'):
            if len(current_chunk) + len(line) + 1 > MAX_MESSAGE_LENGTH:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += ('\n' if current_chunk else '') + line
        if current_chunk:
            chunks.append(current_chunk)
        
        for i, chunk in enumerate(chunks, 1):
            await message.answer(f"📄 <b>Часть {i}/{len(chunks)}:</b>\n\n{chunk}", parse_mode="HTML")


@router.message(Command("optimize"))
async def optimize_text(message: types.Message):
    save_user(message.from_user.id, message.from_user.username)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "📝 Напиши текст после команды, например:\n/optimize Мой пост о фитнесе",
            parse_mode="HTML"
        )
        return
    
    text = args[1]
    safe_text = html_escape(text)
    
    prompt = (
        f"Оптимизируй этот текст для соцсетей, сделай его более привлекательным "
        f"и добавь эмодзи. Ответ должен быть на русском языке:\n\n{text}"
    )
    
    provider = get_user_provider(message.from_user.id)
    model_key = get_user_model(message.from_user.id)
    
    if provider == "openrouter":
        model_name = OR_MODELS.get(model_key, OR_MODELS['1'])['name']
    else:
        model_name = HF_MODELS.get(model_key, HF_MODELS['1'])['name']
    
    status_msg = await message.answer(
        f"✨ Оптимизирую текст через {model_name}...",
        parse_mode="HTML"
    )
    
    try:
        if provider == "openrouter":
            response = await or_client.ask(prompt, model_key)
        else:
            response = await hf_client.ask(prompt, model_key)
        
        try:
            await status_msg.delete()
        except Exception:
            pass
        
        await _split_and_send(
            message,
            f"📝 <b>Исходный текст:</b>\n<blockquote>{safe_text}</blockquote>\n\n"
            f"✨ <b>Оптимизированный вариант:</b>\n\n{html_escape(response)}"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка оптимизации: {type(e).__name__}")
```

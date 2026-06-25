import os
import aiohttp
import asyncio
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Загружаем .env
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Бесплатные модели Hugging Face через OpenRouter
MODELS = {
    "1": {
        "name": "🚀 Llama 3.2 3B (быстрая)",
        "model": "meta-llama/llama-3.2-3b-instruct:free",
        "description": "Быстрая и легкая модель. Идеальна для простых задач и генерации идей.",
        "context": "128K"
    },
    "2": {
        "name": "💎 Gemma 2 2B (Google)",
        "model": "google/gemma-2-2b-it:free",
        "description": "Компактная модель от Google. Отлично подходит для саммари и кратких ответов.",
        "context": "8K"
    },
    "3": {
        "name": "🧠 Mistral 7B (универсальная)",
        "model": "mistralai/mistral-7b-instruct:free",
        "description": "Универсальная модель. Хороша для написания текстов и креативных задач.",
        "context": "32K"
    },
    "4": {
        "name": "⚡ Phi-3 Mini (Microsoft)",
        "model": "microsoft/phi-3-mini-128k-instruct:free",
        "description": "Мощная компактная модель от Microsoft. Отлична для кода и аналитики.",
        "context": "128K"
    },
    "5": {
        "name": "🎯 Zephyr 7B (HuggingFace)",
        "model": "huggingfaceh4/zephyr-7b-beta:free",
        "description": "Модель от Hugging Face. Хороша для диалогов и ролеплея.",
        "context": "8K"
    },
}

# Модель по умолчанию
DEFAULT_MODEL = "1"

class OpenRouterClient:
    def __init__(self):
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.session = None
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        logger.info(f"🔑 OpenRouterClient инициализирован")
        logger.info(f"🔑 API ключ найден: {'✅ ДА' if api_key else '❌ НЕТ'}")
        if api_key:
            logger.info(f"🔑 Ключ: {api_key[:15]}...{api_key[-5:]}")
        logger.info(f"📋 Доступно моделей: {len(MODELS)}")
    
    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    def get_models_list(self) -> str:
        """Возвращает список моделей для отображения"""
        result = "🤖 <b>Доступные модели:</b>\n\n"
        for key, data in MODELS.items():
            result += f"<b>{key}.</b> {data['name']}\n"
            result += f"   {data['description']}\n"
            result += f"   📏 Контекст: {data['context']}\n\n"
        result += "💡 Используй /model <номер> для выбора модели"
        return result
    
    async def ask(self, prompt: str, model_key: str = DEFAULT_MODEL, max_tokens: int = 500) -> Optional[str]:
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            logger.error("❌ OPENROUTER_API_KEY не найден!")
            return "❌ API ключ не найден. Проверь файл .env"
        
        # Получаем модель из словаря
        model_data = MODELS.get(model_key, MODELS[DEFAULT_MODEL])
        model_name = model_data["model"]
        
        logger.info(f"🚀 Отправляю запрос к OpenRouter")
        logger.info(f"🤖 Модель: {model_data['name']} ({model_name})")
        logger.info(f"📝 Промпт: {prompt[:100]}...")
        
        try:
            session = await self._get_session()
            timeout = aiohttp.ClientTimeout(total=25)
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/sergjajx/SocialPilotBot",
                "X-Title": "SocialPilotBot"
            }
            
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            async with session.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=timeout
            ) as resp:
                logger.info(f"📡 {model_name}: статус {resp.status}")
                
                response_text = await resp.text()
                
                if resp.status == 200:
                    data = await resp.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        result = data["choices"][0]["message"]["content"]
                        logger.info(f"✅ {model_name} вернула ответ ({len(result)} символов)")
                        return result
                    else:
                        logger.warning(f"⚠️ {model_name}: нет choices в ответе")
                        logger.debug(f"Ответ: {response_text[:300]}")
                else:
                    logger.warning(f"⚠️ {model_name}: ошибка {resp.status}")
                    logger.warning(f"Ответ: {response_text[:300]}")
                    
        except asyncio.TimeoutError:
            logger.error(f"⏱️ {model_name}: таймаут (25 сек)")
        except Exception as e:
            logger.error(f"❌ {model_name}: {type(e).__name__}: {e}")
        
        return f"⚠️ Модель {model_data['name']} временно недоступна. Попробуй другую модель через /model"

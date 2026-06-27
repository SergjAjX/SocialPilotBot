import os
import aiohttp
import asyncio
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Бесплатные модели Hugging Face (ТОЛЬКО полностью открытые)
HF_MODELS = {
    "1": {
        "name": "🚀 Mistral 7B Instruct",
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "description": "Универсальная модель для текстов и диалогов",
        "context": "32K"
    },
    "2": {
        "name": "💎 Llama 3.2 3B Instruct",
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "description": "Компактная модель от Meta для быстрых задач",
        "context": "128K"
    },
    "3": {
        "name": "⚡ Qwen 2.5 7B",
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "description": "Быстрая модель для кода и аналитики",
        "context": "128K"
    },
    "4": {
        "name": "🎯 Zephyr 7B",
        "model": "HuggingFaceH4/zephyr-7b-beta",
        "description": "Отличная модель от HuggingFace для диалогов",
        "context": "8K"
    },
}

class HuggingFaceClient:
    def __init__(self):
        self.api_key = os.getenv("HF_TOKEN")
        self.base_url = "https://api-inference.huggingface.co/models"
        self.session = None
        
        logger.info(f"🤗 HuggingFaceClient инициализирован")
        logger.info(f"🔑 HF токен найден: {'✅ ДА' if self.api_key else '❌ НЕТ'}")
        if self.api_key:
            logger.info(f"🔑 HF ключ: {self.api_key[:10]}...{self.api_key[-5:]}")
        logger.info(f"📋 Доступно HF моделей: {len(HF_MODELS)}")
    
    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    def get_models_list(self) -> str:
        result = "🤗 <b>Модели Hugging Face (прямой доступ):</b>\n\n"
        for key, data in HF_MODELS.items():
            result += f"<b>{key}.</b> {data['name']}\n"
            result += f"   {data['description']}\n"
            result += f"   📏 Контекст: {data['context']}\n\n"
        result += "💡 Используй /model &lt;номер&gt; для выбора"
        return result
    
    async def ask(self, prompt: str, model_key: str = "1", max_tokens: int = 500) -> Optional[str]:
        if not self.api_key:
            logger.error("❌ HF_TOKEN не найден!")
            return "❌ HF_TOKEN не найден. Проверь файл .env"
        
        model_data = HF_MODELS.get(model_key, HF_MODELS["1"])
        model_name = model_data["model"]
        url = f"{self.base_url}/{model_name}"
        
        logger.info(f"🤗 Запрос к HF: {model_name}")
        logger.info(f"📝 Промпт: {prompt[:100]}...")
        
        try:
            session = await self._get_session()
            timeout = aiohttp.ClientTimeout(total=45)  # Увеличен до 45 сек
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Используем chat-формат для Instruct-моделей
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "return_full_text": False,
                    "do_sample": True,
                    "top_p": 0.95
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": False
                }
            }
            
            async with session.post(url, headers=headers, json=payload, timeout=timeout) as resp:
                logger.info(f"📡 HF {model_name}: статус {resp.status}")
                
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        result = data[0].get("generated_text", "Пустой ответ")
                        # Очистка от возможных артефактов
                        result = result.strip()
                        if not result:
                            return "⚠️ Модель вернула пустой ответ. Попробуй другую модель."
                        logger.info(f"✅ HF {model_name} вернула ответ ({len(result)} символов)")
                        return result
                    else:
                        logger.warning(f"⚠️ HF {model_name}: неожиданный формат ответа")
                        return f"⚠️ Неожиданный формат ответа: {str(data)[:200]}"
                        
                elif resp.status == 503:
                    # Модель загружается
                    error_data = await resp.json()
                    estimated_time = error_data.get("estimated_time", 30)
                    logger.warning(f"⏳ HF {model_name}: загружается ({estimated_time} сек)")
                    return f"⏳ Модель загружается (примерно {int(estimated_time)} сек). Попробуй ещё раз через минуту."
                    
                elif resp.status == 403:
                    logger.error(f"🚫 HF {model_name}: доступ запрещён (gated model)")
                    return f"🚫 Модель {model_data['name']} требует одобрения. Выбери другую через /model"
                    
                elif resp.status == 404:
                    logger.error(f"❓ HF {model_name}: не найдена")
                    return f"❓ Модель не найдена. Попробуй другую через /model"
                    
                elif resp.status == 429:
                    logger.warning(f"🔄 HF {model_name}: превышен лимит")
                    return "🔄 Превышен лимит запросов. Подожди минуту и попробуй снова."
                    
                else:
                    error = await resp.text()
                    logger.error(f"HF ошибка {resp.status}: {error[:300]}")
                    return f"⚠️ Ошибка HF ({resp.status}). Попробуй другую модель через /model"
                    
        except asyncio.TimeoutError:
            logger.error(f"⏱️ HF {model_name}: таймаут (45 сек)")
            return "⏱️ Таймаут. Модель не отвечает. Попробуй другую через /model."
        except Exception as e:
            logger.error(f"❌ HF {model_name}: {type(e).__name__}: {e}")
            return f"❌ Ошибка соединения: {type(e).__name__}"


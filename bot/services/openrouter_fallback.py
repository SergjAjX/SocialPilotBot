import os
import aiohttp
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Загружаем .env
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Актуальные бесплатные модели на январь 2026
MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "google/gemini-flash-1.5",
    "meta-llama/llama-3.2-3b-instruct:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
]

class OpenRouterClient:
    def __init__(self):
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.session = None
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        logger.info(f"🔑 OpenRouterClient инициализирован")
        logger.info(f"🔑 API ключ найден: {'✅ ДА' if api_key else '❌ НЕТ'}")
        if api_key:
            logger.info(f"🔑 Ключ: {api_key[:15]}...{api_key[-5:]}")
    
    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def ask(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            logger.error("❌ OPENROUTER_API_KEY не найден!")
            return "❌ API ключ не найден. Проверь файл .env"
        
        logger.info(f"🚀 Отправляю запрос к OpenRouter")
        logger.info(f"📝 Промпт: {prompt[:100]}...")
        
        for model in MODELS:
            try:
                logger.info(f"🔄 Пробую модель: {model}")
                session = await self._get_session()
                timeout = aiohttp.ClientTimeout(total=20)
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/sergjajx/SocialPilotBot",
                    "X-Title": "SocialPilotBot"
                }
                
                payload = {
                    "model": model,
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
                    logger.info(f"📡 {model}: статус {resp.status}")
                    
                    response_text = await resp.text()
                    
                    if resp.status == 200:
                        data = await resp.json()
                        if "choices" in data and len(data["choices"]) > 0:
                            result = data["choices"][0]["message"]["content"]
                            logger.info(f"✅ {model} вернула ответ ({len(result)} символов)")
                            return result
                        else:
                            logger.warning(f"⚠️ {model}: нет choices в ответе")
                            logger.debug(f"Ответ: {response_text[:300]}")
                    else:
                        logger.warning(f"⚠️ {model}: ошибка {resp.status}")
                        logger.warning(f"Ответ: {response_text[:300]}")
                        
            except asyncio.TimeoutError:
                logger.error(f"⏱️ {model}: таймаут (20 сек)")
                continue
            except Exception as e:
                logger.error(f"❌ {model}: {type(e).__name__}: {e}")
                continue
        
        logger.error("❌ Все модели недоступны")
        return "⚠️ Все модели временно недоступны. Попробуй через минуту."

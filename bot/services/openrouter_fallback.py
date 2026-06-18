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

# Обновлены модели (реально работающие на free)
MODELS = [
    "google/gemma-4-31b-it:free",  # ✅ Работает (проверено)
    "x-ai/grok-3-mini-beta:free",
    "meta-llama/llama-4-scout:free",
    "deepseek/deepseek-chat-v3-0324:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-70b:free",
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
        logger.info(f"📋 Доступно моделей: {len(MODELS)}")
    
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
        
        for idx, model in enumerate(MODELS, 1):
            try:
                logger.info(f"🔄 [{idx}/{len(MODELS)}] Пробую модель: {model}")
                session = await self._get_session()
                timeout = aiohttp.ClientTimeout(total=30)  # Увеличил до 30 сек
                
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
                    elif resp.status == 429:
                        logger.warning(f"⚠️ {model}: 429 Rate Limit (ждём 2 сек)")
                        await asyncio.sleep(2)  # Ждём перед следующей моделью
                        continue
                    else:
                        logger.warning(f"⚠️ {model}: ошибка {resp.status}")
                        logger.warning(f"Ответ: {response_text[:300]}")
                        
            except asyncio.TimeoutError:
                logger.error(f"⏱️ {model}: таймаут (30 сек)")
                continue
            except Exception as e:
                logger.error(f"❌ {model}: {type(e).__name__}: {e}")
                continue
            
            # Добавляю задержку между попытками, чтобы не превысить rate limit
            await asyncio.sleep(1)
        
        logger.error("❌ Все модели недоступны")
        return "⚠️ Все модели временно недоступны. Попробуй через минуту."

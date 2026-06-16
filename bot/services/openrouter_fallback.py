
import os
import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)

MODELS = [
    "google/gemini-2.0-flash-lite-preview-02-05",
    "qwen/qwen-2.5-7b",
    "microsoft/phi-3-mini-128k",
]

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.session = None
    
    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def ask(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        if not self.api_key:
            return "❌ API ключ не найден. Получи его на openrouter.ai/keys"
        
        for model in MODELS:
            try:
                session = await self._get_session()
                timeout = aiohttp.ClientTimeout(total=15)
                
                async with session.post(
                    self.url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens
                    },
                    timeout=timeout
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"Модель {model} упала: {e}")
                continue
        
        return "⚠️ Все модели временно недоступны. Попробуй через минуту."
